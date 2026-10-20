"""Company data for the LDB Finance valuation tool.

Builds, for every S&P 500 company:
  data/universe.json      the list (from Wikipedia), refreshed weekly
  data/co/<TICKER>.json   ten years of annual figures from SEC 10-K filings,
                          plus closing price, 52-week range and beta
  data/co/index.json      a small search index with market value and the
                          multiples used for peer comparison

Fundamentals only change when a company files, so each file is refreshed
once a week; prices are refreshed on every run. Standard library only.
"""
import json, os, re, sys, time, math
from datetime import date, datetime, timezone, timedelta
from html.parser import HTMLParser

from update_data import get, load, save, DATA

CO = os.path.join(DATA, 'co')
NOW = datetime.now(timezone.utc)
STAMP = NOW.strftime('%Y-%m-%dT%H:%M:%SZ')
BROWSER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
           'Accept': 'application/json,text/html,*/*'}

# ------------------------------------------------------------------ universe
class _Table(HTMLParser):
    """collects the rows of <table id="constituents">"""
    def __init__(self):
        super().__init__()
        self.depth = 0; self.rows = []; self.row = None; self.cell = None
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == 'table':
            if self.depth or a.get('id') == 'constituents':
                self.depth += 1
        elif self.depth == 1:
            if tag == 'tr':
                self.row = []
            elif tag in ('td', 'th') and self.row is not None:
                self.cell = []
    def handle_endtag(self, tag):
        if tag == 'table' and self.depth:
            self.depth -= 1
        elif self.depth == 1:
            if tag in ('td', 'th') and self.cell is not None:
                self.row.append(re.sub(r'\s+', ' ', ''.join(self.cell)).strip()); self.cell = None
            elif tag == 'tr' and self.row is not None:
                if self.row: self.rows.append(self.row)
                self.row = None
    def handle_data(self, d):
        if self.cell is not None:
            self.cell.append(d)


def parse_universe(html):
    p = _Table(); p.feed(html)
    if not p.rows:
        raise ValueError('constituents table not found')
    head = [h.lower() for h in p.rows[0]]
    col = lambda *names: next(i for i, h in enumerate(head) if any(n in h for n in names))
    it, iname, isec, isub, icik = col('symbol'), col('security'), col('sector'), col('sub-industry', 'sub industry'), col('cik')
    out = []
    for r in p.rows[1:]:
        if len(r) <= max(it, iname, isec, isub, icik):
            continue
        t = r[it].strip().upper()
        if not re.fullmatch(r'[A-Z][A-Z0-9.\-]{0,6}', t):
            continue
        try:
            cik = int(re.sub(r'\D', '', r[icik]))
        except ValueError:
            continue
        out.append([t, r[iname], r[isec], r[isub], cik])
    if len(out) < 400:
        raise ValueError(f'only {len(out)} companies parsed')
    return out


def update_universe(force=False):
    path = os.path.join(DATA, 'universe.json')
    u = load(path, {})
    fresh = u.get('updated') and (NOW - datetime.fromisoformat(u['updated'].replace('Z', '+00:00'))).days < 7
    if fresh and not force and u.get('companies'):
        return u['companies']
    try:
        html = get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
                   {'User-Agent': 'LDB-Finance/1.0 (student project; github.com/ldiazbusquets)'}).decode('utf-8', 'replace')
        cos = parse_universe(html)
        save(path, {'updated': STAMP, 'source': 'Wikipedia: List of S&P 500 companies', 'companies': cos})
        print(f'  ok   universe {len(cos)} companies')
        return cos
    except Exception as e:
        print(f'  FAIL universe {e}', file=sys.stderr)
        return u.get('companies', [])


