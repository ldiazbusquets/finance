"""Hand-checked formula tests. Each expected number below was worked out by hand (or is a textbook result) and is
written into the test as a literal, so the code is checked against arithmetic, not against itself.

Covers the building blocks every report uses: CAPM and WACC, the growth fade, the DCF (mid-year discounting,
value-driver terminal value, the bridge to a per-share value), the dividend discount model, the bank
excess-return model, the S&P 500 benchmark model, the rating rule, the Monte Carlo draws, and the browser bond
pricer (price, yield, Macaulay and modified duration).

Run: python3 _source/tests/test_formulas.py (or pytest). The build runs it every time.
"""
import contextlib
import io
import json
import math
import os
import random
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
MODELS = os.path.join(SRC, 'models')
ROOT = os.path.dirname(SRC)
sys.path[:0] = [SRC, os.path.join(SRC, 'pages')]


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


def load(script):
    """run a model script quietly and return its namespace (functions and constants)"""
    ns, cwd = {}, os.getcwd()
    os.chdir(MODELS)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(open(script, encoding='utf-8').read(), ns)
    finally:
        os.chdir(cwd)
    return ns


V = load('val_all.py')


# ---------- CAPM and WACC ----------
def test_capm():
    # 5.15% Treasury + beta x 4.5% equity risk premium
    assert close(V['ke'](1.0), .0965)
    assert close(V['ke'](0.8), .0875)        # .0515 + .036
    assert close(V['ke'](0.0), .0515)


def test_wacc():
    # 60/40 equity/debt, beta 0.8 (cost of equity 8.75%), 5% pre-tax debt, 21% tax:
    # .6 x 8.75% + .4 x 5% x .79 = 5.25% + 1.58% = 6.83%
    assert close(V['wacc'](0.8, 60, 40, .05), .0683)
    # no debt: WACC is the cost of equity
    assert close(V['wacc'](1.2, 100, 0, .06), .0515 + 1.2 * .045)


def test_fade():
    g = V['fade']([.10], .03, 10)
    assert len(g) == 10 and close(g[0], .10) and close(g[-1], .03)
    # straight line: 7 points over 9 steps, so year 2 is 10% - 7%/9 = 9.2222%
    assert close(g[1], .10 - .07 / 9)


# ---------- DCF ----------
def test_dcf_two_years_by_hand():
    # revenue 100 grows 10% then 5%; 20% margin, no tax, no reinvestment; WACC 10%; terminal growth 5%;
    # returns on new capital effectively infinite, so the terminal value is next year's cash flow / (W - g).
    #   year 1: revenue 110,   cash flow 22.0,  PV 22.0 / 1.1^0.5 = 20.97618
    #   year 2: revenue 115.5, cash flow 23.1,  PV 23.1 / 1.1^1.5 = 20.02271
    #   terminal: 23.1 x 1.05 / .05 = 485.1, PV 485.1 / 1.1^1.5 = 420.47700
    #   enterprise value 461.47589; +10 net cash = 471.47589 equity; / 10 shares = 47.147589
    r = V['dcf'](100, [.10, .05], [.20], 0.0, lambda t, rev, d: 0.0, .10, .05, 1e12, 10, 10)
    assert close(r['pv'], 20.97618 + 20.02271, 1e-6)
    assert close(r['pvtv'], 420.47700, 1e-6)
    assert close(r['ev'], 461.47589, 1e-6)
    assert close(r['ps'], 47.147589, 1e-6)


def test_dcf_steady_state_is_gordon():
    # constant 3% growth forever, reinvesting g / RONIC of NOPAT: the whole DCF must collapse to the growing
    # perpetuity FCF1 / (W - g), times 1.09^0.5 for mid-year discounting.
    # NOPAT1 = 100 x 1.03 x 20% x 75% = 15.45; reinvestment = 15.45 x 3% / 15% = 3.09; FCF1 = 12.36
    # value = 12.36 / 6% x 1.044031 = 215.0703
    reinv = lambda t, rev, d: rev * .20 * .75 * .03 / .15
    r = V['dcf'](100, [.03] * 10, [.20], .25, reinv, .09, .03, .15, 0, 1)
    assert close(r['rows'][0][7], 12.36, 1e-9)
    assert close(r['ev'], 12.36 / .06 * math.sqrt(1.09), 1e-9)
    assert close(r['ev'], 215.0703, 1e-6)


