"""Costco deep dive (FIN 370, Bryant University), rebuilt for LDB Finance."""

SHEET = 'https://docs.google.com/spreadsheets/d/{}/edit?usp=sharing'
S = {
    'prof': '1GYzuaUDXMzN18TX-xrKuqFp8VuVuJMV_RUbiwXcrDIc', 'port': '1qFl47qVynLiBY0RJIrfUOOqLp6vFK-KVqlyCs7wTFD8',
    'rev': '1eeW8vk5Cp4UuDwIy7UNRmpC33Kf4mj8iJ2tTTAIhom8', 'asset': '15ZvLjAP8uqmbAxFwoWjIlcfDfppHQubSWUrcbA0W6Gk',
    'assetrec': '1Px-F0LIWXYl9h14bGy98v-yCXQnM8BDMStB8Jvy3aJk', 'debt': '10zS6rbZRBBs87h3BubJ9AU-R1uee7m74am9d-MGLk3Q',
    'liab': '1iyQuPsbDV9ue0EhNoDqTDH6RbzKAVlqjqpdU6QEoUho', 'wacc': '1rXgoGmeicwP2SXfdBq7Tgz5d29-yLcqK9hDEgZjrkRE',
    'coc': '1EQ6MqIWIYfMItddHjZB01eUHj4tHHOMWtoDgLnipo20', 'fcf': '1LzADeM6441dEWFaIw6K_xsb_D7qgzpLusUA_m3Vp6cs',
    'fcfv': '1uVkB4cgdQHRjS0t6OZdCl7d9jANdZ4D-kJKP8Axw8cA', 'mult': '1elsOVF_wBSbyzNCfuFU7PQpmI-hNyQXSR-FfX5YJt2M',
    'multm': '1b89VWbUZ_W3A0ns5lcKznaKCzCvcRelpxBRYSLXMudw', 'sum': '1NEk8vhhDm5ciF0GA0JPizddWQddBANwzN4LCYbvd1UU',
}
MODEL = 'https://docs.google.com/spreadsheets/d/1vW76su3EjLUrlYMyZ_0XMBWCukPzG7V0/edit?usp=sharing&ouid=100503891749103320497&rtpof=true&sd=true'
TENK = 'https://drive.google.com/file/d/1i8Pw4PuAFjqeeenarINdwRnz4CVKuPpV/view?usp=sharing'
EXT = '<svg width="12" height="12" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def src(*items):
    return '<div class="srcs">' + ''.join(f'<a href="{SHEET.format(S[k]) if k in S else k}" target="_blank" rel="noopener">{t}{EXT}</a>' for k, t in items) + '</div>'


def stats(rows):
    return '<div class="kv">' + ''.join(f'<div><b>{v}</b><span>{k}</span></div>' for v, k in rows) + '</div>'


