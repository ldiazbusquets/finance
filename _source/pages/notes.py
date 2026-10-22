"""Research notes on bonds and the economy. Figures inside <b data-v> tags are filled in live from
data/markets.json (FRED) by site.js, so the notes stay current between rewrites; fixed facts are dated."""
import json
import latam as LA

EXT = '<svg width="12" height="12" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
DATE = 'October 21, 2026'


def V(k, f='v'):
    return f'<b class="lv" data-v="{k}" data-f="{f}">&mdash;</b>'


def src(links):
    return '<div class="srcs">' + ''.join(f'<a href="{u}" target="_blank" rel="noopener">{t}{EXT}</a>' for t, u in links) + '</div>'


def chart(title, sub, lines, r='y5', zero=False, dp=0, h=280, curve=False):
    spec = {'curve': 1} if curve else {'lines': lines, 'r': r, 'zero': int(zero), 'dp': dp}
    leg = '<div class="legend" data-curvelegend></div>' if curve else f'<div class="legend" data-legend=\'{json.dumps(lines)}\'></div>'
    return (f'<div class="panel" style="margin:22px 0"><div class="hd"><div><h3 class="sec">{title}</h3><p>{sub}</p></div>{leg}</div>'
            f'<svg class="chart" style="height:{h}px" data-chart=\'{json.dumps(spec)}\'></svg><p class="fine" data-stamp></p></div>')


def tiles(keys):
    return f'<div class="ntiles" data-tiles="{",".join(keys)}"></div>'


def sec(h, *ps):
    return f'<h2 class="nh">{h}</h2>' + ''.join(p if p.startswith(('<div', '<p')) else f'<p>{p}</p>' for p in ps)


def key(t):
    return f'<p class="key"><b>Takeaway.</b> {t}</p>'


FRED = lambda sid: f'https://fred.stlouisfed.org/series/{sid}'