# ------------------------------------------------------------------ SEC facts
# Each field lists XBRL tags in priority order; for a given fiscal year the
# first tag that has a value wins.
FLOW = {
    'rev':    ['RevenuesNetOfInterestExpense', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
               'RevenueFromContractWithCustomerIncludingAssessedTax', 'SalesRevenueNet', 'SalesRevenueGoodsNet'],
    'gp':     ['GrossProfit'],
    'ebit':   ['OperatingIncomeLoss'],
    'pretax': ['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
               'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments'],
    'tax':    ['IncomeTaxExpenseBenefit'],
    'ni':     ['NetIncomeLoss', 'NetIncomeLossAvailableToCommonStockholdersBasic', 'ProfitLoss'],
    'intexp': ['InterestExpense', 'InterestExpenseNonoperating', 'InterestExpenseDebt', 'InterestAndDebtExpense'],
    'da':     ['DepreciationDepletionAndAmortization', 'DepreciationAmortizationAndAccretionNet', 'DepreciationAndAmortization', 'Depreciation'],
    'cfo':    ['NetCashProvidedByUsedInOperatingActivities', 'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations'],
    'capex':  ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', 'PaymentsForCapitalImprovements'],
    'sbc':    ['ShareBasedCompensation', 'AllocatedShareBasedCompensationExpense'],
    'div':    ['PaymentsOfDividendsCommonStock', 'PaymentsOfDividends'],
    'nii':    ['InterestIncomeExpenseNet', 'InterestIncomeExpenseAfterProvisionForLoanLoss'],
}
PERSHARE = {
    'eps': ['EarningsPerShareDiluted', 'EarningsPerShareBasicAndDiluted', 'EarningsPerShareBasic'],
    'dps': ['CommonStockDividendsPerShareDeclared', 'CommonStockDividendsPerShareCashPaid'],
}
SHARES = {'dil': ['WeightedAverageNumberOfDilutedSharesOutstanding', 'WeightedAverageNumberOfShareOutstandingBasicAndDiluted']}
STOCK = {
    'cash':   ['CashAndCashEquivalentsAtCarryingValue', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 'Cash'],
    'stinv':  ['MarketableSecuritiesCurrent', 'ShortTermInvestments', 'AvailableForSaleSecuritiesDebtSecuritiesCurrent'],
    'ltd':    ['LongTermDebt', 'LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities'],
    'ltdnc':  ['LongTermDebtNoncurrent', 'LongTermDebtAndCapitalLeaseObligations'],
    'ltdc':   ['LongTermDebtCurrent', 'LongTermDebtAndCapitalLeaseObligationsCurrent'],
    'debtc':  ['DebtCurrent'],
    'stb':    ['ShortTermBorrowings', 'CommercialPaper', 'LoansAndNotesPayable'],
    'eq':     ['StockholdersEquity', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],
    'assets': ['Assets'],
    'ca':     ['AssetsCurrent'],
    'cl':     ['LiabilitiesCurrent'],
}


def _units(g, tag, unit):
    return g.get(tag, {}).get('units', {}).get(unit, [])


def _annual(g, tags, unit, instant):
    """{period end: value}; flows must cover ~one year, latest filing wins.
    The tag the company uses most recently leads, so a series doesn't mix
    definitions; older tags only fill years the lead tag doesn't cover."""
    per = []
    for pri, tag in enumerate(tags):
        best = {}
        for r in _units(g, tag, unit):
            if r.get('form') not in ('10-K', '10-K/A', '10-KT', '20-F', '40-F') or 'end' not in r:
                continue
            if not instant:
                if 'start' not in r:
                    continue
                n = (date.fromisoformat(r['end']) - date.fromisoformat(r['start'])).days
                if not 330 <= n <= 400:
                    continue
            k = r['end']
            if k not in best or r.get('filed', '') > best[k].get('filed', ''):
                best[k] = r
        if best:
            per.append((max(best), -pri, best))
    out = {}
    for _, _, best in sorted(per, reverse=True):
        for k, r in best.items():
            out.setdefault(k, r['val'])
    return out


