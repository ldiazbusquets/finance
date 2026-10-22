"""Writes a CSV for every report's valuation: inputs, the year-by-year projection, the bridge to a value
per share, the scenarios and the sensitivity table. Each file is rebuilt by running the same model script
that produced the report, so the CSV and the report cannot drift apart.

Run from this folder:  python3 export.py   (files go to ../../data/models/<page>.csv)
Then  python3 export.py --check  confirms every report still shows the values its model produces."""
import csv, io, os, sys, contextlib, json
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'data', 'models')
sys.path.insert(0, os.path.join(HERE, '..', 'pages'))


def run(name):
    ns = {}
    with contextlib.redirect_stdout(io.StringIO()), cwd(HERE):
        exec(open(os.path.join(HERE, name + '.py')).read(), ns)
    return ns


@contextlib.contextmanager
def cwd(p):
    old = os.getcwd(); os.chdir(p)
    try:
        yield
    finally:
        os.chdir(old)


B = lambda x: round(x / 1e9, 3)            # dollars to $ billions
P = lambda x: round(x * 100, 2)            # rate to percent


def write(slug, title, method, inputs, head, rows, bridge, scen, sens, note):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, slug + '.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow([f'LDB Finance: {title}']); w.writerow([f'Method: {method}'])
        w.writerow(['Money in US$ billions unless marked; rates in percent. Reproduce with the model script named below.'])
        w.writerow([note]); w.writerow([])
        w.writerow(['INPUTS', 'Value', 'Basis']); [w.writerow(r) for r in inputs]; w.writerow([])
        if rows:
            w.writerow(['PROJECTION (base case)']); w.writerow(head); [w.writerow(r) for r in rows]; w.writerow([])
        w.writerow(['BRIDGE (base case)', 'Value']); [w.writerow(r) for r in bridge]; w.writerow([])
        w.writerow(['SCENARIOS', 'Bear', 'Base', 'Bull']); [w.writerow(r) for r in scen]; w.writerow([])
        if sens:
            w.writerow(['SENSITIVITY', 'Input', 'Value per share']); [w.writerow(['', a, b]) for a, b in sens]


def dcf_rows(d, W):
    return [[2026 + r[0], P(r[1]), B(r[2]), P(r[3]), B(r[4]), B(r[5]), B(r[6]), B(r[7]), round(1 / (1 + W) ** (r[0] - .5), 4), B(r[7] / (1 + W) ** (r[0] - .5))] for r in d['rows']]


DCF_HEAD = ['Year', 'Revenue growth %', 'Revenue', 'Operating margin %', 'Operating income', 'After-tax operating income', 'Reinvestment', 'Free cash flow to the firm', 'Discount factor (mid-year)', 'Present value']


def wsum(bear, base, bull):
    return .25 * bear + .5 * base + .25 * bull


def generic_dcf(key, slug, title, fn, args_bear, args_bull, rev0, tax, gT, ronic, net, sens_W, inputs_extra, script):
    ns = run(script); f = ns[fn]; W0 = ns.get('W0') or ns['ke'](1.58)
    d = f(); bear, bull = ns['bear'], ns['bull']    # exactly the scripts' bear and bull cases (they also move the discount rate)
    inputs = [['Base revenue (latest year)', B(rev0), 'Company filings and guidance'], ['Tax rate %', P(tax), 'Effective rate'],
              ['Discount rate (WACC) %', P(W0), 'CAPM: 5.15% 10-year Treasury + beta x 4.5% equity risk premium, blended with after-tax debt'],
              ['Terminal growth %', P(gT), 'Long-run nominal growth'], ['Return on new capital in the terminal value %', P(ronic), 'Sets reinvestment after year 10'],
              ['Net cash (negative = net debt)', B(net), 'Latest balance sheet'], ['Diluted shares (billions)', round(ns['SH'] / 1e9, 4), 'Latest filing']] + inputs_extra
    n11 = d['rows'][-1][4] * (1 + gT) * (1 - tax)
    bridge = [['Present value of 10 years of cash flow', B(d['pv'])], ['Year-11 after-tax operating income', B(n11)],
              ['Terminal value = NOPAT11 x (1 - g/RONIC) / (WACC - g)', B(n11 * (1 - gT / ronic) / (W0 - gT))], ['Present value of terminal value', B(d['pvtv'])],
              ['Enterprise value', B(d['ev'])], ['Plus net cash', B(net)], ['Equity value', B(d['eq'])], ['Value per share ($)', round(d['ps'], 2)]]
    scen = [['Value per share ($)', round(bear, 2), round(d['ps'], 2), round(bull, 2)], ['Probability', 25, 50, 25], ['Probability-weighted value ($)', '', round(wsum(bear, d['ps'], bull), 2), '']]
    sens = [(f'Discount rate {P(Wx)}%', round(f(W=Wx)['ps'], 2)) for Wx in sens_W]
    write(slug, title, 'Ten-year discounted cash flow (free cash flow to the firm)', inputs, DCF_HEAD, dcf_rows(d, W0), bridge, scen, sens,
          f'Model script: _source/models/{script}.py')
    return d['ps'], bear, bull


