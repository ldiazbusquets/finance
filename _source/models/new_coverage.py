"""Scenario values for SpaceX, Firefly and the private AI and defense companies (written Oct 21, 2026).
Method: revenue and operating margin in 2030, after-tax operating profit capitalised at an exit multiple,
discounted back four years, plus net cash, divided by shares. Rough by design: these are young businesses."""
T = .21
def val(rev, m, mult, disc, yrs, net, shares, kind='pe'):
    ev = rev * m * (1 - T) * mult if kind == 'pe' else rev * mult   # 'ps' = exit EV/sales
    return (ev / (1 + disc) ** yrs + net) / shares

def show(name, cases, price=None, unit=1, label='per share'):
    v = {k: val(*c) for k, c in cases.items()}
    wt = .25 * v['bear'] + .5 * v['base'] + .25 * v['bull']
    f = lambda x: f'{x / unit:,.0f}'
    print(f'{name}: bear {f(v["bear"])} base {f(v["base"])} bull {f(v["bull"])} weighted {f(wt)} {label}' + (f'  price {price}' if price else ''))
    return v, wt

# SpaceX: 13.57B shares, $89.9B cash, $38.8B debt (Sep 30), discount 12%
N = 89.9e9 - 38.8e9
show('SPCX', {'bear': (250e9, .22, 20, .12, 4, N, 13.57e9), 'base': (500e9, .28, 22, .12, 4, N, 13.57e9), 'bull': (900e9, .32, 25, .12, 4, N, 13.57e9)}, 162.57)
# Firefly: 167.4M shares now, more later; discount 15%; exit EV/sales
show('FLY', {'bear': (0.7e9, 0, 2, .15, 4, 0, 200e6, 'ps'), 'base': (1.2e9, 0, 5, .15, 4, .2e9, 185e6, 'ps'), 'bull': (2.0e9, 0, 8, .15, 4, .2e9, 180e6, 'ps')}, 17.41)
# Private companies: equity value in $B (shares = 1), discount 15% (13% Anduril)
show('Anthropic', {'bear': (120e9, .15, 20, .15, 4, 0, 1), 'base': (250e9, .30, 25, .15, 4, 0, 1), 'bull': (450e9, .40, 25, .15, 4, 0, 1)}, unit=1e9, label='$B')
show('OpenAI', {'bear': (150e9, .10, 20, .15, 4, 0, 1), 'base': (280e9, .25, 25, .15, 4, 0, 1), 'bull': (450e9, .35, 25, .15, 4, 0, 1)}, unit=1e9, label='$B')
show('Anduril', {'bear': (8e9, .05, 20, .13, 4, 0, 1), 'base': (14e9, .12, 25, .13, 4, 0, 1), 'bull': (22e9, .18, 35, .13, 4, 0, 1)}, unit=1e9, label='$B')
