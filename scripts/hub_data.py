"""Data for the research hub pages. Standard library only.

  data/earnings.json   upcoming earnings dates for every covered company (Nasdaq calendar,
                       with an estimate from the filing pattern when a date is not out yet)
  data/insiders.json   Form 4 insider trades in covered companies over the past year (SEC EDGAR)
  data/funds.json      the latest 13F holdings of well-known investment managers (SEC EDGAR)

Covered companies are the public names in data/watchlist.json (holdings, watchlist and reports).
"""
import json, os, re, sys, time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone

from update_data import get, load, save, DATA

NOW = datetime.now(timezone.utc)
STAMP = NOW.strftime('%Y-%m-%dT%H:%M:%SZ')
TODAY = NOW.date()
CO = os.path.join(DATA, 'co')
BROWSER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
           'Accept': 'application/json, text/plain, */*', 'Origin': 'https://www.nasdaq.com', 'Referer': 'https://www.nasdaq.com/'}


def covered():
    """[(ticker, name, cik)] for the public companies on the watchlist"""
    wl = load(os.path.join(DATA, 'watchlist.json'), {}).get('companies', [])
    xc = load(os.path.join(DATA, 'extra.json'), {}).get('cik', {})
    out = []
    for c in wl:
        t = c.get('ticker')
        if not t or c.get('private'):
            continue
        d = load(os.path.join(CO, t.replace('.', '-') + '.json'), {})
        cik = d.get('cik') or xc.get(t)
        out.append((t, c.get('name') or d.get('n') or t, int(cik) if cik else None))
    return out


def sec(ua):
    return {'User-Agent': ua, 'Accept-Encoding': 'identity'}


# ------------------------------------------------------------------ earnings calendar
def earnings(cos):
    want = {t for t, _, _ in cos}
    found = {}
    ok = 0
    past = {}
    for i in range(-35, 75):
        d = TODAY + timedelta(days=i)
        if d.weekday() >= 5:
            continue
        try:
            raw = json.loads(get(f'https://api.nasdaq.com/api/calendar/earnings?date={d.isoformat()}', BROWSER, tries=2, timeout=20))
            ok += 1
            for r in ((raw.get('data') or {}).get('rows') or []):
                s = (r.get('symbol') or '').upper()
                if s in want and d < TODAY:
                    past[s] = d.isoformat()          # reported recently; keep the latest
                    continue
                if s in want and s not in found:
                    tm = r.get('time') or ''
                    found[s] = {'date': d.isoformat(), 'when': 'before the open' if 'pre' in tm else 'after the close' if 'after' in tm else '',
                                'epsEst': r.get('epsForecast') or None, 'ests': r.get('noOfEsts') or None,
                                'lastEps': r.get('lastYearEPS') or None, 'quarter': r.get('fiscalQuarterEnding') or None, 'src': 'Nasdaq'}
        except Exception as e:
            if ok == 0 and i > -28:
                print(f'  note earnings calendar unavailable ({str(e)[:60]}); using filing-pattern estimates', file=sys.stderr)
                break
        time.sleep(.25)
    rows = []
    for t, name, cik in cos:
        e = found.get(t)
        if not e and t in past:
            # reported in the past five weeks; the next report is about 13 weeks after that one
            nxt = date.fromisoformat(past[t]) + timedelta(days=91)
            e = {'date': nxt.isoformat(), 'when': '', 'src': 'estimate', 'last': past[t]}
        if e and t in past:
            e['last'] = past[t]
        if not e:
            # estimate from the filing pattern: the next report comes about 13 weeks after the last one
            d = load(os.path.join(CO, t.replace('.', '-') + '.json'), {})
            fl = [x for x in d.get('filings', []) if x['form'] in ('10-Q', '10-K')]
            if fl:
                last = date.fromisoformat(fl[0]['date'])
                nxt = last + timedelta(days=91 if fl[0]['form'] == '10-Q' else 70)
                while nxt < TODAY:
                    nxt += timedelta(days=91)
                e = {'date': nxt.isoformat(), 'when': '', 'src': 'estimate'}
        rows.append({'t': t, 'name': name, **(e or {'date': None})})
    rows.sort(key=lambda r: r['date'] or '9999')
    save(os.path.join(DATA, 'earnings.json'), {'updated': STAMP, 'rows': rows})
    print(f'  ok   earnings {sum(1 for r in rows if r.get("src") == "Nasdaq")} confirmed, {sum(1 for r in rows if r.get("src") == "estimate")} estimated')


