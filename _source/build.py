"""Builds the LDB Finance static pages into ./out from shared pieces."""
import os, re, shutil, json, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages'))
import costco
import gev
import rep
import holdings
import notes
import coverage

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
    t = NAME if title is None else f'{title} | {NAME}'
    url = SITE + ('' if fn == 'index.html' else fn)
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
<meta property="og:image" content="{SITE}preview.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="LDB Finance: Benjamin Franklin from the $100 note, drawn in copper tiles">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}preview.png">
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
<link rel="stylesheet" href="assets/site.css?v=13">
</head>
'''


def nav(cur):
    links = ''.join(f'<a href="{h}"{" class=on" if h == cur else ""}>{n}</a>' for h, n in NAV)
    mlinks = ''.join(f'<a href="{h}"{" class=on" if h == cur else ""}>{n}<span>&rarr;</span></a>' for h, n in NAV)
    return f'''<nav class="top"><div class="wrap">
  <a class="brand" href="./" aria-label="LDB Finance, home"><svg class="lg" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 9.5V4.8A1.8 1.8 0 0 1 4.8 3h4.7M14.5 21h4.7a1.8 1.8 0 0 0 1.8-1.8v-4.7" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><circle cx="12" cy="12" r="2.6" fill="currentColor"/></svg> LDB <span>Finance</span></a>
  <div class="links">{links}</div>
  <div class="right">
    <button class="tg" id="tg" aria-label="Switch theme"></button>
    <button class="mb" id="mb" aria-label="Menu" aria-expanded="false"></button>
    <a class="pill" href="{MAIN}"><span class="ic">{ARROW}</span>Main site</a>
  </div>
</div></nav>
<div class="menu" id="menu">{mlinks}<a href="{MAIN}">Main site<span>&#8599;</span></a></div>
'''


def foot(extra=''):
    return f'''<footer><div class="wrap">
  <span>{NAME} &middot; For education only. Nothing here is investment advice.</span>
  <span class="fl"><a href="about.html">About &amp; sources</a><a href="{MAIN}">Main site</a><a href="{LAB}">LDB Lab</a></span>
</div></footer>
<script src="assets/site.js?v=13"></script>{extra}
</body>
</html>
'''


def page(fn, cur, title, desc, kind, body, extra='', root='', attrs=''):
    html = head(title, desc, fn) + f'<body data-page="{kind}"{attrs}>\n' + nav(cur) + body + foot(extra)
    if root:   # pages GitHub serves at other addresses (404) need absolute links
        html = re.sub(r'(href|src)="(?!https?:|/|#|data:|mailto:)([^"]*)"', lambda m: f'{m.group(1)}="{root}{m.group(2)}"', html)
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


def build():
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
    CARDS = {'LHX': 'Record backlog and missile demand, shares down a third on a CEO exit.', 'VRT': 'Power and cooling for AI data centers, after a growth miss.', 'AWK': 'The largest U.S. water utility, merging with Essential.', 'AMZN': 'AWS growing 37% while capex turns free cash flow negative.', 'META': 'Ads up 28%, free cash flow squeezed by AI spending.', 'JPM': 'The most profitable big bank, valued on return on equity.', 'GEV': 'A record order book valued on its own 2028 targets.', 'NVDA': 'The AI chip leader, priced for a long boom.', 'BA': 'A turnaround with record backlog and positive cash flow.', 'SPCX': 'Rockets, Starlink and now an AI cloud, revenue up 161%.', 'FLY': 'Moon landers and small rockets, down 70% from its high.'}
    META_R = dict(holdings.R); META_R.update({k: coverage.R[k] for k in ('SPCX', 'FLY')}); META_R['GEV'] = dict(t='GEV', slug='gev', name='GE Vernova', call='Hold', base=442, price=890.33)
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
    <a class="snapcta" href="snapshot.html"><div><span class="mono">Any S&amp;P 500 company</span><b>Search a company for an instant research snapshot</b><p>Growth, margins, cash, debt, a bear-to-bull valuation and peers, written from its filings in seconds.</p></div><span class="pill cu"><span class="ic">{ARROW}</span>Search</span></a>
    <div class="split" style="align-items:end;margin-bottom:30px;margin-top:56px"><div><div class="eyebrow mono">Equities</div><h3 class="sec">Holdings</h3></div><p>Every stock in the portfolio, valued with the same method. Written October 20, 2026 and refreshed after each quarter&rsquo;s results.</p></div>
    <div class="grid3 rcards">{holding_cards}</div>
    <div class="split" style="align-items:end;margin-bottom:30px;margin-top:56px"><div><div class="eyebrow mono">Equities</div><h3 class="sec">Private companies</h3></div><p>Companies on the watchlist that are not listed yet. Values are for the whole company, set against the latest private funding round.</p></div>
    <div class="grid3 rcards">{priv_cards}</div>
    <h3 class="sec" style="margin-top:56px">Other reports</h3>
    <div class="grid3 rcards" style="margin-top:24px;margin-bottom:64px">
      {card('kratos.html', 'KTOS &middot; Watch', 'Kratos Defense', 'Drones, hypersonics and engines: the listed company closest to Anduril. Value $23 against $39.', 'Read the report &rarr;', 'live')}
      {card('costco.html', 'COST &middot; Hold / Wait', 'Costco Wholesale', 'FIN 370 coursework: an excellent business trading above its $831.50 cash-flow value.', 'Read the report &rarr;', 'live')}
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
    valuation = ph('Valuation', 'Value <em>any company</em>', 'Search the S&amp;P 500. Each company gets a cash-flow model (or a bank model), a dividend model where it fits and a peer comparison, filled in from its filings. Every assumption can be changed.',
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
    page('valuation.html', 'valuation.html', 'Valuation', 'Search any S&P 500 company for an automatic DCF, peer multiples and a dividend model.', 'valuation', valuation, '\n<script src="assets/val.js?v=10"></script>')

    # ---------------- research snapshot ----------------
    hq = ''.join(f'<button class="chip" type="button" data-pick="{t}">{t}</button>' for t in ['LHX', 'VRT', 'AWK', 'AMZN', 'META', 'JPM', 'GEV', 'NVDA', 'BA'])
    snapshot = ph('Research', 'Research <em>any company</em>', 'Search the S&amp;P 500 for an instant snapshot: what the filings say about growth, margins, cash and debt, a bear, base and bull valuation, and how the company compares with its peers. Generated automatically from SEC data and the last close.',
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
    page('snapshot.html', 'research.html', 'Research snapshot', 'Search any S&P 500 company for an automatic research snapshot from its SEC filings: growth, margins, cash, debt, valuation and peers.', 'snapshot', snapshot, '\n<script src="assets/val.js?v=10"></script>')

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
      {card('loans.html', 'MOD-09', 'Loan and mortgage', 'Payments, amortisation and the true cost of borrowing at today’s rates.', 'Open &rarr;', 'live')}
    </div>
  </div>
</section>
'''
    page('models.html', 'models.html', 'Models', 'Interactive valuation models for companies and bonds.', 'models', models)

    # ---------------- tools ----------------
    tools = ph('Tools', 'Tools you can <em>use</em>', 'Interactive finance tools that run in your browser. Company data comes from the same nightly update as the rest of the site.',
               '<div class="cta">' + pill('#sizer', 'Position sizer') + '<a class="pill gh" href="#xray">Portfolio x-ray</a></div>') + f'''
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

    # ---------------- markets ----------------
    markets = ph('Markets', 'The markets, <em>in numbers</em>', 'Rates, the yield curve, inflation, credit and the S&amp;P 500, refreshed from the Federal Reserve every weekday evening.',
                 '<div class="meta"><span class="mono" id="stamp">&nbsp;</span><span class="mono">Source: FRED, Federal Reserve Bank of St. Louis</span></div>') + '''
