"""Excel versions of every report's valuation, with live formulas.

Each workbook rebuilds the model in spreadsheet formulas: change an input and every number recalculates.
Inputs are blue, formulas black, links between sheets green. Run from this folder:

    python3 xlsx_models.py            writes ../../data/models/<page>.xlsx
    python3 xlsx_models.py --check    also recalculates each file in LibreOffice and compares
                                      every scenario value with the model scripts (needs soffice)
"""
import os, sys, json, subprocess, contextlib, io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.comments import Comment

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'data', 'models')
sys.path.insert(0, os.path.join(HERE, '..', 'pages'))
SRC = 'https://github.com/ldiazbusquets/finance/blob/main/_source/models/'

# ---------------------------------------------------------------- look
DARK, DARK2, HEAD, COPPER, CREAM, MUTED, LINE = '0C0A08', '1B1511', '2A211A', 'C58B5C', 'F4EDE4', 'A8998A', 'E6DDD2'
F = 'Arial'
def font(**k): k.setdefault('name', F); k.setdefault('size', 10); return Font(**k)
def fill(c): return PatternFill('solid', start_color=c, end_color=c)
BLUE, BLACK, GREEN = '0000FF', '000000', '008000'
INFILL = 'FFF8E7'                                   # pale cream behind inputs
THIN = Side(style='thin', color=LINE)
FMT = {'pct': '0.0%;(0.0%);-', 'pct2': '0.00%;(0.00%);-', 'b': '#,##0.00;(#,##0.00);-', 'b1': '#,##0.0;(#,##0.0);-', 'usd': '$#,##0.00;($#,##0.00);-',
       'x': '0.0"x"', 'n': '#,##0;(#,##0);-', 'n4': '0.0000', 'df': '0.0000', 'yr': '@'}


class Sheet:
    def __init__(self, wb, name, title, sub, width, first=False):
        self.ws = wb.active if first else wb.create_sheet(name)
        self.ws.title = name; self.w = width; self.r = 1; self.notecol = None
        ws = self.ws; ws.sheet_view.showGridLines = False
        for r in range(1, 5):
            for c in range(1, width + 1):
                ws.cell(r, c).fill = fill(DARK)
        ws['A1'] = 'LDB FINANCE'; ws['A1'].font = font(size=9, bold=True, color=COPPER)
        ws['A2'] = title; ws['A2'].font = font(size=16, bold=True, color=CREAM)
        ws['A3'] = sub; ws['A3'].font = font(size=9, color=MUTED)
        ws.row_dimensions[2].height = 26
        self.r = 6
        ws.freeze_panes = None   # nothing frozen: every sheet fits on screen
        ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True

    def section(self, text, cols=None):
        ws, r = self.ws, self.r
        for c in range(1, (cols or self.w) + 1):
            ws.cell(r, c).fill = fill(DARK2)
        ws.cell(r, 1, text.upper()).font = font(size=9, bold=True, color=COPPER)
        ws.row_dimensions[r].height = 20
        self.r += 1
        return r

    def header(self, labels, start=1):
        ws, r = self.ws, self.r
        for i, t in enumerate(labels):
            c = ws.cell(r, start + i, t); c.fill = fill(HEAD); c.font = font(size=9, bold=True, color=CREAM)
            c.alignment = Alignment(horizontal='left' if i == 0 else 'center', vertical='center', wrap_text=True)
        ws.row_dimensions[r].height = 30
        self.r += 1
        return r

    def row(self, label, values, fmt=None, kind='f', note=None, key=False, start=2):
        """kind: 'i' input (blue), 'f' formula (black), 'l' link to another sheet (green)"""
        ws, r = self.ws, self.r
        a = ws.cell(r, 1, label); a.font = font(bold=key); a.border = Border(bottom=THIN)
        for i, v in enumerate(values):
            if v is None:
                continue
            c = ws.cell(r, start + i, v); c.border = Border(bottom=THIN)
            c.font = font(color=BLUE if kind == 'i' else GREEN if kind == 'l' else BLACK, bold=key)
            if kind == 'i':
                c.fill = fill(INFILL)
            if key:
                c.fill = fill('F3E3D3')
            if fmt:
                c.number_format = FMT.get(fmt, fmt)
            c.alignment = Alignment(horizontal='right')
        if note:
            n = ws.cell(r, self.notecol or (start + max(1, len(values))), note); n.font = font(size=9, italic=True, color='7A6E62')
        self.r += 1
        return r

    def note(self, text):
        c = self.ws.cell(self.r, 1, text); c.font = font(size=9, italic=True, color='7A6E62'); self.r += 1

    def gap(self, n=1):
        self.r += n

    def widths(self, first=44, rest=13, extra=None):
        self.ws.column_dimensions['A'].width = first
        for c in range(2, self.w + 1):
            self.ws.column_dimensions[L(c)].width = rest
        for k, v in (extra or {}).items():
            self.ws.column_dimensions[k].width = v


def ref(col, row, abs_=True):
    return f'${L(col)}${row}' if abs_ else f'{L(col)}{row}'


# ---------------------------------------------------------------- shared summary sheet
def summary(wb, title, method, price, script, wacc=None, ke=None, wfix=None, scen_sheets=None, ps_cells=None, sens=None, unit='$ per share', notes=()):
    S = Sheet(wb, 'Summary', title, method + '  ·  Inputs in blue can be changed; everything else recalculates.', 5, first=True)
    S.widths(46, 15, {'E': 58}); S.notecol = 5
    out = {}
    if wacc:
        S.section('Discount rate (WACC)')
        rf = S.row('Risk-free rate (10-year Treasury)', [.0515], 'pct2', 'i', 'FRED, October 2026')
        erp = S.row('Equity risk premium', [.045], 'pct2', 'i', 'Long-run U.S. premium')
        beta = S.row('Beta', [wacc['beta']], '0.00', 'i', wacc.get('bnote', 'Measured against the S&P 500'))
        ke_r = S.row('Cost of equity = risk-free + beta x premium', [f'=B{rf}+B{beta}*B{erp}'], 'pct2')
        px = S.row('Share price ($)', [wacc['price']], 'usd', 'i', 'Price at writing')
        sh = S.row('Diluted shares (billions)', [wacc['shares']], FMT['n4'], 'i', 'Latest filing')
        e = S.row('Market value of equity ($B)', [f'=B{px}*B{sh}'], 'b1')
        dbt = S.row('Debt ($B)', [wacc['debt']], 'b1', 'i', 'Latest balance sheet')
        kd = S.row('Pre-tax cost of debt', [wacc['kd']], 'pct2', 'i')
        tx = S.row('Tax rate on interest', [.21], 'pct', 'i', 'U.S. federal rate')
        w = S.row('WACC', [f'=B{e}/(B{e}+B{dbt})*B{ke_r}+B{dbt}/(B{e}+B{dbt})*B{kd}*(1-B{tx})'], 'pct2', key=True)
        out['W'] = f"Summary!$B${w}"
        S.gap()
    elif ke is not None:
        S.section('Cost of equity (CAPM)')
        rf = S.row('Risk-free rate (10-year Treasury)', [.0515], 'pct2', 'i', 'FRED, October 2026')
        erp = S.row('Equity risk premium', [.045], 'pct2', 'i', 'Long-run U.S. premium')
        beta = S.row('Beta', [ke], '0.000', 'i', 'Measured against the S&P 500')
        k = S.row('Cost of equity', [f'=B{rf}+B{beta}*B{erp}'], 'pct2', key=True)
        out['W'] = f"Summary!$B${k}"
        S.gap()
    S.section('Scenarios')
    S.header(['', 'Bear', 'Base', 'Bull'])
    vr = S.row(f'Value ({unit})', [f"='{s}'!{c}" for s, c in zip(scen_sheets, ps_cells)] if scen_sheets else ps_cells, 'usd' if unit.startswith('$ per') else 'b', 'l' if scen_sheets else 'f')
    pr = S.row('Probability', [.25, .5, .25], 'pct', 'i')
    wt = S.row(f'Probability-weighted value ({unit})', [None, f'=SUMPRODUCT(B{vr}:D{vr},B{pr}:D{pr})'], 'usd' if unit.startswith('$ per') else 'b', key=True)
    p = S.row('Price at writing' + (' ($)' if unit.startswith('$ per') else ' ($B, latest valuation)'), [None, price], 'usd' if unit.startswith('$ per') else 'b', 'i')
    S.row('Weighted value against the price', [None, f'=C{wt}/C{p}-1'], 'pct')
    out['rows'] = (vr, pr, wt)
    if sens:
        S.gap(); S.section(sens['title'])
        S.header([sens['col'], sens['vcol']])
        for x, formula in sens['rows']:
            S.row('', [x, formula], None)
            S.ws.cell(S.r - 1, 2).number_format = FMT['pct2']; S.ws.cell(S.r - 1, 2).font = font(color=BLUE); S.ws.cell(S.r - 1, 2).fill = fill(INFILL)
            S.ws.cell(S.r - 1, 3).number_format = FMT['usd'] if unit.startswith('$ per') else FMT['b']
        S.note(sens.get('note', 'Each row recalculates the base case at that rate.'))
    S.script = script
    return S, out