# ------------------------------------------------------------------ Form 4 insider trades
def _v(el, path):
    x = el.find(path)
    return None if x is None or x.text is None else x.text.strip()


def parse4(xml):
    root = ET.fromstring(xml)
    owners = []
    for o in root.findall('reportingOwner'):
        rel = o.find('reportingOwnerRelationship')
        title = []
        if rel is not None:
            if _v(rel, 'officerTitle'): title.append(_v(rel, 'officerTitle'))
            elif _v(rel, 'isOfficer') in ('1', 'true'): title.append('Officer')
            if _v(rel, 'isDirector') in ('1', 'true'): title.append('Director')
            if _v(rel, 'isTenPercentOwner') in ('1', 'true'): title.append('10% owner')
        owners.append(((_v(o, 'reportingOwnerId/rptOwnerName') or '').title(), ', '.join(title)))
    plan = _v(root, 'aff10b5One') in ('1', 'true')
    tx = []
    for t in root.findall('nonDerivativeTable/nonDerivativeTransaction'):
        code = _v(t, 'transactionCoding/transactionCode')
        sh = _v(t, 'transactionAmounts/transactionShares/value')
        px = _v(t, 'transactionAmounts/transactionPricePerShare/value')
        tx.append({'d': _v(t, 'transactionDate/value'), 'code': code,
                   'ad': _v(t, 'transactionAmounts/transactionAcquiredDisposedCode/value'),
                   'sh': float(sh) if sh else None, 'px': float(px) if px else None,
                   'after': float(_v(t, 'postTransactionAmounts/sharesOwnedFollowingTransaction/value') or 0) or None})
    return owners, plan, tx


