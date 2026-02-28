"""Tests for hela data models."""
from __future__ import annotations

import pytest
from datetime import date, datetime

from hela.models.chama import Chama, CycleFrequency, Member, MemberRole
from hela.models.ledger import Contribution, ContributionStatus, Loan, LoanStatus


class TestChama:
    def test_monthly_pool_monthly_frequency(self):
        chama = Chama(
            name="Umoja Savings",
            cycle_frequency=CycleFrequency.MONTHLY,
            contribution_amount=2000,
            registration_date=date(2024, 1, 1),
            meeting_day="Saturday",
        )
        assert chama.monthly_pool == 2000

    def test_monthly_pool_weekly_frequency(self):
        chama = Chama(
            name="Umoja Savings",
            cycle_frequency=CycleFrequency.WEEKLY,
            contribution_amount=500,
            registration_date=date(2024, 1, 1),
            meeting_day="Saturday",
        )
        assert chama.monthly_pool == 2000  # 500 * 4

    def test_chama_gets_unique_id(self):
        c1 = Chama("A", CycleFrequency.MONTHLY, 1000, date.today(), "Monday")
        c2 = Chama("B", CycleFrequency.MONTHLY, 1000, date.today(), "Monday")
        assert c1.id != c2.id


class TestMember:
    def _make_member(self, phone="254712345678", role=MemberRole.MEMBER):
        return Member(
            chama_id="chama-001",
            full_name="Jane Wanjiku",
            phone=phone,
            role=role,
            join_date=date(2024, 1, 1),
        )

    def test_valid_phone_accepted(self):
        m = self._make_member(phone="254712345678")
        assert m.phone == "254712345678"

    def test_phone_without_country_code_rejected(self):
        with pytest.raises(ValueError, match="254"):
            self._make_member(phone="0712345678")

    def test_phone_with_plus_rejected(self):
        with pytest.raises(ValueError):
            self._make_member(phone="+254712345678")

    def test_committee_role_detection(self):
        treasurer = self._make_member(role=MemberRole.TREASURER)
        member = self._make_member(role=MemberRole.MEMBER)
        assert treasurer.is_committee
        assert not member.is_committee

    def test_short_name(self):
        m = self._make_member()
        assert m.short_name == "Jane W."

    def test_short_name_single_word(self):
        m = Member("c1", "Wanjiku", "254712345678", MemberRole.MEMBER, date.today())
        assert m.short_name == "Wanjiku"

    def test_member_gets_unique_id(self):
        m1 = self._make_member()
        m2 = self._make_member()
        assert m1.id != m2.id


class TestLoan:
    def _make_loan(self):
        return Loan(
            chama_id="chama-001",
            member_id="member-001",
            principal=10000,
            interest_rate=0.10,  # 10% per month
            term_months=3,
            disbursed_date=date(2024, 1, 1),
            due_date=date(2024, 4, 1),
        )

    def test_total_repayable(self):
        loan = self._make_loan()
        # 10000 + (10000 * 0.10 * 3) = 10000 + 3000 = 13000
        assert loan.total_repayable == 13000

    def test_monthly_repayment(self):
        loan = self._make_loan()
        assert loan.monthly_repayment == pytest.approx(13000 / 3)

    def test_interest_for_period(self):
        loan = self._make_loan()
        assert loan.interest_for_period(1) == 1000
        assert loan.interest_for_period(3) == 3000


class TestContribution:
    def test_confirmed_is_settled(self):
        c = Contribution(
            chama_id="c1", member_id="m1", amount=2000,
            cycle_date=date.today(), recorded_at=datetime.now(),
            status=ContributionStatus.CONFIRMED,
            mpesa_receipt="RHF7WLMHUF",
        )
        assert c.is_settled

    def test_pending_is_not_settled(self):
        c = Contribution(
            chama_id="c1", member_id="m1", amount=2000,
            cycle_date=date.today(), recorded_at=datetime.now(),
            status=ContributionStatus.PENDING,
        )
        assert not c.is_settled

    def test_waived_is_settled(self):
        c = Contribution(
            chama_id="c1", member_id="m1", amount=0,
            cycle_date=date.today(), recorded_at=datetime.now(),
            status=ContributionStatus.WAIVED,
        )
        assert c.is_settled
