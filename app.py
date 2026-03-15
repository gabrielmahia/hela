"""
hela — Chama management for the 21st century.

Demo app: shows what a digitised chama looks like in practice.
All data is in-memory session state (no database required to run).
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import uuid

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hela — Chama Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.hela-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.hela-header h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    margin: 0 0 0.25rem 0;
    letter-spacing: -1px;
}
.hela-header p {
    font-size: 0.95rem;
    opacity: 0.75;
    margin: 0;
}

.stat-card {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    border-left: 4px solid #0f3460;
    margin-bottom: 0.75rem;
}
.stat-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6c757d;
    margin-bottom: 0.25rem;
}
.stat-card .value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #1a1a2e;
}

.badge-confirmed { background:#d4edda; color:#155724; padding:2px 8px; border-radius:20px; font-size:0.78rem; }
.badge-pending   { background:#fff3cd; color:#856404; padding:2px 8px; border-radius:20px; font-size:0.78rem; }
.badge-failed    { background:#f8d7da; color:#721c24; padding:2px 8px; border-radius:20px; font-size:0.78rem; }
.badge-waived    { background:#d1ecf1; color:#0c5460; padding:2px 8px; border-radius:20px; font-size:0.78rem; }
.badge-demo      { background:#e2d9f3; color:#6f42c1; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

.section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6c757d;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem 0;
}

/* ── Mobile responsive ─────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    [data-testid="stDataFrame"] { overflow-x: auto !important; }
    section[data-testid="stSidebar"] { min-width: 200px !important; }
    .stButton > button { width: 100% !important; min-height: 48px !important; }
    .hela-header h1 { font-size: 1.4rem !important; }
    .stat-card .value { font-size: 1.3rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ── Session state: seed demo data once ────────────────────────────────────────

def _init_state():
    if "chama" not in st.session_state:
        st.session_state.chama = {
            "name": "Umoja Investment Group",
            "frequency": "Monthly",
            "contribution_kes": 5000,
            "meeting_day": "Last Saturday",
            "paybill": "522533",
            "founded": date(2022, 3, 1),
        }

    if "members" not in st.session_state:
        today = date.today()
        st.session_state.members = [
            {"id": "m1", "name": "Jane Wanjiku",    "phone": "254712345678", "role": "Chairperson",  "joined": date(2022, 3, 1),  "active": True},
            {"id": "m2", "name": "John Kamau",      "phone": "254723456789", "role": "Treasurer",    "joined": date(2022, 3, 1),  "active": True},
            {"id": "m3", "name": "Mary Achieng",    "phone": "254734567890", "role": "Secretary",    "joined": date(2022, 3, 1),  "active": True},
            {"id": "m4", "name": "Peter Mwangi",    "phone": "254745678901", "role": "Member",       "joined": date(2022, 6, 1),  "active": True},
            {"id": "m5", "name": "Grace Otieno",    "phone": "254756789012", "role": "Member",       "joined": date(2022, 9, 1),  "active": True},
            {"id": "m6", "name": "David Njoroge",   "phone": "254767890123", "role": "Member",       "joined": date(2023, 1, 1),  "active": True},
        ]

    if "contributions" not in st.session_state:
        # Seed 3 months of contribution history
        contribs = []
        cycle_dates = [
            date.today().replace(day=28) - timedelta(days=60),
            date.today().replace(day=28) - timedelta(days=30),
        ]
        statuses = {
            "m1": ["confirmed", "confirmed"],
            "m2": ["confirmed", "confirmed"],
            "m3": ["confirmed", "waived"],
            "m4": ["confirmed", "confirmed"],
            "m5": ["failed",    "confirmed"],
            "m6": ["confirmed", "pending"],
        }
        for i, cd in enumerate(cycle_dates):
            for m in st.session_state.members:
                receipt = f"RHF{uuid.uuid4().hex[:6].upper()}" if statuses[m["id"]][i] == "confirmed" else None
                contribs.append({
                    "id": str(uuid.uuid4())[:8],
                    "member_id": m["id"],
                    "member_name": m["name"],
                    "amount": st.session_state.chama["contribution_kes"] if statuses[m["id"]][i] != "waived" else 0,
                    "cycle_date": cd,
                    "status": statuses[m["id"]][i],
                    "receipt": receipt,
                    "recorded_at": datetime.now(),
                })
        st.session_state.contributions = contribs

    if "loans" not in st.session_state:
        st.session_state.loans = [
            {
                "id": "L001",
                "member_id": "m4",
                "member_name": "Peter Mwangi",
                "principal": 15000,
                "interest_rate": 0.10,
                "term_months": 3,
                "disbursed": date.today() - timedelta(days=45),
                "due": date.today() + timedelta(days=45),
                "status": "active",
                "repaid": 6667,
            }
        ]

    if "fines" not in st.session_state:
        st.session_state.fines = [
            {
                "id": "F001",
                "member_id": "m5",
                "member_name": "Grace Otieno",
                "amount": 200,
                "reason": "Missed contribution — November cycle",
                "date": date.today() - timedelta(days=30),
                "paid": False,
            }
        ]

_init_state()

# ── Helpers ────────────────────────────────────────────────────────────────────
def member_by_id(mid):
    return next((m for m in st.session_state.members if m["id"] == mid), None)

def active_members():
    return [m for m in st.session_state.members if m["active"]]

def format_kes(amount):
    return f"KES {amount:,.0f}"

def badge(status):
    return f'<span class="badge-{status}">{status.upper()}</span>'

def current_cycle_date():
    today = date.today()
    return today.replace(day=28)


# ── Sidebar nav ────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="font-family:'IBM Plex Mono',monospace; font-size:1.3rem; font-weight:600;
            color:#0f3460; padding:0.5rem 0 1rem 0; border-bottom:2px solid #0f3460;">
    💰 hela
</div>
<div style="font-size:0.8rem; color:#6c757d; margin:0.5rem 0 1.5rem 0;">
    Chama management
</div>
""", unsafe_allow_html=True)

