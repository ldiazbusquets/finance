"""Cross-section consistency checks, run on every build after the pages are written.

The model check (models/export.py --check) proves each report's headline values come from its model.
These checks prove the numbers inside a published report agree with each other:

  1. scenarios   the probability-weighted value is 25% bear + 50% base + 25% bull
  2. field       the price-field chart shows the same bear, base, bull, weighted value and price as the report
  3. scenario    the "Value per share" row of the bear/base/bull table matches the report's values
  4. bridge      PV of cash flows + PV of terminal value = enterprise value; EV +/- net cash = equity; equity / shares = per share
  5. cash flow   in the five-year table, free cash flow = operating cash flow - capital spending, in every column
  6. reconciled  a "free cash flow, last 12 months" figure elsewhere in the report either matches that table
                 or says whose definition it uses ("as ... defines it"), so two different numbers never appear unexplained

A failure stops the build with the page, the check and the numbers, so nothing inconsistent is published.
"""
import html as H
import os
import re

TOL_PCT = 0.025      # bridge and table identities: rounding to the displayed precision
TOL_ABS = 2.0        # dollars per share, for values shown rounded to whole dollars


def money(s):
    """'$1.02T' -> 1.02e12, '&minus;$35B' -> -35e9, '4.89B' -> 4.89e9, '360M' -> 3.6e8, '$358' -> 358"""
    t = H.unescape(s).replace('−', '-').replace(',', '').replace('≈', '').strip()
    m = re.search(r'(-)?\s*\$?\s*(-)?(\d[\d.]*)\s*([TBMK])?', t)
    if not m:
        return None
    v = float(m.group(3)) * {'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3, None: 1}[m.group(4)]
    return -v if (m.group(1) or m.group(2)) else v


def close(a, b, pct=TOL_PCT, ab=0.0):
    return abs(a - b) <= max(ab, pct * max(abs(a), abs(b), 1e-9))


def text(s):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


# Reports where a check legitimately has nothing to check, with the reason. Anything not listed here must run every check.
NO_BRIDGE = {}          # filled from method: only cash-flow models publish a valuation bridge
NO_CASH_TABLE = {
    'TSM': 'files a 20-F in New Taiwan dollars; its table is hand-built from releases, without a cash-flow row',
    'ASML': 'files a 20-F in euros; hand-built table',
    'SKHY': 'Korean filer; hand-built table',
    'SPCX': 'private until its 2026 listing; no five-year SEC history',
    'JPM': 'a bank: operating cash flow and capital spending say little about it, so its table shows revenue and net income only',
}


def check_report(R, page, has_data=True):
    """returns (errors, checks that ran)"""
    errs, ran = [], set()
    t = R['t']
    priv = bool(R.get('private'))
    field = {f[0]: f for f in R.get('field', [])}
    model_row = next((f for k, f in field.items() if k.endswith('model')), None)
    if priv:   # private companies: whole-company values in billions, read from the price field
        bear, bull, base = (model_row[1], model_row[2], model_row[3]) if model_row else (None, None, None)
        wt = field.get('Probability-weighted', (None,) * 4)[3]
        price = None
    else:
        bear, base, bull, wt, price = R.get('bear'), R.get('base'), R.get('bull'), R.get('wt'), R.get('price')
    # 1 scenario weights
    if None not in (bear, base, bull, wt):
        ran.add('weights')
        w = .25 * bear + .5 * base + .25 * bull
        if not close(w, wt, .015, TOL_ABS):
            errs.append(f'{t}: weighted value {wt} but 25/50/25 of {bear}/{base}/{bull} is {w:.1f}')
    # 2 field chart
    if model_row and 'Probability-weighted' in field:
        ran.add('field')
        for f in R.get('field', []):
            lab, lo, hi, mid = f[0], f[1], f[2], f[3]
            if lab.startswith('Probability-weighted') and wt is not None and mid is not None and not close(mid, wt, 0, 0.5):
                errs.append(f'{t}: field chart weighted {mid} vs report {wt}')
            if lab.startswith('Price at writing') and price is not None and mid is not None and not close(mid, price, 0, 0.01):
                errs.append(f'{t}: field chart price {mid} vs report {price}')
            if lo is not None and hi is not None and mid is not None and lab.endswith('model') and None not in (bear, base, bull):
                if not (close(lo, bear, 0, 0.5) and close(hi, bull, 0, 0.5) and close(mid, base, 0, 0.5)):
                    errs.append(f'{t}: field chart {lo}/{mid}/{hi} vs bear/base/bull {bear}/{base}/{bull}')
    # 3 scenario table: the value row of the Bear/Base/Bull table
    for tb in re.findall(r'<table[^>]*>.*?</table>', page, re.S):
        if '<th>Bear</th>' not in tb or '<th>Bull</th>' not in tb:
            continue
        for row in re.findall(r'<tr>(.*?)</tr>', tb, re.S):
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S)
            lab = text(cells[0]) if cells else ''
            if lab.startswith('Value per') or (priv and lab.lower().startswith(('value', 'company value', 'equity value'))):
                if len(cells) < 4 or None in (bear, base, bull):
                    continue
                got = [money(c) for c in cells[1:4]]
                if None in got:
                    continue
                if priv:
                    got = [g / 1e9 if g > 1e6 else g for g in got]
                ran.add('scenario table')
                if not (close(got[0], bear, .005, 0.5) and close(got[1], base, .005, 0.5) and close(got[2], bull, .005, 0.5)):
                    errs.append(f'{t}: scenario table {got} vs bear/base/bull {bear}/{base}/{bull}')
    # 4 valuation bridge
    for br in re.findall(r'<div class="bridge[^"]*">(.*?)</div></div>(?!<div)', page, re.S):
        items = [(text(a), money(b)) for a, b in re.findall(r'<span class="mono">(.*?)</span><b[^>]*>(.*?)</b>', br, re.S)]
        d = {k.lower(): v for k, v in items if v is not None}
        pv = next((v for k, v in d.items() if k.startswith('pv of 10') or k.startswith('pv of ten') or k.startswith('pv of cash')), None)
        tv = next((v for k, v in d.items() if k.startswith('pv of terminal')), None)
        ev = next((v for k, v in d.items() if k.startswith('enterprise value')), None)
        eq = next((v for k, v in d.items() if k.startswith('equity value')), None)
        sh = next((v for k, v in d.items() if k in ('shares', 'diluted shares', 'adr-equivalents', 'units')), None)
        ps = next((v for k, v in d.items() if k.startswith('per share') or k.startswith('per adr') or k.startswith('per unit')), None)
        net_k = next((k for k in d if k.startswith('net') or k.startswith('less net') or k.startswith('plus net')), None)
        if None not in (pv, tv, ev, eq, ps) and sh:
            ran.add('bridge')
        if pv is not None and tv is not None and ev is not None and not close(pv + tv, ev):
            errs.append(f'{t}: bridge PV {pv:.4g} + TV {tv:.4g} != EV {ev:.4g}')
        if ev is not None and eq is not None and net_k:
            n = d[net_k]
            n = -abs(n) if net_k.startswith('less') else n
            if not close(ev + n, eq, TOL_PCT) and not close(ev, eq, .006):
                errs.append(f'{t}: bridge EV {ev:.4g} {"+" if n >= 0 else "-"} {abs(n):.4g} != equity {eq:.4g}')
        if eq is not None and sh and ps is not None and not close(eq / sh, ps, .03, 1.0):
            errs.append(f'{t}: bridge equity {eq:.4g} / shares {sh:.4g} = {eq / sh:.2f}, page says {ps}')
    # 5 five-year table: FCF = OCF - capex, every column
    ttm_fcf = None
    for tb in re.findall(r'<table[^>]*>.*?</table>', page, re.S):
        rows = {}
        for row in re.findall(r'<tr>(.*?)</tr>', tb, re.S):
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
            if cells:
                rows[text(cells[0])] = [money(c) for c in cells[1:]]
        if {'Operating cash flow', 'Capital spending', 'Free cash flow'} <= set(rows):
            ran.add('cash-flow table')
            for i, (o, c, f) in enumerate(zip(rows['Operating cash flow'], rows['Capital spending'], rows['Free cash flow'])):
                if None in (o, c, f):
                    continue
                if not close(o - c, f, 0, 0.11e9 + 0.002 * abs(o)):
                    errs.append(f'{t}: five-year table column {i + 1}: OCF {o / 1e9:.1f}B - capex {c / 1e9:.1f}B != FCF {f / 1e9:.1f}B')
            ttm_fcf = rows['Free cash flow'][-1]
    # 6 a last-12-months free cash flow elsewhere must match the table or name its definition
    if ttm_fcf is not None:
        for m in re.finditer(r'<b>([^<]*?)</b><span>([^<]*Free cash flow[^<]*(last 12 months|last twelve months|trailing)[^<]*)</span>', page, re.I):
            v = money(m.group(1))
            if v is not None and not close(v, ttm_fcf, 0, 0.11e9) and 'defines' not in m.group(2).lower():
                errs.append(f'{t}: "{text(m.group(2))}" shows {text(m.group(1))} but the five-year table has {ttm_fcf / 1e9:.1f}B, with no definition given')
    # every check this report should have must actually have run: a layout change cannot silently skip a rule
    need = {'weights', 'field', 'scenario table'}
    if not priv and R.get('method', '').startswith('Cash-flow') and R.get('bridge', True):
        need.add('bridge')
    if not priv and has_data and t not in NO_CASH_TABLE and R.get('cashtable', True):
        need.add('cash-flow table')
    for c in sorted(need - ran):
        errs.append(f'{t}: the {c} check could not run (expected structure not found on {R["slug"]}.html)')
    return errs, ran


def run(out_dir, reports, data_dir=None):
    errs, n, runs = [], 0, 0
    data_dir = data_dir or os.path.join(out_dir, 'data', 'co')
    for R in reports:
        p = os.path.join(out_dir, R['slug'] + '.html')
        if not os.path.exists(p):
            errs.append(f"{R['t']}: {R['slug']}.html was not generated")
            continue
        n += 1
        e, ran = check_report(R, open(p, encoding='utf-8').read(), os.path.exists(os.path.join(data_dir, R['t'] + '.json')))
        errs += e
        runs += len(ran)
    return n, runs, errs
