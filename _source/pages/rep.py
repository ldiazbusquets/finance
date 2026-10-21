"""Shared builder for LDB Finance research reports.

A report is a dict (see pages/holdings.py). Valuation numbers are worked out in the analyst's
own model and typed in; the five-year table is read from the SEC data collected by the nightly update.
"""
import json, os

EXT = '<svg width="12" height="12" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA = next(p for p in [os.path.join(_HERE, '..', '..', 'data', 'co'), os.path.join(_HERE, '..', 'work', 'co')] if os.path.isdir(p))
# figures the SEC data misses, taken from the company's own release
FIX = {'LHX': {'rev': {'2026-01-02': 21.9e9}}}


def src(links):
    return '<div class="srcs">' + ''.join(f'<a href="{u}" target="_blank" rel="noopener">{t}{EXT}</a>' for t, u in links) + '</div>'


def stats(rows):
    return '<div class="kv">' + ''.join(f'<div><b>{v}</b><span>{k}</span></div>' for v, k in rows) + '</div>'


def table(head, rows, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="scroll"><table class="tbl txt {cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def prose(*ps):
    return '<div class="prose">' + ''.join(f'<p>{p}</p>' for p in ps) + '</div>'


def key(label, text):
    return f'<p class="key"><b>{label}.</b> {text}</p>'


def chap(n, cid, label, h2, body):
    return f'<section class="chap" id="{cid}"><div class="eyebrow mono">{n:02d} &middot; {label}</div><h2>{h2}</h2>{body}</section>'


def money(v):
    if v is None:
        return '&mdash;'
    s = '&minus;' if v < 0 else ''
    a = abs(v)
    return f'{s}${a / 1e9:,.1f}B' if a < 1e12 else f'{s}${a / 1e12:,.2f}T'


def pct(v):
    return '&mdash;' if v is None else ('&minus;' if v < 0 else '') + f'{abs(v) * 100:.1f}%'


def fin_table(t, years=5, bank=False):
    """Five fiscal years plus the trailing twelve months, straight from the SEC data."""
    d = json.load(open(os.path.join(DATA, t + '.json')))
    f, ends, q = d['f'], d['ends'], d.get('q')
    for k, by in FIX.get(t, {}).items():
        for e, v in by.items():
            if e in ends and f[k][ends.index(e)] is None:
                f[k][ends.index(e)] = v
    n = len(ends)
    idx = [i for i in range(n) if f['rev'][i] or f['ni'][i]][-years:]
    def fy(e):   # a year that ends in the first days of January belongs to the year before
        return 'FY' + (str(int(e[:4]) - 1) if e[5:7] == '01' and int(e[8:10]) <= 7 else e[:4])
    cols = [(fy(ends[i]), {k: f[k][i] for k in f}) for i in idx]
    if q and q.get('ttm') and q['end'] > ends[-1]:
        m = q['ttm']
        cols.append(('TTM ' + {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}[q['end'][5:7]] + ' ' + q['end'][:4], m))
    def g(c, k):
        return c[1].get(k)
    rows = [['Revenue'] + [money(g(c, 'rev')) for c in cols]]
    if not bank:
        rows.append(['Operating margin'] + [pct(g(c, 'ebit') / g(c, 'rev')) if g(c, 'ebit') is not None and g(c, 'rev') else '&mdash;' for c in cols])
    rows.append(['Net income'] + [money(g(c, 'ni')) for c in cols])
    if not bank:
        rows.append(['Operating cash flow'] + [money(g(c, 'cfo')) for c in cols])
        rows.append(['Capital spending'] + [money(g(c, 'capex')) for c in cols])
        rows.append(['Free cash flow'] + [money(g(c, 'cfo') - g(c, 'capex')) if g(c, 'cfo') is not None and g(c, 'capex') is not None else '&mdash;' for c in cols])
    return table([''] + [c[0] for c in cols], rows, 'allnum')


def field(R, narrow=False):
    rows, MAX, step_v = R['field'], R['max'], R['tick']
    n = len(rows)
    if narrow:
        x0, span, W, top, step = 8, 384, 400, 34, 70
        bot = top + step * (n - 1) + 22
    else:
        x0, span, W, top, step = 190, 780, 1000, 44, 48
        bot = top + step * (n - 1) + 26
    X = lambda v: x0 + v / MAX * span
    ticks = ''.join(f'<path d="M{X(v):.1f} 6V{bot}"/>' for v in range(0, MAX + 1, step_v))
    sfx = R.get('suffix', '')
    lab = ''.join(f'<text x="{X(v):.1f}" y="{bot + 22}" text-anchor="middle">${v:,}{sfx}</text>' for v in range(0, MAX + 1, step_v * 2))
    out = ''
    for i, (name, lo, hi, pt, txt) in enumerate(rows):
        y = top + i * step
        short = txt.split(', base')[0].split(', average')[0]
        if narrow:
            out += f'<text class="nm" x="{x0}" y="{y - 16}">{name}<tspan class="vl" dx="10">{short}</tspan></text>'
        else:
            out += f'<text class="nm" x="0" y="{y + 5}">{name}</text>'
        if lo is not None:
            out += f'<rect class="rg{" acc" if i == 0 else ""}" x="{X(lo):.1f}" y="{y - 8}" width="{max(2, X(hi) - X(lo)):.1f}" height="16" rx="8"/>'
        if pt is not None:
            out += f'<circle class="{"dot acc" if i < 2 else "dot"}" cx="{X(pt):.1f}" cy="{y}" r="{7 if i < 3 else 5}"/>'
        if not narrow:
            right = X(hi) if hi is not None else X(pt)
            if right > x0 + span * 0.72:
                tx, anchor = (X(lo) if lo is not None else X(pt)) - 14, 'end'
                txt = short
            else:
                tx, anchor = right + 14, 'start'
            out += f'<text class="vl" x="{tx:.1f}" y="{y + 5}" text-anchor="{anchor}">{txt}</text>'
    out += f'<path class="ln" d="M{X(R["base"]):.1f} 6V{bot}"/><path class="ln now cnow" data-x0="{x0}" data-span="{span}" data-max="{MAX}" data-bot="{bot}" d="M0 0" style="display:none"/>'
    cls = 'narrow' if narrow else 'wide'
    aria = '; '.join(f'{r[0]} {r[4]}' for r in rows)
    return f'<svg class="field {cls}" viewBox="0 0 {W} {bot + 34}" role="img" aria-label="Value by method: {aria}"><g class="ax">{ticks}</g><g class="ticks">{lab}</g>{out}</svg>'


def d(v):
    return f'${v:,.0f}' if v >= 100 or float(v).is_integer() else f'${v:,.2f}'


def bridge(items, ps):
    return '<div class="bridge rep">' + ''.join(f'<div><span class="mono">{k}</span><b class="num">{v}</b></div>' for k, v in items) + f'<div class="res"><span class="mono">Per share</span><b class="num">{ps}</b></div></div>'


SCRIPT = {'amazon': 'amzn', 'meta': 'meta', 'nvidia': 'nvda', 'jpmorgan': 'jpm', 'vertiv': 'vrt', 'l3harris': 'lhx', 'american-water': 'awk',
          'boeing': 'ba', 'gev': 'gev'}
SRC_URL = 'https://github.com/ldiazbusquets/finance/blob/main/_source/models/'


def checkit(slug):
    """the 'check the numbers' box: the full model as a CSV and its source code"""
    if not os.path.exists(os.path.join(DATA, '..', 'models', slug + '.csv')):
        return ''
    script = SCRIPT.get(slug, 'new_coverage')
    return (f'<div class="checkit"><div><span class="mono">Check the numbers</span><p>Every figure in this valuation comes from one model script, '
            f'rerun and checked against this page each time the site is built. The download has the inputs and their sources, each year&rsquo;s cash flow, '
            f'the bridge to the value, the scenarios and the sensitivity table.</p></div>'
            f'<div class="cta" style="margin:0;gap:8px"><a class="pill gh sm" href="data/models/{slug}.csv" download>Download the model (CSV)</a>'
            f'<a class="pill gh sm" href="{SRC_URL}{script}.py" target="_blank" rel="noopener">Model code &#8599;</a></div></div>')


def body(R):
    P, B = R['price'], R['base']
    imp = B / P - 1
    cells = ''.join(f'<div><span class="mono">{a}</span><b>{b}</b><small>{c}</small></div>' for a, b, c in R['cells']) if R.get('cells') else (
        f'<div><span class="mono">Value per share</span><b>{d(B)}</b><small>{R["method"]}, base case</small></div>'
        f'<div><span class="mono">Price at writing</span><b>${P:,.2f}</b><small>{R.get("pricenote", "Close, " + R["date"])}</small></div>'
        f'<div><span class="mono">Implied return</span><b class="{"up" if imp >= 0 else "dn"}">{"+" if imp >= 0 else "&minus;"}{abs(imp) * 100:.1f}%</b><small>Price to value</small></div>')
    now = '' if R.get('private') else f'''<div class="panel now" id="now">
        <div class="hd"><div><h3 class="sec">Since the report</h3><p>Today&rsquo;s close against the report&rsquo;s numbers, updated every weekday. The analysis and the call are as of {R['date']} and change only when the report is revised.</p></div>{'' if R.get('noauto') else f'<div class="cta" style="margin:0;gap:8px"><a class="pill gh sm" href="snapshot.html?t={R["t"]}&amp;view=q">Quarterly figures &rarr;</a><a class="pill gh sm" href="valuation.html?t={R["t"]}">Today&rsquo;s automatic model &rarr;</a></div>'}</div>
        <div class="kv four"><div><b id="nPx">&mdash;</b><span id="nPxD">Last close</span></div><div><b id="nChg">&mdash;</b><span>Since the report&rsquo;s ${P:,.2f}</span></div><div><b id="nGap">&mdash;</b><span>Price against {d(B)} value</span></div><div><b id="nRg">&mdash;</b><span>52-week range</span></div></div>
      </div>'''
    disc = R.get('disclosure', f'The author holds {R["t"]} shares.')
    toc = ''.join(f'<a href="#{c[0]}"><i>{n:02d}</i>{c[1]}</a>' for n, c in enumerate(R['toc'], 1))
    head = f'''<header class="ph rp">
  <div class="wrap">
    <div class="eyebrow mono"><a href="research.html">Research</a>&nbsp;/&nbsp;Equities &middot; {R['sector']} &middot; {R['date']}<span class="kind" title="Written and reviewed by Luis Diaz Busquets">Analyst report</span></div>
    <h1>{R['h1']}</h1>
    <p class="sub">{R['sub']}</p>
    <div class="verdict">
      <div class="call"><span class="mono">Recommendation</span><b>{R['call']}</b></div>
      {cells}
    </div>
  </div>
</header>
<section class="tight rbody">
  <div class="wrap rlay">
    <nav class="toc" aria-label="Chapters"><span class="mono">Contents</span>{toc}</nav>
    <div class="rmain">
      {now}
      <div class="panel" style="margin-top:{'0' if R.get('private') else '16px'}">
        <div class="hd"><div><h3 class="sec">Where each method lands, {'company value' if R.get('private') else 'per share'}</h3><p>{R['fieldnote']} <span class="nowkey">The copper line marks the base case{'.' if R.get('private') else '; the fine dotted line is today&rsquo;s close.'}</span></p></div></div>
        {field(R)}{field(R, True)}
        <p class="fine">Written on {R['date']}{R.get('timing', '')}. {'Figures are from company statements and news reports, as linked; they are not audited.' if R.get('private') else 'Figures are from the company&rsquo;s filings and releases unless noted.'} Not investment advice. {disc}</p>
      </div>
'''
    chs = ''.join(chap(n, c[0], c[1], c[2], c[3] + (checkit(R['slug']) if c[0] == 'value' else '')) for n, c in enumerate(R['chapters'], 1))
    return head + chs + '''
    </div>
  </div>
</section>
'''
