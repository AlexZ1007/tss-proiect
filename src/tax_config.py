from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Dict


def _load_rules_from_json() -> Dict[int, Dict[str, Any]]:
    config_path = Path(__file__).resolve().parent / "tax_rules.json"
    raw_rules = json.loads(config_path.read_text(encoding="utf-8"))
    # JSON object keys are strings, but app uses int fiscal years.
    return {int(year): rules for year, rules in raw_rules.items()}


# Central place for fiscal rules loaded from external JSON.
YEARLY_TAX_RULES: Dict[int, Dict[str, Any]] = _load_rules_from_json()


def get_available_years() -> list[int]:
    # Used by UI to populate fiscal year selector.
    return sorted(YEARLY_TAX_RULES.keys())


def get_rules_for_year(fiscal_year: int) -> Dict[str, Any]:
    """
    Return fiscal rules for the given year.

    If an exact year is not available, the latest previous configured year is used.
    Example: if only 2023-2025 exist, asking 2026 returns 2025 rules.
    """
    years = get_available_years()
    if not years:
        raise ValueError("No fiscal rules configured.")

    if fiscal_year in YEARLY_TAX_RULES:
        # deepcopy prevents accidental runtime mutation of source config.
        return deepcopy(YEARLY_TAX_RULES[fiscal_year])

    previous_or_equal = [year for year in years if year <= fiscal_year]
    if previous_or_equal:
        # Forward-compatibility: unknown future year reuses latest known rules.
        return deepcopy(YEARLY_TAX_RULES[max(previous_or_equal)])

    raise ValueError(
        f"No fiscal rules available for year {fiscal_year}. "
        f"Minimum configured year is {min(years)}."
    )
