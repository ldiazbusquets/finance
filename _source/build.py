"""Builds the LDB Finance static pages into ./out from shared pieces."""
import os, re, shutil, json, sys, datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages'))
import costco
import gev
import rep
import titlecase
import holdings
import notes
import coverage
import ratings
rep.apply_ratings(holdings.R); rep.apply_ratings(coverage.R)
GEV_CALL = ratings.rate(460, 890.33)[0]

HERE = os.path.dirname(os.path.abspath(__file__))
# Inside the repo (this file in _source/), the site's own folders are the source: assets, scripts and
# data are edited in place and the pages are written straight into the repo root.
IN_REPO = os.path.basename(HERE) == '_source'
SRC = os.path.dirname(HERE) if IN_REPO else os.path.join(HERE, 'src')
OUT = SRC if IN_REPO else os.path.join(HERE, 'out')
NAME = 'LDB Finance'
MAIN = 'https://ldiazbusquets.github.io/'
LAB = 'https://ldiazbusquets.github.io/lab/'

NAV = [('research.html', 'Research'), ('valuation.html', 'Valuation'), ('models.html', 'Models'), ('tools.html', 'Tools'), ('markets.html', 'Markets'), ('about.html', 'About')]
ARROW = '<svg width="14" height="14" viewBox="0 0 16 16"><path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


SITE = 'https://ldiazbusquets.github.io/finance/'


def head(title, desc, fn='index.html', root=''):
    t = 'Finance | Luis Diaz Busquets' if title is None else f'{title} | {NAME}'   # the home page is named like the Lab's
    url = SITE + ('' if fn == 'index.html' else fn)
    ogf = fn.replace('.html', '.jpg')
    own = os.path.exists(os.path.join(OUT, 'og', ogf))
    img = f'{SITE}og/{ogf}' if own else f'{SITE}preview.png'
    alt = t if own else 'LDB Finance: Benjamin Franklin from the $100 note, drawn in copper tiles'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="LDB Finance">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
<meta name="theme-color" content="#0C0A08">
<link rel="icon" type="image/png" sizes="192x192" href="/favicon.png?v=3">
<link rel="shortcut icon" href="/favicon.ico?v=3">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=3">
<script>
/* light 7am-7pm local time, dark otherwise; a manual pick lasts for this visit */
(function () {{
  var h = new Date().getHours(), byHour = h >= 7 && h < 19, pick = null;
  try {{ var v = (sessionStorage.getItem('theme') || '').split('|'); if (v[0] && v[1] === String(byHour)) pick = v[0]; }} catch (e) {{}}
  if (pick ? pick === 'light' : byHour) document.documentElement.classList.add('lt');
}})();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css?v=39">
</head>
'''


def mk_static():
    """Latest readings as plain text, for readers without JavaScript; the charts replace nothing here."""
    try:
        m = json.load(open(os.path.join(SRC, 'data', 'markets.json')))['series']
    except Exception:
        return ''
    MO = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    rows = []
    for k, v in m.items():
        l = v.get('last') or {}
        if l.get('v') is None:
            continue
        y, mo, dd = l['d'].split('-')
        val = f"{l['v']:,.2f}" if k in ('SP500', 'VIXCLS', 'DCOILWTICO', 'DEXUSEU') else f"{l['v']:.2f}%"
        if k == 'DCOILWTICO':
            val = '$' + val
        rows.append(f"<tr><td>{v['name']}</td><td>{val}</td><td>{MO[int(mo) - 1]} {int(dd)}, {y}</td></tr>")
    return ('<noscript><div class="panel"><div class="hd"><div><h3 class="sec">Latest readings</h3><p>The charts need JavaScript. These are the latest values when this page was built.</p></div></div>'
            '<table class="tbl"><thead><tr><th>Series</th><th>Latest</th><th>As of</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div></noscript>')


def nav(cur):
    links = ''.join(f'<a href="{h}"{" class=on" if h == cur else ""}>{n}</a>' for h, n in NAV)
    mlinks = ''.join(f'<a href="{h}"{" class=on" if h == cur else ""}>{n}<span>&rarr;</span></a>' for h, n in NAV)
    return f'''<nav class="top"><div class="wrap">
  <a class="brand" href="./" aria-label="LDB Finance, home"><svg class="lg" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 9.5V4.8A1.8 1.8 0 0 1 4.8 3h4.7M14.5 21h4.7a1.8 1.8 0 0 0 1.8-1.8v-4.7" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><circle cx="12" cy="12" r="2.6" fill="currentColor"/></svg> LDB <span>Finance</span></a>
  <div class="links">{links}</div>
  <div class="right">
    <button class="tg" id="tg" aria-label="Switch theme"></button>
    <button class="mb" id="mb" aria-label="Menu" aria-expanded="false"></button>
    <span class="sites" role="navigation" aria-label="Luis Diaz Busquets sites"><a href="{MAIN}">Portfolio</a><b aria-current="page">Finance</b><a href="{LAB}">Lab</a></span>
  </div>
</div></nav>
<div class="menu" id="menu">{mlinks}<div class="msites"><a href="{MAIN}">Portfolio</a><b aria-current="page">Finance</b><a href="{LAB}">Lab</a></div></div>
'''


def foot(extra=''):
    return f'''<footer><div class="wrap">
  <span>&copy; <span class="yr">{datetime.date.today().year}</span> Luis Diaz Busquets &middot; {NAME} &middot; For education only. Nothing here is investment advice.</span>
  <span class="fl"><a href="about.html">About &amp; sources</a><a href="{MAIN}">Main site</a><a href="{LAB}">LDB Lab</a></span>
</div></footer>
<script src="assets/site.js?v=20"></script>{extra}
</body>
</html>
'''


def page(fn, cur, title, desc, kind, body, extra='', root='', attrs=''):
    html = head(title, desc, fn) + f'<body data-page="{kind}"{attrs}>\n' + nav(cur) + body + foot(extra)
    if root:   # pages GitHub serves at other addresses (404) need absolute links
        html = re.sub(r'(href|src)="(?!https?:|/|#|data:|mailto:)([^"]*)"', lambda m: f'{m.group(1)}="{root}{m.group(2)}"', html)
    html = titlecase.apply_all(html)
    with open(os.path.join(OUT, fn), 'w') as f:
        f.write(html)


def pill(href, text, cls='cu', ext=False):
    t = ' target="_blank" rel="noopener"' if ext else ''
    return f'<a class="pill {cls}" href="{href}"{t}><span class="ic">{ARROW}</span>{text}</a>'


def ph(eyebrow, h1, sub, extra=''):
    return f'''<header class="ph"><div class="wrap">
  <div class="eyebrow mono">{eyebrow}</div>
  <h1>{h1}</h1>
  <p class="sub">{sub}</p>{extra}
