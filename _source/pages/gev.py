import rep
import ratings
from rep import rating_block, prose
"""GE Vernova deep dive for LDB Finance. Written October 20, 2026, before third-quarter results on October 28."""

EXT = '<svg width="12" height="12" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
L = {
    'q2': 'https://www.sec.gov/Archives/edgar/data/0001996810/000199681026000147/gevpressrelease2q26.htm',
    'q2q': 'https://www.sec.gov/Archives/edgar/data/0001996810/000199681026000148/gev2q2026form10-q.pdf',
    'iu': 'https://www.businesswire.com/news/home/20251209799497/en/GE-Vernova-raises-multi-year-financial-outlook-doubles-dividend-and-increases-buyback-authorization',
    'prolec': 'https://www.gevernova.com/news/press-releases/ge-vernova-completes-prolec-ge-acquisition',
    'ud': 'https://www.utilitydive.com/news/ge-vernova-gas-turbine-backlog-climbs-to-116-gw/826039/',
    'q3': 'https://www.gevernova.com/investors/events/3rd-quarter-2026-earnings-webcast',
    'bofa': 'https://www.benzinga.com/analyst-stock-ratings/analyst-color/26/10/62479818/ge-vernova-q3-preview-analyst-projects-orders-growth-of-44',
    'cons': 'https://www.ad-hoc-news.de/boerse/news/corporate-news/ge-vernova-stock-carries-a-moderate-buy-consensus-at-usd-1-171-87/70224473',
    'edgar': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001996810&type=10-K',
}
PRICE, BASE, BEAR, BULL, WT = 890.33, 442, 272, 682, 460
CALL = ratings.rate(WT, PRICE)[0]
ABS = ('undervalued' if WT / PRICE - 1 >= .10 else 'overvalued' if WT / PRICE - 1 <= -.10 else 'near fair value')


def src(*items):
    return '<div class="srcs">' + ''.join(f'<a href="{L.get(k, k)}" target="_blank" rel="noopener">{t}{EXT}</a>' for k, t in items) + '</div>'


def stats(rows):
    return '<div class="kv">' + ''.join(f'<div><b>{v}</b><span>{k}</span></div>' for v, k in rows) + '</div>'


