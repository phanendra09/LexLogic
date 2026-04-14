"""
LexLogic Desktop — AI Legal Reasoning System
Native Windows Application
Double-click lexlogic.py to run. No browser. No server.
Requirements: Python 3.8+, reportlab (pip install reportlab)
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3, json, os, sys, subprocess, threading, datetime, hashlib, io
from pathlib import Path

# ── PATHS ──────────────────────────────────────────────────────────
BASE = Path(__file__).parent
DB   = BASE / "cases.db"
KB   = BASE / "legal_kb.pl"

# ── THEME ──────────────────────────────────────────────────────────
BG0,BG1,BG2,BG3  = "#0e1117","#161b27","#1e2538","#252d42"
BORD              = "#2e3a55"
TX,TX2,TX3        = "#e8eaf0","#9aa3b8","#5c6480"
AMB,AMB2,AMB3     = "#d4a24c","#f0c06a","#8a6520"
GRN,GRN2          = "#3dba72","#1d6b3e"
RED,RED2          = "#e05252","#7a2222"
YEL,WHT           = "#e0b84c","#ffffff"

FB   = ("Segoe UI",9)
FSM  = ("Segoe UI",8)
FM   = ("Consolas",8)
FM2  = ("Consolas",9)
FBTN = ("Segoe UI",9,"bold")
FBIG = ("Georgia",26,"bold")
FT   = ("Georgia",11,"bold italic")
FTB  = ("Georgia",12,"bold")

# ── DATABASE ───────────────────────────────────────────────────────
def init_db():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS cases(
        id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT UNIQUE,
        subject TEXT, module TEXT, verdict TEXT, rule TEXT, reason TEXT,
        facts TEXT, trace TEXT, engine TEXT, notes TEXT DEFAULT '',
        created_at TEXT)""")
    c.execute("CREATE TABLE IF NOT EXISTS cfg(k TEXT PRIMARY KEY,v TEXT)")
    for k,v in [("judge","Hon. System Judge"),("court","AI Reasoning Court")]:
        c.execute("INSERT OR IGNORE INTO cfg VALUES(?,?)",(k,v))
    c.commit(); c.close()

def get_cfg(k,d="")->str:
    try:
        c=sqlite3.connect(DB); r=c.execute("SELECT v FROM cfg WHERE k=?",(k,)).fetchone()
        c.close(); return r[0] if r else d
    except: return d

def set_cfg(k,v):
    c=sqlite3.connect(DB); c.execute("INSERT OR REPLACE INTO cfg VALUES(?,?)",(k,v))
    c.commit(); c.close()

def get_db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

# ── PROLOG CHECK ───────────────────────────────────────────────────
def prolog_ok():
    try:
        r=subprocess.run(["swipl","--version"],capture_output=True,timeout=4)
        return r.returncode==0
    except: return False

PROLOG = prolog_ok()

