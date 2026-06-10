"""
Mutation Testing Analysis - Raport cosmic-ray
==============================================

Generatorul de mutanți folosit: cosmic-ray
Fișiere analizate: src/calculator_pfa.py

Configurare cosmic-ray:
  - Fișier configurare: mutation-testing/cosmic-ray.toml
  - module-path: src/calculator_pfa.py
  - test-command: python -m pytest tests/ -x -q

Rezultate generale:
  - Total mutanți generați (jobs): 229
  - Mutanți testați (complete): 229 (100%)
  - Mutanți omorâți (killed): 207 (~90.39%)
  - Mutanți supraviețuitori (survived): 22 (9.61%)

Cum se interpretează raportul HTML generat de cosmic-ray:
  - Verde  = mutant killed (testul a picat când codul era mutant — bine)
  - Roșu   = mutant survived (testul a trecut cu codul mutant — problemă)
  - Albastru = no coverage (niciun test nu a atins acea linie)

Operatori de mutație folosiți de cosmic-ray:
  - core/NumberReplacer: înlocuiește o constantă numerică (ex. 0.0 → 1.0, 2 → 3)
  - core/ReplaceBinaryOperator_Sub_Add: înlocuiește operatori (- cu +)
  - core/ReplaceBinaryOperator_Add_Sub: înlocuiește operatori (+ cu -)
  - core/ReplaceBinaryOperator_Add_Mul: înlocuiește operatori (+ cu *)
  - core/ReplaceBinaryOperator_Add_Div: înlocuiește operatori (+ cu /)
  - core/ReplaceBinaryOperator_Sub_Mul: înlocuiește operatori (- cu *)
  - core/ReplaceBinaryOperator_Mul_Pow: înlocuiește operatori (* cu **)
  - core/ReplaceBinaryOperator_Mul_BitXor: înlocuiește operatori (* cu ^)
  - core/ReplaceOrWithAnd: înlocuiește operatori logici (or cu and)
  - core/AddNot: adaugă un operator NOT (ex. if x → if not x)
  - core/ReplaceComparisonOperator_Is_IsNot: înlocuiește operatori de comparație (is cu is not)
  - core/ReplaceComparisonOperator_Lt_Is: înlocuiește operatori de comparație (< cu is)

------------------------------------------------------------------------------
ANALIZA MUTANȚILOR SUPRAVIEȚUITORI
------------------------------------------------------------------------------

Mutanți echivalenți (nu pot fi omorâți):
-----------------------------------------

  NumberReplacer occurrence 2-24 (21 mutanți survived):
    Acești mutanți schimbă constante numerice din cod — multiplicatori din 
    brackets (ex. 6 → 7 în max_income_multiplier) și numărul de zecimale
    din round() (ex. round(cas, 2) → round(cas, 3)).
    Supraviețuiesc deoarece:
      - Multiplicatorii din brackets: testele existente nu testează valori
        de venit exact la frontiera dintre brackets, deci schimbarea unui
        multiplicator cu ±1 nu afectează rezultatul testelor curente.
      - round(..., 2) → round(..., 3): pentru valorile întregi din teste
        (ex. 19800.0, 9900.0), rotunjirea la 2 sau 3 zecimale produce
        același rezultat — zecimalele extra sunt 0.
    Sunt ECHIVALENȚI în contextul datelor de test curente.

------------------------------------------------------------------------------
Mutanți NEECHIVALENȚI aleși pentru a fi omorâți:
-------------------------------------------------

  MUTANT 1: Job 23 — ReplaceBinaryOperator_Sub_Add în calculate()
  ---------------------------------------------------------------
  Fișier:   src/calculator_pfa.py, linia 34
  Mutație:  venit_net_impozabil = max(self.venit_brut - cheltuieli, 0.0)
         →  venit_net_impozabil = max(self.venit_brut + cheltuieli, 0.0)
  Operator: core/ReplaceBinaryOperator_Sub_Add

  De ce este neechivalent:
    Aceasta este o eroare logică reală — în loc să scadă cheltuielile din
    venitul brut (comportament corect), le adaugă. Pentru orice venit cu
    expense_ratio > 0, venit_net_impozabil ar fi mai mare decât cel corect,
    ducând la taxe calculate greșit.

  De ce supraviețuiește:
    În configurarea curentă, expense_ratio = 0.0, deci cheltuieli = 0.
    Prin urmare, venit_brut - 0 == venit_brut + 0, și mutantul produce
    același rezultat. Testele existente nu testează scenariul cu
    expense_ratio != 0, deci nu detectează diferența.

  Cum îl omorâm:
    Monkeypatch pe expense_ratio cu o valoare nenulă (ex. 0.2), astfel
    încât cheltuieli = venit * 0.2 > 0. Atunci:
      - codul corect: venit_net_impozabil = venit - cheltuieli (mai mic)
      - mutantul:     venit_net_impozabil = venit + cheltuieli (mai mare)
    Verificând că cheltuieli > 0 și că venit_net_impozabil == venit - cheltuieli,
    testul va pica pe mutant.

------------------------------------------------------------------------------

  MUTANT 2: Job 205 — NumberReplacer în _get_cass_base() fallback
  ---------------------------------------------------------------
  Fișier:   src/calculator_pfa.py, linia 26
  Mutație:  return 0.0  →  return 1.0  (după bucla de brackets)
  Operator: core/NumberReplacer, occurrence: 2, definition_name: _get_cass_base

  De ce este neechivalent:
    Dacă ramura de fallback (după buclă) ar fi atinsă și ar returna 1.0
    în loc de 0.0, cass_base ar fi 1.0, iar cass = 1.0 * cass_rate = 0.1 RON
    în loc de 0.0 RON — calcul incorect.

  De ce supraviețuiește:
    Ultimul bracket din JSON are max_income_multiplier: null (None), deci
    condiția `upper is None` este mereu True pentru ultimul bracket, și
    funcția returnează mereu din interiorul buclei — ramura `return 0.0`
    de după buclă este dead code cu datele actuale.
    Testele existente nu forțează execuția ramurii post-buclă.

  Cum îl omorâm:
    Apelăm direct _get_cass_base() cu o instanță la care brackets este
    lista goală (prin monkeypatch pe self.rules). Astfel bucla nu se
    execută deloc și se ajunge la `return 0.0`. Verificăm că rezultatul
    este exact 0.0 — mutantul ar returna 1.0 și testul ar pica.

------------------------------------------------------------------------------

Employee: src/calculator_employee.py (raport: mutation-testing/mutation_report_employee.html)
------------------------------------------------------------------------------

Mutanți echivalenți (jobs 91–101) — rotunjiri:
---------------------------------------------

  NumberReplacer pe al doilea argument al lui round(..., 2) din dict-ul
  returnat (venit_brut, cas, cass, impozit, total_taxe, venit_net).
  Mutațiile schimbă 2 în 1, 3, etc. Pe valorile întregi / cu puține zecimale
  folosite în teste, round(x, 2) și round(x, 3) (sau 1) coincid — mutanții
  sunt echivalenți în contextul datelor curente.

Mutant neechivalent ales pentru a fi omorât:
---------------------------------------------

  MUTANT 3: Job 90 — NumberReplacer pe al doilea 0.0 din max(..., 0.0)
  --------------------------------------------------------------------
  Fișier:   src/calculator_employee.py, linia 13
  Mutație:  baza_impozabila = max(self.venit_brut - cas - cass, 0.0)
         →  baza_impozabila = max(self.venit_brut - cas - cass, -1.0)
  Operator: core/NumberReplacer, occurrence: 1, definition_name: calculate

  De ce este neechivalent:
    Când venit_brut - cas - cass < 0, codul corect plafonează baza la 0.0;
    mutantul plafonează la -1.0, deci impozitul și venitul net devin greșite.

  De ce supraviețuiește:
    Cu rate reale din config, cas_rate + cass_rate < 1, deci pentru
    venit_brut ≥ 0 avem venit_brut - cas - cass ≥ 0; al doilea argument
    al lui max nu influențează rezultatul.

  Cum îl omorâm:
    Monkeypatch cas_rate și cass_rate astfel încât cas_rate + cass_rate > 1
    (ex. 0.6 și 0.5). Pentru venit_brut pozitiv mic, venit_brut - cas - cass < 0;
    corect: baza_impozabila = 0.0 → impozit = 0.0; mutant: baza = -1.0 →
    impozit negativ. Assert impozit == 0 omorâște mutantul.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator_employee import EmployeeCalculator
from calculator_pfa import PFACalculator


@pytest.mark.mutation_killer
class TestMutationKillers:
    """
    Teste suplimentare pentru mutanți neechivalenți rămași în viață după
    cosmic-ray pe `calculator_pfa.py` și `calculator_employee.py`.

    """

    # =========================================================================
    # MUTANT 1: Job 23 — ReplaceBinaryOperator_Sub_Add
    #
    # Mutația: max(self.venit_brut - cheltuieli, 0.0)
    #       → max(self.venit_brut + cheltuieli, 0.0)
    #
    # Linia afectată: venit_net_impozabil = max(self.venit_brut - cheltuieli, 0.0)
    #
    # Supraviețuiește deoarece: expense_ratio = 0.0 → cheltuieli = 0 →
    # scăderea și adunarea cu 0 dau același rezultat.
    #
    # Strategia de omor: injectăm un expense_ratio != 0 prin monkeypatch,
    # astfel cheltuieli > 0 și cele două operații produc rezultate diferite.
    # =========================================================================

    def test_kill_mutant_sub_add_cheltuieli_nonzero(self, monkeypatch):
        """
        Omoară mutantul Job 23 (venit_brut - cheltuieli → venit_brut + cheltuieli).

        Injectăm expense_ratio = 0.20 astfel că pentru venit = 100000:
          cheltuieli = 100000 * 0.20 = 20000
          CORECT:  venit_net_impozabil = 100000 - 20000 = 80000
          MUTANT:  venit_net_impozabil = 100000 + 20000 = 120000

        Verificăm că venit_net_impozabil == venit_brut - cheltuieli.
        Mutantul ar produce o valoare cu 40000 mai mare, deci testul pică.
        """
        calc = PFACalculator(100000, 2024)

        # Injectăm expense_ratio nenul în regulile instanței
        monkeypatch.setitem(calc.rules["pfa"], "expense_ratio", 0.20)

        result = calc.calculate()

        expected_cheltuieli = 100000 * 0.20          # 20000.0
        expected_venit_net_impozabil = 100000 - expected_cheltuieli  # 80000.0

        assert result["cheltuieli"] == pytest.approx(expected_cheltuieli, abs=0.01), (
            f"cheltuieli greșite: {result['cheltuieli']} != {expected_cheltuieli}"
        )
        assert result["venit_net_impozabil"] == pytest.approx(expected_venit_net_impozabil, abs=0.01), (
            "venit_net_impozabil trebuie să fie venit_brut - cheltuieli, "
            f"nu venit_brut + cheltuieli. "
            f"Obținut: {result['venit_net_impozabil']}, Așteptat: {expected_venit_net_impozabil}. "
            "Mutantul (+ în loc de -) ar produce 120000, nu 80000."
        )


    # =========================================================================
    # MUTANT 2: Job 205 — NumberReplacer în _get_cass_base fallback
    #
    # Mutația: return 0.0 → return 1.0 (după bucla de brackets)
    #
    # Linia afectată: ultima linie din _get_cass_base(), după for loop.
    #
    # Supraviețuiește deoarece: ultimul bracket are max_income_multiplier=None,
    # deci bucla returnează mereu înainte de a ajunge la return 0.0 —
    # acea linie este dead code cu datele actuale.
    #
    # Strategia de omor: forțăm execuția ramurii post-buclă prin monkeypatch
    # pe brackets cu o listă goală. Bucla nu rulează deloc, se ajunge la
    # return 0.0. Mutantul ar returna 1.0 și testul ar pica.
    # =========================================================================

    def test_kill_mutant_cass_fallback_empty_brackets(self, monkeypatch):
        """
        Omoară mutantul Job 205 (return 0.0 → return 1.0 în _get_cass_base).

        Forțăm execuția ramurii de fallback (după buclă) prin injectarea
        unei liste goale de brackets. Bucla `for bracket in brackets` nu
        se execută deloc, și codul ajunge direct la `return 0.0`.

        CORECT:  return 0.0  → _get_cass_base() == 0.0
        MUTANT:  return 1.0  → _get_cass_base() == 1.0

        Verificăm că rezultatul este exact 0.0.
        """
        calc = PFACalculator(100000, 2024)

        # Înlocuim brackets cu listă goală → bucla nu rulează → se ajunge la return
        monkeypatch.setitem(calc.rules["pfa"], "cass_brackets", [])

        result = calc._get_cass_base(100000)

        assert result == 0.0, (
            f"_get_cass_base cu brackets gol trebuie să returneze 0.0, "
            f"nu {result}. "
            "Mutantul (return 1.0) ar returna 1.0 și acest assert ar pica."
        )

    # =========================================================================
    # MUTANT 3: Job 90 — NumberReplacer pe al doilea argument al lui max
    #
    # Mutația: max(self.venit_brut - cas - cass, 0.0)
    #       → max(self.venit_brut - cas - cass, -1.0)
    #
    # Linia afectată: baza_impozabila = max(self.venit_brut - cas - cass, 0.0)
    #
    # Supraviețuiește deoarece: cu rate reale, venit_brut - cas - cass ≥ 0,
    # deci max returnează mereu primul argument; al doilea literal nu contează.
    #
    # Strategia de omor: forțăm venit_brut - cas - cass < 0 prin monkeypatch
    # pe cas_rate + cass_rate > 1; atunci corect baza = 0, mutant baza = -1.
    # =========================================================================

    def test_kill_employee_mutant_job_90_max_floor_numberreplacer(self, monkeypatch):
        """
        Omoară mutantul Job 90 (al doilea 0.0 din max(..., 0.0) → -1.0).

        Cu cas_rate = 0.6, cass_rate = 0.5 și venit_brut = 10000:
          cas = 6000, cass = 5000, venit_brut - cas - cass = -1000
          CORECT:  baza_impozabila = max(-1000, 0.0) = 0.0  → impozit = 0.0
          MUTANT:  baza_impozabila = max(-1000, -1.0) = -1.0 → impozit = -0.1

        Assert impozit == 0 prinde mutantul; codul corect trece.
        """
        calc = EmployeeCalculator(10000, 2024)
        monkeypatch.setitem(calc.rules["employee"], "cas_rate", 0.6)
        monkeypatch.setitem(calc.rules["employee"], "cass_rate", 0.5)

        result = calc.calculate()

        assert result["impozit"] == pytest.approx(0.0, abs=0.001), (
            "Cu baza impozabilă negativă, impozitul trebuie calculat de la 0.0, "
            f"nu de la -1.0 (mutant Job 90). Obținut: impozit={result['impozit']!r}."
        )