def main():
    vals = {}
    # Amazon, Meta, Nvidia and Vertiv share the same cash-flow engine
    vals['AMZN'] = generic_dcf('AMZN', 'amazon', 'Amazon (AMZN)', 'am', ((.08, .07, .12, .14), {'W': None, 'heavy': (150, 120, 90, 60)}), ((.15, .14, .14, .22), {'heavy': (110, 80, 50, 30)}),
                               810e9, .19, .03, .20, -10e9, [.085, .09, .095, .10], [['Revenue growth, years 1-2 %', '12 / 11', 'Then fades to 3% by year 10'], ['Operating margin %', '13 rising to 18 by year 5', ''], ['Heavy AI capex, years 1-4 ($B)', '130 / 100 / 70 / 50', 'Then reinvestment = revenue growth / 2.0']], 'amzn')
    vals['META'] = generic_dcf('META', 'meta', 'Meta Platforms (META)', 'mt', ((.10, .08, .30, .30), {'heavy': (130, 110, 80, 60)}), ((.24, .18, .36, .44), {'heavy': (90, 70, 40, 25)}),
                               256e9, .16, .03, .25, 1.5e9, [.085, .09, .095, .10], [['Revenue growth, years 1-2 %', '18 / 14', 'Then fades to 3% by year 10'], ['Operating margin %', '34 rising to 38 by year 5', ''], ['Heavy AI capex, years 1-4 ($B)', '110 / 90 / 60 / 40', 'Then reinvestment = revenue growth / 2.0']], 'meta')
    vals['VRT'] = generic_dcf('VRT', 'vertiv', 'Vertiv (VRT)', 'vr', ((.12, .08, .21, .21), {}), ((.35, .22, .235, .27), {}),
                              14.0e9, .21, .03, .25, -0.13e9, [.09, .10, .11, .12], [['Revenue growth, years 1-2 %', '25 / 16', 'Then fades to 3% by year 10'], ['Operating margin %', '22.5 rising to 24.5 by year 3', ''], ['Sales to capital', 3, 'Reinvestment = revenue growth / 3']], 'vrt')
    # the bear and bull cases also move the discount rate by a point: rebuild them exactly as the scripts do
    for key, script, fn in (('AMZN', 'amzn', 'am'), ('META', 'meta', 'mt'), ('VRT', 'vrt', 'vr')):
        ns = run(script); vals[key] = (ns['b'], ns['bear'], ns['bull'])
    ns = run('nvda'); nv = ns['nv']; W0 = ns['ke'](1.58)
    with contextlib.redirect_stdout(io.StringIO()):
        d = ns['dcf'](404e9, ns['fade']([.40, .15]), ns['ramp'](.63, .55, 7), .17, lambda t, r, dd: dd / 2.5, W0, .03, .25, 0, ns['SH'])
    n11 = d['rows'][-1][4] * 1.03 * .83
    write('nvidia', 'Nvidia (NVDA)', 'Ten-year discounted cash flow (free cash flow to the firm)',
          [['Base revenue (fiscal 2027 run-rate)', 404, 'Company filings and guidance'], ['Tax rate %', 17, ''], ['Discount rate %', P(W0), 'CAPM cost of equity, beta 1.58 (no meaningful debt)'],
           ['Terminal growth %', 3, ''], ['Return on new capital %', 25, ''], ['Net cash', 0, ''], ['Diluted shares (billions)', 24.3, ''],
           ['Revenue growth, years 1-2 %', '40 / 15', 'Then fades to 3% by year 10'], ['Operating margin %', '63 easing to 55 by year 7', ''], ['Sales to capital', 2.5, 'Reinvestment = revenue growth / 2.5']],
          DCF_HEAD, dcf_rows(d, W0),
          [['Present value of 10 years of cash flow', B(d['pv'])], ['Terminal value = NOPAT11 x (1 - g/RONIC) / (r - g)', B(n11 * (1 - .03 / .25) / (W0 - .03))], ['Present value of terminal value', B(d['pvtv'])], ['Enterprise value', B(d['ev'])], ['Equity value', B(d['eq'])], ['Value per share ($)', round(d['ps'], 2)]],
          [['Value per share ($)', round(ns['bear'], 2), round(ns['b'], 2), round(ns['bull'], 2)], ['Probability', 25, 50, 25], ['Probability-weighted value ($)', '', round(wsum(ns['bear'], ns['b'], ns['bull']), 2), '']],
          [(f'Discount rate {P(Wx)}%', round(nv(W=Wx), 2)) for Wx in (.09, .10, .11, W0)], 'Model script: _source/models/nvda.py')
    vals['NVDA'] = (ns['b'], ns['bear'], ns['bull'])
    # L3Harris: free cash flow to the firm from guidance
    ns = run('lhx'); lh = ns['lh']; b = lh(); L = dict(ns['LAST'])
    rows = [[2026 + r[0], P(r[1]), B(r[2]), B(r[3]), round(1 / (1 + L['W']) ** (r[0] - .5), 4), B(r[3] / (1 + L['W']) ** (r[0] - .5))] for r in L['rows']]
    write('l3harris', 'L3Harris (LHX)', 'Ten-year discounted free cash flow to the firm, following the 2028 framework',
          [['Revenue, 2026 (guidance midpoint)', 23.45, 'Company guidance'], ['Growth, 2027 and 2028 %', '7.5 / 7.5', 'Reaches the $27B 2028 target; fades to 3% by year 10'],
           ['Cash flow to the firm', '$3.65B, $3.95B, then 14.6% of revenue', 'Free cash flow guidance plus after-tax interest'], ['Discount rate (WACC) %', P(L['W']), 'Beta 0.80 (defense peers), about 19% debt'],
           ['Terminal growth %', 3, ''], ['Net debt and preferred', -10.5, '$9.5B net debt + $1.0B Pentagon preferred'], ['Diluted shares (billions)', 0.1873, '']],
          ['Year', 'Revenue growth %', 'Revenue', 'Free cash flow to the firm', 'Discount factor (mid-year)', 'Present value'], rows,
          [['Present value of 10 years of cash flow', B(L['pv'])], ['Terminal value = FCFF10 x (1+g) / (WACC - g)', B(L['tv'])], ['Present value of terminal value', B(L['pvtv'])], ['Enterprise value', B(L['ev'])], ['Less net debt and preferred', -10.5], ['Equity value', B(L['eq'])], ['Value per share ($)', round(b, 2)]],
          [['Value per share ($)', round(ns['bear'], 2), round(b, 2), round(ns['bull'], 2)], ['Probability', 25, 50, 25], ['Probability-weighted value ($)', '', round(wsum(ns['bear'], b, ns['bull']), 2), '']],
          [(f'Discount rate {P(Wx)}%', round(lh(W=Wx), 2)) for Wx in (.07, .075, .08, .085, .09)], 'Model script: _source/models/lhx.py')
    vals['LHX'] = (b, ns['bear'], ns['bull'])
    # Boeing: free cash flow path back to normal
    ns = run('ba'); ba = ns['ba']; b = ba(); L = dict(ns['LAST'])
    rows = [[2026 + t, B(x), round(1 / (1 + L['W']) ** (t - .5), 4), B(x / (1 + L['W']) ** (t - .5))] for t, x in enumerate(L['flows'], 1)]
    write('boeing', 'Boeing (BA)', 'Ten-year discounted free cash flow to the firm as production recovers',
          [['Free cash flow path, years 1-5 ($B)', '2 / 6 / 9 / 10.5 / 11.5', 'Plus about $2B of after-tax interest to reach cash flow to the firm'], ['Growth, years 6-10 %', '6 fading to 3', ''],
           ['Discount rate (WACC) %', P(L['W']), 'CAPM beta 1.35 with $45.6B of debt'], ['Terminal growth %', 3, ''], ['Net debt', -25.6, 'Latest balance sheet'], ['Diluted shares (billions)', 0.7906, '']],
          ['Year', 'Free cash flow to the firm', 'Discount factor (mid-year)', 'Present value'], rows,
          [['Present value of 10 years of cash flow', B(L['pv'])], ['Terminal value = FCFF10 x (1+g) / (WACC - g)', B(L['tv'])], ['Present value of terminal value', B(L['pvtv'])], ['Enterprise value', B(L['ev'])], ['Less net debt', -25.6], ['Equity value', B(L['eq'])], ['Value per share ($)', round(b, 2)]],
          [['Value per share ($)', round(ns['bear'], 2), round(b, 2), round(ns['bull'], 2)], ['Probability', 25, 50, 25], ['Probability-weighted value ($)', '', round(wsum(ns['bear'], b, ns['bull']), 2), '']],
          [(f'Discount rate {P(Wx)}%', round(ba(W=Wx), 2)) for Wx in (.08, .085, .09, .095)], 'Model script: _source/models/ba.py')
    vals['BA'] = (b, ns['bear'], ns['bull'])
    # GE Vernova
    ns = run('gev'); g = ns['run']; b = g(); L = dict(ns['LAST'])
    rows = [[r[0], P(r[1]), B(r[2]), P(r[3]), B(r[4]), B(r[5]), B(r[6]), B(r[7]), round(1 / (1 + L['W']) ** (i + .5), 4), B(r[7] / (1 + L['W']) ** (i + .5))] for i, r in enumerate(L['rows'])]
    write('gev', 'GE Vernova (GEV)', 'Ten-year discounted cash flow on the company’s 2028 targets',
          [['Revenue, 2026', 46.0, 'Guidance'], ['Growth, 2027 and 2028 %', '12 / 10', 'Then fades to 3% by 2036'], ['EBITDA margin %', '13 in 2026, 20 by 2028', 'Company 2028 target'], ['Depreciation % of revenue', 2.2, ''],
           ['Sales to capital', 4, 'Reinvestment = revenue growth / 4'], ['Tax rate %', 21, ''], ['Discount rate %', 10.7, 'CAPM with beta about 1.2; no net debt'], ['Terminal growth %', 3, ''], ['Return on new capital %', 20, ''],
           ['Net cash', B(L['net']), 'Jun 30 2026: $13.12B cash less $2.85B debt'], ['Diluted shares (billions)', 0.2663, '']],
          ['Year', 'Revenue growth %', 'Revenue', 'EBITDA margin %', 'Operating income', 'After-tax operating income', 'Reinvestment', 'Free cash flow to the firm', 'Discount factor (mid-year)', 'Present value'], rows,
          [['Present value of 10 years of cash flow', B(L['pv'])], ['Present value of terminal value', B(L['pvtv'])], ['Enterprise value', B(L['ev'])], ['Plus net cash', B(L['net'])], ['Equity value', B(L['eq'])], ['Value per share ($)', round(b, 2)]],
          [['Value per share ($)', round(ns['bear'], 2), round(b, 2), round(ns['bull'], 2)], ['Probability', 25, 50, 25], ['Probability-weighted value ($)', '', round(wsum(ns['bear'], b, ns['bull']), 2), '']],
          [(f'Discount rate {P(Wx)}%', round(g(W=Wx), 2)) for Wx in (.085, .09, .095, .10, .107)], 'Model script: _source/models/gev.py')
    vals['GEV'] = (b, ns['bear'], ns['bull'])
    # American Water: dividend discount
    ns = run('awk'); dd = ns['ddm']; b = dd(); L = dict(ns['LAST']); d = L['d0']; rows = []
    for t, gg in enumerate(L['gs'], 1):
        d *= 1 + gg; rows.append([2026 + t, P(gg), round(d, 4), round(1 / (1 + L['k']) ** t, 4), round(d / (1 + L['k']) ** t, 4)])
    write('american-water', 'American Water Works (AWK)', 'Dividend discount model',
          [['Dividend, last 12 months ($)', 3.58, 'Company filings'], ['Dividend growth, years 1-5 %', 8, 'Company 7-9% EPS and dividend target'], ['Growth fades to, by year 10 %', 3.5, 'Long-run'],
           ['Cost of equity %', P(L['k']), 'CAPM: beta 0.70']],
          ['Year', 'Dividend growth %', 'Dividend per share ($)', 'Discount factor', 'Present value ($)'], rows,
          [['Present value of 10 years of dividends ($)', round(L['pv'], 2)], ['Terminal value = D10 x (1+g) / (k - g) ($)', round(L['tv'], 2)], ['Present value of terminal value ($)', round(L['pvtv'], 2)], ['Value per share ($)', round(b, 2)]],
          [['Value per share ($)', round(ns['bear'], 2), round(b, 2), round(ns['bull'], 2)], ['Probability', 25, 50, 25], ['Probability-weighted value ($)', '', round(wsum(ns['bear'], b, ns['bull']), 2), '']],
          [(f'Cost of equity {P(k)}%', round(dd(k=k), 2)) for k in (.07, .075, .08, .085, .09)], 'Model script: _source/models/awk.py')
    vals['AWK'] = (b, ns['bear'], ns['bull'])
    # JPMorgan: excess return on book value
    ns = run('jpm'); k = ns['k']
    write('jpmorgan', 'JPMorgan Chase (JPM)', 'Excess-return model: value = book value x (ROE - g) / (cost of equity - g)',
          [['Book value per share ($)', 132.30, 'Latest 10-Q'], ['Return on equity, through the cycle %', 16, 'Company target range'], ['Growth %', 4.5, ''], ['Cost of equity %', P(k), 'CAPM: beta 1.046']], None, None,
          [['Book value per share ($)', 132.30], ['(ROE - g) / (cost of equity - g)', round((.16 - .045) / (k - .045), 4)], ['Value per share ($)', round(ns['b'], 2)]],
          [['Return on equity %', 14.5, 16, 18], ['Cost of equity %', P(k + .005), P(k), P(k - .005)], ['Value per share ($)', round(ns['bear'], 2), round(ns['b'], 2), round(ns['bull'], 2)], ['Probability', 25, 50, 25], ['Probability-weighted value ($)', '', round(wsum(ns['bear'], ns['b'], ns['bull']), 2), '']],
          [(f'Cost of equity {P(kk)}%', round(ns['v'](.16, kk), 2)) for kk in (.09, .095, .10)], 'Model script: _source/models/jpm.py')
    vals['JPM'] = (ns['b'], ns['bear'], ns['bull'])
    # scenario models: SpaceX, Firefly, Kratos, Axon and the private companies
    ns = run('new_coverage'); val = ns['val']
    SC = {'SPCX': ('spacex', 'SpaceX (SPCX)', (250e9, .22, 20, .12, 4, 51.1e9, 13.57e9), (500e9, .28, 22, .12, 4, 51.1e9, 13.57e9), (900e9, .32, 25, .12, 4, 51.1e9, 13.57e9), 'pe', 1),
          'FLY': ('firefly', 'Firefly Aerospace (FLY)', (0.7e9, 0, 2, .15, 4, 0, 200e6, 'ps'), (1.2e9, 0, 5, .15, 4, .2e9, 185e6, 'ps'), (2.0e9, 0, 8, .15, 4, .2e9, 180e6, 'ps'), 'ps', 1),
          'KTOS': ('kratos', 'Kratos Defense (KTOS)', (2.6e9, .06, 18, .10, 4, 1.2e9, 200e6), (3.2e9, .09, 22, .10, 4, 1.2e9, 200e6), (4.0e9, .12, 28, .10, 4, 1.2e9, 200e6), 'pe', 1),
          'AXON': ('axon', 'Axon Enterprise (AXON)', (6.5e9, .15, 25, .11, 4, -1.1e9, 88e6), (8.5e9, .20, 30, .11, 4, -1.1e9, 88e6), (10.5e9, .25, 35, .11, 4, -1.1e9, 88e6), 'pe', 1),
          'PLTR': ('palantir', 'Palantir Technologies (PLTR)', (18e9, .40, 25, .14, 4, 9.4e9, 2.6e9), (28e9, .50, 30, .14, 4, 9.4e9, 2.6e9), (45e9, .55, 45, .14, 4, 9.4e9, 2.6e9), 'pe', 1),
          'AMD': ('amd', 'Advanced Micro Devices (AMD)', (100e9, .22, 20, .12, 4, 9.9e9, 1.80e9), (150e9, .30, 25, .12, 4, 9.9e9, 1.80e9), (200e9, .35, 30, .12, 4, 9.9e9, 1.80e9), 'pe', 1),
          'ANTHROPIC': ('anthropic', 'Anthropic (private)', (120e9, .15, 20, .15, 4, 0, 1), (250e9, .30, 25, .15, 4, 0, 1), (450e9, .40, 25, .15, 4, 0, 1), 'pe', 1e9),
          'OPENAI': ('openai', 'OpenAI (private)', (150e9, .10, 20, .15, 4, 0, 1), (280e9, .25, 25, .15, 4, 0, 1), (450e9, .35, 25, .15, 4, 0, 1), 'pe', 1e9),
          'ANDURIL': ('anduril', 'Anduril (private)', (8e9, .05, 20, .13, 4, 0, 1), (14e9, .12, 25, .13, 4, 0, 1), (22e9, .18, 35, .13, 4, 0, 1), 'pe', 1e9),
          'BLOOMBERG': ('bloomberg', 'Bloomberg LP (private)', (16e9, .22, 18, .09, 4, 0, 1), (18e9, .28, 22, .09, 4, 0, 1), (20e9, .33, 26, .09, 4, 0, 1), 'pe', 1e9)}
    for t, (slug, title, be, ba_, bu, kind, unit) in SC.items():
        cases = [be, ba_, bu]; v = [val(*c) / unit for c in cases]; u = '$B' if unit > 1 else '$ per share'
        def row(label, f): return [label] + [f(c) for c in cases]
        ev = lambda c: c[0] * c[2] if kind == 'ps' else c[0] * c[1] * .79 * c[2]
        scen = [row('Revenue in 2030 ($B)', lambda c: B(c[0]))]
        if kind == 'pe':
            scen += [row('Operating margin %', lambda c: P(c[1])), row('After-tax operating profit, 2030 ($B)', lambda c: B(c[0] * c[1] * .79)), row('Exit multiple of after-tax profit (x)', lambda c: c[2])]
        else:
            scen += [row('Exit value to sales (x)', lambda c: c[2])]
        scen += [row('Value in 2030 ($B)', lambda c: B(ev(c))), row('Discount rate %', lambda c: P(c[3])), row('Years discounted', lambda c: c[4]),
                 row('Value today ($B)', lambda c: B(ev(c) / (1 + c[3]) ** c[4])), row('Plus net cash ($B)', lambda c: B(c[5]))]
        if unit == 1:
            scen += [row('Shares by 2030 (millions)', lambda c: round(c[6] / 1e6, 1))]
        scen += [['Value (' + u + ')'] + [round(x, 2) for x in v], ['Probability', 25, 50, 25], ['Probability-weighted value (' + u + ')', '', round(wsum(*v), 2), '']]
        write(slug, title, 'Scenario model: 2030 earning power, capitalised and discounted back four years',
              [['Tax rate on operating profit %', 21, 'U.S. federal rate'], ['Formula', 'value = (revenue x margin x (1 - tax) x multiple) / (1 + r)^4 + net cash', 'For Firefly: revenue x EV/sales multiple'], ['Inputs by scenario', 'see SCENARIOS', 'Sources are linked in the report']],
              None, None, [['Base-case value (' + u + ')', round(v[1], 2)]], scen, None, 'Model script: _source/models/new_coverage.py')
        vals[t] = (v[1], v[0], v[2])
    # memory makers: four years of cash flow, then a mid-cycle exit value
    cyc = ns['cyc']
    for t, slug, title, yrs in (('MU', 'micron', 'Micron Technology (MU)', ['FY2027', 'FY2028', 'FY2029', 'FY2030']),
                                ('SNDK', 'sandisk', 'Sandisk (SNDK)', ['FY2027', 'FY2028', 'FY2029', 'FY2030'])):
        C = ns[t]; cases = [C['bear'], C['base'], C['bull']]; v = [cyc(*c) for c in cases]
        def row(label, f): return [label] + [f(c) for c in cases]
        scen = []
        for i, y in enumerate(yrs):
            scen += [row(f'Revenue {y} ($B)', lambda c, i=i: B(c[0][i])), row(f'Free cash flow margin {y} %', lambda c, i=i: P(c[1][i])),
                     row(f'Present value of {y} free cash flow ($B)', lambda c, i=i: B(c[0][i] * c[1][i] / (1 + c[5]) ** (i + 1)))]
        scen += [row('Mid-cycle revenue ($B)', lambda c: B(c[2])), row('Mid-cycle operating margin %', lambda c: P(c[3])), row('Exit multiple of after-tax profit (x)', lambda c: c[4]),
                 row('Present value of exit value ($B)', lambda c: B(c[2] * c[3] * .79 * c[4] / (1 + c[5]) ** 4)), row('Discount rate %', lambda c: P(c[5])),
                 row('Plus net cash ($B)', lambda c: B(c[6])), row('Shares by 2030 (millions)', lambda c: round(c[7] / 1e6, 1)),
                 ['Value ($ per share)'] + [round(x, 2) for x in v], ['Probability', 25, 50, 25], ['Probability-weighted value ($ per share)', '', round(wsum(*v), 2), '']]
        write(slug, title, 'Cycle model: four years of free cash flow at the cycle\'s prices, then a mid-cycle exit value',
              [['Tax rate on operating profit %', 21, 'U.S. federal rate'], ['Formula', 'value = sum of discounted free cash flow, years 1-4 + (mid-cycle revenue x margin x (1 - tax) x multiple) / (1 + r)^4 + net cash', 'Fiscal years'],
               ['Inputs by scenario', 'see SCENARIOS', 'Sources are linked in the report']],
              None, None, [['Base-case value ($ per share)', round(v[1], 2)]], scen, None, 'Model script: _source/models/new_coverage.py')
        vals[t] = (v[1], v[0], v[2])
    return vals


def check(vals):
    import holdings, coverage
    R = dict(holdings.R); R.update(coverage.R)
    R['GEV'] = {'base': 442, 'bear': 272, 'bull': 682, 'wt': 460}
    bad = 0
    for t, (b, be, bu) in vals.items():
        r = R[t]; w = wsum(be, b, bu)
        got = [('base', b), ('bear', be), ('bull', bu), ('wt', w)]
        for k, x in got:
            if r.get(k) is not None and round(x) != r[k]:
                print(f'  MISMATCH {t} {k}: model {x:.2f}, report {r[k]}'); bad += 1
    print('checked', len(vals), 'reports;', 'all match' if not bad else f'{bad} mismatches')
    return bad


if __name__ == '__main__':
    v = main()
    print('wrote', len(os.listdir(OUT)), 'files to data/models/')
    if '--check' in sys.argv:
        sys.exit(1 if check(v) else 0)
