import pytest
import sys
from pathlib import Path

# Allow tests to import modules from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator_pfa import PFACalculator
from calculator_salariat import SalariatCalculator
from tax_config import get_rules_for_year, get_available_years


class TestDecisionCoverage:
    """
    Test suite designed for decision coverage (branch coverage).
    Ensures that every branch of every decision point is executed at least once.
    """

    # Branches in TaxCalculator (calculator_base.py)

    def test_tax_calculator_income_validation(self):
        """
        Covers branches of 'if venit_brut < 0:' in TaxCalculator.__init__
        """
        # Branch True: venit_brut < 0
        with pytest.raises(ValueError, match="Income must be positive."):
            SalariatCalculator(-1, 2024)
        
        # Branch False: venit_brut >= 0
        calc = SalariatCalculator(0, 2024)
        assert calc.venit_brut == 0.0

    # Branches in PFACalculator._get_cas_base (calculator_pfa.py)

    def test_pfa_cas_base_branches(self):
        """
        Covers branches in _get_cas_base:
        1. venit_net_impozabil < lower_threshold
        2. venit_net_impozabil >= lower_threshold AND < upper_threshold
        3. venit_net_impozabil >= upper_threshold
        """
        min_wage = get_rules_for_year(2024)["minimum_wage"] # 3300
        
        # Branch 1: < 12 * 3300 (39600)
        calc1 = PFACalculator(10000, 2024)
        assert calc1._get_cas_base(10000) == 0.0
        
        # Branch 2: >= 39600 AND < 24 * 3300 (79200)
        calc2 = PFACalculator(50000, 2024)
        assert calc2._get_cas_base(50000) == 12 * min_wage
        
        # Branch 3: >= 79200
        calc3 = PFACalculator(100000, 2024)
        assert calc3._get_cas_base(100000) == 24 * min_wage

    # Branches in PFACalculator._get_cass_base (calculator_pfa.py)

    def test_pfa_cass_base_branches(self):
        """
        Covers branches in _get_cass_base loop and 'if upper is None or ...'
        """
        min_wage = get_rules_for_year(2024)["minimum_wage"] # 3300
        
        # Bracket 1: <= 6 * 3300 (19800)
        assert PFACalculator(0, 2024)._get_cass_base(10000) == 0 * min_wage
        
        # Bracket 2: <= 12 * 3300 (39600)
        assert PFACalculator(0, 2024)._get_cass_base(30000) == 6 * min_wage
        
        # Bracket 3: <= 24 * 3300 (79200)
        assert PFACalculator(0, 2024)._get_cass_base(50000) == 12 * min_wage
        
        # Bracket 4: <= 60 * 3300 (198000)
        assert PFACalculator(0, 2024)._get_cass_base(100000) == 24 * min_wage
        
        # Bracket 5: > 60 * 3300 (upper is None)
        assert PFACalculator(0, 2024)._get_cass_base(300000) == 60 * min_wage

    # Branches in get_rules_for_year (tax_config.py)

    def test_get_rules_for_year_branches(self):
        """
        Covers branches in get_rules_for_year:
        1. fiscal_year in YEARLY_TAX_RULES
        2. fiscal_year not in YEARLY_TAX_RULES AND previous_or_equal exists
        3. fiscal_year not in YEARLY_TAX_RULES AND no previous_or_equal
        """
        available_years = get_available_years()
        min_year = min(available_years)
        max_year = max(available_years)
        
        # Branch 1: Exact match
        rules = get_rules_for_year(max_year)
        assert rules["minimum_wage"] > 0
        
        # Branch 2: Fallback to latest
        rules_fallback = get_rules_for_year(max_year + 1)
        assert rules_fallback == rules
        
        # Branch 3: No previous year (too early)
        with pytest.raises(ValueError, match="Minimum configured year is"):
            get_rules_for_year(min_year - 1)

    # Branches for max(..., 0.0) in calculate methods 

    def test_calculate_max_zero_branches(self):
        """
        Ensures the max(..., 0.0) logic is exercised.
        """
        # PFA: venit_net_impozabil = max(self.venit_brut - cheltuieli, 0.0)
        # Note: with current expense_ratio=0.0, this is always >= 0 if venit_brut >= 0
        # But we can still call it with 0
        pfa_result = PFACalculator(0, 2024).calculate()
        assert pfa_result["venit_net_impozabil"] == 0.0
        
        # Salariat: baza_impozabila = max(self.venit_brut - cas - cass, 0.0)
        # Since cas_rate + cass_rate = 0.25 + 0.1 = 0.35, this is always positive for venit_brut > 0
        # But we can call it with 0
        salariat_result = SalariatCalculator(0, 2024).calculate()
        assert salariat_result["impozit"] == 0.0
