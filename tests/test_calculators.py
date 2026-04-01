import sys
from pathlib import Path


# Allow tests to import modules from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator_pfa import PFACalculator
from calculator_salariat import SalariatCalculator


def test_basic_calculations_for_2024() -> None:
    salariat = SalariatCalculator(100000, 2024).calculate()
    assert salariat["cas"] == 25000.0
    assert salariat["cass"] == 10000.0
    assert salariat["impozit"] == 6500.0
    assert salariat["venit_net"] == 58500.0

    pfa = PFACalculator(120000, 2024).calculate()
    assert pfa["cas"] == 19800.0
    assert pfa["cass"] == 7920.0
    assert pfa["impozit"] == 9228.0
    assert pfa["venit_net"] == 83052.0