</div></header>
'''


def card(href, n, title, text, go, status=None, art='', ext=False):
    st = ''
    if status:
        cls, label = {'live': ('live', 'Live'), 'build': ('build', 'In build'), 'plan': ('plan', 'Planned')}[status]
        st = f'<span class="st {cls}">{label}</span>'
    tag = 'a' if href else 'div'
    hr = f' href="{href}"' + (' target="_blank" rel="noopener"' if ext else '') if href else ''
    artsvg = f'<svg class="art" viewBox="0 0 200 86">{art}</svg>' if art else ''
    gotxt = f'<span class="go">{go}</span>' if go else ''
    return f'<{tag} class="card{" tall" if art else ""}"{hr}><div class="top"><span class="n">{n}</span>{st}</div>{artsvg}<h3>{title}</h3><p>{text}</p>{gotxt}</{tag}>'


ART = {
    'bars': '<path d="M0 85h200" style="stroke:var(--line2)"/><g style="fill:var(--acc)"><rect x="8" y="50" width="22" height="35" rx="2" opacity=".35"/><rect x="40" y="38" width="22" height="47" rx="2" opacity=".5"/><rect x="72" y="30" width="22" height="55" rx="2" opacity=".65"/><rect x="104" y="20" width="22" height="65" rx="2" opacity=".8"/><rect x="136" y="8" width="22" height="77" rx="2"/></g>',
    'grid': '<g fill="none" style="stroke:var(--line2)"><path d="M0 21h200M0 43h200M0 65h200M50 0v86M100 0v86M150 0v86"/></g><rect x="100" y="43" width="50" height="22" style="fill:var(--acc)" opacity=".85"/><rect x="50" y="21" width="50" height="22" style="fill:var(--acc)" opacity=".3"/>',
    'curve': '<path d="M0 80C40 80 60 78 80 60s40-50 60-52 40 0 60 0" fill="none" style="stroke:var(--acc)" stroke-width="2"/><path d="M0 80C40 80 60 74 90 50s50-30 110-34" fill="none" style="stroke:var(--t3)" stroke-width="1.2" stroke-dasharray="3 4"/>',
    'area': '<path d="M0 60 25 52 50 58 75 40 100 46 125 30 150 36 175 18 200 24" fill="none" style="stroke:var(--acc)" stroke-width="2"/><path d="M0 60 25 52 50 58 75 40 100 46 125 30 150 36 175 18 200 24V86H0Z" style="fill:var(--acc)" opacity=".1"/>',
}

TOWER = '''<div class="tower" aria-hidden="true">
      <svg viewBox="60 0 180 500">
        <defs>
          <linearGradient id="gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" style="stop-color:var(--glass1)"/><stop offset="1" style="stop-color:var(--glass2)"/></linearGradient>
          <linearGradient id="cu" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8C593A"/><stop offset=".55" stop-color="#723F20"/><stop offset="1" stop-color="#B07A4F"/></linearGradient>
          <linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFF8EF" stop-opacity="0"/><stop offset=".5" stop-color="#F0C090" stop-opacity=".22"/><stop offset="1" stop-color="#FFF8EF" stop-opacity="0"/></linearGradient>
          <clipPath id="body"><path d="M95 500V150l20-20V60l35-55 35 55v70l20 20v350Z"/></clipPath>
        </defs>
        <path d="M95 500V150l20-20V60l35-55 35 55v70l20 20v350Z" fill="url(#gl)"/>
        <g clip-path="url(#body)">
          <g class="tw" id="wins"></g>
          <rect class="sheen" x="40" y="0" width="220" height="500" fill="url(#sh)"/>
          <path d="M115 60 185 130M185 60 115 130" stroke="url(#cu)" stroke-width="1.6" fill="none" opacity=".9"/>
          <path d="M95 150 205 260M205 150 95 260" stroke="url(#cu)" stroke-width="1.2" fill="none" opacity=".55"/>
        </g>
        <path d="M95 500V150l20-20V60l35-55 35 55v70l20 20v350" fill="none" stroke="url(#cu)" stroke-width="1.6"/>
        <path d="M115 130h70M95 150h110M115 60h70" stroke="url(#cu)" stroke-width="1" opacity=".7"/>
        <path d="M150 5V60" stroke="url(#cu)" stroke-width="1" opacity=".6"/>
      </svg>
      <div class="tag"><span class="mono">Markets &middot; live</span><b id="tagv">S&amp;P 500</b><span id="tagd">Updated every weekday evening</span></div>
    </div>'''


def check_models():
    """rerun every report's model, rewrite its CSV, and stop the build if a report no longer matches its model"""
    import subprocess
    r = subprocess.run([sys.executable, 'export.py', '--check'], cwd=os.path.join(HERE, 'models'), capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        sys.exit('A report shows a value its model no longer produces; fix the report or the model before publishing.\n' + r.stderr)


def build():
    check_models()
    if not IN_REPO:
        if os.path.exists(OUT):
            shutil.rmtree(OUT)
        shutil.copytree(SRC, OUT)

    # ---------------- home ----------------
    home = f'''<header class="hero">
  <canvas class="tilebg" id="tilebg" aria-hidden="true"></canvas>
  <div class="wrap">
    <div>
      <div class="kick">Finance &middot; Luis Diaz Busquets</div>
      <h1>Research with <em>the numbers</em> showing.</h1>
      <p class="sub">Company deep dives, valuation models and market data in one place, built so you can check every assumption yourself.</p>
      <div class="cta">{pill('research.html', 'Browse research')}<a class="pill gh" href="markets.html">See the markets</a></div>
    </div>
  </div>
</header>

<section class="tight" style="padding-top:20px">
  <div class="wrap">
    <div class="eyebrow mono">Markets today</div>
    <div id="strip"><div class="tiles">{''.join('<div class="tile"><div class="k mono">&nbsp;</div><div class="v">&nbsp;</div><div class="d">&nbsp;</div></div>' for _ in range(4))}</div></div>
  </div>
</section>

<section id="inside">
  <div class="wrap">
    <div class="eyebrow mono">What's inside</div>
    <h2>Everything for a decision, <em>in one place.</em></h2>
    <div class="grid4">
      {card('research.html', '01', 'Research', 'Deep dives on single businesses, plus notes on bonds and the economy.', 'Browse &rarr;', art=ART['bars'])}
      {card('valuation.html', '02', 'Valuation', 'Search any S&amp;P 500 company for a DCF, peer multiples and a dividend model, filled in automatically.', 'Search &rarr;', art=ART['grid'])}
      {card('tools.html', '03', 'Tools', 'Position sizing, a portfolio x-ray, bond math and options payoffs, live in the browser.', 'Try &rarr;', art=ART['curve'])}
      {card('markets.html', '04', 'Markets', 'Rates, the yield curve, inflation and credit, refreshed every weekday.', 'View &rarr;', art=ART['area'])}
    </div>
  </div>
</section>

<section id="method" style="padding-top:30px">
  <div class="wrap">
    <div class="split">
      <div><div class="eyebrow mono">The method</div><h2>How a deep dive <em>is built.</em></h2></div>
      <p>Every report follows the same four steps, so two companies can be compared side by side.</p>
    </div>
    <div class="steps">
      <div class="step"><span class="k">01</span><h4>The business</h4><p>What it sells, who pays for it and why customers stay.</p></div>
      <div class="step"><span class="k">02</span><h4>The numbers</h4><p>Revenue, margins and cash flow, with the quality of earnings checked.</p></div>
      <div class="step"><span class="k">03</span><h4>The valuation</h4><p>What it's worth under bull, base and bear cases, and what the price already assumes.</p></div>
      <div class="step"><span class="k">04</span><h4>The risks</h4><p>What would change the view, and the dates to watch.</p></div>
    </div>
  </div>
</section>

<div class="bill">
  <canvas id="billcv" aria-hidden="true"></canvas>
  <div class="billtx">
    <div class="eyebrow mono">Valuation</div>
    <h2>What is it <em>really worth?</em></h2>
    <p>Search any S&amp;P 500 company and see its value from cash flows, dividends and peers, next to what the price already assumes.</p>
    {pill('valuation.html', 'Value a company', 'x')}
  </div>
</div>
'''
    page('index.html', None, None, 'Company research, valuation models and market data in one place.', 'home', home, '\n<script src="assets/bill.js?v=12"></script>')

    # ---------------- research ----------------
    ORDER = ['LHX', 'VRT', 'AWK', 'AMZN', 'META', 'JPM', 'GEV', 'NVDA', 'BA', 'SPCX', 'FLY']
    CARDS = {'LHX': 'Record backlog and missile demand, shares down a third on a CEO exit.', 'VRT': 'Power and cooling for AI data centers, after a growth miss.', 'AWK': 'The largest U.S. water utility, merging with Essential.', 'AMZN': 'AWS growing 37% while capex turns free cash flow negative.', 'META': 'Ads up 26%, free cash flow turned negative by AI spending.', 'JPM': 'The most profitable big bank, valued on return on equity.', 'GEV': 'A record order book valued on its own 2028 targets.', 'NVDA': 'The AI chip leader, priced for a long boom.', 'BA': 'A turnaround with record backlog and positive cash flow.', 'SPCX': 'Rockets, Starlink and now an AI cloud, revenue up 161%.', 'FLY': 'Moon landers and small rockets, down 70% from its high.'}
    META_R = dict(holdings.R); META_R.update({k: coverage.R[k] for k in ('SPCX', 'FLY')}); META_R['GEV'] = dict(t='GEV', slug='gev', name='GE Vernova', call=GEV_CALL, base=442, price=890.33)
    def hcard(t):
        r = META_R[t]; href = 'gev.html' if t == 'GEV' else r['slug'] + '.html'
        up = r['base'] / r['price'] - 1
        return card(href, f"{t} &middot; {r['call']}", r['name'], CARDS[t] + f" Value ${r['base']:,} against ${r['price']:,.0f}.", 'Read the report &rarr;', 'live')
    holding_cards = ''.join(hcard(t) for t in ORDER)
    PCARDS = {'ANTHROPIC': 'The maker of Claude, growing more than tenfold a year ahead of a November IPO.', 'OPENAI': 'ChatGPT&rsquo;s billion weekly users, and hundreds of billions to spend before profit.', 'ANDURIL': 'Autonomous weapons growing like software, valued like it too.', 'BLOOMBERG': 'The Terminal and its newsroom: a cash machine that has never published its numbers.'}
    def pcard(t):
        r = coverage.R[t]
        return card(r['slug'] + '.html', f"Private &middot; {r['call']}", r['name'], PCARDS[t] + f" Model value ${r['base']:,}B against ${r['price']:,}B.", 'Read the report &rarr;', 'live')
    priv_cards = ''.join(pcard(t) for t in ('ANTHROPIC', 'OPENAI', 'ANDURIL', 'BLOOMBERG'))
    research = ph('Research', 'Research', 'Deep dives on single companies, plus notes on bonds and the economy. Company figures are pulled from SEC filings automatically, so the numbers stay current between reports.',
                  '<div class="chips"><button class="chip on" data-f="all">All</button><button class="chip" data-f="eq">Equities</button><button class="chip" data-f="fi">Fixed income</button><button class="chip" data-f="mac">Macro</button></div>') + f'''
