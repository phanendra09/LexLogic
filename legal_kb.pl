% ================================================================
%  LexLogic — AI Legal Reasoning Knowledge Base
%  Project 4.1: AI-Based Legal Reasoning System
%  Logic: Propositional + First-Order Logic (Horn Clauses)
%  Inference: SLD Resolution (Backward Chaining via Prolog)
% ================================================================

:- use_module(library(lists)).

% ── DYNAMIC FACTS (asserted per query) ─────────────────────────
:- dynamic
    has_local_address/1,
    has_employment/1,
    has_family_ties/1,
    years_in_community/2,
    violent_offense/1,
    capital_offense/1,
    minor_offense/1,
    first_offense/1,
    repeat_offender/1,
    weapon_involved/1,
    credit_score/2,
    employment_months/2,
    monthly_income/2,
    monthly_debt/2,
    has_cosigner/1,
    has_bankruptcy/1,
    bankruptcy_years_ago/2.


% ================================================================
%  MODULE 1: BAIL ELIGIBILITY
%  FOL Horn Clauses — Backward chaining resolves sub-goals
% ================================================================

% ── BAIL RULES ─────────────────────────────────────────────────

% Rule B3 (Hard Denial): Capital offense → always denied
bail_verdict(Person, denied, 'B3', 'Capital offense: bail denied by statute') :-
    capital_offense(Person), !.

% Rule B4 (Hard Denial): Violent + repeat offender → denied
bail_verdict(Person, denied, 'B4', 'Repeat violent offender: bail denied') :-
    violent_offense(Person),
    repeat_offender(Person), !.

% Rule B1 (Grant): Standard eligibility
bail_verdict(Person, granted, 'B1', 'Not flight risk + not dangerous + community ties') :-
    not_flight_risk(Person),
    not_dangerous(Person),
    community_ties(Person), !.

% Rule B2 (Grant with surety): Minor first offense
bail_verdict(Person, surety, 'B2', 'Minor first offense: granted with surety bond') :-
    minor_offense(Person),
    first_offense(Person), !.

% Default: no rule satisfied
bail_verdict(_Person, denied, 'NONE', 'No eligibility rule satisfied').


% ── BAIL SUB-GOALS (FOL predicates) ────────────────────────────

% not_flight_risk: address AND (employment OR family)
not_flight_risk(Person) :-
    has_local_address(Person),
    has_employment(Person).

not_flight_risk(Person) :-
    has_local_address(Person),
    has_family_ties(Person).

% not_dangerous: no violent offense AND no weapon
not_dangerous(Person) :-
    \+ violent_offense(Person),
    \+ weapon_involved(Person).

% community_ties: family OR (employment AND 2+ years)
community_ties(Person) :-
    has_family_ties(Person).

community_ties(Person) :-
    has_employment(Person),
    years_in_community(Person, Y),
    Y >= 2.


% ── BAIL TRACE (explanation terms) ─────────────────────────────

bail_trace(Person, Steps) :-
    findall(Step, bail_step(Person, Step), Steps).

bail_step(Person, step(pass, 'local_address confirmed',
        'has_local_address(X) ≡ TRUE')) :-
    has_local_address(Person).
bail_step(Person, step(fail, 'local_address missing',
        'has_local_address(X) ≡ FALSE')) :-
    \+ has_local_address(Person).

bail_step(Person, step(pass, 'employment confirmed',
        'has_employment(X) ≡ TRUE')) :-
    has_employment(Person).
bail_step(Person, step(fail, 'employment missing',
        'has_employment(X) ≡ FALSE')) :-
    \+ has_employment(Person).

bail_step(Person, step(pass, 'family ties confirmed',
        'has_family_ties(X) ≡ TRUE')) :-
    has_family_ties(Person).

bail_step(Person, step(pass, 'not_flight_risk derived',
        'local_address(X) ∧ (employment(X) ∨ family(X)) → ¬flight_risk(X)')) :-
    not_flight_risk(Person).
bail_step(Person, step(fail, 'not_flight_risk FAILED',
        'Requires: local_address ∧ (employment ∨ family_ties)')) :-
    \+ not_flight_risk(Person).