def about(S):
    S.gap(); S.section('About this workbook')
    for n in ['Blue cells are inputs; black cells are formulas; green cells link to another sheet. Change any blue cell and the whole model recalculates.',
              f'Built from the model script {SRC}{S.script}.py, and checked against it each time the file is made.',
              'For education only. Not investment advice.']:
        S.note(n)


# ---------------------------------------------------------------- the four cash-flow engines
def dcf_sheet(wb, name, title, p, W_formula):
    """generic ten-year FCFF model (Amazon, Meta, Nvidia, Vertiv)"""
    S = Sheet(wb, name, title, name + ' case: ten-year free cash flow to the firm, values in $ billions', 12)
    S.widths(40, 11, {'L': 40})
    S.section('Inputs')
    i = {}
    i['rev0'] = S.row('Base revenue ($B)', [p['rev0']], 'b1', 'i', p.get('rev0n', 'Latest year or run-rate'))
    i['g1'] = S.row('Revenue growth, year 1', [p['g1']], 'pct', 'i')
    i['g2'] = S.row('Revenue growth, year 2', [p['g2']], 'pct', 'i', 'Then fades in a straight line to terminal growth by year 10')
    i['gT'] = S.row('Terminal growth', [.03], 'pct', 'i')
    i['m0'] = S.row('Operating margin, year 1', [p['m0']], 'pct', 'i')
    i['mT'] = S.row('Operating margin, target', [p['mT']], 'pct', 'i')
    i['ny'] = S.row('Years to reach the target margin', [p['ny']], '0', 'i')
    i['tax'] = S.row('Tax rate', [p['tax']], 'pct', 'i')
    i['s2c'] = S.row('Sales to capital (new revenue per $1 invested)', [p['s2c']], '0.0', 'i', 'Reinvestment = revenue growth / sales to capital')
    i['ron'] = S.row('Return on new capital, after year 10', [p['ronic']], 'pct', 'i', 'Sets reinvestment in the terminal value')
    i['shift'] = S.row('Discount rate shift for this case', [p['shift']], 'pct2', 'i', 'Added to the WACC on the Summary sheet')
    i['W'] = S.row('Discount rate', [f'={W_formula}+B{S.r - 1}'], 'pct2', 'l')
    i['net'] = S.row('Net cash ($B, negative = net debt)', [p['net']], 'b1', 'i', 'Latest balance sheet')
    i['sh'] = S.row('Diluted shares (billions)', [p['shares']], FMT['n4'], 'i', 'Latest filing')
    S.gap(); S.section('Projection')
    yrs = [str(2026 + t) for t in range(1, 11)]
    S.header(['Year'] + yrs)
    a = lambda k: f'$B${i[k]}'
    t = S.row('Year number', list(range(1, 11)), '0', 'f')
    heavy = list(p.get('heavy', ())) + [None] * (10 - len(p.get('heavy', ())))
    hv = S.row('Planned heavy investment ($B)', heavy, 'b1', 'i', 'Years with a capex plan; blank = use sales to capital')
    g = S.row('Revenue growth', [f'={a("g1")}', f'={a("g2")}'] + [f'={a("g2")}+({a("gT")}-{a("g2")})*({L(c)}{S.r - 2}-2)/8' for c in range(4, 12)], 'pct')
    rv = S.row('Revenue ($B)', [f'={a("rev0")}*(1+B{g})'] + [f'={L(c - 1)}{S.r}*(1+{L(c)}{g})' for c in range(3, 12)], 'b1')
    m = S.row('Operating margin', [f'={a("m0")}+({a("mT")}-{a("m0")})*MIN(1,{L(c)}{t}/{a("ny")})' for c in range(2, 12)], 'pct')
    eb = S.row('Operating income ($B)', [f'={L(c)}{rv}*{L(c)}{m}' for c in range(2, 12)], 'b1')
    no = S.row('After-tax operating income ($B)', [f'={L(c)}{eb}*(1-{a("tax")})' for c in range(2, 12)], 'b1')
    ri = S.row('Reinvestment ($B)', [f'=IF(ISNUMBER({L(c)}{hv}),{L(c)}{hv},({L(c)}{rv}-{(a("rev0") if c == 2 else L(c - 1) + str(rv))})/{a("s2c")})' for c in range(2, 12)], 'b1')
    fc = S.row('Free cash flow to the firm ($B)', [f'={L(c)}{no}-{L(c)}{ri}' for c in range(2, 12)], 'b1', key=True)
    df = S.row('Discount factor (mid-year)', [f'=1/(1+{a("W")})^({L(c)}{t}-0.5)' for c in range(2, 12)], 'df')
    pv = S.row('Present value ($B)', [f'={L(c)}{fc}*{L(c)}{df}' for c in range(2, 12)], 'b1')
    S.gap(); S.section('Bridge to value per share')
    b1 = S.row('Present value of ten years of cash flow ($B)', [f'=SUM(B{pv}:K{pv})'], 'b1')
    n11 = S.row('Year-11 after-tax operating income ($B)', [f'=K{eb}*(1+{a("gT")})*(1-{a("tax")})'], 'b1')
    tv = S.row('Terminal value ($B)', [f'=B{n11}*(1-{a("gT")}/{a("ron")})/({a("W")}-{a("gT")})'], 'b1', note='NOPAT11 x (1 - g / return on new capital) / (discount rate - g)')
    pt = S.row('Present value of terminal value ($B)', [f'=B{tv}/(1+{a("W")})^9.5'], 'b1')
    ev = S.row('Enterprise value ($B)', [f'=B{b1}+B{pt}'], 'b1')
    eq = S.row('Equity value ($B)', [f'=B{ev}+{a("net")}'], 'b1')
    ps = S.row('Value per share ($)', [f'=B{eq}/{a("sh")}'], 'usd', key=True)
    return S, {'ps': f'$B${ps}', 'fc': (fc, t), 'eb': eb, 'i': i}


