"""hela — Chama and Member data models.

A chama is a group. A group has members. Each member has a role.
The committee (chair, treasurer, secretary) holds governance authority.

Design decision: roles are per-membership, not per-person. The same
individual can be treasurer in Chama A and a regular member in Chama B.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class MemberRole(str, Enum):
    """Committee roles within a chama."""
    CHAIRPERSON = "chairperson"
    TREASURER = "treasurer"
    SECRETARY = "secretary"
    AUDITOR = "auditor"
    MEMBER = "member"

    @property
    def is_committee(self) -> bool:
        return self in (
            MemberRole.CHAIRPERSON,
            MemberRole.TREASURER,
            MemberRole.SECRETARY,
            MemberRole.AUDITOR,
        )


class CycleFrequency(str, Enum):
    """How often the chama meets and collects contributions."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class ChamaStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"    # Temporarily paused
    DISSOLVED = "dissolved"    # Formally wound up


@dataclass
class Chama:
    """A chama (savings and investment group).

    The fundamental unit. All financial activity belongs to a chama.
    """

    name: str
    cycle_frequency: CycleFrequency
    contribution_amount: float          # KES per member per cycle
    registration_date: date
    meeting_day: str                    # e.g. "Saturday", "First Monday"
    paybill_number: Optional[str] = None  # Safaricom paybill for contributions
    account_reference: Optional[str] = None
    status: ChamaStatus = ChamaStatus.ACTIVE
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def monthly_pool(self) -> float:
        """Expected monthly contribution pool — useful for loan eligibility."""
        multipliers = {
            CycleFrequency.WEEKLY: 4,
            CycleFrequency.BIWEEKLY: 2,
            CycleFrequency.MONTHLY: 1,
            CycleFrequency.QUARTERLY: 0.33,
        }
        return self.contribution_amount * multipliers[self.cycle_frequency]


@dataclass
class Member:
    """A member of a chama.

    One person can hold memberships in multiple chamas. Roles are
    per-membership, not per-person.
    """

    chama_id: str
    full_name: str
    phone: str                  # E.164 format: 254712345678
    role: MemberRole
    join_date: date
    national_id: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not self.phone.startswith("254") or not self.phone.isdigit() or len(self.phone) != 12:
            raise ValueError(
                f"Phone must be E.164 format without '+': e.g. 254712345678, got '{self.phone}'"
            )

    @property
    def is_committee(self) -> bool:
        return self.role.is_committee

    @property
    def short_name(self) -> str:
        """First name + last initial — for compact display."""
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[-1][0]}."
        return parts[0] if parts else self.full_name