bail_step(Person, step(pass, 'not_dangerous derived',
        '¬violent_offense(X) ∧ ¬weapon(X) → ¬dangerous(X)')) :-
    not_dangerous(Person).
bail_step(Person, step(fail, 'not_dangerous FAILED — offense/weapon present',
        'violent_offense(X) ∨ weapon_involved(X) ≡ TRUE')) :-
    \+ not_dangerous(Person).

bail_step(Person, step(pass, 'community_ties derived',
        'family_ties(X) ∨ (employment(X) ∧ years≥2) → community_ties(X)')) :-
    community_ties(Person).
bail_step(Person, step(fail, 'community_ties FAILED',
        'Requires: family_ties(X) ∨ (employment(X) ∧ years_in_community≥2)')) :-
    \+ community_ties(Person).

bail_step(Person, step(pass, 'minor_offense confirmed',
        'minor_offense(X) ≡ TRUE')) :-
    minor_offense(Person).
bail_step(Person, step(pass, 'first_offense confirmed',
        'first_offense(X) ≡ TRUE')) :-
    first_offense(Person).
bail_step(Person, step(fail, 'capital_offense present — hard denial',
        'capital_offense(X) ≡ TRUE → Rule B3 fires')) :-
    capital_offense(Person).
bail_step(Person, step(fail, 'violent + repeat offender — hard denial',
        'violent_offense(X) ∧ repeat_offender(X) ≡ TRUE → Rule B4 fires')) :-
    violent_offense(Person), repeat_offender(Person).


% ================================================================
%  MODULE 2: LOAN APPROVAL
%  Propositional thresholds + FOL rules over individuals
% ================================================================

% ── LOAN RULES ─────────────────────────────────────────────────

% Rule D2 (Hard Denial): Recent bankruptcy
loan_verdict(Person, denied, 'D2', 'Bankruptcy within 7 years: denied by policy') :-
    has_bankruptcy(Person),
    bankruptcy_years_ago(Person, Y),
    Y < 7, !.

% Rule D1 (Hard Denial): Poor credit, no co-signer
loan_verdict(Person, denied, 'D1', 'Poor credit score with no co-signer') :-
    poor_credit_score(Person),
    \+ has_cosigner(Person), !.

% Rule L3 (Premium): Excellent credit + high income
loan_verdict(Person, granted, 'L3', 'Excellent credit + high income: premium approval') :-
    excellent_credit_score(Person),
    high_income(Person), !.

% Rule L1 (Standard): Good credit + stable income + low DTI
loan_verdict(Person, granted, 'L1', 'Good credit + stable income + low debt ratio') :-
    good_credit_score(Person),
    stable_income(Person),
    low_debt_ratio(Person), !.

% Rule L2 (Co-signer): Moderate credit + stable + co-signer
loan_verdict(Person, surety, 'L2', 'Moderate credit with co-signer + stable income') :-
    moderate_credit_score(Person),
    stable_income(Person),
    has_cosigner(Person), !.

% Default
loan_verdict(_Person, denied, 'NONE', 'No loan approval rule satisfied').


% ── CREDIT SCORE CLASSIFICATION (Propositional) ────────────────

excellent_credit_score(P) :- credit_score(P, S), S >= 800.
good_credit_score(P)      :- credit_score(P, S), S >= 700, S < 800.
moderate_credit_score(P)  :- credit_score(P, S), S >= 600, S < 700.
poor_credit_score(P)      :- credit_score(P, S), S < 600.

% ── INCOME & DTI (Propositional thresholds) ────────────────────

stable_income(P) :-
    employment_months(P, M), M >= 24,
    monthly_income(P, I), I > 2000.

high_income(P) :-
    monthly_income(P, I), I > 8000.

low_debt_ratio(P) :-
    monthly_income(P, I), I > 0,
    monthly_debt(P, D),
    Ratio is D / I,
    Ratio =< 0.43.


% ── LOAN TRACE ─────────────────────────────────────────────────

loan_trace(Person, Steps) :-
    findall(Step, loan_step(Person, Step), Steps).

loan_step(Person, step(pass, Label, Logic)) :-
    excellent_credit_score(Person),
    credit_score(Person, S),
    format(atom(Label), 'Credit: Excellent (~w)', [S]),
    Logic = 'credit_score(X,S) ∧ S≥800 → excellent_credit(X)'.