def test_dcf_bridge_adds_up():
    reinv = lambda t, rev, d: .3 * d
    r = V['dcf'](500, V['fade']([.12, .10]), V['ramp'](.15, .22, 5), .21, reinv, .085, .03, .2, -40, 7)
    assert close(r['ev'], r['pv'] + r['pvtv'])
    assert close(r['eq'], r['ev'] - 40)
    assert close(r['ps'], r['eq'] / 7)


# ---------- dividend discount model (AWK) ----------
def test_ddm_constant_growth():
    awk = load('awk.py')
    # growth 4% in every year and forever: D1 / (k - g) = 1.04 / (9% - 4%) = 20.80
    assert close(awk['ddm'](g=.04, gT=.04, k=.09, d0=1.0), 20.80, 1e-9)
    # $2.00 dividend, 3%, 8%: 2.06 / 5% = 41.20
    assert close(awk['ddm'](g=.03, gT=.03, k=.08, d0=2.0), 41.20, 1e-9)


def test_ddm_two_stage_by_hand():
    awk = load('awk.py')
    # d0 = 1; 10% for 5 years, then fading by 1.3 points a year to 3.5% in year 10; k = 9%
    gs = [.10] * 5 + [.087, .074, .061, .048, .035]
    d, pv = 1.0, 0.0
    for t, g in enumerate(gs, 1):
        d *= 1 + g; pv += d / 1.09 ** t
    want = pv + d * 1.035 / (.09 - .035) / 1.09 ** 10
    assert close(awk['ddm'](g=.10, yrs=5, gT=.035, k=.09, d0=1.0), want, 1e-9)
    # and the same number written out: year-10 dividend 2.16379, PV of dividends 10.08940, PV of terminal 17.19994
    assert close(want, 27.28934, 1e-6)


# ---------- bank excess-return model (JPM) ----------
def test_excess_return():
    jpm = load('jpm.py')
    v = jpm['v']
    # earning exactly the cost of equity, a bank is worth its book value
    assert close(v(jpm['k'], jpm['k']), jpm['BV'])
    # ROE 15%, growth 4.5%, cost of equity 10%: (15 - 4.5) / (10 - 4.5) = 1.909 x book
    assert close(v(.15, .10), (.105 / .055) * jpm['BV'])
    # the implied ROE printed by the script must price the stock exactly
    roe = jpm['G'] + jpm['P'] / jpm['BV'] * (jpm['k'] - jpm['G'])
    assert close(v(roe, jpm['k']), jpm['P'])


# ---------- S&P 500 benchmark ----------
def test_market_model():
    sys.path.insert(0, MODELS)
    import market
    # one growth rate for ever: f0 (1 + g) / (r - g). 100 x 1.03 / (8% - 3%) = 2,060
    assert close(market.value(.08, 100, .03, .03), 2060, 1e-9)
    # implied return inverts the value
    assert close(market.implied_r(100, 2060, .03), .08, 1e-6)


# ---------- rating rule ----------
def test_rating_rule():
    import ratings
    m = ratings.MKT
    # value 100 at price 100 is worth 1 / 0.678 - 1 = 47.5% more than the market's value-to-price: Buy
    call, absolute, rel = ratings.rate(100, 100)
    assert call == 'Buy' and close(absolute, 0) and close(rel, 1 / m - 1)
    # just past each line, and just inside it
    assert ratings.rate(m * 1.1501 * 100, 100)[0] == 'Buy'
    assert ratings.rate(m * .8499 * 100, 100)[0] == 'Sell'
    assert ratings.rate(m * 100, 100)[0] == 'Hold'
    assert ratings.rate(m * 1.149 * 100, 100)[0] == 'Hold' and ratings.rate(m * .851 * 100, 100)[0] == 'Hold'


# ---------- Monte Carlo ----------
def test_split_normal_percentiles():
    sys.path.insert(0, MODELS)
    import montecarlo as mc
    # z = -1.28 gives the bear input, 0 the base, +1.28 the bull; the two sides can have different widths
    assert close(mc.side(10, 6, 20, -mc.Z90), 6) and close(mc.side(10, 6, 20, 0), 10) and close(mc.side(10, 6, 20, mc.Z90), 20)
    rnd = random.Random(1)
    xs = sorted(mc.side(10, 6, 20, rnd.gauss(0, 1)) for _ in range(40000))
    assert abs(xs[4000] - 6) < .15 and abs(xs[20000] - 10) < .1 and abs(xs[36000] - 20) < .35


