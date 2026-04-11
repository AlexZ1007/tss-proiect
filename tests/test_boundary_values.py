import pytest
import sys
from pathlib import Path

# Allow tests to import modules from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator_pfa import PFACalculator
from calculator_salariat import SalariatCalculator
from tax_config import get_available_years


class TestBoundaryValueAnalysis:
    """
    Test suite using boundary value analysis for tax calculators.
    We test values at the boundaries of equivalence classes.
    """

    def test_venit_brut_boundary_negative(self):
        """Boundary: just below zero (invalid)"""
        with pytest.raises(ValueError):
            SalariatCalculator(-0.01, 2024)
        with pytest.raises(ValueError):
            PFACalculator(-0.01, 2024)

    def test_venit_brut_boundary_zero(self):
        """Boundary: exactly zero"""
        salariat = SalariatCalculator(0, 2024).calculate()
        assert salariat["venit_net"] == 0.0

        pfa = PFACalculator(0, 2024).calculate()
        assert pfa["venit_net"] == 0.0

    def test_venit_brut_boundary_just_above_zero(self):
        """Boundary: just above zero"""
        salariat = SalariatCalculator(0.01, 2024).calculate()
        assert salariat["venit_net"] > 0

        pfa = PFACalculator(0.01, 2024).calculate()
        assert pfa["venit_net"] > 0

    def test_anul_fiscal_boundary_min_year_minus_one(self):
        """Boundary: year just below minimum available"""
        min_year = min(get_available_years())
        with pytest.raises(ValueError):
            SalariatCalculator(100000, min_year - 1)
        with pytest.raises(ValueError):
            PFACalculator(100000, min_year - 1)

    def test_anul_fiscal_boundary_min_year(self):
        """Boundary: minimum available year"""
        min_year = min(get_available_years())
        salariat = SalariatCalculator(100000, min_year).calculate()
        assert "venit_net" in salariat

        pfa = PFACalculator(100000, min_year).calculate()
        assert "venit_net" in pfa

    def test_anul_fiscal_boundary_min_year_plus_one(self):
        """Boundary: year just above minimum available"""
        min_year = min(get_available_years())
        salariat = SalariatCalculator(100000, min_year + 1).calculate()
        assert "venit_net" in salariat

        pfa = PFACalculator(100000, min_year + 1).calculate()
        assert "venit_net" in pfa

    def test_anul_fiscal_boundary_max_year_minus_one(self):
        """Boundary: year just below maximum available"""
        max_year = max(get_available_years())
        salariat = SalariatCalculator(100000, max_year - 1).calculate()
        assert "venit_net" in salariat

        pfa = PFACalculator(100000, max_year - 1).calculate()
        assert "venit_net" in pfa

    def test_anul_fiscal_boundary_max_year(self):
        """Boundary: maximum available year"""
        max_year = max(get_available_years())
        salariat = SalariatCalculator(100000, max_year).calculate()
        assert "venit_net" in salariat

        pfa = PFACalculator(100000, max_year).calculate()
        assert "venit_net" in pfa

    def test_anul_fiscal_boundary_max_year_plus_one(self):
        """Boundary: year just above maximum available (fallback)"""
        max_year = max(get_available_years())
        salariat = SalariatCalculator(100000, max_year + 1).calculate()
        assert "venit_net" in salariat

        pfa = PFACalculator(100000, max_year + 1).calculate()
        assert "venit_net" in pfa

    # PFA-specific boundaries for CAS thresholds (2024)
    def test_pfa_cas_boundary_lower_threshold_minus_one(self):
        """Boundary: just below lower CAS threshold"""
        threshold = 12 * 3300  # 39600
        venit = threshold - 1
        pfa = PFACalculator(venit, 2024).calculate()
        assert pfa["cas"] == 0.0  # Below threshold, no CAS

    def test_pfa_cas_boundary_lower_threshold(self):
        """Boundary: exactly at lower CAS threshold"""
        threshold = 12 * 3300  # 39600
        venit = threshold
        pfa = PFACalculator(venit, 2024).calculate()
        expected_cas = 12 * 3300 * 0.25  # lower_base_multiplier * minimum_wage * cas_rate
        assert pfa["cas"] == expected_cas

    def test_pfa_cas_boundary_lower_threshold_plus_one(self):
        """Boundary: just above lower CAS threshold"""
        threshold = 12 * 3300  # 39600
        venit = threshold + 1
        pfa = PFACalculator(venit, 2024).calculate()
        expected_cas = 12 * 3300 * 0.25
        assert pfa["cas"] == expected_cas

    def test_pfa_cas_boundary_upper_threshold_minus_one(self):
        """Boundary: just below upper CAS threshold"""
        threshold = 24 * 3300  # 79200
        venit = threshold - 1
        pfa = PFACalculator(venit, 2024).calculate()
        expected_cas = 12 * 3300 * 0.25  # Still in lower bracket
        assert pfa["cas"] == expected_cas

    def test_pfa_cas_boundary_upper_threshold(self):
        """Boundary: exactly at upper CAS threshold"""
        threshold = 24 * 3300  # 79200
        venit = threshold
        pfa = PFACalculator(venit, 2024).calculate()
        expected_cas = 24 * 3300 * 0.25  # upper_base_multiplier * minimum_wage * cas_rate
        assert pfa["cas"] == expected_cas

    def test_pfa_cas_boundary_upper_threshold_plus_one(self):
        """Boundary: just above upper CAS threshold"""
        threshold = 24 * 3300  # 79200
        venit = threshold + 1
        pfa = PFACalculator(venit, 2024).calculate()
        expected_cas = 24 * 3300 * 0.25
        assert pfa["cas"] == expected_cas

    # PFA-specific boundaries for CASS brackets (2024)
    def test_pfa_cass_boundary_bracket_transitions(self):
        """Boundary values at CASS bracket transitions"""
        brackets = [
            (6 * 3300 - 1, 0),      # Just below first bracket
            (6 * 3300, 0),          # At first bracket boundary
            (6 * 3300 + 1, 6 * 3300), # Just above first bracket
            (12 * 3300 - 1, 6 * 3300), # Just below second bracket
            (12 * 3300, 6 * 3300), # At second bracket boundary
            (12 * 3300 + 1, 12 * 3300), # Just above second bracket
            (24 * 3300 - 1, 12 * 3300), # Just below third bracket
            (24 * 3300, 12 * 3300), # At third bracket boundary
            (24 * 3300 + 1, 24 * 3300), # Just above third bracket
            (60 * 3300 - 1, 24 * 3300), # Just below fourth bracket
            (60 * 3300, 24 * 3300), # At fourth bracket boundary
            (60 * 3300 + 1, 60 * 3300), # Just above fourth bracket
        ]

        for venit, expected_base in brackets:
            pfa = PFACalculator(venit, 2024).calculate()
            expected_cass = expected_base * 0.1
            assert pfa["cass"] == expected_cass, f"Failed for venit={venit}, expected_cass={expected_cass}"