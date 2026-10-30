"""Ranges instead of three fixed cases.

Every report has a bear, base and bull case. Instead of weighting them 25/50/25, this reruns each report's own
model thousands of times, drawing every input from a range:

  - each input's base-case value is its median; its bear and bull values are its 10th and 90th percentiles
    (a split normal, so the two sides can be different widths);
  - the business inputs (growth, margins, multiples, capex) share a common "how the business goes" factor
    (correlation 0.6), because in practice they move together; the discount rate moves on its own;
  - inputs are kept inside sensible bounds (a discount rate at least 1.5 points above terminal growth, margins
    and multiples not below zero unless the base case is).

The result for each report: the expected (mean) value, the 10th/50th/90th percentile values, the chance the value
exceeds the price, and the chance the stock is cheaper than the S&P 500 on the same assumptions. The draws are
seeded, so every build gives the same numbers. Run: python3 montecarlo.py
"""
import contextlib
import inspect
import io
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
N = 4000
RHO = 0.6          # correlation of the business inputs with their common factor
Z90 = 1.2815516    # bear and bull = 10th and 90th percentiles
SEED = 20261023

# script, function, bear inputs, bull inputs; base inputs are the function's own defaults unless given.
# 'W' entries are offsets added to the base discount rate named in 'wbase' (an expression in the script).
G4 = ('g1', 'g2', 'm0', 'mT')
SPECS = {
    'NVDA': ('nvda', 'nv', G4, (.20, .05, .60, .45), (.55, .25, .65, .60), {'wbase': 'ke(1.58)'}),
    'AMZN': ('amzn', 'am', G4, (.08, .07, .12, .14), (.16, .15, .14, .22), {'heavy': ((190, 150, 110, 70), (150, 110, 70, 40))}),
    'META': ('meta', 'mt', G4, (.10, .08, .30, .30), (.24, .18, .36, .44), {'heavy': ((130, 110, 80, 60), (90, 70, 40, 25))}),
    'VRT': ('vrt', 'vr', G4, (.15, .08, .215, .21), (.40, .22, .24, .275), {}),
    'LHX': ('lhx', 'lh', ('g1', 'g2', 'conv'), (.04, .03, .115), (.10, .09, .15), {}),
    'BA': ('ba', 'ba', ('path',), ((1.5, 1, 3, 5, 7.5),), ((2.5, 4.5, 8, 12, 14),), {}),
    'AWK': ('awk', 'ddm', ('g', 'gT'), (.06, .03), (.09, .04), {'wname': 'k', 'wbase': 'ke(0.70)', 'dw': (.01, -.005)}),
    'GEV': ('gev', 'run', ('g27', 'g28', 'mT'), (.07, .05, .16), (.16, .14, .23), {'wname': 'W', 'wbase': '.107', 'dw': (.008, -.010), 'price': 878.03}),
    'MSFT': ('msft', 'ms', G4, (.12, .10, .42, .40), (.21, .18, .47, .48), {'heavy': ((200, 170, 130, 90), (160, 110, 70, 40))}),
    'GOOGL': ('googl', 'gg', G4, (.09, .07, .31, .30), (.19, .17, .36, .38), {'heavy': ((180, 150, 110, 80), (130, 100, 70, 40))}),
    'TSM': ('tsm', 'ts', G4, (.12, .08, .52, .48), (.32, .25, .59, .57), {}),
    'ASML': ('asml', 'asm', G4, (.08, .05, .36, .36), (.30, .20, .43, .47), {}),
    'LMT': ('lmt', 'lm', G4, (.04, .03, .10, .105), (.09, .08, .12, .13), {}),
    'NOC': ('noc', 'nc', G4, (.03, .03, .105, .105), (.08, .09, .118, .13), {}),
    'CAT': ('cat', 'ct', G4, (.0, .02, .17, .17), (.12, .10, .215, .23), {}),
    'AVGO': ('avgo', 'av', G4, (.30, .0, .48, .45), (.60, .45, .57, .53), {}),
    'RTX': ('rtx', 'rt', G4, (.04, .04, .115, .12), (.10, .09, .13, .155), {}),
    'GD': ('gd', 'gd', G4, (.04, .03, .10, .10), (.09, .08, .11, .12), {}),
    'CEG': ('ceg', 'cg', G4, (.02, .03, .15, .15), (.08, .10, .17, .23), {'heavy': ((3, 3, 2.5, 2.5), (2.5, 2.5, 2, 2))}),
    'UNH': ('unh', 'uh', G4, (.02, .04, .05, .055), (.06, .09, .06, .08), {}),
    'XOM': ('xom', 'xm', G4, (-.15, .0, .11, .10), (.03, .02, .14, .14), {}),
    'V': ('v', 'vi', G4, (.07, .06, .60, .58), (.13, .12, .63, .66), {}),
    'JNJ': ('jnj', 'jj', G4, (.02, .03, .28, .28), (.07, .08, .32, .34), {}),
}
SCEN = ['SPCX', 'FLY', 'KTOS', 'AXON', 'PLTR', 'AMD']          # 2030 scenario model (new_coverage.val)
CYCLE = ['MU', 'SNDK', 'SKHY']                                   # memory-cycle model (new_coverage.cyc)


