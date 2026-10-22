"""Puerto Rico against Latin America: IMF World Economic Outlook, October 2026, all in U.S. dollars.
Every figure here is copied from the IMF DataMapper (WEO October 2026 vintage), pulled October 22, 2026.
2025 is the latest year with (mostly) actual data; 2026 and 2027 are IMF projections."""

SRC = 'IMF World Economic Outlook, October 2026'
# order: Puerto Rico first, then the six large economies, then nearby smaller ones, then the U.S. for reference
C = [('PRI', 'Puerto Rico'), ('CHL', 'Chile'), ('ARG', 'Argentina'), ('MEX', 'Mexico'), ('BRA', 'Brazil'),
     ('COL', 'Colombia'), ('PER', 'Peru'), ('URY', 'Uruguay'), ('PAN', 'Panama'), ('CRI', 'Costa Rica'),
     ('DOM', 'Dominican Republic'), ('SLV', 'El Salvador'), ('USA', 'United States')]
NAME = dict(C)
MAIN = ['PRI', 'CHL', 'ARG', 'MEX', 'BRA', 'COL', 'PER']

# GDP, current U.S. dollars, billions
GDP = {'PRI': {2015: 103.38, 2019: 105.13, 2024: 126.03, 2025: 129.37, 2026: 133.22, 2027: 139.39},
       'ARG': {2015: 642.46, 2019: 446.76, 2024: 637.74, 2025: 683.59, 2026: 768.21, 2027: 762.29},
       'BRA': {2015: 1800.05, 2019: 1873.29, 2024: 2185.82, 2025: 2279.92, 2026: 2654.76, 2027: 2796.14},
       'CHL': {2015: 242.52, 2019: 278.06, 2024: 329.20, 2025: 357.40, 2026: 402.24, 2027: 413.44},
       'COL': {2015: 293.49, 2019: 323.06, 2024: 420.50, 2025: 457.10, 2026: 572.74, 2027: 634.70},
       'MEX': {2015: 1213.29, 2019: 1304.11, 2024: 1834.64, 2025: 1835.04, 2026: 2176.24, 2027: 2314.52},
       'PER': {2015: 193.35, 2019: 236.27, 2024: 295.33, 2025: 341.96, 2026: 399.59, 2027: 413.60},
       'DOM': {2015: 71.06, 2019: 89.24, 2024: 124.61, 2025: 127.90, 2026: 145.36, 2027: 158.76},
       'CRI': {2015: 56.44, 2019: 64.75, 2024: 96.73, 2025: 102.90, 2026: 115.25, 2027: 124.40},
       'URY': {2015: 58.22, 2019: 62.23, 2024: 82.32, 2025: 85.58, 2026: 95.16, 2027: 100.53},
       'PAN': {2015: 55.77, 2019: 69.78, 2024: 86.52, 2025: 90.46, 2026: 96.47, 2027: 102.71},
       'SLV': {2015: 23.44, 2019: 26.88, 2024: 34.88, 2025: 36.71, 2026: 39.38, 2027: 41.78},
       'USA': {2015: 18295.0, 2019: 21539.98, 2024: 29381.03, 2025: 30861.30, 2026: 32642.37, 2027: 34441.61}}

# GDP per person, current U.S. dollars, 2015-2027
_Y = list(range(2015, 2028))
_PC = {'PRI': [29242, 29978, 30329, 30680, 31830, 31427, 32619, 35354, 36981, 39344, 40620, 41851, 43808],
       'ARG': [14895, 12773, 14618, 11786, 9942, 8489, 10610, 13702, 14020, 13550, 14399, 16021, 15741],
       'BRA': [8893, 8813, 10056, 9282, 9011, 7057, 7952, 9256, 10350, 10282, 10683, 12397, 13016],
       'CHL': [13507, 13705, 14970, 15752, 14604, 13211, 16275, 15379, 17003, 16539, 17837, 19961, 20415],
       'COL': [6337, 6037, 6577, 6924, 6540, 5363, 6231, 6688, 7027, 7980, 8617, 10726, 11817],
       'MEX': [9915, 9000, 9543, 9971, 10251, 8744, 10207, 11288, 13686, 13870, 13759, 16191, 17095],
       'PER': [6453, 6535, 7106, 7273, 7353, 6407, 6923, 7432, 8084, 8669, 9938, 11498, 11783],
       'DOM': [7120, 7506, 7784, 8286, 8615, 7525, 9023, 10715, 11280, 11542, 11749, 13245, 14348],
       'CRI': [11635, 11987, 12185, 12458, 12757, 12244, 12661, 13576, 16582, 18165, 19162, 21282, 22779],
       'URY': [16765, 16517, 18608, 18656, 17740, 15257, 17314, 20347, 22656, 23576, 24549, 27339, 28923],
       'PAN': [14028, 14803, 15697, 16187, 16540, 13336, 15538, 17400, 18822, 19187, 19814, 20877, 21960],
       'SLV': [3790, 3901, 4020, 4184, 4320, 3997, 4643, 5075, 5320, 5503, 5751, 6124, 6453],
       'USA': [57007, 58180, 60293, 63165, 65561, 64518, 71426, 77964, 82579, 86417, 90267, 95212, 100208]}