<section class="tight" data-cat="eq">
  <div class="wrap">
    <div class="tools6">
      <a href="ask.html"><span class="mono">AI</span><b>Ask the filings</b><p>Questions answered from 10-K and 10-Q figures, with sources.</p></a>
      <a href="screener.html"><span class="mono">Screen</span><b>Screener</b><p>Filter the S&amp;P 500 by growth, margins, valuation and debt.</p></a>
      <a href="compare.html"><span class="mono">Compare</span><b>Side by side</b><p>Two to four companies, figure by figure.</p></a>
      <a href="track.html"><span class="mono">Scorecard</span><b>Track record</b><p>Every call, scored against the S&amp;P 500.</p></a>
      <a href="earnings.html"><span class="mono">Calendar</span><b>Earnings hub</b><p>Upcoming reports and what the latest quarter changed.</p></a>
      <a href="insiders.html"><span class="mono">Ownership</span><b>Insiders and funds</b><p>Executive trades and what famous investors own.</p></a>
    </div>
    <a class="snapcta" href="snapshot.html"><div><span class="mono">Any S&amp;P 500 company</span><b>Search a company for an instant research snapshot</b><p>Growth, margins, cash, debt, a bear-to-bull valuation and peers, with annual 10-K and quarterly 10-Q figures, written from its filings in seconds.</p></div><span class="pill cu"><span class="ic">{ARROW}</span>Search</span></a>
    <div class="split" style="align-items:end;margin-bottom:30px;margin-top:56px"><div><div class="eyebrow mono">Equities</div><h3 class="sec">Holdings</h3></div><p>Every stock in the portfolio, valued with the same method. Written October 20, 2026 and refreshed after each quarter&rsquo;s results.</p></div>
    <div class="grid3 rcards">{holding_cards}</div>
    <div class="split" style="align-items:end;margin-bottom:30px;margin-top:56px"><div><div class="eyebrow mono">Equities</div><h3 class="sec">Private companies</h3></div><p>Companies on the watchlist that are not listed yet. Values are for the whole company, set against the latest private funding round.</p></div>
    <div class="grid3 rcards">{priv_cards}</div>
    <h3 class="sec" style="margin-top:56px">Other reports</h3>
    <div class="grid3 rcards" style="margin-top:24px;margin-bottom:64px">
      {card('lockheed-martin.html', 'LMT &middot; ' + coverage.R['LMT']['call'], 'Lockheed Martin', 'A record $292 billion backlog, and where Anduril can and can&rsquo;t compete. Value $647 against $590.', 'Read the report &rarr;', 'live')}
      {card('northrop-grumman.html', 'NOC &middot; ' + coverage.R['NOC']['call'], 'Northrop Grumman', 'The B-21 and Sentinel, and a private Anduril now worth more. Value $564 against $553.', 'Read the report &rarr;', 'live')}
      {card('caterpillar.html', 'CAT &middot; ' + coverage.R['CAT']['call'], 'Caterpillar', 'Engines and turbines for AI data centers, inside a cyclical machinery company. Value $442 against $704.', 'Read the report &rarr;', 'live')}
      {card('asml.html', 'ASML &middot; ' + coverage.R['ASML']['call'], 'ASML', 'The only maker of EUV machines, with demand ahead of supply to 2028. Value $1,081 against $1,561.', 'Read the report &rarr;', 'live')}
      {card('sk-hynix.html', 'SKHY &middot; ' + coverage.R['SKHY']['call'], 'SK hynix', 'The HBM leader at a 76% margin, valued across the memory cycle. Value $111 against $132 an ADR.', 'Read the report &rarr;', 'live')}
      {card('palantir.html', 'PLTR &middot; ' + coverage.R['PLTR']['call'], 'Palantir', 'AI software growing 93% at a 47% margin, priced for the bull case. Value $87 against $202.', 'Read the report &rarr;', 'live')}
      {card('amd.html', 'AMD &middot; ' + coverage.R['AMD']['call'], 'AMD', 'Data center up 107% and Helios racks shipping, after a 140% run. Value $353 against $553.', 'Read the report &rarr;', 'live')}
      {card('micron.html', 'MU &middot; ' + coverage.R['MU']['call'], 'Micron', 'An 87% gross margin in the tightest memory market ever, valued across the cycle. Value $622 against $914.', 'Read the report &rarr;', 'live')}
      {card('sandisk.html', 'SNDK &middot; ' + coverage.R['SNDK']['call'], 'Sandisk', 'Pure flash: from losses to an 85% margin in a year. Value $636 against $1,378.', 'Read the report &rarr;', 'live')}
      {card('axon.html', 'AXON &middot; ' + coverage.R['AXON']['call'], 'Axon Enterprise', 'TASERs, body cameras and AI translation, down half from its peak. Value $314 against $396.', 'Read the report &rarr;', 'live')}
      {card('kratos.html', 'KTOS &middot; ' + coverage.R['KTOS']['call'], 'Kratos Defense', 'Drones, hypersonics and engines: the listed company closest to Anduril. Value $24 against $39.', 'Read the report &rarr;', 'live')}
      {card('costco.html', 'COST &middot; Coursework', 'Costco Wholesale', 'FIN 370 coursework: an excellent business trading above its $831.50 cash-flow value.', 'Read the report &rarr;', 'live')}
    </div>
    <div class="split" style="align-items:end;margin-bottom:34px">
      <div><div class="eyebrow mono">Equities</div><h3 class="sec">Company coverage</h3></div>
      <p class="mono" id="cstamp" style="font-size:11px">&nbsp;</p>
    </div>
    <div id="cov"><div class="wait">Loading coverage&hellip;</div></div>
  </div>
</section>

<section class="tight" data-cat="fi">
  <div class="wrap">
    <div class="eyebrow mono">Fixed income</div><h3 class="sec">Bond notes</h3>
    <div class="grid3" style="margin-top:30px">
      {''.join(card(n['slug'] + '.html', n['code'], n['name'], n['card'], 'Read the note &rarr;', 'live') for n in notes.NOTES if n['cat'] == 'fi')}
    </div>
  </div>
</section>

<section class="tight" data-cat="mac">
  <div class="wrap">
    <div class="eyebrow mono">Macro</div><h3 class="sec">Economy notes</h3>
    <div class="grid3" style="margin-top:30px">
      {''.join(card(n['slug'] + '.html', n['code'], n['name'], n['card'], 'Read the note &rarr;', 'live') for n in notes.NOTES if n['cat'] == 'mac')}
    </div>
  </div>
</section>
'''
    page('research.html', 'research.html', 'Research', 'Company deep dives and notes on bonds and the economy.', 'research', research)

    # ---------------- valuation ----------------
    quick = ''.join(f'<button class="chip" type="button" data-pick="{t}">{t}</button>' for t in ['AAPL', 'MSFT', 'NVDA', 'JPM', 'KO', 'COST', 'XOM'])
    valuation = ph('Valuation<span class="kind auto" title="Generated from SEC filings and the last close by code, with no analyst review">Automated model</span>', 'Value <em>any company</em>', 'Search the S&amp;P 500. Each company gets a cash-flow model (or a bank model), a dividend model where it fits and a peer comparison, filled in from its filings. Every assumption can be changed.',
                   f'''<div class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="q" type="search" placeholder="Search by ticker or name, like AAPL or Coca-Cola" autocomplete="off" spellcheck="false" aria-label="Search companies"><div class="sug" id="sug" role="listbox"></div></div>
<div class="quick"><span class="mono">Try</span>{quick}</div><p class="mono" id="count" style="margin-top:18px;font-size:11px">&nbsp;</p>''') + '''
<section class="tight">
  <div class="wrap">
    <div id="status"></div>
    <div id="out" hidden>
      <div id="co"></div>
      <div id="verdict"></div>
      <div id="field"></div>
      <div id="model"></div>
      <div id="fin" style="margin-top:16px"></div>
      <div id="filings"></div>
      <p class="disc">Automatic estimates from reported figures and simple assumptions. They are a starting point for analysis, not a price target and not investment advice. Prices are the last close and can be a day old.</p>
    </div>
  </div>
