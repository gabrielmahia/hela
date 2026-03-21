# 💰 Hela — Chama Management for the 21st Century

**Chama management for the 21st century.**

[![Live App](https://img.shields.io/badge/Live%20App-hela.streamlit.app-FF4B4B?logo=streamlit)](https://helaismoney.streamlit.app)
[![Live Data](https://img.shields.io/badge/Live%20Data-open.er-api.com%20%C2%B7%20COB%20RSS-00b4d8)](#hela)
[![Status](https://img.shields.io/badge/status-early%20development-orange)](#roadmap)
[![License](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-red)](LICENSE)

> **Hela** /héla/ — *Kiswahili*: money, wealth, funds.

Kenya has over 300,000 registered chamas — informal savings and investment groups — plus an unknown multiple of unregistered ones. By some estimates, chamas manage over KES 300 billion in assets collectively. They are the dominant financial infrastructure for ordinary Kenyans.

Their software situation: WhatsApp groups, paper ledgers, and Excel sheets.

Hela digitises the chama without replacing what makes it work.

---

## The problem

**What chamas do well:** trust, accountability, discipline, community. These aren't software problems.

**What they struggle with:** contribution tracking, interest calculations, loan management, attendance records, end-of-cycle reporting. These are exactly software problems.

**What existing software misses:** mobile-first, M-Pesa native, Kiswahili, designed for committee governance (chair + treasurer + secretary), offline tolerant, never needs more than USSD to function.

---

## What hela is

A progressive web app and USSD interface for chama financial management.

**Core features (in development):**

| Feature | Status | Description |
|---|---|---|
| Member ledger | 🔧 Building | Contributions, withdrawals, balances per member |
| M-Pesa integration | 🔧 Building | STK Push for contributions; M-Pesa statement import |
| Loan management | 📋 Designed | Loans, repayments, interest accrual, overdue tracking |
| Meeting records | 📋 Designed | Attendance, minutes, decisions, quorum tracking |
| End-of-cycle report | 📋 Designed | PDF financial summary for the AGM |
| USSD interface | 📋 Designed | Full functionality via basic phone, no data needed |
| Committee roles | 📋 Designed | Chair, Treasurer, Secretary, Auditor, Member |
| Multi-chama | 🔮 Future | Umbrella groups and chapter federation |

---

## Design principles

**M-Pesa native, not M-Pesa bolted on.**
Contributions come through M-Pesa STK Push. Disbursements go out via B2C. The ledger auto-reconciles from M-Pesa callbacks — no manual entry for payments.

**USSD as first-class interface.**
A treasurer checking the balance or recording a fine should be able to do it on a Sh. 2,000 feature phone with no data. The web app is additive, not the baseline.

**Committee governance, not individual accounts.**
Hela is designed around the chama structure: a committee holds authority over funds, not any single individual. Withdrawal approvals require quorum.

**Kiswahili first, English second.**
Interface defaults to Kiswahili. English is an option, not the assumption.

---

## Architecture

```
hela/
├── models/
│   ├── chama.py        # Chama, Member, Committee
│   ├── ledger.py       # Contribution, Withdrawal, Loan, Repayment
│   └── meeting.py      # Meeting, Attendance, Minute
├── services/
│   ├── contributions.py  # Record, reconcile from M-Pesa callbacks
│   ├── loans.py          # Originate, repay, calculate interest
│   ├── reports.py        # Cycle-end PDF generation
│   └── mpesa.py          # Thin wrapper over m-pesa-rails
├── ussd/
│   └── handler.py        # Africa's Talking USSD session handler
├── api/
│   └── v1/               # REST API for web and mobile clients
└── web/
    └── app.py            # Streamlit coordinator dashboard
```

**Dependencies:**
- [`m-pesa-rails`](https://github.com/gabrielmahia/m-pesa-rails) — M-Pesa integration
- Africa's Talking SDK — USSD
- SQLite (single-chama) / PostgreSQL (multi-chama SaaS)
- ReportLab — PDF cycle reports

---

## Roadmap

### v0.1 — Member ledger and M-Pesa contributions
- [ ] Chama and member data models
- [ ] Contribution recording with M-Pesa callback reconciliation
- [ ] Basic Streamlit coordinator dashboard
- [ ] 80% test coverage

### v0.2 — Loans and USSD
- [ ] Loan origination, repayment, interest calculation
- [ ] USSD interface (Africa's Talking)
- [ ] SMS notifications (contribution confirmed, loan due)

### v0.3 — Reports and governance
- [ ] End-of-cycle PDF report (balance sheet, per-member statement)
- [ ] Committee approval workflow for withdrawals
- [ ] AGM readiness checklist

### v1.0 — Production launch
- [ ] Multi-tenancy (one hela instance, many chamas)
- [ ] Safaricom paybill registration guide
- [ ] Product Hunt launch

---

## Contributing

Not accepting pull requests yet. Open an issue to discuss.
Contact: contact@aikungfu.dev

---

## License

CC BY-NC-ND 4.0. Commercial licensing: contact@aikungfu.dev

---

*Part of the [gabrielmahia](https://github.com/gabrielmahia) portfolio — infrastructure where Africa's economic reality meets software engineering.*
---

## Portfolio

Part of a suite of civic and community tools built by [Gabriel Mahia](https://github.com/gabrielmahia):

| App | What it does |
|-----|-------------|
| [🌊 Mafuriko](https://floodwatch-kenya.streamlit.app) | Flood risk & policy enforcement tracker — Kenya |
| [💧 WapiMaji](https://wapimaji.streamlit.app) | Water stress & drought intelligence — 47 counties |
| [🏛️ Macho ya Wananchi](https://macho-ya-wananchi.streamlit.app) | MP voting records, CDF spending, bill tracker |
| [🌾 JuaMazao](https://juamazao.streamlit.app) | Live food price intelligence for smallholders |
| [🏦 ChaguaSacco](https://chaguasacco.streamlit.app) | Compare Kenya SACCOs on dividends & loan rates |
| [🛡️ Hesabu](https://hesabu.streamlit.app) | County budget absorption tracker |
| [🗺️ Hifadhi](https://hifadhi.streamlit.app) | Riparian encroachment & Water Act compliance map |
| [💰 Hela](https://helaismoney.streamlit.app) | Chama management for the 21st century |
| [💸 Peleka](https://tumapesa.streamlit.app) | True cost remittance comparison — diaspora to Kenya |
| [📊 Msimamo](https://easystocktrader.streamlit.app) | Macro risk & trade intelligence terminal |
| [🦁 Dagoretti](https://dagoretti-high-school-community-app.streamlit.app) | Alumni atlas & community hub for Dagoretti High |
| [⛪ Jumuia](https://jumuia.streamlit.app) | Catholic parish tools — church finder, pastoral care |

