from typing import Dict

from calculator_base import TaxCalculator


class SalariatCalculator(TaxCalculator):
    def calculate(self) -> Dict[str, float]:
        # Rates are loaded from yearly config via TaxCalculator base class.
        rules = self.rules["salariat"]
        cas = self.venit_brut * rules["cas_rate"]
        cass = self.venit_brut * rules["cass_rate"]
        # Income tax for salary is applied after social contributions.
        baza_impozabila = max(self.venit_brut - cas - cass, 0.0)
        impozit = baza_impozabila * rules["income_tax_rate"]
        total_taxe = cas + cass + impozit
        venit_net = self.venit_brut - total_taxe

        return {
            "venit_brut": round(self.venit_brut, 2),
            "cas": round(cas, 2),
            "cass": round(cass, 2),
            "impozit": round(impozit, 2),
            "total_taxe": round(total_taxe, 2),
            "venit_net": round(venit_net, 2),
        }
