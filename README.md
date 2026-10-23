# LDB Finance

**Company research, valuation models and market data, built so every number can be checked.** A finance research site by Luis Diaz Busquets.

**Live site:** https://ldiazbusquets.github.io/finance/

## What's inside

| Section | What it is |
|---|---|
| **Research** | Analyst reports on more than 30 public companies and four private ones (Anthropic, OpenAI, Anduril, Bloomberg). Each one includes the business, latest results, five years of figures, the balance sheet, a valuation with bear/base/bull cases, what the price assumes, risks, a comparison with its S&P 500 industry peers, and a rating. There are also notes on rates, inflation, credit and Puerto Rico. |
| **Valuation** | Search any S&P 500 company for an automatic DCF, peer multiples and a dividend model, built from its SEC filings and the last close. |
| **Models** | Every report's valuation as a downloadable spreadsheet in live formulas, a CSV, and the Python script that produced it. |
| **Tools** | Portfolio x-ray and risk, a household financial plan run through 1,000 simulated markets, retirement withdrawals with guardrails against the 4% rule, tax-loss harvesting with direct indexing, bond math, loans and options payoffs. All of them run in the browser. |
| **Markets** | Rates, the yield curve, inflation, credit spreads and oil, refreshed every weekday. |
| **Research hub** | Ask the filings, a stock screener, side-by-side comparisons, an earnings calendar, insider and fund holdings, and a public track record of every call. |
| **Ask AI** | A chat bubble on every page. A small open model (Qwen3) runs privately in the visitor's browser and answers from the page being read, the site's ratings, market data and recent headlines. |

## How ratings work

Every report values its company with the same assumptions: a 5.15% 10-year Treasury yield, a 4.5% equity risk premium and the CAPM. On those assumptions the S&P 500 itself is worth about 68% of its price (`_source/models/market.py`). Each report's model is rerun 4,000 times with every input drawn from a range: the base case is the middle, and the bear and bull cases are the 10th and 90th percentiles. Business inputs move together (correlation 0.6), and the discount rate moves on its own (`_source/models/montecarlo.py`). The average of those runs, the **expected value**, is compared with the price, and that is compared with the market figure:

- **Buy:** at least 15% cheaper than the market.
- **Hold:** within 15% either way.
- **Sell:** at least 15% dearer than the market.

The rating is relative. Each report also gives an absolute label: **undervalued**, **near fair value** or **overvalued**, based on its value against its price. Each report also shows the likely range (10th to 90th percentile), the chance the value beats the price and the chance the stock is cheaper than the market. It also says whether the rating would change if the index grew 6% or 10% a year instead of 8%. The same rule applies whoever owns the stock, and the author's holdings appear only in each report's disclosure. The full method is on the About page.

## Architecture

Static HTML on GitHub Pages: no server, no accounts, no tracking.

```
reports/           every company report (generated)
notes/             research notes on rates, inflation, credit and Puerto Rico (generated)
archive/           frozen published versions of each report
*.html             the site's own pages: home, research, tools, markets, about (generated)
_source/           the generator: edit here, never the generated HTML
  build.py         layout, every non-report page, and the build checks
  pages/           report content (holdings.py, coverage.py), report template (rep.py), ratings rule (ratings.py), notes
  models/          one Python valuation script per report, plus export.py (CSV) and xlsx_models.py (Excel)
  consistency.py   cross-section checks on the generated reports
scripts/           data pipeline run by GitHub Actions
data/              market, company, price, headline and model data (generated)
assets/            CSS and the browser JavaScript for tools, the research hub and Ask AI
```

### Data pipeline

`.github/workflows/update-data.yml` runs every weekday after the close (`scripts/update_data.py`):

- Rates, inflation, spreads and oil come from FRED, through a `FRED_API_KEY` secret.
- Company financials come from SEC EDGAR XBRL company facts, through a `SEC_USER_AGENT` secret. Annual figures come from 10-Ks; quarterly and trailing-twelve-month figures come from 10-Qs.
- Prices for every S&P 500 company and the index come from Yahoo Finance closing prices.
- Earnings dates, Form 4 insider trades and 13F fund holdings feed the research hub.