loan_step(Person, step(pass, Label, Logic)) :-
    \+ excellent_credit_score(Person),
    good_credit_score(Person),
    credit_score(Person, S),
    format(atom(Label), 'Credit: Good (~w)', [S]),
    Logic = 'credit_score(X,S) ∧ 700≤S<800 → good_credit(X)'.
loan_step(Person, step(warn, Label, Logic)) :-
    \+ excellent_credit_score(Person),
    \+ good_credit_score(Person),
    moderate_credit_score(Person),
    credit_score(Person, S),
    format(atom(Label), 'Credit: Moderate (~w)', [S]),
    Logic = 'credit_score(X,S) ∧ 600≤S<700 → moderate_credit(X)'.
loan_step(Person, step(fail, Label, Logic)) :-
    poor_credit_score(Person),
    credit_score(Person, S),
    format(atom(Label), 'Credit: Poor (~w)', [S]),
    Logic = 'credit_score(X,S) ∧ S<600 → poor_credit(X)'.

loan_step(Person, step(pass, Label, Logic)) :-
    stable_income(Person),
    employment_months(Person, M),
    monthly_income(Person, I),
    format(atom(Label), 'Stable income: ~wmo tenure, $~w/mo', [M, I]),
    Logic = 'employment_months(X,M) ∧ M≥24 ∧ monthly_income(X,I) ∧ I>2000 → stable_income(X)'.
loan_step(Person, step(fail, Label, Logic)) :-
    \+ stable_income(Person),
    format(atom(Label), 'Stable income FAILED', []),
    Logic = 'Requires: employment_months≥24 ∧ monthly_income>$2,000'.

loan_step(Person, step(pass, Label, Logic)) :-
    low_debt_ratio(Person),
    monthly_income(Person, I), monthly_debt(Person, D),
    Ratio is D / I,
    format(atom(Label), 'Low DTI: ~1f%', [Ratio*100]),
    Logic = 'monthly_debt/monthly_income ≤ 0.43 → low_debt_ratio(X)'.
loan_step(Person, step(fail, Label, Logic)) :-
    \+ low_debt_ratio(Person),
    format(atom(Label), 'High DTI — exceeds 43% threshold', []),
    Logic = 'monthly_debt/monthly_income > 0.43 → ¬low_debt_ratio(X)'.

loan_step(Person, step(pass, 'High income confirmed',
        'monthly_income(X,I) ∧ I>8000 → high_income(X)')) :-
    high_income(Person).

loan_step(Person, step(pass, 'Co-signer present',
        'has_cosigner(X) ≡ TRUE')) :-
    has_cosigner(Person).

loan_step(Person, step(fail, 'Bankruptcy within 7 years — hard denial',
        'has_bankruptcy(X) ∧ years_ago<7 → loan_denied(X) [Rule D2]')) :-
    has_bankruptcy(Person),
    bankruptcy_years_ago(Person, Y), Y < 7.


% ================================================================
%  MODULE 3: CRIMINAL SENTENCING
%  FOL Horn Clauses — severity + aggravating/mitigating factors
% ================================================================

:- dynamic
    offense_severity/2,
    premeditation/1,
    victim_vulnerability/1,
    shows_remorse/1,
    cooperated/1,
    mental_health_factor/1,
    prior_convictions/2.

% Rule S4 (Maximum): severity >= 8 AND premeditation AND weapon
sentencing_verdict(Person, maximum, 'S4', 'Maximum sentence: severe premeditated offense with weapon') :-
    offense_severity(Person, S), S >= 8,
    premeditation(Person),
    weapon_involved(Person), !.

% Rule S3 (Severe): severity >= 6 AND any aggravating factor
sentencing_verdict(Person, severe, 'S3', 'Severe sentence: high severity with aggravating factors') :-
    offense_severity(Person, S), S >= 6,
    has_aggravating(Person), !.

% Rule S1 (Minimal): severity =< 3 AND mitigating factors AND first offense
sentencing_verdict(Person, minimal, 'S1', 'Minimal sentence: low severity with mitigating circumstances') :-
    offense_severity(Person, S), S =< 3,
    has_mitigating(Person),
    first_offense(Person), !.