<section class="tight">
  <div class="wrap">
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
    <p class="lead" style="margin-top:40px;font-size:14px">Everything on this site is for education. It is not investment advice, and nothing here is a recommendation to buy or sell any security.</p>
  </div>
</section>
'''
    page('about.html', 'about.html', 'About', 'Who builds LDB Finance, where the data comes from and how research is done.', 'about', about)


    # ---------------- bonds ----------------
    bonds = ph('Models &middot; Fixed income', 'Bonds, <em>priced and shocked</em>', 'Price any fixed-coupon bond, see its duration and convexity, then hit a portfolio with a rate move. Yields start at today&rsquo;s Treasury curve.',
               '<div class="cta">' + pill('#pricer', 'Bond pricer') + '<a class="pill gh" href="#shock">Rate shock</a></div>') + '''
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
    page('bonds.html', 'models.html', 'Bond pricer and rate shock', 'Price any bond, see its duration and convexity, and test a bond portfolio against rate moves on the live Treasury curve.', 'bonds', bonds, '\n<script src="assets/bonds.js?v=1"></script>')

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
    page('loans.html', 'models.html', 'Loan and mortgage calculator', 'Monthly payments, amortisation, extra payments, PMI and APR for mortgages and other loans, starting from today’s mortgage rate.', 'loans', loans, '\n<script src="assets/loans.js?v=2"></script>')

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
            page(r['slug'] + '.html', 'research.html', f"{r['name']} ({t}) research", f"{r['name']} valued with a scenario model: ${r['base']:,} a share against ${r['price']:,.2f} at writing. {r['call']}.", 'report', rep.body(r), attrs=f' data-ticker="{t}" data-then="{r["price"]}" data-val="{r["base"]}"')
    page('gev.html', 'research.html', 'GE Vernova (GEV) research', 'GE Vernova valued on its own 2028 targets: a record order book, a cash-flow value of $442 a share and a Hold.', 'report', gev.body(), attrs=' data-ticker="GEV" data-then="890.33" data-val="442"')

    # ---------------- 404 ----------------
    nf = ph('Error 404', 'Page <em>not found</em>', 'That page doesn\u2019t exist, or it has moved. Try one of these instead.',
            '<div class="cta">' + pill('./', 'Home') + '<a class="pill gh" href="valuation.html">Value a company</a><a class="pill gh" href="markets.html">Markets</a></div>')
    page('404.html', None, 'Page not found', 'This page does not exist.', 'nf', nf, root='/finance/')


if __name__ == '__main__':
    build()
    print('built', sorted(f for f in os.listdir(OUT) if f.endswith('.html')))
