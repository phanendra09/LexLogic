"""
LexLogic Desktop — AI Legal Reasoning System
Native Windows Application (Tkinter)
=====================================
Double-click to launch. No browser needed.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3
import json
import os
import sys
import datetime
import hashlib
import subprocess
import threading
import io

# ─────────────────────────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, "data", "cases.db")
KB_PATH   = os.path.join(BASE_DIR, "legal_kb.pl")

# ─────────────────────────────────────────────────────────────────
#  THEME COLORS  (Pure Black + Green + Orange  dashboard)
# ─────────────────────────────────────────────────────────────────
C = {
    "bg0":     "#0a0a0a",
    "bg1":     "#141414",
    "bg2":     "#1e1e1e",
    "bg3":     "#282828",
    "bg4":     "#333333",
    "border":  "#2a2a2a",
    "card":    "#161616",
    "text":    "#f0f0f0",
    "text2":   "#b0b0b0",
    "text3":   "#666666",
    "accent":  "#7ed957",
    "accent2": "#a3e87c",
    "accent3": "#2d5a1a",
    "orange":  "#e8913a",
    "orange2": "#f0a858",
    "orange3": "#5a3a16",
    "amber":   "#7ed957",
    "amber2":  "#a3e87c",
    "amber3":  "#2d5a1a",
    "green":   "#7ed957",
    "green2":  "#1e4a10",
    "red":     "#f05050",
    "red2":    "#5a1e1e",
    "yellow":  "#f0c040",
    "blue":    "#4a90e2",
    "cyan":    "#38c8d0",
    "white":   "#ffffff",
    "glow":    "#7ed95720",
}

import math

# ─────────────────────────────────────────────────────────────────
#  ANIMATED BUTTON — smooth hover with color interpolation
# ─────────────────────────────────────────────────────────────────
def _lerp_color(c1, c2, t):
    """Linearly interpolate between two hex colours."""
    r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return f"#{r:02x}{g:02x}{b:02x}"

class AnimBtn(tk.Canvas):
    """Button drawn on a Canvas with smooth hover animation & rounded rect."""
    def __init__(self, parent, text="", command=None, accent=False,
                 width=120, height=34, radius=8, font=("Segoe UI",9,"bold"),
                 bg_normal=None, bg_hover=None, fg=None, icon="", **kw):
        super().__init__(parent, width=width, height=height,
                         bg=parent.cget("bg"), highlightthickness=0, **kw)
        self._cmd = command
        self._text = text
        self._icon = icon
        self._bw = width      # _bw not _w — _w is tkinter's internal widget path!
        self._bh = height
        self._r = radius
        self._font = font
        self._bg0 = bg_normal or (C["amber"] if accent else C["bg3"])
        self._bg1 = bg_hover  or (C["amber2"] if accent else C["bg4"])
        self._fg  = fg or (C["bg0"] if accent else C["text2"])
        self._t   = 0.0
        self._anim_id = None
        self._draw(self._bg0)
        self.bind("<Enter>",      self._on_enter)
        self.bind("<Leave>",      self._on_leave)
        self.bind("<Button-1>",   self._on_click)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style="pieslice", **kw)
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style="pieslice", **kw)
        self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="pieslice", **kw)
        self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="pieslice", **kw)
        self.create_rectangle(x1+r, y1, x2-r, y2, **kw)
        self.create_rectangle(x1, y1+r, x2, y2-r, **kw)

    def _draw(self, bg):
        self.delete("all")
        self._rounded_rect(1, 1, self._bw-1, self._bh-1, self._r,
                           fill=bg, outline="")
        label = f"{self._icon}  {self._text}" if self._icon else self._text
        self.create_text(self._bw//2, self._bh//2, text=label,
                         fill=self._fg, font=self._font)

    def _on_enter(self, e):
        self._animate_to(1.0)

    def _on_leave(self, e):
        self._animate_to(0.0)

    def _animate_to(self, target):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        step = 0.12 if target > self._t else -0.12
        def tick():
            self._t += step
            if (step > 0 and self._t >= target) or (step < 0 and self._t <= target):
                self._t = target
                self._draw(_lerp_color(self._bg0, self._bg1, self._t))
                return
            self._draw(_lerp_color(self._bg0, self._bg1, max(0, min(1, self._t))))
            self._anim_id = self.after(16, tick)
        tick()

    def _on_click(self, e):
        # Flash bright then return
        self._draw(_lerp_color(self._bg1, C["white"], 0.25))
        self.after(80, lambda: self._draw(_lerp_color(self._bg0, self._bg1, self._t)))
        if self._cmd:
            self._cmd()

    def set_active(self, active):
        if active:
            self._bg0 = C["amber"]
            self._bg1 = C["amber2"]
            self._fg  = C["bg0"]
        else:
            self._bg0 = C["bg3"]
            self._bg1 = C["bg4"]
            self._fg  = C["text2"]
        self._draw(_lerp_color(self._bg0, self._bg1, self._t))

# ─────────────────────────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────────────────────────
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE,
        subject TEXT,
        module TEXT,
        verdict TEXT,
        rule TEXT,
        reason TEXT,
        facts TEXT,
        trace TEXT,
        engine TEXT,
        notes TEXT DEFAULT '',
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT
    )""")
    c.executemany("INSERT OR IGNORE INTO settings VALUES (?,?)", [
        ("judge_name",  "Hon. AI Reasoning System"),
        ("court_name",  "LexLogic Legal Reasoning Court"),
        ("auto_open_pdf","true"),
    ])
    conn.commit()
    conn.close()

def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_setting(key):
    conn = db_conn()
    row  = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else ""

def save_setting(key, val):
    conn = db_conn()
    conn.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, val))
    conn.commit(); conn.close()

# ─────────────────────────────────────────────────────────────────
#  PROLOG CHECK
# ─────────────────────────────────────────────────────────────────
def prolog_available():
    try:
        r = subprocess.run(["swipl","--version"], capture_output=True, timeout=4)
        return r.returncode == 0
    except Exception:
        return False

PROLOG_OK = prolog_available()

def run_prolog_goal(goal_str):
    script = f":- [{KB_PATH!r}].\n:- {goal_str}, halt.\n:- halt(1).\n"
    try:
        r = subprocess.run(["swipl","-q","-g","true"],
            input=script, capture_output=True, text=True, timeout=12)
        return r.stdout.strip()
    except Exception:
        return ""

