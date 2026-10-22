"""Scenario values for SpaceX, Firefly and the private AI and defense companies (written Oct 21, 2026).
Method: revenue and operating margin in 2030, after-tax operating profit capitalised at an exit multiple,
discounted back four years, plus net cash, divided by shares. Rough by design: these are young businesses."""
T = .21
CONV = .80   # free cash flow in 2030 as a share of after-tax operating profit (the rest is reinvested)
REG = {}     # every case set, for export.py and xlsx_models.py


def interim(rev, m, disc, yrs, fcf0, kind='pe'):
    """Free cash flow between now and 2030: a straight line from this year's level to CONV x 2030 after-tax
    operating profit (zero for a 'ps' company not yet profitable). Returns (flows, present value)."""
    if fcf0 is None:
        return [], 0.0
    fT = rev * m * (1 - T) * CONV if kind == 'pe' else 0.0
    flows = [fcf0 + (fT - fcf0) * t / yrs for t in range(1, yrs + 1)]
    return flows, sum(f / (1 + disc) ** t for t, f in enumerate(flows, 1))


def val(rev, m, mult, disc, yrs, net, shares, kind='pe', fcf0=None):
    """value = PV of free cash flow, years 1-4 + PV of the 2030 exit value + net cash, per share.
    fcf0 = this year's free cash flow; None for private companies, whose interim cash burn is funded by new
    shares (so it shows up as dilution, which these whole-company values leave out)."""
    ev = rev * m * (1 - T) * mult if kind == 'pe' else rev * mult   # 'ps' = exit EV/sales
    return (ev / (1 + disc) ** yrs + interim(rev, m, disc, yrs, fcf0, kind)[1] + net) / shares

def show(name, cases, price=None, unit=1, label='per share'):
    REG[name] = cases
    v = {k: val(*c) for k, c in cases.items()}
    wt = .25 * v['bear'] + .5 * v['base'] + .25 * v['bull']
    f = lambda x: f'{x / unit:,.0f}'
    print(f'{name}: bear {f(v["bear"])} base {f(v["base"])} bull {f(v["bull"])} weighted {f(wt)} {label}' + (f'  price {price}' if price else ''))
    return v, wt

# SpaceX: 13.57B shares, $89.9B cash, $38.8B debt (Sep 30), discount 12%
N = 89.9e9 - 38.8e9
show('SPCX', {'bear': (250e9, .22, 20, .12, 4, N, 13.57e9, 'pe', -68e9), 'base': (500e9, .28, 22, .12, 4, N, 13.57e9, 'pe', -68e9), 'bull': (900e9, .32, 25, .12, 4, N, 13.57e9, 'pe', -68e9)}, 162.57)
# Firefly: 167.4M shares now, more later; discount 15%; exit EV/sales
show('FLY', {'bear': (0.7e9, 0, 2, .15, 4, 0, 200e6, 'ps', -0.23e9), 'base': (1.2e9, 0, 5, .15, 4, .2e9, 185e6, 'ps', -0.23e9), 'bull': (2.0e9, 0, 8, .15, 4, .2e9, 180e6, 'ps', -0.23e9)}, 17.41)
# Private companies: equity value in $B (shares = 1), discount 15% (13% Anduril)
show('Anthropic', {'bear': (120e9, .15, 20, .15, 4, 0, 1), 'base': (250e9, .30, 25, .15, 4, 0, 1), 'bull': (450e9, .40, 25, .15, 4, 0, 1)}, unit=1e9, label='$B')
show('OpenAI', {'bear': (150e9, .10, 20, .15, 4, 0, 1), 'base': (280e9, .25, 25, .15, 4, 0, 1), 'bull': (450e9, .35, 25, .15, 4, 0, 1)}, unit=1e9, label='$B')
show('Anduril', {'bear': (8e9, .05, 20, .13, 4, 0, 1), 'base': (14e9, .12, 25, .13, 4, 0, 1), 'bull': (22e9, .18, 35, .13, 4, 0, 1)}, unit=1e9, label='$B')
# Kratos: 187.7M shares now, ~200M by 2030 (stock pay); net cash ~$1.3B (cash $1.44B less leases), less ~$0.1B 2026 burn
# discount 10% (CAPM: 5.15% + 1.1 beta x 4.5%)
show('KTOS', {'bear': (2.6e9, .06, 18, .10, 4, 1.2e9, 200e6, 'pe', -0.13e9), 'base': (3.2e9, .09, 22, .10, 4, 1.2e9, 200e6, 'pe', -0.13e9), 'bull': (4.0e9, .12, 28, .10, 4, 1.2e9, 200e6, 'pe', -0.13e9)}, 38.81)
# Bloomberg LP: ~$15B revenue (Forbes/BCG estimates), mature, discount 9% (beta ~0.8)
show('Bloomberg', {'bear': (16e9, .22, 18, .09, 4, 0, 1), 'base': (18e9, .28, 22, .09, 4, 0, 1), 'bull': (20e9, .33, 26, .09, 4, 0, 1)}, unit=1e9, label='$B')
# Axon: 81.2M shares now, ~88M by 2030 (stock pay; target <2.5% a year); net debt ~$1.1B (Jun 30, before and after the $1B convert)
# discount 11% (CAPM: 5.15% + 1.44 beta x 4.5% = 11.6%, rounded down for 95% recurring revenue); margins are operating margin after stock pay
show('AXON', {'bear': (6.5e9, .15, 25, .11, 4, -1.1e9, 88e6, 'pe', 0.14e9), 'base': (8.5e9, .20, 30, .11, 4, -1.1e9, 88e6, 'pe', 0.14e9), 'bull': (10.5e9, .25, 35, .11, 4, -1.1e9, 88e6, 'pe', 0.14e9)}, 396.30)

