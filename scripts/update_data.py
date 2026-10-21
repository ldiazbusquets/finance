"""Nightly data update for LDB Finance.

Pulls market data from FRED (Federal Reserve Bank of St. Louis) and company
figures from SEC EDGAR, and writes small JSON files into data/ for the site.
Uses only the Python standard library. Anything that fails keeps its previous
value, so one bad download never blanks the site.

Secrets (repo Settings > Secrets and variables > Actions):
  FRED_API_KEY    free key from fredaccount.stlouisfed.org/apikeys (needed:
                  FRED blocks plain downloads from servers like GitHub's)
  SEC_USER_AGENT  "Your Name your@email.com"; SEC asks every program to
                  identify itself. Without it the company step is skipped.
"""
import csv, io, json, os, re, sys, time, urllib.request
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
TODAY = date.today()
START = (TODAY - timedelta(days=365 * 6 + 60)).isoformat()

# key: (FRED id, name, short label, format, note, transform)
SERIES = {
    'SP500':        ('SP500', 'S&P 500', 'S&P 500', 'index', 'Daily close', None),
    'VIXCLS':       ('VIXCLS', 'VIX', 'VIX', 'level', 'Expected 30-day volatility', None),
    'DFF':          ('DFF', 'Fed funds rate', 'Fed funds', 'rate', 'Effective rate', None),
    'DGS3MO':       ('DGS3MO', '3-month Treasury', '3M Treasury', 'rate', '', None),
    'DGS2':         ('DGS2', '2-year Treasury', '2Y Treasury', 'rate', '', None),
    'DGS10':        ('DGS10', '10-year Treasury', '10Y Treasury', 'rate', '', None),
    'DGS30':        ('DGS30', '30-year Treasury', '30Y Treasury', 'rate', '', None),
    'T10Y2Y':       ('T10Y2Y', '10-year minus 2-year', '10Y–2Y', 'rate', 'Below zero means inverted', None),
    'MORTGAGE30US': ('MORTGAGE30US', '30-year mortgage', 'Mortgage', 'rate', 'Weekly average', None),
    'BAMLH0A0HYM2': ('BAMLH0A0HYM2', 'High-yield spread', 'HY spread', 'rate', 'Over Treasuries', None),
    'DCOILWTICO':   ('DCOILWTICO', 'WTI crude oil', 'Oil', 'price', 'Per barrel', None),
    'DEXUSEU':      ('DEXUSEU', 'Euro', 'EUR/USD', 'fx', 'Dollars per euro', None),
    'CPI_YOY':      ('CPIAUCSL', 'CPI inflation', 'CPI inflation', 'macro', 'Year over year', 'yoy'),
    'CORE_PCE_YOY': ('PCEPILFE', 'Core PCE inflation', 'Core PCE', 'macro', 'Fed’s preferred gauge', 'yoy'),
    'UNRATE':       ('UNRATE', 'Unemployment rate', 'Unemployment', 'macro', 'Monthly', None),
    'GDP_REAL':     ('A191RL1Q225SBEA', 'Real GDP growth', 'GDP growth', 'macro', 'Quarterly, annualised', None),
    'CORE_CPI_YOY': ('CPILFESL', 'Core CPI inflation', 'Core CPI', 'macro', 'Excludes food and energy', 'yoy'),
    'T10YIE':       ('T10YIE', '10-year breakeven inflation', 'Breakeven', 'rate', 'Inflation priced into Treasuries', None),
    'BAMLC0A0CM':   ('BAMLC0A0CM', 'Investment-grade spread', 'IG spread', 'rate', 'Over Treasuries', None),
    'PR_UNRATE':    ('PRUR', 'Puerto Rico unemployment', 'PR jobless', 'macro', 'Monthly', None),
    'PR_JOBS_YOY':  ('SMS72000000000000001', 'Puerto Rico job growth', 'PR job growth', 'macro', 'Nonfarm payrolls, year over year', 'yoy'),
}
CURVE = [('1M', 'DGS1MO'), ('3M', 'DGS3MO'), ('6M', 'DGS6MO'), ('1Y', 'DGS1'), ('2Y', 'DGS2'), ('3Y', 'DGS3'),
         ('5Y', 'DGS5'), ('7Y', 'DGS7'), ('10Y', 'DGS10'), ('20Y', 'DGS20'), ('30Y', 'DGS30')]


