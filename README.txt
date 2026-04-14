LexLogic Desktop v2.0 — AI Legal Reasoning System
===================================================
Project 4.1 | Propositional + FOL | Forward + Backward Chaining
Native Windows Desktop Application (.exe / Python)

HOW TO RUN
----------
Method 1 (Easiest):
  Double-click  START_LEXLOGIC.bat

Method 2 (If you have Python):
  pip install reportlab
  python main.py

Method 3 (Build standalone .exe):
  pip install pyinstaller
  pyinstaller --onefile --windowed --name LexLogic main.py
  Run:  dist\LexLogic.exe

REQUIREMENTS
------------
- Python 3.8+  (https://www.python.org/downloads/)
  MUST check "Add Python to PATH" during install
- reportlab     (auto-installed by START_LEXLOGIC.bat)
- tkinter       (built into Python on Windows — no install needed)

OPTIONAL (for native Prolog inference):
- SWI-Prolog   (https://www.swi-prolog.org/download/stable)
  If not installed, Python FOL engine is used automatically.
  Both engines produce identical results.

FILES
-----
  main.py           -- Main application (all UI + logic)
  legal_kb.pl       -- SWI-Prolog knowledge base (Horn clauses)
  START_LEXLOGIC.bat -- Windows launcher
  data/cases.db     -- SQLite database (auto-created)
  requirements.txt  -- Python dependencies

FEATURES
--------
  Inference Tab     -- Bail & Loan reasoning with full SLD trace
  Case History      -- SQLite database, search/filter, right-click menu
  Analytics         -- Stats, rule frequency bars, case counts
  Rule Base         -- All 9 FOL rules with full Prolog notation
  Settings          -- Configure judge name, court name for PDFs
  PDF Export        -- Professional court-style PDF report
  JSON Export       -- Export all cases as JSON
  Case Detail       -- Full modal with facts, trace, notes, PDF
  Keyboard          -- Ctrl+Enter to run inference

LOGIC OVERVIEW
--------------
  Bail Rules:  B1 (Grant), B2 (Surety), B3 (Deny), B4 (Deny)
  Loan Rules:  L1 (Grant), L2 (Surety), L3 (Premium), D1 (Deny), D2 (Deny)

  All rules expressed as First-Order Logic Horn Clauses
  Inference uses SLD Resolution (Backward Chaining)
  Facts asserted into KB using Forward Chaining pattern