def dcf_sens(name, info, Wcells):
    """discount-rate sensitivity for the generic DCF: cash flows do not depend on the rate, so only discounting changes"""
    fc, t = info['fc']; i = info['i']; s = f"'{name}'!"
    rows = []
    for k, W in enumerate(Wcells):
        r = 'B{row}'
        rows.append((W, lambda row, W=W: f"=(SUMPRODUCT({s}$B${fc}:$K${fc},1/(1+B{row})^({s}$B${t}:$K${t}-0.5))+{s}$K${info['eb']}*(1+{s}$B${i['gT']})*(1-{s}$B${i['tax']})*(1-{s}$B${i['gT']}/{s}$B${i['ron']})/(B{row}-{s}$B${i['gT']})/(1+B{row})^9.5+{s}$B${i['net']})/{s}$B${i['sh']}"))
    return rows


def generic_cases():
    """the exact cases in amzn.py, meta.py, nvda.py, vrt.py, lmt.py, noc.py, cat.py and asml.py"""
    return {
        'AMZN': dict(slug='amazon', title='Amazon (AMZN)', script='amzn', rev0n='Base revenue for 2026, $810B', price=262.63, W=[.085, .09, .095, .10],
                     wacc=dict(beta=1.33, price=262.63, shares=10.9, debt=133, kd=.05),
                     base=dict(rev0=810, g1=.12, g2=.11, m0=.13, mT=.18, ny=5, tax=.19, s2c=2.0, ronic=.20, net=-10, shares=10.9, heavy=(130, 100, 70, 50), shift=0),
                     bear=dict(g1=.08, g2=.07, m0=.12, mT=.14, heavy=(150, 120, 90, 60), shift=.01), bull=dict(g1=.15, g2=.14, m0=.14, mT=.22, heavy=(110, 80, 50, 30), shift=-.01)),
        'META': dict(slug='meta', title='Meta Platforms (META)', script='meta', rev0n='Base revenue for 2026, $256B', price=697.52, W=[.085, .09, .095, .10],
                     wacc=dict(beta=1.42, price=697.52, shares=2.573, debt=80.92, kd=.05),
                     base=dict(rev0=256, g1=.18, g2=.14, m0=.34, mT=.38, ny=5, tax=.16, s2c=2.0, ronic=.25, net=1.5, shares=2.573, heavy=(110, 90, 60, 40), shift=0),
                     bear=dict(g1=.10, g2=.08, m0=.30, mT=.30, heavy=(130, 110, 80, 60), shift=.01), bull=dict(g1=.24, g2=.18, m0=.36, mT=.44, heavy=(90, 70, 40, 25), shift=-.01)),
        'NVDA': dict(slug='nvidia', title='Nvidia (NVDA)', script='nvda', rev0n='Fiscal 2027 run-rate, $404B', price=216.47, W=[.09, .10, .11],
                     wacc=dict(beta=1.58),
                     base=dict(rev0=404, g1=.40, g2=.15, m0=.63, mT=.55, ny=7, tax=.17, s2c=2.5, ronic=.25, net=0, shares=24.3, shift=0),
                     bear=dict(g1=.20, g2=.05, m0=.60, mT=.45, shift=.01), bull=dict(g1=.55, g2=.25, m0=.65, mT=.60, shift=-.01)),
        'VRT': dict(slug='vertiv', title='Vertiv (VRT)', script='vrt', rev0n='2026 guidance midpoint, $14.0B', price=203.56, W=[.09, .10, .11, .12],
                    wacc=dict(beta=1.83, price=203.56, shares=0.393, debt=2.94, kd=.055),
                    base=dict(rev0=14.0, g1=.25, g2=.16, m0=.225, mT=.245, ny=3, tax=.21, s2c=3, ronic=.25, net=-0.13, shares=0.393, shift=0),
                    bear=dict(g1=.12, g2=.08, m0=.21, mT=.21, shift=.01), bull=dict(g1=.35, g2=.22, m0=.235, mT=.27, shift=-.01)),
        'LMT': dict(slug='lockheed-martin', title='Lockheed Martin (LMT)', script='lmt', rev0n='2026 guidance midpoint, $81.0B', price=590.20, W=[.07, .075, .08, .085, .09],
                    wacc=dict(beta=0.80, price=590.20, shares=0.2315, debt=20.5, kd=.05),
                    base=dict(rev0=81.0, g1=.07, g2=.06, m0=.115, mT=.12, ny=4, tax=.16, s2c=4, ronic=.15, net=-14.5, shares=0.2315, shift=0),
                    bear=dict(g1=.04, g2=.03, m0=.10, mT=.105, shift=.01), bull=dict(g1=.09, g2=.08, m0=.12, mT=.13, shift=-.01)),
        'NOC': dict(slug='northrop-grumman', title='Northrop Grumman (NOC)', script='noc', rev0n='2026 guidance midpoint, $44.0B', price=552.53, W=[.07, .075, .08, .085, .09],
                    wacc=dict(beta=0.80, price=552.53, shares=0.143, debt=15.2, kd=.05),
                    base=dict(rev0=44.0, g1=.06, g2=.07, m0=.113, mT=.12, ny=5, tax=.16, s2c=3, ronic=.15, net=-11.5, shares=0.143, shift=0),
                    bear=dict(g1=.03, g2=.03, m0=.105, mT=.105, shift=.01), bull=dict(g1=.08, g2=.09, m0=.118, mT=.13, shift=-.01)),
        'CAT': dict(slug='caterpillar', title='Caterpillar (CAT)', script='cat', rev0n='2026 estimate, $78.0B', price=703.84, W=[.085, .09, .095, .10, .105],
                    wacc=dict(beta=1.05, price=703.84, shares=0.4625, debt=11.0, kd=.05),
                    base=dict(rev0=78.0, g1=.08, g2=.06, m0=.20, mT=.21, ny=4, tax=.22, s2c=3, ronic=.20, net=-5.0, shares=0.4625, shift=0),
                    bear=dict(g1=0, g2=.02, m0=.17, mT=.17, shift=.01), bull=dict(g1=.12, g2=.10, m0=.215, mT=.23, shift=-.01)),
        'ASML': dict(slug='asml', title='ASML Holding (ASML), US$ at 1.123 per euro', script='asml', rev0n='2026 guidance midpoint, EUR 44.5B = $50.0B', price=1560.54, W=[.095, .10, .105, .11, .115],
                     wacc=dict(beta=1.30),
                     base=dict(rev0=44.5 * 1.123, g1=.22, g2=.15, m0=.415, mT=.44, ny=3, tax=.16, s2c=3, ronic=.30, net=9.0 * 1.123, shares=0.3831, shift=0),
                     bear=dict(g1=.08, g2=.05, m0=.36, mT=.36, shift=.01), bull=dict(g1=.30, g2=.20, m0=.43, mT=.47, shift=-.01)),
    }


