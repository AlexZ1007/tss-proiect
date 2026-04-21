import pytest
import sys
from pathlib import Path

# Allow tests to import modules from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator_pfa import PFACalculator
from tax_config import get_rules_for_year, get_available_years


class TestBasisPath:
    """
    Test suite designed for Basis Path Testing.
    Targets the linearly independent paths through the control flow graph.
    """

    # Path Analysis for PFACalculator._get_cas_base
    # The method has 3 independent paths (Cyclomatic Complexity = 3):
    # Path 1: Income < lower_threshold -> return 0.0
    # Path 2: Income >= lower_threshold AND Income < upper_threshold -> return lower_base
    # Path 3: Income >= upper_threshold -> return upper_base

    def test_cas_base_path_1_below_lower(self):
        """Path 1: Income is strictly below the lower threshold."""
        calc = PFACalculator(10000, 2024)
        # Threshold is 39600. Input 10000.
        assert calc._get_cas_base(10000) == 0.0

    def test_cas_base_path_2_between_thresholds(self):
        """Path 2: Income is between the lower and upper thresholds."""
        calc = PFACalculator(50000, 2024)
        # Thresholds: 39600 and 79200. Input 50000.
        min_wage = 3300
        assert calc._get_cas_base(50000) == 12 * min_wage

    def test_cas_base_path_3_above_upper(self):
        """Path 3: Income is exactly at or above the upper threshold."""
        calc = PFACalculator(100000, 2024)
        # Upper threshold is 79200. Input 100000.
        min_wage = 3300
        assert calc._get_cas_base(100000) == 24 * min_wage

    # Path Analysis for get_rules_for_year 
    # The method has 3 independent paths:
    # Path 1: fiscal_year in YEARLY_TAX_RULES (Exact match)
    # Path 2: fiscal_year not in rules, but previous_or_equal exists (Fallback)
    # Path 3: fiscal_year not in rules, and no previous_or_equal (ValueError)

    def test_get_rules_path_1_exact_match(self):
        """Path 1: The requested year exists in the configuration."""
        available_years = get_available_years()
        target_year = available_years[0]
        rules = get_rules_for_year(target_year)
        assert rules is not None
        assert "minimum_wage" in rules

    def test_get_rules_path_2_fallback(self):
        """Path 2: The year is missing but a previous year exists (future year fallback)."""
        max_year = max(get_available_years())
        rules = get_rules_for_year(max_year + 5)
        # Should return the rules for the latest available year.
        expected_rules = get_rules_for_year(max_year)
        assert rules == expected_rules

    def test_get_rules_path_3_no_history(self):
        """Path 3: The year is before any configured data."""
        min_year = min(get_available_years())
        with pytest.raises(ValueError, match="Minimum configured year is"):
            get_rules_for_year(min_year - 1)

    # Path Analysis for TaxCalculator.__init__ 
    # Path 1: Income < 0 (Exception)
    # Path 2: Income >= 0 (Success)

    def test_init_path_1_negative_income(self):
        """Path 1: Initialization with negative income triggers an exception."""
        with pytest.raises(ValueError, match="Income must be positive"):
            PFACalculator(-1, 2024)

    def test_init_path_2_valid_income(self):
        """Path 2: Initialization with valid income completes normally."""
        calc = PFACalculator(1000, 2024)
        assert calc.venit_brut == 1000.0
