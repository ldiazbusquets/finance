"""Calibration: what our own assumptions say about the S&P 500 as a whole.

If the method that values single stocks also finds the whole index far below its price, part of every
stock's gap is the method, not the stock. Ratings therefore compare each stock with the index on the same
assumptions (see pages/rep.py, MKT). Run:  python3 market.py   (writes ../../data/models/market.json)"""
import json, os, glob
HERE = os.path.dirname(os.path.abspath(__file__))
CO = os.path.join(HERE, '..', '..', 'data', 'co')
RF, ERP = .0515, .045            # the same 10-year Treasury yield and equity premium every report uses
KE = RF + ERP                    # cost of equity for the market (beta 1)


def aggregate():
    P = json.load(open(os.path.join(CO, 'prices.json')))['px']
    n = mc = ni = fcf = 0
    for f in glob.glob(os.path.join(CO, '*.json')):
        t = os.path.basename(f)[:-5]
        if t not in P:
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict) or 'f' not in d:
            continue
        q = (d.get('q') or {}).get('ttm') or {}
        sh, p = d.get('sh'), P[t].get('p')
        if not sh or not p or not q.get('ni'):
            continue
        n += 1; mc += sh * p; ni += q['ni']; fcf += (q.get('cfo') or 0) - (q.get('capex') or 0)
    return n, mc, ni, fcf


def value(r, f0, g1, gT=.03):
    """two-stage: g1 for five years, fading to gT by year ten, then a growing perpetuity"""
    gs = [g1] * 5 + [g1 + (gT - g1) * i / 5 for i in range(1, 6)]
    f = f0; tot = 0
    for t, g in enumerate(gs, 1):
        f *= 1 + g; tot += f / (1 + r) ** t
    return tot + f * (1 + gT) / (r - gT) / (1 + r) ** 10


def implied_r(f0, mc, g1):
    lo, hi = .031, .4
    for _ in range(80):
        m = (lo + hi) / 2
        if value(m, f0, g1) > mc: lo = m
        else: hi = m
    return m


def main():
    n, mc, ni, fcf = aggregate()
    out = {'companies': n, 'market_value': mc, 'net_income': ni, 'free_cash_flow': fcf, 'cost_of_equity': KE,
           'scenarios': {}}
    for g in (.06, .08, .10):
        v = value(KE, fcf, g)
        out['scenarios'][f'{g:.2f}'] = {'value_to_price': v / mc, 'implied_cost_of_equity': implied_r(fcf, mc, g), 'implied_premium': implied_r(fcf, mc, g) - RF}
    os.makedirs(os.path.join(HERE, '..', '..', 'data', 'models'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, '..', '..', 'data', 'models', 'market.json'), 'w'), indent=1)
    print(f"{n} companies, ${mc / 1e12:.1f}T market value, ${fcf / 1e9:,.0f}B free cash flow ({fcf / mc:.2%} yield), P/E {mc / ni:.1f}")
    for g, s in out['scenarios'].items():
        print(f"  growth {g}: value/price {s['value_to_price']:.3f}, implied cost of equity {s['implied_cost_of_equity']:.2%}, implied premium {s['implied_premium']:.2%}")
    return out


if __name__ == '__main__':
    main()
