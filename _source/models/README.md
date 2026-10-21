# Valuation models behind the reports

Each script reproduces the numbers in one report (run from this folder, e.g. `python3 nvda.py`).
`val_all.py` holds the shared pieces: a 5.15% 10-year Treasury, a 4.5% equity risk premium, CAPM cost of
equity, WACC, and a ten-year cash-flow model with a terminal value on the return on new capital.

To refresh a report after earnings: update the price, base-year revenue, growth, margin and capital
inputs at the top of the script from the new results and guidance, rerun it, then copy the base, bear,
bull, weighted, sensitivity and implied figures into the report in `../pages/holdings.py`.