def fundamentals(facts):
    g = facts.get('facts', {}).get('us-gaap', {})
    flow = {k: _annual(g, v, 'USD', False) for k, v in FLOW.items()}
    flow.update({k: _annual(g, v, 'USD/shares', False) for k, v in PERSHARE.items()})
    flow.update({k: _annual(g, v, 'shares', False) for k, v in SHARES.items()})
    stock = {k: _annual(g, v, 'USD', True) for k, v in STOCK.items()}
    ends = sorted(e for e in set(flow['rev']) | set(flow['ni']) if e >= '2010-01-01')
    # drop near-duplicate period ends (restated stubs): keep the last end within 300 days
    keep = []
    for e in ends:
        if keep and (date.fromisoformat(e) - date.fromisoformat(keep[-1])).days < 300:
            keep[-1] = e
        else:
            keep.append(e)
    ends = keep[-10:]

    def near(series, e, days=10):
        if e in series:
            return series[e]
        d0 = date.fromisoformat(e)
        for k, v in series.items():
            if abs((date.fromisoformat(k) - d0).days) <= days:
                return v
        return None

    f = {k: [] for k in list(FLOW) + list(PERSHARE) + list(SHARES) + ['debt', 'cash', 'eq', 'assets', 'ca', 'cl', 'debtcur']}
    for e in ends:
        for k in list(FLOW) + list(PERSHARE) + list(SHARES):
            f[k].append(near(flow[k], e))
        s = {k: near(v, e) for k, v in stock.items()}
        # total debt without double counting: LongTermDebt includes its current part;
        # DebtCurrent already includes short-term borrowings and commercial paper
        if s['ltd'] is not None:
            debt = s['ltd'] + (s['stb'] or 0)
            cur = (s['ltdc'] or 0) + (s['stb'] or 0)
        elif s['ltdnc'] is not None or s['debtc'] is not None or s['ltdc'] is not None:
            cur = s['debtc'] if s['debtc'] is not None else (s['ltdc'] or 0) + (s['stb'] or 0)
            debt = (s['ltdnc'] or 0) + cur
        else:
            debt, cur = None, None
        f['debt'].append(debt)
        f['debtcur'].append(cur)
        f['cash'].append(None if s['cash'] is None else s['cash'] + (s['stinv'] or 0))
        for k in ('eq', 'assets', 'ca', 'cl'):
            f[k].append(s[k])
    # fill gaps that can be derived
    for i in range(len(ends)):
        if f['ebit'][i] is None and f['pretax'][i] is not None:
            f['ebit'][i] = f['pretax'][i] + (f['intexp'][i] or 0)
        if f['eps'][i] is None and f['ni'][i] is not None and f['dil'][i]:
            f['eps'][i] = f['ni'][i] / f['dil'][i]
        if f['dps'][i] is None and f['div'][i] and f['dil'][i]:
            f['dps'][i] = f['div'][i] / f['dil'][i]
    for k, v in f.items():
        f[k] = [None if x is None else (round(x, 4) if k in ('eps', 'dps') else int(round(x))) for x in v]
    dei = facts.get('facts', {}).get('dei', {})
    so = dei.get('EntityCommonStockSharesOutstanding', {}).get('units', {}).get('shares', [])
    shares = None
    if so:
        last = max(r['end'] for r in so)
        shares = sum(r['val'] for r in so if r['end'] == last and r.get('form', '').startswith(('10-', '20-', '40-'))) or so[-1]['val']
    return ends, f, shares