PC = {c: dict(zip(_Y, v)) for c, v in _PC.items()}

# GDP per person at purchasing-power parity, international dollars
PPP = {'PRI': {2019: 36218, 2025: 52189, 2026: 53917}, 'ARG': {2019: 23535, 2025: 31497, 2026: 32899},
       'BRA': {2019: 16035, 2025: 23363, 2026: 24594}, 'CHL': {2019: 25826, 2025: 35791, 2026: 37008},
       'COL': {2019: 16349, 2025: 22516, 2026: 23634}, 'MEX': {2019: 20725, 2025: 25684, 2026: 26743},
       'PER': {2019: 14182, 2025: 19199, 2026: 20238}, 'DOM': {2019: 20789, 2025: 30393, 2026: 32597},
       'CRI': {2019: 23111, 2025: 32320, 2026: 34214}, 'URY': {2019: 24970, 2025: 37197, 2026: 39008},
       'PAN': {2019: 33365, 2025: 43951, 2026: 47129}, 'SLV': {2019: 9757, 2025: 14061, 2026: 15077}, 'USA': {2019: 65561, 2025: 90267, 2026: 95212}}

# real GDP growth, percent
_GY = list(range(2016, 2028))
_G = {'PRI': [-1.3, -2.9, -4.4, 1.7, -4.2, 0.4, 3.0, 0.7, 3.2, 0.3, -0.1, 1.0],
      'ARG': [-2.1, 2.8, -2.6, -2.0, -9.9, 10.4, 6.0, -1.9, -1.4, 4.5, 2.1, 3.5],
      'BRA': [-3.3, 1.3, 1.8, 1.2, -3.3, 4.8, 3.0, 3.2, 3.4, 2.3, 2.2, 1.9],
      'CHL': [1.8, 1.4, 4.0, 0.6, -6.1, 11.3, 2.1, 0.7, 2.8, 2.5, 0.6, 2.6],
      'COL': [2.1, 1.4, 2.6, 3.2, -7.2, 10.8, 7.3, 0.8, 1.5, 2.6, 2.2, 2.3],
      'MEX': [1.8, 1.9, 2.0, -0.4, -8.4, 6.0, 3.7, 3.1, 1.5, 0.5, 1.5, 1.8],
      'PER': [4.0, 2.5, 4.0, 2.2, -10.9, 13.4, 2.8, -0.4, 3.5, 3.4, 3.0, 2.9],
      'DOM': [6.7, 3.9, 7.1, 4.9, -7.9, 14.0, 5.2, 2.2, 5.0, 2.1, 4.6, 4.4],
      'CRI': [4.2, 4.2, 2.9, 2.7, -4.1, 8.2, 5.5, 4.8, 4.1, 4.6, 3.3, 3.5],
      'URY': [1.7, 1.7, 0.2, 0.9, -7.4, 5.8, 4.6, 0.8, 3.3, 1.8, 1.3, 2.4],
      'PAN': [4.6, 5.7, 3.9, 3.1, -17.8, 16.5, 11.0, 7.2, 2.7, 4.4, 5.0, 4.2],
      'SLV': [2.5, 2.2, 2.4, 2.4, -7.9, 11.9, 2.9, 3.4, 2.6, 3.9, 4.5, 4.0],
      'USA': [1.8, 2.5, 3.0, 2.6, -2.1, 6.3, 2.4, 2.9, 3.0, 2.3, 2.3, 2.3]}
G = {c: dict(zip(_GY, v)) for c, v in _G.items()}