% Rule S2 (Moderate): default — severity 4-7 or no special factors
sentencing_verdict(Person, moderate, 'S2', 'Moderate sentence: standard guidelines apply') :-
    offense_severity(Person, _), !.

% Default
sentencing_verdict(_Person, moderate, 'NONE', 'Default moderate sentence — insufficient data').

% Aggravating sub-goals
has_aggravating(Person) :- premeditation(Person).
has_aggravating(Person) :- weapon_involved(Person).
has_aggravating(Person) :- victim_vulnerability(Person).
has_aggravating(Person) :- prior_convictions(Person, N), N >= 2.

% Mitigating sub-goals
has_mitigating(Person) :- shows_remorse(Person).
has_mitigating(Person) :- cooperated(Person).
has_mitigating(Person) :- mental_health_factor(Person).

% Sentencing trace
sentencing_trace(Person, Steps) :-
    findall(Step, sentencing_step(Person, Step), Steps).

sentencing_step(Person, step(pass, Label, 'offense_severity(X,S)')) :-
    offense_severity(Person, S),
    format(atom(Label), 'Offense severity: ~w/10', [S]).
sentencing_step(Person, step(pass, 'Premeditation confirmed', 'premeditation(X) = TRUE')) :-
    premeditation(Person).
sentencing_step(Person, step(pass, 'Victim vulnerability confirmed', 'victim_vulnerability(X) = TRUE')) :-
    victim_vulnerability(Person).
sentencing_step(Person, step(pass, 'Shows remorse', 'shows_remorse(X) = TRUE')) :-
    shows_remorse(Person).
sentencing_step(Person, step(pass, 'Cooperated with authorities', 'cooperated(X) = TRUE')) :-
    cooperated(Person).
sentencing_step(Person, step(pass, 'Mental health factor present', 'mental_health_factor(X) = TRUE')) :-
    mental_health_factor(Person).
sentencing_step(Person, step(pass, Label, 'prior_convictions(X,N)')) :-
    prior_convictions(Person, N),
    format(atom(Label), 'Prior convictions: ~w', [N]).
sentencing_step(Person, step(pass, 'Has aggravating factors', 'has_aggravating(X) = TRUE')) :-
    has_aggravating(Person).
sentencing_step(Person, step(fail, 'No aggravating factors', 'has_aggravating(X) = FALSE')) :-
    \+ has_aggravating(Person).
sentencing_step(Person, step(pass, 'Has mitigating factors', 'has_mitigating(X) = TRUE')) :-
    has_mitigating(Person).
sentencing_step(Person, step(fail, 'No mitigating factors', 'has_mitigating(X) = FALSE')) :-
    \+ has_mitigating(Person).


% ================================================================
%  MODULE 4: ETHICS / CONFLICT-OF-INTEREST
%  FOL rules for judicial/legal ethics screening
% ================================================================

:- dynamic
    relationship_type/2,      % family, financial, professional, none
    disclosure_made/1,
    prior_conflict/1,
    conflict_severity/2.       % 1-5

% Rule E3 (Disqualification): family/financial relationship + high severity + no disclosure
ethics_verdict(Person, disqualification, 'E3', 'Disqualification: undisclosed serious conflict') :-
    relationship_type(Person, Type),
    member(Type, [family, financial]),
    conflict_severity(Person, Sev), Sev >= 4,
    \+ disclosure_made(Person), !.

% Rule E2 (Recusal): any non-none relationship + prior conflict
ethics_verdict(Person, recusal, 'E2', 'Recusal required: prior conflict with active relationship') :-
    relationship_type(Person, Type),
    Type \= none,
    prior_conflict(Person), !.

% Rule E1 (Waivable): minor conflict, disclosed, low severity
ethics_verdict(Person, waivable, 'E1', 'Conflict waivable: disclosed minor relationship') :-
    relationship_type(Person, Type),
    Type \= none,
    disclosure_made(Person),
    conflict_severity(Person, Sev), Sev =< 2, !.

% Default: no conflict
ethics_verdict(_Person, clear, 'NONE', 'No conflict of interest detected').

% Ethics trace
ethics_trace(Person, Steps) :-
    findall(Step, ethics_step(Person, Step), Steps).