def run_script(name):
    ns = {}
    cwd = os.getcwd()
    os.chdir(HERE)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(open(name + '.py').read(), ns)
    finally:
        os.chdir(cwd)
    return ns


def side(base, bear, bull, z):
    """split normal: z = -1.28 gives bear, 0 base, +1.28 bull, extended smoothly beyond"""
    if isinstance(base, (tuple, list)):
        return type(base)(side(b, x, y, z) for b, x, y in zip(base, bear, bull))
    if isinstance(base, str) or base is None:
        return base
    return base + z * ((base - bear) if z < 0 else (bull - base)) / Z90


def clip_like(v, base):
    """keep a drawn input on the same side of zero as its base value (margins, multiples, revenue, shares)"""
    if isinstance(v, (tuple, list)):
        return type(v)(clip_like(a, b) for a, b in zip(v, base))
    if isinstance(v, (int, float)) and isinstance(base, (int, float)) and base > 0 and v < 0:
        return 0.0
    return v


def num(x):
    return x['ps'] if isinstance(x, dict) else x


def draws(n=N, seed=SEED):
    rnd = random.Random(seed)
    for _ in range(n):
        f = rnd.gauss(0, 1)
        yield f, rnd, rnd.gauss(0, 1)


def stats(vals, price, mkt):
    vals = sorted(v for v in vals if v == v and abs(v) != float('inf'))
    n = len(vals)
    q = lambda p: vals[min(n - 1, max(0, int(p * n)))]
    mean = sum(vals) / n
    out = {'n': n, 'mean': mean, 'p10': q(.10), 'p50': q(.50), 'p90': q(.90)}
    if price:
        out['p_above_price'] = sum(v > price for v in vals) / n
        out['p_cheaper_than_market'] = sum(v / price > mkt for v in vals) / n
    return out


def simulate_spec(key):
    script, fn, names, bear, bull, extra = SPECS[key]
    ns = run_script(script)
    f = ns[fn]
    sig = inspect.signature(f)
    base = [sig.parameters[k].default for k in names]
    wname = extra.get('wname', 'W')
    wbase = eval(extra['wbase'], ns) if 'wbase' in extra else ns['W0']
    dw = extra.get('dw', (.01, -.01))
    hv = extra.get('heavy')
    hbase = sig.parameters['heavy'].default if hv else None
    gT = sig.parameters['gT'].default if 'gT' in sig.parameters and 'gT' not in names else .03
    vals = []
    for fz, rnd, wz in draws():
        kw = {}
        for k, b0, x, y in zip(names, base, bear, bull):
            z = math.sqrt(RHO) * fz + math.sqrt(1 - RHO) * rnd.gauss(0, 1)
            kw[k] = side(b0, x, y, z) if not isinstance(b0, (int, float)) or k.startswith('g') else clip_like(side(b0, x, y, z), b0)
        if hv:
            z = math.sqrt(RHO) * fz + math.sqrt(1 - RHO) * rnd.gauss(0, 1)
            kw['heavy'] = tuple(max(0, v) for v in side(hbase, hv[0], hv[1], z))
        w = side(wbase, wbase + dw[0], wbase + dw[1], wz)
        g_term = kw.get('gT', gT)
        kw[wname] = max(w, g_term + .015, .05)
        try:
            vals.append(num(f(**kw)))
        except (ZeroDivisionError, OverflowError, ValueError):
            pass
    base_val = num(f())
    return extra.get('price') or ns.get('P'), vals, base_val


def simulate_jpm():
    ns = run_script('jpm')
    v, k = ns['v'], ns['k']
    vals = []
    for fz, rnd, wz in draws():
        roe = side(.16, .145, .18, fz)
        kk = max(side(k, k + .005, k - .005, wz), ns['G'] + .015)
        vals.append(v(roe, kk))
    return ns['P'], vals, v(.16, k)


def simulate_cases(key, fn, cases, unit=1):
    vals = []
    for fz, rnd, wz in draws():
        z_each = lambda: math.sqrt(RHO) * fz + math.sqrt(1 - RHO) * rnd.gauss(0, 1)
        args = []
        for i, (b, x, y) in enumerate(zip(cases['base'], cases['bear'], cases['bull'])):
            if isinstance(b, str) or b is None:
                args.append(b)
            elif b == x == y:
                args.append(b)
            elif fn.__name__ == 'val' and i == 3 or fn.__name__ == 'cyc' and i == 5:   # discount rate: its own factor
                args.append(side(b, x, y, wz))
            else:
                args.append(clip_like(side(b, x, y, z_each()), b))
        try:
            vals.append(fn(*args) / unit)
        except (ZeroDivisionError, OverflowError, ValueError):
            pass
    return vals, fn(*cases['base']) / unit


