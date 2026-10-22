# Valuation models behind the reports

Each script reproduces the numbers in one report (run from this folder, e.g. `python3 nvda.py`).
`val_all.py` holds the shared pieces: a 5.15% 10-year Treasury, a 4.5% equity risk premium, CAPM cost of
equity, WACC, and a ten-year cash-flow model with a terminal value on the return on new capital.

To refresh a report after earnings: update the price, base-year revenue, growth, margin and capital
inputs at the top of the script from the new results and guidance, rerun it, then copy the base, bear,
bull, weighted, sensitivity and implied figures into the report in `../pages/holdings.py`.

## Checking and downloads

`export.py` reruns every model and writes the downloadable CSVs in `data/models/` (inputs, year-by-year cash
flows, the bridge to the value, scenarios and sensitivity). `build.py` runs `export.py --check` first and stops if
any report shows a base, bear, bull or weighted value its model no longer produces, so a report and its model
cannot drift apart. When refreshing a report, change the model script first, then copy its outputs into the page.

`xlsx_models.py` writes the Excel versions (`data/models/<page>.xlsx`): the same models rebuilt in live
formulas, with inputs in blue, formulas in black and links between sheets in green. `python3 xlsx_models.py --check`
recalculates every workbook in LibreOffice (set `RECALC` to the path of a recalc script) and compares each bear,
base and bull value with the model scripts. Rerun it whenever a model changes.