def test_inputs_correlate_at_rho():
    sys.path.insert(0, MODELS)
    import montecarlo as mc
    a, b = [], []
    for f, rnd, _ in mc.draws(20000, seed=7):
        a.append(math.sqrt(mc.RHO) * f + math.sqrt(1 - mc.RHO) * rnd.gauss(0, 1))
        b.append(math.sqrt(mc.RHO) * f + math.sqrt(1 - mc.RHO) * rnd.gauss(0, 1))
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a) / len(a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b) / len(b))
    assert abs(cov / sa / sb - .6) < .02


def test_mc_stats():
    sys.path.insert(0, MODELS)
    import montecarlo as mc
    s = mc.stats(list(range(1, 101)), 50, .678)
    assert s['mean'] == 50.5 and s['p10'] == 11 and s['p50'] == 51 and s['p90'] == 91
    assert s['p_above_price'] == .5
    assert s['p_cheaper_than_market'] == sum(v / 50 > .678 for v in range(1, 101)) / 100   # 67 of 100


def test_published_means_match_rule():
    # every published rating must follow from the published expected value at the report's price
    import ratings
    mcj = json.load(open(os.path.join(ROOT, 'data', 'models', 'montecarlo.json')))['reports']
    for t, m in mcj.items():
        if m.get('price') and m.get('mean'):
            call, _, rel = ratings.rate(m['mean'], m['price'])
            assert call in ('Buy', 'Hold', 'Sell') and close(rel, m['mean'] / m['price'] / ratings.MKT - 1)


# ---------- bond pricer (assets/bonds.js), run in Node ----------
BOND_JS = r"""
const src = require('fs').readFileSync(process.argv[1], 'utf8');
const a = src.indexOf('/* ---------- bond math'), b = src.indexOf("/* ---------- today's");
eval(src.slice(a, b));
const out = {
  par:  price({c: .05, T: 10, f: 2, F: 1000}, .05),
  six:  price({c: .05, T: 10, f: 2, F: 1000}, .06),
  ytm:  ytm({c: .05, T: 10, f: 2, F: 1000}, 925.6126),
  zero: stats({c: 0, T: 10, f: 1, F: 1000}, .05),
  ann:  stats({c: .10, T: 3, f: 1, F: 1000}, .10)
};
console.log(JSON.stringify({par: out.par, six: out.six, ytm: out.ytm, zp: out.zero.P, zmac: out.zero.mac, zmod: out.zero.mod,
  amac: out.ann.mac, amod: out.ann.mod, adv: out.ann.dv01}));
"""


def test_bond_pricer():
    node = shutil.which('node')
    if not node:
        print('  (node not installed: bond pricer test skipped)')
        return
    r = subprocess.run([node, '-e', BOND_JS, os.path.join(ROOT, 'assets', 'bonds.js')], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert close(o['par'], 1000, 1e-9)                         # coupon = yield: par
    # 5% semi-annual, 10 years, at 6%: 25 x a(20, 3%) + 1000 / 1.03^20 = 371.9369 + 553.6758 = 925.6126
    assert close(o['six'], 925.6126, 1e-6)
    assert abs(o['ytm'] - .06) < 1e-6
    # 10-year zero at 5%: 1000 / 1.05^10 = 613.9133; Macaulay duration 10; modified 10 / 1.05 = 9.5238
    assert close(o['zp'], 613.9133, 1e-6) and close(o['zmac'], 10) and close(o['zmod'], 9.523810, 1e-6)
    # 3-year 10% annual bond at par: PVs 90.909, 82.645, 826.446; Macaulay (90.909 + 2 x 82.645 + 3 x 826.446) / 1000 = 2.7355
    assert close(o['amac'], 2.735537, 1e-6) and close(o['amod'], 2.486852, 1e-6)
    assert close(o['adv'], 2.486852 * 1000 * 1e-4, 1e-6)       # DV01: $0.2487 per $1,000 per basis point


if __name__ == '__main__':
    n = 0
    for k, f in list(globals().items()):
        if k.startswith('test_'):
            f(); n += 1
    print(f'{n} formula tests passed (hand-checked CAPM, WACC, DCF, DDM, excess return, benchmark, rating rule, Monte Carlo, bonds)')
