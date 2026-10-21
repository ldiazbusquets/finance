# Site source

The HTML pages in this repo are generated. Edit the source here, then rebuild:

```
cd _source
python3 build.py
```

That rewrites every page in the repo root. Nothing else is touched: `assets/`, `scripts/` and `data/` are
edited in place, and `data/` is refreshed every weekday by the **Update data** workflow.

- `build.py` holds the shared layout (head, nav, footer) and every page that is not a report.
- `pages/rep.py` is the template for research reports; `pages/holdings.py` holds the reports on holdings.
- `pages/gev.py` and `pages/costco.py` are the two hand-built reports.
- `pages/coverage.py` holds SpaceX and Firefly (holdings valued with 2030 scenarios) and the private companies
  Anthropic, OpenAI and Anduril (`private=True`: whole-company values in billions, no share price).
  Their scenario math is in `models/new_coverage.py`.

To add a report, add an entry to `R` in `pages/holdings.py` (or a new module), add its ticker to
`data/watchlist.json` with `"page"`, `"call"` and `"value"`, and rebuild.

## Research hub

`ask.html`, `screener.html`, `compare.html`, `track.html`, `earnings.html` and `insiders.html` are built by
`build.py` and run on `assets/hub.js`. Their data:

- `data/co/index.json`: screener columns (growth, margins, cash-flow yield, debt, dividends), from `scripts/company_data.py`.
- `data/earnings.json`, `data/insiders.json` (SEC Form 4), `data/funds.json` (SEC 13F): written by `scripts/hub_data.py`
  on every data update. Watchlist names outside the S&P 500 get SEC figures through `data/extra.json`.
- `data/calls.json`: the track-record ledger. The build appends a row whenever a report's date or call changes;
  past rows are never edited.

`og.py` draws the link-preview images in `og/` (see the comment at its top for the fonts it needs).
