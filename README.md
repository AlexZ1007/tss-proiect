# Comparator Taxe Romania - PFA vs Salariat

Aplicatie web in Python (Streamlit) pentru compararea taxelor dintre:
- Salariat
- PFA

Aplicatia foloseste reguli fiscale configurabile pe an in `src/tax_config.py`.

## Cerinte

- Python 3.10+
- `pip`

## Instalare dependente

Din radacina proiectului:

```bash
pip install -r requirements.txt
```

## Rulare proiect (Streamlit)

Din radacina proiectului:

```bash
streamlit run src/app.py
```

Dupa lansare, aplicatia se deschide in browser automat (sau poti copia URL-ul afisat in terminal).

## Rulare teste (pytest)

Din radacina proiectului:

```bash
pytest
```

Pentru output mai detaliat:

```bash
pytest -v
```

