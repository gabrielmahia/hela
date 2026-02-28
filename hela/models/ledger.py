"""hela — Financial ledger models.

Every KES that flows into or out of a chama is recorded here.
The ledger is append-only: nothing is ever deleted or modified.
Corrections are made by recording offsetting entries.

Design decisions:
- Amounts always in KES, stored as floats. Precision requirement
  for chamas is 2dp; no need for Decimal for this scale.
- mpesa_receipt is the canonical idempotency key for M-Pesa transactions.
  If a receipt is already in the ledger, the transaction is a duplicate.
- status field for contributions: pending (STK sent), confirmed (callback
  received), failed (cancelled or expired).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class ContributionStatus(str, Enum):
    PENDING = "pending"        # STK Push sent, awaiting PIN
    CONFIRMED = "confirmed"    # M-Pesa callback received, payment succeeded
    FAILED = "failed"          # Customer cancelled or timed out
    WAIVED = "waived"          # Treasurer waived the contribution (recorded manually)


class LoanStatus(str, Enum):
    ACTIVE = "active"
    FULLY_REPAID = "fully_repaid"
    DEFAULTED = "defaulted"
    WRITTEN_OFF = "written_off"


@dataclass
class Contribution:
    """A single contribution from a member for a specific cycle.

    One contribution per member per cycle is the norm, though
    catch-up contributions (multiple cycles, one payment) are supported.
    """

    chama_id: str
    member_id: str
    amount: float                       # KES
    cycle_date: date                    # The cycle this contribution is for
    recorded_at: datetime
    status: ContributionStatus = ContributionStatus.PENDING
    mpesa_receipt: Optional[str] = None     # From STK callback — idempotency key
    mpesa_phone: Optional[str] = None       # May differ from member.phone (another phone)
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def is_settled(self) -> bool:
        return self.status in (ContributionStatus.CONFIRMED, ContributionStatus.WAIVED)


@dataclass
class Loan:
    """A loan issued to a member from the chama pool.

    Interest is calculated as simple interest on the principal.
    Most chamas use 10% flat per month — configurable per chama.
    """

    chama_id: str
    member_id: str
    principal: float            # KES disbursed
    interest_rate: float        # Monthly rate, e.g. 0.10 for 10%
    term_months: int
    disbursed_date: date
    due_date: date
    status: LoanStatus = LoanStatus.ACTIVE
    mpesa_receipt: Optional[str] = None     # B2C receipt for disbursement
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def total_repayable(self) -> float:
        """Principal + simple interest for the full term."""
        return self.principal * (1 + self.interest_rate * self.term_months)

    @property
    def monthly_repayment(self) -> float:
        return self.total_repayable / self.term_months

    def interest_for_period(self, months: int) -> float:
        return self.principal * self.interest_rate * months


@dataclass
class Repayment:
    """A loan repayment (partial or full)."""

    loan_id: str
    chama_id: str
    member_id: str
    amount: float
    paid_at: datetime
    mpesa_receipt: Optional[str] = None
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Fine:
    """A fine levied against a member (late contribution, absenteeism, etc)."""

    chama_id: str
    member_id: str
    amount: float
    reason: str
    levied_date: date
    is_paid: bool = False
    paid_date: Optional[date] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