# average consumer-price inflation, percent
INF = {'PRI': {2023: 3.5, 2024: 2.0, 2025: 1.5, 2026: 3.1}, 'ARG': {2023: 133.5, 2024: 219.9, 2025: 41.9, 2026: 32.5},
       'BRA': {2023: 4.6, 2024: 4.4, 2025: 5.0, 2026: 4.4}, 'CHL': {2023: 7.6, 2024: 3.9, 2025: 4.2, 2026: 3.7},
       'COL': {2023: 11.7, 2024: 6.6, 2025: 5.1, 2026: 6.0}, 'MEX': {2023: 5.5, 2024: 4.7, 2025: 3.8, 2026: 3.8},
       'PER': {2023: 6.3, 2024: 2.4, 2025: 1.5, 2026: 3.8}, 'DOM': {2023: 4.8, 2024: 3.3, 2025: 3.9, 2026: 5.1},
       'CRI': {2023: 0.5, 2024: -0.4, 2025: -0.1, 2026: -0.8}, 'URY': {2023: 5.9, 2024: 4.8, 2025: 4.7, 2026: 4.0},
       'PAN': {2023: 1.5, 2024: 0.7, 2025: -0.1, 2026: 1.8},
       'SLV': {2023: 4.0, 2024: 0.9, 2025: 0.3, 2026: 2.7}, 'USA': {2023: 4.1, 2024: 3.0, 2025: 2.7, 2026: 3.6}}

# unemployment rate, percent
UR = {'PRI': {2019: 8.3, 2025: 5.6}, 'ARG': {2019: 9.8, 2025: 7.4}, 'BRA': {2019: 12.0, 2025: 6.0},
      'CHL': {2019: 7.2, 2025: 8.5}, 'COL': {2019: 9.9, 2025: 8.0}, 'MEX': {2019: 3.5, 2025: 2.6},
      'PER': {2019: 6.6, 2025: 5.9}, 'DOM': {2019: 6.2, 2025: 5.3}, 'CRI': {2019: 12.4, 2025: 6.3},
      'URY': {2019: 8.9, 2025: 7.5}, 'PAN': {2019: 7.1, 2025: 10.4}, 'SLV': {2019: 6.5, 2025: 4.2}, 'USA': {2019: 3.7, 2025: 4.3}}

# general government gross debt, percent of GDP
DEBT = {'PRI': {2019: 48.8, 2025: 17.6}, 'ARG': {2019: 89.8, 2025: 80.1}, 'BRA': {2019: 87.1, 2025: 93.3},
        'CHL': {2019: 28.3, 2025: 41.5}, 'COL': {2019: 51.0, 2025: 59.9}, 'MEX': {2019: 51.9, 2025: 61.7},
        'PER': {2019: 26.5, 2025: 30.1}, 'DOM': {2019: 53.5, 2025: 59.0}, 'CRI': {2019: 56.1, 2025: 60.4},
        'URY': {2019: 59.6, 2025: 65.6}, 'PAN': {2019: 42.5, 2025: 56.6}, 'SLV': {2019: 77.9, 2025: 87.6}, 'USA': {2019: 108.8, 2025: 124.4}}

# population, millions
POP = {'PRI': {2015: 3.54, 2025: 3.19}, 'ARG': {2015: 43.13, 2025: 47.47}, 'BRA': {2015: 202.40, 2025: 213.42},
       'CHL': {2015: 17.95, 2025: 20.04}, 'COL': {2015: 46.31, 2025: 53.05}, 'MEX': {2015: 122.37, 2025: 133.37},
       'PER': {2015: 29.96, 2025: 34.41}, 'DOM': {2015: 9.98, 2025: 10.88}, 'CRI': {2015: 4.85, 2025: 5.37},
       'URY': {2015: 3.47, 2025: 3.49}, 'PAN': {2015: 3.98, 2025: 4.57}, 'SLV': {2015: 6.18, 2025: 6.38}, 'USA': {2015: 320.93, 2025: 341.89}}

# Puerto Rico real GNP / real GDP, fiscal 2025 (DDEC): $69.9B / $103.9B in 2017 dollars
PR_GNP_RATIO = 69.9 / 103.9


def cum(c, a=2020, b=2026):
    """Cumulative real growth from the end of year a-1 to the end of year b, percent."""
    x = 1.0
    for y in range(a, b + 1):
        x *= 1 + G[c][y] / 100
    return (x - 1) * 100


def popchg(c):
    return (POP[c][2025] / POP[c][2015] - 1) * 100


def check():
    # GDP / population should match GDP per person within rounding (IMF publishes all three)
    for c in NAME:
        implied = GDP[c][2025] * 1e3 / POP[c][2025]
        assert abs(implied / PC[c][2025] - 1) < 0.01, (c, implied, PC[c][2025])
    assert len(_PC['PRI']) == len(_Y) and all(len(v) == len(_GY) for v in _G.values())


