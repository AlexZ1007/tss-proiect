from abc import ABC, abstractmethod
from typing import Any, Dict

from tax_config import get_rules_for_year


class TaxCalculator(ABC):
    def __init__(self, venit_brut: float, anul_fiscal: int) -> None:
        if venit_brut < 0:
            raise ValueError("Income must be positive.")
        # Shared state used by concrete calculators.
        self.venit_brut = float(venit_brut)
        self.anul_fiscal = int(anul_fiscal)
        self.rules: Dict[str, Any] = get_rules_for_year(self.anul_fiscal)
        self.minimum_wage: float = float(self.rules["minimum_wage"])

    @abstractmethod
    def calculate(self) -> Dict[str, float]:
        """Return a standardized dict with all relevant tax values."""