</section>
'''
    page('valuation.html', 'valuation.html', 'Valuation', 'Search any S&P 500 company for an automatic DCF, peer multiples and a dividend model.', 'valuation', valuation, '\n<script src="assets/val.js?v=14"></script>')

    # ---------------- research snapshot ----------------
    hq = ''.join(f'<button class="chip" type="button" data-pick="{t}">{t}</button>' for t in ['LHX', 'VRT', 'AWK', 'AMZN', 'META', 'JPM', 'GEV', 'NVDA', 'BA'])
    snapshot = ph('Research<span class="kind auto" title="Generated from SEC filings and the last close by code, with no analyst review">Automated model</span>', 'Research <em>any company</em>', 'Search the S&amp;P 500 for an instant snapshot: what the filings say about growth, margins, cash and debt, a bear, base and bull valuation, and how the company compares with its peers. Generated automatically from SEC data and the last close.',
                  f'''<div class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="q" type="search" placeholder="Search by ticker or name, like AAPL or Coca-Cola" autocomplete="off" spellcheck="false" aria-label="Search companies"><div class="sug" id="sug" role="listbox"></div></div>
<div class="quick"><span class="mono">Holdings</span>{hq}</div><p class="mono" id="count" style="margin-top:18px;font-size:11px">&nbsp;</p>''') + '''
<section class="tight">
  <div class="wrap">
    <div id="status"></div>
    <div id="out" hidden>
      <div id="co"></div>
      <div id="snap"></div>
      <div id="fin" style="margin-top:16px"></div>
      <div id="filings"></div>
      <p class="disc">Written automatically from reported figures and simple assumptions, with no human review. A starting point for research, not a recommendation and not investment advice. Prices are the last close and can be a day old.</p>
    </div>
  </div>
</section>
'''
    page('snapshot.html', 'research.html', 'Research snapshot', 'Search any S&P 500 company for an automatic research snapshot from its SEC filings: growth, margins, cash, debt, valuation and peers.', 'snapshot', snapshot, '\n<script src="assets/val.js?v=14"></script>')

    # ---------------- calls ledger (track record) ----------------
    MONTHS = {m: i + 1 for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])}
    def iso(d):
        m, day, y = re.match(r'([A-Za-z]+) (\d+), (\d{4})', d).groups()
        return f'{y}-{MONTHS[m]:02d}-{int(day):02d}'
    wlh = {c['ticker']: c for c in json.load(open(os.path.join(SRC, 'data', 'watchlist.json')))['companies']}
    cur_calls = []
    for t, r in list(holdings.R.items()) + [(k, v) for k, v in coverage.R.items() if not v.get('private')]:
        cur_calls.append({'t': t, 'name': r['name'], 'page': r['slug'] + '.html', 'date': iso(r.get('rated') or r['date']), 'call': r['call'], 'value': r['base'], 'price': r['price'], 'held': bool(wlh.get(t, {}).get('holding'))})
    cur_calls.append({'t': 'GEV', 'name': 'GE Vernova', 'page': 'gev.html', 'date': iso(ratings.RATED), 'call': GEV_CALL, 'value': 442, 'price': 890.33, 'held': True})
    lp = os.path.join(SRC, 'data', 'calls.json')
    ledger = json.load(open(lp)) if os.path.exists(lp) else {'_note': 'Every published call, appended when a report is written or its call changes. Never edit past rows.', 'calls': []}
    have = {(c['t'], c['date']) for c in ledger['calls']}
    for c in cur_calls:
        if (c['t'], c['date']) not in have:
            ledger['calls'].append(c)
    ledger['calls'].sort(key=lambda c: (c['date'], c['t']))
    with open(lp, 'w') as f:
        json.dump(ledger, f, indent=1)

    def tool_page(fn, cur, eyebrow, h1, sub, kind, inner, title, desc, extra_head=''):
        body = ph(eyebrow, h1, sub, extra_head) + f'''
<section class="tight">
  <div class="wrap">
    {inner}
  </div>
</section>
'''
        page(fn, cur, title, desc, kind, body, '\n<script src="assets/hub.js?v=6"></script>')

    tool_page('track.html', 'research.html', 'Research', 'Track <em>record</em>',
              'Every call this site publishes is logged on the day it is made and never edited, then scored the same way: total return against the S&amp;P 500 over exactly the same days.', 'track',
              '''<div id="tsum" class="kv four"></div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Every call</h3><p>Return includes dividends and runs from the close on the report date. Each call is checked against the S&amp;P 500 at three, six and twelve months; a call is <b>ahead</b> if it beat the index at its latest checkpoint. The call itself (Buy, Hold or Watch) is shown alongside and summarised separately above, so the method is the same for every recommendation.</p><p class="mono" id="tstamp" style="margin-top:8px">&nbsp;</p></div></div><div class="scroll"><table class="tbl" id="ttab"></table></div></div>
    <p class="disc">Rows are never edited: when a report is revised, its new call is added as a new row and scored from its own date. The log started on October 20, 2026, so the first checkpoints arrive in January 2027 and results before then are mostly noise. Private-company views are not scored because they have no market price. Costco (FIN 370 coursework) is left out because its sections were priced on different dates. Not investment advice.</p>''',
              'Track record', 'Every call published on LDB Finance, scored the same way against the S&P 500 at 3, 6 and 12 months.')

    tool_page('screener.html', 'research.html', 'Research<span class="kind auto" title="Generated from SEC filings and the last close by code, with no analyst review">Automated model</span>', 'Stock <em>screener</em>',
              'Filter every S&amp;P 500 company, plus the companies covered here, by growth, profitability, valuation and debt. Figures come from SEC filings and the last close.', 'screener',
              '''<div class="scrbar">
      <div class="chips" id="presets" style="margin-top:0"></div>
      <div class="sfl" id="filters"></div>
    </div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec" id="scount">Companies</h3><p>Click a column to sort; click a company for its full snapshot. Tick up to four to compare.</p></div><a class="pill gh sm" id="cmpgo" href="compare.html" hidden>Compare selected &rarr;</a></div><div class="scroll"><table class="tbl scr" id="stab"></table></div></div>
    <p class="disc">Growth is the latest fiscal year; margins and returns use the latest twelve months where a newer 10-Q exists. Banks and insurers have no operating margin or net-debt figure. Not investment advice.</p>''',
              'Stock screener', 'Screen the S&P 500 by growth, margins, valuation, debt and dividends, straight from SEC filings.')

    tool_page('compare.html', 'research.html', 'Research<span class="kind auto" title="Generated from SEC filings and the last close by code, with no analyst review">Automated model</span>', 'Compare <em>companies</em>',
              'Put two to four companies side by side: growth, margins, cash, debt and valuation, from their annual and quarterly filings.', 'compare',
              '''<div class="search" style="margin-top:0"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="q" type="search" placeholder="Add a company, like MSFT or Coca-Cola" autocomplete="off" spellcheck="false" aria-label="Add a company"><div class="sug" id="sug" role="listbox"></div></div>
    <div class="chips" id="picked" style="margin-top:18px"></div>
    <div id="cmp" style="margin-top:24px"></div>''',
              'Compare companies', 'Compare up to four companies side by side from their SEC filings.')

    tool_page('earnings.html', 'research.html', 'Research', 'Earnings <em>hub</em>',
              'When each covered company reports next, and what its latest quarter changed. Dates come from the Nasdaq calendar; quarters come straight from the 10-Q filings.', 'earnings',
              '''<div class="panel"><div class="hd"><div><h3 class="sec">Coming up</h3><p id="estamp">Holdings first, then the rest of the watchlist.</p></div></div><div id="ecal"></div></div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">What the latest quarter changed</h3><p>Each company&rsquo;s most recent quarter against the same quarter a year earlier, newest filing first.</p></div></div><div class="scroll"><table class="tbl" id="eq"></table></div></div>
    <p class="disc">Dates marked &ldquo;estimated&rdquo; are about 13 weeks after the company&rsquo;s last report, or projected from its filing pattern, until it announces a date. Not investment advice.</p>''',
              'Earnings hub', 'Upcoming earnings dates and what each latest quarter changed, for every company covered on LDB Finance.')

    tool_page('insiders.html', 'research.html', 'Research', 'Insiders <em>and funds</em>',
              'Open-market buys and sells by executives and directors from SEC Form 4, and the latest holdings of well-known investors from their 13F filings.', 'insiders',
              '''<div class="panel"><div class="hd"><div><h3 class="sec">Insider trading, past year</h3><p>Open-market purchases and sales only; stock grants, option exercises and shares withheld for tax are left out. Trades under a pre-arranged 10b5-1 plan are marked, since they say less about the insider&rsquo;s view.</p></div></div><div class="scroll"><table class="tbl" id="isum"></table></div><div id="idet" style="margin-top:22px"></div></div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">What famous investors own</h3><p id="fstamp">Latest 13F filings. 13Fs are filed 45 days after each quarter and show U.S. stock positions only.</p></div></div><div id="funds"></div></div>
    <p class="disc">From SEC EDGAR. A 13F is a snapshot at quarter end and may have changed since. Not investment advice.</p>''',
              'Insiders and funds', 'Insider buys and sells from SEC Form 4 and famous investors’ holdings from 13F filings, for the companies covered on LDB Finance.')

    tool_page('ask.html', 'research.html', 'Research<span class="kind auto" title="Answers are computed from SEC filings by code; the optional AI only rewords them">Automated answers</span>', 'Ask <em>the filings</em>',
              'Ask a question about any covered company and get an answer built from its 10-K and 10-Q figures, with every number traced to its filing. On computers that support it, an AI model running privately in your browser can write the answer in plain English.', 'ask',
              '''<div class="askbox panel">
      <div class="askrow"><div class="search" style="margin:0;flex:1 1 220px;max-width:none"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="q" type="search" placeholder="Company, like NVDA or Costco" autocomplete="off" spellcheck="false" aria-label="Company"><div class="sug" id="sug" role="listbox"></div></div>
      <span class="mono" id="acur">No company picked</span></div>
      <form id="aform" class="askrow" autocomplete="off"><input id="aq" type="text" placeholder="Ask anything, like: Why did margins change last quarter?" aria-label="Your question"><button class="pill cu" type="submit"><span class="ic">&rarr;</span>Ask</button></form>
      <div class="chips" id="asugg" style="margin-top:14px"></div>
      <div class="aimode" id="aimode"></div>
    </div>
    <div id="alog" style="margin-top:16px"></div>
    <p class="disc">Answers use only the company&rsquo;s reported figures and the last close; they do not include news, guidance or analyst estimates unless a report on this site covers them. The AI model runs on your device and nothing you type leaves your browser. Check important numbers against the linked filings. Not investment advice.</p>''',
              'Ask the filings', 'Ask questions about any covered company, answered from its SEC 10-K and 10-Q figures with sources.')

    # ---------------- models ----------------
    models = ph('Models', 'Valuation <em>models</em>', 'Every model shows its inputs on the page. The live ones run inside the <a href="valuation.html" style="color:var(--acc)">Valuation</a> tool for any S&amp;P 500 company.') + f'''
