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

To add a report, add an entry to `R` in `pages/holdings.py` (or a new module), add its ticker to
`data/watchlist.json` with `"page"`, `"call"` and `"value"`, and rebuild.
