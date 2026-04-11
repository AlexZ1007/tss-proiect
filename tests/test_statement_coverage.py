# acoperire la nivel de instructiuni
import pytest
import sys
from pathlib import Path

# Allow tests to import modules from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator_pfa import PFACalculator
from calculator_salariat import SalariatCalculator
from tax_config import get_available_years, get_rules_for_year, _load_rules_from_json


class TestStatementCoverage:
    """
    Test suite designed for statement coverage.
    Each test ensures that specific code paths and statements are executed.
    """

    # Coverage for calculator_base.py
    def test_calculator_base_init_valid(self):
        """Cover valid initialization path"""
        calc = SalariatCalculator(100000, 2024)
        assert calc.venit_brut == 100000.0
        assert calc.anul_fiscal == 2024
        assert "salariat" in calc.rules

    def test_calculator_base_init_negative_income(self):
        """Cover ValueError for negative income"""
        with pytest.raises(ValueError, match="Income must be positive"):
            SalariatCalculator(-1000, 2024)

    def test_calculator_base_init_zero_income(self):
        """Cover zero income (edge case)"""
        calc = SalariatCalculator(0, 2024)
        assert calc.venit_brut == 0.0

    # Coverage for calculator_salariat.py
    def test_salariat_calculate_normal_case(self):
        """Cover normal calculation path"""
        calc = SalariatCalculator(100000, 2024)
        result = calc.calculate()
        assert result["cas"] == 25000.0
        assert result["cass"] == 10000.0
        assert result["impozit"] == 6500.0
        assert result["venit_net"] == 58500.0

    def test_salariat_calculate_zero_income(self):
        """Cover calculation with zero income"""
        calc = SalariatCalculator(0, 2024)
        result = calc.calculate()
        assert result["cas"] == 0.0
        assert result["cass"] == 0.0
        assert result["impozit"] == 0.0
        assert result["venit_net"] == 0.0

    def test_salariat_calculate_tax_free_year(self):
        """Cover calculation in tax-free year (2025+)"""
        calc = SalariatCalculator(100000, 2025)
        result = calc.calculate()
        assert result["cas"] == 25000.0
        assert result["cass"] == 10000.0
        assert result["impozit"] == 0.0  # income_tax_rate = 0.0
        assert result["venit_net"] == 65000.0

    # Coverage for calculator_pfa.py
    def test_pfa_calculate_normal_case(self):
        """Cover normal PFA calculation"""
        calc = PFACalculator(120000, 2024)
        result = calc.calculate()
        assert result["cas"] == 19800.0
        assert result["cass"] == 7920.0
        assert result["impozit"] == 9228.0
        assert result["venit_net"] == 83052.0

    def test_pfa_calculate_zero_income(self):
        """Cover PFA calculation with zero income"""
        calc = PFACalculator(0, 2024)
        result = calc.calculate()
        assert result["cas"] == 0.0
        assert result["cass"] == 0.0
        assert result["impozit"] == 0.0
        assert result["venit_net"] == 0.0

    def test_pfa_get_cas_base_below_lower_threshold(self):
        """Cover CAS base calculation below lower threshold"""
        calc = PFACalculator(30000, 2024)  # Below 12*3300=39600
        result = calc.calculate()
        assert result["cas"] == 0.0

    def test_pfa_get_cas_base_between_thresholds(self):
        """Cover CAS base calculation between lower and upper threshold"""
        calc = PFACalculator(60000, 2024)  # Between 39600 and 79200
        result = calc.calculate()
        expected_cas = 12 * 3300 * 0.25  # lower_base_multiplier * min_wage * cas_rate
        assert result["cas"] == expected_cas

    def test_pfa_get_cas_base_above_upper_threshold(self):
        """Cover CAS base calculation above upper threshold"""
        calc = PFACalculator(150000, 2024)  # Above 24*3300=79200
        result = calc.calculate()
        expected_cas = 24 * 3300 * 0.25  # upper_base_multiplier * min_wage * cas_rate
        assert result["cas"] == expected_cas

    def test_pfa_get_cass_base_bracket_1(self):
        """Cover CASS bracket 1 (below 6*3300=19800)"""
        calc = PFACalculator(10000, 2024)
        result = calc.calculate()
        assert result["cass"] == 0.0  # base_multiplier = 0

    def test_pfa_get_cass_base_bracket_2(self):
        """Cover CASS bracket 2 (6*3300 to 12*3300)"""
        calc = PFACalculator(30000, 2024)  # Between 19800 and 39600
        result = calc.calculate()
        expected_cass = 6 * 3300 * 0.1  # base_multiplier * min_wage * cass_rate
        assert result["cass"] == expected_cass

    def test_pfa_get_cass_base_bracket_3(self):
        """Cover CASS bracket 3 (12*3300 to 24*3300)"""
        calc = PFACalculator(50000, 2024)  # Between 39600 and 79200
        result = calc.calculate()
        expected_cass = 12 * 3300 * 0.1
        assert result["cass"] == expected_cass

    def test_pfa_get_cass_base_bracket_4(self):
        """Cover CASS bracket 4 (24*3300 to 60*3300)"""
        calc = PFACalculator(100000, 2024)  # Between 79200 and 198000
        result = calc.calculate()
        expected_cass = 24 * 3300 * 0.1
        assert result["cass"] == expected_cass

    def test_pfa_get_cass_base_bracket_5(self):
        """Cover CASS bracket 5 (above 60*3300)"""
        calc = PFACalculator(250000, 2024)  # Above 198000
        result = calc.calculate()
        expected_cass = 60 * 3300 * 0.1
        assert result["cass"] == expected_cass

    # Coverage for tax_config.py
    def test_load_rules_from_json(self):
        """Cover JSON loading"""
        rules = _load_rules_from_json()
        assert isinstance(rules, dict)
        assert 2024 in rules

    def test_get_available_years(self):
        """Cover getting available years"""
        years = get_available_years()
        assert isinstance(years, list)
        assert len(years) > 0
        assert years == sorted(years)

    def test_get_rules_for_year_exact_match(self):
        """Cover exact year match"""
        rules = get_rules_for_year(2024)
        assert rules["minimum_wage"] == 3300.0

    def test_get_rules_for_year_future_year(self):
        """Cover future year fallback"""
        rules = get_rules_for_year(2030)  # Future year
        # Should return 2025 rules (latest)
        assert rules["minimum_wage"] == 3700.0

    def test_get_rules_for_year_early_year_error(self):
        """Cover early year error"""
        with pytest.raises(ValueError, match="Minimum configured year"):
            get_rules_for_year(2020)

    # Additional coverage for edge cases
    def test_pfa_with_expense_ratio(self):
        """Cover PFA with expense ratio (if configured)"""
        # Currently expense_ratio is 0.0, but test the path
        calc = PFACalculator(100000, 2024)
        result = calc.calculate()
        assert result["cheltuieli"] == 0.0  # expense_ratio = 0.0

    def test_calculations_with_different_years(self):
        """Cover calculations with different configured years"""
        for year in [2023, 2024, 2025]:
            salariat = SalariatCalculator(100000, year).calculate()
            pfa = PFACalculator(100000, year).calculate()
            assert "venit_net" in salariat
            assert "venit_net" in pfa