def get(url, headers=None, tries=3, timeout=40):
    h = {'User-Agent': 'LDB-Finance-data/1.0'}
    h.update(headers or {})
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 + i * 3)


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, separators=(',', ':'), ensure_ascii=False)


# ---------------------------------------------------------------- FRED
FRED_KEY = os.environ.get('FRED_API_KEY', '').strip()
BROWSER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
           'Accept': 'text/csv,text/plain,*/*'}


def fred(series_id):
    if FRED_KEY:
        url = (f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}'
               f'&api_key={FRED_KEY}&file_type=json&observation_start={START}')
        obs = json.loads(get(url, tries=3, timeout=30)).get('observations', [])
        out = []
        for o in obs:
            try:
                out.append((o['date'][:10], float(o['value'])))
            except (ValueError, KeyError):
                continue  # "." means no value that day
        if not out:
            raise ValueError(f'{series_id}: no data')
        return out
    raw = get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={START}', BROWSER, tries=2, timeout=20).decode('utf-8', 'replace')
    rows = list(csv.reader(io.StringIO(raw)))
    out = []
    for r in rows[1:]:
        if len(r) < 2:
            continue
        try:
            out.append((r[0][:10], float(r[1])))
        except ValueError:
            continue  # "." or blank means no value that day
    if not out:
        raise ValueError(f'{series_id}: no data')
    return out


def yoy(pts):
    by = {d[:7]: v for d, v in pts}
    out = []
    for d, v in pts:
        y, m = int(d[:4]), d[5:7]
        prev = by.get(f'{y - 1}-{m}')
        if prev:
            out.append((d, (v / prev - 1) * 100))
    return out


def weekly(pts):
    """keep the last observation of each ISO week"""
    seen, out = {}, []
    for d, v in pts:
        k = date.fromisoformat(d).isocalendar()[:2]
        seen[k] = (d, v)
    return sorted(seen.values())