# ---------------------------------------------------------------- added Oct 21, 2026: Palantir, AMD, Micron, Sandisk
# Discount rates are CAPM: 5.15% 10-year yield + beta x 4.5% premium, rounded to a whole percent.
# Palantir: beta 2.01 -> 14%. 2026 revenue guided at $8.15B. Net cash $9.4B (no debt, Jun 30). ~2.6B diluted shares by 2030.
# Margins are GAAP operating margin, after stock pay.
show('PLTR', {'bear': (18e9, .40, 25, .14, 4, 9.4e9, 2.6e9, 'pe', 3.36e9), 'base': (28e9, .50, 30, .14, 4, 9.4e9, 2.6e9, 'pe', 3.36e9), 'bull': (45e9, .55, 45, .14, 4, 9.4e9, 2.6e9, 'pe', 3.36e9)}, 201.72)
# AMD: beta 1.59 -> 12%. Net cash $9.9B ($13.1B cash and investments less $3.2B debt, Jun 27).
# 1.63B shares plus up to 160M from the OpenAI warrant -> 1.80B by 2030.
show('AMD', {'bear': (100e9, .22, 20, .12, 4, 9.9e9, 1.80e9, 'pe', 8.40e9), 'base': (150e9, .30, 25, .12, 4, 9.9e9, 1.80e9, 'pe', 8.40e9), 'bull': (200e9, .35, 30, .12, 4, 9.9e9, 1.80e9, 'pe', 8.40e9)}, 552.72)


def cyc(revs, fcfm, nrev, nm, mult, disc, net, shares):
    """Memory makers: four years of free cash flow at the cycle's prices, then a mid-cycle exit value.
    value = sum(revenue_t x FCF margin_t / (1 + r)^t) + (normal revenue x normal margin x (1 - tax) x multiple) / (1 + r)^4 + net cash"""
    pv = sum(r * m / (1 + disc) ** (i + 1) for i, (r, m) in enumerate(zip(revs, fcfm)))
    tv = nrev * nm * (1 - T) * mult / (1 + disc) ** len(revs)
    return (pv + tv + net) / shares


def showc(name, cases, price):
    v = {k: cyc(*c) for k, c in cases.items()}
    wt = .25 * v['bear'] + .5 * v['base'] + .25 * v['bull']
    print(f'{name}: bear {v["bear"]:,.0f} base {v["base"]:,.0f} bull {v["bull"]:,.0f} weighted {wt:,.0f} per share  price {price}')
    return v, wt

# Micron: beta 2.03 -> 14%. Fiscal 2026 revenue $133.2B; Q1 FY27 guided at $61.5B. Net cash $68.3B (Sep 3).
# Capex above $50B in fiscal 2027; Q4 FY26 free cash flow was 61% of revenue (79% operating cash flow less capex). ~1.10B shares by 2030 after buybacks (1.13B today).
MU = {'bear': ([220e9, 200e9, 130e9, 110e9], [.50, .38, .15, .05], 130e9, .25, 10, .14, 68.3e9, 1.10e9),
      'base': ([250e9, 280e9, 200e9, 150e9], [.55, .50, .30, .15], 170e9, .35, 12, .14, 68.3e9, 1.10e9),
      'bull': ([290e9, 350e9, 330e9, 300e9], [.58, .58, .52, .45], 280e9, .45, 14, .14, 68.3e9, 1.10e9)}
showc('MU', MU, 913.67)
# Sandisk: beta 2.09 -> 15%. Fiscal 2026 revenue $20.2B; Q1 FY27 guided at $10.3-10.8B. Cash $4.8B, no debt (Jul 3).
# Q4 FY26 free cash flow was 79% of revenue. ~150M shares by 2030 (155M diluted guided for Q1, less buybacks from the $15.5B authorisation).
SNDK = {'bear': ([40e9, 35e9, 20e9, 16e9], [.60, .42, .10, 0], 18e9, .12, 8, .15, 4.8e9, 150e6),
        'base': ([45e9, 50e9, 35e9, 25e9], [.65, .60, .35, .20], 28e9, .25, 10, .15, 4.8e9, 150e6),
        'bull': ([52e9, 65e9, 65e9, 60e9], [.68, .65, .62, .60], 50e9, .40, 12, .15, 4.8e9, 150e6)}
showc('SNDK', SNDK, 1378.22)
# SK hynix (ADR SKHY, 10 ADRs = 1 Korean share): values per ADR in dollars, won converted at 1,327 per dollar.
# Beta about 1.6 plus Korea and memory-cycle risk -> 14%, as for Micron. Q2 2026 net cash KRW 69.4T ($52B) plus ~$28B from the July ADR offering -> ~$80B.
# ~745.8M common shares after the offering (728.0M + 17.79M), ~740M outstanding net of treasury -> 7.40B ADR-equivalents.
SKHY = {'bear': ([280e9, 230e9, 150e9, 120e9], [.45, .35, .10, .05], 150e9, .25, 10, .14, 80e9, 7.40e9),
        'base': ([330e9, 350e9, 240e9, 180e9], [.50, .45, .28, .15], 210e9, .35, 12, .14, 80e9, 7.40e9),
        'bull': ([380e9, 450e9, 400e9, 350e9], [.55, .52, .45, .40], 320e9, .45, 14, .14, 80e9, 7.40e9)}
showc('SKHY', SKHY, 131.69)
