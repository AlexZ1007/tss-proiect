import pytest
import sys
from pathlib import Path

# Allow tests to import modules from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator_pfa import PFACalculator
from calculator_salariat import SalariatCalculator
from tax_config import get_available_years


class TestEquivalencePartitioning:
    """
    Test suite using equivalence class partitioning for tax calculators.
    We divide inputs into valid and invalid partitions and test representatives.
    """

    # Equivalence classes for venit_brut (gross income)
    # Invalid: negative values
    # Valid: zero (edge case), positive values (further partitioned by size)

    # Equivalence classes for anul_fiscal (fiscal year)
    # Invalid: non-integer, integer < min available year
    # Valid: exact available years, future years (fallback to latest)

    def test_venit_brut_invalid_negative(self):
        """Test invalid equivalence class: negative venit_brut"""
        with pytest.raises(ValueError, match="Income must be positive"):
            SalariatCalculator(-1000, 2024)
        with pytest.raises(ValueError, match="Income must be positive"):
            PFACalculator(-50000, 2024)

    def test_venit_brut_valid_zero(self):
        """Test valid equivalence class: zero venit_brut (edge case)"""
        salariat = SalariatCalculator(0, 2024).calculate()
        assert salariat["venit_net"] == 0.0
        assert salariat["total_taxe"] == 0.0

        pfa = PFACalculator(0, 2024).calculate()
        assert pfa["venit_net"] == 0.0
        assert pfa["total_taxe"] == 0.0

    def test_venit_brut_valid_small_positive(self):
        """Test valid equivalence class: small positive venit_brut"""
        # Small income, below minimum wage thresholds
        venit = 10000  # Less than 12 * 3300 = 39600 for 2024
        salariat = SalariatCalculator(venit, 2024).calculate()
        assert salariat["venit_net"] > 0
        assert salariat["total_taxe"] > 0

        pfa = PFACalculator(venit, 2024).calculate()
        assert pfa["venit_net"] > 0
        assert pfa["total_taxe"] >= 0  # Might be 0 for low income

    def test_venit_brut_valid_large_positive(self):
        """Test valid equivalence class: large positive venit_brut"""
        # Large income, above all thresholds
        venit = 500000  # Much larger than 60 * 3300 = 198000
        salariat = SalariatCalculator(venit, 2024).calculate()
        assert salariat["venit_net"] > 0
        assert salariat["total_taxe"] > 0

        pfa = PFACalculator(venit, 2024).calculate()
        assert pfa["venit_net"] > 0
        assert pfa["total_taxe"] > 0

    def test_anul_fiscal_invalid_non_integer(self):
        """Test invalid equivalence class: non-integer anul_fiscal that cannot be converted"""
        with pytest.raises(ValueError):
            SalariatCalculator(100000, "invalid_year")
        with pytest.raises(ValueError):
            PFACalculator(100000, "2024abc")

    def test_anul_fiscal_invalid_too_early(self):
        """Test invalid equivalence class: year before minimum available"""
        min_year = min(get_available_years())
        with pytest.raises(ValueError, match=f"Minimum configured year is {min_year}"):
            SalariatCalculator(100000, min_year - 1)
        with pytest.raises(ValueError, match=f"Minimum configured year is {min_year}"):
            PFACalculator(100000, min_year - 1)

    def test_anul_fiscal_valid_exact_years(self):
        """Test valid equivalence class: exact available years"""
        for year in get_available_years():
            salariat = SalariatCalculator(100000, year).calculate()
            assert "venit_net" in salariat

            pfa = PFACalculator(100000, year).calculate()
            assert "venit_net" in pfa

    def test_anul_fiscal_valid_future_year(self):
        """Test valid equivalence class: future year (fallback to latest)"""
        max_year = max(get_available_years())
        future_year = max_year + 5  # e.g., 2030

        salariat = SalariatCalculator(100000, future_year).calculate()
        assert "venit_net" in salariat

        pfa = PFACalculator(100000, future_year).calculate()
        assert "venit_net" in pfa

    # Additional equivalence classes for PFA-specific thresholds
    def test_pfa_income_thresholds_low(self):
        """Test PFA equivalence class: income below lower CAS threshold"""
        # For 2024: lower_threshold = 12 * 3300 = 39600
        venit = 30000  # Below 39600
        pfa = PFACalculator(venit, 2024).calculate()
        assert pfa["cas"] == 0.0  # No CAS for low income

    def test_pfa_income_thresholds_medium(self):
        """Test PFA equivalence class: income between lower and upper CAS threshold"""
        # Between 12*3300=39600 and 24*3300=79200
        venit = 60000
        pfa = PFACalculator(venit, 2024).calculate()
        expected_cas_base = 12 * 3300  # lower_base_multiplier * minimum_wage
        expected_cas = expected_cas_base * 0.25  # cas_rate
        assert pfa["cas"] == expected_cas

    def test_pfa_income_thresholds_high(self):
        """Test PFA equivalence class: income above upper CAS threshold"""
        # Above 24*3300=79200
        venit = 150000
        pfa = PFACalculator(venit, 2024).calculate()
        expected_cas_base = 24 * 3300  # upper_base_multiplier * minimum_wage
        expected_cas = expected_cas_base * 0.25
        assert pfa["cas"] == expected_cas

    def test_pfa_cass_brackets(self):
        """Test PFA equivalence class: different CASS brackets"""
        # Test different brackets based on income levels
        test_cases = [
            (10000, 0),      # Below 6*3300=19800 -> base_multiplier=0
            (30000, 6*3300), # Between 6 and 12 -> 6*3300
            (50000, 12*3300), # Between 12 and 24 -> 12*3300
            (100000, 24*3300), # Between 24 and 60 -> 24*3300
            (300000, 60*3300), # Above 60 -> 60*3300
        ]

        for venit, expected_base in test_cases:
            pfa = PFACalculator(venit, 2024).calculate()
            expected_cass = expected_base * 0.1  # cass_rate
            assert pfa["cass"] == expected_cass