def summarise(pts, meta):
    name, short, fmt, note = meta
    gaps = sorted((date.fromisoformat(pts[i][0]) - date.fromisoformat(pts[i - 1][0])).days for i in range(max(1, len(pts) - 30), len(pts)))
    gap = gaps[len(gaps) // 2] if gaps else 1
    label = '1d' if gap <= 4 else '1w' if gap <= 9 else '1m' if gap <= 45 else '1q'
    last, prev = pts[-1], pts[-2] if len(pts) > 1 else None
    one = (TODAY - timedelta(days=366)).isoformat()
    five = (TODAY - timedelta(days=365 * 5 + 5)).isoformat()
    y1 = [p for p in pts if p[0] >= one]
    y5 = [p for p in pts if p[0] >= five]
    if gap <= 9:
        y5 = weekly(y5)
    r = lambda v: round(v, 4)
    return {
        'name': name, 'short': short, 'fmt': fmt, 'note': note, 'chgLabel': label,
        'last': {'d': last[0], 'v': r(last[1])},
        'prev': {'d': prev[0], 'v': r(prev[1])} if prev else None,
        'chg': r(last[1] - prev[1]) if prev else None,
        'chgPct': r((last[1] / prev[1] - 1) * 100) if prev and prev[1] else None,
        'y1': [[d, r(v)] for d, v in y1],
        'y5': [[d, r(v)] for d, v in y5],
    }


def value_on(pts, day):
    best = None
    for d, v in pts:
        if d <= day:
            best = (d, v)
        else:
            break
    return best


def update_markets():
    path = os.path.join(DATA, 'markets.json')
    m = load(path, {})
    m.setdefault('series', {})
    ok = 0
    fails = 0
    cache = {}
    for key, (sid, name, short, fmt, note, tf) in SERIES.items():
        if fails >= 3 and not ok:
            print('  FRED is not answering; stopping market downloads for this run.', file=sys.stderr)
            if not FRED_KEY:
                print('  Add a FRED_API_KEY secret (free at fredaccount.stlouisfed.org/apikeys).', file=sys.stderr)
            return 0
        try:
            pts = cache.get(sid) or fred(sid)
            cache[sid] = pts
            if tf == 'yoy':
                pts = yoy(pts)
            m['series'][key] = summarise(pts, (name, short, fmt, note))
            ok += 1
            print(f'  ok   {key:14} {pts[-1]}')
        except Exception as e:
            fails += 1
            print(f'  FAIL {key:14} {e}', file=sys.stderr)
        time.sleep(.4)
    try:
        cur = {}
        for t, sid in CURVE:
            cur[t] = cache.get(sid) or fred(sid)
            time.sleep(.4)
        latest = max(p[-1][0] for p in cur.values())
        sets = []
        for label, days in (('Today', 0), ('1 month ago', 30), ('1 year ago', 365)):
            day = (date.fromisoformat(latest) - timedelta(days=days)).isoformat()
            vals = [value_on(cur[t], day) for t, _ in CURVE]
            dates = [v[0] for v in vals if v]
            sets.append({'label': label, 'date': max(dates) if dates else day, 'v': [round(v[1], 3) if v else None for v in vals]})
        m['curve'] = {'tenors': [t for t, _ in CURVE], 'sets': sets}
        ok += 1
        print('  ok   curve', sets[0]['date'])
    except Exception as e:
        print(f'  FAIL curve {e}', file=sys.stderr)
    if ok:
        m['updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        save(path, m)
    return ok


# ---------------------------------------------------------------- SEC
REV = ['RevenuesNetOfInterestExpense', 'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueNet']
NI = ['NetIncomeLoss', 'ProfitLoss']
EPS = ['EarningsPerShareDiluted']
CFO = ['NetCashProvidedByUsedInOperatingActivities']
CAPEX = ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets']
EQ = ['StockholdersEquity']
ASSETS = ['Assets']


def annual(facts, tags, unit='USD', instant=False):
    """{fiscal year end date: value} from 10-K filings, earlier tags win"""
    gaap = facts.get('facts', {}).get('us-gaap', {})
    out = {}
    for tag in tags:
        rows = gaap.get(tag, {}).get('units', {}).get(unit, [])
        best = {}
        for r in rows:
            if r.get('form') not in ('10-K', '10-K/A') or r.get('fp') != 'FY':
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
        for k, r in best.items():
            out.setdefault(k, r['val'])
    return out


def update_companies(ua):
    wl = load(os.path.join(DATA, 'watchlist.json'), {}).get('companies', [])
    if not wl:
        return 0
    hdr = {'User-Agent': ua, 'Accept-Encoding': 'identity'}
    tick = json.loads(get('https://www.sec.gov/files/company_tickers.json', hdr))
    cik_of = {v['ticker'].upper(): int(v['cik_str']) for v in tick.values()}
    ipath = os.path.join(DATA, 'companies', 'index.json')
    old = {c['ticker']: c for c in load(ipath, {}).get('companies', [])}
    rows, ok = [], 0
    for w in wl:
        t = w['ticker'].upper()
        row = dict(old.get(t, {}), ticker=t, sector=w.get('sector', ''), status=w.get('status', 'plan'), page=w.get('page'))
        if w.get('private'):            # private companies have no SEC filings to read
            row.update(name=w.get('name') or t, private=True)
            rows.append(row)
            continue
        try:
            cik = cik_of[t]
            facts = json.loads(get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json', hdr)); time.sleep(.25)
            sub = json.loads(get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json', hdr)); time.sleep(.25)
            fin = 6000 <= int(sub.get('sic') or 0) <= 6799
            rev, ni, eps = annual(facts, REV), annual(facts, NI), annual(facts, EPS, 'USD/shares')
            cfo, capex = annual(facts, CFO), annual(facts, CAPEX)
            eq, assets = annual(facts, EQ, instant=True), annual(facts, ASSETS, instant=True)
            ends = sorted(set(rev) | set(ni))[-6:]
            years = []
            for e in ends:
                f = None if fin or e not in cfo or e not in capex else cfo[e] - capex[e]
                years.append({'fy': int(e[:4]), 'end': e, 'revenue': rev.get(e), 'netIncome': ni.get(e), 'eps': eps.get(e),
                              'cfo': cfo.get(e), 'capex': capex.get(e), 'fcf': f, 'equity': eq.get(e), 'assets': assets.get(e)})
            rec = sub.get('filings', {}).get('recent', {})
            filings = []
            for i, form in enumerate(rec.get('form', [])):
                if form in ('10-K', '10-Q', '8-K') and len(filings) < 8:
                    acc = rec['accessionNumber'][i].replace('-', '')
                    filings.append({'form': form, 'date': rec['filingDate'][i],
                                    'url': f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{rec["primaryDocument"][i]}',
                                    'desc': rec.get('primaryDocDescription', [''] * (i + 1))[i]})
            tenk = None
            for i, form in enumerate(rec.get('form', [])):
                if form == '10-K':
                    tenk = {'url': f'https://www.sec.gov/Archives/edgar/data/{cik}/{rec["accessionNumber"][i].replace("-", "")}/{rec["primaryDocument"][i]}'}
                    break
            name = sub.get('name') or t
            save(os.path.join(DATA, 'companies', f'{t}.json'), {'ticker': t, 'name': name, 'cik': cik, 'sic': sub.get('sicDescription'),
                                                                'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                                'annual': years, 'filings': filings})
            last = years[-1] if years else {}
            prev = years[-2] if len(years) > 1 else {}
            g = (last['revenue'] / prev['revenue'] - 1) if last.get('revenue') and prev.get('revenue') else None
            mg = (last['netIncome'] / last['revenue']) if last.get('netIncome') is not None and last.get('revenue') else None
            row.update(name=w.get('name') or pretty(name), fy=last.get('fy'), revenue=last.get('revenue'), revGrowth=g, netIncome=last.get('netIncome'),
                       margin=mg, eps=last.get('eps'), fcf=last.get('fcf'), filing=tenk['url'] if tenk else None)
            ok += 1
            print(f'  ok   {t:6} FY{last.get("fy")} revenue {last.get("revenue")}')
        except Exception as e:
            print(f'  FAIL {t:6} {e}', file=sys.stderr)
        row.setdefault('name', w.get('name') or t)
        rows.append(row)
    if ok:
        save(ipath, {'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'companies': rows})
    return ok


def pretty(n):
    small = {'and', 'of', 'the', '&'}
    keep = {'JPMORGAN': 'JPMorgan', 'CO': 'Co.', 'INC': 'Inc.', 'CORP': 'Corp.', 'LLC': 'LLC', 'PLC': 'plc'}
    n = re.sub(r'\s*/[A-Z]{2,4}/?', '', n)
    words = n.replace(',', '').replace('/DE/', '').replace('/', ' ').split()
    out = []
    for i, w in enumerate(words):
        u = w.upper().rstrip('.')
        out.append(keep.get(u) or (w.lower() if i and w.lower() in small else w.capitalize()))
    return ' '.join(out).strip()


if __name__ == '__main__':
    print('Markets (FRED)')
    m = update_markets()
    c = 0
    ua = os.environ.get('SEC_USER_AGENT', '').strip()
    if ua and '@' in ua:
        print('Companies (SEC EDGAR)')
        try:
            c = update_companies(ua)
        except Exception as e:
            print(f'  FAIL companies {e}', file=sys.stderr)
    else:
        print('Companies skipped: add an SEC_USER_AGENT secret like "Your Name you@email.com"')
    print('S&P 500 companies (valuation tool)')
    k = 0
    try:
        import company_data
        k = company_data.run(ua if ua and '@' in ua else '')
    except Exception as e:
        print(f'  FAIL valuation data {e}', file=sys.stderr)
    print(f'done: {m} market items, {c} companies, {k} valuation updates')
    if not m and not c and not k:
        sys.exit(1)