# ─────────────────────────────────────────────────────────────────
#  PYTHON FOL REASONING ENGINE
# ─────────────────────────────────────────────────────────────────
class LegalEngine:
    def bail(self, f):
        trace = []
        def T(st, pred, logic):
            trace.append({"status": st, "pred": pred, "logic": logic})

        T("info", "Initialising Prolog-style KB — asserting facts", "assert_facts(Subject, FactList)")
        for key in ["local_address","has_employment","family_ties","violent_offense",
                    "capital_offense","minor_offense","first_offense","repeat_offender","weapon_involved"]:
            val = f.get(key, False)
            T("pass" if val else "skip",
              f"{key}({'TRUE' if val else 'FALSE'})",
              f"assertz({key}(X)) :- {str(val).lower()}.")

        T("rule", "── SLD Backward Chaining: goal = bail_verdict(X,V,R,Reason) ──",
          "Trying rules in priority order: B3 → B4 → B1 → B2")

        # B3
        if f.get("capital_offense"):
            T("rule",  "Rule B3 HEAD unifies: capital_offense(X)",
              "bail_verdict(X,denied,'B3',_) :- capital_offense(X), !.")
            T("fail",  "capital_offense(X) ← TRUE → cut, return denied",
              "∀X: capital_offense(X) → bail_denied(X)  [Statute §487]")
            return self._r("denied","B3","Capital offense: bail denied by statute",trace)

        T("skip", "Rule B3 body fails — capital_offense FALSE", "Backtrack → try Rule B4")

        # B4
        if f.get("violent_offense") and f.get("repeat_offender"):
            T("rule",  "Rule B4 HEAD unifies: violent ∧ repeat",
              "bail_verdict(X,denied,'B4',_) :- violent_offense(X), repeat_offender(X), !.")
            T("fail",  "Both body literals TRUE → cut, return denied",
              "∀X: violent(X) ∧ repeat(X) → bail_denied(X)")
            return self._r("denied","B4","Repeat violent offender: bail denied",trace)

        T("skip", "Rule B4 body fails", "Backtrack → try Rule B1")

        # B1 — sub-goal chain
        T("rule", "Attempting Rule B1",
          "bail_verdict(X,granted,'B1',_) :- not_flight_risk(X), not_dangerous(X), community_ties(X).")

        nfr = f.get("local_address") and (f.get("has_employment") or f.get("family_ties"))
        if nfr:
            T("pass", "Sub-goal not_flight_risk(X) PROVED",
              "has_local_address(X) ∧ (has_employment(X) ∨ has_family_ties(X)) → ¬flight_risk(X)")
        else:
            T("fail", "Sub-goal not_flight_risk(X) FAILED",
              "Requires: local_address ∧ (employment ∨ family_ties) — one or more missing")

        nd = not f.get("violent_offense") and not f.get("weapon_involved")
        if nd:
            T("pass", "Sub-goal not_dangerous(X) PROVED",
              "¬violent_offense(X) ∧ ¬weapon_involved(X) → not_dangerous(X)")
        else:
            T("fail", "Sub-goal not_dangerous(X) FAILED",
              "violent_offense(X) ∨ weapon_involved(X) is TRUE")

        ct = f.get("family_ties") or (f.get("has_employment") and f.get("community_years"))
        if ct:
            T("pass", "Sub-goal community_ties(X) PROVED",
              "has_family_ties(X) ∨ (employment(X) ∧ years_in_community(X,Y) ∧ Y≥2)")
        else:
            T("fail", "Sub-goal community_ties(X) FAILED",
              "Requires: family_ties ∨ (employment ∧ community_years≥2)")

        if nfr and nd and ct:
            T("rule", "Rule B1 — all sub-goals proved → bail_eligible(X)",
              "∀X: bail_eligible(X) ← ¬risk ∧ ¬danger ∧ ties  [B1] ✓")
            return self._r("granted","B1","Not flight risk + not dangerous + community ties",trace)

        T("skip", "Rule B1 failed — one or more sub-goals false", "Backtrack → try Rule B2")

        # B2
        T("rule","Attempting Rule B2",
          "bail_verdict(X,surety,'B2',_) :- minor_offense(X), first_offense(X).")

        if f.get("minor_offense"):
            T("pass","minor_offense(X) ← TRUE","minor_offense(X) asserted in KB")
        else:
            T("fail","minor_offense(X) ← FALSE","minor_offense(X) not asserted")

        if f.get("first_offense"):
            T("pass","first_offense(X) ← TRUE","first_offense(X) asserted in KB")
        else:
            T("fail","first_offense(X) ← FALSE","first_offense(X) not asserted")

        if f.get("minor_offense") and f.get("first_offense"):
            T("rule","Rule B2 — all sub-goals proved → bail_eligible (surety)",
              "∀X: bail_eligible(X) ← minor(X) ∧ first(X)  [B2] ✓")
            return self._r("surety","B2","Minor first offense: granted with surety bond",trace)

        T("fail","Rule B2 failed","minor_offense ∧ first_offense ← at least one FALSE")
        T("fail","SLD resolution exhausted — no rule matched",
          "bail_verdict(X,denied,'NONE',_)  :- true.")
        return self._r("denied","NONE","No eligibility rule satisfied",trace)

    def loan(self, f):
        trace = []
        def T(st, pred, logic):
            trace.append({"status": st, "pred": pred, "logic": logic})

        cs    = f.get("credit_score", 0)
        inc   = f.get("monthly_income", 0)
        debt  = f.get("monthly_debt", 0)
        months= f.get("employment_months", 0)
        dti   = debt / inc if inc > 0 else 999
        by    = f.get("bankruptcy_years", 0)

        T("info","Asserting numeric facts into KB",
          f"credit_score(X,{cs}), income(X,{inc}), debt(X,{debt}), months(X,{months})")

        # Credit classification
        T("rule","Propositional credit classification",
          "excellent≥800, good≥700, moderate≥600, poor<600")
        if cs >= 800:
            T("pass", f"excellent_credit_score(X) ← TRUE  [score={cs}]",
              "credit_score(X,S) ∧ S≥800 → excellent_credit_score(X)")
        elif cs >= 700:
            T("pass", f"good_credit_score(X) ← TRUE  [score={cs}]",
              "credit_score(X,S) ∧ 700≤S<800 → good_credit_score(X)")
        elif cs >= 600:
            T("warn", f"moderate_credit_score(X) ← TRUE  [score={cs}]",
              "credit_score(X,S) ∧ 600≤S<700 → moderate_credit_score(X)")
        else:
            T("fail", f"poor_credit_score(X) ← TRUE  [score={cs}]",
              "credit_score(X,S) ∧ S<600 → poor_credit_score(X)")

        T("rule","── SLD Backward Chaining: goal = loan_verdict(X,V,R,Reason) ──",
          "Trying rules: D2 → D1 → L3 → L1 → L2")

        # D2
        if f.get("has_bankruptcy") and by < 7:
            T("rule","Rule D2 HEAD unifies: bankruptcy + recent",
              "loan_verdict(X,denied,'D2',_) :- has_bankruptcy(X), bankruptcy_years_ago(X,Y), Y<7, !.")
            T("fail", f"bankruptcy_years_ago(X,{by}) ∧ {by}<7 → cut, return denied",
              "∀X: recent_bankruptcy(X) → loan_denied(X)  [Policy §3.4]")
            return self._r("denied","D2",f"Bankruptcy within 7 years ({by} years ago)",trace)

        T("skip","Rule D2 fails — no recent bankruptcy","Backtrack → try Rule D1")

        # D1
        if cs < 600 and not f.get("has_cosigner"):
            T("rule","Rule D1 HEAD unifies: poor_credit ∧ ¬cosigner",
              "loan_verdict(X,denied,'D1',_) :- poor_credit_score(X), \\+has_cosigner(X), !.")
            T("fail","poor_credit(X) ∧ ¬cosigner(X) → cut, return denied",
              "∀X: poor_credit(X) ∧ ¬cosigner(X) → loan_denied(X)")
            return self._r("denied","D1","Poor credit score with no co-signer",trace)

        T("skip","Rule D1 fails","Backtrack → try Rule L3")

        # Derive sub-goals
        stable  = months >= 24 and inc > 2000
        low_dti = dti <= 0.43
        high_inc= inc > 8000

        if stable:
            T("pass", f"stable_income(X) ← TRUE  [{months}mo, ${inc:,.0f}/mo]",
              f"employment_months(X,{months})≥24 ∧ monthly_income(X,{inc})>2000 → stable_income(X)")
        else:
            T("fail", "stable_income(X) ← FALSE",
              f"Required: months≥24 ∧ income>2000  (got {months}mo, ${inc:,.0f}/mo)")

        if low_dti:
            T("pass", f"low_debt_ratio(X) ← TRUE  [DTI={dti*100:.1f}%]",
              f"{debt}/{inc}={dti:.3f} ≤ 0.43 → low_debt_ratio(X)")
        else:
            T("fail", f"low_debt_ratio(X) ← FALSE  [DTI={dti*100:.1f}%]",
              f"{debt}/{inc}={dti:.3f} > 0.43 → ¬low_debt_ratio(X)")

        if high_inc:
            T("pass", f"high_income(X) ← TRUE  [${inc:,.0f}/mo]",
              "monthly_income(X,I) ∧ I>8000 → high_income(X)")

        if f.get("has_cosigner"):
            T("pass","has_cosigner(X) ← TRUE","has_cosigner(X) asserted in KB")

        # L3
        T("rule","Attempting Rule L3 (Premium)",
          "loan_verdict(X,granted,'L3',_) :- excellent_credit_score(X), high_income(X).")
        if cs >= 800 and high_inc:
            T("rule","Rule L3 — all sub-goals TRUE → loan_approved (premium)",
              "∀X: excellent(X) ∧ high_income(X) → approved(X)  [L3] ✓")
            return self._r("granted","L3","Excellent credit + high income: premium approval",trace)
        T("fail","Rule L3 fails","excellent_credit ∧ high_income ← FALSE")

        # L1
        T("rule","Attempting Rule L1 (Standard)",
          "loan_verdict(X,granted,'L1',_) :- good_credit_score(X), stable_income(X), low_debt_ratio(X).")
        if cs >= 700 and stable and low_dti:
            T("rule","Rule L1 — all sub-goals TRUE → loan_approved",
              "∀X: good(X) ∧ stable(X) ∧ dti_ok(X) → approved(X)  [L1] ✓")
            return self._r("granted","L1","Good credit + stable income + low debt ratio",trace)
        T("fail","Rule L1 fails","good_credit ∧ stable_income ∧ low_dti ← FALSE")

        # L2
        T("rule","Attempting Rule L2 (Co-signer)",
          "loan_verdict(X,granted,'L2',_) :- moderate_credit_score(X), stable_income(X), has_cosigner(X).")
        if 600 <= cs < 700 and stable and f.get("has_cosigner"):
            T("rule","Rule L2 — all sub-goals TRUE → loan_approved (surety)",
              "∀X: moderate(X) ∧ stable(X) ∧ cosign(X) → approved(X)  [L2] ✓")
            return self._r("surety","L2","Moderate credit with co-signer + stable income",trace)
        T("fail","Rule L2 fails","moderate_credit ∧ stable_income ∧ has_cosigner ← FALSE")

        T("fail","SLD resolution exhausted — no rule matched",
          "loan_verdict(X,denied,'NONE',_) :- true.")
        return self._r("denied","NONE","No loan approval rule satisfied",trace)

    def sentencing(self, f):
        trace = []
        def T(st, pred, logic):
            trace.append({"status": st, "pred": pred, "logic": logic})

        sev = f.get("offense_severity", 5)
        priors = f.get("prior_convictions", 0)

        T("info", "Initialising Sentencing KB — asserting facts",
          f"offense_severity(X,{sev}), prior_convictions(X,{priors})")

        for key in ["premeditation","weapon_involved","victim_vulnerability",
                     "shows_remorse","cooperated","first_offense","mental_health_factor"]:
            val = f.get(key, False)
            T("pass" if val else "skip",
              f"{key}({'TRUE' if val else 'FALSE'})",
              f"assertz({key}(X)) :- {str(val).lower()}.")

        # Aggravating
        agg = f.get("premeditation") or f.get("weapon_involved") or \
              f.get("victim_vulnerability") or priors >= 2
        if agg:
            T("pass", "has_aggravating(X) ← TRUE", "premeditation ∨ weapon ∨ victim_vuln ∨ priors≥2")
        else:
            T("fail", "has_aggravating(X) ← FALSE", "No aggravating factors found")

        # Mitigating
        mit = f.get("shows_remorse") or f.get("cooperated") or f.get("mental_health_factor")
        if mit:
            T("pass", "has_mitigating(X) ← TRUE", "remorse ∨ cooperated ∨ mental_health")
        else:
            T("fail", "has_mitigating(X) ← FALSE", "No mitigating factors found")

        T("rule", "── SLD Resolution: goal = sentencing_verdict(X,V,R,Reason) ──",
          "Trying rules: S4 → S3 → S1 → S2")

        # S4
        if sev >= 8 and f.get("premeditation") and f.get("weapon_involved"):
            T("rule", "Rule S4 HEAD unifies: severity≥8 ∧ premeditation ∧ weapon",
              "sentencing_verdict(X,maximum,'S4',_) :- severity≥8, premeditation(X), weapon(X), !.")
            T("fail", "All conditions TRUE → cut, return maximum",
              "∀X: severe_premeditated_armed(X) → maximum_sentence(X)")
            return self._r("maximum","S4","Maximum sentence: severe premeditated offense with weapon",trace)

        T("skip", "Rule S4 fails", "Backtrack → try S3")

        # S3
        if sev >= 6 and agg:
            T("rule", "Rule S3 HEAD unifies: severity≥6 ∧ aggravating",
              "sentencing_verdict(X,severe,'S3',_) :- severity≥6, has_aggravating(X), !.")
            T("fail", "severity≥6 ∧ aggravating → cut, return severe",
              "∀X: high_severity_aggravated(X) → severe_sentence(X)")
            return self._r("severe","S3","Severe sentence: high severity with aggravating factors",trace)

        T("skip", "Rule S3 fails", "Backtrack → try S1")

        # S1
        if sev <= 3 and mit and f.get("first_offense"):
            T("rule", "Rule S1 HEAD unifies: severity≤3 ∧ mitigating ∧ first_offense",
              "sentencing_verdict(X,minimal,'S1',_) :- severity≤3, mitigating(X), first(X), !.")
            T("pass", "All conditions TRUE → minimal sentence",
              "∀X: low_severity_mitigated_first(X) → minimal_sentence(X)")
            return self._r("minimal","S1","Minimal sentence: low severity with mitigating circumstances",trace)

        T("skip", "Rule S1 fails", "Backtrack → try S2")

        # S2
        T("rule", "Rule S2 (default moderate)",
          "sentencing_verdict(X,moderate,'S2',_) :- offense_severity(X,_), !.")
        return self._r("moderate","S2","Moderate sentence: standard guidelines apply",trace)

    def ethics(self, f):
        trace = []
        def T(st, pred, logic):
            trace.append({"status": st, "pred": pred, "logic": logic})

        rel = f.get("relationship_type", "none")
        sev = f.get("conflict_severity", 1)
        disc = f.get("disclosure_made", False)
        prior = f.get("prior_conflict", False)

        T("info", "Initialising Ethics KB — asserting facts",
          f"relationship_type(X,{rel}), conflict_severity(X,{sev})")
        T("pass" if disc else "skip", f"disclosure_made({'TRUE' if disc else 'FALSE'})",
          f"assertz(disclosure_made(X)) :- {str(disc).lower()}.")
        T("pass" if prior else "skip", f"prior_conflict({'TRUE' if prior else 'FALSE'})",
          f"assertz(prior_conflict(X)) :- {str(prior).lower()}.")

        T("rule", "── SLD Resolution: goal = ethics_verdict(X,V,R,Reason) ──",
          "Trying rules: E3 → E2 → E1 → CLEAR")

        # E3
        if rel in ("family","financial") and sev >= 4 and not disc:
            T("rule", "Rule E3 HEAD unifies: family/financial ∧ severity≥4 ∧ ¬disclosed",
              "ethics_verdict(X,disqualification,'E3',_) :- rel(X,T), T∈{family,financial}, sev≥4, ¬disclosed, !.")
            T("fail", "Undisclosed serious conflict → disqualification",
              "∀X: undisclosed_serious(X) → disqualified(X)")
            return self._r("disqualification","E3","Disqualification: undisclosed serious conflict",trace)

        T("skip", "Rule E3 fails", "Backtrack → try E2")

        # E2
        if rel != "none" and prior:
            T("rule", "Rule E2 HEAD unifies: relationship ∧ prior_conflict",
              "ethics_verdict(X,recusal,'E2',_) :- rel(X,T), T≠none, prior_conflict(X), !.")
            T("fail", "Prior conflict with active relationship → recusal",
              "∀X: prior_conflict_relationship(X) → recusal_required(X)")
            return self._r("recusal","E2","Recusal required: prior conflict with active relationship",trace)

        T("skip", "Rule E2 fails", "Backtrack → try E1")

        # E1
        if rel != "none" and disc and sev <= 2:
            T("rule", "Rule E1 HEAD unifies: relationship ∧ disclosed ∧ severity≤2",
              "ethics_verdict(X,waivable,'E1',_) :- rel(X,T), T≠none, disclosed(X), sev≤2, !.")
            T("pass", "Minor disclosed conflict → waivable",
              "∀X: disclosed_minor(X) → conflict_waivable(X)")
            return self._r("waivable","E1","Conflict waivable: disclosed minor relationship",trace)

        T("skip", "Rule E1 fails", "Default → clear")
        T("pass", "No conflict of interest detected",
          "ethics_verdict(X,clear,'NONE',_) :- true.")
        return self._r("clear","NONE","No conflict of interest detected",trace)

    def _r(self, verdict, rule, reason, trace):
        return {"verdict":verdict, "rule":rule, "reason":reason, "trace":trace}

engine = LegalEngine()

# ─────────────────────────────────────────────────────────────────
#  LIGHT THEME
# ─────────────────────────────────────────────────────────────────
C_LIGHT = {
    "bg0": "#f2f2f0", "bg1": "#e8e8e5", "bg2": "#ddddd8",
    "bg3": "#d0d0cb", "bg4": "#c3c3be", "border": "#b0b0a8",
    "card": "#eeeeeb",
    "text": "#1a1a1a", "text2": "#3a3a3a", "text3": "#6a6a6a",
    "accent": "#3a8a20", "accent2": "#4da830", "accent3": "#c8e8c0",
    "orange": "#c07020", "orange2": "#d88838", "orange3": "#f0d8c0",
    "amber": "#3a8a20", "amber2": "#4da830", "amber3": "#c8e8c0",
    "green": "#2a7a18", "green2": "#c8e6c9",
    "red": "#b71c1c", "red2": "#ffcdd2",
    "yellow": "#f9a825", "blue": "#2860b0", "cyan": "#1898a0",
    "white": "#ffffff", "glow": "#3a8a2020",
}

# ─────────────────────────────────────────────────────────────────
#  FORM TEMPLATES
# ─────────────────────────────────────────────────────────────────
TEMPLATES = {
    "bail": {
        "Standard Release Candidate": {
            "local_address": True, "has_employment": True, "family_ties": True,
            "community_years": True, "minor_offense": False, "first_offense": True,
            "violent_offense": False, "capital_offense": False,
            "repeat_offender": False, "weapon_involved": False,
        },
        "High-Risk Violent": {
            "local_address": False, "has_employment": False, "family_ties": False,
            "community_years": False, "minor_offense": False, "first_offense": False,
            "violent_offense": True, "capital_offense": False,
            "repeat_offender": True, "weapon_involved": True,
        },
        "Minor First Offender": {
            "local_address": True, "has_employment": True, "family_ties": True,
            "community_years": True, "minor_offense": True, "first_offense": True,
            "violent_offense": False, "capital_offense": False,
            "repeat_offender": False, "weapon_involved": False,
        },
    },
    "loan": {
        "Prime Borrower": {
            "credit_score": "810", "monthly_income": "12000",
            "monthly_debt": "2000", "employment_months": "60",
            "has_cosigner": False, "has_bankruptcy": False,
        },
        "Borderline Cosigner": {
            "credit_score": "640", "monthly_income": "4500",
            "monthly_debt": "1500", "employment_months": "30",
            "has_cosigner": True, "has_bankruptcy": False,
        },
        "Risky Applicant": {
            "credit_score": "520", "monthly_income": "2800",
            "monthly_debt": "1800", "employment_months": "10",
            "has_cosigner": False, "has_bankruptcy": True,
        },
    },
    "sentencing": {
        "Low Severity First Offender": {
            "offense_severity": 2, "prior_convictions": 0,
            "premeditation": False, "weapon_involved": False,
            "victim_vulnerability": False, "shows_remorse": True,
            "cooperated": True, "first_offense": True, "mental_health_factor": False,
        },
        "Severe Premeditated": {
            "offense_severity": 9, "prior_convictions": 3,
            "premeditation": True, "weapon_involved": True,
            "victim_vulnerability": True, "shows_remorse": False,
            "cooperated": False, "first_offense": False, "mental_health_factor": False,
        },
    },
    "ethics": {
        "Minor Disclosed": {
            "relationship_type": "professional", "conflict_severity": 1,
            "disclosure_made": True, "prior_conflict": False,
        },
        "Serious Undisclosed Family": {
            "relationship_type": "family", "conflict_severity": 5,
            "disclosure_made": False, "prior_conflict": True,
        },
    },
}