def filings_of(sub, cik):
    """latest 10-K and the three latest 10-Qs"""
    rec = sub.get('filings', {}).get('recent', {})
    out, tenk, tenq = [], 0, 0
    for i, form in enumerate(rec.get('form', [])):
        if (form == '10-K' and not tenk) or (form == '10-Q' and tenq < 3):
            acc = rec['accessionNumber'][i].replace('-', '')
            out.append({'form': form, 'date': rec['filingDate'][i],
                        'url': f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{rec["primaryDocument"][i]}'})
            tenk += form == '10-K'; tenq += form == '10-Q'
        if tenk and tenq >= 3:
            break
    return out


BANKLIKE = {'Diversified Banks', 'Regional Banks', 'Investment Banking & Brokerage', 'Asset Management & Custody Banks',
            'Consumer Finance', 'Life & Health Insurance', 'Property & Casualty Insurance', 'Multi-line Insurance', 'Reinsurance',
            'Other Diversified Financial Services', 'Multi-Sector Holdings', 'Commercial & Residential Mortgage Finance',
            'Diversified Financial Services'}


def model_of(sector, sub):
    if sub in BANKLIKE:
        return 'bank'
    if sector == 'Real Estate':
        return 'reit'
    return 'dcf'


def update_fundamentals(cos, ua, limit):
    hdr = {'User-Agent': ua, 'Accept-Encoding': 'identity'}
    due = []
    for t, name, sec, sub, cik in cos:
        d = load(os.path.join(CO, f'{fn(t)}.json'), {})
        age = 99
        if d.get('fupd'):
            age = (NOW - datetime.fromisoformat(d['fupd'].replace('Z', '+00:00'))).days
        if age >= 7:
            due.append((age, t, name, sec, sub, cik))
    due.sort(reverse=True)
    done = fails = 0
    for age, t, name, sec, sub, cik in due[:limit]:
        path = os.path.join(CO, f'{fn(t)}.json')
        d = load(path, {})
        try:
            facts = json.loads(get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json', hdr, tries=2, timeout=60)); time.sleep(.12)
            sub_ = json.loads(get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json', hdr, tries=2, timeout=30)); time.sleep(.12)
            ends, f, shares = fundamentals(facts)
            if not ends:
                raise ValueError('no annual figures')
            d.update({'t': t, 'n': name, 'sec': sec, 'sub': sub, 'cik': cik, 'model': model_of(sec, sub),
                      'ends': ends, 'f': f, 'sh': shares, 'filings': filings_of(sub_, cik), 'fupd': STAMP})
            save(path, d)
            done += 1
        except Exception as e:
            fails += 1
            print(f'  FAIL facts {t:6} {str(e)[:120]}', file=sys.stderr)
            if fails >= 15 and not done:
                print('  SEC is not answering; stopping company figures for this run.', file=sys.stderr)
                break
    print(f'  ok   fundamentals refreshed {done}, failed {fails}, still due {max(0, len(due) - limit)}')
    return done


# ------------------------------------------------------------------ prices
def fn(t):
    return t.replace('.', '-')


def yahoo(sym):
    raw = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=2y&interval=1wk&includeAdjustedClose=true', BROWSER, tries=2, timeout=20)
    r = json.loads(raw)['chart']['result'][0]
    m = r['meta']
    ts = r.get('timestamp') or []
    cl = (r.get('indicators', {}).get('adjclose') or [{}])[0].get('adjclose') or r['indicators']['quote'][0]['close']
    hist = {t: c for t, c in zip(ts, cl) if c}
    return {'p': m.get('regularMarketPrice'), 'd': datetime.fromtimestamp(m.get('regularMarketTime', 0), timezone.utc).strftime('%Y-%m-%d'),
            'hi': m.get('fiftyTwoWeekHigh'), 'lo': m.get('fiftyTwoWeekLow'), 'cur': m.get('currency')}, hist


def beta(h, mkt):
    """weekly returns over ~2 years against the S&P 500, Blume-adjusted toward 1"""
    common = sorted(set(h) & set(mkt))
    if len(common) < 52:
        return None, len(common)
    a = [h[t] for t in common]; b = [mkt[t] for t in common]
    ra = [a[i] / a[i - 1] - 1 for i in range(1, len(a))]
    rb = [b[i] / b[i - 1] - 1 for i in range(1, len(b))]
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / (len(ra) - 1)
    var = sum((y - mb) ** 2 for y in rb) / (len(rb) - 1)
    if not var:
        return None, len(ra)
    raw = cov / var
    return round(0.67 * raw + 0.33, 3), len(ra)


def update_prices(cos):
    """closing prices + beta for everyone in one small file, so daily runs
    don't rewrite 500 company files"""
    path = os.path.join(CO, 'prices.json')
    P = load(path, {}).get('px', {})
    try:
        _, mkt = yahoo('%5EGSPC')
    except Exception as e:
        print(f'  FAIL prices: S&P 500 history unavailable ({e}); keeping previous prices', file=sys.stderr)
        return 0
    ok = fails = 0
    for t, *_ in cos:
        try:
            px, hist = yahoo(fn(t))
            if not px.get('p'):
                raise ValueError('no price')
            b, n = beta(hist, mkt)
            P[t] = {'p': round(px['p'], 4), 'd': px['d'], 'hi': px['hi'], 'lo': px['lo'], 'b': b, 'bn': n}
            ok += 1
        except Exception as e:
            fails += 1
            if fails <= 10:
                print(f'  FAIL price {t:6} {str(e)[:100]}', file=sys.stderr)
            if fails >= 25 and not ok:
                print('  Price source is not answering; keeping previous prices.', file=sys.stderr)
                break
        time.sleep(.15)
    if ok:
        save(path, {'updated': STAMP, 'source': 'Yahoo Finance (closing prices)', 'px': P})
    print(f'  ok   prices {ok}, failed {fails}')
    return ok


# ------------------------------------------------------------------ index
def last(v):
    for x in reversed(v or []):
        if x is not None:
            return x
    return None


def build_index(cos):
    rows = []
    P = load(os.path.join(CO, 'prices.json'), {}).get('px', {})
    for t, name, sec, sub, cik in cos:
        d = load(os.path.join(CO, f'{fn(t)}.json'), None)
        if not d or not d.get('f'):
            continue
        f = d['f']
        p = (P.get(t) or {}).get('p')
        sh = d.get('sh') or last(f.get('dil'))
        mcap = p * sh if p and sh else None
        ni, rev, eq = last(f['ni']), last(f['rev']), last(f['eq'])
        ebit, da = last(f['ebit']), last(f['da'])
        debt, cash = last(f['debt']) or 0, last(f['cash']) or 0
        ev = mcap + debt - cash if mcap else None
        ebitda = ebit + (da or 0) if ebit is not None else None
        r = lambda x, k=2: None if x is None or not math.isfinite(x) else round(x, k)
        rows.append([t, name, sec, sub, r(mcap, 0), r(p),
                     r(mcap / ni) if mcap and ni and ni > 0 else None,
                     r(ev / ebitda) if ev and ebitda and ebitda > 0 and d.get('model') == 'dcf' else None,
                     r(ev / rev) if ev and rev and rev > 0 and d.get('model') == 'dcf' else None,
                     r(mcap / eq) if mcap and eq and eq > 0 else None,
                     d.get('model')])
    rows.sort(key=lambda x: -(x[4] or 0))
    save(os.path.join(CO, 'index.json'), {'updated': STAMP,
          'cols': ['t', 'name', 'sector', 'sub', 'mcap', 'price', 'pe', 'evEbitda', 'evSales', 'pb', 'model'], 'rows': rows})
    print(f'  ok   index {len(rows)} companies')
    return len(rows)


def run(ua):
    os.makedirs(CO, exist_ok=True)
    manual = os.environ.get('RUN_KIND', '') == 'workflow_dispatch'
    cos = update_universe()
    if not cos:
        return 0
    n = 0
    if ua:
        n += update_fundamentals(cos, ua, limit=600 if manual else 120)
    n += update_prices(cos)
    build_index(cos)
    return n
