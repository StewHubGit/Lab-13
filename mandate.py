"""Screen candidate portfolios against the supplied Meridian mandate.

All weights and share limits are percentages (90 means 90%, not 0.90).
Money inputs are USD millions. Uses only the Python standard library.
"""

from collections import defaultdict
from decimal import Decimal


# EDITABLE INPUTS
# Holding: (issuer, business days to redeem, reserve-eligible)
HOLDINGS = {
    "Cash": ("none", 0, True),
    "Treasury bills": ("U.S. Treasury", 1, True),
    "Treasury 10-year note": ("U.S. Treasury", 1, True),
    "Global equity index fund": ("diversified fund", 2, False),
    "Investment-grade bond fund": ("diversified fund", 3, False),
    "Private real estate fund": ("diversified fund", 90, False),
    "Acme Corp bonds": ("Acme Corp", 4, False),
    "Acme Corp stock": ("Acme Corp", 1, False),
}

CANDIDATES = {
    "A": {
        "Cash": 2,
        "Treasury bills": 2,
        "Treasury 10-year note": 10,
        "Global equity index fund": 60,
        "Investment-grade bond fund": 26,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
    "B": {
        "Cash": 1,
        "Treasury bills": 0,
        "Treasury 10-year note": 0,
        "Global equity index fund": 55,
        "Investment-grade bond fund": 20,
        "Private real estate fund": 15,
        "Acme Corp bonds": 5,
        "Acme Corp stock": 4,
    },
    "C": {
        "Cash": 1,
        "Treasury bills": 1,
        "Treasury 10-year note": 0,
        "Global equity index fund": 70,
        "Investment-grade bond fund": 20,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 8,
    },
    # Deliberate suitability challenge: checkable compliance is not suitability.
    "D": {
        "Cash": 0,
        "Treasury bills": 0,
        "Treasury 10-year note": 100,
        "Global equity index fund": 0,
        "Investment-grade bond fund": 0,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
}

RESERVE_SIZE = 100
QUARTERLY_DISTRIBUTION = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5
MINIMUM_LIQUID_SHARE = 90
ISSUER_LIMIT = 8
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}


def decimal(value):
    """Preserve editable decimal inputs without binary floating-point noise."""
    return Decimal(str(value))


def check_candidate(weights, reserve_minimum):
    """Return each check's label, measured percent, and pass/fail result."""
    unknown = set(weights) - set(HOLDINGS)
    if unknown:
        raise ValueError(f"Unknown holdings: {', '.join(sorted(unknown))}")

    # An omitted holding has zero weight.
    amounts = {holding: decimal(weights.get(holding, 0)) for holding in HOLDINGS}
    total = sum(amounts.values(), Decimal(0))
    lowest = min(amounts.values())
    eligible = Decimal(0)
    liquid = Decimal(0)
    companies = defaultdict(Decimal)

    for holding, weight in amounts.items():
        issuer, days, reserve_eligible = HOLDINGS[holding]
        if reserve_eligible:
            eligible += weight
        if days <= LIQUIDITY_WINDOW:
            liquid += weight
        if issuer not in EXEMPT_ISSUERS:
            companies[issuer] += weight

    largest_company = max(companies.values(), default=Decimal(0))
    return [
        ("Weights sum to 100%", total, total == 100),
        ("Lowest weight (long-only)", lowest, lowest >= 0),
        ("Reserve-eligible weight", eligible, eligible >= reserve_minimum),
        (
            f"Redeemable within {LIQUIDITY_WINDOW} business days",
            liquid,
            liquid >= decimal(MINIMUM_LIQUID_SHARE),
        ),
        ("Largest single company", largest_company, largest_company <= decimal(ISSUER_LIMIT)),
    ]


def main():
    if decimal(RESERVE_SIZE) <= 0:
        raise ValueError("Reserve size must be positive.")

    reserve_minimum = (
        decimal(QUARTERS_TO_COVER)
        * decimal(QUARTERLY_DISTRIBUTION)
        / decimal(RESERVE_SIZE)
        * 100
    )
    print(f"Reserve minimum: {reserve_minimum:.1f}%")

    for name, weights in CANDIDATES.items():
        print(f"\nCandidate {name}")
        checks = check_candidate(weights, reserve_minimum)
        for label, measured, passed in checks:
            print(f"  {label}: {measured:.1f}% - {'pass' if passed else 'FAIL'}")
        print("  Calendar-year loss rule: requires CIO clarification")
        failures = sum(not passed for _, _, passed in checks)
        verdict = "passes every checkable rule" if failures == 0 else f"fails {failures} rule(s)"
        print(f"  {verdict}")


if __name__ == "__main__":
    main()