<section class="tight">
  <div class="wrap">
    <div class="eyebrow mono">Equity</div><h3 class="sec">Valuing a company</h3>
    <div class="grid3" style="margin-top:30px">
      {card('valuation.html', 'MOD-01', 'Discounted cash flow', 'Ten years of free cash flow and a terminal value, filled in from filings, with a sensitivity table.', 'Open &rarr;', 'live')}
      {card('valuation.html', 'MOD-02', 'Trading comparables', 'Value a company against its closest peers on P/E, EV/EBITDA and EV/Sales.', 'Open &rarr;', 'live')}
      {card('valuation.html?t=JPM', 'MOD-03', 'Bull, base and bear', 'Three scenarios with probabilities, ending in one probability-weighted value. Built into every company in the Valuation tool.', 'Open &rarr;', 'live')}
      {card('valuation.html?t=JPM', 'MOD-04', 'Bank valuation', 'Banks and insurers are valued on book value and return on equity, not cash flow.', 'Open &rarr;', 'live')}
      {card('valuation.html?t=PLTR', 'MOD-05', 'Growth-company DCF', 'For fast growers: growth that starts high and fades, margins that ramp, reinvestment tied to new revenue.', 'Open &rarr;', 'live')}
      {card('valuation.html?t=KO', 'MOD-06', 'Dividend discount', 'Value from dividends alone, shown automatically for steady payers.', 'Open &rarr;', 'live')}
    </div>
  </div>
</section>
<section class="tight" style="padding-top:20px">
  <div class="wrap">
    <div class="eyebrow mono">Fixed income</div><h3 class="sec">Valuing a bond</h3>
    <div class="grid3" style="margin-top:30px">
      {card('bonds.html#pricer', 'MOD-07', 'Bond pricer', 'Price, yield to maturity, duration and convexity for any fixed-coupon bond.', 'Open &rarr;', 'live')}
      {card('bonds.html#shock', 'MOD-08', 'Rate shock', 'What a portfolio of bonds loses or gains if rates jump or fall, using the live Treasury curve.', 'Open &rarr;', 'live')}
      {card('fixed-income.html', 'MOD-10', 'Bond portfolio stress test', 'Treasuries and corporates against curve twists, humps and spread shocks, with key-rate risk and a goal to fund.', 'Open &rarr;', 'live')}
      {card('loans.html', 'MOD-09', 'Loan and mortgage', 'Payments, amortisation and the true cost of borrowing at today’s rates.', 'Open &rarr;', 'live')}
    </div>
  </div>
</section>
'''
    page('models.html', 'models.html', 'Models', 'Interactive valuation models for companies and bonds.', 'models', models)

    # ---------------- tools ----------------
    tools = ph('Tools', 'Tools you can <em>use</em>', 'Interactive finance tools that run in your browser. Company data comes from the same nightly update as the rest of the site.',
               '<div class="cta">' + pill('#sizer', 'Position sizer') + '<a class="pill gh" href="#xray">Portfolio x-ray</a><a class="pill gh" href="risk.html">Portfolio risk</a><a class="pill gh" href="plan.html">Financial plan</a></div>') + f'''
<section class="tight" id="sizer">
  <div class="wrap">
    <div class="split" style="margin-bottom:34px"><div><div class="eyebrow mono">TOOL-06</div><h3 class="sec">Position sizer</h3></div><p>Decide the loss you can accept first; the number of shares follows from the distance to your stop.</p></div>
    <div class="cols2 bond">
      <div class="panel"><div id="zIn"></div></div>
      <div class="panel"><div id="zOut"></div><svg class="chart lad" id="zCh"></svg></div>
    </div>
  </div>
</section>

<section class="tight" id="xray" style="padding-top:30px">
  <div class="wrap">
    <div class="split" style="margin-bottom:34px"><div><div class="eyebrow mono">TOOL-07</div><h3 class="sec">Portfolio x-ray</h3></div><p>List what you own. S&amp;P 500 index funds (SPY, VOO, IVV, SPLG, RSP) are opened up into their companies, so overlap with your single stocks shows.</p></div>
    <div class="panel">
      <div class="hd"><div><h3 class="sec">Your holdings</h3><p>Ticker and current value in dollars. Saved in this browser only.</p></div><div class="cta" style="margin:0"><button type="button" class="reset" id="xAdd">+ Add a holding</button><button type="button" class="reset" id="xEx">Example</button><button type="button" class="reset" id="xClr">Clear</button></div></div>
      <div id="xT"></div>
    </div>
    <div class="panel" style="margin-top:16px"><div id="xOut"></div></div>
    <p class="disc">S&amp;P 500 weights here are by total market value, which is close to, but not exactly, the index&rsquo;s float-adjusted weights. Companies outside the S&amp;P 500 are counted as &ldquo;not covered&rdquo;.</p>
    <a class="snapcta" href="risk.html" style="margin-top:24px"><div><span class="mono">TOOL-08 &middot; Next step</span><b>Measure the risk of a portfolio</b><p>Volatility, drawdowns, beta, value at risk, which holding carries the risk, correlations and the efficient frontier, from five years of weekly returns.</p></div><span class="pill cu"><span class="ic">{ARROW}</span>Open</span></a>
    <a class="snapcta" href="plan.html" style="margin-top:16px"><div><span class="mono">TOOL-09 &middot; Wealth planning</span><b>Will the money last?</b><p>A household projected year by year: pay, taxes, spending, debts, goals and Social Security, run through 1,000 markets, with what-ifs and the savings it would take.</p></div><span class="pill cu"><span class="ic">{ARROW}</span>Open</span></a>
  </div>
</section>

<section class="tight" style="padding-top:20px">
  <div class="wrap">
    <div class="eyebrow mono">More tools &middot; in LDB Lab</div><h3 class="sec">Ready to try</h3>
    <div class="grid3" style="margin-top:30px">
      {card(LAB + 'options.html', 'TOOL-01', 'Options builder', 'Build spreads, straddles and condors. Payoff at expiry and today, Black-Scholes prices and the Greeks.', 'Open &#8599;', 'live', ext=True)}
      {card(LAB + 'kelly.html', 'TOOL-02', 'Kelly challenge', 'How much to bet when you have an edge, and what happens when you bet too much.', 'Open &#8599;', 'live', ext=True)}
      {card(LAB + 'market-maker.html', 'TOOL-03', 'Market-making game', 'Quote a bid and ask against traders who know more than you, with Bayesian updating.', 'Open &#8599;', 'live', ext=True)}
      {card(LAB + 'montecarlo.html', 'TOOL-04', 'Monte Carlo planner', 'Thousands of simulated lifetimes, and a planner that learns how much stock to hold.', 'Open &#8599;', 'live', ext=True)}
      {card(LAB + 'models.html', 'TOOL-05', 'Model Playground', 'FinBERT, BERT, Qwen3 and Llama 3.2 read the same financial headline side by side.', 'Open &#8599;', 'live', ext=True)}
    </div>
  </div>