NOTES = [
    dict(slug='note-yield-curve', code='FI-01', cat='fi', label='Fixed income', title='Reading the <em>yield curve</em>',
         name='Reading the yield curve', card='What the shape of the Treasury curve says about growth, inflation and the Fed.',
         sub='The yield curve plots what the U.S. government pays to borrow for different lengths of time. Its shape is one of the most watched signals in markets, because it compresses what investors expect for growth, inflation and the Fed into a single line.',
         body=lambda: tiles(['DGS3MO', 'DGS2', 'DGS10', 'T10Y2Y'])
         + sec('What the curve is',
               'Each point on the curve is the yield on a Treasury of a given maturity, from one month to thirty years. Normally it slopes <b>upward</b>: lenders want more to tie up money for longer, because more can go wrong over thirty years than over three months, from inflation to a change in Fed policy. That extra yield for time is called the <b>term premium</b>.',
               'Short yields are anchored by the Federal Reserve&rsquo;s policy rate. Long yields reflect where investors expect short rates to average over the life of the bond, plus that term premium.')
         + chart('The curve today', 'Yield by maturity, today against a month and a year ago.', [], curve=True)
         + sec('Today&rsquo;s shape',
               f'The 10-year yields {V("DGS10")} and the 2-year {V("DGS2")}, so the curve slopes up by {V("T10Y2Y")} between them. A year ago the 10-year was at {V("DGS10", "y1")}: long yields have moved {V("DGS10", "c1")} since.',
               '<div data-calc="shape"></div>')
         + chart('The 10-year minus the 2-year', 'Below zero, the curve is inverted.', [['T10Y2Y', 'acc', 2, '', 1]], zero=True, dp=1)
         + sec('Why inversions matter',
               'When short yields rise above long ones, the curve is <b>inverted</b>. It happens when the Fed holds short rates high and investors expect it to cut later because the economy will weaken. An inverted 10-year minus 2-year spread came before most U.S. recessions since the 1970s, which is why it is watched so closely.',
               'It is a signal, not a rule. The curve was inverted from mid-2022 to late 2024, the longest stretch on record, and the economy kept growing. Strong household finances and government spending did more to offset tight policy than the curve allowed for.')
         + key('Read the curve as the market&rsquo;s summary of rates and inflation, not as a forecast on its own. Its shape today says inflation risk, not recession, is what bond investors are pricing.')
         + src([('FRED: 10-year minus 2-year', FRED('T10Y2Y')), ('U.S. Treasury yield curve rates', 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates')])),

    dict(slug='note-duration', code='FI-02', cat='fi', label='Fixed income', title='Duration and <em>convexity</em>',
         name='Duration and convexity', card='How much a bond moves when rates move, worked through with real Treasuries.',
         sub='A bond&rsquo;s price falls when interest rates rise. Duration measures by how much; convexity explains why the loss on a rise is smaller than the gain on an equal fall. Both are worked through below with today&rsquo;s Treasury yields.',
         body=lambda: sec('Duration in one sentence',
               '<b>Modified duration</b> is the percentage a bond&rsquo;s price changes for a one-point change in its yield. A duration of 8 means a rise in yields from 5% to 6% costs about 8% of the price.',
               'It grows with maturity, because the money comes back later and is discounted for longer, and it shrinks with a higher coupon, because more of the money comes back sooner. A zero-coupon bond&rsquo;s duration roughly equals its maturity.')
         + '<div class="panel" style="margin:22px 0"><div class="hd"><div><h3 class="sec">Today&rsquo;s Treasuries, priced at par</h3><p>Each bond pays a coupon equal to today&rsquo;s yield for its maturity, twice a year. Price change for a one-point move in either direction.</p></div></div><div data-calc="dur"></div><p class="fine" data-stamp></p></div>'
         + sec('Convexity: why the two columns are not equal',
               'Look across each row: the gain when yields fall is larger than the loss when they rise. That asymmetry is <b>convexity</b>. A bond&rsquo;s price is a curve, not a straight line, so duration (the slope at today&rsquo;s yield) overstates the loss and understates the gain for large moves.',
               'Convexity matters most for long bonds and big moves. For a 30-year Treasury, the difference between the duration estimate and the true price change runs to several percentage points on a two-point move.')
         + sec('How investors use it',
               '<b>Matching:</b> a pension fund that owes payments in 15 years holds bonds with a duration near 15, so a change in rates moves its assets and its liabilities together.',
               '<b>Positioning:</b> a manager who expects rates to fall lengthens duration to gain more; one who expects them to rise shortens it. <b>DV01</b>, the dollar change for a one-basis-point move, turns duration into money.')
         + key('Duration tells you how much rate risk you own; convexity tells you that owning long bonds pays you a little for big moves in either direction.')
         + '<p class="cta2"><a class="pill cu" href="bonds.html"><span class="ic"><svg width="14" height="14" viewBox="0 0 16 16"><path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>Price any bond in the bond pricer</a></p>'),

    dict(slug='note-credit-spreads', code='FI-03', cat='fi', label='Fixed income', title='Credit <em>spreads</em>',
         name='Credit spreads', card='What investors demand to lend to riskier companies, and what that signals.',
         sub='A credit spread is the extra yield a company pays over a Treasury of the same maturity. It is the price of default risk, and it moves with how nervous investors are about the economy.',
         body=lambda: tiles(['BAMLC0A0CM', 'BAMLH0A0HYM2', 'DGS10'])
         + sec('What the spread pays for',
               'A company bond yields more than a Treasury because the company can default, its bonds are harder to sell, and in a crisis they fall when investors most need cash. The spread bundles all three.',
               f'Spreads come in two families. <b>Investment-grade</b> companies, rated BBB&minus; or better, pay {V("BAMLC0A0CM")} over Treasuries today. <b>High-yield</b> companies, rated below that, pay {V("BAMLH0A0HYM2")}.')
         + chart('Spreads over Treasuries', 'Option-adjusted spreads on the ICE BofA U.S. corporate indexes.', [['BAMLH0A0HYM2', 'acc', 2], ['BAMLC0A0CM', 't2', 1.4]], dp=1)
         + sec('What today&rsquo;s level says',
               'Over the long run, the high-yield spread has averaged about 5 percentage points. It reached about 20 points at the end of 2008 and about 11 in March 2020. At ' + V('BAMLH0A0HYM2') + ', investors are asking for well below the average, which means they expect few defaults and are comfortable taking risk.',
               'Tight spreads are a sign of confidence, but also of thin protection: when they are low, there is little cushion if the economy turns. Widening spreads have often been one of the earlier warnings of trouble, because bond investors focus on the downside.')
         + sec('How it connects to stocks',
               'Spreads and stock prices tend to move as mirror images. When spreads widen, the cost of borrowing rises for the riskiest companies first, and their shares usually fall with it. Watching the high-yield spread is a quick way to check whether the bond market agrees with the stock market&rsquo;s mood.')
         + key('Low spreads mean investors are relaxed about credit. That helps companies borrow, but it leaves less margin of safety for lenders.')
         + src([('FRED: high-yield spread', FRED('BAMLH0A0HYM2')), ('FRED: investment-grade spread', FRED('BAMLC0A0CM'))])),

    dict(slug='note-inflation', code='MAC-01', cat='mac', label='Macro', title='Inflation, <em>measured three ways</em>',
         name='Inflation, measured three ways', card='CPI, core CPI and core PCE: why they differ and which one the Fed watches.',
         sub='The U.S. publishes several inflation measures, and they rarely agree. The differences come from what each one counts and how it weights it, and they matter because the Fed targets one measure in particular.',
         body=lambda: tiles(['CPI_YOY', 'CORE_CPI_YOY', 'CORE_PCE_YOY', 'T10YIE'])
         + sec('The three measures',
               f'<b>CPI</b>, from the Bureau of Labor Statistics, tracks the prices urban households pay for a fixed basket of goods and services. It rose {V("CPI_YOY")} in the year to {V("CPI_YOY", "m")}.',
               f'<b>Core CPI</b> removes food and energy, whose prices swing with weather and oil, to show the underlying trend: {V("CORE_CPI_YOY")}.',
               f'<b>Core PCE</b>, from the Bureau of Economic Analysis, measures prices across all consumer spending, including what is paid on households&rsquo; behalf such as employer health insurance. It rose {V("CORE_PCE_YOY")} in the year to {V("CORE_PCE_YOY", "m")}. This is the measure the Federal Reserve targets at 2%.')
         + chart('Inflation, year over year', 'Monthly readings over five years.', [['CPI_YOY', 'acc', 2], ['CORE_CPI_YOY', 't2', 1.4], ['CORE_PCE_YOY', 't3', 1.4, '4 4']], dp=0)
         + sec('Why the measures differ',
               '<b>Weights:</b> housing is roughly a third of CPI but a much smaller share of PCE, so rents move CPI more. <b>Scope:</b> PCE includes spending that households do not pay directly, like medical care paid by insurers. <b>Formula:</b> PCE adjusts as people switch to cheaper goods when prices rise, which CPI does more slowly. Over long periods those differences have left CPI running a few tenths of a point above PCE, though the gap can flip for months at a time when items weighted more heavily in PCE, such as health care, rise faster.')
         + sec('What the bond market expects',
               f'The <b>10-year breakeven</b>, the gap between ordinary and inflation-protected Treasury yields, shows the average inflation investors are pricing for the next decade: {V("T10YIE")}. When it rises, investors think inflation will last; when it stays near 2&ndash;2.5%, they trust the Fed to bring it back.')
         + key('Watch core PCE for what the Fed will do, CPI for what households feel, and the breakeven for whether markets believe the Fed.')
         + src([('FRED: CPI', FRED('CPIAUCSL')), ('FRED: core PCE prices', FRED('PCEPILFE')), ('FRED: 10-year breakeven', FRED('T10YIE'))])),

    dict(slug='note-policy-rate', code='MAC-02', cat='mac', label='Macro', title='The policy <em>rate path</em>',
         name='The policy rate path', card='Where the fed funds rate is, where markets expect it to go, and why.',
         sub='The federal funds rate is the Fed&rsquo;s main tool: the rate banks charge each other overnight. In September 2026 the Fed raised it for the first time in more than three years. This note covers where it is, what the Fed says comes next, and what markets are pricing.',
         body=lambda: tiles(['DFF', 'DGS3MO', 'DGS2', 'CORE_PCE_YOY'])
         + sec('Where the rate is',
               f'On September 16, 2026 the Federal Open Market Committee voted 12&ndash;0 to raise the target range by a quarter point, to <b>3.75&ndash;4.00%</b>, its first increase since July 2023. The effective rate is {V("DFF")}. The statement said inflation &ldquo;remains elevated&rdquo; and that the move would support a &ldquo;timelier return&rdquo; to the 2% goal. It was the first hike under Chair Kevin Warsh, who took office in May.')
         + chart('The policy rate, the 2-year and inflation', 'Five years of the effective fed funds rate, the 2-year Treasury and core PCE inflation.', [['DFF', 'acc', 2], ['DGS2', 't2', 1.4], ['CORE_PCE_YOY', 't3', 1.2, '4 4']], dp=0)
         + sec('What the Fed projects',
               'In September, officials&rsquo; median projection (the &ldquo;dot plot&rdquo;) put the rate at <b>4.1% at the end of 2026</b>, implying one more quarter-point increase, and 4.1% at the end of 2027 before easing to 3.9% in 2028. Their estimate of the long-run neutral rate rose to 3.2%. Sixteen of eighteen officials expected at least one more hike this year.')
         + sec('What markets are pricing', '<div data-calc="path"></div>')
         + sec('Why it matters for investors',
               'Higher policy rates raise the discount rate used to value every stock and bond. They hit long-duration assets hardest: growth stocks, long bonds and utilities. That is a large part of why the cash-flow values in the holdings reports come in below today&rsquo;s prices, since the 10-year Treasury is ' + V('DGS10') + '. The next decision is due on October 27&ndash;28.')
         + key('The Fed has turned from pausing to tightening. Until core inflation clearly falls back toward 2%, the burden of proof is on rate cuts, not hikes.')
         + src([('FOMC statement, Sept 16, 2026', 'https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm'), ('Projections summary', 'https://www.chase.com/personal/investments/learning-and-insights/article/federal-reserve-raises-rates-officials-signal-one-more-hike-in-2026'), ('FRED: fed funds', FRED('DFF'))])),

    dict(slug='note-puerto-rico', code='MAC-03', cat='mac', label='Macro', title='Puerto Rico&rsquo;s <em>economy</em>',
         name='Puerto Rico&rsquo;s economy', card='Growth, federal funds and the local tax picture for investors on the island.',
         sub='Puerto Rico is a U.S. territory with its own tax system, a shrinking population and an economy built on pharmaceutical manufacturing and federal transfers. Growth is slow, but the job market is the strongest it has been in decades.',
         body=lambda: tiles(['PR_UNRATE', 'PR_JOBS_YOY', 'UNRATE'])
         + sec('Output: GDP versus GNP',
               'Real GDP grew just <b>0.3% in fiscal 2025</b> (July 2024 to June 2025), to $103.9 billion in 2017 dollars, according to the Department of Economic Development and Commerce. Real GNP, which counts only income that stays on the island, was <b>$69.9 billion</b>. The gap of more than $30 billion is mostly the profits of multinational manufacturers, chiefly pharmaceutical and medical-device makers, that are booked in Puerto Rico but paid out abroad. For residents, GNP is the better measure of living standards.',
               'The Planning Board and other forecasters expect growth below 1% for fiscal 2026.')
         + sec('Jobs: the bright spot',
               f'Unemployment averaged about 5.6% in 2025, the lowest on record, and is {V("PR_UNRATE")} now. Payroll employment averaged about 963,000 jobs in 2025, up 0.9%; over the latest twelve months the change is {V("PR_JOBS_YOY")}. The weakness is participation: only about 45% of adults are working or looking for work, against roughly 62% on the mainland, so many adults sit outside the labor market.')
         + chart('Unemployment: Puerto Rico and the U.S.', 'Monthly unemployment rate, five years.', [['PR_UNRATE', 'acc', 2], ['UNRATE', 't2', 1.4]], dp=0)
         + sec('Structural forces',
               '<b>Population:</b> about 3.2 million and roughly flat in 2024 after years of decline, which limits the workforce. <b>Federal money:</b> recovery and mitigation funds after Hurricanes Irma and Mar&iacute;a, projected at about $69 billion, are still being spent on the grid, water, housing and roads. <b>Energy:</b> power is expensive and unreliable, and the electric utility PREPA&rsquo;s debt has been in court-supervised restructuring since 2017. <b>Manufacturing:</b> about 83,000 jobs, 9% of the total, with pharma reshoring the main growth hope.')
         + sec('The tax picture for investors',
               'Residents generally do not pay federal income tax on Puerto Rico-source income; they pay Puerto Rico income tax instead. Act 60 offers decrees with reduced rates to new resident investors, exporters of services and manufacturers. The island&rsquo;s government bonds, restructured in 2022 under the PROMESA process, are exempt from federal, state and local income tax for most U.S. holders.')
         + key('Puerto Rico is a slow-growth economy with a tight job market. Its outcomes depend on how well federal funds are spent and whether the power grid gets fixed.')
         + src([('DDEC economic report, 2025', 'https://docs.pr.gov/files/DDEC/DEDC%20PUERTO%20RICO%20DATA%20CENTER/Puerto%20Rico%20Economic%20Analysis/DEDC%20Puerto%20Rico%20Economic%20Report%20-%20End%20of%20Year%202025.pdf'), ('2026 outlook', 'https://newsismybusiness.com/puerto-ricos-2026-outlook-modest-growth-high-stakes/'), ('FRED: Puerto Rico unemployment', FRED('PRUR'))])),
    dict(slug='note-pr-latam', code='MAC-04', cat='mac', label='Macro', date='October 22, 2026',
         foot='Figures are from the IMF World Economic Outlook, October 2026, pulled on October 22, 2026; 2026 and 2027 are IMF forecasts.', title='Puerto Rico and <em>Latin America</em>',
         name='Puerto Rico and Latin America', card='Size, income, growth, inflation and debt against Chile, Mexico, Brazil, Colombia, Peru, Argentina and El Salvador, all in dollars.',
         sub='Puerto Rico shares a language and much of its history with Latin America, but it uses the U.S. dollar and sits inside the U.S. economy. Put side by side in dollars, it is the richest economy in the region per person and one of the slowest-growing. This note uses the IMF&rsquo;s October 2026 figures for every country.',
         body=lambda: LA.table()
         + sec('How the comparison works',
               'Every figure comes from the IMF&rsquo;s World Economic Outlook, which converts each country&rsquo;s GDP into U.S. dollars at the average market exchange rate for the year. Puerto Rico needs no conversion: its economy runs on dollars. That matters more than it looks. The IMF expects Colombia&rsquo;s GDP to rise from $457 billion to $573 billion in dollars this year, a 25% jump, while its real economy grows only about 2.2%. Most of the difference is a stronger peso and local inflation. Dollar figures for the rest of the region swing with their currencies; Puerto Rico&rsquo;s do not.',
               'The second measure, <b>purchasing-power parity</b> (PPP), corrects for the fact that a dollar buys more in Lima or Bogot&aacute; than in San Juan. It is the better guide to living standards; market dollars are the better guide to what an economy is worth to a foreign investor.')
         + sec('Size: about the Dominican Republic',
               'Puerto Rico&rsquo;s GDP was <b>$129 billion</b> in 2025. That is a fraction of Brazil ($2.28 trillion) and Mexico ($1.84 trillion), about a third of Chile ($357 billion) or Peru ($342 billion), and almost exactly the size of the Dominican Republic ($128 billion). On the IMF&rsquo;s forecasts the Dominican Republic overtakes it this year, at $145 billion against $133 billion.')
         + LA.per_person()
         + sec('Income: well ahead, with a caveat',
               'At <b>$40,620</b> of GDP per person, Puerto Rico is far ahead of every country here: 1.7 times Uruguay, 2.3 times Chile, 3.8 times Brazil and 4.7 times Colombia. It is still under half the U.S. figure of $90,267.',
               'Two things narrow the gap. First, part of Puerto Rico&rsquo;s GDP is the profit of multinational drug and medical-device makers that is booked on the island and paid out abroad. Real GNP, which leaves that out, was about 67% of real GDP in fiscal 2025. Applied to the dollar figure, that suggests roughly <b>$27,000</b> per person, still the highest in the group but much closer to Uruguay&rsquo;s $24,549. Second, prices are higher in Puerto Rico. On a purchasing-power basis it is about $52,000 per person against $36,000 for Chile and $44,000 for Panama, so the lead shrinks from 2.3 times Chile to about 1.5 times.')
         + LA.trend()
         + LA.growth()
         + sec('Growth: the weakest in the group',
               'From 2019 to 2026, including the IMF&rsquo;s forecast for this year, Puerto Rico&rsquo;s real GDP grows about <b>3%</b> in total. Costa Rica, Panama and the Dominican Republic grow more than 25%, Colombia 18%, Brazil 16%, and Chile and Peru 14%. Even Mexico (7%) and Argentina (9%), both weak, do better. The IMF puts Puerto Rico&rsquo;s growth at &minus;0.1% for 2026 and 1.0% for 2027.',
               'Part of the gap is people. Puerto Rico&rsquo;s population fell about 10% between 2015 and 2025, to 3.2 million, while Colombia&rsquo;s and Peru&rsquo;s grew about 15%. Output per person has held up better than the headline: dollar GDP per person rose about 39% from 2015 to 2025, more than Chile (32%), the same as Mexico, and less than Uruguay (46%).')
         + sec('El Salvador: a pickup from a low base',
               'El Salvador is the closest parallel to Puerto Rico in one respect: it has used the U.S. dollar since 2001. Its economy has picked up under President Nayib Bukele. Growth averaged about 2.4% a year in the five years before the pandemic; it was <b>3.9% in 2025</b>, and the IMF expects <b>4.5% in 2026</b>, the third-fastest in this table after Panama and the Dominican Republic. The IMF credits stronger consumption and investment, strong remittances, tourism and construction, and a much better security picture after the government&rsquo;s crackdown on gangs, which human-rights groups have criticized for mass detentions under a state of exception.',
               'From 2022 to 2026 its real GDP grows about 18%, ahead of Brazil, Colombia and Mexico. But it starts from far behind: GDP per person is about <b>$5,750</b>, the lowest here and one-seventh of Puerto Rico&rsquo;s, and government debt is high at about 88% of GDP. It is in a 40-month, $1.4 billion IMF program agreed in late 2024, which led it to make bitcoin acceptance voluntary in January 2025. Unemployment of about 4.2% and inflation of 0.3% in 2025 show what the dollar brings; the debt and the low income level show what it does not.')
         + sec('Inflation and money: the dollar&rsquo;s advantage',
               'Because it uses the dollar and the Federal Reserve sets its interest rates, Puerto Rico imports U.S. inflation. Prices rose <b>1.5%</b> in 2025, against 3.8% in Mexico, 4.2% in Chile, 5.0% in Brazil and 5.1% in Colombia. Argentina has brought inflation down from 220% in 2024 to 42% in 2025, and the IMF expects 32.5% this year. Peru matched Puerto Rico at 1.5%. The trade-off is that Puerto Rico has no exchange rate or central bank of its own to cushion a downturn.')
         + sec('Jobs and debt',
               'Puerto Rico&rsquo;s unemployment rate of about 5.6% in 2025 is lower than Chile (8.5%), Colombia (8.0%) and Argentina (7.4%), and close to Brazil (6.0%) and Peru (5.9%). Mexico reports 2.6%, partly because many workers are in informal jobs. Puerto Rico&rsquo;s weakness is participation: only about 45% of adults work or look for work, so the jobless rate flatters it.',
               'On debt, the IMF puts Puerto Rico&rsquo;s government at <b>18% of GDP</b>, the lowest here, against 93% for Brazil, 80% for Argentina, 62% for Mexico and 60% for Colombia. That low figure reflects the 2022 restructuring under PROMESA, which cut the central government&rsquo;s bonded debt sharply. It does not include the power utility PREPA, whose debt is still being restructured, or unfunded pension promises, and the island&rsquo;s budget remains under a federal oversight board.')
         + key('Puerto Rico is richer and more stable than any economy in Latin America, measured in dollars, but it barely grows and its population is shrinking. Its neighbors offer growth and higher interest rates, with currency risk attached; Puerto Rico offers the dollar and slow growth.')
         + src([('IMF DataMapper: GDP per person', 'https://www.imf.org/external/datamapper/NGDPDPC@WEO/PRI/CHL/ARG/MEX/BRA/COL/PER'), ('IMF World Economic Outlook, October 2026', 'https://www.imf.org/en/Publications/WEO'), ('IMF regional forecasts (MercoPress)', 'https://en.mercopress.com/2026/10/13/imf-trims-latin-america-s-outlook-to-2.3-and-sharply-cuts-argentina-s'), ('IMF review of El Salvador (Tico Times)', 'https://ticotimes.net/2026/09/04/imf-el-salvador-loan-bitcoin-reforms'), ('DDEC economic report, 2025', 'https://docs.pr.gov/files/DDEC/DEDC%20PUERTO%20RICO%20DATA%20CENTER/Puerto%20Rico%20Economic%20Analysis/DEDC%20Puerto%20Rico%20Economic%20Report%20-%20End%20of%20Year%202025.pdf')])),
]


def body(n):
    return f'''<header class="ph rp">
  <div class="wrap">
    <div class="eyebrow mono"><a href="research.html">Research</a>&nbsp;/&nbsp;{n['label']} &middot; {n['code']} &middot; {n.get('date', DATE)}<span class="kind" title="Written by Luis Diaz Busquets; the charts update with each data run">Analyst note</span></div>
    <h1>{n['title']}</h1>
    <p class="sub">{n['sub']}</p>
  </div>
</header>
<section class="tight rbody">
  <div class="wrap"><article class="note">{n['body']()}
  <p class="fine" style="margin-top:34px">{n.get('foot', f'Figures in copper come straight from FRED and update every weekday; other figures are as of {DATE}.')} For education only, not investment advice.</p></article></div>
</section>
'''