ethics_step(Person, step(pass, Label, 'relationship_type(X,T)')) :-
    relationship_type(Person, T),
    format(atom(Label), 'Relationship type: ~w', [T]).
ethics_step(Person, step(pass, 'Disclosure made', 'disclosure_made(X) = TRUE')) :-
    disclosure_made(Person).
ethics_step(Person, step(fail, 'No disclosure made', 'disclosure_made(X) = FALSE')) :-
    \+ disclosure_made(Person).
ethics_step(Person, step(pass, 'Prior conflict exists', 'prior_conflict(X) = TRUE')) :-
    prior_conflict(Person).
ethics_step(Person, step(fail, 'No prior conflict', 'prior_conflict(X) = FALSE')) :-
    \+ prior_conflict(Person).
ethics_step(Person, step(pass, Label, 'conflict_severity(X,S)')) :-
    conflict_severity(Person, S),
    format(atom(Label), 'Conflict severity: ~w/5', [S]).


% ================================================================
%  QUERY INTERFACE — called by Python via subprocess
% ================================================================

% run_bail_query(+Name, +FactsAtom)
run_bail_query(Name, FactsAtom) :-
    term_to_atom(Facts, FactsAtom),
    retract_all_facts(Name),
    assert_facts(Name, Facts),
    bail_verdict(Name, Verdict, Rule, Reason),
    bail_trace(Name, TraceSteps),
    format(atom(Out), '~w|~w|~w|~w', [Verdict, Rule, Reason, TraceSteps]),
    writeln(Out).

% run_loan_query(+Name, +FactsAtom)
run_loan_query(Name, FactsAtom) :-
    term_to_atom(Facts, FactsAtom),
    retract_all_facts(Name),
    assert_facts(Name, Facts),
    loan_verdict(Name, Verdict, Rule, Reason),
    loan_trace(Name, TraceSteps),
    format(atom(Out), '~w|~w|~w|~w', [Verdict, Rule, Reason, TraceSteps]),
    writeln(Out).


% ================================================================
%  FACT ASSERTION ENGINE
% ================================================================

retract_all_facts(P) :-
    forall(member(F, [has_local_address,has_employment,has_family_ties,
                      violent_offense,capital_offense,minor_offense,
                      first_offense,repeat_offender,weapon_involved,
                      has_cosigner,has_bankruptcy]),
           (G =.. [F,P], retractall(G))),
    retractall(years_in_community(P,_)),
    retractall(credit_score(P,_)),
    retractall(employment_months(P,_)),
    retractall(monthly_income(P,_)),
    retractall(monthly_debt(P,_)),
    retractall(bankruptcy_years_ago(P,_)).

assert_facts(_, []).
assert_facts(P, [H|T]) :- assert_fact(P, H), assert_facts(P, T).

assert_fact(P, local_address)         :- assertz(has_local_address(P)).
assert_fact(P, employment)            :- assertz(has_employment(P)).
assert_fact(P, family_ties)           :- assertz(has_family_ties(P)).
assert_fact(P, violent_offense)       :- assertz(violent_offense(P)).
assert_fact(P, capital_offense)       :- assertz(capital_offense(P)).
assert_fact(P, minor_offense)         :- assertz(minor_offense(P)).
assert_fact(P, first_offense)         :- assertz(first_offense(P)).
assert_fact(P, repeat_offender)       :- assertz(repeat_offender(P)).
assert_fact(P, weapon_involved)       :- assertz(weapon_involved(P)).
assert_fact(P, has_cosigner)          :- assertz(has_cosigner(P)).
assert_fact(P, has_bankruptcy)        :- assertz(has_bankruptcy(P)).
assert_fact(P, years_in_community(Y)) :- assertz(years_in_community(P,Y)).
assert_fact(P, credit_score(S))       :- assertz(credit_score(P,S)).
assert_fact(P, employment_months(M))  :- assertz(employment_months(P,M)).
assert_fact(P, monthly_income(I))     :- assertz(monthly_income(P,I)).
assert_fact(P, monthly_debt(D))       :- assertz(monthly_debt(P,D)).
assert_fact(P, bankruptcy_years(Y))   :- assertz(bankruptcy_years_ago(P,Y)).