</section>
'''
    page('tools.html', 'tools.html', 'Tools', 'Position sizing, a portfolio x-ray and more finance tools that run in the browser.', 'tools', tools, '\n<script src="assets/tools.js?v=1"></script>')

    # ---------------- financial planner ----------------
    plan = ph('Tools<span class="kind auto" title="Calculated by code from your inputs, with no analyst review">Automated model</span>', 'Financial <em>plan</em>', 'A whole household on one page: pay, taxes, spending, debts, goals and Social Security, projected year by year and run through 1,000 different markets. The question it answers is the one a planner asks first: will the money last?',
             '<div class="meta"><span class="mono" id="plInfl">&nbsp;</span><span class="mono">All results in today&rsquo;s dollars</span></div>') + '''
<section class="tight">
  <div class="wrap">
    <div class="cols2 plan">
      <div class="panel"><div class="hd"><div><h3 class="sec">The household</h3><p>Change anything; everything below updates.</p></div></div><div id="plIn"></div></div>
      <div>
        <div class="panel"><div class="hd"><div><h3 class="sec">Debts</h3><p>Payments come out of savings until each is paid off.</p></div><button type="button" class="reset" id="plAddD">+ Add</button></div><div class="scroll" id="plDebt"></div></div>
        <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Goals</h3><p>One-off costs in today&rsquo;s dollars: a home, a car, tuition.</p></div><button type="button" class="reset" id="plAddG">+ Add</button></div><div class="scroll" id="plGoal"></div></div>
        <details class="panel plas" style="margin-top:16px"><summary><h3 class="sec">Assumptions</h3><span class="mono">Returns, volatility, inflation</span></summary><div id="plAs" style="margin-top:18px"></div><p class="fine">Returns are nominal and drawn at random each year around these averages. Stocks and bonds are only slightly correlated. Cash earns a little less than the 3-month Treasury.</p></details>
      </div>
    </div>
    <div id="plSum" style="margin-top:16px"></div><div id="plWarn"></div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Net worth, 1,000 markets</h3><p>Copper: the middle outcome. Shaded: the middle 80%. Dashed: the worst 10%. Everything in today&rsquo;s dollars.</p></div></div><svg class="chart" id="plFan" style="height:330px"></svg></div>
    <div class="cols eq">
      <div class="panel"><div class="hd"><div><h3 class="sec">What if</h3><p>The same plan with one thing changed.</p></div></div><div id="plSc" class="scroll"></div></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">What it would take</h3><p>The two levers most people have.</p></div></div><div id="plSolve"></div>
        <h3 class="sec" style="margin-top:26px">Debts</h3><div id="plDebtOut" style="margin-top:14px"></div></div>
    </div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Year by year</h3><p>With average returns every year, in today&rsquo;s dollars. Retirement row highlighted.</p></div></div><div id="plFlow" class="scroll"></div></div>
    <p class="disc">A teaching model, not a financial plan: taxes are one flat rate, all investments are treated as one account, and returns are random draws, not forecasts. Real planning also covers account types, required withdrawals, health costs, insurance and estate questions. Not investment advice.</p>
  </div>
</section>
'''
    page('plan.html', 'tools.html', 'Financial plan', 'Model a household year by year: pay, taxes, spending, debts, goals and Social Security, run through 1,000 markets to see whether the money lasts, with what-ifs and what it would take.', 'plan', plan, '\n<script src="assets/plan.js?v=2"></script>')

    # ---------------- portfolio risk ----------------
    risk = ph('Tools<span class="kind auto" title="Calculated by code from historical prices, with no analyst review">Automated model</span>', 'Portfolio <em>risk</em>', 'How a mix of stocks, funds and bonds actually behaved: how much it swung, how far it fell, which holding carried the risk and what the same holdings could have done with different weights.',
              '<div class="meta"><span class="mono" id="rkStamp">&nbsp;</span><span class="mono">Source: Yahoo Finance weekly total returns</span></div>') + '''
<section class="tight">
  <div class="wrap">
    <div class="panel">
      <div class="hd"><div><h3 class="sec">Your portfolio</h3><p>Ticker and dollar amount. Any S&amp;P 500 company, the companies researched here and about fifty common ETFs, including bond and gold funds.</p></div><div class="cta" style="margin:0"><button type="button" class="reset" id="rkAdd">+ Add a holding</button></div></div>
      <div class="chips sm" id="rkPre" style="margin-bottom:16px"></div>
      <div id="rkT"></div>
      <div class="seg sm" id="rkLook"></div>
    </div>
    <div id="rkOut" style="margin-top:16px"></div>
    <div class="cols eq">
      <div class="panel"><div class="hd"><div><h3 class="sec">Growth of $10,000</h3><p>Dividends included.</p></div></div><svg class="chart" id="rkG"></svg><p class="fine" id="rkGNote"></p></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">Drawdowns</h3><p>Distance below the last high.</p></div></div><svg class="chart" id="rkD"></svg><p class="fine" id="rkDNote"></p></div>
    </div>
    <div class="cols eq">
      <div class="panel"><div class="hd"><div><h3 class="sec">Where the risk comes from</h3><p>Each holding&rsquo;s share of the money against its share of the portfolio&rsquo;s volatility.</p></div></div><div id="rkC"></div><p class="fine" id="rkCNote"></p></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">How they move together</h3><p>Correlation of weekly returns: copper moves together, green moves opposite.</p></div></div><div id="rkH"></div></div>
    </div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">The efficient frontier</h3><p>The same holdings, every long-only mix: grey circles are single holdings, the copper line the best return for each level of risk.</p></div></div>
      <div class="cols2 rkf"><svg class="chart" id="rkF" style="height:320px"></svg><div id="rkFT"></div></div></div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">The worst weeks</h3><p>The mix&rsquo;s six biggest weekly losses in the period, with the S&amp;P 500 alongside.</p></div></div><div id="rkW" class="scroll"></div></div>
    <p class="disc">Weekly total returns from Yahoo Finance adjusted closes, refreshed once a week. The portfolio is rebalanced to your weights every week. Volatility and ratios are annualised from weekly figures; value at risk is historical, from the worst 5% of weeks. Past behaviour is not a forecast, and nothing here is a recommendation. Not investment advice.</p>
  </div>
</section>
'''
    page('risk.html', 'tools.html', 'Portfolio risk', 'Volatility, drawdowns, beta, value at risk, risk contribution, correlations and the efficient frontier for any mix of stocks and ETFs, from five years of weekly returns.', 'risk', risk, '\n<script src="assets/risk.js?v=2"></script>')

    # ---------------- markets ----------------
    markets = ph('Markets', 'The markets, <em>in numbers</em>', 'Rates, the yield curve, inflation, credit and the S&amp;P 500, refreshed from the Federal Reserve every weekday evening.',
                 '<div class="meta"><span class="mono" id="stamp">&nbsp;</span><span class="mono">Source: FRED, Federal Reserve Bank of St. Louis</span></div>') + '''
<section class="tight">
  <div class="wrap">
    ''' + mk_static() + '''
    <div id="mwait"></div>
    <div class="tiles" id="mtiles" data-need></div>

    <div class="cols" data-need>
      <div class="panel"><div class="hd"><div><h3 class="sec">Treasury yield curve</h3><p>Yield by maturity, today against a month and a year ago.</p></div><div class="legend" id="lg-curve"></div></div><svg class="chart" id="c-curve"></svg></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">Rates</h3><p>Policy rate, Treasuries and mortgages.</p></div></div><div id="t-rates"></div></div>
    </div>

    <div class="cols" data-need>
      <div class="panel"><div class="hd"><div><h3 class="sec">S&amp;P 500</h3><p>The past year, daily close.</p></div></div><svg class="chart" id="c-spx"></svg></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">Economy</h3><p>Inflation, jobs and growth.</p></div></div><div id="t-macro"></div></div>
    </div>

    <div class="cols" data-need>
      <div class="panel"><div class="hd"><div><h3 class="sec">10-year minus 2-year</h3><p>Below zero, the curve is inverted, which has come before most recessions.</p></div></div><svg class="chart" id="c-spread"></svg></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">Credit, oil and currency</h3><p>Risk appetite and the dollar.</p></div></div><div id="t-cross"></div></div>
    </div>

    <div class="panel" style="margin-top:16px" data-need><div class="hd"><div><h3 class="sec">Policy rate against inflation</h3><p>Five years of the fed funds rate, the 10-year yield and CPI inflation.</p></div>
      <div class="legend"><span><i style="background:var(--acc);height:2px"></i>Fed funds</span><span><i style="background:var(--t3)"></i>10-year</span><span><i style="background:var(--t2);height:1px"></i>CPI inflation</span></div></div><svg class="chart" id="c-policy" style="height:300px"></svg></div>
  </div>