def make_generic(key, c):
    base = c['base']
    cases = {'Base': base, 'Bear': {**base, **c['bear']}, 'Bull': {**base, **c['bull']}}
    wb = Workbook()
    hasdebt = 'debt' in c['wacc']
    S, out = summary(wb, c['title'], 'Ten-year discounted cash flow (free cash flow to the firm)', c['price'], c['script'],
                     wacc=c['wacc'] if hasdebt else None, ke=None if hasdebt else c['wacc']['beta'], scen_sheets=None, ps_cells=['', '', ''])
    infos = {}
    for name in ('Base', 'Bear', 'Bull'):
        p = dict(cases[name]); p['rev0n'] = c['rev0n']
        _, infos[name] = dcf_sheet(wb, name, c['title'], p, out['W'])
    vr = out['rows'][0]
    for col, name in zip('BCD', ('Bear', 'Base', 'Bull')):
        cell = S.ws[f'{col}{vr}']; cell.value = f"='{name}'!{infos[name]['ps']}"; cell.font = font(color=GREEN); cell.number_format = FMT['usd']
    sens = dcf_sens('Base', infos['Base'], c['W'])
    sens_block(S, c['W'], lambda r: sens[0][1](r))
    return wb


# ---------------------------------------------------------------- L3Harris, Boeing, GE Vernova, American Water, JPMorgan
def make_lhx():
    wb = Workbook()
    S, out = summary(wb, 'L3Harris (LHX)', 'Ten-year discounted free cash flow to the firm, following the 2028 framework', 248.77, 'lhx',
                     wacc=dict(beta=0.80, price=248.77, shares=0.1873, debt=11.0, kd=.055, bnote='Defense peers; the measured 0.61 understates risk'), scen_sheets=None, ps_cells=['', '', ''])
    cases = {'Base': (.075, .075, .146, 0), 'Bear': (.04, .03, .125, .01), 'Bull': (.10, .09, .155, -.01)}
    info = {}
    for name, (g1, g2, conv, shift) in cases.items():
        X = Sheet(wb, name, 'L3Harris (LHX)', name + ' case: free cash flow to the firm from guidance, $ billions', 12); X.widths(40, 11, {'L': 40})
        X.section('Inputs')
        rev0 = X.row('Revenue, 2026 ($B)', [23.45], 'b', 'i', 'Guidance midpoint')
        a1 = X.row('Revenue growth, 2027', [g1], 'pct', 'i'); a2 = X.row('Revenue growth, 2028', [g2], 'pct', 'i', 'Then fades to terminal growth by year 10')
        gT = X.row('Terminal growth', [.03], 'pct', 'i')
        f1 = X.row('Free cash flow to the firm, 2027 guidance ($B)', [3.65], 'b', 'i', 'Free cash flow guidance plus after-tax interest')
        r1 = X.row('Revenue behind that guidance, 2027 ($B)', [25.2], 'b', 'i')
        f2 = X.row('Free cash flow to the firm, 2028 guidance ($B)', [3.95], 'b', 'i')
        r2 = X.row('Revenue behind that guidance, 2028 ($B)', [27.1], 'b', 'i')
        cv = X.row('Cash conversion after 2028 (share of revenue)', [conv], 'pct', 'i', 'Also caps 2027 and 2028')
        sh_ = X.row('Discount rate shift for this case', [shift], 'pct2', 'i')
        W = X.row('Discount rate', [f'={out["W"]}+B{sh_}'], 'pct2', 'l')
        net = X.row('Net debt and preferred ($B)', [-10.5], 'b', 'i', '$9.5B net debt + $1.0B Pentagon preferred')
        sh = X.row('Diluted shares (billions)', [0.1873], FMT['n4'], 'i')
        X.gap(); X.section('Projection'); X.header(['Year'] + [str(2026 + t) for t in range(1, 11)])
        t = X.row('Year number', list(range(1, 11)), '0')
        g = X.row('Revenue growth', [f'=$B${a1}', f'=$B${a2}'] + [f'=$B${a2}+($B${gT}-$B${a2})*({L(c)}{t}-2)/8' for c in range(4, 12)], 'pct')
        rv = X.row('Revenue ($B)', [f'=$B${rev0}*(1+B{g})'] + [f'={L(c - 1)}{X.r}*(1+{L(c)}{g})' for c in range(3, 12)], 'b')
        cr = X.row('Cash conversion', [f'=MIN($B${f1}/$B${r1},$B${cv})', f'=MIN($B${f2}/$B${r2},$B${cv})'] + [f'=$B${cv}' for c in range(4, 12)], 'pct')
        fc = X.row('Free cash flow to the firm ($B)', [f'={L(c)}{rv}*{L(c)}{cr}' for c in range(2, 12)], 'b', key=True)
        df = X.row('Discount factor (mid-year)', [f'=1/(1+$B${W})^({L(c)}{t}-0.5)' for c in range(2, 12)], 'df')
        pv = X.row('Present value ($B)', [f'={L(c)}{fc}*{L(c)}{df}' for c in range(2, 12)], 'b')
        X.gap(); X.section('Bridge to value per share')
        p10 = X.row('Present value of ten years of cash flow ($B)', [f'=SUM(B{pv}:K{pv})'], 'b')
        tv = X.row('Terminal value ($B)', [f'=K{fc}*(1+$B${gT})/($B${W}-$B${gT})'], 'b', note='FCFF10 x (1 + g) / (discount rate - g)')
        pt = X.row('Present value of terminal value ($B)', [f'=B{tv}/(1+$B${W})^9.5'], 'b')
        ev = X.row('Enterprise value ($B)', [f'=B{p10}+B{pt}'], 'b')
        eq = X.row('Equity value ($B)', [f'=B{ev}+$B${net}'], 'b')
        ps = X.row('Value per share ($)', [f'=B{eq}/$B${sh}'], 'usd', key=True)
        info[name] = dict(ps=ps, fc=fc, t=t, gT=gT, net=net, sh=sh)
    link_scen(S, out, {n: info[n]['ps'] for n in info})
    i = info['Base']; s = "'Base'!"
    sens_block(S, [.07, .075, .08, .085, .09], lambda r: f"=(SUMPRODUCT({s}$B${i['fc']}:$K${i['fc']},1/(1+B{r})^({s}$B${i['t']}:$K${i['t']}-0.5))+{s}$K${i['fc']}*(1+{s}$B${i['gT']})/(B{r}-{s}$B${i['gT']})/(1+B{r})^9.5+{s}$B${i['net']})/{s}$B${i['sh']}")
    return wb