def table(head, rows, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="scroll"><table class="tbl txt {cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def chap(n, cid, label, h2, body):
    return f'<section class="chap" id="{cid}"><div class="eyebrow mono">{n} &middot; {label}</div><h2>{h2}</h2>{body}</section>'


# where each method lands, $0 to $1,600: (name, low, high, point, label, accent)
MAX = 1600
ROWS = [('Cash-flow model', BEAR, BULL, BASE, f'${BEAR} to ${BULL}, base ${BASE}', True),
        ('Probability-weighted', None, None, WT, f'${WT}', False),
        ('Price at writing', None, None, PRICE, f'${PRICE:,.2f}', False),
        ('52-week range', 530, 1196, None, '$530 to $1,196', False),
        ('Analyst targets', 470, 1450, 1172, '$470 to $1,450, average $1,172', False)]


def field(narrow=False):
    n = len(ROWS)
    if narrow:
        x0, span, W, top, step = 8, 384, 400, 34, 70
        bot = top + step * (n - 1) + 22
    else:
        x0, span, W, top, step = 190, 780, 1000, 44, 48
        bot = top + step * (n - 1) + 26
    X = lambda v: x0 + v / MAX * span
    ticks = ''.join(f'<path d="M{X(v):.1f} 6V{bot}"/>' for v in range(0, MAX + 1, 200))
    lab = ''.join(f'<text x="{X(v):.1f}" y="{bot + 22}" text-anchor="middle">${v:,}</text>' for v in range(0, MAX + 1, 400))
    out = ''
    for i, (name, lo, hi, pt, txt, acc) in enumerate(ROWS):
        y = top + i * step
        short = txt.split(', average')[0].split(', base')[0]
        if narrow:
            out += f'<text class="nm" x="{x0}" y="{y - 16}">{name}<tspan class="vl" dx="10">{short}</tspan></text>'
        else:
            out += f'<text class="nm" x="0" y="{y + 5}">{name}</text>'
        if lo is not None:
            out += f'<rect class="rg{" acc" if acc else ""}" x="{X(lo):.1f}" y="{y - 8}" width="{X(hi) - X(lo):.1f}" height="16" rx="8"/>'
        if pt is not None:
            out += f'<circle class="{"dot acc" if acc or i == 1 else "dot"}" cx="{X(pt):.1f}" cy="{y}" r="{7 if i < 3 else 5}"/>'
        if not narrow:
            tx, anchor = (X(hi) + 12 if hi else X(pt) + 16), 'start'
            if i == 4: tx, anchor, txt = X(lo) - 12, 'end', short
            out += f'<text class="vl" x="{tx:.1f}" y="{y + 5}" text-anchor="{anchor}">{txt}</text>'
    out += f'<path class="ln" d="M{X(BASE):.1f} 6V{bot}"/><path class="ln now cnow" data-x0="{x0}" data-span="{span}" data-max="{MAX}" data-bot="{bot}" d="M0 0" style="display:none"/>'
    cls = 'narrow' if narrow else 'wide'
    return (f'<svg class="field {cls}" viewBox="0 0 {W} {bot + 34}" role="img" aria-label="Valuation ranges: cash-flow model {BEAR} to {BULL} dollars with a base case of {BASE}, '
            f'probability-weighted {WT}, price at writing {PRICE}, 52-week range 530 to 1,196, analyst targets 470 to 1,450 with an average of 1,172">'
            f'<g class="ax">{ticks}</g><g class="ticks">{lab}</g>{out}</svg>')


def body():
    toc = ''.join(f'<a href="#{c}"><i>{n:02d}</i>{t}</a>' for n, (c, t) in enumerate([
        ('overview', 'The business'), ('orders', 'The order book'), ('segments', 'Three segments'), ('profit', 'Profit and cash'),
        ('capital', 'Balance sheet'), ('value', 'Cash-flow value'), ('implied', 'What the price assumes'), ('risks', 'Risks'), ('rec', 'Rating')], 1))
    head = f'''<header class="ph rp">
  <div class="wrap">
    <div class="eyebrow mono"><a href="research.html">Research</a>&nbsp;/&nbsp;Equities &middot; Industrials &middot; October 20, 2026<span class="kind" title="Written and reviewed by Luis Diaz Busquets">Analyst report</span></div>
    <div class="rmark" data-logo="GEV" aria-hidden="true"><span class="tk">GEV</span></div>
    <h1>GE <em>Vernova</em></h1>
    <p class="sub">GE Vernova (GEV) makes the gas turbines, grid equipment and wind turbines behind a large share of the world&rsquo;s electricity, and AI data centers have filled its order book for years ahead. This report values the business on the company&rsquo;s own 2028 targets. The conclusion: an exceptional order book, at a price that already assumes more than those targets.</p>
    <div class="verdict">
      <div class="call"><span class="mono">Rating vs S&amp;P 500</span><b>{CALL}</b><small>On its own: {ABS}</small></div>
      <div><span class="mono">Value per share</span><b>${BASE}</b><small>Cash-flow model, base case</small></div>
      <div><span class="mono">Price at writing</span><b>${PRICE:,.2f}</b><small>Close, October 20, 2026</small></div>
      <div><span class="mono">Implied return</span><b class="dn">&minus;{(1 - BASE / PRICE) * 100:.1f}%</b><small>Price to value</small></div>
    </div>
  </div>
</header>
<section class="tight rbody">
  <div class="wrap rlay">
    <nav class="toc" aria-label="Chapters"><span class="mono">Contents</span>{toc}</nav>
    <div class="rmain">
      <div class="panel now" id="now">
        <div class="hd"><div><h3 class="sec">Since the report</h3><p>Today&rsquo;s close against the report&rsquo;s numbers, updated every weekday.</p></div><a class="pill gh sm" href="valuation.html?t=GEV">Today&rsquo;s automatic model &rarr;</a></div>
        <div class="kv four"><div><b id="nPx">&mdash;</b><span id="nPxD">Last close</span></div><div><b id="nChg">&mdash;</b><span>Since the report&rsquo;s ${PRICE:,.2f}</span></div><div><b id="nGap">&mdash;</b><span>Price against ${BASE} value</span></div><div><b id="nRg">&mdash;</b><span>52-week range</span></div></div>
      </div>
      <div class="panel" style="margin-top:16px">
        <div class="hd"><div><h3 class="sec">Where each method lands, per share</h3><p>The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the Street&rsquo;s targets. <span class="nowkey">The copper line marks the base case; the fine dotted line is today&rsquo;s close.</span></p></div></div>
        {field()}{field(True)}
        <p class="fine">Written on October 20, 2026, before third-quarter results on October 28. Figures are from GE Vernova&rsquo;s filings and releases unless noted. Not investment advice. The author holds GEV shares.</p>
      </div>
'''
    c1 = chap('01', 'overview', 'The business', 'The machines that make electricity, <em>and the grid that carries it.</em>', f'''
<div class="prose"><p>GE Vernova is the former energy business of General Electric, spun off as its own company in April 2024. It sells equipment and, more importantly, decades of service on that equipment. Once a gas turbine or a grid substation is installed, it needs parts, upgrades and maintenance for 30 years or more, so <b>every machine sold today is also a long service contract</b>.</p>
<p>Demand changed in 2024 and 2025. Power use in the U.S. had been flat for about fifteen years; AI data centers, factories moving back onshore and the electrification of heating and transport have pushed it up again. Utilities need new gas plants that can run around the clock, and the grid needs transformers and switchgear to connect them. GE Vernova sells both.</p></div>
<div class="cols eq tight2">
  <div class="prose"><h4>Power</h4><p>Gas turbines, the largest piece, plus steam, hydro and nuclear, including the BWRX-300 small modular reactor. Roughly half of revenue, and most of the profit.</p>
  <h4>Electrification</h4><p>Grid equipment: transformers, switchgear, high-voltage links and the software that runs them. In February 2026 it bought the remaining half of Prolec GE, a transformer maker, for $5.275 billion.</p></div>
  <div class="prose"><h4>Wind</h4><p>Onshore and offshore turbines. Revenue is shrinking and the segment loses money, held back by U.S. permitting, tariffs and offshore project problems.</p>
  <h4>Who it competes with</h4><p>In gas turbines, essentially two rivals: Siemens Energy and Mitsubishi Heavy Industries. In grid equipment: Siemens Energy, Hitachi Energy, Schneider Electric and Eaton. In wind: Vestas and Siemens Gamesa.</p></div>
</div>
<p class="key"><b>Takeaway.</b> A three-player market for large gas turbines, sold out for years, with a long tail of service revenue behind every sale. Few industrial businesses have that much visibility.</p>
{src(('prolec', 'Prolec GE acquisition, Feb 2026'), ('edgar', 'GE Vernova filings, SEC EDGAR'))}''')
    c2 = chap('02', 'orders', 'The order book', '$176 billion of backlog, <em>and turbines sold into 2031.</em>', f'''
{stats([('$176B', 'Total backlog, June 30, 2026'), ('$24.2B', 'Q2 orders, up 88% organic'), ('116 GW', 'Gas turbines under contract'), ('125 GW+', 'Target for the end of 2026'), ('$5B+', 'Data-center orders in the first half'), ('20 GW', 'Turbines built a year, from Q3 2026')])}
<div class="prose"><p>The backlog is the reason the stock has re-rated. It reached a record <b>$176 billion</b> in June, up $13 billion in one quarter and from $129 billion a year earlier. Second-quarter orders were $24.2 billion, 88% higher than a year before, and Power orders alone more than doubled.</p>
<p>In gas turbines GE Vernova counts two kinds of commitment: firm orders (53 GW in June) and slot reservations, where a customer pays to hold a production slot (63 GW). Together that is 116 GW, and the company expects to end 2026 above 125 GW. For scale, it plans to build 20 GW a year from the third quarter of 2026, 24 GW in 2028 and 30 GW by 2030, so <b>the factories are effectively sold out for about five years</b>. Management said it is already taking reservations for 2031.</p>
<p>A sold-out factory sets its own prices. Management said orders taken in the first half of 2026 were priced more than 20% above the fourth-quarter 2025 average, and those higher prices reach revenue only as the turbines ship, from 2027 onward.</p></div>
<p class="key"><b>Read.</b> The order book makes revenue for 2027 and 2028 unusually predictable. The open questions are margins and how long the cycle lasts, not demand.</p>
{src(('q2', 'Q2 2026 results'), ('ud', 'Utility Dive, gas backlog'))}''')
    c3 = chap('03', 'segments', 'Three segments', 'Two engines of profit, <em>one drag.</em>', f'''
{table(['Segment', 'Q2 orders', 'Q2 revenue', 'Q2 EBITDA margin', '2026 guidance', '2028 target margin'], [
    ['Power', '$16.7B, +134%', '$5.5B, +14%', '18.8%', '18&ndash;20% organic growth, 17&ndash;19% margin', '22%'],
    ['Electrification', '$6.3B, +66%', '$3.6B, +29% organic', '18.4%', '$14.5&ndash;15.0B revenue, 18&ndash;20% margin', '22%'],
    ['Wind', '$1.2B, &minus;40%', '$2.0B, &minus;11%', '&minus;13.6%', 'About $400M of losses', '6%'],
    ['Company', '$24.2B, +88%', '$11.1B, +12% organic', '11.3%', '$45.5&ndash;46.5B revenue, 12&ndash;14% margin', '20%'],
], 'mid')}
<div class="prose" style="margin-top:22px"><p><b>Power</b> is the profit engine. Its margin rose about 3 points in a year on an organic basis as pricing and volume improved, and service on the installed fleet keeps earnings steady between equipment cycles. <b>Electrification</b> is growing fastest: Prolec GE added about $5 billion of backlog, and data-center orders in the first half were more than double those for all of 2025. Both segments target a 22% margin by 2028.</p>
<p><b>Wind</b> is the drag. Orders fell 40%, the segment lost $275 million in the quarter, and the 2028 plan has its revenue still falling. Because Wind is shrinking while the other two grow, the company margin rises even if nothing else changes.</p></div>
<p class="key"><b>Read.</b> The 20% company margin target is mostly a mix story: more Power and Electrification at 22%, less Wind.</p>
{src(('q2', 'Q2 2026 segment results'), ('iu', '2028 outlook, Dec 2025'))}''')
    c4 = chap('04', 'profit', 'Profit and cash', 'Margins are rising fast, <em>from a low base.</em>', f'''
{table(['', 'FY2022', 'FY2023', 'FY2024', 'FY2025', 'TTM Jun 2026'], [
    ['Revenue', '$29.7B', '$33.2B', '$34.9B', '$38.1B', '$41.4B'],
    ['Gross margin', '11.7%', '14.5%', '17.4%', '19.8%', '20.2%'],
    ['Operating margin (GAAP)', '&minus;9.7%', '&minus;2.8%', '1.3%', '3.6%', '4.4%'],
    ['Net income', '&minus;$2.7B', '&minus;$0.4B', '$1.6B', '$4.9B', '$9.5B'],
    ['Operating cash flow', '&minus;$0.1B', '$1.2B', '$2.6B', '$5.0B', '$14.1B'],
    ['Free cash flow', '&minus;$0.6B', '$0.4B', '$1.7B', '$3.7B', '$12.4B'],
], 'allnum')}
<div class="prose" style="margin-top:22px"><p>Four years ago this business lost money. Gross margin has since nearly doubled to about 20%, and GAAP operating margin turned positive in 2024. On the company&rsquo;s adjusted measure, EBITDA margin was 11.3% in the second quarter, and it guides to 12 to 14% for 2026 and 20% by 2028.</p>
<p><b>Reported profit flatters the trend.</b> 2025 net income included a $2.1 billion tax benefit, and the last twelve months include a $4.0 billion gain from revaluing the half of Prolec GE it already owned. Strip those out and earnings are far lower, which is why the headline P/E of about 25 is misleading.</p>
<p><b>Cash flow also runs ahead of profit</b>, for a better reason: customers pay large deposits to secure turbine slots. Free cash flow was $5.1 billion in the second quarter alone, and 2026 guidance is $11.5 to $12.5 billion, more than double the earlier plan. That cash is real, but it is paid in advance for turbines still to be built, so it will slow as deliveries catch up with orders.</p></div>
<p class="key"><b>Read.</b> Value the business on operating margins, not on this year&rsquo;s net income or deposit-driven cash flow.</p>
{src(('q2', 'Q2 2026 results'), ('edgar', '10-K and 10-Q filings'))}''')
    c5 = chap('05', 'capital', 'Balance sheet', 'More cash than debt, <em>and a growing payout.</em>', f'''
{stats([('$13.1B', 'Cash, June 30, 2026'), ('$2.8B', 'Debt, mostly the 2026 notes'), ('$10B', 'Buyback authorization'), ('$854', 'Average buyback price in 2026'), ('$0.50', 'Quarterly dividend, doubled'), ('266M', 'Shares outstanding')])}
<div class="prose"><p>GE Vernova has net cash of about $10 billion, even after paying for Prolec GE, part of which was financed with $2.6 billion of senior notes. The plan is to return at least a third of the cash it generates. In the first half of 2026 it bought back 4.3 million shares at an average of $854 and returned $3.9 billion in total, and the quarterly dividend was doubled to $0.50 in December 2025.</p>
<p>The company also plans about $6 billion of capital spending and $5 billion of research and development from 2025 to 2028, much of it to lift turbine output from 20 to 30 GW a year inside existing factories.</p></div>
<p class="key"><b>Read.</b> The balance sheet carries no risk to the thesis. The only real question is the price paid for buybacks: shares repurchased near $850 are worth it only if the growth case below plays out.</p>
{src(('q2', 'Q2 2026 capital returns'), ('iu', 'Dividend and buyback, Dec 2025'))}''')
    c6 = chap('06', 'value', 'Cash-flow value', f'The company&rsquo;s own targets support about ${BASE} a share.', f'''
<div class="prose"><p>The model starts from 2026 revenue guidance, follows the company&rsquo;s 2028 plan, then lets growth fade to 3% by 2036. The base case gives GE Vernova everything it has promised: double-digit growth through 2028 and a 20% EBITDA margin from then on.</p></div>
{table(['Assumption', 'Base case', 'Basis'], [
    ['Revenue, 2026', '$46.0B', 'Midpoint of guidance, including Prolec GE'],
    ['Growth, 2027 and 2028', '12%, then 10%', 'Reaches about $57B in 2028: the $52B target plus Prolec GE'],
    ['Growth after 2028', 'Fades to 3% by 2036', 'Capacity reaches 30 GW in 2030; the cycle matures'],
    ['Adjusted EBITDA margin', '13% in 2026, 20% from 2028', 'The company&rsquo;s 2028 target, held for good'],
    ['Depreciation', '2.2% of revenue', 'Rising with the capacity build-out'],
    ['Tax rate', '21%', 'U.S. statutory rate'],
    ['Reinvestment', '$1 for every $4 of new revenue', 'Capital spending plus working capital'],
    ['Discount rate (WACC)', '10.7%', '5.2% Treasury, beta 1.25, 4.5% equity premium; almost no debt'],
    ['Terminal growth', '3.0%', 'With a 20% return on new capital'],
], 'mid')}
<div class="bridge rep">{''.join(f'<div><span class="mono">{k}</span><b class="num">{v}</b></div>' for k, v in [('PV of 2027&ndash;2036 cash flow', '$52.4B'), ('PV of terminal value', '$55.2B'), ('Enterprise value', '$107.6B'), ('Plus net cash', '$10.3B'), ('Equity value', '$117.8B'), ('Shares', '266.3M')])}<div class="res"><span class="mono">Per share</span><b class="num">${BASE}</b></div></div>
<h3 class="sec sm">Bear, base and bull</h3>
{table(['', 'Bear', 'Base', 'Bull'], [
    ['Growth, 2027 / 2028', '7% / 5%', '12% / 10%', '16% / 14%'],
    ['EBITDA margin from 2028', '16%', '20%', '23%'],
    ['WACC', '11.5%', '10.7%', '9.7%'],
    ['Value per share', f'${BEAR}', f'${BASE}', f'${BULL}'],
    ['Probability', '25%', '50%', '25%'],
], 'allnum')}
<div class="prose" style="margin-top:22px"><p>Weighted 25/50/25, the three cases give <b>${WT} a share</b>. Even the bull case, with faster growth, margins above target and a lower discount rate, reaches ${BULL}, still well below the price.</p></div>
<h3 class="sec sm">Sensitivity to the discount rate</h3>
{table(['WACC', '8.5%', '9.0%', '9.5%', '10.0%', '10.7%'], [['Value per share', '$607', '$559', '$518', '$484', f'${BASE}']], 'allnum')}
<p class="key"><b>Why the automatic model is lower.</b> The <a href="valuation.html?t=GEV">Valuation tool</a> sees only reported results, a 4% operating margin, and gives about $230. This report replaces that with the company&rsquo;s own margin targets. Switching the tool to High growth and setting a 17.5% operating margin gets close to these numbers.</p>
{src(('q2', 'Q2 2026 guidance'), ('iu', '2028 framework'))}{rep.checkit('gev')}''')
    c7 = chap('07', 'implied', 'What the price assumes', 'At $890, the market expects <em>much more than the plan.</em>', f'''
<div class="prose"><p>Running the model backwards shows what has to be true to justify ${PRICE:,.2f}. Holding everything else at the base case, the price needs <b>one</b> of these:</p></div>
{table(['To reach $890, you need', 'Instead of', 'How likely'], [
    ['Revenue growth of about 30% a year in 2027 and 2028', '12% and 10%, in line with guidance', 'Capacity limits make it hard: output rises from 20 to 24 GW by 2028'],
    ['An EBITDA margin near 39%', 'The 20% target', 'No large industrial equipment maker runs at that level'],
    ['A discount rate of about 6.7%', '10.7%', 'Lower than the cost of equity for most utilities'],
], '')}
<div class="prose" style="margin-top:22px"><p>In practice the market is betting on a mix: higher prices for longer, margins above 20% after 2028, and a power cycle that lasts well into the 2030s. Peer multiples tell the same story. At about $227 billion of enterprise value, the stock trades near <b>20 times the 2028 EBITDA target</b> and 38 times this year&rsquo;s, multiples usually reserved for software companies.</p>
<p>The Street is more positive. The average of 35 analyst targets is about $1,172, with a range of $470 to $1,450, and most rate it Buy. Their targets rest on earnings well beyond 2028 at premium multiples.</p></div>
<p class="key"><b>Insight.</b> The disagreement is about what happens after 2028. The company&rsquo;s plan, taken at face value, supports roughly half the current price.</p>
{src(('cons', 'Analyst consensus, Oct 2026'), ('bofa', 'BofA Q3 preview'))}''')
    c8 = chap('08', 'risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>', f'''
{table(['Risk', 'Why it matters'], [
    ['The gas cycle turns', 'GE&rsquo;s power business has boomed and collapsed before. If data-center demand slows or financing tightens, slot reservations are softer commitments than firm orders.'],
    ['Execution on capacity', 'Raising output from 20 to 30 GW while keeping quality and delivery dates is the core of the plan. Delays would push revenue and cash flow out.'],
    ['Wind', 'Losses of about $400 million in 2026, unresolved claims at Vineyard Wind and a weak U.S. market could cost more than planned.'],
    ['Tariffs and supply chain', 'Section 232 tariff decisions and input costs could squeeze margins on fixed-price contracts.'],
    ['Valuation', 'At about twice the base-case value, the stock is exposed to any disappointment in orders or margins, as the swing from a 52-week low of $530 shows.'],
], '')}
<div class="prose" style="margin-top:22px"><h4>Upside</h4><p>Pricing keeps rising; electrification grows faster than planned on data-center and grid spending; nuclear (the BWRX-300) becomes a real business; and margins pass 20% as Wind shrinks. Any two together would move the value well above the bull case.</p></div>
{src(('q2', 'Q2 2026 results'), ('ud', 'Utility Dive'))}''')
    G = dict(t='GEV', price=PRICE, base=BASE, wt=WT, private=False, rated=ratings.RATED,
             field=[('Analyst targets', 470, 1450, 1172, '')])
    G['call'], G['gap'], G['rel'] = ratings.rate(WT, PRICE)
    _, p1, p2 = ratings.REC['GEV']
    c9 = chap('09', 'rec', 'Rating', G['call'] + '. ' + ratings.REC['GEV'][0], prose(p1, '<b>What would change the value:</b> ' + p2) + rating_block(G) + rep.industry('GEV').replace('R_NAME_HOLDER', 'GE Vernova') + f'''
<div class="band sm"><div class="eyebrow mono">Final view</div><h2>A great business, <em>priced for a greater one.</em></h2><p>GE Vernova is one of the clearest beneficiaries of rising power demand. On the company&rsquo;s own targets the shares are fully valued; the upside depends on what comes after 2028.</p></div>
{src(('q3', 'Q3 2026 results webcast, Oct 28'), ('bofa', 'BofA Q3 preview'))}''')
    return head + c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + '''
    </div>
  </div>
</section>
'''