</section>
'''
    page('markets.html', 'markets.html', 'Markets', 'Rates, the yield curve, inflation and credit, refreshed every weekday.', 'markets', markets)

    # ---------------- about ----------------
    about = ph('About', 'About <em>this site</em>', 'An independent finance site by Luis Diaz Busquets, a finance student at Bryant University with minors in Applied AI and Law.') + f'''
<section class="tight">
  <div class="wrap">
    <div class="cols eq" style="margin-top:0;align-items:start">
      <div class="prose">
        <div class="eyebrow mono">Why it exists</div>
        <p>Most research hides its assumptions. Here, <b>every number links back to where it came from</b> and every model shows its inputs, so you can disagree with a conclusion and see exactly where.</p>
        <p>The site sits alongside the <a href="{MAIN}" style="color:var(--acc)">main site</a>, which covers who I am and my experience, and <a href="{LAB}" style="color:var(--acc)">LDB Lab</a>, which is about machine learning.</p>
        <div style="margin-top:28px">{pill(MAIN, 'Main site')}</div>
      </div>
      <div>
        <div class="eyebrow mono">Where the data comes from</div>
        <dl class="src">
          <dt>Market data</dt><dd>Federal Reserve Economic Data (FRED), from the Federal Reserve Bank of St. Louis. Treasury yields, the policy rate, inflation, jobs, credit spreads, oil, the dollar and the S&amp;P 500.</dd>
          <dt>Company figures</dt><dd>SEC EDGAR: the financial statements companies file in their 10-K annual reports.</dd>
          <dt>How often</dt><dd>An automatic job refreshes everything every weekday evening after US markets close. Some series, like inflation, are only published monthly.</dd>
        </dl>
      </div>
    </div>
  </div>
</section>
<section class="tight" style="padding-top:10px">
  <div class="wrap">
    <div class="eyebrow mono">The method</div><h3 class="sec">How a deep dive is built</h3>
    <div class="steps" style="margin-top:30px">
      <div class="step"><span class="k">01</span><h4>The business</h4><p>What it sells, who pays for it and why customers stay.</p></div>
      <div class="step"><span class="k">02</span><h4>The numbers</h4><p>Revenue, margins and cash flow, with the quality of earnings checked.</p></div>
      <div class="step"><span class="k">03</span><h4>The valuation</h4><p>What it's worth under bull, base and bear cases, and what the price already assumes.</p></div>
      <div class="step"><span class="k">04</span><h4>The risks</h4><p>What would change the view, and the dates to watch.</p></div>
    </div>
  </div>
</section>
<section class="tight" style="padding-top:10px" id="ratings">
  <div class="wrap">
    <div class="eyebrow mono">Objectivity</div><h3 class="sec">How ratings work</h3>
    <div class="cols eq" style="margin-top:24px;align-items:start">
      <div class="prose">
        <p>Every public company gets a <b>Buy</b>, <b>Hold</b> or <b>Sell</b> from the same rule, whoever owns it. The rule starts from the report&rsquo;s probability-weighted value (25% bear, 50% base, 25% bull) and the price at writing.</p>
        <p>Because the value depends on the discount rate, the same assumptions are first applied to the whole S&amp;P 500: a 5.15% 10-year Treasury yield and a 4.5% equity risk premium. On those assumptions the index is worth about <b>{{MKT_PCT}}% of its price</b>, so part of every stock&rsquo;s gap is the method, not the stock. The rating compares each stock with the market on that same basis:</p>
        <ul class="dl"><li><b>Buy</b>: at least 15% cheaper than the market.</li><li><b>Hold</b>: within 15% either way.</li><li><b>Sell</b>: at least 15% dearer than the market.</li></ul>
        <p>Each report shows both numbers, the absolute value and the comparison with the market, and says whether the rating would change if the index grew 6% or 10% a year instead of 8%. Private companies are not rated, since there is no price to buy them at; the Costco report is university coursework and is left as written.</p>
      </div>
      <div>
        <div class="eyebrow mono">The S&amp;P 500 on the reports&rsquo; assumptions</div>
        <div class="scroll"><table class="tbl txt allnum"><thead><tr><th>Index growth, years 1&ndash;5</th><th>Value / price</th><th>Implied equity premium</th></tr></thead><tbody>{{MKT_ROWS}}</tbody></table></div>
        <p class="fine">{{MKT_N}} S&amp;P 500 companies with complete data, ${{MKT_MC:.1f}} trillion of market value and ${{MKT_FCF:,.0f}} billion of free cash flow over the last twelve months. Growth fades to 3% by year ten. Rebuilt with <code>_source/models/market.py</code>; the ratings use the 8% row, as of {{RATED}}.</p>
        <div class="eyebrow mono" style="margin-top:26px">Other rules</div>
        <dl class="src">
          <dt>Ownership</dt><dd>Stated once, in each report&rsquo;s disclosure line. It never enters the rating or the recommendation text.</dd>
          <dt>Sources</dt><dd>Company releases and SEC filings first; news sites only for prices, analyst targets and reactions. Figures that are the analyst&rsquo;s own estimates are marked as such.</dd>
          <dt>Changes</dt><dd>When a rating changes, the old one stays in the <a href="track.html" style="color:var(--acc)">track record</a>, which scores every call against the S&amp;P 500.</dd>
          <dt>Known lean</dt><dd>On these assumptions the models sit below analysts&rsquo; targets almost everywhere. Each report explains its own gap with the Street.</dd>
        </dl>
      </div>
    </div>
    <p class="lead" style="margin-top:40px;font-size:14px">Everything on this site is for education. It is not investment advice, and nothing here is a recommendation to buy or sell any security.</p>
  </div>
</section>
'''
    _mk = json.load(open(os.path.join(SRC, 'data', 'models', 'market.json')))
    about = about.replace('{MKT_PCT}', f'{ratings.MKT * 100:.0f}').replace('{MKT_N}', str(_mk['companies'])).replace('{RATED}', ratings.RATED)
    about = about.replace('{MKT_ROWS}', ''.join(f"<tr><td>{float(g) * 100:.0f}%</td><td>{v['value_to_price'] * 100:.0f}%</td><td>{v['implied_premium'] * 100:.1f}%</td></tr>" for g, v in _mk['scenarios'].items()))
    about = about.replace('${MKT_MC:.1f}', f"${_mk['market_value'] / 1e12:.1f}").replace('${MKT_FCF:,.0f}', f"${_mk['free_cash_flow'] / 1e9:,.0f}")
    page('about.html', 'about.html', 'About', 'Who builds LDB Finance, where the data comes from and how research is done.', 'about', about)


    # ---------------- bonds ----------------
    bonds = ph('Models &middot; Fixed income', 'Bonds, <em>priced and shocked</em>', 'Price any fixed-coupon bond, see its duration and convexity, then hit a portfolio with a rate move. Yields start at today&rsquo;s Treasury curve.',
               '<div class="cta">' + pill('#pricer', 'Bond pricer') + '<a class="pill gh" href="#shock">Rate shock</a><a class="pill gh" href="fixed-income.html">Portfolio stress test</a></div>') + '''
<section class="tight" id="pricer">
  <div class="wrap">
    <div class="split" style="margin-bottom:34px"><div><div class="eyebrow mono">MOD-07</div><h3 class="sec">Bond pricer</h3></div><p>Enter a yield to get the price, or a price to get the yield. Everything else follows from the cash flows.</p></div>
    <div class="cols2 bond">
      <div class="panel"><div id="bIn"></div></div>
      <div class="panel"><div id="bOut"></div></div>
    </div>
    <div class="cols eq">
      <div class="panel"><div class="hd"><div><h3 class="sec">Price against yield</h3><p>The copper curve is the real price. The dashed line is what duration alone predicts; the gap between them is convexity, and it always works in the holder&rsquo;s favor.</p></div></div><svg class="chart" id="cPY"></svg></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">Where the value comes from</h3><p>Today&rsquo;s value of each payment: coupons in copper, the face value at the end in grey. Duration is the average date, weighted by value.</p></div></div><svg class="chart cf" id="cCF"></svg></div>
    </div>
  </div>
</section>

<section class="tight" id="shock" style="padding-top:30px">
  <div class="wrap">
    <div class="split" style="margin-bottom:34px"><div><div class="eyebrow mono">MOD-08</div><h3 class="sec">Rate shock</h3></div><p>Build a bond portfolio, then move the curve. The short and long ends can move separately, so you can test twists as well as parallel shifts.</p></div>
    <div class="panel">
      <div class="hd"><div><h3 class="sec">Your bonds</h3><p>Edit any cell. Coupons are paid twice a year.</p></div><div class="cta" style="margin:0"><button type="button" class="reset" id="pfAdd">+ Add a bond</button><button type="button" class="reset" id="pfLad">Treasury ladder</button></div></div>
      <div id="pfT"></div>
    </div>
    <div class="cols2 shk">
      <div class="panel"><div class="hd"><div><h3 class="sec">The shock</h3><p>Moves between 2 and 30 years are filled in on a straight line.</p></div></div><div id="sIn"></div></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">Gain or loss by size of move</h3><p>Parallel shifts from &minus;300 to +500 bp. Dashed: duration alone.</p></div></div><svg class="chart" id="cSh"></svg><p class="fine" id="cShNote"></p></div>
    </div>
    <div class="panel" style="margin-top:16px"><div id="sOut"></div></div>
    <p class="disc">Prices assume settlement on a coupon date, so there is no accrued interest. Yields are compounded at the coupon frequency. For education only, not investment advice.</p>
  </div>