def make_ba():
    wb = Workbook()
    S, out = summary(wb, 'Boeing (BA)', 'Ten-year discounted free cash flow to the firm as production recovers', 190.47, 'ba',
                     wacc=dict(beta=1.35, price=190.47, shares=0.7906, debt=45.6, kd=.06), scen_sheets=None, ps_cells=['', '', ''])
    cases = {'Base': ((2, 6, 9, 10.5, 11.5), 0), 'Bear': ((0.5, 3, 5, 6.5, 7.5), .01), 'Bull': ((3, 8, 11, 13, 14), -.01)}
    info = {}
    for name, (path, shift) in cases.items():
        X = Sheet(wb, name, 'Boeing (BA)', name + ' case: free cash flow back to normal, $ billions', 12); X.widths(40, 11, {'L': 40})
        X.section('Inputs')
        ad = X.row('After-tax interest added back ($B a year)', [2.0], 'b', 'i', 'Turns free cash flow into cash flow to the firm')
        g5 = X.row('Growth in year 6', [.06], 'pct', 'i', 'Fades in a straight line to terminal growth by year 10')
        gT = X.row('Terminal growth', [.03], 'pct', 'i')
        sh_ = X.row('Discount rate shift for this case', [shift], 'pct2', 'i')
        W = X.row('Discount rate', [f'={out["W"]}+B{sh_}'], 'pct2', 'l')
        net = X.row('Net debt ($B)', [-25.6], 'b', 'i', 'Latest balance sheet')
        sh = X.row('Diluted shares (billions)', [0.7906], FMT['n4'], 'i')
        X.gap(); X.section('Projection'); X.header(['Year'] + [str(2026 + t) for t in range(1, 11)])
        t = X.row('Year number', list(range(1, 11)), '0')
        fp = X.row('Free cash flow path ($B)', list(path) + [None] * 5, 'b', 'i', 'Years 1-5: the production recovery')
        g = X.row('Growth', [None] * 5 + [f'=$B${g5}+($B${gT}-$B${g5})*({L(c)}{t}-5)/5' for c in range(7, 12)], 'pct')
        fc = X.row('Free cash flow to the firm ($B)', [f'={L(c)}{fp}+$B${ad}' for c in range(2, 7)] + [f'={L(c - 1)}{X.r}*(1+{L(c)}{g})' for c in range(7, 12)], 'b', key=True)
        df = X.row('Discount factor (mid-year)', [f'=1/(1+$B${W})^({L(c)}{t}-0.5)' for c in range(2, 12)], 'df')
        pv = X.row('Present value ($B)', [f'={L(c)}{fc}*{L(c)}{df}' for c in range(2, 12)], 'b')
        X.gap(); X.section('Bridge to value per share')
        p10 = X.row('Present value of ten years of cash flow ($B)', [f'=SUM(B{pv}:K{pv})'], 'b')
        tv = X.row('Terminal value ($B)', [f'=K{fc}*(1+$B${gT})/($B${W}-$B${gT})'], 'b', note='FCFF10 x (1 + g) / (discount rate - g)')
        pt = X.row('Present value of terminal value ($B)', [f'=B{tv}/(1+$B${W})^9.5'], 'b')
        ev = X.row('Enterprise value ($B)', [f'=B{p10}+B{pt}'], 'b')
        eq = X.row('Equity value ($B)', [f'=B{ev}+$B${net}'], 'b')
        ps = X.row('Value per share ($)', [f'=B{eq}/$B${sh}'], 'usd', key=True)
        info[name] = dict(ps=ps, fc=fc, t=t, gT=gT, net=net, sh=sh)
    link_scen(S, out, {n: info[n]['ps'] for n in info})
    i = info['Base']; s = "'Base'!"
    sens_block(S, [.08, .085, .09, .095], lambda r: f"=(SUMPRODUCT({s}$B${i['fc']}:$K${i['fc']},1/(1+B{r})^({s}$B${i['t']}:$K${i['t']}-0.5))+{s}$K${i['fc']}*(1+{s}$B${i['gT']})/(B{r}-{s}$B${i['gT']})/(1+B{r})^9.5+{s}$B${i['net']})/{s}$B${i['sh']}")
    return wb


def make_gev():
    wb = Workbook()
    S, out = summary(wb, 'GE Vernova (GEV)', 'Ten-year discounted cash flow on the company’s 2028 targets', 890.33, 'gev', scen_sheets=None, ps_cells=['', '', ''])
    cases = {'Base': (.12, .10, .20, .107), 'Bear': (.07, .05, .16, .115), 'Bull': (.16, .14, .23, .097)}
    info = {}
    for name, (g27, g28, mT, Wv) in cases.items():
        X = Sheet(wb, name, 'GE Vernova (GEV)', name + ' case: ten-year free cash flow to the firm, $ billions', 12); X.widths(40, 11, {'L': 40})
        X.section('Inputs')
        rev0 = X.row('Revenue, 2026 ($B)', [46.0], 'b1', 'i', 'Guidance')
        a1 = X.row('Revenue growth, 2027', [g27], 'pct', 'i'); a2 = X.row('Revenue growth, 2028', [g28], 'pct', 'i', 'Then fades to terminal growth by 2036')
        gT = X.row('Terminal growth', [.03], 'pct', 'i')
        m0 = X.row('EBITDA margin, 2026', [.13], 'pct', 'i'); mt = X.row('EBITDA margin, 2028 target', [mT], 'pct', 'i', 'Company 2028 target, reached in two years')
        da = X.row('Depreciation, share of revenue', [.022], 'pct', 'i')
        s2c = X.row('Sales to capital', [4], '0.0', 'i', 'Reinvestment = revenue growth / 4')
        tax = X.row('Tax rate', [.21], 'pct', 'i')
        ron = X.row('Return on new capital, after year 10', [.20], 'pct', 'i')
        W = X.row('Discount rate', [Wv], 'pct2', 'i', 'CAPM with beta about 1.2; no net debt')
        net = X.row('Net cash ($B)', [10.27], 'b', 'i', 'Jun 30 2026: $13.12B cash less $2.85B debt')
        sh = X.row('Diluted shares (billions)', [0.2663], FMT['n4'], 'i')
        X.gap(); X.section('Projection'); X.header(['Year'] + [str(2026 + t) for t in range(1, 11)])
        t = X.row('Year number', list(range(1, 11)), '0')
        g = X.row('Revenue growth', [f'=$B${a1}', f'=$B${a2}'] + [f'=$B${a2}+($B${gT}-$B${a2})*({L(c)}{t}-2)/8' for c in range(4, 12)], 'pct')
        rv = X.row('Revenue ($B)', [f'=$B${rev0}*(1+B{g})'] + [f'={L(c - 1)}{X.r}*(1+{L(c)}{g})' for c in range(3, 12)], 'b1')
        eb = X.row('EBITDA margin', [f'=$B${m0}+($B${mt}-$B${m0})*MIN(1,{L(c)}{t}/2)' for c in range(2, 12)], 'pct')
        oi = X.row('Operating income ($B)', [f'={L(c)}{rv}*({L(c)}{eb}-$B${da})' for c in range(2, 12)], 'b1')
        no = X.row('After-tax operating income ($B)', [f'={L(c)}{oi}*(1-$B${tax})' for c in range(2, 12)], 'b1')
        ri = X.row('Reinvestment ($B)', [f'=({L(c)}{rv}-{("$B$" + str(rev0)) if c == 2 else L(c - 1) + str(rv)})/$B${s2c}' for c in range(2, 12)], 'b1')
        fc = X.row('Free cash flow to the firm ($B)', [f'={L(c)}{no}-{L(c)}{ri}' for c in range(2, 12)], 'b1', key=True)
        df = X.row('Discount factor (mid-year)', [f'=1/(1+$B${W})^({L(c)}{t}-0.5)' for c in range(2, 12)], 'df')
        pv = X.row('Present value ($B)', [f'={L(c)}{fc}*{L(c)}{df}' for c in range(2, 12)], 'b1')
        X.gap(); X.section('Bridge to value per share')
        p10 = X.row('Present value of ten years of cash flow ($B)', [f'=SUM(B{pv}:K{pv})'], 'b1')
        n11 = X.row('Year-11 after-tax operating income ($B)', [f'=K{oi}*(1+$B${gT})*(1-$B${tax})'], 'b1')
        tv = X.row('Terminal value ($B)', [f'=B{n11}*(1-$B${gT}/$B${ron})/($B${W}-$B${gT})'], 'b1', note='NOPAT11 x (1 - g / return on new capital) / (discount rate - g)')
        pt = X.row('Present value of terminal value ($B)', [f'=B{tv}/(1+$B${W})^9.5'], 'b1')
        ev = X.row('Enterprise value ($B)', [f'=B{p10}+B{pt}'], 'b1')
        eq = X.row('Equity value ($B)', [f'=B{ev}+$B${net}'], 'b1')
        ps = X.row('Value per share ($)', [f'=B{eq}/$B${sh}'], 'usd', key=True)
        info[name] = dict(ps=ps, fc=fc, t=t, gT=gT, net=net, sh=sh, oi=oi, tax=tax, ron=ron)
    link_scen(S, out, {n: info[n]['ps'] for n in info})
    i = info['Base']; s = "'Base'!"
    sens_block(S, [.085, .09, .095, .10, .107], lambda r: f"=(SUMPRODUCT({s}$B${i['fc']}:$K${i['fc']},1/(1+B{r})^({s}$B${i['t']}:$K${i['t']}-0.5))+{s}$K${i['oi']}*(1+{s}$B${i['gT']})*(1-{s}$B${i['tax']})*(1-{s}$B${i['gT']}/{s}$B${i['ron']})/(B{r}-{s}$B${i['gT']})/(1+B{r})^9.5+{s}$B${i['net']})/{s}$B${i['sh']}")
    return wb