`.github/workflows/news.yml` collects market headlines (titles only) from public RSS feeds three times each weekday, for Ask AI.

## Checks before anything is published

`python3 _source/build.py` stops without publishing if any of these fail:

1. **Model check** (`models/export.py --check`): every model script reruns, and each report's bear, base, bull and weighted values must match what its model produces.
2. **Consistency check** (`consistency.py`): inside each generated report:
   - The weighted value equals 25% bear, 50% base and 25% bull, and the simulation's unshocked run reproduces each report's base case.
   - The price chart, the scenario table and the report agree.
   - The valuation bridge adds up. PV of cash flows plus PV of the terminal value equals enterprise value; EV plus or minus net cash equals equity; and equity divided by shares equals the per-share value.
   - In the five-year table, free cash flow equals operating cash flow minus capital spending in every column.
   - A trailing free-cash-flow figure elsewhere in the report must match that table or name whose definition it uses. Amazon's own figure, for example, nets $4.0 billion of equipment proceeds.
   Every check a report should have must actually run. If a layout change hides the structure a rule looks for, the build fails instead of skipping it. The few exemptions (foreign filers with hand-built tables, the bank) are listed in the code with a reason. Private companies are checked too, in billions. `_source/tests/test_consistency.py` breaks a real report in specific ways and confirms that the checker catches each one; the build runs it every time.
3. **Formula tests** (`tests/test_formulas.py`): the building blocks are checked against numbers worked out by hand or taken from textbooks: CAPM and WACC, the growth fade, a two-year DCF and a steady-state DCF that must equal the growing-perpetuity formula, the bridge to per-share value, the dividend model, the bank excess-return model (a bank earning its cost of equity is worth book value), the S&P 500 benchmark, the rating lines, the Monte Carlo draws (percentiles and the 0.6 correlation), and the bond pricer (a 5% ten-year bond at 6% is $925.61; a ten-year zero has a duration of exactly ten years).
4. **Spreadsheet check** (`models/xlsx_models.py --check`, run whenever a model changes): every Excel workbook is recalculated in LibreOffice and compared with the Python models.

5. **Audit against filings** (by hand): the build can't catch a figure copied wrong from a filing, so reports are also checked against the company's own release or SEC filing. Each pass, with any corrections, is logged on the About page (`about.html#audit`).

## Keeping reports current

Each weekday the data job runs `scripts/review_data.py`. It applies the rating rule at the latest close, keeping each report's value fixed, and writes `data/review.json`. The Research page and each report then flag reports where:

- the rating would change at today's price, or is within 3 points of a threshold;
- the company has filed a 10-Q or 10-K, or reported results, since the report;
- the price has moved 15% or more since the report.

Values and ratings change only when a report is revised. The flags only say which reports to revise first.

## Published versions

When a report's published numbers change (its date, rating, base case, weighted value or price at writing), the build freezes a copy of the new version in `archive/<report>/<date>.html` (`_source/archive.py`). Frozen copies keep the page as published, without the live parts, and are never edited. `archive/index.json` lists every version, and each report links its earlier ones.

## Reproducing a valuation

```
cd _source/models
python3 nvda.py          # prints the base, bear and bull cases, the weighted value, discount-rate sensitivity and implied growth
python3 market.py        # the S&P 500 on the same assumptions (the rating benchmark)
```

Each report also links its spreadsheet, CSV and script, and ends with a **Figures and sources** chapter: where each kind of figure comes from (with links to the release and the latest 10-K and 10-Q), whether the report has been checked by hand, and the exact ranges its simulation draws from with the results.

## Notes

- Figures for 2026 come from company filings and releases, which each report cites. Estimates are labelled.
- Reports were drafted with help from Claude, an AI model made by Anthropic. Anthropic is itself the subject of a report here, and is a customer or investee of several covered companies. Those links are disclosed where they apply.
- Nothing here is investment advice.
