# TaxVision RO

## Table of Contents
- [Purpose of the Application](#purpose-of-the-application)
- [Project Resources](#project-resources)
- [Project Setup](#project-setup)
- [Technical Report](#technical-report)
  - [Testing Scope](#testing-scope)
  - [Testing Strategies](#testing-strategies)
  - [Tax Rules Configuration Structure (`src/tax_rules.json`)](#tax-rules-configuration-structure-srctax_rulesjson)
  - [Environment and Execution](#environment-and-execution)
  - [Technologies](#technologies)
    - [Streamlit vs Django](#streamlit-vs-django)
    - [Pytest vs Unittest](#pytest-vs-unittest)
- [Diagrams](#diagrams)
- [AI-Assisted Testing Report](#ai-assisted-testing-report)

## Purpose of the Application
TaxVision RO helps users analyze Romanian income tax outcomes through a clear comparison workflow and practical decision support.

Primary objectives:
- Provide a clear history of comparisons so users can track and review previous simulations.
- Export calculation results to Excel for reporting and further analysis.
- Offer graphical views of results to make differences easier to interpret.
- Support educational and analytical use through reproducible, structured project outputs.

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
- `WSL` for mutation testing
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

### 4) Tool versions


## Technical Report

### Testing Scope
The testing scope includes only the business-logic layer:
- `calculator_pfa` (derived from `calculator_base`)
- `calculator_employee` (derived from `calculator_base`)

Excluded from testing scope:
- Frontend/display concerns
- Streamlit presentation/UI behavior

### Testing Strategies
The implemented testing strategies are covered through dedicated test modules.

#### Basis path
#### Boundary value
#### Condition coverage
#### Decision coverage
#### Equivalence partitioning
#### Statement coverage
#### Mutation testing

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
- Mutation testing with `mutmut` was run through WSL.

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

## AI-Assisted Testing Report