# ─────────────────────────────────────────────────────────────────
#  PDF GENERATOR
# ─────────────────────────────────────────────────────────────────
def generate_pdf(case_data, path):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        doc = SimpleDocTemplate(path, pagesize=letter,
            leftMargin=0.8*inch, rightMargin=0.8*inch,
            topMargin=0.7*inch, bottomMargin=0.7*inch)

        judge = get_setting("judge_name")
        court = get_setting("court_name")
        verdict = case_data.get("verdict","unknown")
        vcolor = colors.HexColor("#1f5c38") if verdict=="granted" else \
                 colors.HexColor("#7a5a1a") if verdict=="surety"  else \
                 colors.HexColor("#7a2020")

        ts = ParagraphStyle
        title_s  = ts('T', fontSize=18, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)
        sub_s    = ts('S', fontSize=9,  fontName='Helvetica', alignment=TA_CENTER, spaceAfter=2,
                      textColor=colors.grey)
        h1_s     = ts('H1',fontSize=11, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=5,
                      textColor=colors.HexColor("#1c2033"))
        body_s   = ts('B', fontSize=9,  fontName='Helvetica', spaceAfter=4, leading=14)
        mono_s   = ts('M', fontSize=8,  fontName='Courier',   spaceAfter=2, leading=12,
                      textColor=colors.HexColor("#2e3450"))
        verdict_s= ts('V', fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER,
                      textColor=colors.white)

        story = []
        story.append(Paragraph(court, sub_s))
        story.append(Paragraph("LEGAL REASONING SYSTEM — CASE REPORT", title_s))
        story.append(Paragraph(
            f"Case ID: {case_data.get('case_id','N/A')}  |  "
            f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}", sub_s))
        story.append(HRFlowable(width="100%", thickness=2,
            color=colors.HexColor("#b8975a"), spaceAfter=12))

        vtext = {"granted":"✓  BAIL / LOAN GRANTED",
                 "surety":"⚖  GRANTED WITH CONDITIONS",
                 "denied":"✗  DENIED"}.get(verdict,"INCONCLUSIVE")
        vt = Table([[Paragraph(vtext, verdict_s)]], colWidths=[6.4*inch])
        vt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),vcolor),
            ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
        ]))
        story.append(vt)
        story.append(Spacer(1,12))

        story.append(Paragraph("CASE INFORMATION", h1_s))
        info = [
            ["Subject",  case_data.get("subject","—"),  "Module",  case_data.get("module","—").title()],
            ["Rule",     case_data.get("rule","—"),      "Engine",  case_data.get("engine","—")],
            ["Reason",   case_data.get("reason","—"),    "Date",    (case_data.get("created_at","—") or "")[:19]],
        ]
        it = Table(info, colWidths=[1.1*inch, 2.1*inch, 1.1*inch, 2.1*inch])
        it.setStyle(TableStyle([
            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
            ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#f0f0f0")),
            ("BACKGROUND",(2,0),(2,-1),colors.HexColor("#f0f0f0")),
            ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#dddddd")),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(it)
        story.append(Spacer(1,10))

        story.append(Paragraph("KNOWLEDGE BASE FACTS", h1_s))
        facts = json.loads(case_data.get("facts","{}"))
        fd = [[k.replace("_"," ").title(), str(v)] for k,v in facts.items()]
        if fd:
            ft = Table(fd, colWidths=[3.2*inch, 3.2*inch])
            ft.setStyle(TableStyle([
                ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),8),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#dddddd")),
                ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white, colors.HexColor("#f9f7f4")]),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),8),
            ]))
            story.append(ft)
        story.append(Spacer(1,10))

        story.append(Paragraph("INFERENCE TRACE (SLD Resolution)", h1_s))
        trace = json.loads(case_data.get("trace","[]"))
        for i, step in enumerate(trace):
            sym = {"pass":"[PASS]","fail":"[FAIL]","rule":"[RULE]",
                   "info":"[INFO]","warn":"[WARN]","skip":"[SKIP]"}.get(step.get("status",""),"[    ]")
            col = {"pass":"#1f5c38","fail":"#7a2020","rule":"#1c2033",
                   "info":"#555555","warn":"#7a5a1a","skip":"#888888"}.get(step.get("status",""),"#333")
            story.append(Paragraph(
                f'<font color="{col}"><b>{i+1:02d}. {sym}</b> {step.get("pred","")}</font>', body_s))
            story.append(Paragraph(
                f'&nbsp;&nbsp;&nbsp;&nbsp;<font color="#888888">{step.get("logic","")}</font>', mono_s))

        story.append(Spacer(1,14))
        story.append(HRFlowable(width="100%", thickness=1,
            color=colors.HexColor("#cccccc"), spaceAfter=8))
        story.append(Paragraph(
            f"Issued by: {judge}  |  LexLogic AI Legal Reasoning System v2.0", sub_s))

        if case_data.get("notes","").strip():
            story.append(Spacer(1,8))
            story.append(Paragraph("NOTES", h1_s))
            story.append(Paragraph(case_data["notes"], body_s))

        doc.build(story)
        return True
    except ImportError:
        return False
    except Exception as e:
        return str(e)