def _plain(v):
    if isinstance(v, (tuple, list)):
        return [_plain(x) for x in v]
    return round(v, 6) if isinstance(v, float) else v


def inputs_spec(key):
    """the ranges this report's simulation draws from: (input, bear = 10th pct, base = median, bull = 90th pct)"""
    script, fn, names, bear, bull, extra = SPECS[key]
    ns = run_script(script)
    sig = inspect.signature(ns[fn])
    rows = [[k, _plain(x), _plain(sig.parameters[k].default), _plain(y)] for k, x, y in zip(names, bear, bull)]
    if extra.get('heavy'):
        rows.append(['heavy', _plain(extra['heavy'][0]), _plain(sig.parameters['heavy'].default), _plain(extra['heavy'][1])])
    wbase = eval(extra['wbase'], ns) if 'wbase' in extra else ns['W0']
    dw = extra.get('dw', (.01, -.01))
    rows.append(['W', _plain(wbase + dw[0]), _plain(wbase), _plain(wbase + dw[1])])
    return rows


def inputs_cases(fn, cases):
    names = list(inspect.signature(fn).parameters)
    rows = []
    for k, x, b, y in zip(names, cases['bear'], cases['base'], cases['bull']):
        if isinstance(b, str) or b is None or b == x == y:
            continue
        rows.append([k, _plain(x), _plain(b), _plain(y)])
    return rows


def run_all(mkt=None):
    if mkt is None:
        mkt = json.load(open(os.path.join(HERE, '..', '..', 'data', 'models', 'market.json')))['scenarios']['0.08']['value_to_price']
    out = {}
    for key in SPECS:
        price, vals, b = simulate_spec(key)
        out[key] = dict(stats(vals, price, mkt), base=b, price=price, inputs=inputs_spec(key))
    price, vals, b = simulate_jpm()
    jk = run_script('jpm')['k']
    out['JPM'] = dict(stats(vals, price, mkt), base=b, price=price, inputs=[['roe', .145, .16, .18], ['ke', _plain(jk + .005), _plain(jk), _plain(jk - .005)]])
    nc = run_script('new_coverage')
    prices = {'SPCX': 162.57, 'FLY': 17.41, 'KTOS': 38.81, 'AXON': 396.30, 'PLTR': 201.72, 'AMD': 552.72, 'MU': 913.67, 'SNDK': 1378.22, 'SKHY': 131.69}
    for key in SCEN:
        vals, b = simulate_cases(key, nc['val'], nc['REG'][key])
        out[key] = dict(stats(vals, prices[key], mkt), base=b, price=prices[key], inputs=inputs_cases(nc['val'], nc['REG'][key]))
    for key in CYCLE:
        vals, b = simulate_cases(key, nc['cyc'], nc[key])
        out[key] = dict(stats(vals, prices[key], mkt), base=b, price=prices[key], inputs=inputs_cases(nc['cyc'], nc[key]))
    for key, name in (('ANTHROPIC', 'Anthropic'), ('OPENAI', 'OpenAI'), ('ANDURIL', 'Anduril'), ('BLOOMBERG', 'Bloomberg')):
        vals, b = simulate_cases(key, nc['val'], nc['REG'][name], unit=1e9)
        out[key] = dict(stats(vals, None, mkt), base=b, price=None, inputs=inputs_cases(nc['val'], nc['REG'][name]))
    return out


OUT = os.path.join(HERE, '..', '..', 'data', 'models', 'montecarlo.json')


def write():
    res = run_all()
    meta = {'draws': N, 'seed': SEED, 'correlation': RHO, 'percentiles': 'bear = 10th, base = median, bull = 90th'}
    with open(OUT, 'w') as f:
        json.dump({'method': meta, 'reports': {k: {a: (round(b, 4) if isinstance(b, float) else b) for a, b in r.items()} for k, r in res.items()}}, f, indent=1)
    return res


if __name__ == '__main__':
    res = run_all()
    for k, r in res.items():
        pa = f"P(>price) {r['p_above_price']:.0%}  P(cheaper than mkt) {r['p_cheaper_than_market']:.0%}" if r.get('price') else ''
        print(f"{k:10} base {r['base']:8.1f}  mean {r['mean']:8.1f}  p10 {r['p10']:8.1f}  p50 {r['p50']:8.1f}  p90 {r['p90']:8.1f}  {pa}")