def make_awk():
    wb = Workbook()
    S, out = summary(wb, 'American Water Works (AWK)', 'Dividend discount model', 135.79, 'awk', ke=0.70, scen_sheets=None, ps_cells=['', '', ''])
    cases = {'Base': (.08, .035, 0), 'Bear': (.06, .03, .01), 'Bull': (.09, .04, -.005)}
    info = {}
    for name, (g, gT_, shift) in cases.items():
        X = Sheet(wb, name, 'American Water Works (AWK)', name + ' case: dividends per share, $', 12); X.widths(40, 11, {'L': 40})
        X.section('Inputs')
        d0 = X.row('Dividend, last 12 months ($)', [3.58], 'usd', 'i', 'Company filings')
        gg = X.row('Dividend growth, years 1-5', [g], 'pct', 'i', 'Company 7-9% EPS and dividend target')
        gT = X.row('Long-run growth, from year 10', [gT_], 'pct', 'i', 'Growth fades to it over years 6-10')
        sh_ = X.row('Cost of equity shift for this case', [shift], 'pct2', 'i')
        k = X.row('Cost of equity', [f'={out["W"]}+B{sh_}'], 'pct2', 'l')
        X.gap(); X.section('Dividends'); X.header(['Year'] + [str(2026 + t) for t in range(1, 11)])
        t = X.row('Year number', list(range(1, 11)), '0')
        gr = X.row('Dividend growth', [f'=$B${gg}'] * 5 + [f'=$B${gg}+($B${gT}-$B${gg})*({L(c)}{t}-5)/5' for c in range(7, 12)], 'pct')
        dv = X.row('Dividend per share ($)', [f'=$B${d0}*(1+B{gr})'] + [f'={L(c - 1)}{X.r}*(1+{L(c)}{gr})' for c in range(3, 12)], 'usd', key=True)
        df = X.row('Discount factor', [f'=1/(1+$B${k})^{L(c)}{t}' for c in range(2, 12)], 'df')
        pv = X.row('Present value ($)', [f'={L(c)}{dv}*{L(c)}{df}' for c in range(2, 12)], 'usd')
        X.gap(); X.section('Value per share')
        p10 = X.row('Present value of ten years of dividends ($)', [f'=SUM(B{pv}:K{pv})'], 'usd')
        tv = X.row('Terminal value ($)', [f'=K{dv}*(1+$B${gT})/($B${k}-$B${gT})'], 'usd', note='D10 x (1 + g) / (cost of equity - g)')
        pt = X.row('Present value of terminal value ($)', [f'=B{tv}/(1+$B${k})^10'], 'usd')
        ps = X.row('Value per share ($)', [f'=B{p10}+B{pt}'], 'usd', key=True)
        info[name] = dict(ps=ps, dv=dv, t=t, gT=gT)
    link_scen(S, out, {n: info[n]['ps'] for n in info})
    i = info['Base']; s = "'Base'!"
    sens_block(S, [.07, .075, .08, .085, .09], lambda r: f"=SUMPRODUCT({s}$B${i['dv']}:$K${i['dv']},1/(1+B{r})^{s}$B${i['t']}:$K${i['t']})+{s}$K${i['dv']}*(1+{s}$B${i['gT']})/(B{r}-{s}$B${i['gT']})/(1+B{r})^10",
               col='Cost of equity (base case)', note='Each row reprices the base case at that cost of equity.')
    return wb


def make_jpm():
    wb = Workbook()
    S, out = summary(wb, 'JPMorgan Chase (JPM)', 'Excess-return model: value = book value x (ROE - g) / (cost of equity - g)', 335.26, 'jpm', ke=1.046, scen_sheets=None, ps_cells=['', '', ''])
    vr = out['rows'][0]
    # the model fits in four rows, so it lives on the summary sheet above the scenario values
    X = Sheet(wb, 'Model', 'JPMorgan Chase (JPM)', 'Excess return on book value, by scenario', 5); X.widths(46, 14, {'E': 50})
    X.section('Inputs and value'); X.header(['', 'Bear', 'Base', 'Bull'])
    bv = X.row('Book value per share ($)', [132.30] * 3, 'usd', 'i', 'Latest 10-Q')
    roe = X.row('Return on equity, through the cycle', [.145, .16, .18], 'pct', 'i', 'Company target range')
    g = X.row('Long-run growth', [.045] * 3, 'pct', 'i')
    sh = X.row('Cost of equity shift', [.005, 0, -.005], 'pct2', 'i')
    k = X.row('Cost of equity', [f'={out["W"]}+{c}{sh}' for c in 'BCD'], 'pct2', 'l')
    m = X.row('(ROE - g) / (cost of equity - g)', [f'=({c}{roe}-{c}{g})/({c}{k}-{c}{g})' for c in 'BCD'], '0.000')
    ps = X.row('Value per share ($)', [f'={c}{bv}*{c}{m}' for c in 'BCD'], 'usd', key=True)
    for c in 'BCD':
        cell = S.ws[f'{c}{vr}']; cell.value = f"='Model'!{c}{ps}"; cell.font = font(color=GREEN); cell.number_format = FMT['usd']
    sens_block(S, [.09, .095, .10], lambda r: f"='Model'!$C${bv}*('Model'!$C${roe}-'Model'!$C${g})/(B{r}-'Model'!$C${g})", col='Cost of equity (base case)', note='Each row reprices the base case at that cost of equity.')
    return wb


