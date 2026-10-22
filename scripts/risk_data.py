"""Weekly total returns for the portfolio risk tool.

For every S&P 500 company, the companies covered on the site and a list of common ETFs, downloads five years of
weekly adjusted closes (dividends included) from Yahoo Finance and writes:
  data/risk/index.json   the shared week grid and the list of tickers with names
  data/risk/<T>.json     that ticker's weekly returns on the grid (null where it did not trade yet)
Weekly data barely changes from day to day, so the full refresh runs at most once every six days
(set RISK_FORCE=1 to force it). Only the standard library is used.
"""
import json, os, sys, time
from datetime import date, datetime, timedelta, timezone

from update_data import get, load, save, DATA
from hub_data import BROWSER

OUT = os.path.join(DATA, 'risk')
ETFS = {
    'SPY': 'SPDR S&P 500 ETF', 'VOO': 'Vanguard S&P 500 ETF', 'IVV': 'iShares Core S&P 500 ETF', 'VTI': 'Vanguard Total Stock Market ETF',
    'QQQ': 'Invesco QQQ (Nasdaq-100)', 'DIA': 'SPDR Dow Jones Industrial Average ETF', 'IWM': 'iShares Russell 2000 ETF',
    'IJR': 'iShares Core S&P Small-Cap ETF', 'IJH': 'iShares Core S&P Mid-Cap ETF', 'AVUV': 'Avantis U.S. Small Cap Value ETF',
    'VEA': 'Vanguard FTSE Developed Markets ETF', 'VWO': 'Vanguard FTSE Emerging Markets ETF', 'VXUS': 'Vanguard Total International Stock ETF',
    'EFA': 'iShares MSCI EAFE ETF', 'VGT': 'Vanguard Information Technology ETF', 'VHT': 'Vanguard Health Care ETF',
    'VDC': 'Vanguard Consumer Staples ETF', 'VNQ': 'Vanguard Real Estate ETF', 'XLE': 'Energy Select Sector SPDR',
    'XLF': 'Financial Select Sector SPDR', 'XLK': 'Technology Select Sector SPDR', 'XLV': 'Health Care Select Sector SPDR',
    'XLU': 'Utilities Select Sector SPDR', 'SMH': 'VanEck Semiconductor ETF', 'SOXX': 'iShares Semiconductor ETF',
    'SCHD': 'Schwab U.S. Dividend Equity ETF', 'VIG': 'Vanguard Dividend Appreciation ETF', 'VYM': 'Vanguard High Dividend Yield ETF',
    'NLR': 'VanEck Uranium and Nuclear ETF', 'URA': 'Global X Uranium ETF', 'GLD': 'SPDR Gold Shares', 'SLV': 'iShares Silver Trust',
    'TLT': 'iShares 20+ Year Treasury Bond ETF', 'IEF': 'iShares 7-10 Year Treasury Bond ETF', 'SHY': 'iShares 1-3 Year Treasury Bond ETF',
    'BIL': 'SPDR 1-3 Month T-Bill ETF', 'BND': 'Vanguard Total Bond Market ETF', 'AGG': 'iShares Core U.S. Aggregate Bond ETF',
    'LQD': 'iShares Investment Grade Corporate Bond ETF', 'HYG': 'iShares High Yield Corporate Bond ETF', 'TIP': 'iShares TIPS Bond ETF',
    'QTUM': 'Defiance Quantum ETF', 'CHAT': 'Roundhill Generative AI & Technology ETF', 'ARKK': 'ARK Innovation ETF',
    'IBIT': 'iShares Bitcoin Trust', 'VT': 'Vanguard Total World Stock ETF', 'SCHG': 'Schwab U.S. Large-Cap Growth ETF',
}


def weekly(sym):
    """[(week date, adjusted close)] for completed weeks over the last five years"""
    ysym = sym.replace('.', '-')
    raw = json.loads(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{ysym}?range=5y&interval=1wk&includeAdjustedClose=true',
                         BROWSER, tries=2, timeout=20))
    r = raw['chart']['result'][0]
    adj = (r.get('indicators', {}).get('adjclose') or [{}])[0].get('adjclose') or r['indicators']['quote'][0]['close']
    today = date.today()
    out = []
    for ts, c in zip(r.get('timestamp') or [], adj):
        if not c:
            continue
        d = datetime.fromtimestamp(ts, timezone.utc).date()
        if d + timedelta(days=4) > today:       # the current week is not finished yet
            continue
        out.append((d.isoformat(), c))
    return out


def run(force=False):
    os.makedirs(OUT, exist_ok=True)
    ip = os.path.join(OUT, 'index.json')
    old = load(ip, {}) if os.path.exists(ip) else {}
    if not force and old.get('updated'):
        age = (date.today() - date.fromisoformat(old['updated'][:10])).days
        if age < 6:
            print(f'  risk data is {age} days old; next refresh in {6 - age} days')
            return 0
    names = dict(ETFS)
    try:
        for t, n, *_ in load(os.path.join(DATA, 'universe.json'), {}).get('companies', []):
            names.setdefault(t, n)
    except Exception as e:
        print(f'  note universe {e}', file=sys.stderr)
    try:
        for c in load(os.path.join(DATA, 'watchlist.json'), {}).get('companies', []):
            if c.get('ticker') and c.get('status') == 'live' and not c.get('private') and c['ticker'].isupper() and len(c['ticker']) <= 5:
                names.setdefault(c['ticker'], c.get('name', c['ticker']))
    except Exception as e:
        print(f'  note watchlist {e}', file=sys.stderr)
    for k in ('ANTHROPIC', 'OPENAI', 'ANDURIL', 'BLOOMBERG'):
        names.pop(k, None)
    spy = weekly('SPY')
    grid = [d for d, _ in spy]
    pos = {d: i for i, d in enumerate(grid)}
    done, fails = {}, []
    for i, t in enumerate(sorted(names)):
        try:
            w = spy if t == 'SPY' else weekly(t)
            px = [None] * len(grid)
            for d, c in w:
                if d in pos:
                    px[pos[d]] = c
            r = [None] * len(grid)
            for k in range(1, len(grid)):
                if px[k] is not None and px[k - 1] is not None and px[k - 1] > 0:
                    r[k] = round(px[k] / px[k - 1] - 1, 5)
            if sum(x is not None for x in r) < 26:
                fails.append(t); continue
            save(os.path.join(OUT, t + '.json'), {'t': t, 'r': r})
            done[t] = names[t]
        except Exception as e:
            fails.append(t)
        if t != 'SPY':
            time.sleep(0.25)
        if i % 100 == 0:
            print(f'  risk {i}/{len(names)}')
    if len(done) < 50:
        print(f'  FAIL risk data: only {len(done)} tickers', file=sys.stderr)
        return 0
    save(ip, {'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'source': 'Yahoo Finance weekly adjusted closes',
              'dates': grid, 'names': dict(sorted(done.items())), 'etfs': sorted(t for t in ETFS if t in done)})
    print(f'  risk data: {len(done)} tickers, {len(grid)} weeks; failed {len(fails)}: {" ".join(fails[:20])}')
    return len(done)


if __name__ == '__main__':
    run(force=True)
