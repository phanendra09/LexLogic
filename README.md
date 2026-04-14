# ⚖ LexLogic — AI Legal Reasoning System

A **Knowledge-Based AI System** for automated legal decision-making using First-Order Logic (FOL) Horn Clauses and SLD Resolution (Backward Chaining).

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![Prolog](https://img.shields.io/badge/Logic-SWI--Prolog-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

---

## 🔍 What is LexLogic?

LexLogic automates legal reasoning across **4 modules** using formal logic:

| Module | Domain | Rules |
|--------|--------|-------|
| ⚖ **Bail Eligibility** | Criminal law — should bail be granted? | B1–B4 |
| 💰 **Loan Approval** | Financial — should a loan be approved? | L1–L3, D1–D2 |
| 🔨 **Criminal Sentencing** | Sentencing — minimal to maximum? | S1–S4 |
| ⚠ **Ethics Screening** | Conflict of interest — waivable to disqualified? | E1–E3 |

Each decision comes with a **complete inference trace** showing exactly which rules fired and why.

---

## 🧠 How It Works

### The Algorithm: SLD Resolution (Backward Chaining)

1. **Start with a goal** — e.g., `bail_verdict(X, V, R, _)`
2. **Try to unify** with each rule HEAD in priority order
3. **Recursively prove** all sub-goals in the rule BODY
4. If all sub-goals pass → **rule fires** → return verdict
5. If any sub-goal fails → **backtrack** to the next rule
6. If no rule matches → **default verdict**

### Example Rule (Horn Clause):
```prolog
bail_verdict(Person, granted, 'B1', 'Eligible') :-
    not_flight_risk(Person),      % Sub-goal 1
    not_dangerous(Person),        % Sub-goal 2
    community_ties(Person), !.    % Sub-goal 3 + CUT
```

### Dual-Engine Architecture:
- **Python FOL Engine** — Always available, implements SLD resolution in Python
- **SWI-Prolog Engine** — Optional, provides native logic programming evaluation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (tested on 3.13)
- `pip install reportlab` (optional — for PDF export)
- SWI-Prolog (optional — for native Prolog engine)

### Run
```bash
python main.py
```
Double-click to launch. No server, no browser needed.

---

## 📂 Project Structure

```
lexlogic_win/
├── main.py          # Complete app: UI + Engine + Database (~2,660 lines)
├── engine.py        # Standalone backup engine (Bail + Loan)
├── legal_kb.pl      # Prolog Knowledge Base (all 4 modules, ~468 lines)
├── utils.py         # Helper utilities
├── data/
│   └── cases.db     # SQLite database (auto-created)
└── .gitignore
```

---

## ✨ Features

- 🧠 **SLD Resolution Engine** — Backward chaining over Horn Clauses
- 📜 **Inference Trace** — Step-by-step rule evaluation with FOL notation
- 💬 **Plain-English Explain** — Converts traces to human-readable explanations
- 🗄 **Case History** — SQLite database with search, filter, and analytics
- 📊 **Analytics** — Pie chart visualization of verdict distribution
- 📄 **PDF Reports** — Professional legal documents via ReportLab
- 📂 **Batch Import** — CSV file processing for multiple cases
- ⚖ **Case Comparison** — Side-by-side comparison of two cases
- 🎨 **Theme Toggle** — Light/dark dashboard theme
- 📝 **Form Templates** — Pre-filled presets for quick testing
- ⌨ **Keyboard Shortcuts** — Ctrl+Enter (run), Ctrl+B/L/S (modules)

---

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.13 | Core language |
| Tkinter | Desktop GUI (built-in) |
| SQLite3 | Case database (built-in) |
| SWI-Prolog | Optional native logic engine |
| ReportLab | PDF generation |
| JSON | Facts & trace serialization |

---

## 📖 Logic Foundations

| Concept | Usage in LexLogic |
|---------|-------------------|
| **Propositional Logic** | Fact assertions: `capital_offense(X) = TRUE` |
| **First-Order Logic** | Rules with variables: `∀X: capital(X) → denied(X)` |
| **Horn Clauses** | Each rule is `HEAD :- BODY.` format |
| **SLD Resolution** | Backward chaining inference algorithm |
| **CUT (!)** | Prevents backtracking for hard-denial rules |

---

## 📜 License

This project is for educational purposes — part of a B.Tech CSE project on AI-based legal reasoning.