def link_scen(S, out, ps):
    vr = out['rows'][0]
    for c, name in zip('BCD', ('Bear', 'Base', 'Bull')):
        cell = S.ws[f'{c}{vr}']; cell.value = f"='{name}'!$B${ps[name]}"; cell.font = font(color=GREEN); cell.number_format = FMT['usd']


def sens_block(S, Wlist, f, col='Discount rate (base case)', note='Each row reprices the base case at that discount rate; the cash flows themselves do not change.', usd=True):
    S.gap(); S.section('Sensitivity'); S.header(['Base case, repriced at', col.replace(' (base case)', ''), 'Value per share ($)' if usd else 'Value ($B)'])
    for W in Wlist:
        r = S.r
        S.ws.cell(r, 1).border = Border(bottom=THIN)
        cc = S.ws.cell(r, 2, W); cc.number_format = FMT['pct2']; cc.font = font(color=BLUE); cc.fill = fill(INFILL)
        v = S.ws.cell(r, 3, f(r)); v.number_format = FMT['usd'] if usd else FMT['b']; v.font = font(); v.border = Border(bottom=THIN); S.r += 1
    S.note(note)
    about(S)


# ---------------------------------------------------------------- scenario models and the memory cycle model
def make_scenario(slug, title, cases, kind, unit, price):
    usd = unit == 1
    wb = Workbook()
    S, out = summary(wb, title, 'Scenario model: 2030 earning power, capitalised and discounted back four years, plus cash flow along the way', price, 'new_coverage',
                     scen_sheets=None, ps_cells=['', '', ''], unit='$ per share' if usd else '$B, whole company')
    X = Sheet(wb, 'Model', title, 'Bear, base and bull in one table, $ billions', 5); X.widths(48, 14, {'E': 52})
    X.section('Inputs'); X.header(['', 'Bear', 'Base', 'Bull'])
    rv = X.row('Revenue in 2030 ($B)', [c[0] / 1e9 for c in cases], 'b', 'i')
    if kind == 'pe':
        mg = X.row('Operating margin in 2030', [c[1] for c in cases], 'pct', 'i')
        tx = X.row('Tax rate', [.21] * 3, 'pct', 'i', 'U.S. federal rate')
        mu = X.row('Exit multiple of after-tax operating profit', [c[2] for c in cases], 'x', 'i')
    else:
        mu = X.row('Exit value to sales', [c[2] for c in cases], 'x', 'i', 'For a young company without steady profit')
    r = X.row('Discount rate', [c[3] for c in cases], 'pct', 'i')
    n = X.row('Years discounted', [c[4] for c in cases], '0', 'i')
    nc = X.row('Net cash ($B)', [c[5] / 1e9 for c in cases], 'b', 'i')
    if usd:
        sh = X.row('Shares by 2030 (billions)', [c[6] / 1e9 for c in cases], FMT['n4'], 'i')
    has_fcf = cases[1][8] is not None
    if has_fcf:
        f0 = X.row('Free cash flow this year ($B)', [c[8] / 1e9 for c in cases], 'b', 'i', 'Operating cash flow less capital spending, last twelve months')
        cv = X.row('Free cash flow in 2030, share of after-tax profit', [.8] * 3, 'pct', 'i', 'The rest is reinvested; zero for a company without profit yet' if kind != 'pe' else 'The rest is reinvested')
    X.gap(); X.section('Value'); X.header(['', 'Bear', 'Base', 'Bull'])
    if kind == 'pe':
        ap = X.row('After-tax operating profit, 2030 ($B)', [f'={c}{rv}*{c}{mg}*(1-{c}{tx})' for c in 'BCD'], 'b')
        v30 = X.row('Value in 2030 ($B)', [f'={c}{ap}*{c}{mu}' for c in 'BCD'], 'b')
    else:
        v30 = X.row('Value in 2030 ($B)', [f'={c}{rv}*{c}{mu}' for c in 'BCD'], 'b')
    vt = X.row('Value today ($B)', [f'={c}{v30}/(1+{c}{r})^{c}{n}' for c in 'BCD'], 'b')
    if has_fcf:
        fT = X.row('Free cash flow in 2030 ($B)', [(f'={c}{ap}*{c}{cv}' if kind == 'pe' else '=0') for c in 'BCD'], 'b')
        yrs_rows = [X.row(f'Free cash flow, year {k} ($B)', [f'={c}{f0}+({c}{fT}-{c}{f0})*{k}/{c}{n}' for c in 'BCD'], 'b') for k in range(1, 5)]
        pvf = X.row('Present value of free cash flow, years 1-4 ($B)', [f'=' + '+'.join(f'{c}{yr}/(1+{c}{r})^{k}' for k, yr in enumerate(yrs_rows, 1)) for c in 'BCD'], 'b')
        eq = X.row('Plus cash flow and net cash: equity value ($B)', [f'={c}{vt}+{c}{pvf}+{c}{nc}' for c in 'BCD'], 'b', key=not usd)
    else:
        eq = X.row('Plus net cash: equity value ($B)', [f'={c}{vt}+{c}{nc}' for c in 'BCD'], 'b', key=not usd)
    if usd:
        ps = X.row('Value per share ($)', [f'={c}{eq}/{c}{sh}' for c in 'BCD'], 'usd', key=True)
    else:
        ps = eq
    vr = out['rows'][0]
    for c in 'BCD':
        cell = S.ws[f'{c}{vr}']; cell.value = f"='Model'!{c}{ps}"; cell.font = font(color=GREEN); cell.number_format = FMT['usd'] if usd else FMT['b']
    base_r = cases[1][3]
    def f(rr):
        extra = '+'.join(f"'Model'!$C${yr}/(1+B{rr})^{k}" for k, yr in enumerate(yrs_rows, 1)) if has_fcf else '0'
        return f"=('Model'!$C${v30}/(1+B{rr})^'Model'!$C${n}+{extra}+'Model'!$C${nc})" + (f"/'Model'!$C${sh}" if usd else '')
    sens_block(S, [base_r - .02, base_r - .01, base_r, base_r + .01, base_r + .02], f, usd=usd, note='Each row reprices the base case at that discount rate.')
    return wb