PAGE = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "👥 Members", "💳 Contributions", "🏦 Loans & Fines", "⚙️ Settings"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
c = st.session_state.chama
st.sidebar.markdown(f"""
<div style="font-size:0.8rem; color:#6c757d;">
<b style="color:#1a1a2e;">{c['name']}</b><br>
{c['frequency']} · {format_kes(c['contribution_kes'])}/member<br>
Meets: {c['meeting_day']}<br>
Paybill: {c['paybill']}
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown('<span class="badge-demo">⚠️ DEMO DATA</span>', unsafe_allow_html=True)
st.sidebar.caption("No real transactions. All figures are illustrative.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == "📊 Dashboard":
    st.markdown("""
    <div style="background:#fff3cd;border-left:4px solid #ffc107;border-radius:6px;padding:0.8rem 1rem;margin-bottom:1rem;">
      <strong>⚠️ DEMO MODE</strong> — All names, transactions, and figures below are illustrative.
      This is a preview of what your chama could look like once members start contributing.
      <br><span style="font-size:0.82rem;">To start with your real chama: use the ⚙️ <strong>Settings</strong> page to rename the group and clear demo data.</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hela-header">
        <h1>💰 Hela — Chama Manager</h1>
        <p>{c['name']} &nbsp;·&nbsp; Founded {c['founded'].strftime('%B %Y')} &nbsp;·&nbsp; {len(active_members())} active members</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    total_contributions = sum(ct["amount"] for ct in st.session_state.contributions if ct["status"] == "confirmed")
    active_loans_total = sum(ln["principal"] - ln["repaid"] for ln in st.session_state.loans if ln["status"] == "active")
    unpaid_fines = sum(f["amount"] for f in st.session_state.fines if not f["paid"])
    welfare_fund = 1_800  # demo

    kpis = [
        ("💰 Contributions collected", format_kes(total_contributions), "#0f3460"),
        ("🏦 Active loans", format_kes(active_loans_total), "#e63946"),
        ("⚠️ Unpaid fines", format_kes(unpaid_fines), "#f4a261"),
        ("🤝 Welfare fund", format_kes(welfare_fund), "#2a9d8f"),
    ]
    kpi_html = '<div style="display:flex;flex-wrap:wrap;gap:0.75rem;margin-bottom:1.2rem;">'
    for label, value, color in kpis:
        kpi_html += (
            f'<div style="flex:1 1 160px;min-width:140px;background:#f8f9fa;'
            f'border-left:4px solid {color};border-radius:8px;padding:0.9rem 1rem;">'
            f'<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.06em;'
            f'color:#6c757d;margin-bottom:0.25rem;">{label}</div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:1.4rem;'
            f'font-weight:700;color:#1a1a2e;">{value}</div>'
            f'</div>'
        )
    kpi_html += '</div>'
    st.markdown(kpi_html, unsafe_allow_html=True)

    # Current cycle status
    st.markdown('<div class="section-title">Current cycle — contribution status</div>', unsafe_allow_html=True)

    current_cycle = current_cycle_date()
    cycle_contribs = [ct for ct in st.session_state.contributions if ct["cycle_date"] == current_cycle]
    am = active_members()
    paid_ids = {ct["member_id"] for ct in cycle_contribs if ct["status"] in ("confirmed", "waived")}
    pending_ids = {ct["member_id"] for ct in cycle_contribs if ct["status"] == "pending"}
    defaulters = [m for m in am if m["id"] not in paid_ids and m["id"] not in pending_ids]

    collected = sum(ct["amount"] for ct in cycle_contribs if ct["status"] == "confirmed")
    expected = c["contribution_kes"] * len(am)
    pct = int(collected / expected * 100) if expected > 0 else 0

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.progress(pct / 100, text=f"{pct}% collected")
        st.markdown(f"**{format_kes(collected)}** of {format_kes(expected)} expected")
        st.caption(f"Cycle date: {current_cycle.strftime('%d %b %Y')}")
    with col_b:
        if defaulters:
            st.warning(f"**{len(defaulters)} member(s) have not yet paid:**")
            for m in defaulters:
                st.markdown(f"- {m['name']} &nbsp; `{m['phone']}`")
        else:
            st.success("All members have paid or been waived for this cycle. ✓")

    # Recent activity
    st.markdown('<div class="section-title">Recent contributions</div>', unsafe_allow_html=True)
    recent = sorted(st.session_state.contributions, key=lambda x: x["recorded_at"], reverse=True)[:8]
    rows = []
    for ct in recent:
        rows.append({
            "Member": ct["member_name"],
            "Amount": format_kes(ct["amount"]),
            "Cycle": ct["cycle_date"].strftime("%b %Y"),
            "Status": ct["status"].upper(),
            "M-Pesa receipt": ct["receipt"] or "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Members
# ══════════════════════════════════════════════════════════════════════════════
elif PAGE == "👥 Members":
    st.title("Members")

    col1, col2 = st.columns([3, 1])
    with col2:
        add_mode = st.toggle("Add new member")

    if add_mode:
        st.markdown('<div class="section-title">Add member</div>', unsafe_allow_html=True)
        with st.form("add_member"):
            n1, n2 = st.columns(2)
            with n1:
                new_name = st.text_input("Full name")
                new_phone = st.text_input("Phone (07XXXXXXXX or 254XXXXXXXXX)")
            with n2:
                new_role = st.selectbox("Role", ["Member", "Chairperson", "Treasurer", "Secretary", "Auditor"])
                new_joined = st.date_input("Join date", value=date.today())
            submitted = st.form_submit_button("Add member", type="primary")
            if submitted and new_name and new_phone:
                phone = new_phone.strip().lstrip("+")
                if phone.startswith("07"): phone = "254" + phone[1:]
                elif phone.startswith("7") and len(phone) == 9: phone = "254" + phone
                if not (phone.startswith("254") and phone.isdigit() and len(phone) == 12):
                    st.error("Invalid phone number. Use 07XXXXXXXX or 254XXXXXXXXX format.")
                else:
                    st.session_state.members.append({
                        "id": str(uuid.uuid4())[:6],
                        "name": new_name.strip(),
                        "phone": phone,
                        "role": new_role,
                        "joined": new_joined,
                        "active": True,
                    })
                    st.success(f"Added {new_name}.")
                    st.rerun()

    st.markdown('<div class="section-title">Active members</div>', unsafe_allow_html=True)
    am = active_members()
    rows = []
    for m in am:
        # Contribution compliance rate
        member_contribs = [ct for ct in st.session_state.contributions if ct["member_id"] == m["id"]]
        settled = sum(1 for ct in member_contribs if ct["status"] in ("confirmed", "waived"))
        total_c = len(member_contribs)
        rate = f"{int(settled/total_c*100)}%" if total_c > 0 else "—"
        rows.append({
            "Name": m["name"],
            "Phone": m["phone"],
            "Role": m["role"],
            "Joined": m["joined"].strftime("%b %Y"),
            "Compliance": rate,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(f"{len(am)} active members · Contribution: {format_kes(c['contribution_kes'])} / {c['frequency'].lower()}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Contributions
# ══════════════════════════════════════════════════════════════════════════════
elif PAGE == "💳 Contributions":
    st.title("Contributions")

    tab1, tab2 = st.tabs(["Record payment", "History"])

    with tab1:
        st.markdown('<div class="section-title">Record an M-Pesa payment</div>', unsafe_allow_html=True)
        with st.form("record_contribution"):
            c1, c2, c3 = st.columns(3)
            with c1:
                member_names = [m["name"] for m in active_members()]
                sel_member = st.selectbox("Member", member_names)
            with c2:
                amount_in = st.number_input("Amount (KES)", min_value=0, value=c["contribution_kes"], step=100)
            with c3:
                cycle_in = st.date_input("Cycle date", value=current_cycle_date())

            receipt_in = st.text_input("M-Pesa receipt number", placeholder="e.g. RHF7WLMHUF")
            notes_in = st.text_input("Notes (optional)")
            status_in = st.radio("Status", ["confirmed", "pending", "waived", "failed"], horizontal=True)
            submitted = st.form_submit_button("Record payment", type="primary")

            if submitted:
                selected_member = next(m for m in active_members() if m["name"] == sel_member)
                # Idempotency: check receipt not already recorded
                if receipt_in and any(ct["receipt"] == receipt_in for ct in st.session_state.contributions):
                    st.warning(f"Receipt {receipt_in} already recorded. Duplicate ignored.")
                else:
                    st.session_state.contributions.append({
                        "id": str(uuid.uuid4())[:8],
                        "member_id": selected_member["id"],
                        "member_name": selected_member["name"],
                        "amount": amount_in,
                        "cycle_date": cycle_in,
                        "status": status_in,
                        "receipt": receipt_in or None,
                        "recorded_at": datetime.now(),
                        "notes": notes_in,
                    })
                    st.success(f"Recorded: {sel_member} — {format_kes(amount_in)} [{status_in.upper()}]")
                    st.rerun()

    with tab2:
        st.markdown('<div class="section-title">All contributions</div>', unsafe_allow_html=True)

        # Filter
        f1, f2 = st.columns(2)
        with f1:
            filter_status = st.multiselect("Filter by status", ["confirmed", "pending", "failed", "waived"],
                                           default=["confirmed", "pending", "failed", "waived"])
        with f2:
            filter_member = st.selectbox("Filter by member", ["All"] + [m["name"] for m in active_members()])

        filtered = st.session_state.contributions
        if filter_status:
            filtered = [ct for ct in filtered if ct["status"] in filter_status]
        if filter_member != "All":
            filtered = [ct for ct in filtered if ct["member_name"] == filter_member]

        filtered = sorted(filtered, key=lambda x: x["cycle_date"], reverse=True)
        rows = [{
            "Member": ct["member_name"],
            "Amount": format_kes(ct["amount"]),
            "Cycle": ct["cycle_date"].strftime("%b %Y"),
            "Status": ct["status"].upper(),
            "Receipt": ct["receipt"] or "—",
            "Recorded": ct["recorded_at"].strftime("%d %b %H:%M"),
        } for ct in filtered]
        st.dataframe(pd.DataFrame(rows) if rows else pd.DataFrame(), use_container_width=True, hide_index=True)
        if filtered:
            confirmed_total = sum(ct["amount"] for ct in filtered if ct["status"] == "confirmed")
            st.caption(f"{len(filtered)} records · Confirmed total: {format_kes(confirmed_total)}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Loans & Fines
# ══════════════════════════════════════════════════════════════════════════════
elif PAGE == "🏦 Loans & Fines":
    st.title("Loans & Fines")
    tab1, tab2 = st.tabs(["Loans", "Fines"])

    with tab1:
        st.markdown('<div class="section-title">Active loans</div>', unsafe_allow_html=True)

        rows = []
        for ln in st.session_state.loans:
            outstanding = ln["principal"] - ln["repaid"]
            total_due = ln["principal"] * (1 + ln["interest_rate"] * ln["term_months"])
            rows.append({
                "Member": ln["member_name"],
                "Principal": format_kes(ln["principal"]),
                "Total repayable": format_kes(total_due),
                "Repaid": format_kes(ln["repaid"]),
                "Outstanding": format_kes(outstanding),
                "Due date": ln["due"].strftime("%d %b %Y"),
                "Status": ln["status"].upper(),
            })
        st.dataframe(pd.DataFrame(rows) if rows else pd.DataFrame(), use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">Issue new loan</div>', unsafe_allow_html=True)
        with st.form("new_loan"):
            l1, l2, l3 = st.columns(3)
            with l1:
                loan_member = st.selectbox("Member", [m["name"] for m in active_members()])
                loan_principal = st.number_input("Principal (KES)", min_value=1000, value=10000, step=1000)
            with l2:
                loan_rate = st.number_input("Monthly interest %", min_value=0.0, value=10.0, step=1.0)
                loan_term = st.number_input("Term (months)", min_value=1, value=3, step=1)
            with l3:
                loan_date = st.date_input("Disbursement date", value=date.today())

            total_rep = loan_principal * (1 + loan_rate / 100 * loan_term)
            st.info(f"Total repayable: **{format_kes(total_rep)}** · Monthly instalment: **{format_kes(total_rep/loan_term)}**")
            if st.form_submit_button("Issue loan", type="primary"):
                selected = next(m for m in active_members() if m["name"] == loan_member)
                st.session_state.loans.append({
                    "id": f"L{len(st.session_state.loans)+1:03d}",
                    "member_id": selected["id"],
                    "member_name": loan_member,
                    "principal": loan_principal,
                    "interest_rate": loan_rate / 100,
                    "term_months": int(loan_term),
                    "disbursed": loan_date,
                    "due": loan_date + timedelta(days=30 * int(loan_term)),
                    "status": "active",
                    "repaid": 0,
                })
                st.success(f"Loan issued to {loan_member}: {format_kes(loan_principal)}")
                st.rerun()

    with tab2:
        st.markdown('<div class="section-title">Fines</div>', unsafe_allow_html=True)
        rows = [{"Member": f["member_name"], "Amount": format_kes(f["amount"]),
                 "Reason": f["reason"], "Date": f["date"].strftime("%d %b %Y"),
                 "Paid": "✓" if f["paid"] else "✗"} for f in st.session_state.fines]
        st.dataframe(pd.DataFrame(rows) if rows else pd.DataFrame(), use_container_width=True, hide_index=True)

        with st.form("new_fine"):
            st.markdown("**Levy a fine**")
            f1, f2, f3 = st.columns(3)
            with f1:
                fine_member = st.selectbox("Member", [m["name"] for m in active_members()])
            with f2:
                fine_amount = st.number_input("Amount (KES)", min_value=50, value=200, step=50)
            with f3:
                fine_reason = st.text_input("Reason")
            if st.form_submit_button("Levy fine"):
                sel = next(m for m in active_members() if m["name"] == fine_member)
                st.session_state.fines.append({
                    "id": str(uuid.uuid4())[:6],
                    "member_id": sel["id"],
                    "member_name": fine_member,
                    "amount": fine_amount,
                    "reason": fine_reason,
                    "date": date.today(),
                    "paid": False,
                })
                st.success(f"Fine of {format_kes(fine_amount)} levied on {fine_member}.")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Settings
# ══════════════════════════════════════════════════════════════════════════════
elif PAGE == "⚙️ Settings":
    st.title("Chama settings")
    st.info("Changes here update your session only (demo mode — no database).")

    with st.form("settings"):
        c = st.session_state.chama
        new_name = st.text_input("Chama name", value=c["name"])
        col1, col2 = st.columns(2)
        with col1:
            new_freq = st.selectbox("Meeting frequency", ["Weekly", "Biweekly", "Monthly", "Quarterly"],
                                    index=["Weekly","Biweekly","Monthly","Quarterly"].index(c["frequency"]))
            new_contrib = st.number_input("Contribution per member (KES)", value=c["contribution_kes"], step=500)
        with col2:
            new_day = st.text_input("Meeting day", value=c["meeting_day"])
            new_paybill = st.text_input("M-Pesa paybill number", value=c["paybill"])

        if st.form_submit_button("Save settings", type="primary"):
            st.session_state.chama.update({
                "name": new_name,
                "frequency": new_freq,
                "contribution_kes": new_contrib,
                "meeting_day": new_day,
                "paybill": new_paybill,
            })
            st.success("Settings updated.")
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🗑️ Reset demo data")
    st.caption(
        "Clears all demo members, contributions, loans, and fines. "
        "Use this once you're ready to enter your chama's real data."
    )
    if st.button("Clear demo data and start fresh", type="secondary"):
        for key in ["members", "contributions", "loans", "fines"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.chama["name"] = new_name or "My Chama"
        st.success("Demo data cleared. Add your real members in the Members page.")
        st.rerun()