check()


# ---------- rendering for the note ----------
import json


def _f(v, d=1):
    return ('&minus;' if v < 0 else '') + f'{abs(v):,.{d}f}'


def table():
    hd = ['', 'GDP, $B', 'Per person, $', 'Per person, PPP $', 'Growth 2025', 'Growth 2026<sup>f</sup>', 'Inflation 2025', 'Jobless 2025', 'Debt, % GDP', 'People, M']
    rows = []
    for c, n in C:
        cls = ' class="me"' if c == 'PRI' else ' class="med"' if c == 'USA' else ''
        cells = [f'${GDP[c][2025]:,.0f}', f'${PC[c][2025]:,}', f'${PPP[c][2025]:,}', _f(G[c][2025]) + '%', _f(G[c][2026]) + '%',
                 _f(INF[c][2025]) + '%', f'{UR[c][2025]:.1f}%', f'{DEBT[c][2025]:.0f}%', f'{POP[c][2025]:,.1f}']
        rows.append(f'<tr{cls}><td>{n}</td>' + ''.join(f'<td>{x}</td>' for x in cells) + '</tr>')
    return ('<div class="scroll" style="margin:22px 0 8px"><table class="tbl txt allnum lat"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in hd)
            + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
            + f'<p class="fine">{SRC}. All values in U.S. dollars at market exchange rates except PPP, which adjusts for local prices. 2025 is the latest year; f = IMF forecast. Debt is general government gross debt.</p>')


def bars(title, sub, items, fmt, legend='', mx=None):
    """items: (label, value, second value or None, highlight). Horizontal bars as HTML so labels stay readable on phones."""
    mx = mx or max(max(v, w or 0) for _, v, w, _ in items)
    out = []
    for lab, v, w, hl in items:
        sec = f'<i class="b2" style="width:{w / mx * 100:.1f}%"></i>' if w is not None else ''
        out.append(f'<div class="hb{" hl" if hl else ""}"><span class="hn">{lab}</span><span class="ht"><i class="b1" style="width:{max(v, 0) / mx * 100:.1f}%"></i>{sec}</span><span class="hv">{fmt(v)}</span></div>')
    return (f'<div class="panel" style="margin:22px 0"><div class="hd"><div><h3 class="sec">{title}</h3><p>{sub}</p></div>{legend}</div>'
            f'<div class="hbars">{"".join(out)}</div><p class="fine">{SRC}.</p></div>')


def per_person():
    items = sorted([(NAME[c], PC[c][2025], PPP[c][2025], c == 'PRI') for c in NAME if c != 'USA'], key=lambda x: -x[1])
    leg = '<div class="legend"><span><i style="background:var(--t2);height:8px"></i>Market dollars</span><span><i style="background:var(--t3);height:8px;opacity:.4"></i>Purchasing power</span></div>'
    return bars('GDP per person, 2025', 'The solid bar is GDP per person in U.S. dollars at market exchange rates; the pale bar is the purchasing-power figure, which allows for lower local prices. Puerto Rico in copper.',
                items, lambda v: f'${v:,}', leg)


def growth():
    items = sorted([(NAME[c], cum(c), None, c == 'PRI') for c in NAME if c != 'USA'], key=lambda x: -x[1])
    return bars('Real growth since 2019', 'Total growth in inflation-adjusted GDP from 2019 to 2026, using the IMF&rsquo;s 2026 forecast.',
                items, lambda v: f'+{v:.0f}%' if v >= 0 else f'&minus;{abs(v):.0f}%')


def trend():
    col = {'PRI': ('acc', 2.4), 'CHL': ('t2', 1.3), 'ARG': ('t3', 1.2), 'MEX': ('t2', 1.3), 'BRA': ('t3', 1.2), 'COL': ('t3', 1.2), 'PER': ('t2', 1.2)}
    data = [{'n': NAME[c], 'c': col[c][0], 'w': col[c][1], 'p': [[str(y), PC[c][y]] for y in _Y]} for c in MAIN]
    spec = {'data': data, 'yf': 'k', 'dash_from': '2026'}
    return ('<div class="panel" style="margin:22px 0"><div class="hd"><div><h3 class="sec">GDP per person, 2015 to 2027</h3>'
            '<p>U.S. dollars at market rates. 2026 and 2027 are IMF forecasts.</p></div></div>'
            f'<svg class="chart" style="height:300px" data-chart=\'{json.dumps(spec)}\'></svg><p class="fine">{SRC}.</p></div>')