def make_cycle(slug, title, C, price, years):
    wb = Workbook()
    S, out = summary(wb, title, 'Cycle model: four years of free cash flow at the cycle’s prices, then a mid-cycle exit value', price, 'new_coverage', scen_sheets=None, ps_cells=['', '', ''])
    cases = [C['bear'], C['base'], C['bull']]
    X = Sheet(wb, 'Model', title, 'Bear, base and bull in one table, $ billions, fiscal years', 5); X.widths(48, 14, {'E': 52})
    X.section('Inputs'); X.header(['', 'Bear', 'Base', 'Bull'])
    rv = [X.row(f'Revenue, {y} ($B)', [c[0][i] / 1e9 for c in cases], 'b', 'i') for i, y in enumerate(years)]
    fm = [X.row(f'Free cash flow margin, {y}', [c[1][i] for c in cases], 'pct', 'i') for i, y in enumerate(years)]
    nr = X.row('Mid-cycle revenue ($B)', [c[2] / 1e9 for c in cases], 'b', 'i')
    nm = X.row('Mid-cycle operating margin', [c[3] for c in cases], 'pct', 'i')
    tx = X.row('Tax rate', [.21] * 3, 'pct', 'i')
    mu = X.row('Exit multiple of after-tax operating profit', [c[4] for c in cases], 'x', 'i')
    r = X.row('Discount rate', [c[5] for c in cases], 'pct', 'i')
    nc = X.row('Net cash ($B)', [c[6] / 1e9 for c in cases], 'b', 'i')
    sh = X.row('Shares by 2030 (billions)', [c[7] / 1e9 for c in cases], FMT['n4'], 'i')
    X.gap(); X.section('Value'); X.header(['', 'Bear', 'Base', 'Bull'])
    pvs = []
    for i, y in enumerate(years):
        f = X.row(f'Free cash flow, {y} ($B)', [f'={c}{rv[i]}*{c}{fm[i]}' for c in 'BCD'], 'b')
        pvs.append(X.row(f'Present value, {y} ($B)', [f'={c}{f}/(1+{c}{r})^{i + 1}' for c in 'BCD'], 'b'))
    ex = X.row('Exit value at the end of year 4 ($B)', [f'={c}{nr}*{c}{nm}*(1-{c}{tx})*{c}{mu}' for c in 'BCD'], 'b')
    pe = X.row('Present value of the exit value ($B)', [f'={c}{ex}/(1+{c}{r})^4' for c in 'BCD'], 'b')
    eq = X.row('Equity value ($B)', [f'=' + '+'.join(f'{c}{p}' for p in pvs) + f'+{c}{pe}+{c}{nc}' for c in 'BCD'], 'b')
    ps = X.row('Value per share ($)', [f'={c}{eq}/{c}{sh}' for c in 'BCD'], 'usd', key=True)
    vr = out['rows'][0]
    for c in 'BCD':
        cell = S.ws[f'{c}{vr}']; cell.value = f"='Model'!{c}{ps}"; cell.font = font(color=GREEN); cell.number_format = FMT['usd']
    rb = C['base'][5]
    def f(rr):
        parts = '+'.join(f"'Model'!$C${rv[i]}*'Model'!$C${fm[i]}/(1+B{rr})^{i + 1}" for i in range(len(years)))
        return f"=({parts}+'Model'!$C${ex}/(1+B{rr})^4+'Model'!$C${nc})/'Model'!$C${sh}"
    sens_block(S, [rb - .02, rb - .01, rb, rb + .01, rb + .02], f, note='Each row reprices the base case at that discount rate.')
    return wb


# ---------------------------------------------------------------- build all, then check
def run_script(name):
    ns = {}
    old = os.getcwd(); os.chdir(HERE)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(open(os.path.join(HERE, name + '.py')).read(), ns)
    finally:
        os.chdir(old)
    return ns


def all_books():
    import holdings, coverage
    R = dict(holdings.R); R.update(coverage.R)
    books = {}
    for key, c in generic_cases().items():
        books[c['slug']] = (key, make_generic(key, c))
    books['l3harris'] = ('LHX', make_lhx()); books['boeing'] = ('BA', make_ba()); books['gev'] = ('GEV', make_gev())
    books['american-water'] = ('AWK', make_awk()); books['jpmorgan'] = ('JPM', make_jpm())
    ns0 = run_script('new_coverage')
    NAMES = {'SPCX': ('spacex', 'SpaceX (SPCX)', 'SPCX', 1), 'FLY': ('firefly', 'Firefly Aerospace (FLY)', 'FLY', 1), 'KTOS': ('kratos', 'Kratos Defense (KTOS)', 'KTOS', 1),
             'AXON': ('axon', 'Axon Enterprise (AXON)', 'AXON', 1), 'PLTR': ('palantir', 'Palantir Technologies (PLTR)', 'PLTR', 1), 'AMD': ('amd', 'Advanced Micro Devices (AMD)', 'AMD', 1),
             'ANTHROPIC': ('anthropic', 'Anthropic (private)', 'Anthropic', 1e9), 'OPENAI': ('openai', 'OpenAI (private)', 'OpenAI', 1e9),
             'ANDURIL': ('anduril', 'Anduril (private)', 'Anduril', 1e9), 'BLOOMBERG': ('bloomberg', 'Bloomberg LP (private)', 'Bloomberg', 1e9)}
    SC = {}
    for t, (slug, title, reg, unit) in NAMES.items():
        C = ns0['REG'][reg]; cs = [tuple(C[k]) + (('pe', None) if len(C[k]) == 7 else ()) for k in ('bear', 'base', 'bull')]
        SC[t] = (slug, title, cs, cs[1][7], unit)
    for t, (slug, title, cases, kind, unit) in SC.items():
        books[slug] = (t, make_scenario(slug, title, cases, kind, unit, R[t]['price']))
    ns = run_script('new_coverage')
    books['micron'] = ('MU', make_cycle('micron', 'Micron Technology (MU)', ns['MU'], R['MU']['price'], ['FY2027', 'FY2028', 'FY2029', 'FY2030']))
    books['sandisk'] = ('SNDK', make_cycle('sandisk', 'Sandisk (SNDK)', ns['SNDK'], R['SNDK']['price'], ['FY2027', 'FY2028', 'FY2029', 'FY2030']))
    books['sk-hynix'] = ('SKHY', make_cycle('sk-hynix', 'SK hynix (SKHY), per ADR', ns['SKHY'], R['SKHY']['price'], ['2027', '2028', '2029', '2030']))
    return books


def write_all():
    os.makedirs(OUT, exist_ok=True)
    books = all_books()
    for slug, (t, wb) in books.items():
        wb.active = 0
        wb.properties.creator = 'LDB Finance'; wb.properties.title = wb['Summary']['A2'].value
        wb.save(os.path.join(OUT, slug + '.xlsx'))
    return books


def check(books):
    """recalculate every file in LibreOffice, then compare the scenario values with the model scripts"""
    import export
    with contextlib.redirect_stdout(io.StringIO()):
        vals = export.main()
    from openpyxl import load_workbook
    recalc = os.environ.get('RECALC') or ''
    bad = 0
    for slug, (t, _) in books.items():
        path = os.path.join(OUT, slug + '.xlsx')
        if recalc:
            res = subprocess.run([sys.executable, recalc, path, '60'], capture_output=True, text=True)
            try:
                j = json.loads(res.stdout[res.stdout.index('{'):])
            except Exception:
                print('  recalc failed', slug, res.stdout[-300:], res.stderr[-300:]); bad += 1; continue
            if j.get('status') != 'success':
                print('  ERRORS', slug, j); bad += 1
        wb = load_workbook(path, data_only=True); ws = wb['Summary']
        row = next(r for r in range(1, ws.max_row + 1) if str(ws.cell(r, 1).value or '').startswith('Value ('))
        got = [ws.cell(row, c).value for c in (2, 3, 4)]
        b, be, bu = vals[t]
        unit = 1e9 if t in ('ANTHROPIC', 'OPENAI', 'ANDURIL', 'BLOOMBERG') else 1
        want = [be, b, bu]
        for g, w in zip(got, want):
            if g is None or abs(g - w) > max(0.01, abs(w) * 1e-6):
                print(f'  MISMATCH {t}: workbook {got}, model {want}'); bad += 1; break
    print('checked', len(books), 'workbooks;', 'all match' if not bad else f'{bad} problems')
    return bad


if __name__ == '__main__':
    bk = write_all()
    print('wrote', len(bk), 'workbooks')
    if '--check' in sys.argv:
        sys.exit(1 if check(bk) else 0)
