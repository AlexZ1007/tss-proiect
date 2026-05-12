# TaxVision RO

Theme: T1 - Testare Unitară în Python
Team: Dragomir Miruna, Iștoc Simona, Tanislav Alexia, Zamfir Alexandru

## Table of Contents
- [Purpose of the Application](#purpose-of-the-application)
- [Project Resources](#project-resources)
- [Project Setup](#project-setup)
- [Continuous Integration (CI)](#continuous-integration-ci)
- [Technical Report](#technical-report)
  - [Testing Scope](#testing-scope)
  - [Testing Strategies](#testing-strategies)
  - [Tax Rules Configuration Structure (`src/tax_rules.json`)](#tax-rules-configuration-structure-srctax_rulesjson)
  - [Environment and Execution](#environment-and-execution)
  - [Technologies](#technologies)
    - [Streamlit vs Django](#streamlit-vs-django)
    - [Pytest vs Unittest](#pytest-vs-unittest)
- [Diagrams](#diagrams)
  - [Use case](#use-case-application-flow)
  - [Pipeline](#development-and-testing-pipeline)
- [AI-Assisted Testing Report](#ai-assisted-testing-report)

## Purpose of the Application
TaxVision RO helps users analyze Romanian income tax outcomes through a clear comparison workflow and practical decision support.

Primary objectives:
- Provide a clear history of comparisons so users can track and review previous simulations.
- Export calculation results to Excel and CSV for reporting and further analysis.
- Offer graphical views of results to make differences easier to interpret.

## Project Resources
### Presentation
- Presentation file: `TBD`

### Demo
- Application demo video: `TBD`
- Test execution results: `TBD`

## Project Setup
### Prerequisites
- Python 3.10 or newer
- `pip`
- Optional: a Python virtual environment (`venv`)

### 1) Install dependencies
From the project root:

```bash
pip install -r requirements.txt
```

### 2) Run the application (Streamlit)
From the project root:

```bash
streamlit run src/app.py
```

After startup, Streamlit opens in the browser automatically (or use the URL shown in the terminal).

### 3) Run tests (pytest)
From the project root:

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

### 4) Mutation testing (cosmic-ray)
Mutation testing uses [cosmic-ray](https://cosmic-ray.readthedocs.io/) with the configuration in [`cosmic-ray.toml`](cosmic-ray.toml).

```bash
# Initialize session - Inițializează sesiunea
cosmic-ray init cosmic-ray.toml session.sqlite

# Run mutants (may take a few minutes) - Rulează mutanții (poate dura câteva minute)
cosmic-ray exec cosmic-ray.toml session.sqlite

# View results in the terminal - Vezi rezultatele în terminal
cr-report session.sqlite

# Generate HTML report - Generează raport HTML
# On Windows, force UTF-8 on stdout so characters such as "ă" in captured test output
# do not trigger UnicodeEncodeError when redirecting to a file (cp1252 cannot encode them).
PYTHONIOENCODING=utf-8 cr-html session.sqlite > mutation_report.html
```

The HTML report is written to `mutation_report.html` in the project root. In **cmd.exe**, use `set PYTHONIOENCODING=utf-8 && cr-html session.sqlite > mutation_report.html` instead.

### 5) Tool versions


## Continuous Integration (CI)

When this repository is hosted on GitHub, [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs only on **push to `master`** (for example after a pull request is merged). It does not run on other branches or on pull request events alone.

- **What runs:** `pytest` only (the full test suite under `tests/`).
- **What does not run:** mutation testing (`cosmic-ray`) is **not** executed in CI.
  
## Technical Report

### Testing Scope
The testing scope includes mainly the business-logic layer:
- `calculator_pfa` (derived from `calculator_base`)
- `calculator_employee` (derived from `calculator_base`)
- `run_simulation(venit_brut, anul_fiscal, user_triggered)` - helper function used to run the simulation and update the session state.

Excluded from testing scope:
- Frontend/display concerns
- Streamlit presentation/UI behavior

### Testing Strategies
The implemented testing strategies are covered through dedicated test modules.

#### Basis path
Tests all linearly independent paths through the control flow graph, ensuring every unique execution sequence is covered. Paths were identified by mapping the source code logic into CFGs and ensuring each test case introduces at least one new edge. The core calculation logic (e.g., `_get_cas_base`) has a Cyclomatic Complexity of **V(G) = 3** because it contains 2 decision nodes ($V(G) = P + 1$), requiring exactly 3 independent paths for complete coverage.

- [CFG: CAS Base Calculation](diagrams/cfg_cas_base_test.png)
- [CFG: Tax Config Retrieval](diagrams/cfg_tax_config_base_test.png)
- [CFG: Initialization Validation](diagrams/cfg_init_validation_base_test.png)
- [CFG: Project Basis Path](diagrams/cfg_PFACalculator.png)
#### Boundary value
#### Condition coverage
Validates that each individual condition in compound boolean expressions evaluates to both True and False independently.
#### Decision coverage
Ensures that every branch of every decision point (e.g., if/else blocks) is executed at least once.
#### Equivalence partitioning
#### Statement coverage
#### Mutation testing

**Mutation testing analysis - cosmic-ray report**

Mutant generator: **cosmic-ray**. File under analysis: `src/calculator_pfa.py`.

**Configuration**

- Config file: [`cosmic-ray.toml`](cosmic-ray.toml)
- `module-path`: `src/calculator_pfa.py`
- `test-command`: `python -X utf8 -m pytest tests/ -x -q` (UTF-8 mode avoids Cosmic Ray decoding errors on Windows)

**Overall results**

Before: 
| Metric | Value |
|--------|-------|
| Total mutants generated (jobs) | 229 |
| Mutants executed to completion | 229 (100%) |
| Mutants killed | 207 (~90.39%) |
| Surviving mutants | 22 (~9.61%) |

After:
| Metric | Value |
|--------|-------|
| Total mutants generated (jobs) | 229 |
| Mutants executed to completion | 229 (100%) |
| Mutants killed | 210 (~91.70%) |
| Surviving mutants | 19  (~8.30%) |

**How to read the cosmic-ray HTML report**

- **Green** - mutant killed (tests fail on mutated code - desired).
- **Red** - mutant survived (tests still pass on mutated code - suite weakness).
- **Blue** - no coverage (no test reaches that line).

**Example mutation operators**

- `core/NumberReplacer` - replaces numeric literals (e.g. `0.0` → `1.0`, `2` → `3`).
- `core/ReplaceBinaryOperator_Sub_Add` / `Add_Sub` / `Add_Mul` / `Add_Div` / `Sub_Mul` / `Mul_Pow` / `Mul_BitXor` - replaces arithmetic operators (e.g. `-` with `+`).
- `core/ReplaceOrWithAnd` - `or` → `and`.
- `core/AddNot` - inserts `not` (e.g. `if x` → `if not x`).
- `core/ReplaceComparisonOperator_Is_IsNot`, `ReplaceComparisonOperator_Lt_Is` - replaces comparison operators.

---

**Analysis of surviving mutants**

**Equivalent mutants (relative to current test data)**

*NumberReplacer occurrence 2–24 (19 survived)*

These mutants change numeric constants - bracket multipliers (e.g. `6` → `7` in `max_income_multiplier`) and the number of decimal places in `round()` (e.g. `round(cas, 2)` → `round(cas, 3)`).

They survive because:

- Bracket multipliers: tests do not use incomes exactly on bracket boundaries, so nudging a multiplier by ±1 does not change the observable outcome.
- `round(..., 2)` vs `round(..., 3)`: for the integer-valued amounts used in tests (e.g. `19800.0`, `9900.0`), rounding to two or three decimal places agrees.

**Non-equivalent mutants selected for killing**

1. **Job 23 - `ReplaceBinaryOperator_Sub_Add` in `calculate()`**  
   - **File:** `src/calculator_pfa.py`, line 34.  
   - **Mutation:** `venit_net_impozabil = max(self.venit_brut - cheltuieli, 0.0)` → `venit_net_impozabil = max(self.venit_brut + cheltuieli, 0.0)`.  
   - **Operator:** `core/ReplaceBinaryOperator_Sub_Add`.  
   - **Why it is not equivalent:** expenses are added to gross income instead of subtracted - for `expense_ratio > 0`, net taxable income is too high and tax is wrong.  
   - **Why it survives:** with `expense_ratio = 0.0`, `cheltuieli = 0`, so `venit_brut - 0` and `venit_brut + 0` coincide; tests do not cover `expense_ratio != 0`.  
   - **How to kill it:** monkeypatch `expense_ratio` (e.g. `0.2`) so `cheltuieli > 0`; assert `venit_net_impozabil == venit - cheltuieli` - the mutant fails.

2. **Job 205 - `NumberReplacer` in `_get_cass_base()` (post-loop fallback)**  
   - **File:** `src/calculator_pfa.py`, line 26.  
   - **Mutation:** `return 0.0` → `return 1.0` after the bracket loop.  
   - **Operator:** `core/NumberReplacer` (occurrence 2, `definition_name: _get_cass_base`).  
   - **Why it is not equivalent:** if that fallback ran with `1.0`, the CASS base would be wrong (e.g. non-zero CASS instead of zero).  
   - **Why it survives:** the last JSON bracket has `max_income_multiplier: null`, so `upper is None` is always true for the last bracket and the function returns inside the loop - the post-loop `return 0.0` is dead code with the current data.  
   - **How to kill it:** call `_get_cass_base()` directly with an empty `brackets` list (e.g. monkeypatch `self.rules`); expect exactly `0.0` - the mutant returns `1.0` and the test fails.

### Tax Rules Configuration Structure (`src/tax_rules.json`)
The fiscal configuration file is organized by year and contains all rule parameters needed by the calculation layer.

Structure overview:
- Top-level object keys are fiscal years (for example, `2023`, `2024`, `2025`).
- Each year contains:
  - `minimum_wage` - yearly minimum wage value used as the reference for thresholds and contribution bases.
  - `employee` - tax and contribution rules applied by the Employee calculator flow.
  - `pfa` - tax, thresholds, and bracket rules applied by the PFA calculator flow.

Inside `employee`:
- `cas_rate` - the current-year CAS contribution rate applied to employee gross income.
- `cass_rate` - the current-year CASS contribution rate applied to employee gross income.
- `income_tax_rate` - the current-year income tax rate applied after contribution deductions.

Inside `pfa`:
- `expense_ratio` - the deductible expense ratio used to estimate net taxable income from gross income.
- `cas_rate` - the current-year CAS rate used for PFA social contribution calculation.
- `income_tax_rate` - the current-year income tax rate applied to PFA taxable income.
- `cas_thresholds` - yearly threshold and base-multiplier rules used to determine CAS calculation base.
- `cass_rate` - the current-year CASS rate applied to the CASS base selected from brackets.
- `cass_brackets` - ordered income brackets that select the CASS base multiplier for the current year.

Bracket semantics:
- `max_income_multiplier` defines the upper interval limit as a multiple of minimum wage.
- `base_multiplier` defines the base used for CASS computation in that bracket.
- `max_income_multiplier: null` marks the final open-ended bracket.

### Environment and Execution
We ran everything directly on Windows (no virtual machine).
- Regular test execution was done on Windows.
- Mutation testing with cosmic-ray was run through WSL.

### Technologies

#### Streamlit vs Django
Streamlit was chosen because we wanted to focus on tax logic and testing, not on building full web infrastructure.
- With Streamlit, we could quickly build the interface we needed (inputs, comparison metrics, charts, export actions) and iterate fast.
- Django is great for larger web platforms, but here it would have added extra layers (models, routing, templates, admin) that were outside our project goal.
- In short, Streamlit let us keep the project lightweight and spend more time on correctness and test coverage.

#### Pytest vs Unittest
The most important tooling decision in this project was using `pytest` instead of `unittest`.
- `pytest` made the test suite easier to write and read, especially because we organized tests by strategy (basis path, boundary value, condition, decision, equivalence, statement, mutation).
- We relied on `pytest` assertions and structure to keep tests concise while still expressing business rules clearly.
- Compared to `unittest`, we got the same verification power with less boilerplate, which helped us scale the suite faster.
- `pytest` also fit naturally with our mutation-testing workflow and with the way we structured this repository.

Our conclusion: `unittest` is solid, but `pytest` matched our goals better for speed, readability, and maintainability.

## Diagrams


### Use case (application flow)

High-level flow from user input through calculators to the frontend and optional export.

![Use case diagram](diagrams/useCase.png)

### Development and testing pipeline

Local development, testing strategies, and GitHub flow through Actions on `master`.

![Development and testing pipeline](diagrams/pipeline.png)

## AI-Assisted Testing Report


### Tools and roles

| Tool | Role |
|------|------|
| **Google Gemini** | Early brainstorming about the application idea and how to apply testing strategies. |
| **Gemini and Cursor** | Drafting and refining automated tests (`pytest`), including structure, assertions, and edge cases aligned with `src/` calculators and `src/tax_rules.json`. |
| **Cursor (feedback loop)** | After a full test module was written, we used the chat to cross-check coverage-for example, by walking through `TestEquivalencePartitioning` in `tests/test_equivalence_partitioning.py` to confirm invalid/valid partitions for `venit_brut` and `anul_fiscal` were represented and that both `EmployeeCalculator` and `PFACalculator` stayed in sync. |
| **Cursor** | Building and iterating the Streamlit UI in `src/app.py` (layout, inputs, comparison flow, exports) while keeping business logic in calculators and tests separate from presentation. |

### Workflow example

In **`tests/test_boundary_values.py`** we first wrote **employee** boundary cases by hand, then used this prompt to add **PFA** to the same tests: “Here is `test_venit_brut_boundary_zero` for `EmployeeCalculator` only. Add matching `PFACalculator` calls and assertions in the same test, same year, without changing pytest style.”

```19:40:tests/test_boundary_values.py
    def test_venit_brut_boundary_negative(self):
        """Boundary: just below zero (invalid)"""
        with pytest.raises(ValueError):
            EmployeeCalculator(-0.01, 2024)
        with pytest.raises(ValueError):
            PFACalculator(-0.01, 2024)

    def test_venit_brut_boundary_zero(self):
        """Boundary: exactly zero"""
        employee = EmployeeCalculator(0, 2024).calculate()
        assert employee["venit_net"] == 0.0

        pfa = PFACalculator(0, 2024).calculate()
        assert pfa["venit_net"] == 0.0

    def test_venit_brut_boundary_just_above_zero(self):
        """Boundary: just above zero"""
        employee = EmployeeCalculator(0.01, 2024).calculate()
        assert employee["venit_net"] > 0

        pfa = PFACalculator(0.01, 2024).calculate()
        assert pfa["venit_net"] > 0
```

### Example of prompts used


**Streamlit UI (Cursor)**

- **Prompt:** “Add a sidebar fiscal year selector and wire it to both calculators without moving tax math out of `src/` calculators.”

**Coverage review (Cursor)**

- **Prompt:** In `tests/test_equivalence_partitioning.py`, list every equivalence class we claim in the docstring and show which test method covers it for employee vs PFA. Flag gaps.

**Mutation testing with cosmic-ray (Cursor / Gemini)**

- **Prompt:** “We run mutation testing with cosmic-ray on the calculator code under `src/`. Walk through how to install and run it (`cosmic-ray init` / `cosmic-ray exec`, then `cr-report` / `cr-html` if needed). Then break down the report: how many mutants, killed vs survived vs no coverage, what those buckets mean for our repo, a few interesting survivors, and which look equivalent vs worth a new test.”

### Limitations and how we used AI safely

- AI suggestions were always checked against **`src/tax_rules.json`** and running **`pytest`**; incorrect rates or thresholds were caught by tests or manual spot checks.
- We treated AI output as **draft code**: naming, imports, and assertions were aligned with the rest of the repo before merging.

### Summary

Gemini helped frame the problem and test matrix; Gemini and Cursor accelerated writing and extending suites such as **`tests/test_boundary_values.py`** and **`tests/test_equivalence_partitioning.py`**; Cursor closed the loop on coverage and delivered the Streamlit front end.