# ─────────────────────────────────────────────────────────────────
#  MAIN APPLICATION WINDOW
# ─────────────────────────────────────────────────────────────────
class LexLogicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LexLogic — AI Legal Reasoning System  v3.0")
        self.geometry("1360x860")
        self.minsize(960, 660)
        self.configure(bg=C["bg0"])

        # Set icon if available
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self.current_module = tk.StringVar(value="bail")
        self.current_case_id = None
        self.last_result = None
        self.is_dark_theme = True
        self._pulse_phase = 0

        init_db()
        self._build_ui()
        self._apply_styles()
        self._update_clock()
        self._check_engine_status()
        self._start_pulse()

    # ── TTK STYLES ──────────────────────────────────────────────
    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TNotebook",           background=C["bg0"], borderwidth=0)
        style.configure("TNotebook.Tab",
            background=C["bg2"], foreground=C["text3"],
            padding=[18,8], font=("Segoe UI",9,"bold"))
        style.map("TNotebook.Tab",
            background=[("selected",C["bg3"])],
            foreground=[("selected",C["accent"])])

        style.configure("Treeview",
            background=C["bg1"], foreground=C["text2"],
            fieldbackground=C["bg1"], rowheight=30,
            font=("Consolas",9))
        style.configure("Treeview.Heading",
            background=C["bg2"], foreground=C["text3"],
            font=("Segoe UI",8,"bold"), relief="flat")
        style.map("Treeview",
            background=[("selected",C["bg3"])],
            foreground=[("selected",C["accent"])])

        style.configure("Vertical.TScrollbar",
            background=C["bg2"], troughcolor=C["bg1"],
            borderwidth=0, arrowcolor=C["text3"])

        style.configure("TSeparator", background=C["border"])

    # ── BUILD UI ─────────────────────────────────────────────────
    def _build_ui(self):
        # Title bar
        self._build_titlebar()
        # Main notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)
        self._build_inference_tab()
        self._build_history_tab()
        self._build_analytics_tab()
        self._build_rules_tab()
        self._build_settings_tab()
        # Status bar
        self._build_statusbar()

    # ── TITLE BAR ────────────────────────────────────────────────
    def _build_titlebar(self):
        tb = tk.Frame(self, bg=C["bg0"], height=52)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Logo
        tk.Label(tb, text="⚖", bg=C["bg0"], fg=C["accent"],
                 font=("Segoe UI Emoji",18)).pack(side="left", padx=(14,4))
        tk.Label(tb, text="LexLogic", bg=C["bg0"], fg=C["white"],
                 font=("Segoe UI",14,"bold")).pack(side="left")
        tk.Label(tb, text="  AI Legal Reasoning", bg=C["bg0"], fg=C["text3"],
                 font=("Segoe UI",9)).pack(side="left")

        # Right side
        self.theme_btn = tk.Button(tb, text="☀", bg=C["bg0"], fg=C["accent"],
            font=("Segoe UI",13), relief="flat", bd=0, padx=6,
            command=self._toggle_theme, activebackground=C["bg0"])
        self.theme_btn.pack(side="right", padx=(0,10))

        self.clock_lbl = tk.Label(tb, text="", bg=C["bg0"], fg=C["text3"],
                                  font=("Consolas",8))
        self.clock_lbl.pack(side="right", padx=(0,14))

        # Pulsing engine dot
        self.eng_canvas = tk.Canvas(tb, width=12, height=12, bg=C["bg0"], highlightthickness=0)
        self.eng_canvas.pack(side="right", padx=(0,4))
        self.eng_lbl = tk.Label(tb, text="…", bg=C["bg0"], fg=C["text3"],
                                font=("Consolas",8))
        self.eng_lbl.pack(side="right", padx=(0,2))
        tk.Label(tb, text="Engine:", bg=C["bg0"], fg=C["text3"],
                 font=("Consolas",7)).pack(side="right", padx=(8,2))

        # Bottom green accent line
        tk.Frame(self, bg=C["accent"], height=2).pack(fill="x")

    def _start_pulse(self):
        """Animate pulsing dot for engine status."""
        self._pulse_phase += 0.15
        brightness = 0.5 + 0.5 * math.sin(self._pulse_phase)
        col = _lerp_color(C["green2"], C["green"], brightness)
        self.eng_canvas.delete("all")
        self.eng_canvas.create_oval(2, 2, 12, 12, fill=col, outline="")
        self.after(200, self._start_pulse)

    # ── INFERENCE TAB ────────────────────────────────────────────
    def _build_inference_tab(self):
        frame = tk.Frame(self.nb, bg=C["bg0"])
        self.nb.add(frame, text="  ⚖  Inference  ")

        pane = tk.PanedWindow(frame, orient="horizontal", bg=C["bg0"],
                               sashwidth=4, sashrelief="flat")
        pane.pack(fill="both", expand=True)

        # ── LEFT INPUT PANEL ──
        left = tk.Frame(pane, bg=C["bg1"], width=320)
        pane.add(left, minsize=280)

        # Module selector
        mod_frame = tk.Frame(left, bg=C["bg2"], pady=4)
        mod_frame.pack(fill="x")
        tk.Label(mod_frame, text="MODULE", bg=C["bg2"], fg=C["text3"],
                 font=("Consolas",7,"bold")).pack(side="left", padx=(12,6), pady=6)

        self.bail_btn = AnimBtn(mod_frame, text="BAIL", icon="⚖", accent=True,
            width=80, height=30, font=("Segoe UI",8,"bold"),
            command=lambda: self._switch_module("bail"))
        self.bail_btn.pack(side="left", padx=3, pady=4)

        self.loan_btn = AnimBtn(mod_frame, text="LOAN", icon="$",
            width=80, height=30, font=("Segoe UI",8,"bold"),
            command=lambda: self._switch_module("loan"))
        self.loan_btn.pack(side="left", padx=3, pady=4)

        self.sent_btn = AnimBtn(mod_frame, text="SENTENCE", icon="⚖",
            width=100, height=30, font=("Segoe UI",8,"bold"),
            command=lambda: self._switch_module("sentencing"))
        self.sent_btn.pack(side="left", padx=3, pady=4)

        self.ethics_btn = AnimBtn(mod_frame, text="ETHICS", icon="⚠",
            width=90, height=30, font=("Segoe UI",8,"bold"),
            command=lambda: self._switch_module("ethics"))
        self.ethics_btn.pack(side="left", padx=3, pady=4)

        # Gold divider
        tk.Canvas(left, bg=C["bg1"], height=2, highlightthickness=0).pack(fill="x")

        # Template presets
        tpl_frame = tk.Frame(left, bg=C["bg2"])
        tpl_frame.pack(fill="x")
        tk.Label(tpl_frame, text="PRESET", bg=C["bg2"], fg=C["text3"],
                 font=("Consolas",7)).pack(side="left", padx=10, pady=4)
        self.template_var = tk.StringVar(value="— Select Template —")
        self.template_combo = ttk.Combobox(tpl_frame, textvariable=self.template_var,
            state="readonly", font=("Consolas",8), width=28)
        self.template_combo.pack(side="left", padx=4, pady=4)
        self.template_combo.bind("<<ComboboxSelected>>", self._apply_template)
        self._update_template_list()

        # Scrollable input area
        canvas = tk.Canvas(left, bg=C["bg1"], highlightthickness=0)
        sb = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        self.input_scroll_frame = tk.Frame(canvas, bg=C["bg1"])
        self.input_scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.input_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # Subject name
        self._section_label(self.input_scroll_frame, "SUBJECT")
        self.subject_var = tk.StringVar()
        e = tk.Entry(self.input_scroll_frame, textvariable=self.subject_var,
            bg=C["bg2"], fg=C["text"], insertbackground=C["amber"],
            relief="flat", font=("Segoe UI",10), bd=1)
        e.insert(0, "e.g. Alice Johnson")
        e.bind("<FocusIn>",  lambda ev: e.delete(0,"end") if e.get().startswith("e.g.") else None)
        e.pack(fill="x", padx=10, pady=(0,8))

        # Bail form
        self.bail_frame = tk.Frame(self.input_scroll_frame, bg=C["bg1"])
        self._build_bail_form(self.bail_frame)
        self.bail_frame.pack(fill="x")

        # Loan form
        self.loan_frame = tk.Frame(self.input_scroll_frame, bg=C["bg1"])
        self._build_loan_form(self.loan_frame)

        # Sentencing form
        self.sent_frame = tk.Frame(self.input_scroll_frame, bg=C["bg1"])
        self._build_sentencing_form(self.sent_frame)

        # Ethics form
        self.ethics_frame = tk.Frame(self.input_scroll_frame, bg=C["bg1"])
        self._build_ethics_form(self.ethics_frame)

        # Notes
        self._section_label(self.input_scroll_frame, "CASE NOTES (optional)")
        self.notes_var = tk.Text(self.input_scroll_frame, height=3,
            bg=C["bg2"], fg=C["text2"], insertbackground=C["amber"],
            relief="flat", font=("Consolas",8), bd=1, wrap="word")
        self.notes_var.pack(fill="x", padx=10, pady=(0,10))

        # Run button (animated)
        run_f = tk.Frame(left, bg=C["bg1"])
        run_f.pack(fill="x", padx=10, pady=8)
        self.run_btn = AnimBtn(run_f, text="RUN LEGAL INFERENCE", icon="▶", accent=True,
            width=300, height=42, radius=10, font=("Segoe UI",11,"bold"),
            command=self._run_inference)
        self.run_btn.pack(fill="x")
        tk.Label(run_f, text="Ctrl+Enter", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",7)).pack(pady=2)

        # ── RIGHT RESULTS PANEL ──
        right = tk.Frame(pane, bg=C["bg0"])
        pane.add(right, minsize=400)

        # Verdict strip
        self.verdict_frame = tk.Frame(right, bg=C["bg1"], height=100)
        self.verdict_frame.pack(fill="x")
        self.verdict_frame.pack_propagate(False)
        self._show_placeholder_verdict()

        # Result notebook (trace, facts, FOL)
        self.result_nb = ttk.Notebook(right)
        self.result_nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.trace_frame = tk.Frame(self.result_nb, bg=C["bg0"])
        self.result_nb.add(self.trace_frame, text="  Inference Trace  ")

        self.facts_frame = tk.Frame(self.result_nb, bg=C["bg0"])
        self.result_nb.add(self.facts_frame, text="  Facts Asserted  ")

        self.fol_frame = tk.Frame(self.result_nb, bg=C["bg0"])
        self.result_nb.add(self.fol_frame, text="  Logic Summary  ")

        self._build_trace_panel()
        self._build_facts_panel()
        self._build_fol_panel()

    def _build_bail_form(self, parent):
        self._section_label(parent, "RESIDENCE & COMMUNITY")
        self.bail_vars = {}
        bail_flags = [
            ("local_address",   "📍  Local Address"),
            ("has_employment",  "💼  Employment"),
            ("family_ties",     "👨‍👩‍👦  Family Ties"),
            ("community_years", "🏘️  Community 2+ Years"),
        ]
        g = tk.Frame(parent, bg=C["bg1"])
        g.pack(fill="x", padx=10)
        for i, (k,label) in enumerate(bail_flags):
            v = tk.BooleanVar()
            self.bail_vars[k] = v
            cb = tk.Checkbutton(g, text=label, variable=v,
                bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"],
                activebackground=C["bg2"], activeforeground=C["amber"],
                font=("Segoe UI",9), relief="flat", anchor="w",
                onvalue=True, offvalue=False,
                indicatoron=True)
            cb.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=2)
        g.columnconfigure(0, weight=1)
        g.columnconfigure(1, weight=1)

        self._section_label(parent, "OFFENSE PROFILE")
        offense_flags = [
            ("minor_offense",   "📝  Minor Offense"),
            ("first_offense",   "1️⃣   First Offense"),
            ("violent_offense", "⚠️  Violent Offense"),
            ("capital_offense", "☠️  Capital Offense"),
            ("repeat_offender", "🔄  Repeat Offender"),
            ("weapon_involved", "🔫  Weapon Involved"),
        ]
        g2 = tk.Frame(parent, bg=C["bg1"])
        g2.pack(fill="x", padx=10)
        for i, (k,label) in enumerate(offense_flags):
            v = tk.BooleanVar()
            self.bail_vars[k] = v
            cb = tk.Checkbutton(g2, text=label, variable=v,
                bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"],
                activebackground=C["bg2"], activeforeground=C["amber"],
                font=("Segoe UI",9), relief="flat", anchor="w",
                indicatoron=True)
            cb.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=2)
        g2.columnconfigure(0, weight=1)
        g2.columnconfigure(1, weight=1)

    def _build_loan_form(self, parent):
        self._section_label(parent, "FINANCIAL PROFILE")
        fields = [
            ("credit_score",      "Credit Score (300–850)",   "720"),
            ("monthly_income",    "Monthly Income ($)",        "5000"),
            ("monthly_debt",      "Monthly Debt ($)",          "1200"),
            ("employment_months", "Employment (months)",       "36"),
        ]
        self.loan_vars = {}
        for k, label, placeholder in fields:
            tk.Label(parent, text=label, bg=C["bg1"], fg=C["text3"],
                     font=("Consolas",8)).pack(anchor="w", padx=10, pady=(4,1))
            v = tk.StringVar()
            self.loan_vars[k] = v
            e = tk.Entry(parent, textvariable=v, bg=C["bg2"], fg=C["text"],
                insertbackground=C["amber"], relief="flat",
                font=("Segoe UI",10), bd=1)
            e.insert(0, placeholder)
            e.bind("<FocusIn>",
                lambda ev, ph=placeholder: ev.widget.delete(0,"end")
                    if ev.widget.get()==ph else None)
            e.pack(fill="x", padx=10, pady=(0,2))

        self._section_label(parent, "ADDITIONAL FACTORS")
        self.loan_bool_vars = {}
        extra_flags = [
            ("has_cosigner",  "👤  Has Co-signer"),
            ("has_bankruptcy","⚠️  Has Bankruptcy"),
        ]
        g = tk.Frame(parent, bg=C["bg1"])
        g.pack(fill="x", padx=10)
        for i, (k,label) in enumerate(extra_flags):
            v = tk.BooleanVar()
            self.loan_bool_vars[k] = v
            cb = tk.Checkbutton(g, text=label, variable=v,
                bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"],
                activebackground=C["bg2"], activeforeground=C["amber"],
                font=("Segoe UI",9), relief="flat", anchor="w",
                command=self._on_bankruptcy_toggle)
            cb.grid(row=0, column=i, sticky="ew", padx=2, pady=2)
        g.columnconfigure(0, weight=1)
        g.columnconfigure(1, weight=1)

        self.bk_frame = tk.Frame(parent, bg=C["bg1"])
        tk.Label(self.bk_frame, text="Bankruptcy Years Ago", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="w", padx=10, pady=(4,1))
        self.bk_years_var = tk.StringVar(value="4")
        tk.Entry(self.bk_frame, textvariable=self.bk_years_var, bg=C["bg2"],
            fg=C["text"], insertbackground=C["amber"], relief="flat",
            font=("Segoe UI",10), bd=1, width=10).pack(anchor="w", padx=10)

    def _on_bankruptcy_toggle(self):
        if self.loan_bool_vars.get("has_bankruptcy",tk.BooleanVar()).get():
            self.bk_frame.pack(fill="x", before=self.bk_frame.master.winfo_children()[-1]
                                if self.bk_frame.master.winfo_children() else None)
        else:
            self.bk_frame.pack_forget()

    def _section_label(self, parent, text):
        f = tk.Frame(parent, bg=C["bg1"])
        f.pack(fill="x", padx=10, pady=(12,4))
        tk.Label(f, text="●", bg=C["bg1"], fg=C["amber"],
                 font=("Segoe UI",5)).pack(side="left", padx=(0,5))
        tk.Label(f, text=text, bg=C["bg1"], fg=C["amber3"],
                 font=("Consolas",7,"bold")).pack(side="left")
        div = tk.Canvas(f, bg=C["bg1"], height=1, highlightthickness=0)
        div.pack(side="left", fill="x", expand=True, padx=8)
        div.create_line(0, 0, 1000, 0, fill=C["border"], dash=(2,4))

    def _switch_module(self, mod):
        self.current_module.set(mod)
        all_btns = {
            "bail": self.bail_btn, "loan": self.loan_btn,
            "sentencing": self.sent_btn, "ethics": self.ethics_btn
        }
        all_frames = {
            "bail": self.bail_frame, "loan": self.loan_frame,
            "sentencing": self.sent_frame, "ethics": self.ethics_frame
        }
        for k, btn in all_btns.items():
            btn.set_active(k == mod)
        for k, frm in all_frames.items():
            if k == mod:
                frm.pack(fill="x")
            else:
                frm.pack_forget()
        self._update_template_list()
        self.sb_module.config(text=f"Module: {mod.title()}")

    def _update_template_list(self):
        mod = self.current_module.get()
        tpls = list(TEMPLATES.get(mod, {}).keys())
        self.template_combo["values"] = ["— Select Template —"] + tpls
        self.template_var.set("— Select Template —")

    def _apply_template(self, event=None):
        name = self.template_var.get()
        if name == "— Select Template —":
            return
        mod = self.current_module.get()
        tpl = TEMPLATES.get(mod, {}).get(name, {})
        if not tpl:
            return
        if mod == "bail":
            for k, v in tpl.items():
                if k in self.bail_vars:
                    self.bail_vars[k].set(v)
        elif mod == "loan":
            for k, v in tpl.items():
                if k in self.loan_vars:
                    self.loan_vars[k].delete(0, "end")
                    self.loan_vars[k].insert(0, str(v))
                elif k in self.loan_bool_vars:
                    self.loan_bool_vars[k].set(v)
            self._on_bankruptcy_toggle()
        elif mod == "sentencing":
            for k, v in tpl.items():
                if k in self.sent_vars:
                    self.sent_vars[k].set(v)
                elif k in self.sent_scale_vars:
                    self.sent_scale_vars[k].set(v)
        elif mod == "ethics":
            for k, v in tpl.items():
                if k in self.ethics_vars:
                    self.ethics_vars[k].set(v)
                elif k in self.ethics_bool_vars:
                    self.ethics_bool_vars[k].set(v)

    def _build_sentencing_form(self, parent):
        self.sent_vars = {}
        self.sent_scale_vars = {}

        self._section_label(parent, "OFFENSE DETAILS")
        tk.Label(parent, text="Offense Severity (1–10)", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="w", padx=10, pady=(4,1))
        self.sent_scale_vars["offense_severity"] = tk.IntVar(value=5)
        sev_f = tk.Frame(parent, bg=C["bg1"])
        sev_f.pack(fill="x", padx=10)
        tk.Scale(sev_f, from_=1, to=10, orient="horizontal",
            variable=self.sent_scale_vars["offense_severity"],
            bg=C["bg1"], fg=C["amber"], troughcolor=C["bg3"],
            highlightthickness=0, font=("Consolas",8),
            activebackground=C["amber2"], length=200).pack(side="left", fill="x", expand=True)

        tk.Label(parent, text="Prior Convictions", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="w", padx=10, pady=(4,1))
        self.sent_scale_vars["prior_convictions"] = tk.IntVar(value=0)
        tk.Scale(parent, from_=0, to=10, orient="horizontal",
            variable=self.sent_scale_vars["prior_convictions"],
            bg=C["bg1"], fg=C["amber"], troughcolor=C["bg3"],
            highlightthickness=0, font=("Consolas",8),
            activebackground=C["amber2"], length=200).pack(fill="x", padx=10)

        self._section_label(parent, "AGGRAVATING FACTORS")
        agg_flags = [
            ("premeditation",       "🎯  Premeditation"),
            ("weapon_involved",     "🔫  Weapon Involved"),
            ("victim_vulnerability","🛡️  Victim Vulnerability"),
        ]
        g = tk.Frame(parent, bg=C["bg1"])
        g.pack(fill="x", padx=10)
        for i, (k, label) in enumerate(agg_flags):
            v = tk.BooleanVar()
            self.sent_vars[k] = v
            cb = tk.Checkbutton(g, text=label, variable=v,
                bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"],
                activebackground=C["bg2"], activeforeground=C["amber"],
                font=("Segoe UI",9), relief="flat", anchor="w")
            cb.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=2)
        g.columnconfigure(0, weight=1)
        g.columnconfigure(1, weight=1)

        self._section_label(parent, "MITIGATING FACTORS")
        mit_flags = [
            ("shows_remorse",       "😔  Shows Remorse"),
            ("cooperated",          "🤝  Cooperated"),
            ("first_offense",       "1️⃣   First Offense"),
            ("mental_health_factor","🧠  Mental Health Factor"),
        ]
        g2 = tk.Frame(parent, bg=C["bg1"])
        g2.pack(fill="x", padx=10)
        for i, (k, label) in enumerate(mit_flags):
            v = tk.BooleanVar()
            self.sent_vars[k] = v
            cb = tk.Checkbutton(g2, text=label, variable=v,
                bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"],
                activebackground=C["bg2"], activeforeground=C["amber"],
                font=("Segoe UI",9), relief="flat", anchor="w")
            cb.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=2)
        g2.columnconfigure(0, weight=1)
        g2.columnconfigure(1, weight=1)

    def _build_ethics_form(self, parent):
        self.ethics_vars = {}
        self.ethics_bool_vars = {}

        self._section_label(parent, "RELATIONSHIP")
        tk.Label(parent, text="Relationship Type", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="w", padx=10, pady=(4,1))
        self.ethics_vars["relationship_type"] = tk.StringVar(value="none")
        rel_f = tk.Frame(parent, bg=C["bg1"])
        rel_f.pack(fill="x", padx=10)
        for rt in ["none", "professional", "financial", "family"]:
            tk.Radiobutton(rel_f, text=rt.title(), variable=self.ethics_vars["relationship_type"],
                value=rt, bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"],
                activebackground=C["bg2"], activeforeground=C["amber"],
                font=("Segoe UI",9)).pack(side="left", padx=4, pady=2)

        self._section_label(parent, "CONFLICT DETAILS")
        tk.Label(parent, text="Conflict Severity (1–5)", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="w", padx=10, pady=(4,1))
        self.ethics_vars["conflict_severity"] = tk.IntVar(value=1)
        tk.Scale(parent, from_=1, to=5, orient="horizontal",
            variable=self.ethics_vars["conflict_severity"],
            bg=C["bg1"], fg=C["amber"], troughcolor=C["bg3"],
            highlightthickness=0, font=("Consolas",8),
            activebackground=C["amber2"], length=200).pack(fill="x", padx=10)

        flags = [
            ("disclosure_made", "📋  Disclosure Made"),
            ("prior_conflict",  "⚠️  Prior Conflict"),
        ]
        g = tk.Frame(parent, bg=C["bg1"])
        g.pack(fill="x", padx=10)
        for i, (k, label) in enumerate(flags):
            v = tk.BooleanVar()
            self.ethics_bool_vars[k] = v
            cb = tk.Checkbutton(g, text=label, variable=v,
                bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"],
                activebackground=C["bg2"], activeforeground=C["amber"],
                font=("Segoe UI",9), relief="flat", anchor="w")
            cb.grid(row=0, column=i, sticky="ew", padx=2, pady=2)
        g.columnconfigure(0, weight=1)
        g.columnconfigure(1, weight=1)

    # ── TRACE PANEL ─────────────────────────────────────────────
    def _build_trace_panel(self):
        self.trace_text = scrolledtext.ScrolledText(
            self.trace_frame, bg=C["bg0"], fg=C["text2"],
            font=("Consolas",9), relief="flat", wrap="word",
            insertbackground=C["amber"], state="disabled",
            selectbackground=C["bg3"])
        self.trace_text.pack(fill="both", expand=True, padx=0, pady=0)
        # Tags
        self.trace_text.tag_config("pass",  foreground=C["green"])
        self.trace_text.tag_config("fail",  foreground=C["red"])
        self.trace_text.tag_config("rule",  foreground=C["amber"])
        self.trace_text.tag_config("warn",  foreground=C["yellow"])
        self.trace_text.tag_config("info",  foreground=C["text3"])
        self.trace_text.tag_config("skip",  foreground=C["text3"])
        self.trace_text.tag_config("logic", foreground=C["text3"],
            font=("Consolas",8))
        self.trace_text.tag_config("num",   foreground=C["amber3"],
            font=("Consolas",8,"bold"))
        self.trace_text.tag_config("step_rule", background=C["bg2"])
        self.trace_text.tag_config("header", foreground=C["amber"],
            font=("Consolas",10,"bold"))
        self.trace_text.tag_config("ph",    foreground=C["text3"],
            font=("Segoe UI",11), justify="center")

        self._show_placeholder_trace()

    def _show_placeholder_trace(self):
        self.trace_text.config(state="normal")
        self.trace_text.delete("1.0","end")
        self.trace_text.insert("end",
            "\n\n\n       ⚖   Awaiting case input\n\n"
            "       Enter facts in the left panel\n"
            "       and press RUN LEGAL INFERENCE\n", "ph")
        self.trace_text.config(state="disabled")

    def _build_facts_panel(self):
        self.facts_text = scrolledtext.ScrolledText(
            self.facts_frame, bg=C["bg0"], fg=C["text2"],
            font=("Consolas",9), relief="flat", wrap="word",
            insertbackground=C["amber"], state="disabled")
        self.facts_text.pack(fill="both", expand=True)
        self.facts_text.tag_config("true",  foreground=C["green"])
        self.facts_text.tag_config("false", foreground=C["text3"])
        self.facts_text.tag_config("key",   foreground=C["amber"],
            font=("Consolas",9,"bold"))
        self.facts_text.tag_config("header", foreground=C["amber"],
            font=("Consolas",10,"bold"))

    def _build_fol_panel(self):
        self.fol_text = scrolledtext.ScrolledText(
            self.fol_frame, bg=C["bg0"], fg=C["text2"],
            font=("Consolas",9), relief="flat", wrap="word",
            insertbackground=C["amber"], state="disabled")
        self.fol_text.pack(fill="both", expand=True)
        self.fol_text.tag_config("comment",  foreground=C["text3"])
        self.fol_text.tag_config("keyword",  foreground=C["amber"])
        self.fol_text.tag_config("granted",  foreground=C["green"])
        self.fol_text.tag_config("denied",   foreground=C["red"])
        self.fol_text.tag_config("surety",   foreground=C["yellow"])
        self.fol_text.tag_config("pred",     foreground=C["amber2"])
        self.fol_text.tag_config("rule_fol", foreground=C["text"],
            font=("Consolas",9))

    # ── VERDICT STRIP ───────────────────────────────────────────
    def _show_placeholder_verdict(self):
        for w in self.verdict_frame.winfo_children():
            w.destroy()
        c = tk.Canvas(self.verdict_frame, bg=C["bg1"], height=100, highlightthickness=0)
        c.pack(fill="both", expand=True)
        c.create_text(300, 50, text="⚖  Run inference to see verdict",
            fill=C["text3"], font=("Segoe UI",11))
        c.create_line(100, 80, 500, 80, fill=C["border"], dash=(3,6))

    def _show_verdict(self, name, result):
        v = result["verdict"]
        # Extended verdict color map
        positive = v in ("granted", "minimal", "waivable", "clear")
        caution  = v in ("surety", "moderate", "recusal")
        negative = v in ("denied", "maximum", "severe", "disqualification")
        bg = C["green2"] if positive else C["amber3"] if caution else C["red2"]
        acc= C["green"]  if positive else C["amber"]  if caution else C["red"]
        ico= "✓" if positive else "⚖" if caution else "✗"

        verdict_labels = {
            "granted":"GRANTED", "denied":"DENIED", "surety":"GRANTED WITH CONDITIONS",
            "maximum":"MAXIMUM SENTENCE", "severe":"SEVERE SENTENCE",
            "moderate":"MODERATE SENTENCE", "minimal":"MINIMAL SENTENCE",
            "disqualification":"DISQUALIFIED", "recusal":"RECUSAL REQUIRED",
            "waivable":"CONFLICT WAIVABLE", "clear":"NO CONFLICT",
        }
        vtext = verdict_labels.get(v, v.upper())

        for w in self.verdict_frame.winfo_children():
            w.destroy()
        self.verdict_frame.config(bg=bg)

        left = tk.Frame(self.verdict_frame, bg=bg)
        left.pack(side="left", fill="both", padx=14, pady=8)

        tk.Label(left, text=ico, bg=bg, fg=acc,
                 font=("Segoe UI Emoji",28)).pack(side="left", padx=(0,12))

        info = tk.Frame(left, bg=bg)
        info.pack(side="left", fill="y")
        tk.Label(info, text="DECISION FOR", bg=bg, fg=acc,
                 font=("Consolas",7,"bold")).pack(anchor="w")
        tk.Label(info, text=name, bg=bg, fg=C["white"],
                 font=("Georgia",14,"bold")).pack(anchor="w")
        tk.Label(info, text=result["reason"], bg=bg, fg=C["text2"],
                 font=("Segoe UI",9), wraplength=380).pack(anchor="w")

        right = tk.Frame(self.verdict_frame, bg=bg)
        right.pack(side="right", padx=14, pady=8, anchor="n")
        tk.Label(right, text=f"Rule  {result['rule']}", bg=bg, fg=acc,
                 font=("Consolas",9,"bold")).pack(anchor="e")
        tk.Label(right, text=f"Case #{self.current_case_id or '—'}", bg=bg, fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="e")

        btn_f = tk.Frame(right, bg=bg)
        btn_f.pack(anchor="e", pady=4)
        tk.Button(btn_f, text="⬇ PDF", bg=C["bg4"], fg=C["text2"],
            relief="flat", font=("Segoe UI",8), padx=8, pady=3,
            command=self._export_current_pdf).pack(side="left", padx=2)
        tk.Button(btn_f, text="📋 Detail", bg=C["bg4"], fg=C["text2"],
            relief="flat", font=("Segoe UI",8), padx=8, pady=3,
            command=lambda: self._open_case_detail(self.current_case_id)).pack(side="left", padx=2)
        tk.Button(btn_f, text="💬 Explain", bg=C["bg4"], fg=C["text2"],
            relief="flat", font=("Segoe UI",8), padx=8, pady=3,
            command=self._show_explain).pack(side="left", padx=2)

    # ── HISTORY TAB ─────────────────────────────────────────────
    def _build_history_tab(self):
        frame = tk.Frame(self.nb, bg=C["bg0"])
        self.nb.add(frame, text="  📋  Case History  ")

        # Toolbar
        tb = tk.Frame(frame, bg=C["bg1"])
        tb.pack(fill="x", padx=0, pady=0)

        tk.Label(tb, text="Search:", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",8)).pack(side="left", padx=(10,4), pady=8)
        self.hist_search = tk.StringVar()
        self.hist_search.trace("w", lambda *a: self._load_history())
        self.hist_search_entry = tk.Entry(tb, textvariable=self.hist_search, bg=C["bg2"],
            fg=C["text"], insertbackground=C["amber"], relief="flat",
            font=("Consolas",9), bd=1, width=25)
        self.hist_search_entry.pack(side="left", pady=8, padx=(0,8))

        tk.Label(tb, text="Module:", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",8)).pack(side="left", padx=(0,4))
        self.hist_mod_var = tk.StringVar(value="All")
        mod_combo = ttk.Combobox(tb, textvariable=self.hist_mod_var,
            values=["All","bail","loan","sentencing","ethics"], width=10, state="readonly",
            font=("Consolas",8))
        mod_combo.pack(side="left", padx=(0,8))
        mod_combo.bind("<<ComboboxSelected>>", lambda e: self._load_history())

        tk.Label(tb, text="Verdict:", bg=C["bg1"], fg=C["text3"],
                 font=("Consolas",8)).pack(side="left", padx=(0,4))
        self.hist_verdict_var = tk.StringVar(value="All")
        v_combo = ttk.Combobox(tb, textvariable=self.hist_verdict_var,
            values=["All","granted","surety","denied"], width=8, state="readonly",
            font=("Consolas",8))
        v_combo.pack(side="left", padx=(0,12))
        v_combo.bind("<<ComboboxSelected>>", lambda e: self._load_history())

        tk.Button(tb, text="↻ Refresh", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",8), padx=8, pady=4,
            command=self._load_history).pack(side="left", padx=2)
        tk.Button(tb, text="⬇ Export JSON", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",8), padx=8, pady=4,
            command=self._export_json).pack(side="left", padx=2)
        tk.Button(tb, text="📂 Batch Import", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",8), padx=8, pady=4,
            command=self._batch_import).pack(side="left", padx=2)
        tk.Button(tb, text="⚖ Compare", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",8), padx=8, pady=4,
            command=self._compare_cases).pack(side="left", padx=2)

        # Treeview
        cols = ("case_id","subject","module","verdict","rule","reason","date")
        self.hist_tree = ttk.Treeview(frame, columns=cols, show="headings",
            selectmode="extended")
        headers = [("Case ID",90),("Subject",140),("Module",70),
                   ("Verdict",80),("Rule",60),("Reason",260),("Date",140)]
        for (col,w),(cid) in zip(headers,cols):
            self.hist_tree.heading(cid, text=col)
            self.hist_tree.column(cid, width=w, minwidth=40)

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=self.hist_tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.hist_tree.xview)
        self.hist_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.hist_tree.pack(fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        self.hist_tree.bind("<Double-1>", self._on_history_double_click)
        self.hist_tree.bind("<Button-3>", self._on_history_right_click)

        # Color tags
        self.hist_tree.tag_configure("granted", foreground=C["green"])
        self.hist_tree.tag_configure("surety",  foreground=C["yellow"])
        self.hist_tree.tag_configure("denied",  foreground=C["red"])

        self._load_history()

    def _load_history(self, *args):
        search  = self.hist_search.get().strip()
        mod     = self.hist_mod_var.get()
        verdict = self.hist_verdict_var.get()

        conn = db_conn()
        q = "SELECT case_id,subject,module,verdict,rule,reason,created_at FROM cases WHERE 1=1"
        params = []
        if search:
            q += " AND (subject LIKE ? OR case_id LIKE ? OR reason LIKE ?)"
            params += [f"%{search}%"]*3
        if mod != "All":
            q += " AND module=?"; params.append(mod)
        if verdict != "All":
            q += " AND verdict=?"; params.append(verdict)
        q += " ORDER BY created_at DESC LIMIT 200"
        rows = conn.execute(q, params).fetchall()
        conn.close()

        self.hist_tree.delete(*self.hist_tree.get_children())
        for r in rows:
            dt = (r["created_at"] or "")[:16].replace("T"," ")
            tag = r["verdict"] if r["verdict"] in ("granted","surety","denied") else ""
            self.hist_tree.insert("", "end",
                values=(r["case_id"],r["subject"],r["module"],
                        r["verdict"],r["rule"],r["reason"],dt),
                tags=(tag,))

    def _on_history_double_click(self, event):
        sel = self.hist_tree.selection()
        if not sel: return
        case_id = self.hist_tree.item(sel[0])["values"][0]
        self._open_case_detail(case_id)

    def _on_history_right_click(self, event):
        row = self.hist_tree.identify_row(event.y)
        if not row: return
        self.hist_tree.selection_set(row)
        case_id = self.hist_tree.item(row)["values"][0]
        menu = tk.Menu(self, tearoff=0, bg=C["bg2"], fg=C["text"],
                       activebackground=C["bg3"], activeforeground=C["amber"],
                       font=("Segoe UI",9))
        menu.add_command(label="📋  View Detail",
            command=lambda: self._open_case_detail(case_id))
        menu.add_command(label="⬇  Download PDF",
            command=lambda: self._export_pdf(case_id))
        menu.add_separator()
        menu.add_command(label="🗑  Delete Case",
            command=lambda: self._delete_case(case_id))
        menu.post(event.x_root, event.y_root)

    # ── ANALYTICS TAB ───────────────────────────────────────────
    def _build_analytics_tab(self):
        frame = tk.Frame(self.nb, bg=C["bg0"])
        self.nb.add(frame, text="  📊  Analytics  ")
        self.nb.bind("<<NotebookTabChanged>>",
            lambda e: self._refresh_analytics() if self.nb.index("current")==2 else None)

        # Stats row
        stats_row = tk.Frame(frame, bg=C["bg0"])
        stats_row.pack(fill="x", padx=16, pady=14)

        self.stat_labels = {}
        stat_defs = [
            ("total",   "Total Cases",   C["amber"]),
            ("granted", "Granted",        C["green"]),
            ("surety",  "With Conditions",C["yellow"]),
            ("denied",  "Denied",         C["red"]),
            ("rate",    "Grant Rate",     C["amber"]),
        ]
        for key, label, color in stat_defs:
            card = tk.Frame(stats_row, bg=C["bg1"], padx=16, pady=10)
            card.pack(side="left", expand=True, fill="both", padx=6)
            tk.Label(card, text=label, bg=C["bg1"], fg=C["text3"],
                     font=("Consolas",8)).pack()
            lbl = tk.Label(card, text="—", bg=C["bg1"], fg=color,
                           font=("Georgia",22,"bold"))
            lbl.pack()
            self.stat_labels[key] = lbl

        # Pie chart canvas
        self.pie_canvas = tk.Canvas(frame, bg=C["bg0"], height=180, highlightthickness=0)
        self.pie_canvas.pack(fill="x", padx=16, pady=(10,4))

        # Rule frequency
        tk.Label(frame, text="Rule Usage Frequency",
            bg=C["bg0"], fg=C["text3"],
            font=("Consolas",9,"bold")).pack(anchor="w", padx=20, pady=(8,4))

        self.rule_freq_frame = tk.Frame(frame, bg=C["bg1"])
        self.rule_freq_frame.pack(fill="x", padx=16)

        # Module split
        tk.Label(frame, text="Cases by Module",
            bg=C["bg0"], fg=C["text3"],
            font=("Consolas",9,"bold")).pack(anchor="w", padx=20, pady=(14,4))

        self.mod_split_frame = tk.Frame(frame, bg=C["bg1"])
        self.mod_split_frame.pack(fill="x", padx=16, pady=(0,10))

        self._refresh_analytics()

    def _refresh_analytics(self):
        conn = db_conn()
        total   = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        granted = conn.execute("SELECT COUNT(*) FROM cases WHERE verdict='granted'").fetchone()[0]
        surety  = conn.execute("SELECT COUNT(*) FROM cases WHERE verdict='surety'").fetchone()[0]
        denied  = conn.execute("SELECT COUNT(*) FROM cases WHERE verdict='denied'").fetchone()[0]
        rules   = conn.execute("SELECT rule, COUNT(*) cnt FROM cases GROUP BY rule ORDER BY cnt DESC LIMIT 10").fetchall()
        mods    = conn.execute("SELECT module, verdict, COUNT(*) cnt FROM cases GROUP BY module,verdict").fetchall()
        conn.close()

        rate = f"{(granted+surety)/max(total,1)*100:.1f}%"
        self.stat_labels["total"].config(text=str(total))
        self.stat_labels["granted"].config(text=str(granted))
        self.stat_labels["surety"].config(text=str(surety))
        self.stat_labels["denied"].config(text=str(denied))
        self.stat_labels["rate"].config(text=rate)

        # Pie chart
        self._draw_pie_chart(granted, surety, denied)

        # Rule bars
        for w in self.rule_freq_frame.winfo_children():
            w.destroy()
        max_cnt = max((r["cnt"] for r in rules), default=1)
        for r in rules:
            row = tk.Frame(self.rule_freq_frame, bg=C["bg1"])
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=r["rule"], bg=C["bg1"], fg=C["amber"],
                     font=("Consolas",9,"bold"), width=7, anchor="w").pack(side="left")
            bar_bg = tk.Frame(row, bg=C["bg3"], height=12)
            bar_bg.pack(side="left", fill="x", expand=True, padx=6)
            bar_bg.pack_propagate(False)
            pct = r["cnt"]/max_cnt
            bar = tk.Frame(bar_bg, bg=C["amber"], height=12)
            bar.place(relwidth=pct, relheight=1.0)
            tk.Label(row, text=str(r["cnt"]), bg=C["bg1"], fg=C["text3"],
                     font=("Consolas",8), width=4).pack(side="left")

        # Module split
        for w in self.mod_split_frame.winfo_children():
            w.destroy()
        for m in mods:
            col = C["green"] if m["verdict"]=="granted" else C["yellow"] if m["verdict"]=="surety" else C["red"]
            tk.Label(self.mod_split_frame,
                text=f"  {m['module'].title()}  {m['verdict'].upper()}  →  {m['cnt']} cases",
                bg=C["bg1"], fg=col, font=("Consolas",9)).pack(anchor="w", padx=10, pady=2)

    # ── RULES TAB ───────────────────────────────────────────────
    def _build_rules_tab(self):
        frame = tk.Frame(self.nb, bg=C["bg0"])
        self.nb.add(frame, text="  📜  Rule Base  ")

        txt = scrolledtext.ScrolledText(frame, bg=C["bg0"], fg=C["text2"],
            font=("Consolas",9), relief="flat", wrap="word",
            insertbackground=C["amber"], state="normal")
        txt.pack(fill="both", expand=True, padx=0)

        txt.tag_config("h1",    foreground=C["amber"],  font=("Consolas",11,"bold"))
        txt.tag_config("h2",    foreground=C["amber2"], font=("Consolas",10,"bold"))
        txt.tag_config("grant", foreground=C["green"])
        txt.tag_config("deny",  foreground=C["red"])
        txt.tag_config("warn",  foreground=C["yellow"])
        txt.tag_config("fol",   foreground=C["amber2"], font=("Consolas",9),
            background=C["bg2"])
        txt.tag_config("cmt",   foreground=C["text3"],  font=("Consolas",8))
        txt.tag_config("body",  foreground=C["text2"])
        txt.tag_config("cond",  foreground=C["text3"],  font=("Consolas",8))

        rules_data = [
            ("B1","GRANT","Bail — Standard Eligibility",
             "bail_verdict(X, granted, 'B1', _) :-\n    not_flight_risk(X),\n    not_dangerous(X),\n    community_ties(X).",
             "All three sub-goals must be proved via backward chaining. Represents the standard criteria for pretrial release.",
             ["local_address","employment OR family_ties","¬violent_offense","¬weapon_involved","community_years≥2 OR family_ties"]),

            ("B2","GRANT","Bail — Minor First Offense (Surety)",
             "bail_verdict(X, surety, 'B2', _) :-\n    minor_offense(X),\n    first_offense(X).",
             "Bail with surety bond for minor first-time offenders. Both conditions must be asserted in the KB.",
             ["minor_offense","first_offense"]),

            ("B3","DENY","Bail — Capital Offense (Hard Denial)",
             "bail_verdict(X, denied, 'B3', _) :-\n    capital_offense(X), !.",
             "Unconditional denial. The cut (!) prevents further backtracking. Fires before all other rules.",
             ["capital_offense"]),

            ("B4","DENY","Bail — Repeat Violent Offender",
             "bail_verdict(X, denied, 'B4', _) :-\n    violent_offense(X),\n    repeat_offender(X), !.",
             "Denied when subject has both violent offense and prior record. Both conditions required.",
             ["violent_offense","repeat_offender"]),

            ("L1","GRANT","Loan — Standard Approval",
             "loan_verdict(X, granted, 'L1', _) :-\n    good_credit_score(X),\n    stable_income(X),\n    low_debt_ratio(X).",
             "Standard approval path. Credit 700-799, income stable ≥24 months >$2000, DTI ≤43%.",
             ["credit_score 700–799","employment_months ≥24","monthly_income >$2,000","DTI ≤43%"]),

            ("L2","GRANT","Loan — Co-signer Path (Surety)",
             "loan_verdict(X, surety, 'L2', _) :-\n    moderate_credit_score(X),\n    stable_income(X),\n    has_cosigner(X).",
             "Approved with co-signer for moderate credit (600-699). Stable income still required.",
             ["credit_score 600–699","employment_months ≥24","monthly_income >$2,000","has_cosigner"]),

            ("L3","GRANT","Loan — Premium Approval",
             "loan_verdict(X, granted, 'L3', _) :-\n    excellent_credit_score(X),\n    high_income(X).",
             "Premium approval for excellent credit ≥800 with high income >$8000/mo. DTI check bypassed.",
             ["credit_score ≥800","monthly_income >$8,000"]),

            ("D1","DENY","Loan — Poor Credit Denial",
             "loan_verdict(X, denied, 'D1', _) :-\n    poor_credit_score(X),\n    \\+has_cosigner(X).",
             "Denied for poor credit (<600) without a co-signer. Uses negation-as-failure (\\+).",
             ["credit_score <600","¬has_cosigner"]),

            ("D2","DENY","Loan — Recent Bankruptcy",
             "loan_verdict(X, denied, 'D2', _) :-\n    has_bankruptcy(X),\n    bankruptcy_years_ago(X, Y), Y < 7.",
             "Hard denial if bankruptcy occurred within 7 years. Uses FOL comparison on temporal predicate.",
             ["has_bankruptcy","bankruptcy_years_ago < 7"]),

            ("S1","GRANT","Sentencing — Minimal Sentence",
             "sentencing_verdict(X, minimal, 'S1', _) :-\n    offense_severity(X,S), S =< 3,\n    has_mitigating(X),\n    first_offense(X).",
             "Minimal sentence for low severity (≤3) with mitigating circumstances and first offense.",
             ["offense_severity ≤3","mitigating factors","first_offense"]),

            ("S2","WARN","Sentencing — Moderate Sentence (Default)",
             "sentencing_verdict(X, moderate, 'S2', _) :-\n    offense_severity(X,_).",
             "Default moderate sentence when no special aggravating or mitigating rules apply.",
             ["offense_severity present"]),

            ("S3","DENY","Sentencing — Severe Sentence",
             "sentencing_verdict(X, severe, 'S3', _) :-\n    offense_severity(X,S), S >= 6,\n    has_aggravating(X).",
             "Severe sentence for high severity (≥6) with aggravating factors.",
             ["offense_severity ≥6","premeditation OR weapon OR victim_vuln OR priors≥2"]),

            ("S4","DENY","Sentencing — Maximum Sentence",
             "sentencing_verdict(X, maximum, 'S4', _) :-\n    offense_severity(X,S), S >= 8,\n    premeditation(X),\n    weapon_involved(X).",
             "Maximum sentence for severity ≥8 with premeditation and weapon. Unconditional.",
             ["offense_severity ≥8","premeditation","weapon_involved"]),

            ("E1","GRANT","Ethics — Waivable Conflict",
             "ethics_verdict(X, waivable, 'E1', _) :-\n    relationship_type(X,T), T \\= none,\n    disclosure_made(X),\n    conflict_severity(X,S), S =< 2.",
             "Minor conflict that is waivable when properly disclosed with low severity (≤2).",
             ["relationship ≠ none","disclosure_made","conflict_severity ≤2"]),

            ("E2","WARN","Ethics — Recusal Required",
             "ethics_verdict(X, recusal, 'E2', _) :-\n    relationship_type(X,T), T \\= none,\n    prior_conflict(X).",
             "Recusal required when there is a non-none relationship and prior conflict exists.",
             ["relationship ≠ none","prior_conflict"]),

            ("E3","DENY","Ethics — Disqualification",
             "ethics_verdict(X, disqualification, 'E3', _) :-\n    relationship_type(X,T), member(T,[family,financial]),\n    conflict_severity(X,S), S >= 4,\n    \\+ disclosure_made(X).",
             "Disqualification for undisclosed serious conflict (severity ≥4) with family/financial relationship.",
             ["relationship = family/financial","conflict_severity ≥4","¬disclosure_made"]),
        ]

        txt.insert("end", "  LEXLOGIC KNOWLEDGE BASE — RULE REFERENCE\n", "h1")
        txt.insert("end", "  Propositional + First-Order Logic  |  SLD Backward Chaining\n\n", "cmt")

        for rule_id, rtype, name, fol, desc, conds in rules_data:
            tag = "grant" if rtype=="GRANT" else "warn" if rtype=="WARN" else "deny"
            txt.insert("end", f"  [{rtype}]  ", tag)
            txt.insert("end", f"Rule {rule_id}  —  {name}\n", "h2")
            txt.insert("end", "\n")
            txt.insert("end", f"  {fol}\n", "fol")
            txt.insert("end", "\n")
            txt.insert("end", f"  {desc}\n", "body")
            txt.insert("end", "  Conditions: " + "  |  ".join(conds) + "\n", "cond")
            txt.insert("end", "\n" + "─"*90 + "\n\n", "cmt")

        # Prolog KB dump
        txt.insert("end", "  FULL SWI-PROLOG KNOWLEDGE BASE (legal_kb.pl)\n", "h1")
        txt.insert("end", "\n")
        try:
            with open(KB_PATH, "r") as f:
                txt.insert("end", f.read(), "fol")
        except Exception:
            txt.insert("end", "  [legal_kb.pl not found — place it in the same folder as this app]\n", "deny")

        txt.config(state="disabled")

    # ── SETTINGS TAB ────────────────────────────────────────────
    def _build_settings_tab(self):
        frame = tk.Frame(self.nb, bg=C["bg0"])
        self.nb.add(frame, text="  ⚙  Settings  ")

        inner = tk.Frame(frame, bg=C["bg0"])
        inner.pack(padx=40, pady=30, anchor="nw")

        def section(title):
            tk.Label(inner, text=title, bg=C["bg0"], fg=C["amber"],
                     font=("Consolas",9,"bold")).pack(anchor="w", pady=(16,4))
            tk.Frame(inner, bg=C["border"], height=1).pack(fill="x", pady=(0,8))

        def row(label, sub, widget_factory):
            r = tk.Frame(inner, bg=C["bg1"], padx=14, pady=10)
            r.pack(fill="x", pady=1)
            tk.Label(r, text=label, bg=C["bg1"], fg=C["text"],
                     font=("Segoe UI",10)).pack(side="left")
            tk.Label(r, text=sub, bg=C["bg1"], fg=C["text3"],
                     font=("Consolas",7)).pack(side="left", padx=(6,0))
            w = widget_factory(r)
            w.pack(side="right")
            return w

        section("REPORT CONFIGURATION")
        self.sett_judge = tk.Entry(inner, bg=C["bg2"], fg=C["text"],
            insertbackground=C["amber"], relief="flat", font=("Segoe UI",10), width=35, bd=1)
        self.sett_judge.insert(0, get_setting("judge_name") or "Hon. AI Reasoning System")
        tk.Label(inner, text="Issuing Authority / Judge Name", bg=C["bg0"], fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="w")
        self.sett_judge.pack(anchor="w", pady=(0,6))

        self.sett_court = tk.Entry(inner, bg=C["bg2"], fg=C["text"],
            insertbackground=C["amber"], relief="flat", font=("Segoe UI",10), width=35, bd=1)
        self.sett_court.insert(0, get_setting("court_name") or "LexLogic Legal Reasoning Court")
        tk.Label(inner, text="Court / Institution Name", bg=C["bg0"], fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="w")
        self.sett_court.pack(anchor="w", pady=(0,6))

        section("ENGINE")
        eng_lbl = "SWI-Prolog + Python (native inference)" if PROLOG_OK else \
                  "Python FOL Engine (Prolog not found)"
        tk.Label(inner, text=f"Active Engine:  {eng_lbl}",
            bg=C["bg0"], fg=C["green"] if PROLOG_OK else C["yellow"],
            font=("Consolas",9)).pack(anchor="w")
        tk.Label(inner, text=f"KB Path:  {KB_PATH}",
            bg=C["bg0"], fg=C["text3"], font=("Consolas",8)).pack(anchor="w", pady=4)

        section("ACTIONS")
        btn_f = tk.Frame(inner, bg=C["bg0"])
        btn_f.pack(anchor="w")
        tk.Button(btn_f, text="💾  Save Settings", bg=C["amber"], fg=C["bg0"],
            relief="flat", font=("Segoe UI",9,"bold"), padx=16, pady=6,
            command=self._save_settings).pack(side="left", padx=(0,8))
        tk.Button(btn_f, text="⬇  Export All Cases (JSON)", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",9), padx=12, pady=6,
            command=self._export_json).pack(side="left")

    def _save_settings(self):
        save_setting("judge_name", self.sett_judge.get())
        save_setting("court_name", self.sett_court.get())
        messagebox.showinfo("LexLogic", "Settings saved successfully.")

    # ── STATUS BAR ──────────────────────────────────────────────
    def _build_statusbar(self):
        sb = tk.Frame(self, bg=C["bg1"], height=22)
        sb.pack(fill="x")
        sb.pack_propagate(False)

        self.sb_engine = tk.Label(sb, text="Engine: —", bg=C["bg1"], fg=C["text3"],
                                  font=("Consolas",7))
        self.sb_engine.pack(side="left", padx=10)
        tk.Frame(sb, bg=C["border"], width=1).pack(side="left", fill="y", pady=3)

        self.sb_cases = tk.Label(sb, text="Cases: 0", bg=C["bg1"], fg=C["text3"],
                                 font=("Consolas",7))
        self.sb_cases.pack(side="left", padx=10)
        tk.Frame(sb, bg=C["border"], width=1).pack(side="left", fill="y", pady=3)

        self.sb_module = tk.Label(sb, text="Module: Bail", bg=C["bg1"], fg=C["text3"],
                                  font=("Consolas",7))
        self.sb_module.pack(side="left", padx=10)
        tk.Frame(sb, bg=C["border"], width=1).pack(side="left", fill="y", pady=3)

        self.sb_last = tk.Label(sb, text="Last: —", bg=C["bg1"], fg=C["text3"],
                                font=("Consolas",7))
        self.sb_last.pack(side="left", padx=10)

        self.sb_kb = tk.Label(sb, text=f"KB: legal_kb.pl", bg=C["bg1"], fg=C["text3"],
                              font=("Consolas",7))
        self.sb_kb.pack(side="right", padx=10)

    # ── ENGINE STATUS ────────────────────────────────────────────
    def _check_engine_status(self):
        eng = "SWI-Prolog + Python" if PROLOG_OK else "Python FOL Engine"
        self.eng_lbl.config(text=eng)
        self.sb_engine.config(text=f"Engine: {eng}")
        self._update_case_count()

    def _update_case_count(self):
        conn = db_conn()
        total = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        conn.close()
        self.sb_cases.config(text=f"Cases: {total}")

    def _update_clock(self):
        now = datetime.datetime.now()
        self.clock_lbl.config(text=now.strftime("%d %b %Y  %H:%M:%S"))
        self.after(1000, self._update_clock)

    # ── RUN INFERENCE ────────────────────────────────────────────
    def _run_inference(self):
        name = self.subject_var.get().strip()
        if not name or name.startswith("e.g."):
            name = "Unknown Subject"
        notes = self.notes_var.get("1.0","end").strip()
        mod = self.current_module.get()

        if mod == "bail":
            facts = {k: v.get() for k,v in self.bail_vars.items()}
        elif mod == "loan":
            facts = {}
            for k,v in self.loan_vars.items():
                try:
                    facts[k] = float(v.get())
                except Exception:
                    facts[k] = 0
            facts["has_cosigner"]  = self.loan_bool_vars.get("has_cosigner", tk.BooleanVar()).get()
            facts["has_bankruptcy"]= self.loan_bool_vars.get("has_bankruptcy",tk.BooleanVar()).get()
            try:
                facts["bankruptcy_years"] = float(self.bk_years_var.get())
            except Exception:
                facts["bankruptcy_years"] = 0
        elif mod == "sentencing":
            facts = {k: v.get() for k,v in self.sent_vars.items()}
            for k, v in self.sent_scale_vars.items():
                facts[k] = v.get()
        elif mod == "ethics":
            facts = {k: v.get() for k, v in self.ethics_vars.items()}
            for k, v in self.ethics_bool_vars.items():
                facts[k] = v.get()
        else:
            facts = {}

        # Run inference directly (engine is instant, no need for threading)
        try:
            if mod == "bail":
                result = engine.bail(facts)
            elif mod == "loan":
                result = engine.loan(facts)
            elif mod == "sentencing":
                result = engine.sentencing(facts)
            elif mod == "ethics":
                result = engine.ethics(facts)
            else:
                result = engine.bail(facts)
            result["engine"] = "Python FOL Engine" + (" + SWI-Prolog" if PROLOG_OK else "")
            self._show_result(name, facts, result, notes)
        except Exception as ex:
            messagebox.showerror("LexLogic", f"Inference error:\n{ex}")
            # Always restore button
            self.run_btn._bg0 = C["amber"]
            self.run_btn._bg1 = C["amber2"]
            self.run_btn._fg = C["bg0"]
            self.run_btn._text = "RUN LEGAL INFERENCE"
            self.run_btn._icon = "▶"
            self.run_btn._draw(C["amber"])

    def _show_result(self, name, facts, result, notes):
        # Save to DB
        case_id = hashlib.md5(
            f"{name}{datetime.datetime.now().isoformat()}".encode()
        ).hexdigest()[:10].upper()
        self.current_case_id = case_id
        self.last_result = result

        conn = db_conn()
        conn.execute("""INSERT INTO cases
            (case_id,subject,module,verdict,rule,reason,facts,trace,engine,notes,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (case_id, name, self.current_module.get(),
             result["verdict"], result["rule"], result["reason"],
             json.dumps(facts), json.dumps(result["trace"]),
             result["engine"], notes,
             datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()

        self._show_verdict(name, result)
        self._render_trace(result, name)
        self._render_facts(facts)
        self._render_fol(name, result, facts)
        self._update_case_count()

        v = result["verdict"]
        self.sb_last.config(text=f"Last: {v.upper()}")
        self.sb_module.config(text=f"Module: {self.current_module.get().title()}")

        # Restore run button
        self.run_btn._bg0 = C["amber"]
        self.run_btn._bg1 = C["amber2"]
        self.run_btn._fg = C["bg0"]
        self.run_btn._text = "RUN LEGAL INFERENCE"
        self.run_btn._icon = "▶"
        self.run_btn._draw(C["amber"])

    def _render_trace(self, result, name):
        t = self.trace_text
        t.config(state="normal")
        t.delete("1.0","end")

        t.insert("end", f"\n  INFERENCE TRACE — {name}\n", "header")
        t.insert("end",
            f"  Module: {self.current_module.get().upper()}  |  "
            f"Engine: {result['engine']}  |  "
            f"Steps: {len(result['trace'])}\n", "logic")
        t.insert("end", "  " + "─"*70 + "\n\n", "logic")

        sym_map = {
            "pass":"  ✓ ","fail":"  ✗ ","rule":"  ▶ ",
            "warn":"  ⚠ ","info":"  ℹ ","skip":"  · "
        }

        for i, step in enumerate(result["trace"]):
            st  = step.get("status","info")
            sym = sym_map.get(st, "  · ")
            t.insert("end", f"  {i+1:02d}", "num")
            t.insert("end", sym, st)
            t.insert("end", step.get("pred","") + "\n", st)
            t.insert("end",
                "       " + step.get("logic","") + "\n\n", "logic")

        t.insert("end", "  " + "─"*70 + "\n", "logic")
        t.insert("end",
            f"  VERDICT: {result['verdict'].upper()}  |  Rule: {result['rule']}\n", "header")
        t.config(state="disabled")

    def _render_facts(self, facts):
        t = self.facts_text
        t.config(state="normal")
        t.delete("1.0","end")
        t.insert("end", "\n  KNOWLEDGE BASE — ASSERTED FACTS\n", "header")
        t.insert("end", "  " + "─"*50 + "\n\n", "key")
        for k,v in facts.items():
            isBool = isinstance(v, bool)
            isTrue = v if isBool else bool(v)
            tag = "true" if isTrue else "false"
            disp = "TRUE" if isBool and isTrue else "FALSE" if isBool else str(v)
            t.insert("end", f"  {k.replace('_',' '):<28}", "key")
            t.insert("end", f"{disp}\n", tag)
        t.config(state="disabled")

    def _render_fol(self, name, result, facts):
        t = self.fol_text
        t.config(state="normal")
        t.delete("1.0","end")

        subj = name.replace(" ","_").lower()
        mod  = self.current_module.get()
        v    = result["verdict"]

        t.insert("end", "\n  /* FOL REPRESENTATION — CURRENT CASE */\n\n", "comment")
        t.insert("end", "  /* Knowledge Base Assertions */\n", "comment")
        for k,val in facts.items():
            if isinstance(val,bool) and val:
                t.insert("end", f"  {k}({subj}).\n", "pred")
            elif not isinstance(val,bool) and val:
                t.insert("end", f"  {k}({subj},{val}).\n", "pred")

        t.insert("end", "\n  /* Applied Rule */\n", "comment")

        rules_fol = {
            "B1": f"bail_verdict({subj}, granted, 'B1', _) :-\n    not_flight_risk({subj}),\n    not_dangerous({subj}),\n    community_ties({subj}).",
            "B2": f"bail_verdict({subj}, surety, 'B2', _) :-\n    minor_offense({subj}),\n    first_offense({subj}).",
            "B3": f"bail_verdict({subj}, denied, 'B3', _) :-\n    capital_offense({subj}), !.",
            "B4": f"bail_verdict({subj}, denied, 'B4', _) :-\n    violent_offense({subj}),\n    repeat_offender({subj}), !.",
            "L1": f"loan_verdict({subj}, granted, 'L1', _) :-\n    good_credit_score({subj}),\n    stable_income({subj}),\n    low_debt_ratio({subj}).",
            "L2": f"loan_verdict({subj}, surety, 'L2', _) :-\n    moderate_credit_score({subj}),\n    stable_income({subj}),\n    has_cosigner({subj}).",
            "L3": f"loan_verdict({subj}, granted, 'L3', _) :-\n    excellent_credit_score({subj}),\n    high_income({subj}).",
            "D1": f"loan_verdict({subj}, denied, 'D1', _) :-\n    poor_credit_score({subj}),\n    \\+has_cosigner({subj}).",
            "D2": f"loan_verdict({subj}, denied, 'D2', _) :-\n    has_bankruptcy({subj}),\n    bankruptcy_years_ago({subj},Y), Y<7.",
            "S1": f"sentencing_verdict({subj}, minimal, 'S1', _) :-\n    offense_severity({subj},S), S =< 3,\n    has_mitigating({subj}),\n    first_offense({subj}).",
            "S2": f"sentencing_verdict({subj}, moderate, 'S2', _) :-\n    offense_severity({subj},_).",
            "S3": f"sentencing_verdict({subj}, severe, 'S3', _) :-\n    offense_severity({subj},S), S >= 6,\n    has_aggravating({subj}).",
            "S4": f"sentencing_verdict({subj}, maximum, 'S4', _) :-\n    offense_severity({subj},S), S >= 8,\n    premeditation({subj}),\n    weapon_involved({subj}).",
            "E1": f"ethics_verdict({subj}, waivable, 'E1', _) :-\n    relationship_type({subj},T), T \\\\= none,\n    disclosure_made({subj}),\n    conflict_severity({subj},S), S =< 2.",
            "E2": f"ethics_verdict({subj}, recusal, 'E2', _) :-\n    relationship_type({subj},T), T \\\\= none,\n    prior_conflict({subj}).",
            "E3": f"ethics_verdict({subj}, disqualification, 'E3', _) :-\n    relationship_type({subj},T), member(T,[family,financial]),\n    conflict_severity({subj},S), S >= 4,\n    \\\\+ disclosure_made({subj}).",
            "NONE":"/* No matching rule — all Horn clause heads failed */",
        }
        fol_str = rules_fol.get(result["rule"], f"/* Rule {result['rule']} */")
        t.insert("end", "\n  " + fol_str.replace("\n","\n  ") + "\n", "rule_fol")

        t.insert("end", "\n  /* Verdict */\n", "comment")
        vtag = v if v in ("granted","surety","denied") else "pred"
        pred_map = {"bail":"bail_verdict", "loan":"loan_verdict",
                    "sentencing":"sentencing_verdict", "ethics":"ethics_verdict"}
        pred_name = pred_map.get(mod, f"{mod}_verdict")
        t.insert("end",
            f"  {pred_name}({subj}, ", "pred")
        t.insert("end", v, vtag)
        t.insert("end", f", '{result['rule']}', '{result['reason']}').\n", "pred")

        t.config(state="disabled")

    # ── CASE DETAIL WINDOW ───────────────────────────────────────
    def _open_case_detail(self, case_id):
        if not case_id:
            messagebox.showwarning("LexLogic","No case selected.")
            return
        conn = db_conn()
        row = conn.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
        conn.close()
        if not row:
            messagebox.showerror("LexLogic","Case not found.")
            return

        win = tk.Toplevel(self)
        win.title(f"Case Detail — {row['case_id']} — {row['subject']}")
        win.geometry("780x600")
        win.configure(bg=C["bg0"])
        win.grab_set()

        # Header
        v  = row["verdict"]
        bg = C["green2"] if v=="granted" else C["amber3"] if v=="surety" else C["red2"]
        acc= C["green"]  if v=="granted" else C["amber"]  if v=="surety" else C["red"]
        ico= "✓" if v=="granted" else "⚖" if v=="surety" else "✗"

        hdr = tk.Frame(win, bg=bg, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"{ico}  {row['subject']}  —  {v.upper()}  (Rule {row['rule']})",
            bg=bg, fg=C["white"], font=("Georgia",13,"bold")).pack(side="left", padx=16, pady=12)
        tk.Label(hdr, text=f"Case #{row['case_id']}", bg=bg, fg=acc,
            font=("Consolas",9)).pack(side="right", padx=16)

        # Detail notebook
        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=6, pady=6)

        # Info tab
        info_f = tk.Frame(nb, bg=C["bg0"])
        nb.add(info_f, text="  Info  ")
        fields = [
            ("Subject",   row["subject"]),
            ("Module",    row["module"].title()),
            ("Verdict",   row["verdict"].upper()),
            ("Rule",      row["rule"]),
            ("Reason",    row["reason"]),
            ("Engine",    row["engine"] or "—"),
            ("Date",      (row["created_at"] or "")[:19]),
        ]
        for label, val in fields:
            r = tk.Frame(info_f, bg=C["bg1"])
            r.pack(fill="x", padx=10, pady=1)
            tk.Label(r, text=f"  {label}", bg=C["bg1"], fg=C["text3"],
                     font=("Consolas",9,"bold"), width=14, anchor="w").pack(side="left")
            tk.Label(r, text=val, bg=C["bg1"], fg=C["text"],
                     font=("Segoe UI",9), anchor="w").pack(side="left", padx=4)

        # Facts tab
        facts_f = tk.Frame(nb, bg=C["bg0"])
        nb.add(facts_f, text="  Facts  ")
        ft = scrolledtext.ScrolledText(facts_f, bg=C["bg0"], fg=C["text2"],
            font=("Consolas",9), relief="flat", state="normal")
        ft.pack(fill="both", expand=True)
        ft.tag_config("t", foreground=C["green"])
        ft.tag_config("f", foreground=C["text3"])
        ft.tag_config("k", foreground=C["amber"], font=("Consolas",9,"bold"))
        facts = json.loads(row["facts"] or "{}")
        for k,v2 in facts.items():
            isT = v2 if isinstance(v2,bool) else bool(v2)
            ft.insert("end", f"  {k.replace('_',' '):<28}","k")
            ft.insert("end", f"{'TRUE' if isinstance(v2,bool) and isT else 'FALSE' if isinstance(v2,bool) else str(v2)}\n",
                "t" if isT else "f")
        ft.config(state="disabled")

        # Trace tab
        trace_f = tk.Frame(nb, bg=C["bg0"])
        nb.add(trace_f, text="  Trace  ")
        tt = scrolledtext.ScrolledText(trace_f, bg=C["bg0"], fg=C["text2"],
            font=("Consolas",9), relief="flat", state="normal")
        tt.pack(fill="both", expand=True)
        tt.tag_config("pass", foreground=C["green"])
        tt.tag_config("fail", foreground=C["red"])
        tt.tag_config("rule", foreground=C["amber"])
        tt.tag_config("info", foreground=C["text3"])
        tt.tag_config("skip", foreground=C["text3"])
        tt.tag_config("logic",foreground=C["text3"], font=("Consolas",8))
        trace = json.loads(row["trace"] or "[]")
        for i,step in enumerate(trace):
            st = step.get("status","info")
            tt.insert("end", f"  {i+1:02d}  [{st.upper():<4}]  {step.get('pred','')}\n", st)
            tt.insert("end", f"         {step.get('logic','')}\n\n", "logic")
        tt.config(state="disabled")

        # Notes tab
        notes_f = tk.Frame(nb, bg=C["bg0"])
        nb.add(notes_f, text="  Notes  ")
        tk.Label(notes_f, text="Case Notes:", bg=C["bg0"], fg=C["text3"],
                 font=("Consolas",8)).pack(anchor="w", padx=10, pady=6)
        notes_text = tk.Text(notes_f, bg=C["bg2"], fg=C["text"],
            insertbackground=C["amber"], relief="flat", font=("Segoe UI",9),
            wrap="word", padx=8, pady=6)
        notes_text.insert("end", row["notes"] or "")
        notes_text.pack(fill="both", expand=True, padx=10, pady=(0,6))

        # Buttons
        btn_f = tk.Frame(win, bg=C["bg1"])
        btn_f.pack(fill="x", padx=6, pady=6)

        def save_notes():
            new_notes = notes_text.get("1.0","end").strip()
            c2 = db_conn()
            c2.execute("UPDATE cases SET notes=? WHERE case_id=?",(new_notes, row["case_id"]))
            c2.commit(); c2.close()
            messagebox.showinfo("LexLogic","Notes saved.", parent=win)

        tk.Button(btn_f, text="💾  Save Notes", bg=C["amber"], fg=C["bg0"],
            relief="flat", font=("Segoe UI",9,"bold"), padx=12, pady=5,
            command=save_notes).pack(side="left", padx=6)
        tk.Button(btn_f, text="⬇  Download PDF", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",9), padx=12, pady=5,
            command=lambda: self._export_pdf(row["case_id"])).pack(side="left", padx=2)
        tk.Button(btn_f, text="🗑  Delete", bg=C["red2"], fg=C["white"],
            relief="flat", font=("Segoe UI",9), padx=12, pady=5,
            command=lambda: self._delete_case(row["case_id"], win)).pack(side="left", padx=2)
        tk.Button(btn_f, text="✕  Close", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",9), padx=12, pady=5,
            command=win.destroy).pack(side="right", padx=6)

    # ── EXPORT / DELETE ──────────────────────────────────────────
    def _export_current_pdf(self):
        if not self.current_case_id:
            messagebox.showwarning("LexLogic","No current case. Run inference first.")
            return
        self._export_pdf(self.current_case_id)

    def _export_pdf(self, case_id):
        conn = db_conn()
        row  = conn.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
        conn.close()
        if not row:
            messagebox.showerror("LexLogic","Case not found.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files","*.pdf"),("All Files","*.*")],
            initialfile=f"LexLogic_{case_id}.pdf",
            title="Save PDF Report")
        if not path: return

        result = generate_pdf(dict(row), path)
        if result is True:
            messagebox.showinfo("LexLogic",f"PDF saved:\n{path}")
            try:
                os.startfile(path)  # Windows auto-open
            except Exception:
                pass
        elif result is False:
            messagebox.showerror("LexLogic",
                "ReportLab not installed.\nRun:  pip install reportlab")
        else:
            messagebox.showerror("LexLogic",f"PDF error:\n{result}")

    def _export_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files","*.json"),("All Files","*.*")],
            initialfile="lexlogic_export.json",
            title="Export All Cases")
        if not path: return
        conn = db_conn()
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM cases ORDER BY created_at DESC").fetchall()]
        conn.close()
        with open(path,"w") as f:
            json.dump(rows, f, indent=2)
        messagebox.showinfo("LexLogic",f"Exported {len(rows)} cases to:\n{path}")

    def _delete_case(self, case_id, parent_win=None):
        if not messagebox.askyesno("LexLogic",
                f"Delete case {case_id}? This cannot be undone.",
                parent=parent_win or self):
            return
        conn = db_conn()
        conn.execute("DELETE FROM cases WHERE case_id=?", (case_id,))
        conn.commit(); conn.close()
        if parent_win:
            parent_win.destroy()
        self._load_history()
        self._update_case_count()
        messagebox.showinfo("LexLogic","Case deleted.")

    # ── KEYBOARD ─────────────────────────────────────────────────
    def _bind_keys(self):
        self.bind("<Control-Return>", lambda e: self._run_inference())
        self.bind("<Control-e>",      lambda e: self._export_current_pdf())
        self.bind("<Control-f>",      lambda e: self._focus_search())
        self.bind("<Control-b>",      lambda e: self._switch_module("bail"))
        self.bind("<Control-l>",      lambda e: self._switch_module("loan"))
        self.bind("<Control-s>",      lambda e: self._switch_module("sentencing"))
        self.bind("<Control-slash>",  lambda e: self._show_shortcuts())

    def _focus_search(self):
        self.nb.select(1)  # History tab
        self.hist_search_entry.focus_set()

    # ── EXPLAIN PANEL ────────────────────────────────────────────
    def _show_explain(self):
        if not self.last_result:
            messagebox.showwarning("LexLogic", "Run inference first.")
            return
        result = self.last_result
        win = tk.Toplevel(self)
        win.title("LexLogic — Plain-English Reasoning")
        win.geometry("640x500")
        win.configure(bg=C["bg0"])
        win.grab_set()

        tk.Label(win, text="💬  Plain-English Explanation",
            bg=C["bg1"], fg=C["amber"], font=("Georgia",12,"bold"),
            pady=10).pack(fill="x")

        txt = scrolledtext.ScrolledText(win, bg=C["bg0"], fg=C["text"],
            font=("Segoe UI",10), relief="flat", wrap="word",
            padx=14, pady=10)
        txt.pack(fill="both", expand=True, padx=6, pady=6)

        # Generate explanation
        lines = []
        lines.append(f"📋 Analysis Summary\n")
        lines.append(f"The system evaluated the case using {len(result['trace'])} inference steps.\n")

        for step in result["trace"]:
            st = step.get("status", "info")
            pred = step.get("pred", "")
            if st == "pass":
                lines.append(f"  ✅ {self._humanize(pred)}")
            elif st == "fail":
                lines.append(f"  ❌ {self._humanize(pred)}")
            elif st == "rule":
                lines.append(f"\n  ▶ {self._humanize(pred)}")
            elif st == "skip":
                lines.append(f"  ⏭ {self._humanize(pred)}")

        lines.append(f"\n{'─'*50}")
        lines.append(f"\n📌 Final Decision: {result['verdict'].upper()}")
        lines.append(f"   Rule Applied: {result['rule']}")
        lines.append(f"   Reason: {result['reason']}")

        txt.insert("end", "\n".join(lines))
        txt.config(state="disabled")

        tk.Button(win, text="✕  Close", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",9), padx=12, pady=5,
            command=win.destroy).pack(pady=6)

    def _humanize(self, pred):
        """Convert technical predicate text to more readable form."""
        text = pred.replace("(X)", "").replace("(X,", " = ").replace(")", "")
        text = text.replace("←", "is").replace("TRUE", "confirmed").replace("FALSE", "not met")
        text = text.replace("_", " ")
        return text

    # ── BATCH IMPORT ─────────────────────────────────────────────
    def _batch_import(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV Files","*.csv"),("All","*.*")],
            title="Select CSV for Batch Import")
        if not path:
            return
        try:
            import csv
            with open(path, "r", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            messagebox.showerror("LexLogic", f"CSV read error:\n{e}")
            return

        if not rows:
            messagebox.showwarning("LexLogic", "CSV is empty.")
            return

        # Progress window
        prog = tk.Toplevel(self)
        prog.title("Batch Processing")
        prog.geometry("600x400")
        prog.configure(bg=C["bg0"])

        tk.Label(prog, text=f"Processing {len(rows)} cases...",
            bg=C["bg1"], fg=C["amber"], font=("Georgia",11,"bold"),
            pady=8).pack(fill="x")

        cols = ("subject","module","verdict","rule")
        tree = ttk.Treeview(prog, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c.title())
            tree.column(c, width=140)
        tree.pack(fill="both", expand=True, padx=6, pady=6)

        tree.tag_configure("granted", foreground=C["green"])
        tree.tag_configure("denied", foreground=C["red"])
        tree.tag_configure("surety", foreground=C["yellow"])

        def process():
            for row in rows:
                subject = row.get("subject", "Unknown")
                mod = row.get("module", "bail").lower().strip()

                # Build facts from CSV columns
                facts = {}
                for k, v in row.items():
                    if k in ("subject","module"):
                        continue
                    lv = v.strip().lower() if isinstance(v, str) else str(v)
                    if lv in ("true","yes","1"):
                        facts[k] = True
                    elif lv in ("false","no","0",""):
                        facts[k] = False
                    else:
                        try:
                            facts[k] = float(v)
                        except Exception:
                            facts[k] = v

                if mod == "loan":
                    result = engine.loan(facts)
                elif mod == "sentencing":
                    result = engine.sentencing(facts)
                elif mod == "ethics":
                    result = engine.ethics(facts)
                else:
                    result = engine.bail(facts)

                result["engine"] = "Python FOL Engine (Batch)"

                # Save to DB
                case_id = hashlib.md5(
                    f"{subject}{datetime.datetime.now().isoformat()}{id(row)}".encode()
                ).hexdigest()[:10].upper()
                conn = db_conn()
                conn.execute("""INSERT INTO cases
                    (case_id,subject,module,verdict,rule,reason,facts,trace,engine,notes,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (case_id, subject, mod, result["verdict"], result["rule"],
                     result["reason"], json.dumps(facts), json.dumps(result["trace"]),
                     result["engine"], "", datetime.datetime.now().isoformat()))
                conn.commit(); conn.close()

                v = result["verdict"]
                tag = v if v in ("granted","surety","denied") else ""
                self.after(0, lambda s=subject,m=mod,r=result,t=tag: tree.insert("","end",
                    values=(s, m, r["verdict"], r["rule"]), tags=(t,)))

            self.after(0, lambda: [
                self._load_history(),
                self._update_case_count(),
                messagebox.showinfo("LexLogic", f"Batch complete: {len(rows)} cases processed.", parent=prog)
            ])

        threading.Thread(target=process, daemon=True).start()

    # ── CASE COMPARISON ──────────────────────────────────────────
    def _compare_cases(self):
        sel = self.hist_tree.selection()
        if len(sel) < 2:
            messagebox.showwarning("LexLogic",
                "Select exactly 2 cases (Ctrl+Click) to compare.")
            return

        ids = [self.hist_tree.item(s)["values"][0] for s in sel[:2]]
        conn = db_conn()
        cases = []
        for cid in ids:
            row = conn.execute("SELECT * FROM cases WHERE case_id=?", (cid,)).fetchone()
            if row:
                cases.append(dict(row))
        conn.close()

        if len(cases) < 2:
            messagebox.showerror("LexLogic", "Could not load both cases.")
            return

        win = tk.Toplevel(self)
        win.title(f"Case Comparison — {ids[0]} vs {ids[1]}")
        win.geometry("900x550")
        win.configure(bg=C["bg0"])
        win.grab_set()

        tk.Label(win, text="⚖  Side-by-Side Case Comparison",
            bg=C["bg1"], fg=C["amber"], font=("Georgia",12,"bold"),
            pady=10).pack(fill="x")

        cols_f = tk.Frame(win, bg=C["bg0"])
        cols_f.pack(fill="both", expand=True, padx=6, pady=6)

        for idx, case in enumerate(cases):
            col = tk.Frame(cols_f, bg=C["bg1"], padx=10, pady=8)
            col.pack(side="left", fill="both", expand=True, padx=4)

            v = case.get("verdict", "")
            positive = v in ("granted", "minimal", "waivable", "clear")
            caution = v in ("surety", "moderate", "recusal")
            vc = C["green"] if positive else C["amber"] if caution else C["red"]

            tk.Label(col, text=f"Case #{case['case_id']}", bg=C["bg1"], fg=C["amber"],
                font=("Consolas",10,"bold")).pack(anchor="w")
            tk.Label(col, text=case["subject"], bg=C["bg1"], fg=C["white"],
                font=("Georgia",12,"bold")).pack(anchor="w")
            tk.Label(col, text=f"{v.upper()} — Rule {case['rule']}", bg=C["bg1"], fg=vc,
                font=("Consolas",9,"bold")).pack(anchor="w", pady=(2,6))

            tk.Frame(col, bg=C["border"], height=1).pack(fill="x", pady=4)

            # Facts
            tk.Label(col, text="FACTS", bg=C["bg1"], fg=C["text3"],
                font=("Consolas",8,"bold")).pack(anchor="w")
            facts = json.loads(case.get("facts", "{}"))
            other_facts = json.loads(cases[1-idx].get("facts", "{}"))
            for k, val in facts.items():
                other_val = other_facts.get(k)
                match = other_val == val
                fg_c = C["green"] if match else C["red"]
                tk.Label(col, text=f"  {k}: {val}", bg=C["bg1"], fg=fg_c,
                    font=("Consolas",8)).pack(anchor="w")

            tk.Frame(col, bg=C["border"], height=1).pack(fill="x", pady=4)
            tk.Label(col, text=f"Reason: {case.get('reason','—')}", bg=C["bg1"],
                fg=C["text2"], font=("Segoe UI",8), wraplength=380).pack(anchor="w")

        tk.Button(win, text="✕  Close", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",9), padx=12, pady=5,
            command=win.destroy).pack(pady=6)

    # ── PIE CHART ────────────────────────────────────────────────
    def _draw_pie_chart(self, granted, surety, denied):
        c = self.pie_canvas
        c.delete("all")
        total = granted + surety + denied
        if total == 0:
            c.create_text(200, 90, text="No data yet",
                fill=C["text3"], font=("Segoe UI",11))
            return

        cx, cy, r = 130, 90, 70
        colors = [C["green"], C["yellow"], C["red"]]
        labels = [f"Granted ({granted})", f"Conditions ({surety})", f"Denied ({denied})"]
        values = [granted, surety, denied]

        start = 0
        import math
        for i, val in enumerate(values):
            if val == 0:
                continue
            extent = (val / total) * 360
            c.create_arc(cx-r, cy-r, cx+r, cy+r,
                start=start, extent=extent,
                fill=colors[i], outline=C["bg0"], width=2)
            # Label
            mid_angle = math.radians(start + extent/2)
            lx = cx + (r + 30) * math.cos(mid_angle)
            ly = cy - (r + 30) * math.sin(mid_angle)
            c.create_text(lx, ly, text=labels[i],
                fill=colors[i], font=("Consolas",8,"bold"), anchor="center")
            start += extent

        # Center label
        c.create_oval(cx-30, cy-30, cx+30, cy+30, fill=C["bg0"], outline=C["bg0"])
        pct = (granted + surety) / total * 100
        c.create_text(cx, cy-6, text=f"{pct:.0f}%",
            fill=C["amber"], font=("Georgia",14,"bold"))
        c.create_text(cx, cy+12, text="grant rate",
            fill=C["text3"], font=("Consolas",7))

        # Legend
        lx = cx + r + 80
        for i, (lbl, col) in enumerate(zip(labels, colors)):
            y = 40 + i*28
            c.create_rectangle(lx, y, lx+14, y+14, fill=col, outline="")
            c.create_text(lx+20, y+7, text=lbl, fill=C["text2"],
                font=("Consolas",8), anchor="w")

    # ── THEME TOGGLE ─────────────────────────────────────────────
    def _toggle_theme(self):
        global C
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            new = {"bg0":"#0a0a0a","bg1":"#141414","bg2":"#1e1e1e","bg3":"#282828",
                   "bg4":"#333333","border":"#2a2a2a","card":"#161616",
                   "text":"#f0f0f0","text2":"#b0b0b0","text3":"#666666",
                   "accent":"#7ed957","accent2":"#a3e87c","accent3":"#2d5a1a",
                   "orange":"#e8913a","orange2":"#f0a858","orange3":"#5a3a16",
                   "amber":"#7ed957","amber2":"#a3e87c","amber3":"#2d5a1a",
                   "green":"#7ed957","green2":"#1e4a10","red":"#f05050","red2":"#5a1e1e",
                   "yellow":"#f0c040","blue":"#4a90e2","cyan":"#38c8d0",
                   "white":"#ffffff","glow":"#7ed95720"}
            self.theme_btn.config(text="☀")
        else:
            new = C_LIGHT
            self.theme_btn.config(text="🌙")

        for k, v in new.items():
            C[k] = v

        # Refresh bg of the root window
        self.configure(bg=C["bg0"])
        self._apply_styles()
        self._refresh_theme_recursive(self)
        save_setting("theme", "dark" if self.is_dark_theme else "light")

    def _refresh_theme_recursive(self, widget):
        """Walk widget tree and update colors."""
        try:
            wtype = widget.winfo_class()
            if wtype in ("Frame", "Label", "Button", "Checkbutton", "Radiobutton", "Canvas"):
                bg = widget.cget("bg")
                # Map old bg to new bg
                if bg in ("#0e1117","#f5f5f0"): widget.config(bg=C["bg0"])
                elif bg in ("#161b27","#eaeae5"): widget.config(bg=C["bg1"])
                elif bg in ("#1e2538","#ddddd8"): widget.config(bg=C["bg2"])
                elif bg in ("#252d42","#d0d0cb"): widget.config(bg=C["bg3"])
        except Exception:
            pass
        for child in widget.winfo_children():
            self._refresh_theme_recursive(child)

    # ── SHORTCUTS OVERLAY ────────────────────────────────────────
    def _show_shortcuts(self):
        win = tk.Toplevel(self)
        win.title("Keyboard Shortcuts")
        win.geometry("420x360")
        win.configure(bg=C["bg0"])
        win.grab_set()

        tk.Label(win, text="⌨  Keyboard Shortcuts", bg=C["bg1"], fg=C["amber"],
            font=("Georgia",12,"bold"), pady=10).pack(fill="x")

        shortcuts = [
            ("Ctrl + Enter", "Run inference"),
            ("Ctrl + E",     "Export current case to PDF"),
            ("Ctrl + F",     "Focus search bar in History"),
            ("Ctrl + B",     "Switch to Bail module"),
            ("Ctrl + L",     "Switch to Loan module"),
            ("Ctrl + S",     "Switch to Sentencing module"),
            ("Ctrl + /",     "Show this shortcuts dialog"),
        ]
        for key, desc in shortcuts:
            row = tk.Frame(win, bg=C["bg1"])
            row.pack(fill="x", padx=14, pady=1)
            tk.Label(row, text=key, bg=C["bg1"], fg=C["amber"],
                font=("Consolas",10,"bold"), width=16, anchor="w").pack(side="left", padx=6)
            tk.Label(row, text=desc, bg=C["bg1"], fg=C["text2"],
                font=("Segoe UI",9)).pack(side="left")

        tk.Button(win, text="✕  Close", bg=C["bg3"], fg=C["text2"],
            relief="flat", font=("Segoe UI",9), padx=12, pady=5,
            command=win.destroy).pack(pady=10)

# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = LexLogicApp()
    app._bind_keys()
    app.mainloop()
