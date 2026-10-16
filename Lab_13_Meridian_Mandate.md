# Lab 13: Meridian Foundation mandate checker

Prepared with AI assistance from the supplied case. No optimization was performed. This file records the classifications, computed results, failure probe, assessment of candidate D, and policy interpretation. It does not represent an independently completed AI-off exercise.

## 1. Statement types: S1-S10

| Statement | Type | Reason |
|---|---|---|
| S1: Seven-year horizon; annual rebalancing. | Hard constraint | Defines the planning horizon and an implementation requirement; rebalancing is not permission to exceed other limits. |
| S2: CPI + 4% annually, net of costs, over rolling five-year periods. | Objective | Specifies the desired real return, cost basis, and evaluation period; achieving it is not guaranteed. |
| S3: Distribute $0.75m quarterly; hold twelve months in cash or daily-liquid government securities. | Hard constraint | Requires $3m, or 3% of the $100m portfolio, in reserve-eligible holdings. |
| S4: Benchmark is 60% global equities / 40% U.S. investment-grade bonds. | Preference / evaluation reference | Establishes a comparator, but supplies no required allocation bands or tracking-error limit. |
| S5: Long-only; no borrowing, short sales, or derivatives. | Hard constraint | Restricts financing and exposures; the checker tests nonnegative supplied holdings and full allocation. |
| S6: No issuer above 8%. | Hard constraint | Aggregates one company's securities; cash, U.S. Treasury securities, and diversified funds are exempt under the case rule. |
| S7: Annual turnover at most 25% without committee approval. | Hard constraint with approval exception | Exceeding the cap requires approval; a holdings snapshot cannot establish annual turnover. |
| S8: At least 90% redeemable within five business days. | Hard constraint | Supplies a measurable liquidity threshold and window. |
| S9: No calendar-year loss greater than 10%; no measure or breach rule. | Unverifiable promise as stated | The loss definition and policy response are missing; holdings alone cannot establish a future loss guarantee. The program never tests this statement. |
| S10: No sector, ESG, tax, or home-bias preference; pilot optimization unspecified. | Missing | Those preferences are explicitly absent, but the optimization criterion has not been selected. |

## 2. Checker and observed results

Run the standard-library-only file from the same folder:

```powershell
python mandate.py
```

All holdings, weights, and thresholds are editable at the top. Results are computed from those inputs, including issuer aggregation. The minimum reserve is calculated as:

**4 quarters x $0.75m / $100m x 100 = 3.0%.**

The case explicitly marks the Treasury 10-year note reserve-eligible, so it counts. Redeemability is evaluated using the supplied business-day values. The program does not silently substitute different eligibility definitions.

| Rule / measured percentage | A | B | C | D |
|---|---|---|---|---|
| Weights sum to 100% | 100.0 pass | 100.0 pass | 100.0 pass | 100.0 pass |
| Lowest weight is nonnegative | 0.0 pass | 0.0 pass | 0.0 pass | 0.0 pass |
| Reserve-eligible weight >= 3.0% | 14.0 pass | 1.0 FAIL | 2.0 FAIL | 100.0 pass |
| Redeemable in five days >= 90.0% | 100.0 pass | 85.0 FAIL | 100.0 pass | 100.0 pass |
| Largest nonexempt company <= 8.0% | 0.0 pass | 9.0 FAIL | 8.0 pass | 0.0 pass |
| Calendar-year loss rule | requires CIO clarification | requires CIO clarification | requires CIO clarification | requires CIO clarification |
| Verdict | passes every checkable rule | fails 3 rule(s) | fails 1 rule(s) | passes every checkable rule |

B's Acme bonds (5%) and Acme stock (4%) total **9%**. C's 8% Acme holding is exactly at the cap and passes. Exempt issuers do not enter the largest-company calculation.

### Negative-weight probe

Temporarily changed A's Cash from **2 to -2** and global equity index fund from **60 to 64**, then ran the checker. Observed:

| A probe check | Measured percentage | Result |
|---|---:|---|
| Total weight | 100.0 | pass |
| Lowest weight | -2.0 | FAIL |
| Reserve-eligible weight | 10.0 | pass |
| Five-day liquidity | 100.0 | pass |
| Largest nonexempt company | 0.0 | pass |

The verdict was **fails 1 rule(s)**. The reserve passes because -2% cash + 2% bills + 10% Treasury notes = 10%. The long-only failure is still decisive. Restored A to Cash **2** and global equities **60**, reran, and recovered its original passing result. The saved inputs contain the restored portfolio.

## 3. The attack: candidate D

| Holding | D weight |
|---|---:|
| Cash | 0% |
| Treasury bills | 0% |
| Treasury 10-year note | 100% |
| Global equity index fund | 0% |
| Investment-grade bond fund | 0% |
| Private real estate fund | 0% |
| Acme Corp bonds | 0% |
| Acme Corp stock | 0% |

D is included in `mandate.py` and runs with A-C. It passes all five checkable rules: the note is reserve-eligible, redeems in one business day, and has an exempt Treasury issuer.

**Assessment: reject D as a client recommendation pending clarification of S9.** Its entire value is exposed to the market-price movements of a long-term bond. Fast redemption does not mean price stability, so the liquidity check cannot establish protection against a large calendar-year loss. This is a specific weakness in the checker-to-client link, not a demonstrated numerical breach of S9: no yield, duration, rate scenario, or operational loss measure was supplied.

D also has no demonstrated basis for satisfying S2's CPI + 4% objective. Its deviation from the S4 benchmark is a review concern, not an automatic mandate violation, because S4 contains no allocation or tracking-error limits. Passing the script therefore earns D further scrutiny, not investment approval.

## 4. One question for the CIO

**Question:** What should the pilot optimize: downside protection, achieving CPI + 4%, or tracking the 60/40 benchmark?

**Answer that changes the design:** Prioritize downside protection; the 10% loss concern matters more than benchmark tracking.

**Design consequence:** Replace the proposed 100% 10-year Treasury exposure with greater cash and Treasury-bill exposure to reduce interest-rate sensitivity. This is a design direction, not an optimized allocation or a claim that the return target will be met. Before implementing an optimizer, translate the answer into an approved, measurable downside criterion; the actual CIO has not supplied that answer yet.

## 5. Reflection and provisional policy statement

**Why passing can still be wrong:** The checker establishes only five properties of the proposed holdings. It does not establish return adequacy (S2), acceptable losses (S9), annual turnover compliance (S7), or the annual implementation plan (S1). It cannot select what Meridian should value most when S10 leaves the optimization criterion unspecified. D demonstrates that compliant liquidity and exempt issuer concentration can coexist with concentrated market risk.

**Least-certain type: S4.** A benchmark is an evaluation reference rather than a natural fit for the five supplied labels. Preference is the closest available label. Treating it as a hard 60/40 allocation would invent a rule. Explicit allocation bands or a tracking-error limit from the CIO would change that classification.

**Provisional policy statement:** Manage the $100m reserve over a seven-year horizon with annual rebalancing (S1), pursuing CPI + 4% annually net of costs over rolling five-year periods (S2). Fund the $0.75m quarterly distribution and maintain at least twelve months of payouts in the case's reserve-eligible assets (S3). Evaluate performance against the 60/40 benchmark without inventing allocation bands (S4). Hold only permitted long positions with no borrowing, short sales, or derivatives (S5); aggregate company exposures under the 8% cap and apply the stated exemptions (S6). Keep annual turnover within 25% unless the committee approves otherwise (S7), and maintain at least 90% five-business-day liquidity (S8). Record S9 as unresolved rather than promising a loss ceiling. Apply no unstated sector, ESG, tax, or home-bias preference, and obtain the CIO's optimization criterion before optimizing (S10).

A and D pass the current holdings screen. B and C fail it. None of those outcomes alone establishes full mandate compliance or client suitability.
