"""Link-preview images (1200x630) for reports and research tools, written to og/<page>.jpg.
Run after build.py when a report's call or value changes:  python3 og.py
Needs Playwright with Chromium, and the Manrope and Geist Mono fonts (npm @fontsource/manrope, @fontsource/geist-mono);
set FONTS to the folder that holds their .woff2 files."""
import os, sys, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages'))
import holdings, coverage, notes

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'og')
FONTS = os.environ.get('FONTS', '')


def font(name):
    for d, _, fs in os.walk(FONTS):
        if name in fs:
            return base64.b64encode(open(os.path.join(d, name), 'rb').read()).decode()
    return ''


CSS = '''
@font-face { font-family: M; font-weight: 300; src: url(data:font/woff2;base64,%s); }
@font-face { font-family: M; font-weight: 400; src: url(data:font/woff2;base64,%s); }
@font-face { font-family: M; font-weight: 500; src: url(data:font/woff2;base64,%s); }
@font-face { font-family: G; font-weight: 500; src: url(data:font/woff2;base64,%s); }
* { margin: 0; box-sizing: border-box; }
body { width: 1200px; height: 630px; background: #0C0A08; color: #F4EDE4; font-family: M, sans-serif; position: relative; overflow: hidden; }
.glow { position: absolute; right: -180px; top: -220px; width: 760px; height: 760px; border-radius: 50%%; background: radial-gradient(circle, rgba(176,122,79,.30), rgba(176,122,79,0) 65%%); }
.grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(244,237,228,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(244,237,228,.035) 1px, transparent 1px); background-size: 60px 60px; }
.in { position: absolute; inset: 64px 72px; display: flex; flex-direction: column; }
.brand { display: flex; align-items: center; gap: 12px; font-weight: 500; font-size: 26px; letter-spacing: -.01em; }
.brand span { color: #A8998A; font-weight: 400; }
.eye { margin-top: auto; font: 500 18px G, monospace; letter-spacing: .12em; text-transform: uppercase; color: #C58B5C; }
h1 { font-weight: 300; font-size: 92px; line-height: 1; letter-spacing: -.045em; margin-top: 18px; }
h1 em { font-style: normal; color: #A8998A; }
.row { display: flex; gap: 14px; margin-top: 36px; }
.cell { border: 1px solid rgba(244,237,228,.16); border-radius: 18px; padding: 16px 24px; min-width: 190px; background: rgba(244,237,228,.03); }
.cell.cu { background: linear-gradient(135deg, #8C593A, #723F20 55%%, #B07A4F); border-color: transparent; }
.cell small { display: block; font: 500 13px G, monospace; letter-spacing: .1em; text-transform: uppercase; color: #A8998A; }
.cell.cu small { color: rgba(255,248,239,.75); }
.cell b { display: block; font-weight: 400; font-size: 40px; letter-spacing: -.03em; margin-top: 6px; }
.sub { margin-top: 28px; font-size: 26px; line-height: 1.4; color: #C9BCAE; max-width: 980px; }
'''


def card(eye, h1, cells=None, sub=''):
    cs = ''.join(f'<div class="cell{" cu" if i == 0 else ""}"><small>{a}</small><b>{b}</b></div>' for i, (a, b) in enumerate(cells or []))
    logo = '<svg viewBox="0 0 24 24" width="30" height="30"><path d="M3 9.5V4.8A1.8 1.8 0 0 1 4.8 3h4.7M14.5 21h4.7a1.8 1.8 0 0 0 1.8-1.8v-4.7" fill="none" stroke="#C58B5C" stroke-width="1.7" stroke-linecap="round"/><circle cx="12" cy="12" r="2.6" fill="#C58B5C"/></svg>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="grid"></div><div class="glow"></div><div class="in">'
            f'<div class="brand">{logo}LDB <span>Finance</span></div><div class="eye">{eye}</div><h1>{h1}</h1>'
            + (f'<div class="row">{cs}</div>' if cs else '') + (f'<p class="sub">{sub}</p>' if sub else '') + '</div></body></html>')


def jobs():
    out = []
    for t, r in list(holdings.R.items()) + list(coverage.R.items()):
        if r.get('private'):
            cells = [('View', r['call']), ('Latest valuation', f"${r['price']:,}B"), ('Model value', f"${r['base']:,}B")]
            eye = f"Research &middot; {r['sector']}"
        else:
            cells = [('Call', r['call']), ('Value per share', f"${r['base']:,}"), ('Price at writing', f"${r['price']:,.2f}")]
            eye = f"Research &middot; {t} &middot; {r['sector']}"
        out.append((r['slug'], card(eye, r['h1'], cells)))
    out.append(('gev', card('Research &middot; GEV &middot; Electrical equipment', 'GE <em>Vernova</em>', [('Call', 'Hold'), ('Value per share', '$442'), ('Price at writing', '$890.33')])))
    out.append(('costco', card('Research &middot; COST &middot; FIN 370', 'Costco <em>Wholesale</em>', [('Call', 'Hold / Wait'), ('Value per share', '$831.50'), ('Price at the time', '$970.31')])))
    tools = [('ask', 'Ask <em>the filings</em>', 'Questions about any covered company, answered from its 10-K and 10-Q figures with sources.'),
             ('screener', 'Stock <em>screener</em>', 'Filter the S&amp;P 500 by growth, margins, valuation and debt, from SEC filings.'),
             ('compare', 'Compare <em>companies</em>', 'Up to four companies side by side, annual and quarterly.'),
             ('track', 'Track <em>record</em>', 'Every published call, scored against the S&amp;P 500 since the day it was made.'),
             ('earnings', 'Earnings <em>hub</em>', 'Upcoming reports and what each latest quarter changed.'),
             ('insiders', 'Insiders <em>and funds</em>', 'Executive trades from Form 4 and famous investors&rsquo; holdings from 13F filings.'),
             ('snapshot', 'Research <em>any company</em>', 'An instant snapshot of any S&amp;P 500 company from its filings, annual and quarterly.'),
             ('risk', 'Portfolio <em>risk</em>', 'Volatility, drawdowns, value at risk, correlations and the efficient frontier for any mix.'),
             ('fixed-income', 'Bond portfolio, <em>stress-tested</em>', 'Curve twists, humps and credit-spread shocks, bond by bond, with key-rate risk.')]
    for slug, h, sub in tools:
        out.append((slug, card('Research tool', h, sub=sub)))
    return out


def main():
    from playwright.sync_api import sync_playwright
    global CSS
    CSS = CSS % (font('manrope-latin-300-normal.woff2'), font('manrope-latin-400-normal.woff2'), font('manrope-latin-500-normal.woff2'), font('geist-mono-latin-500-normal.woff2'))
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1200, 'height': 630})
        for slug, html in jobs():
            pg.set_content(html); pg.wait_for_timeout(120)
            pg.screenshot(path=os.path.join(OUT, slug + '.jpg'), type='jpeg', quality=88)
        b.close()
    print('og images:', len(jobs()))


if __name__ == '__main__':
    main()