def insiders(cos, ua):
    path = os.path.join(DATA, 'insiders.json')
    old = load(path, {})
    seen = old.get('seen', {})           # accession -> parsed rows, so each filing is read once
    since = (TODAY - timedelta(days=365)).isoformat()
    out, n_new = {}, 0
    for t, name, cik in cos:
        if not cik:
            continue
        try:
            sub = json.loads(get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json', sec(ua), tries=2, timeout=30)); time.sleep(.12)
        except Exception as e:
            print(f'  FAIL insiders {t} {str(e)[:60]}', file=sys.stderr); continue
        rec = sub.get('filings', {}).get('recent', {})
        rows = []
        for i, form in enumerate(rec.get('form', [])):
            if form != '4' or rec['filingDate'][i] < since:
                continue
            acc = rec['accessionNumber'][i]
            if acc not in seen:
                if n_new >= (2500 if os.environ.get('RUN_KIND', '') == 'workflow_dispatch' else 400):   # cap per run; the rest is picked up next time
                    continue
                doc = re.sub(r'^xslF345X\d+/', '', rec['primaryDocument'][i])
                url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-", "")}/{doc}'
                try:
                    owners, plan, tx = parse4(get(url, sec(ua), tries=2, timeout=30))
                    seen[acc] = {'o': owners, 'p': plan, 'tx': tx, 'u': f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-", "")}/{rec["primaryDocument"][i]}', 'f': rec['filingDate'][i]}
                except Exception as e:
                    seen[acc] = {'err': str(e)[:60], 'f': rec['filingDate'][i]}
                n_new += 1
                time.sleep(.12)
            s = seen[acc]
            if 'tx' not in s:
                continue
            who, title = (s['o'][0] if s['o'] else ('', ''))
            for x in s['tx']:
                if x['code'] not in ('P', 'S'):
                    continue                  # open-market buys and sells only; grants, exercises and tax withholding are left out
                rows.append({'d': x['d'], 'who': who, 'title': title, 'type': 'Buy' if x['code'] == 'P' else 'Sell',
                             'sh': x['sh'], 'px': x['px'], 'val': round(x['sh'] * x['px']) if x['sh'] and x['px'] else None,
                             'after': x['after'], 'plan': s['p'], 'url': s['u'], 'filed': s['f']})
        rows.sort(key=lambda r: r['d'] or '', reverse=True)
        b = [r for r in rows if r['type'] == 'Buy']; sl = [r for r in rows if r['type'] == 'Sell']
        out[t] = {'name': name, 'buys': len(b), 'sells': len(sl), 'buyVal': sum(r['val'] or 0 for r in b),
                  'sellVal': sum(r['val'] or 0 for r in sl), 'rows': rows[:60]}
    seen = {k: v for k, v in seen.items() if v.get('f', '') >= since}
    save(path, {'updated': STAMP, 'source': 'SEC EDGAR Form 4', 'companies': out, 'seen': seen})
    print(f'  ok   insiders {len(out)} companies, {n_new} new filings read')


# ------------------------------------------------------------------ 13F holdings of well-known managers
FUNDS = [  # (CIK, check word in the SEC name, display name, manager)
    (1067983, 'BERKSHIRE', 'Berkshire Hathaway', 'Warren Buffett and Greg Abel'),
    (1336528, 'PERSHING', 'Pershing Square', 'Bill Ackman'),
    (1536411, 'DUQUESNE', 'Duquesne Family Office', 'Stanley Druckenmiller'),
    (1656456, 'APPALOOSA', 'Appaloosa', 'David Tepper'),
    (1061768, 'BAUPOST', 'Baupost Group', 'Seth Klarman'),
    (1040273, 'THIRD POINT', 'Third Point', 'Dan Loeb'),
    (1167483, 'TIGER GLOBAL', 'Tiger Global', 'Chase Coleman'),
    (1350694, 'BRIDGEWATER', 'Bridgewater Associates', 'Founded by Ray Dalio'),
    (1697748, 'ARK', 'ARK Investment Management', 'Cathie Wood'),
    (1037389, 'RENAISSANCE', 'Renaissance Technologies', 'Quantitative; founded by Jim Simons'),
]
DROP = {'inc', 'corp', 'corporation', 'co', 'com', 'ltd', 'plc', 'holdings', 'hldgs', 'holding', 'group', 'grp', 'the', 'class', 'cl',
        'a', 'b', 'c', 'and', 'new', 'del', 'sa', 'nv', 'ag', 'lp', 'llc', 'company', 'cos', 'incorporated', 'shs', 'ord', 'common', 'stock', 'com.'}


ABBR = {'mtr': 'motor', 'mtrs': 'motors', 'pete': 'petroleum', 'wtr': 'water', 'wks': 'works', 'intl': 'international', 'svcs': 'services',
        'sys': 'systems', 'mfg': 'manufacturing', 'natl': 'national', 'finl': 'financial', 'amer': 'america', 'hlth': 'health', 'tr': 'trust',
        'pptys': 'properties', 'ppty': 'property', 'comm': 'communications', 'ent': 'entertainment', 'resh': 'research', 'bros': 'brothers',
        'labs': 'laboratories', 'pharma': 'pharmaceuticals', 'dominos': 'domino s', 'str': 'street'}


def norm(s, expand=False):
    s = re.sub(r'\(.*?\)', ' ', (s or '').lower()).replace('&', ' and ').replace("'", ' ')
    w = [x for x in re.split(r'[^a-z0-9]+', s) if x and x not in DROP]
    if expand:
        w = ' '.join(ABBR.get(x, x) for x in w).split()
    return ' '.join(w)


ALIAS = {'space exploration technologies': 'SPCX', 'kratos defense and security solutions': 'KTOS', 'axon enterprise': 'AXON',
         'firefly aerospace': 'FLY', 'berkshire hathaway': 'BRK.B', 'alphabet': 'GOOGL'}


def match(n, names):
    """ticker for a 13F issuer name: exact, then word-by-word prefix match (13F names are abbreviated, like
    "BANK OF AMER CORP" or "SPACE EXPLORATION TECH"), accepted only when exactly one company fits"""
    if not n:
        return None
    if n in names:
        return names[n]
    w = n.split()
    if len(w[0]) < 3 or set(w) & {'spdr', 'etf', 'ishares', 'index', 'fund', 'vanguard', 'invesco', 'proshares', 'direxion', 'portfolio'}:
        return None                                   # exchange-traded funds are not companies
    hits = set()
    for k, t in names.items():
        kw = k.split()
        if not kw:
            continue
        m = min(len(w), len(kw))
        ok = True
        for i in range(m):
            if w[i] == kw[i]:
                continue
            # a shortened word only matches as the last word of both names ("bank of amer" / "bank of america")
            if i == len(w) - 1 and i == len(kw) - 1 and (kw[i].startswith(w[i]) or w[i].startswith(kw[i])) and min(len(w[i]), len(kw[i])) >= 3:
                continue
            ok = False
            break
        if ok:
            hits.add(t)
    return hits.pop() if len(hits) == 1 else None


def funds(ua):
    path = os.path.join(DATA, 'funds.json')
    old = load(path, {})
    fresh = old.get('updated') and (NOW - datetime.fromisoformat(old['updated'].replace('Z', '+00:00'))).days < 6
    if fresh and os.environ.get('RUN_KIND', '') != 'workflow_dispatch':
        print('  ok   funds (fresh this week)'); return
    uni = load(os.path.join(DATA, 'universe.json'), {}).get('companies', [])
    names = {}
    for t, name, *_ in uni:
        names.setdefault(norm(name, True), t)
    for t, name, _ in covered():
        names.setdefault(norm(name, True), t)
    for k, t in ALIAS.items():
        names[k] = t
    out, held = [], {}
    for cik, word, disp, mgr in FUNDS:
        try:
            sub = json.loads(get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json', sec(ua), tries=2, timeout=30)); time.sleep(.12)
            if word not in (sub.get('name') or '').upper():
                print(f'  note fund {disp}: CIK {cik} is {sub.get("name")}; skipped', file=sys.stderr); continue
            rec = sub['filings']['recent']
            i = rec['form'].index('13F-HR')
            acc = rec['accessionNumber'][i].replace('-', '')
            idx = json.loads(get(f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/index.json', sec(ua), tries=2, timeout=30)); time.sleep(.12)
            xmls = [x['name'] for x in idx['directory']['item'] if x['name'].lower().endswith('.xml') and 'primary_doc' not in x['name'].lower()]
            raw = get(f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{xmls[0]}', sec(ua), tries=2, timeout=60); time.sleep(.12)
            root = ET.fromstring(raw)
            ns = root.tag.split('}')[0] + '}' if root.tag.startswith('{') else ''
            agg = {}
            for it in root.iter(ns + 'infoTable'):
                if it.find(ns + 'putCall') is not None:
                    continue
                cu = it.findtext(ns + 'cusip') or ''
                nm = it.findtext(ns + 'nameOfIssuer') or ''
                v = float(it.findtext(ns + 'value') or 0)
                sh = float(it.findtext(ns + 'shrsOrPrnAmt/' + ns + 'sshPrnamt') or 0)
                a = agg.setdefault(cu, {'name': nm, 'val': 0, 'sh': 0})
                a['val'] += v; a['sh'] += sh
            px = sorted(a['val'] / a['sh'] for a in agg.values() if a['sh'] > 0 and a['val'] > 0)
            if px and px[len(px) // 2] < 2:           # some filers still report values in thousands of dollars
                for a in agg.values():
                    a['val'] *= 1000
            tot = sum(a['val'] for a in agg.values()) or 1
            hold = sorted(agg.values(), key=lambda a: -a['val'])
            top = []
            for a in hold:
                tk = match(norm(a['name'], True), names)
                row = {'name': a['name'].title(), 'val': round(a['val']), 'sh': round(a['sh']), 'pct': round(a['val'] / tot, 4), 't': tk}
                if len(top) < 15:
                    top.append(row)
                if tk:
                    held.setdefault(tk, []).append({'fund': disp, 'val': row['val'], 'pct': row['pct'], 'sh': row['sh']})
            out.append({'fund': disp, 'mgr': mgr, 'period': rec['reportDate'][i], 'filed': rec['filingDate'][i], 'total': round(tot), 'n': len(hold),
                        'url': f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/', 'top': top})
        except Exception as e:
            print(f'  FAIL fund {disp} {str(e)[:80]}', file=sys.stderr)
    if out:
        for v in held.values():
            v.sort(key=lambda x: -x['val'])
        save(path, {'updated': STAMP, 'source': 'SEC EDGAR 13F-HR', 'funds': out, 'held': held})
    print(f'  ok   funds {len(out)} managers')


def run(ua):
    cos = covered()
    for step, fn in (('earnings', lambda: earnings(cos)), ('insiders', lambda: insiders(cos, ua) if ua else None), ('funds', lambda: funds(ua) if ua else None)):
        try:
            fn()
        except Exception as e:
            print(f'  FAIL {step} {str(e)[:120]}', file=sys.stderr)