</section>
'''
    page('bonds.html', 'models.html', 'Bond pricer and rate shock', 'Price any bond, see its duration and convexity, and test a bond portfolio against rate moves on the live Treasury curve.', 'bonds', bonds, '\n<script src="assets/bonds.js?v=2"></script>')

    # ---------------- fixed-income portfolio ----------------
    fi = ph('Models &middot; Fixed income', 'Bond portfolio, <em>stress-tested</em>', 'Build a portfolio of Treasuries and corporate bonds, then bend the yield curve and widen credit spreads. Every payment is repriced at the curve on its own date, so twists and humps show up bond by bond.',
            '<div class="meta"><span class="mono" id="fiStamp">&nbsp;</span><span class="mono">Source: FRED, Federal Reserve Bank of St. Louis</span></div>') + '''
<section class="tight">
  <div class="wrap">
    <div class="panel">
      <div class="hd"><div><h3 class="sec">Your bonds</h3><p>Edit any cell. Coupons are paid twice a year; yields start at today&rsquo;s Treasury curve plus the market spread for each type.</p></div><div class="cta" style="margin:0"><button type="button" class="reset" id="fiAdd">+ Add a bond</button><button type="button" class="reset" id="fiReset">Starter portfolio</button></div></div>
      <div id="fiT"></div>
    </div>
    <div style="margin-top:16px" id="fiSum"></div>
    <div class="cols2 shk">
      <div class="panel"><div class="hd"><div><h3 class="sec">The move</h3><p>Pick a scenario or set the curve yourself: level moves every maturity, slope tilts the long end against the short, curvature lifts the middle.</p></div></div><div id="fiS"></div></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">Treasury curve</h3><p>Today, dashed; after the move, copper. Dots mark the four key maturities.</p></div></div><svg class="chart" id="fiCurve"></svg></div>
    </div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">What the move does</h3><p>Full repricing, split into the part from Treasury yields and the part from credit spreads.</p></div></div><div id="fiRes"></div></div>
    <div class="cols eq">
      <div class="panel"><div class="hd"><div><h3 class="sec">Where the rate risk sits</h3><p>Key-rate exposure at 2, 5, 10 and 30 years.</p></div></div><svg class="chart" id="fiKrd" style="height:220px"></svg><p class="fine" id="fiKrdNote"></p></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">Cash coming in</h3><p>Every coupon and principal payment, by year.</p></div></div><svg class="chart" id="fiCf" style="height:220px"></svg><p class="fine" id="fiCfNote"></p></div>
    </div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">What you own</h3><p>Share of market value.</p></div></div><div id="fiMix"></div></div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Assets against a goal</h3><p>Asset-liability matching: a future payment is a short position in a bond, so it has a duration too.</p></div></div><div id="fiG"></div><div id="fiGoal" style="margin-top:20px"></div></div>
    <p class="disc">The Treasury curve is the daily constant-maturity curve from FRED, used as a discount curve with straight lines between maturities. Spreads are the ICE BofA investment-grade and high-yield averages; real bonds trade at their own spreads, so enter a bond&rsquo;s actual yield if you know it. A bond fund can be entered as one bond at its average maturity and yield. Settlement is on a coupon date. For education only, not investment advice.</p>
  </div>
</section>
'''
    page('fixed-income.html', 'models.html', 'Bond portfolio stress test', 'Build a portfolio of Treasuries and corporate bonds and test it against curve twists, humps and credit-spread shocks, with key-rate durations, cash flows and a goal to fund.', 'fi', fi, '\n<script src="assets/fi.js?v=1"></script>')

    # ---------------- loans ----------------
    loans = ph('Models &middot; MOD-09', 'Loans and <em>mortgages</em>', 'What a loan really costs: the monthly payment, every year of interest, what extra payments save, and the APR once points and fees are counted. The mortgage rate starts at this week&rsquo;s national average.') + '''
<section class="tight">
  <div class="wrap">
    <div class="cols2 loan">
      <div class="panel"><div class="hd"><div><h3 class="sec">The loan</h3><p>Pick a type, then change any number.</p></div></div><div id="lIn"></div></div>
      <div class="panel"><div class="hd"><div><h3 class="sec">What it costs</h3><p>Fixed rate, paid monthly.</p></div></div><div id="lOut"></div></div>
    </div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Paying it down</h3><p>The balance falls slowly at first, because early payments are mostly interest.</p></div><div class="legend" id="lLeg"></div></div><svg class="chart" id="lChart"></svg></div>
    <div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Rate and term, side by side</h3><p>Monthly payment and total interest on the same loan. The highlighted row is your rate.</p></div></div><div id="lGrid"></div></div>
    <details class="panel sched" style="margin-top:16px"><summary><h3 class="sec">Year-by-year schedule</h3></summary><div id="lTable"></div></details>
    <p class="disc">Assumes a fixed rate, monthly payments and that taxes and insurance stay at today&rsquo;s level. PMI is estimated and drops once the balance reaches 78% of the price. For education only; a lender&rsquo;s Loan Estimate is the figure to rely on.</p>
  </div>
</section>
'''
    page('loans.html', 'models.html', 'Loan and mortgage calculator', 'Monthly payments, amortisation, extra payments, PMI and APR for mortgages and other loans, starting from today’s mortgage rate.', 'loans', loans, '\n<script src="assets/loans.js?v=3"></script>')

    # ---------------- research reports ----------------
    page('costco.html', 'research.html', 'Costco Wholesale (COST) research', 'A full fundamental analysis of Costco against Walmart, Target and BJ\u2019s, ending in a cash-flow value of $831.50 a share and a Hold / Wait.', 'report', costco.body(), attrs=' data-ticker="COST" data-then="970.31" data-val="831.50"')
    for t, r in holdings.R.items():
        page(r['slug'] + '.html', 'research.html', f"{r['name']} ({t}) research", f"{r['name']} valued with a cash-flow, bank or dividend model: ${r['base']:,} a share against ${r['price']:,.2f} at writing. {r['call']}.", 'report', rep.body(r), attrs=f' data-ticker="{t}" data-then="{r["price"]}" data-val="{r["base"]}"')
    for n in notes.NOTES:
        page(n['slug'] + '.html', 'research.html', re.sub('<[^>]+>', '', n['name']).replace('&rsquo;', '\u2019') + ' | Research note', re.sub('<[^>]+>', '', n['card']), 'note', notes.body(n))
    for t, r in coverage.R.items():
        if r.get('private'):
            page(r['slug'] + '.html', 'research.html', f"{r['name']} research", f"{r['name']} (private) valued on 2030 earning power: about ${r['base']:,}B against ${r['price']:,}B at its latest valuation.", 'report', rep.body(r))
        else:
            page(r['slug'] + '.html', 'research.html', f"{r['name']} ({t}) research", f"{r['name']} valued with a {r['method'].lower()}: ${r['base']:,} a share against ${r['price']:,.2f} at writing. {r['call']}.", 'report', rep.body(r), attrs=f' data-ticker="{t}" data-then="{r["price"]}" data-val="{r["base"]}"')
    page('gev.html', 'research.html', 'GE Vernova (GEV) research', 'GE Vernova valued on its own 2028 targets: a record order book, a cash-flow value of $442 a share and a Hold.', 'report', gev.body(), attrs=' data-ticker="GEV" data-then="890.33" data-val="442"')

    # ---------------- sitemap ----------------
    pages = sorted(f for f in os.listdir(OUT) if f.endswith('.html') and f != '404.html')
    with open(os.path.join(OUT, 'sitemap.xml'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{SITE}{"" if p == "index.html" else p}</loc></url>\n' for p in pages) + '</urlset>\n')

    # ---------------- 404 ----------------
    nf = ph('Error 404', 'Page <em>not found</em>', 'That page doesn\u2019t exist, or it has moved. Try one of these instead.',
            '<div class="cta">' + pill('./', 'Home') + '<a class="pill gh" href="valuation.html">Value a company</a><a class="pill gh" href="markets.html">Markets</a></div>')
    page('404.html', None, 'Page not found', 'This page does not exist.', 'nf', nf, root='/finance/')


if __name__ == '__main__':
    build()
    print('built', sorted(f for f in os.listdir(OUT) if f.endswith('.html')))
