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
    if so and max(r['end'] for r in so) < (date.today() - timedelta(days=730)).isoformat():
        so = []   # the company stopped tagging it; a years-old count would be wrong
    if so:
        last = max(r['end'] for r in so)
        shares = sum(r['val'] for r in so if r['end'] == last and r.get('form', '').startswith(('10-', '20-', '40-'))) or so[-1]['val']
    return ends, f, shares


# ------------------------------------------------------------------ latest quarter
QFORMS = ('10-K', '10-K/A', '10-KT', '10-Q', '10-Q/A', '20-F', '40-F', '6-K')


def _days(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def _rows(g, tag, unit, instant):
    out = []
    for r in _units(g, tag, unit):
        if r.get('form') not in QFORMS or 'end' not in r or (not instant and 'start' not in r):
            continue
        out.append(r)
    return out


def _pick(rows, ok):
    """the latest-filed row that passes ok()"""
    best = None
    for r in rows:
        if ok(r) and (best is None or r.get('filed', '') > best.get('filed', '')):
            best = r
    return best


def _ttm_one(rows, E, fye):
    """trailing twelve months ending E: last fiscal year + this year to date - last year to date"""
    full = _pick(rows, lambda r: r['end'] == E and 330 <= _days(r['start'], r['end']) <= 400)
    if full:
        return full['val']
    ytd = _pick(rows, lambda r: r['end'] == E and abs(_days(fye, r['start']) - 1) <= 7)
    if not ytd:
        return None
    n = _days(ytd['start'], E)
    ann = _pick(rows, lambda r: abs(_days(r['end'], fye)) <= 7 and 330 <= _days(r['start'], r['end']) <= 400)
    prev = _pick(rows, lambda r: abs(_days(r['end'], E) - 365) <= 10 and abs(_days(r['start'], r['end']) - n) <= 10)
    if not ann or not prev:
        return None
    return ann['val'] + ytd['val'] - prev['val']


def quarterly(facts, ends):
    """Figures from the latest 10-Q when it is newer than the last 10-K:
    trailing-twelve-month flows and the latest balance sheet."""
    if not ends:
        return None
    g = facts.get('facts', {}).get('us-gaap', {})
    fye = ends[-1]
    E = None
    for tag in FLOW['rev'] + FLOW['ni']:
        for r in _rows(g, tag, 'USD', False):
            if r['form'].startswith('10-Q') and r['end'] > fye and (E is None or r['end'] > E):
                E = r['end']
    if not E or _days(fye, E) > 300:
        return None
    ttm = {}
    for key, tags, unit in [(k, v, 'USD') for k, v in FLOW.items()] + [(k, v, 'USD/shares') for k, v in PERSHARE.items()]:
        val = None
        for tag in tags:                       # first tag with a usable value at E wins
            val = _ttm_one(_rows(g, tag, unit, False), E, fye)
            if val is not None:
                break
        ttm[key] = val
    if ttm.get('ebit') is None and ttm.get('pretax') is not None:
        ttm['ebit'] = ttm['pretax'] + (ttm.get('intexp') or 0)
    dil = None
    for tag in SHARES['dil']:
        r = _pick(_rows(g, tag, 'shares', False), lambda r: r['end'] == E and 80 <= _days(r['start'], r['end']) <= 100)
        if r:
            dil = r['val']; break
    s = {}
    for k, tags in STOCK.items():
        s[k] = None
        for tag in tags:
            r = _pick(_rows(g, tag, 'USD', True), lambda r: r['end'] == E)
            if r:
                s[k] = r['val']; break
    if s['ltd'] is not None:
        debt, cur = s['ltd'] + (s['stb'] or 0), (s['ltdc'] or 0) + (s['stb'] or 0)
    elif s['ltdnc'] is not None or s['debtc'] is not None or s['ltdc'] is not None:
        cur = s['debtc'] if s['debtc'] is not None else (s['ltdc'] or 0) + (s['stb'] or 0)
        debt = (s['ltdnc'] or 0) + cur
    else:
        debt = cur = None
    bs = {'debt': debt, 'debtcur': cur, 'cash': None if s['cash'] is None else s['cash'] + (s['stinv'] or 0),
          'eq': s['eq'], 'assets': s['assets'], 'ca': s['ca'], 'cl': s['cl']}
    if ttm.get('rev') is None and ttm.get('ni') is None:
        return None
    rnd = lambda k, x: None if x is None else (round(x, 4) if k in ('eps', 'dps') else int(round(x)))
    return {'end': E, 'ttm': {k: rnd(k, v) for k, v in ttm.items()}, 'bs': {k: rnd(k, v) for k, v in bs.items()},
            'dil': None if dil is None else int(dil)}


QKEYS = ['rev', 'gp', 'ebit', 'ni', 'cfo', 'capex', 'sbc', 'da']


def _discrete(rows):
    """{quarter end: value} for one tag. 10-Qs give three-month figures for the income statement but
    year-to-date figures for cash flow, and the 10-K gives only the year; a quarter is a ~3-month
    row, or a cumulative row minus the cumulative row one quarter shorter with the same start."""
    best = {}
    for r in rows:
        k = (r['start'], r['end'])
        if k not in best or r.get('filed', '') > best[k].get('filed', ''):
            best[k] = r
    by_start = {}
    for (a, b), r in best.items():
        by_start.setdefault(a, []).append((b, r['val']))
    out = {}
    for (a, b), r in best.items():
        n = _days(a, b)
        if 80 <= n <= 125:                    # 12- to 16-week quarters (Costco's fourth quarter is 16 weeks)
            out[b] = r['val']
    for a, lst in by_start.items():
        lst.sort()
        for (b0, v0), (b1, v1) in zip(lst, lst[1:]):
            if 80 <= _days(b0, b1) <= 125 and _days(a, b0) >= 80 and b1 not in out:
                out[b1] = v1 - v0
    return out


def _fix_year_as_quarter(d, only=None):
    """Some filers tag the full-year figure with the fourth quarter's dates (L3Harris, FY2025). A quarter
    more than twice the size of its neighbours, with the three quarters before it known, is the year:
    subtract those three quarters."""
    ks = sorted(d)
    fixed = set()
    for i, e in enumerate(ks):
        if only is not None and not any(abs(_days(e, x)) <= 7 for x in only):
            continue
        if e not in d:
            continue
        others = sorted(abs(d[k]) for k in ks if k != e and k in d and abs(_days(k, e)) <= 200)   # the quarters around it
        if len(others) < 2 or d[e] <= 0:
            continue
        med = others[len(others) // 2]
        if d[e] > 2.2 * med:
            last3 = [k for k in ks[:i] if k in d and 0 < _days(k, e) <= 290]
            if len(last3) >= 3:
                d[e] = d[e] - sum(d[k] for k in last3[-3:])
            else:
                del d[e]
            fixed.add(e)
    return fixed


def _qlabel(e, fye):
    """fiscal quarter label for a quarter ending e, given a fiscal-year end date"""
    de, df = date.fromisoformat(e), date.fromisoformat(fye)
    if de.day <= 7: de -= timedelta(days=de.day)       # 52/53-week years ending in early January
    if df.day <= 7: df -= timedelta(days=df.day)
    m = (de.month - df.month) % 12
    k = round(m / 3) % 4 or 4
    fy = de.year if de.month <= df.month else de.year + 1
    if df.month == 12: fy = de.year
    return f'Q{k} FY{str(fy)[-2:]}'


def quarters(facts, ends, n=8, frev=None):
    """The last n fiscal quarters: income statement and cash flow per quarter, balance sheet at each quarter end."""
    if not ends:
        return None
    g = facts.get('facts', {}).get('us-gaap', {})
    ser = {}
    yearq = set()
    for key in QKEYS:
        per = []
        for pri, tag in enumerate(FLOW[key]):
            d = _discrete(_rows(g, tag, 'USD', False))
            if d:
                per.append((max(d), -pri, d))
        out = {}
        for _, _, d in sorted(per, reverse=True):
            for k, v in d.items():
                out.setdefault(k, v)
        if key == 'rev':
            yearq = _fix_year_as_quarter(out)
        elif yearq:               # the same filing glitch usually hits the other lines of that quarter
            _fix_year_as_quarter(out, only=yearq)
        ser[key] = out
    eps = {}
    for tag in PERSHARE['eps']:
        for k, v in _discrete(_rows(g, tag, 'USD/shares', False)).items():
            eps.setdefault(k, v)
    ser['eps'] = eps
    qe = sorted(e for e in set(ser['rev']) | set(ser['ni']) if e >= (date.today() - timedelta(days=365 * 4)).isoformat())
    keep = []
    for e in qe:                               # one end per quarter: drop restated stubs within 30 days
        if keep and _days(keep[-1], e) < 30:
            keep[-1] = e
        else:
            keep.append(e)
    qe = keep[-(n + 4):]                       # four extra so the first shown quarter has a year-ago comparison
    if len(qe) < 2:
        return None

    def near(d, e):
        if e in d:
            return d[e]
        for k, v in d.items():
            if abs(_days(k, e)) <= 7:
                return v
        return None
    f = {k: [near(ser[k], e) for e in qe] for k in QKEYS + ['eps']}
    bs = {'cash': [], 'debt': [], 'eq': []}
    for e in qe:
        s = {}
        for k, tags in STOCK.items():
            s[k] = None
            for tag in tags:
                r = _pick(_rows(g, tag, 'USD', True), lambda r: abs(_days(r['end'], e)) <= 3)
                if r:
                    s[k] = r['val']; break
        if s['ltd'] is not None:
            debt = s['ltd'] + (s['stb'] or 0)
        elif s['ltdnc'] is not None or s['debtc'] is not None or s['ltdc'] is not None:
            debt = (s['ltdnc'] or 0) + (s['debtc'] if s['debtc'] is not None else (s['ltdc'] or 0) + (s['stb'] or 0))
        else:
            debt = None
        bs['cash'].append(None if s['cash'] is None else s['cash'] + (s['stinv'] or 0))
        bs['debt'].append(debt)
        bs['eq'].append(s['eq'])
    rnd = lambda k, x: None if x is None else (round(x, 4) if k == 'eps' else int(round(x)))
    f = {k: [rnd(k, x) for x in v] for k, v in f.items()}
    f.update({k: [rnd(k, x) for x in v] for k, v in bs.items()})
    # revenue can't be negative; a negative quarter is a tagging mix-up, so leave it blank
    f['rev'] = [None if x is not None and x < 0 else x for x in f['rev']]
    # reconcile: the four quarters of each fiscal year should add up to the 10-K year
    warn = False
    if frev:
        for i, e in enumerate(ends):
            a = frev[i]
            idx = [j for j, x in enumerate(qe) if 0 <= _days(x, e) <= 300]
            if a and len(idx) == 4 and any(abs(_days(qe[j], e)) <= 7 for j in idx):
                vals = [f['rev'][j] for j in idx]
                if None in vals or abs(sum(vals) / a - 1) > 0.03:
                    warn = True
    out = {'ends': qe, 'lab': [_qlabel(e, ends[-1]) for e in qe], 'f': f}
    if warn:
        out['warn'] = 1
    return out


def filings_of(sub, cik, nk=3, nq=8):
    """the latest 10-Ks and 10-Qs, newest first, with the period each one covers"""
    rec = sub.get('filings', {}).get('recent', {})
    out, tenk, tenq = [], 0, 0
    for i, form in enumerate(rec.get('form', [])):
        if (form == '10-K' and tenk < nk) or (form == '10-Q' and tenq < nq):
            acc = rec['accessionNumber'][i].replace('-', '')
            out.append({'form': form, 'date': rec['filingDate'][i], 'per': (rec.get('reportDate') or [''] * (i + 1))[i],
                        'url': f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{rec["primaryDocument"][i]}'})
            tenk += form == '10-K'; tenq += form == '10-Q'
        if tenk >= nk and tenq >= nq:
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


# Companies that moved to a new SEC registrant (a new holding company or a
# redomicile) keep their history under the old CIK. data/overrides.json maps
# ticker -> [older CIKs] under predecessorCik; their filings are merged in.
EXTRA = {}
SHAREFAC = {}
SHARESOV = {}
FVER = 9   # bump when the extraction rules change, so every file is rebuilt


def sig(t):
    v = [EXTRA.get(t), SHAREFAC.get(t), SHARESOV.get(t)]
    return json.dumps(v) if any(v) else ''


def merge(into, facts):
    for ns, tags in facts.get('facts', {}).items():
        dst = into['facts'].setdefault(ns, {})
        for tag, body in tags.items():
            d = dst.setdefault(tag, {'units': {}})
            for unit, rows in body.get('units', {}).items():
                d['units'].setdefault(unit, []).extend(rows)
    return into


def update_fundamentals(cos, ua, limit):
    global EXTRA
    global SHAREFAC
    ov = load(os.path.join(DATA, 'overrides.json'), {})
    EXTRA = ov.get('predecessorCik', {})
    SHAREFAC = ov.get('shareClassFactor', {})
    global SHARESOV
    SHARESOV = ov.get('sharesOutstanding', {})
    hdr = {'User-Agent': ua, 'Accept-Encoding': 'identity'}
    due = []
    for t, name, sec, sub, cik in cos:
        d = load(os.path.join(CO, f'{fn(t)}.json'), {})
        age = 99
        if d.get('fupd'):
            age = (NOW - datetime.fromisoformat(d['fupd'].replace('Z', '+00:00'))).days
        if d.get('fver') != FVER or d.get('ovsig', '') != sig(t):
            age = max(age, 50)   # the extraction rules or a hand correction changed
        if age >= 7:
            due.append((age, t, name, sec, sub, cik))
    due.sort(reverse=True)
    done = fails = 0
    for age, t, name, sec, sub, cik in due[:limit]:
        path = os.path.join(CO, f'{fn(t)}.json')
        d = load(path, {})
        try:
            facts = {'facts': {}}
            for k in [cik] + [x for x in EXTRA.get(t, []) if x != cik]:
                try:
                    merge(facts, json.loads(get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{k:010d}.json', hdr, tries=2, timeout=60)))
                except Exception as e:
                    if k == cik and not EXTRA.get(t):
                        raise
                time.sleep(.12)
            sub_ = json.loads(get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json', hdr, tries=2, timeout=30)); time.sleep(.12)
            fil = filings_of(sub_, cik)
            if not any(x['form'] == '10-K' for x in fil) and EXTRA.get(t):
                old = EXTRA[t][0]
                fil += [x for x in filings_of(json.loads(get(f'https://data.sec.gov/submissions/CIK{old:010d}.json', hdr, tries=2, timeout=30)), old) if x['form'] == '10-K']
            ends, f, shares = fundamentals(facts)
            fac = SHAREFAC.get(t)
            if fac:
                # e.g. Berkshire reports per Class A share; the listed B share is 1/1500 of one
                ni_, eps_ = last(f['ni']), last(f['eps'])
                shares = ni_ / eps_ * fac if ni_ and eps_ else shares
                for k in ('eps', 'dps'):
                    f[k] = [None if x is None else round(x / fac, 4) for x in f[k]]
                f['dil'] = [None if x is None else int(x * fac) for x in f['dil']]
            so = SHARESOV.get(t)
            if so:
                # the company doesn't tag its share count in XBRL (Berkshire); use the
                # count from its latest 10-Q cover page, in listed-share equivalents
                shares = so['shares']
                f['eps'] = [None if x is None else round(x / shares, 4) for x in f['ni']]
                f['dil'] = [shares if x is not None else None for x in f['ni']]
            dil = last(f['dil'])
            if shares and dil and not 0.33 < shares / dil < 3:
                shares = dil   # cover-page count is off (share classes); use diluted count
            if not ends:
                raise ValueError('no annual figures yet (new listing or new holding company; add its predecessor to data/overrides.json)')
            try:
                qd = quarterly(facts, ends)
            except Exception as e:      # the quarter is a bonus; never lose the annual figures over it
                print(f'  note quarter {t:6} {str(e)[:80]}', file=sys.stderr); qd = None
            try:
                qs = None if (fac or so) else quarters(facts, ends, frev=f['rev'])
            except Exception as e:
                print(f'  note quarters {t:6} {str(e)[:80]}', file=sys.stderr); qs = None
            if qd and (fac or so):
                qd = None               # share-class adjusted companies keep annual figures only
            if qd:                      # sanity check against the last 10-K: twelve months can't be half or double a year
                fy, tr = last(f['rev']), qd['ttm'].get('rev')
                if fy and tr and not 0.6 < tr / fy < 1.7:
                    print(f'  note quarter {t:6} twelve-month revenue {tr} vs last year {fy}; keeping annual figures', file=sys.stderr); qd = None
            d.update({'t': t, 'n': name, 'sec': sec, 'sub': sub, 'cik': cik, 'model': model_of(sec, sub),
                      'ends': ends, 'f': f, 'sh': shares, 'q': qd, 'qs': qs, 'filings': fil, 'fupd': STAMP, 'fver': FVER, 'ovsig': sig(t)})
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
        qd = d.get('q') or {}
        tt, bs = qd.get('ttm') or {}, qd.get('bs') or {}
        if tt.get('rev') is not None or tt.get('ni') is not None:    # trailing twelve months, when a 10-Q is newer
            ni = tt['ni'] if tt.get('ni') is not None else ni
            rev = tt['rev'] if tt.get('rev') is not None else rev
            ebit = tt['ebit'] if tt.get('ebit') is not None else ebit
            da = tt['da'] if tt.get('da') is not None else da
        if bs.get('eq') is not None: eq = bs['eq']
        if bs.get('debt') is not None: debt = bs['debt']
        if bs.get('cash') is not None: cash = bs['cash']
        ev = mcap + debt - cash if mcap else None
        ebitda = ebit + (da or 0) if ebit is not None else None
        r = lambda x, k=2: None if x is None or not math.isfinite(x) else round(x, k)
        # screener metrics: growth, margins, cash, debt, dividends, latest quarter
        rv = [x for x in f['rev'] if x]
        g1 = rv[-1] / rv[-2] - 1 if len(rv) >= 2 and rv[-2] > 0 else None
        g3 = (rv[-1] / rv[-4]) ** (1 / 3) - 1 if len(rv) >= 4 and rv[-4] > 0 and rv[-1] > 0 else None
        cfo = tt['cfo'] if tt.get('cfo') is not None else last(f['cfo'])
        capex = tt['capex'] if tt.get('capex') is not None else last(f['capex'])
        fcf = cfo - (capex or 0) if cfo is not None and d.get('model') != 'bank' else None
        dps = last(f.get('dps') or [])
        qs = d.get('qs') or {}
        qf, qg = qs.get('f') or {}, None
        if qf.get('rev') and len(qf['rev']) >= 5 and qf['rev'][-1] and qf['rev'][-5] and qf['rev'][-5] > 0 and not qs.get('warn'):
            qg = qf['rev'][-1] / qf['rev'][-5] - 1
        b = (P.get(t) or {}).get('b')
        extra_cols = [r(g1, 4), r(g3, 4),
                      r(ebit / rev, 4) if ebit is not None and rev and d.get('model') != 'bank' else None,
                      r(ni / rev, 4) if ni is not None and rev else None,
                      r(fcf / mcap, 4) if fcf is not None and mcap else None,
                      r((debt - cash) / ebitda, 2) if ebitda and ebitda > 0 and d.get('model') != 'bank' else None,
                      r(dps / p, 4) if dps and p else 0,
                      r(ni / eq, 4) if ni is not None and eq and eq > 0 else None,
                      r(qg, 4), b, (qs.get('lab') or [None])[-1]]
        rows.append([t, name, sec, sub, r(mcap, 0), r(p),
                     r(mcap / ni) if mcap and ni and ni > 0 else None,
                     r(ev / ebitda) if ev and ebitda and ebitda > 0 and d.get('model') in ('dcf', 'reit') else None,
                     r(ev / rev) if ev and rev and rev > 0 and d.get('model') in ('dcf', 'reit') else None,
                     r(mcap / eq) if mcap and eq and eq > 0 else None,
                     d.get('model'), 1 if t in SP else 0] + extra_cols)
    rows.sort(key=lambda x: -(x[4] or 0))
    save(os.path.join(CO, 'index.json'), {'updated': STAMP,
          'cols': ['t', 'name', 'sector', 'sub', 'mcap', 'price', 'pe', 'evEbitda', 'evSales', 'pb', 'model', 'sp',
                  'g1', 'g3', 'om', 'nm', 'fcfy', 'nde', 'dy', 'roe', 'qg', 'beta', 'qlab'], 'rows': rows})
    print(f'  ok   index {len(rows)} companies')
    return len(rows)


def watch_extra(cos, ua):
    """Watchlist companies outside the S&P 500 (Kratos, Firefly, SpaceX...) as universe rows. CIKs come from
    SEC's ticker list, cached in data/extra.json; GICS sector and sub-industry from the watchlist's "gics" field."""
    have = {c[0] for c in cos}
    wl = [c for c in load(os.path.join(DATA, 'watchlist.json'), {}).get('companies', [])
          if c.get('ticker') and c['ticker'] not in have and not c.get('private')]
    if not wl:
        return []
    path = os.path.join(DATA, 'extra.json')
    cache = load(path, {}).get('cik', {})
    if ua and any(c['ticker'] not in cache for c in wl):
        try:
            tk = json.loads(get('https://www.sec.gov/files/company_tickers.json', {'User-Agent': ua, 'Accept-Encoding': 'identity'}, tries=2, timeout=30))
            m = {v['ticker'].upper(): v['cik_str'] for v in tk.values()}
            for c in wl:
                if c['ticker'] in m:
                    cache[c['ticker']] = m[c['ticker']]
            save(path, {'updated': STAMP, 'source': 'SEC company_tickers.json', 'cik': cache})
        except Exception as e:
            print(f'  FAIL SEC ticker list {e}', file=sys.stderr)
    out = []
    for c in wl:
        if c['ticker'] in cache:
            sec, sub = (c.get('gics') or ['Industrials', 'Aerospace & Defense'])
            out.append([c['ticker'], c.get('name') or c['ticker'], sec, sub, int(cache[c['ticker']])])
    return out


def run(ua):
    os.makedirs(CO, exist_ok=True)
    manual = os.environ.get('RUN_KIND', '') == 'workflow_dispatch'
    cos = update_universe()
    if not cos:
        return 0
    n = 0
    xs = watch_extra(cos, ua)                 # watchlist names outside the S&P 500 get the same treatment
    SP.clear(); SP.update(c[0] for c in cos)
    allc = list(cos) + xs
    if ua:
        n += update_fundamentals(allc, ua, limit=600 if manual else 120)
    # covered companies without an SEC record (none today) still get daily prices
    have = {c[0] for c in allc}
    extra = [(c['ticker'],) for c in load(os.path.join(DATA, 'watchlist.json'), {}).get('companies', [])
             if c.get('ticker') and c['ticker'] not in have and not c.get('private')]
    n += update_prices(allc + extra)
    build_index(allc)
    return n


SP = set()
