import pytest
import sys
from pathlib import Path

# Allow tests to import modules from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator_pfa import PFACalculator
from calculator_salariat import SalariatCalculator
from tax_config import get_rules_for_year


class TestConditionCoverage:
    """
    Test suite designed for condition coverage.
    Ensures that every individual condition in a compound boolean expression 
    is evaluated to both True and False.
    """

    # Compound Condition in PFACalculator._get_cass_base 
    # Expression: if upper is None or venit_net_impozabil <= upper * self.minimum_wage:
    # Condition 1: upper is None
    # Condition 2: venit_net_impozabil <= upper * self.minimum_wage

    def test_pfa_cass_condition_upper_is_not_none_and_within_limit(self):
        """
        Target: upper is None (False) OR within_limit (True)
        Satisfies: Condition 1 = False, Condition 2 = True
        """
        # For 2024, first bracket upper is 6 * 3300 = 19800.
        # Income 10000 is <= 19800.
        calc = PFACalculator(0, 2024)
        # Condition 1 (upper is None): False (it's 6.0)
        # Condition 2 (within limit): True (10000 <= 19800)
        assert calc._get_cass_base(10000) == 0.0

    def test_pfa_cass_condition_upper_is_not_none_and_exceeds_limit(self):
        """
        Target: upper is None (False) OR within_limit (False)
        Satisfies: Condition 1 = False, Condition 2 = False
        """
        # For 2024, first bracket upper is 19800.
        # Income 25000 is > 19800, so it fails the first bracket check.
        calc = PFACalculator(0, 2024)
        # Condition 1 (upper is None): False
        # Condition 2 (within limit): False (25000 <= 19800 is False)
        # This will move to the next iteration of the loop.
        # To strictly test the condition of the FIRST bracket:
        # We verify it doesn't return the base of the first bracket.
        min_wage = 3300
        assert calc._get_cass_base(25000) != 0 * min_wage
        assert calc._get_cass_base(25000) == 6 * min_wage

    def test_pfa_cass_condition_upper_is_none(self):
        """
        Target: upper is None (True)
        Satisfies: Condition 1 = True
        """
        # For 2024, the last bracket has max_income_multiplier: null (None).
        # Income 300000 exceeds all previous brackets.
        calc = PFACalculator(0, 2024)
        # In the final iteration:
        # Condition 1 (upper is None): True
        # Condition 2: (not evaluated due to short-circuit, but counts for coverage)
        assert calc._get_cass_base(300000) == 60 * 3300

    # Basic Conditions (Condition coverage = Decision coverage for simple ones)

    def test_income_validation_conditions(self):
        """
        Target: venit_brut < 0
        """
        # Condition True
        with pytest.raises(ValueError):
            SalariatCalculator(-100, 2024)
        # Condition False
        assert SalariatCalculator(100, 2024).venit_brut == 100.0

    def test_tax_config_year_match_conditions(self):
        """
        Target: fiscal_year in YEARLY_TAX_RULES
        """
        # Condition True
        assert get_rules_for_year(2024)["minimum_wage"] == 3300.0
        # Condition False
        assert get_rules_for_year(2030)["minimum_wage"] == 3700.0

    def test_tax_config_fallback_logic_conditions(self):
        """
        Target: if previous_or_equal:
        Inside get_rules_for_year when year not in rules.
        """
        # Condition True (year 2030 has previous years 2023, 2024, 2025)
        assert get_rules_for_year(2030) is not None
        
        # Condition False (year 2020 has NO previous years)
        with pytest.raises(ValueError):
            get_rules_for_year(2020)
