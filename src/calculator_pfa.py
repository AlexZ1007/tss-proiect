from typing import Dict, Optional

from calculator_base import TaxCalculator


class PFACalculator(TaxCalculator):
    def _get_cas_base(self, venit_net_impozabil: float) -> float:
        # CAS base changes with thresholds expressed in minimum wages.
        cas_rules = self.rules["pfa"]["cas_thresholds"]
        lower_threshold = cas_rules["lower_multiplier"] * self.minimum_wage
        upper_threshold = cas_rules["upper_multiplier"] * self.minimum_wage

        if venit_net_impozabil < lower_threshold:
            return 0.0
        if venit_net_impozabil < upper_threshold:
            return cas_rules["lower_base_multiplier"] * self.minimum_wage
        return cas_rules["upper_base_multiplier"] * self.minimum_wage

    def _get_cass_base(self, venit_net_impozabil: float) -> float:
        # CASS uses progressive brackets configured per fiscal year.
        brackets = self.rules["pfa"]["cass_brackets"]
        for bracket in brackets:
            upper: Optional[float] = bracket["max_income_multiplier"]
            if upper is None or venit_net_impozabil <= upper * self.minimum_wage:
                return bracket["base_multiplier"] * self.minimum_wage
        return 0.0

    def calculate(self) -> Dict[str, float]:
        pfa_rules = self.rules["pfa"]
        expense_ratio = pfa_rules.get("expense_ratio", 0.0)

        cheltuieli = self.venit_brut * expense_ratio
        # Current model uses a configurable flat expense ratio.
        venit_net_impozabil = max(self.venit_brut - cheltuieli, 0.0)

        cas_base = self._get_cas_base(venit_net_impozabil)
        cas = cas_base * pfa_rules["cas_rate"]

        cass_base = self._get_cass_base(venit_net_impozabil)
        cass = cass_base * pfa_rules["cass_rate"]

        baza_impozit = max(venit_net_impozabil - cas - cass, 0.0)
        # If a future year sets income_tax_rate to 0.0, tax is effectively removed.
        impozit = baza_impozit * pfa_rules["income_tax_rate"]

        total_taxe = cas + cass + impozit
        venit_net = self.venit_brut - total_taxe

        return {
            "venit_brut": round(self.venit_brut, 2),
            "cheltuieli": round(cheltuieli, 2),
            "venit_net_impozabil": round(venit_net_impozabil, 2),
            "cas": round(cas, 2),
            "cass": round(cass, 2),
            "impozit": round(impozit, 2),
            "total_taxe": round(total_taxe, 2),
            "venit_net": round(venit_net, 2),
        }