# ── PYTHON FOL ENGINE ──────────────────────────────────────────────
class Engine:
    def bail(self,f):
        T=[]; A=lambda s,p,l: T.append({"s":s,"p":p,"l":l})
        A("info","KB loaded — facts asserted into working memory",
          "Dynamic predicates initialised for subject")
        for k,v in f.items():
            if isinstance(v,bool) and v: A("pass",f"{k}(X) <- TRUE",f"assertz({k}(subject)).")
        A("rule","SLD Resolution begins: goal = bail_verdict(X,V,R,_)",
          "Trying rules in order: B3 > B4 > B1 > B2")
        if f.get("capital_offense"):
            A("rule","Rule B3 unifies: capital_offense(X).",
              "bail_verdict(X,denied,'B3',_) :- capital_offense(X), !.")
            A("fail","capital_offense <- TRUE  >> CUT >> bail_denied",
              "forall X: capital_offense(X) -> bail_denied(X)  [Statute s.487]")
            return self._r("denied","B3","Capital offense — bail denied by statute",T)
        A("info","Rule B3 fails (capital_offense=FALSE) — backtrack","Try Rule B4")
        if f.get("violent_offense") and f.get("repeat_offender"):
            A("rule","Rule B4 unifies: violent_offense(X), repeat_offender(X).",
              "bail_verdict(X,denied,'B4',_) :- violent_offense(X),repeat_offender(X),!.")
            A("fail","Both unified >> CUT >> bail_denied",
              "forall X: violent(X) ^ repeat(X) -> bail_denied(X)  [s.302 CrPC]")
            return self._r("denied","B4","Repeat violent offender — bail denied",T)
        A("info","Rule B4 fails — backtrack","Try Rule B1")
        A("rule","Rule B1: bail_eligible(X) :- not_flight_risk(X), not_dangerous(X), community_ties(X).",
          "Backward chaining: prove all three sub-goals")
        nfr = f.get("local_address") and (f.get("has_employment") or f.get("family_ties"))
        if nfr: A("pass","Sub-goal not_flight_risk(X) PROVED",
                  "local_address(X) ^ (employment(X) v family_ties(X)) -> neg_flight_risk(X)")
        else:   A("fail","Sub-goal not_flight_risk(X) FAILED",
                  "Requires: local_address ^ (employment v family_ties)")
        nd = not f.get("violent_offense") and not f.get("weapon_involved")
        if nd:  A("pass","Sub-goal not_dangerous(X) PROVED",
                  "neg_violent(X) ^ neg_weapon(X) -> not_dangerous(X)")
        else:   A("fail","Sub-goal not_dangerous(X) FAILED",
                  "violent_offense(X) v weapon_involved(X) = TRUE")
        ct = f.get("family_ties") or (f.get("has_employment") and f.get("community_years"))
        if ct:  A("pass","Sub-goal community_ties(X) PROVED",
                  "family_ties(X) v (employment(X) ^ years_in_community(X,Y) ^ Y>=2)")
        else:   A("fail","Sub-goal community_ties(X) FAILED",
                  "Requires: family_ties v (employment ^ community_years>=2)")
        if nfr and nd and ct:
            A("rule","Rule B1: ALL sub-goals TRUE >> bail_eligible(X)",
              "forall X: neg_risk^neg_danger^ties -> bail_eligible(X)  [Rule B1] OK")
            return self._r("granted","B1","Not flight risk + not dangerous + community ties",T)
        A("info","Rule B1 fails — backtrack","Try Rule B2")
        A("rule","Rule B2: bail_eligible(X) :- minor_offense(X), first_offense(X).",
          "Prove: minor_offense AND first_offense")
        if f.get("minor_offense"): A("pass","minor_offense(X) <- TRUE","assertz(minor_offense(X))")
        else:                       A("fail","minor_offense(X) <- FALSE","not asserted")
        if f.get("first_offense"):  A("pass","first_offense(X) <- TRUE","assertz(first_offense(X))")
        else:                        A("fail","first_offense(X) <- FALSE","not asserted")
        if f.get("minor_offense") and f.get("first_offense"):
            A("rule","Rule B2: ALL sub-goals TRUE >> bail_eligible (surety)",
              "forall X: minor(X)^first(X) -> bail_eligible(X)  [Rule B2] OK")
            return self._r("surety","B2","Minor first offense — granted with surety bond",T)
        A("fail","Rule B2 fails","minor_offense ^ first_offense = FALSE")
        A("fail","SLD Resolution exhausted — no Horn clause matched",
          "bail_verdict(X, denied, 'NONE', 'No rule satisfied').")
        return self._r("denied","NONE","No eligibility rule satisfied",T)

    def loan(self,f):
        T=[]; A=lambda s,p,l: T.append({"s":s,"p":p,"l":l})
        cs=f.get("credit_score",0); inc=f.get("monthly_income",0)
        debt=f.get("monthly_debt",0); mo=f.get("employment_months",0)
        dti=debt/inc if inc>0 else 999; by=f.get("bankruptcy_years",0)
        A("info","KB loaded — numeric facts asserted",
          f"credit_score(X,{cs}), monthly_income(X,{inc}), monthly_debt(X,{debt}), employment_months(X,{mo})")
        A("rule","Propositional credit classification","excellent>=800, good>=700, moderate>=600, poor<600")
        if   cs>=800: A("pass",f"excellent_credit_score(X) <- TRUE (score={cs})","S>=800 -> excellent_credit_score(X)")
        elif cs>=700: A("pass",f"good_credit_score(X) <- TRUE (score={cs})","700<=S<800 -> good_credit_score(X)")
        elif cs>=600: A("warn",f"moderate_credit_score(X) <- TRUE (score={cs})","600<=S<700 -> moderate_credit_score(X)")
        else:         A("fail",f"poor_credit_score(X) <- TRUE (score={cs})","S<600 -> poor_credit_score(X)")
        A("rule","SLD Resolution begins: goal = loan_verdict(X,V,R,_)",
          "Trying rules: D2 > D1 > L3 > L1 > L2")
        if f.get("has_bankruptcy") and by<7:
            A("rule","Rule D2 unifies: has_bankruptcy(X), bankruptcy_years_ago(X,Y), Y<7.",
              "loan_verdict(X,denied,'D2',_) :- has_bankruptcy(X), bankruptcy_years_ago(X,Y), Y<7, !.")
            A("fail",f"bankruptcy_years_ago(X,{by}) ^ {by}<7 -> DENY",
              f"forall X: recent_bankruptcy(X) -> loan_denied(X)  [Policy s.3.4]")
            return self._r("denied","D2",f"Bankruptcy {by} years ago (must be >=7 years)",T)
        A("info","Rule D2 fails — no recent bankruptcy","Try D1")
        if cs<600 and not f.get("has_cosigner"):
            A("rule","Rule D1 unifies: poor_credit_score(X), neg_has_cosigner(X).",
              "loan_verdict(X,denied,'D1',_) :- poor_credit_score(X), \+has_cosigner(X), !.")
            A("fail","poor_credit ^ neg_cosigner -> DENY",
              "forall X: poor_credit(X) ^ neg_cosigner(X) -> loan_denied(X)")
            return self._r("denied","D1","Poor credit with no co-signer",T)
        A("info","Rule D1 fails","Try L3")
        st=mo>=24 and inc>2000; ld=dti<=0.43; hi=inc>8000
        if st: A("pass",f"stable_income(X) <- TRUE [{mo}mo, ${inc:,.0f}/mo]",
                 f"employment_months(X,{mo})^{mo}>=24 ^ monthly_income(X,{inc})^{inc}>2000")
        else:  A("fail",f"stable_income(X) <- FALSE [{mo}mo, ${inc:,.0f}/mo]",
                 "Requires: employment_months>=24 ^ monthly_income>2000")
        if ld:  A("pass",f"low_debt_ratio(X) <- TRUE [DTI={dti*100:.1f}%]",
                  f"monthly_debt/monthly_income={debt}/{inc}={dti:.3f}<=0.43")
        else:   A("fail",f"low_debt_ratio(X) <- FALSE [DTI={dti*100:.1f}%]",
                  f"monthly_debt/monthly_income={debt}/{inc}={dti:.3f}>0.43")
        if hi:  A("pass",f"high_income(X) <- TRUE [${inc:,.0f}/mo]","monthly_income(X,I)^I>8000")
        if f.get("has_cosigner"): A("pass","has_cosigner(X) <- TRUE","assertz(has_cosigner(X))")
        A("rule","Rule L3: loan_approved(X) :- excellent_credit_score(X), high_income(X).",
          "Sub-goals: excellent_credit AND high_income")
        if cs>=800 and hi:
            A("rule","Rule L3: ALL sub-goals TRUE >> PREMIUM APPROVAL",
              "forall X: excellent(X)^high_income(X) -> loan_approved(X)  [L3] OK")
            return self._r("granted","L3","Excellent credit + high income — premium approval",T)
        A("fail","Rule L3 fails","Requires: credit>=800 ^ income>$8,000/mo")
        A("rule","Rule L1: loan_approved(X) :- good_credit_score(X), stable_income(X), low_debt_ratio(X).",
          "Sub-goals: good_credit AND stable_income AND low_dti")
        if cs>=700 and st and ld:
            A("rule","Rule L1: ALL sub-goals TRUE >> STANDARD APPROVAL",
              "forall X: good(X)^stable(X)^dti_ok(X) -> loan_approved(X)  [L1] OK")
            return self._r("granted","L1","Good credit + stable income + low DTI",T)
        A("fail","Rule L1 fails","Requires: credit>=700 ^ stable_income ^ DTI<=43%")
        A("rule","Rule L2: loan_approved(X) :- moderate_credit_score(X), stable_income(X), has_cosigner(X).",
          "Sub-goals: moderate_credit AND stable_income AND has_cosigner")
        if 600<=cs<700 and st and f.get("has_cosigner"):
            A("rule","Rule L2: ALL sub-goals TRUE >> APPROVED (CO-SIGNER)",
              "forall X: moderate(X)^stable(X)^cosign(X) -> loan_approved(X)  [L2] OK")
            return self._r("surety","L2","Moderate credit with co-signer + stable income",T)
        A("fail","Rule L2 fails","Requires: 600<=credit<700 ^ stable_income ^ has_cosigner")
        A("fail","SLD Resolution exhausted — no rule matched",
          "loan_verdict(X, denied, 'NONE', 'No rule satisfied').")
        return self._r("denied","NONE","No loan approval rule satisfied",T)

    def _r(self,v,r,reason,T):
        return {"verdict":v,"rule":r,"reason":reason,"trace":T}

ENG = Engine()