def table(head, rows, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="scroll"><table class="tbl txt {cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def chap(n, cid, label, h2, body):
    return f'<section class="chap" id="{cid}"><div class="eyebrow mono">{n} &middot; {label}</div><h2>{h2}</h2>{body}</section>'


# where each method lands, $0 to $1,400; a wide chart for desktop and a stacked one for phones
ROWS = [('Peer multiples', 395, 500, None, '$395 to $500'), ('Cash-flow model', None, None, 831.5, '$831.50'),
        ('Price at the time', None, None, 970.31, '$970.31'), ('Analyst targets', 650, 1315, 1072, '$650 to $1,315, average $1,072')]


def field(narrow=False):
    if narrow:
        x0, span, W, top, step, H = 8, 384, 400, 30, 64, 300
    else:
        x0, span, W, top, step, H = 170, 800, 1000, 44, 50, 240
    X = lambda v: x0 + v / 1400 * span
    bot = top + step * 3 + 22 if narrow else 206
    ticks = ''.join(f'<path d="M{X(v):.1f} 6V{bot}"/>' for v in range(0, 1401, 200))
    lab = ''.join(f'<text x="{X(v):.1f}" y="{bot + 22}" text-anchor="middle">${v:,}</text>' for v in range(0, 1401, 400))
    out = ''
    for i, (name, lo, hi, pt, txt) in enumerate(ROWS):
        y = top + i * step
        if narrow:
            out += f'<text class="nm" x="{x0}" y="{y - 10}">{name}<tspan class="vl" dx="10">{txt.split(", average")[0]}</tspan></text>'
        else:
            out += f'<text class="nm" x="0" y="{y + 5}">{name}</text>'
        if lo is not None:
            out += f'<rect class="rg{" acc" if i == 0 else ""}" x="{X(lo):.1f}" y="{y - 8}" width="{X(hi) - X(lo):.1f}" height="16" rx="8"/>'
        if pt is not None:
            out += f'<circle class="{"dot acc" if i == 1 else "dot"}" cx="{X(pt):.1f}" cy="{y}" r="{7 if i < 3 else 5}"/>'
        if not narrow:
            tx, anchor = (X(hi) + 12 if hi else X(pt) + 16), 'start'
            if i == 1: tx, anchor = X(pt) - 16, 'end'
            if i == 3: tx, anchor, txt = X(lo) - 12, 'end', txt.split(', average')[0]
            out += f'<text class="vl" x="{tx:.1f}" y="{y + 5}" text-anchor="{anchor}">{txt}</text>'
    out += f'<path class="ln" d="M{X(831.5):.1f} 6V{bot}"/><path class="ln now cnow" data-x0="{x0}" data-span="{span}" data-bot="{bot}" d="M0 0" style="display:none"/>'
    cls = 'narrow' if narrow else 'wide'
    return f'<svg class="field {cls}" viewBox="0 0 {W} {bot + 34}" role="img" aria-label="Valuation ranges: peer multiples 395 to 500 dollars, cash-flow model 831.50, price at the time 970.31, analyst targets 650 to 1,315 with an average of 1,072"><g class="ax">{ticks}</g><g class="ticks">{lab}</g>{out}</svg>'


def body():
    toc = ''.join(f'<a href="#{c}"><i>{n:02d}</i>{t}</a>' for n, (c, t) in enumerate([
        ('overview', 'The business'), ('profit', 'Profitability'), ('revenue', 'Revenue quality'), ('assets', 'Working capital'),
        ('debt', 'Debt'), ('wacc', 'Cost of capital'), ('fcf', 'Cash-flow value'), ('mult', 'Peer multiples'), ('rec', 'Recommendation')], 1))
    head = f'''<header class="ph rp">
  <div class="wrap">
    <div class="eyebrow mono"><a href="research.html">Research</a>&nbsp;/&nbsp;Equities &middot; FIN 370, Bryant University<span class="kind" title="Coursework, priced section by section during the semester">Course research</span></div>
    <h1>Costco <em>Wholesale</em></h1>
    <p class="sub">A full fundamental analysis of Costco (COST) against Walmart, Target and BJ&rsquo;s: profitability, revenue quality, working capital, debt, cost of capital and two valuation approaches. The conclusion: an excellent business, trading above what its cash flows support.</p>
    <div class="verdict">
      <div class="call"><span class="mono">Recommendation</span><b>Hold / Wait</b></div>
      <div><span class="mono">Value per share</span><b>$831.50</b><small>Free cash flow model</small></div>
      <div><span class="mono">Price at the time</span><b>$970.31</b><small>When the report closed</small></div>
      <div><span class="mono">Implied return</span><b class="dn">&minus;14.31%</b><small>Price to value</small></div>
    </div>
  </div>
</header>
<section class="tight rbody">
  <div class="wrap rlay">
    <nav class="toc" aria-label="Chapters"><span class="mono">Contents</span>{toc}</nav>
    <div class="rmain">
      <div class="panel now" id="now">
        <div class="hd"><div><h3 class="sec">Since the report</h3><p>Today&rsquo;s close against the report&rsquo;s numbers, updated every weekday.</p></div><a class="pill gh sm" href="valuation.html?t=COST">Today&rsquo;s automatic model &rarr;</a></div>
        <div class="kv four"><div><b id="nPx">&mdash;</b><span id="nPxD">Last close</span></div><div><b id="nChg">&mdash;</b><span>Since the report&rsquo;s $970.31</span></div><div><b id="nGap">&mdash;</b><span>Price against $831.50 value</span></div><div><b id="nRg">&mdash;</b><span>52-week range</span></div></div>
      </div>
      <div class="panel" style="margin-top:16px">
        <div class="hd"><div><h3 class="sec">Where each method lands, per share</h3><p>Peer multiples, the cash-flow model, the price at the time and the Street&rsquo;s targets. <span class="nowkey">The copper line marks the model&rsquo;s value; the fine dotted line is today&rsquo;s close.</span></p></div></div>
        {field()}{field(True)}
        <p class="fine">Prices and estimates are as of when each section was written during the semester, so the price quoted varies slightly between sections. This is coursework and not investment advice.</p>
      </div>
'''
    c1 = chap('01', 'overview', 'The business', 'A membership business <em>that happens to sell groceries.</em>', f'''
<div class="prose"><p>Costco runs a membership-based warehouse model: a limited selection of branded and private-label goods at low prices, for households and small businesses. The strategy is high volume, fast inventory turnover and tight cost control, which keeps merchandise margins thin. <b>A large share of operating income comes from annual membership fees</b>, a stable and recurring stream, and the Kirkland Signature private label adds loyalty and margin.</p></div>
<blockquote>&ldquo;To continually provide our members with quality goods and services at the lowest possible prices.&rdquo;<cite>Costco&rsquo;s mission</cite></blockquote>
<div class="cols eq tight2">
  <div class="prose"><h4>Sector</h4><p>Consumer Staples, Retail Consumer Staples subsector, as a warehouse club. Demand for food, household goods and everyday necessities holds up across the cycle, which gives Costco steady traffic and predictable cash flow.</p>
  <h4>Industry outlook</h4><p>Staples retail is defensive, and scale wins on supplier terms and logistics. The pressures are labor costs, supply-chain inflation, thin margins and the cost of building e-commerce. Disciplined, loyal-customer businesses like Costco are best placed.</p></div>
  <div class="prose"><h4>How it reaches members</h4><ul class="dl">
    <li><b>Warehouses</b> are the main channel: bulk buying at low margins.</li>
    <li><b>Costco.com</b> adds large and specialty items.</li>
    <li><b>Services</b> such as pharmacy, optical, hearing aids, fuel, food courts and travel bring members back.</li>
    <li><b>Business sales</b> serve small and mid-sized companies with bulk purchasing and delivery.</li></ul>
  <p>No single supplier or customer is a material share of purchases or revenue, so concentration risk is low.</p></div>
</div>
<h3 class="sec sm">Competitors</h3>
{table(['Peer', 'Where it overlaps', 'Where it differs'], [
    ['BJ&rsquo;s Wholesale Club', 'Membership warehouse model, bulk pricing, competes for the same club members', 'Smaller and almost entirely domestic, more promotional'],
    ['Walmart', 'Scale, global footprint, cost leadership, grocery focus', 'No membership at core stores, broader customer base, less fee income'],
    ['Target', 'National big-box footprint, staples plus discretionary, strong private labels', 'No membership fees, more cyclical, more reliance on promotions'],
    ['Dollar General', 'Value-conscious shoppers, everyday staples', 'Smaller baskets, lower-income and rural focus, higher product margins'],
    ['Dollar Tree', 'Low prices and essentials', 'Fixed price points, no recurring revenue, more cyclical customers']])}
<p class="key"><b>Takeaway.</b> Membership revenue, a low-margin high-volume model and steady renewal fees give Costco more earnings visibility than peers that lean on promotions, discretionary spending or merchandise markups.</p>
{src((TENK, 'Costco 10-K, FY2025'))}''')
    c2 = chap('02', 'profit', 'Profitability', 'The lowest margins in the group, <em>and the steadiest returns.</em>', f'''
{stats([('12.84%', 'Gross margin, FY2025'), ('3.77%', 'Operating margin, from 3.47%'), ('2.94%', 'Net margin, from 2.56%'), ('10.50%', 'Return on assets, from 8.45%'), ('30&ndash;33%', 'Return on net operating assets'), ('25&ndash;31%', 'Return on equity')])}
<div class="prose"><p>From fiscal 2021 to 2025, gross margin sat around 12 to 13% every year, the lowest of the four, by design. Even so, <b>operating margin rose from 3.47% to 3.77% and net margin from 2.56% to 2.94%</b>, a steady gain in efficiency. Target&rsquo;s margins swung sharply in 2022, Walmart&rsquo;s were stable and moderate, and BJ&rsquo;s ran slightly above Costco without improving as consistently.</p>
<p>Returns are where Costco pulls away: return on assets climbed from 8.45% to about 10.5%, and return on net operating assets held at roughly 30 to 33%.</p></div>
<h3 class="sec sm">DuPont: what drives return on equity</h3>
{table(['Component', 'FY2021', 'FY2025', 'Read'], [
    ['Net profit margin', '2.56%', '2.94%', 'Improving steadily'],
    ['Asset turnover', '3.41&times;', '3.75&times;', 'More sales from every dollar of assets'],
    ['Equity multiplier', '3.28&times;', '2.64&times;', 'Less reliance on leverage'],
], 'nums')}
<p class="key"><b>Read.</b> Return on equity stayed high while leverage fell, so shareholder returns come from operations, not debt.</p>
{src(('prof', 'Profitability sheet'), ('port', 'Portfolio sheet'))}''')
    c3 = chap('03', 'revenue', 'Revenue quality', 'Growth that comes from scale, <em>not from markup.</em>', f'''
{stats([('87&ndash;88%', 'Cost of goods, share of revenue'), ('~9%', 'SG&amp;A, share of revenue'), ('&gt; 1.0&times;', 'Operating cash flow to net income'), ('72.7%', 'Revenue from the U.S.'), ('13.4%', 'Revenue from Canada'), ('~92%', 'From developed markets')])}
<div class="prose"><p>Top-line growth comes from net merchandise sales and membership fees: new warehouses, comparable-sales growth and high renewal rates. Cost of goods stays at 87 to 88% of revenue, so <b>growth is coming from volume and efficiency, not wider margins</b>. BJ&rsquo;s cost of goods runs about 81 to 82%, a different pricing structure, with growth that has slowed more noticeably.</p>
<p>SG&amp;A held near 9% of revenue through inflation and wage pressure, against 14 to 15% at BJ&rsquo;s, and operating income as a share of revenue is flat to rising: operating leverage as the business scales.</p>
<p><b>Earnings quality is high.</b> Operating cash flow has exceeded net income every year, so reported profit is backed by cash rather than accruals. BJ&rsquo;s also clears 1.0 but with more swings from working capital.</p>
<p>Costco is a pure-play warehouse club. About 86 to 87% of revenue comes from the Americas and roughly 92% from developed markets, which limits political and currency risk but also limits exposure to faster-growing emerging markets.</p></div>
{src(('rev', 'Revenue recognition sheet'))}''')
    c4 = chap('04', 'assets', 'Working capital', 'Customers pay <em>before suppliers are due.</em>', f'''
<div class="prose"><p>By textbook liquidity ratios Costco looks thin. That is the model working: fast inventory turnover and near-instant collection mean <b>the business funds itself from operations</b>.</p></div>
{table(['Measure', 'Five-year range', 'What it shows'], [
    ['Cash ratio', '0.31 to 0.45', 'Little idle cash; liquidity comes from turnover'],
    ['Current ratio', 'Close to 1.0', 'Normal for high-volume retail'],
    ['Days cash on hand', '16 to 23 days', 'Steady cash flow means small reserves'],
    ['Receivables, share of assets', '3 to 4%', 'Most sales are paid on the spot'],
    ['Days sales outstanding', '3 to 4 days', 'Very fast collection, low credit risk'],
    ['Inventory days', '27 to 33 days', 'An efficient supply chain'],
    ['Inventory turnover', '11 to 13&times;', 'Goods move quickly, low holding cost'],
    ['Days payable outstanding', '30 to 35 days', 'Suppliers partly finance inventory'],
    ['Cash conversion cycle', 'Near zero', 'Costco is often paid before it pays'],
    ['Net PP&amp;E, share of assets', '43 to 47%', 'It owns its warehouses and distribution'],
    ['PP&amp;E turnover', '7 to 8&times;', 'High sales per dollar of property'],
], 'mid')}
{src(('asset', 'Asset analysis sheet'), ('assetrec', 'Asset recognition sheet'))}''')
    c5 = chap('05', 'debt', 'Debt', 'Almost no leverage, <em>interest covered eighty times.</em>', f'''
{stats([('2.46%', 'Debt to market value of equity'), ('12.89%', 'Debt to total assets'), ('80&times;+', 'EBITDA to interest'), ('86&times;+', 'Operating cash flow to interest'), ('&gt; 3', 'Altman Z-score, all five years'), ('Staggered', 'Senior notes plus leases')])}
<div class="prose"><p>Costco carries far less debt than BJ&rsquo;s, Target or Walmart. In 2025 interest-bearing debt was about <b>2.46% of the market value of equity</b> and 12.89% of total assets, the lowest of the group. EBITDA covers interest more than 80 times.</p>
<p>The Altman Z-score stayed above the safe-zone line of 3 every year, carried by a market value far above total liabilities and more than three dollars of sales per dollar of assets. The liquidity term looks weak only because working capital is negative, which is normal for a fast-turning retailer.</p>
<p>Long-term debt is mostly senior unsecured notes plus leases on warehouses and offices, with maturities spread over many years to keep refinancing risk low.</p></div>
{src(('debt', 'Debt analysis sheet'), ('liab', 'Liabilities and debt financing'))}''')
    c6 = chap('06', 'wacc', 'Cost of capital', 'A discount rate of 8.36%, <em>built with CAPM.</em>', f'''
{stats([('8.36%', 'WACC, base case'), ('4.22%', 'Risk-free rate, 10-year Treasury'), ('5.0%', 'Market risk premium'), ('0.86', 'Beta, FactSet and Capital IQ average')])}
<div class="prose"><p>The weighted average cost of capital blends the cost of debt and the cost of equity, and it is the discount rate in the valuation. Cost of equity comes from the Capital Asset Pricing Model: a 4.22% risk-free rate, a 5.0% market risk premium and a beta of 0.86, the average of the FactSet and S&amp;P Capital IQ estimates. Cost of debt is from market data, after tax, with weights from the market value of equity and the book value of debt.</p>
<p>A lower beta lowers the cost of equity and the WACC; a higher one raises both. With debt so small, <b>the WACC is almost entirely the cost of equity</b>.</p></div>
{src(('wacc', 'WACC sheet'), ('coc', 'Cost of capital sheet'))}''')
    c7 = chap('07', 'fcf', 'Cash-flow value', 'The cash flows support $831.50 a share. <em>The market paid more.</em>', f'''
<div class="prose"><p>The free cash flow model values Costco at <b>$831.50 a share</b>. Against a price of about $994.68 when this section was written, the stock was about $163 a share above the model&rsquo;s value.</p></div>
{table(['Assumption', 'Value', 'Basis'], [
    ['Revenue growth, 2026&ndash;2030', '8.45% falling to 5.07%', 'FactSet estimates; expansion continues but slows'],
    ['Terminal growth', '3.0%', 'In line with long-run economic growth'],
    ['Cost of goods', '86 to 87% of sales', 'FactSet projections and historical averages'],
    ['SG&amp;A', '7.87% of sales', 'Recent average, held roughly flat'],
    ['Change in net operating assets', '&minus;0.58% of sales', 'Ongoing investment in warehouses and logistics'],
    ['WACC', '8.36%', 'From chapter 06'],
], 'mid')}
<div class="prose" style="margin-top:22px"><p><b>Reading the gap.</b> The market is pricing in stronger long-term growth, continued global expansion and lasting success of the membership model. The model is more conservative: growth fades gradually and reinvestment continues. The fundamentals are strong; the price carries a premium to them.</p></div>
{src(('fcf', 'Free cash flow sheet'), ('fcfv', 'FCF valuation sheet'))}''')
    c8 = chap('08', 'mult', 'Peer multiples', 'Peers say $300 to $500. <em>That is the premium, measured.</em>', f'''
<div class="prose"><p>Per-share figures for Costco and its peers come from forward FactSet estimates, so every comparison is on the same basis. Costco trades at a premium on every multiple, most of all on price to earnings and price to cash flow.</p>
<p>Peer multiples were summarized by average, first quartile and third quartile. Given Costco&rsquo;s quality, <b>the third quartile was used as the benchmark</b>, and even that implies only about $300 to $500 a share.</p></div>
<p class="key"><b>Insight.</b> The premium is large enough that ordinary peer multiples cannot capture it. The market is paying for the membership model and its consistency, not for this year&rsquo;s earnings.</p>
{src(('mult', 'Multiples sheet'), ('multm', 'Market multiples sheet'))}''')
    c9 = chap('09', 'rec', 'Recommendation', 'Hold and wait. <em>A great company with no margin of safety.</em>', f'''
<div class="prose"><p>At $970.31 against a value of $831.50, the stock implies about <b>14.31% downside</b>. The fundamentals are excellent, but the price leaves no room for error, so the call is <b>Hold / Wait</b> for a better entry point.</p>
<h4>Why the cash-flow model carries all the weight</h4>
<p>Multiples (P/E, P/S, P/B and P/CF) give roughly $395 to $500 a share. They were left out of the final number because they cannot capture the membership revenue and the stability of long-run growth, so the cash-flow model has a 100% weight.</p>
<h4>Where this differs from the Street</h4>
<p>Analysts are more optimistic: an average target of about $1,072 within a range of $650 to $1,315, with Buy and Overweight ratings at roughly 55 to 65% over time and very few Sells. Their targets build in growth, continued dominance and premium multiples. This analysis puts price discipline first: even the best companies can be poor investments at the wrong price.</p></div>
<h3 class="sec sm">Second look: a blended value</h3>
<div class="prose"><p>The course model weights the cash-flow value at 100%. Most practitioners blend methods, so this table shows what a 70/30 split between the cash-flow model and peer multiples gives, using the midpoint of the $395 to $500 multiples range.</p></div>
{table(['Method', 'Value', 'Weight', 'Contribution'], [['Cash-flow model', '$831.50', '70%', '$582.05'], ['Peer multiples, midpoint', '$447.50', '30%', '$134.25'], ['Blended value', '', '', '<b>$716.30</b>']], 'allnum')}
<p class="key"><b>Read.</b> A blend lowers the value to about $716, 26% below the $970.31 price, so it strengthens the Hold / Wait call. The official number stays at $831.50, the figure submitted for FIN 370.</p>
<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Own the business, <em>wait for the price.</em></h2><p>Costco remains a high-quality, well-managed company with strong long-term fundamentals. Its valuation is what limits the upside.</p></div>
{src(('sum', 'Valuation summary sheet'), (MODEL, 'Full financial model'))}''')
    return head + c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + '''
    </div>
  </div>
</section>
'''
