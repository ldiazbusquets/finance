"""Research reports on the author's holdings, written October 20, 2026.

Valuation numbers come from the analyst's own model (10-year free cash flow, or excess return for the bank,
or dividends for the utility), with a 5.15% 10-year Treasury and a 4.5% equity risk premium throughout.
"""
from rep import src, stats, table, prose, key, fin_table, bridge

DATE = 'October 20, 2026'
LATER = ', before its third-quarter results later this month'


def scen(rows, lab=('Bear', 'Base', 'Bull')):
    return table([''] + list(lab), rows, 'allnum')


def sens(label, cols, vals):
    return '<h3 class="sec sm">Sensitivity to the discount rate</h3>' + table([label] + cols, [['Value per share'] + vals], 'allnum')


def implied(rows):
    return table(['To reach today&rsquo;s price, you need', 'Instead of'], rows)


TOC = [('overview', 'The business'), ('results', 'Latest results'), ('fin', 'Five years'), ('capital', 'Balance sheet'),
       ('value', 'Valuation'), ('implied', 'What the price assumes'), ('risks', 'Risks'), ('rec', 'Rating')]

R = {}

# ---------------------------------------------------------------- NVIDIA
NV = 'https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027'
R['NVDA'] = dict(
    t='NVDA', slug='nvidia', name='Nvidia', h1='Nvidia', sector='Semiconductors', date=DATE, timing=', before its fiscal third-quarter results in November',
    sub='Nvidia sells the chips, networking and software that nearly every large AI model is trained and run on. Revenue doubled again this year and margins sit at 75%. The question is not the business but how long this level of spending lasts, and the price already assumes it lasts a long time.',
    call='Hold', method='Cash-flow model', price=216.47, base=166, bear=82, bull=306, wt=180, max=400, tick=50,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 82, 306, 166, '$82 to $306, base $166'), ('Probability-weighted', None, None, 180, '$180'),
           ('Price at writing', None, None, 216.47, '$216.47'), ('52-week range', 164, 243, None, '$164 to $243')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'The default supplier <em>of AI computing.</em>',
         prose('Nvidia designs graphics processors and the systems built around them: full racks of GPUs, CPUs and networking that data centers buy as one unit, plus CUDA, the software layer most AI developers write for. It does not own factories; TSMC makes its chips.',
               'Data centers are now almost the whole company: <b>$89.0 billion of $96.2 billion</b> in revenue last quarter. Its biggest customers are the cloud companies (Microsoft, Google, Amazon, Oracle, Meta) and a fast-growing group of specialist AI clouds. Several of those customers also design their own chips, which is the main long-run competitive threat alongside AMD.')
         + key('Takeaway', 'The lead rests on three things competitors have to match at once: the chip, the networking that ties thousands of them together, and the software developers already use.')
         + src([('Q2 FY2027 results', NV)])),
        ('results', 'Latest results', '$96 billion in a quarter, <em>up 106%.</em>',
         stats([('$96.2B', 'Revenue, Q2 FY2027'), ('+106%', 'Growth from a year earlier'), ('$89.0B', 'Data center revenue, +117%'), ('75.0%', 'Gross margin'), ('$108B', 'Q3 revenue guidance'), ('$26B', 'Returned to shareholders in Q2')])
         + prose('In the quarter to July, revenue rose 18% from the previous quarter and 106% from a year earlier. Operating income was $63.7 billion, about two-thirds of revenue. Management guided the next quarter to <b>$108 billion</b>, assuming no data-center sales to China, with gross margin of about 74%.',
                 'The product cycle is moving to Vera Rubin, which the company says is in full production and ramping at cloud partners. Nvidia also returned about $26 billion through buybacks and dividends in the quarter and has about $99 billion left under its buyback authorization.')
         + src([('Q2 FY2027 results', NV)])),
        ('fin', 'Five years', 'From $27 billion to $300 billion <em>in four years.</em>',
         fin_table('NVDA') + prose('Revenue was flat in fiscal 2023, then took off with ChatGPT. Margins rose with it: operating margin went from 16% to above 60%, because each new chip generation sold at a higher price than it cost to make. Free cash flow follows profit closely; the business needs little capital because TSMC builds the factories.')
         + src([('Nvidia filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=10-K')])),
        ('capital', 'Balance sheet', 'Plenty of cash, <em>returned through buybacks.</em>',
         prose('Debt is small next to a $5 trillion market value, and cash and investments roughly cover it, so the model ignores net debt. Almost all cash returns come through buybacks; the dividend is token. The bigger balance-sheet items are supply commitments: Nvidia pre-pays and commits to suppliers to secure chip and memory capacity, which would become a burden if demand fell quickly.')
         + key('Read', 'No financial risk; the exposure is operational, through supply commitments made in a boom.')),
        ('value', 'Valuation', 'The model gives <em>$166 a share.</em>',
         prose('The base year is fiscal 2027 (to January 2027), estimated at <b>$404 billion</b> from the first two quarters, guidance and a modest fourth quarter. The model then assumes another strong year and a long fade.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, FY2027', '$404B', 'Two reported quarters, Q3 guidance, a higher Q4'],
             ['Growth, next two years', '40%, then 15%', 'The Rubin cycle, then normalising spending'],
             ['Growth after that', 'Fades to 3% by year 10', 'AI spending matures'],
             ['Operating margin', '63% falling to 55% by year 7', 'Competition and custom chips take some pricing'],
             ['Tax rate', '17%', 'Company guidance of 16&ndash;18%'],
             ['Reinvestment', '$1 for every $2.50 of new revenue', 'Inventory, supply prepayments and capital'],
             ['Discount rate', '12.3%', '5.15% Treasury, beta 1.58, 4.5% premium; almost no debt'],
             ['Terminal growth', '3.0%', 'With a 25% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$2.22T'), ('PV of terminal value', '$1.82T'), ('Enterprise value', '$4.04T'), ('Net cash', '&asymp; $0'), ('Equity value', '$4.04T'), ('Shares', '24.3B')], '$166')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, next two years', '20% / 5%', '40% / 15%', '55% / 25%'], ['Long-run operating margin', '45%', '55%', '60%'],
             ['Discount rate', '13.3%', '12.3%', '11.3%'], ['Value per share', '$82', '$166', '$306'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25, the cases give <b>$180</b>.')
         + sens('Discount rate', ['9.0%', '10.0%', '11.0%', '12.3%'], ['$258', '$221', '$193', '$166'])
         + key('Read', 'The discount rate decides this one. At 10%, a common choice for a company this size, the price is about fair; at the 12.3% that Nvidia&rsquo;s beta implies, it is not.')),
        ('implied', 'What the price assumes', 'At $216, the market prices in <em>a longer boom.</em>',
         implied([['Revenue growth of about 84% next year, then 15%', '40%, then 15%'], ['A long-run operating margin near 73%', '55%'], ['A discount rate of about 10.1%', '12.3%']])
         + prose('None of these is impossible for Nvidia; each has been beaten before. But the price needs the AI build-out to keep growing well past 2027 without customers&rsquo; own chips taking meaningful share.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Customer spending slows', 'A handful of cloud companies buy most of the output. If their returns on AI disappoint, orders can fall quickly.'],
             ['Custom chips', 'Google, Amazon, Microsoft and Meta all design their own accelerators and would rather not pay Nvidia&rsquo;s margins.'],
             ['China and export rules', 'Guidance assumes no data-center sales to China; policy can move either way.'],
             ['Supply chain', 'Dependence on TSMC and on memory supply; a disruption in Taiwan is the tail risk.'],
         ]) + prose('<b>Upside:</b> AI moving from training into everyday use (inference), robotics and sovereign AI could extend the cycle further than the model allows.')),
        ('rec', 'Rating', 'Hold. <em>Fair at a 10% discount rate, rich at 12%.</em>',
         prose('At $216.47 against a base case of $166 ($180 weighted), Nvidia trades above what the model supports at its own cost of capital, but within reach of it at a lower rate. The business is in its strongest position ever. The call is <b>Hold</b>: keep the position, add only on a pullback toward the base case.',
               '<b>What would change the view:</b> next-year guidance that points to growth well above 40% would move it toward Buy; signs that cloud spending is peaking would move it toward Sell. Watch fiscal third-quarter results in November against the $108 billion guidance.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>The best business in tech, <em>priced like it.</em></h2><p>Nvidia earns more than almost any company in history; the price already counts on that continuing.</p></div>'),
    ])

# ---------------------------------------------------------------- Amazon
AM = 'https://www.sec.gov/Archives/edgar/data/0001018724/000101872426000038/amzn-20260930xex991.htm'
AM_CALL = 'https://finance.yahoo.com/markets/stocks/articles/amazon-com-q3-earnings-call-001416198.html'
AM_RX = 'https://www.forbes.com/sites/fionariley/2026/10/29/amazon-falls-short-of-overall-revenue-prediction-despite-aws-revenue-growth-nearing-40/'
R['AMZN'] = dict(
    t='AMZN', slug='amazon', name='Amazon', h1='Amazon', sector='Consumer &amp; cloud', date='October 30, 2026', timing=', the morning after its third-quarter results',
    sub='Amazon is three businesses in one: the largest online store, the largest cloud (AWS) and a fast-growing advertising arm. AWS growth sped up to 39% in the third quarter, its fastest in almost five years, but Amazon said spending will rise again in 2027 from about $220 billion this year, and it now borrows to pay for it. The price still assumes that spending pays off handsomely.',
    call='Hold', method='Cash-flow model', price=243.79, pricenote='Close, October 29, 2026, before the results', base=155, bear=66, bull=279, wt=164, max=400, tick=50,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 66, 279, 155, '$66 to $279, base $155'), ('Probability-weighted', None, None, 164, '$164'),
           ('Price at writing', None, None, 243.79, '$243.79'), ('52-week range', 196, 287, None, '$196 to $287')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'A store, a cloud <em>and an ad network.</em>',
         prose('Amazon reports three segments. <b>North America</b> and <b>International</b> are the store: first-party retail, third-party seller services, Prime subscriptions and advertising. <b>AWS</b> rents computing, storage and AI infrastructure to companies and governments.',
               'Most of the profit comes from AWS and advertising, which ride on the store&rsquo;s traffic. Retail itself earns thin margins but funds the logistics network that keeps customers loyal. Amazon also owns a large stake in Anthropic, the AI company, which it does not value in its operating results.')
         + key('Takeaway', 'Value comes mostly from AWS and ads; the store is the moat that feeds them.')),
        ('results', 'Latest results', 'AWS is growing 39% <em>on a $184 billion pace.</em>',
         stats([('$201.9B', 'Revenue, Q3 2026, +12%'), ('+39%', 'AWS growth'), ('$28.1B', 'Operating income, +61%'), ('39%', 'AWS operating margin'), ('$578B', 'AWS backlog'), ('&minus;$42.4B', 'Free cash flow, last 12 months, as Amazon defines it')])
         + prose('Third-quarter revenue rose 12% to $201.9 billion, slightly below the $202.3 billion analysts expected; moving Prime Day into the second quarter took about four points off growth. AWS revenue grew 39% to $46.0 billion with $17.8 billion of operating income, and its backlog reached $578 billion. Operating income of $28.1 billion, a record 13.9% margin, beat the $22.5&ndash;26.5 billion guidance; North America earned 7.7% on sales and International 3.7%. Advertising grew 11% to $19.6 billion. EPS of $1.89 was below the $1.96 expected.',
                 'The cost is in cash flow: free cash flow over the last twelve months was <b>negative $42.4 billion</b> as Amazon defines it, because capital spending (net of proceeds) rose 82% in a year, to $211 billion. Capital spending is still guided to about $220 billion for 2026, and management said it will &ldquo;rise meaningfully&rdquo; in 2027. Long-term debt has risen to $173 billion from $66 billion at the end of 2025. Guidance for the fourth quarter is $240&ndash;247 billion of revenue and $28.5&ndash;33.5 billion of operating income. The shares, which closed at $243.79 before the report, fell about 6% in after-hours trading.')
         + src([('Q3 2026 results, Amazon', AM), ('Earnings call highlights', AM_CALL), ('Market reaction', AM_RX)])),
        ('fin', 'Five years', 'Margins tripled; <em>cash flow went the other way.</em>',
         fin_table('AMZN') + prose('Operating margin rose from 2% in 2022 to about 12% as AWS and ads grew faster than retail. Net income in the last twelve months includes the Anthropic gains. Capital spending has more than doubled since 2024, so free cash flow has fallen even as profit rose.')
         + src([('Amazon filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K')])),
        ('capital', 'Balance sheet', 'Strong, <em>but now borrowing to build.</em>',
         prose('Amazon held about $114 billion of cash and marketable securities at the end of September against $173 billion of long-term debt, so net debt is now about $59 billion, up from roughly $10 billion in June. It pays no dividend and buys back little; every spare dollar goes into data centers, chips (Trainium) and the Leo satellite network. The Anthropic stake is a sizeable asset that is <b>not</b> included in this valuation, so it is upside to the numbers below; Anthropic&rsquo;s planned IPO would give it a market price.')
         + src([('Q3 2026 results, Amazon', AM)])),
        ('value', 'Valuation', 'The model gives <em>$155 a share.</em>',
         prose('This update raises 2026 revenue to $828 billion and growth by a point a year, because AWS is growing faster with a larger backlog, and raises the investment path because 2027 spending will be higher. More net debt comes off the value. The changes roughly cancel out.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, 2026', '$828B', 'Three quarters plus the Q4 guidance midpoint'],
             ['Growth, 2027 and 2028', '13%, then 12%', 'AWS near 30% on its backlog, retail mid-to-high single digits'],
             ['Growth after that', 'Fades to 3% by year 10', 'A straight glide to long-run economic growth'],
             ['Operating margin', '13% rising to 18% by 2031', 'More AWS and advertising in the mix'],
             ['Net investment', '$170B, $130B, $90B, $60B, then $1 per $2 of new revenue', 'Spending rises in 2027, then the build peaks and normalises'],
             ['Tax rate', '19%', 'Below the 21% federal rate after credits'],
             ['Discount rate', '10.7%', 'Beta 1.33, 4.5% premium, about 6% debt'],
             ['Terminal growth', '3.0%', 'With a 20% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$623B'), ('PV of terminal value', '$1.13T'), ('Enterprise value', '$1.75T'), ('Less net debt', '$59B'), ('Equity value', '$1.69T'), ('Shares', '10.9B')], '$155')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '8% / 7%', '13% / 12%', '16% / 15%'], ['Long-run operating margin', '14%', '18%', '22%'],
             ['Discount rate', '11.7%', '10.7%', '9.7%'], ['Value per share', '$66', '$155', '$279'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$164</b>, up from $162.') + sens('Discount rate', ['8.5%', '9.0%', '9.5%', '10.0%'], ['$236', '$212', '$192', '$175'])),
        ('implied', 'What the price assumes', 'At $244, the build-out <em>has to earn a lot.</em>',
         implied([['A long-run operating margin near 26%', '18%; Amazon&rsquo;s best quarter so far was 13.9%'], ['Revenue growth of about 22% a year for two years', '13% and 12%'], ['A discount rate of about 8.3%', '10.7%']])
         + prose('The market is betting that the $220 billion a year going into AI infrastructure, and more in 2027, earns AWS-like returns. The Anthropic stake, left out of the model, covers part of the gap.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['AI returns', 'If AI demand cools, Amazon is left with expensive capacity and falling AWS margins.'],
             ['Cash flow and debt', 'Free cash flow is deeply negative and debt has more than doubled this year, leaving less room for error.'],
             ['Regulation', 'The U.S. antitrust case against the store, and scrutiny of AWS in Europe.'],
             ['Consumer slowdown', 'Retail and ads both depend on spending; advertising growth slowed to 11%.'],
         ]) + prose('<b>Upside:</b> the $578 billion AWS backlog, Trainium chips cutting AWS costs and selling outside AWS from late 2027, Leo satellite internet starting service, and the value of the Anthropic stake.')),
        ('rec', 'Rating', 'A great company <em>in an expensive building phase.</em>',
         prose('At $243.79 against a base case of $155 ($164 weighted), the shares still price in much higher long-run margins than Amazon has ever earned, even after the drop. AWS is the strongest it has been in years; the question is what the spending earns, and the answer keeps being deferred as the bill rises.',
               '<b>Watch in the fourth-quarter report:</b> the 2027 capital spending figure, AWS growth staying near 40%, and operating income against the $28.5&ndash;33.5 billion guide.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Own the platform, <em>wait for the cash.</em></h2><p>The spending is a bet on AI that only pays off if AWS keeps its margins as it grows.</p></div>'),
    ])

# ---------------------------------------------------------------- Meta
ME = 'https://www.stocktitan.net/news/META/meta-reports-second-quarter-2026-hkjfhayj8l0v.html'
ME3 = 'https://www.sec.gov/Archives/edgar/data/0001326801/000162828026066700/meta-09302026xexhibit991.htm'
R['META'] = dict(
    t='META', slug='meta', name='Meta Platforms', h1='Meta <em>Platforms</em>', sector='Communication services', date='October 22, 2026', timing=', the day after its third-quarter results',
    sub='Meta owns Facebook, Instagram, WhatsApp and Messenger, used by 3.6 billion people a day, and sells the ads in between. AI has made those ads work better and revenue is growing 26%. But Meta is spending so heavily on AI data centers that free cash flow turned negative last quarter.',
    call='Hold', method='Cash-flow model', price=697.52, base=531, bear=223, bull=918, wt=551, max=1000, tick=100,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 223, 918, 531, '$223 to $918, base $531'), ('Probability-weighted', None, None, 551, '$551'),
           ('Price at writing', None, None, 697.52, '$697.52'), ('52-week range', 520, 780, None, '$520 to $780')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Three billion people <em>and an ad auction.</em>',
         prose('Meta earns nearly all its money from advertising on its Family of Apps. AI ranks what each person sees and which ads they are shown, and tools like Advantage+ let advertisers hand the whole campaign to Meta&rsquo;s systems. Reality Labs, the headset and smart-glasses unit, loses about $4&ndash;5 billion a quarter.',
               'The strategic bet is on building its own frontier AI models and the computing to run them, both to improve ads and to create new products such as Meta AI.')
         + key('Takeaway', 'The ad machine is stronger than ever; the debate is about how much it costs to keep it ahead.')),
        ('results', 'Latest results', 'Revenue up 26%, <em>a $9.9 billion legal bill.</em>',
         stats([('$64.6B', 'Revenue, Q3 2026, +26%'), ('3.64B', 'Daily active people, +3%'), ('+10% / +14%', 'Ad impressions / price per ad'), ('20%', 'Operating margin, from 40%'), ('&minus;$2.1B', 'Free cash flow'), ('$73&ndash;76B', 'Q4 revenue guidance')])
         + prose('Revenue grew 26% to $64.6 billion, about $1.2 billion more than analysts expected, with more ads and a 14% rise in the price per ad. Costs grew 68%, mostly because of a $9.89 billion charge for the settlement with state attorneys general over teen mental health, part of an agreement to pay up to about $18.6 billion. Operating income fell 37% to $13.0 billion; without the charge it would have been about $22.9 billion, a 35% margin. EPS was $3.83, or about $7.40 without the charge.',
                 'Capital spending of $34.9 billion was more than the $32.8 billion of operating cash flow, so free cash flow was negative $2.1 billion. Meta again bought back no stock. Guidance: fourth-quarter revenue of $73&ndash;76 billion, 2026 expenses raised to $175&ndash;179 billion to include the charge, and capex narrowed to $135&ndash;145 billion. There is no 2027 capex figure yet, but management expects strong revenue growth throughout 2027, continued heavy AI investment and Reality Labs losses near $15 billion. Meta also announced a stock dividend of one new non-voting Class C share per share held, in effect a 2-for-1 split. The charter change that allows it takes effect on January 19, 2027; the record and payment dates are still to be set. The shares closed at $697.52 before the report and rose about 4% after hours.')
         + src([('Q3 2026 results', ME3), ('Market reaction', 'https://www.investing.com/news/company-news/meta-q3-2026-slides-revenue-surges-26-as-margins-compress-sharply-93CH-4964286'), ('Stock split', 'https://www.tradingkey.com/analysis/stocks/us-stocks/262231250-meta-stock-split-better-expected-earnings-tradingkey')])),
        ('fin', 'Five years', 'Back to growth, <em>then into a spending wave.</em>',
         fin_table('META') + prose('2022 was the low point: revenue fell and Reality Labs spending peaked. The &ldquo;year of efficiency&rdquo; in 2023 restored margins above 40%. Capital spending has more than doubled since 2024, and free cash flow has fallen accordingly.')
         + src([('Meta filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=10-K')])),
        ('capital', 'Balance sheet', 'From net cash <em>to borrowing.</em>',
         prose('Meta had $82.5 billion of cash and securities against $80.9 billion of long-term debt at the end of September, so it is roughly net cash neutral after years of large net cash. Buybacks have stopped for now; the $2.10 annual dividend continues. The youth-safety settlement removes part of the legal risk management had warned about, but the cash has still to be paid and other cases remain open.')),
        ('value', 'Valuation', 'The model gives <em>$531 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, 2026', '$256B', 'First nine months plus Q4 guidance'],
             ['Growth, 2027 and 2028', '18%, then 14%', 'AI-improved ads, slowing from 28%'],
             ['Operating margin', '34% rising to 38% by 2031', 'Excluding the one-off legal charge; depreciation from the build-out holds it below past highs'],
             ['Net investment', '$110B, $90B, $60B, $40B, then $1 per $2 of new revenue', 'Spending peaks in 2027'],
             ['Tax rate', '16%', 'Guidance of 15&ndash;17%'],
             ['Discount rate', '11.2%', 'Beta 1.42, 4.5% premium'],
             ['Terminal growth', '3.0%', 'With a 25% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$560B'), ('PV of terminal value', '$804B'), ('Enterprise value', '$1.37T'), ('Plus net cash', '$2B'), ('Equity value', '$1.37T'), ('Shares', '2.57B')], '$531')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '10% / 8%', '18% / 14%', '24% / 18%'], ['Long-run operating margin', '30%', '38%', '44%'],
             ['Discount rate', '12.2%', '11.2%', '10.2%'], ['Value per share', '$223', '$531', '$918'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$551</b>. The value rose from $516 because 2026 revenue is now expected to be about $8 billion higher; spending plans are unchanged.') + sens('Discount rate', ['8.5%', '9.0%', '9.5%', '10.0%'], ['$845', '$766', '$698', '$641'])),
        ('implied', 'What the price assumes', 'At $697, margins <em>back near 50%.</em>',
         implied([['A long-run operating margin near 50%', '38%; Meta&rsquo;s peak was in the low 40s'], ['Revenue growth of about 21% a year for two years', '18% and 14%'], ['A discount rate of about 9.5%', '11.2%']])
         + prose('Meta is closer to fair value than Amazon or Vertiv: a slightly lower discount rate or slightly faster growth closes most of the gap.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['AI spending without return', 'Capex of $130&ndash;145 billion a year has to lift revenue or it simply lowers margins.'],
             ['Legal', 'After the $9.9 billion settlement, other youth-safety cases, EU regulation and antitrust can still cost money and limit ad targeting.'],
             ['Reality Labs', 'Losses of $18&ndash;19 billion this year and about $15 billion in 2027, with no clear payoff date.'],
             ['Ad cycle', 'Advertising is the first budget cut in a slowdown.'],
         ]) + prose('<b>Upside:</b> WhatsApp business messaging, AI agents that sell for advertisers, and spending easing after 2027 would lift free cash flow quickly.')),
        ('rec', 'Rating', 'Hold. <em>Strong ads, heavy bills.</em>',
         prose('At $697.52 against a base case of $531 ($551 weighted), Meta trades above the model at an 11% discount rate but close to fair at 9.5%. The quarter was better than feared: ads grew faster than expected and the legal charge is a one-off. But free cash flow is now negative and there is still no limit on 2027 spending. The call stays <b>Hold</b>. A move toward the mid $500s, or evidence that 2027 spending will fall, would make it a Buy.',
               '<b>Watch in the fourth-quarter report:</b> revenue against $73&ndash;76 billion, the first 2027 capex guidance, when the settlement is paid, and whether buybacks resume.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>The ad machine works. <em>The AI bill is the question.</em></h2><p>Meta can afford the spending; the price needs it to pay off.</p></div>'),
    ])

# ---------------------------------------------------------------- JPMorgan
JP = 'https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/quarterly-earnings/2026/3rd-quarter/6c1f8114-1be4-4174-8292-f75bbb59bc21.pdf'
R['JPM'] = dict(
    t='JPM', slug='jpmorgan', name='JPMorgan Chase', h1='JPMorgan <em>Chase</em>', sector='Banks', date=DATE, timing=', a week after its third-quarter results on October 13',
    sub='JPMorgan is the largest U.S. bank and the most profitable of the big ones, earning about 20% on tangible equity. The question for a bank is what return on equity it can sustain and what multiple of book value that justifies. At 2.5 times book, the market already assumes today&rsquo;s exceptional returns last.',
    call='Hold', method='Excess-return model', price=335.26, base=284, bear=226, bull=368, wt=290, max=500, tick=50,
    fieldnote='The excess-return model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Excess-return model', 226, 368, 284, '$226 to $368, base $284'), ('Probability-weighted', None, None, 290, '$290'),
           ('Price at writing', None, None, 335.26, '$335.26'), ('52-week range', 279, 367, None, '$279 to $367')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Four businesses, <em>one balance sheet.</em>',
         prose('JPMorgan runs Consumer &amp; Community Banking (Chase branches, cards, mortgages), the Commercial &amp; Investment Bank (lending, investment banking, trading, payments), and Asset &amp; Wealth Management. Deposits are its raw material: cheap, sticky funding it lends and invests at a spread.',
                 'Scale is the advantage. It spends more on technology than most competitors earn, and it is the default counterparty for large companies and governments.')
         + key('Takeaway', 'A bank is valued on what it earns on its equity, not on cash flow, because debt is its product.')),
        ('results', 'Latest results', '20% return on tangible equity, <em>again.</em>',
         stats([('$15.3B', 'Net income, Q3 2026'), ('$5.57', 'EPS ($5.75 ex securities losses)'), ('$50.9B', 'Revenue, +8%'), ('20%', 'Return on tangible equity'), ('13.9%', 'CET1 capital ratio'), ('$132.30', 'Book value per share')])
         + prose('Third-quarter net income was $15.3 billion. Net interest income rose 13% to $27.1 billion; markets revenue rose 15% to $10.3 billion, led by equities (+49%); investment banking fees rose 14%. Expenses grew 12%. Credit was steady: net charge-offs fell to $2.2 billion.',
                 'Management guided fourth-quarter NII to about $28 billion and gave a first 2027 view of about $107 billion excluding markets. Jamie Dimon said the bank has roughly $30 billion of excess capital and cut buybacks to $0.7 billion this quarter, preferring to lend it out at good returns.')
         + src([('Q3 2026 results', JP), ('Earnings call', 'https://www.tradingkey.com/news/transcripts/262214756-tradingkey')])),
        ('fin', 'Five years', 'Earnings up by half <em>since 2022.</em>',
         fin_table('JPM', bank=True) + prose('Revenue has risen about 50% since 2022, helped by higher interest rates and the First Republic acquisition in 2023. Return on equity has stayed in the high teens.')
         + src([('JPMorgan filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000019617&type=10-K')])),
        ('capital', 'Capital', 'More capital <em>than it needs.</em>',
         prose('CET1, the main regulatory capital measure, was 13.9%, comfortably above requirements. The bank paid $4.4 billion of dividends in the quarter ($1.65 a share). Tangible book value per share is $112.64, up 7% in a year; book value per share is $132.30.')),
        ('value', 'Valuation', 'The model gives <em>$284 a share.</em>',
         prose('The excess-return model values a bank by how far its return on equity beats its cost of equity: <b>justified price-to-book = (ROE &minus; g) &divide; (cost of equity &minus; g)</b>.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Sustainable return on equity', '16%', 'Between today&rsquo;s 17% and the 17% through-cycle ROTCE target (about 14.5% ROE)'],
             ['Long-run growth', '4.5%', 'Retained earnings growing the balance sheet'],
             ['Cost of equity', '9.9%', '5.15% Treasury, beta 1.05, 4.5% premium'],
             ['Book value per share', '$132.30', 'September 30, 2026'],
         ], 'mid')
         + bridge([('ROE &minus; growth', '11.5%'), ('Cost of equity &minus; growth', '5.4%'), ('Justified P/B', '2.15&times;'), ('Book value per share', '$132.30'), ('Today&rsquo;s P/B', '2.53&times;'), ('Implied ROE today', '18.1%')], '$284')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Return on equity', '14.5%', '16%', '18%'], ['Cost of equity', '10.4%', '9.9%', '9.4%'],
             ['Value per share', '$226', '$284', '$368'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$290</b>.') + sens('Cost of equity', ['9.0%', '9.5%', '10.0%'], ['$338', '$304', '$277'])),
        ('implied', 'What the price assumes', 'At $335, an 18% return <em>for good.</em>',
         implied([['A lasting return on equity of about 18%', '16%, and a 17% through-cycle ROTCE target'], ['A cost of equity near 9.0%', '9.9%']])
         + prose('That is achievable in good years, as 2026 shows, but it leaves no room for a credit cycle or lower rates.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Credit cycle', 'Card losses are at 3.2% and stable; a recession would raise them and require reserves.'],
             ['Lower rates', 'NII benefits from today&rsquo;s rates; cuts would squeeze it.'],
             ['Expenses', '2027 costs near $114 billion as the bank invests in technology and branches.'],
             ['Succession', 'Jamie Dimon&rsquo;s eventual departure.'],
         ]) + prose('<b>Upside:</b> lighter capital rules releasing the $30 billion of excess capital, and continued strength in markets and investment banking.')),
        ('rec', 'Rating', 'Hold. <em>The best bank, at a full price.</em>',
         prose('At $335.26 against a base case of $284 ($290 weighted), the shares need returns above the bank&rsquo;s own through-cycle target. The call is <b>Hold</b>; it would be a Buy below about 2.2 times book value, roughly $290.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Quality you pay for.</h2><p>JPMorgan earns more than its peers; the premium is already in the price.</p></div>'),
    ])

# ---------------------------------------------------------------- Vertiv
VR = 'https://www.prnewswire.com/news-releases/vertiv-reports-strong-third-quarter-2026-with-net-sales-growth-of-61-organic-orders-growth-over-100-and-diluted-eps-growth-of-91-adjusted-diluted-eps-growth-of-78-raises-full-year-2026-guidance-across-all-key-metrics-302921936.html'
VR_CALL = 'https://finance.biggo.com/news/US_VRT_2026-10-28'
VR_Q2 = 'https://www.nasdaq.com/press-release/vertiv-reports-strong-second-quarter-2026-diluted-eps-growth-53-adjusted-diluted-eps'
R['VRT'] = dict(
    t='VRT', slug='vertiv', name='Vertiv', h1='Vertiv', sector='Electrical equipment', date='October 29, 2026', timing=', the day after its third-quarter results',
    sub='Vertiv makes the power and cooling equipment inside data centers, from backup power to the liquid cooling that AI chips now need. After a second-quarter miss, the third quarter answered the doubts: sales up 61%, orders more than doubled and guidance raised again. The shares jumped 16% to $243, which still prices in far more growth than the model.',
    call='Sell', method='Cash-flow model', price=242.94, pricenote='Close, October 28, 2026', base=131, bear=72, bull=208, wt=136, max=400, tick=50,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 72, 208, 131, '$72 to $208, base $131'), ('Probability-weighted', None, None, 136, '$136'),
           ('Price at writing', None, None, 242.94, '$242.94'), ('52-week range', 148, 380, None, '$148 to $380')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Keeping AI chips <em>powered and cool.</em>',
         prose('Vertiv sells uninterruptible power supplies, switchgear and power distribution, thermal management (including liquid cooling for GPUs), and the service that keeps them running. Its customers are cloud companies, colocation operators and enterprises building data centers, now increasingly for AI.',
                 'As each rack of AI chips draws more power and generates more heat, the equipment Vertiv sells per megawatt rises. Its main competitors are Schneider Electric and Eaton.')),
        ('results', 'Latest results', 'Sales up 61%, <em>orders more than doubled.</em>',
         stats([('$4.31B', 'Sales, Q3 2026, +61%'), ('55%', 'Organic growth'), ('100%+', 'Organic order growth'), ('25.2%', 'Adjusted operating margin'), ('$14.45&ndash;14.85B', '2026 sales guidance, from $13.8&ndash;14.2B'), ('$7.10&ndash;7.20', '2026 adjusted EPS guidance, from $6.65&ndash;6.75')])
         + prose('Third-quarter sales rose 61% to $4.31 billion, 55% organically, and adjusted EPS rose 78% to $2.21, $0.41 above the company&rsquo;s own guidance. Management said $100&ndash;150 million of sales that slipped out of the second quarter were delivered in this one, so part of the beat is the earlier miss catching up. Organic orders more than doubled, though Vertiv gave only the growth rate and said it will stop disclosing order figures. Adjusted operating margin was 25.2%, and adjusted free cash flow $652 million.',
                 'Full-year guidance rose again: sales of $14.45&ndash;14.85 billion, 37&ndash;39% organic growth, a 24% adjusted operating margin, adjusted EPS of $7.10&ndash;7.20 and $2.6&ndash;2.8 billion of adjusted free cash flow. The fourth quarter is guided to about $4.4 billion of sales, up about 50% organically. Management would not give 2027 numbers but expects growth well above the market. The shares rose 16% on the day.')
         + src([('Q3 2026 results', VR), ('Earnings call summary', VR_CALL), ('Q2 2026 results', VR_Q2)])),
        ('fin', 'Five years', 'Sales doubled; <em>margins nearly tripled.</em>',
         fin_table('VRT') + prose('Operating margin rose from about 4% in 2022 to near 19% in the last twelve months, and free cash flow went from negative to over $2.9 billion.')
         + src([('Vertiv filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001674101&type=10-K')])),
        ('capital', 'Balance sheet', 'From leveraged <em>to net cash.</em>',
         prose('Vertiv was formed from a private-equity buyout and carried heavy debt. At the end of September it held $3.7 billion of cash and short-term investments against $2.9 billion of debt, about $0.8 billion of net cash, with $6.2 billion of liquidity. It keeps buying bolt-on businesses: in the quarter it announced UtilityInnovation Group (microgrids and power controls) and King Environmental Services (load testing in Europe).')
         + src([('Q3 2026 results', VR)])),
        ('value', 'Valuation', 'The model gives <em>$131 a share.</em>',
         prose('This update starts from the higher 2026 guidance and assumes faster growth in 2027: the fourth-quarter guidance alone is a run-rate of about $17.6 billion a year, 20% above 2026, and orders doubled. The margin path moves up half a point in line with the new guidance.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Sales, 2026', '$14.65B', 'Guidance midpoint'],
             ['Growth, 2027 and 2028', '30%, then 16%', 'Orders doubled and a fourth-quarter run-rate 20% above 2026, then slowing'],
             ['Operating margin', '23% rising to 25%', 'Adjusted margin less acquisition amortization'],
             ['Reinvestment', '$1 for every $3 of new sales', 'Factories, working capital and acquisitions to add capacity'],
             ['Discount rate', '13.1%', 'Beta 1.83, 4.5% premium'],
             ['Terminal growth', '3.0%', 'With a 25% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$27B'), ('PV of terminal value', '$23B'), ('Enterprise value', '$51B'), ('Plus net cash', '$0.8B'), ('Equity value', '$52B'), ('Shares', '393M')], '$131')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '15% / 8%', '30% / 16%', '40% / 22%'], ['Long-run operating margin', '21%', '25%', '27.5%'],
             ['Discount rate', '14.1%', '13.1%', '12.1%'], ['Value per share', '$72', '$131', '$208'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$136</b>.') + sens('Discount rate', ['9.0%', '10.0%', '11.0%', '12.0%'], ['$230', '$195', '$169', '$149'])
         + key('Read', 'Vertiv&rsquo;s beta of 1.83 gives it the highest discount rate of any holding. At 9%, the price is about fair.')),
        ('implied', 'What the price assumes', 'At $243, <em>36% growth for two years.</em>',
         implied([['Sales growth of about 36% a year in 2027 and 2028', '30% and 16%'], ['A long-run operating margin near 46%', '25%'], ['A discount rate of about 8.7%', '13.1%']])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Execution', 'The third quarter recovered the second-quarter shortfall; the fourth quarter has to deliver about 50% organic growth.'],
             ['Visibility', 'Vertiv now gives only the growth rate of orders and will stop disclosing them, so demand is harder to check.'],
             ['Data-center spending', 'Results depend on a small number of very large customers&rsquo; build plans.'],
             ['Competition', 'Schneider, Eaton and new liquid-cooling entrants are chasing the same projects.'],
         ]) + prose('<b>Upside:</b> orders that doubled point to 2027 growth above the base case, and 800-volt DC power products, due to start earning revenue in 2027, could raise content per data center.')),
        ('rec', 'Rating', 'A clean quarter, <em>a full price.</em>',
         prose('At $242.94 against a base case of $131 ($136 weighted), the shares price in growth and margins well above even this update&rsquo;s higher assumptions; the bull case ($208) is still below the price. The quarter removed the execution doubt, and the price rose by more than the value.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>The execution is back. <em>The price ran ahead of it.</em></h2><p>Demand is not the issue; the price already assumes it lasts.</p></div>'),
    ])

# ---------------------------------------------------------------- L3Harris
LH = 'https://www.sec.gov/Archives/edgar/data/0000202058/000020205826000084/exhibit991q3cy26earnings.htm'
LH_CALL = 'https://ca.investing.com/news/stock-market-news/earnings-call-transcript-l3harris-tops-q3-2026-estimates-and-lifts-guidance-93CH-4914955'
LH_SL = 'https://ca.investing.com/news/stock-market-news/l3harris-q3-2026-slides-record-backlog-drives-guidance-raise-93CH-4914984'
R['LHX'] = dict(
    t='LHX', slug='l3harris', name='L3Harris', h1='L3<em>Harris</em>', sector='Aerospace &amp; defense', date='October 30, 2026', timing=', the day after its third-quarter results',
    sub='L3Harris makes satellites, secure communications, sensors and, since buying Aerojet Rocketdyne, the rocket motors inside U.S. missiles. In the third quarter about $11 billion of missile awards tripled its orders and lifted the backlog to a record $53 billion, but it also cut its 2028 cash target from $3.5 billion to about $3 billion. The shares rose 7% to $278, still well below what the model gives.',
    call='Buy', method='Cash-flow model', price=278.43, pricenote='Close, October 29, 2026', base=402, bear=215, bull=626, wt=411, max=800, tick=100,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 215, 626, 402, '$215 to $626, base $402'), ('Probability-weighted', None, None, 411, '$411'),
           ('Price at writing', None, None, 278.43, '$278.43'), ('52-week range', 232, 379, None, '$232 to $379')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Space, communications <em>and missiles.</em>',
         prose('L3Harris has three segments. <b>Space &amp; Mission Systems</b> builds satellites, sensors and aircraft systems. <b>Communications &amp; Spectrum Dominance</b> makes tactical radios and electronic warfare equipment, its most profitable unit. <b>Missile Solutions</b> makes solid rocket motors and propulsion for interceptors such as THAAD and PAC-3, a bottleneck for U.S. munitions supply.',
                 'In January 2026 the Pentagon committed a $1 billion investment in Missile Solutions ahead of a planned IPO of that business; L3Harris has since pushed the IPO to mid-2027 at the earliest and says it will only go ahead at an attractive valuation.')),
        ('results', 'Latest results', 'Orders tripled, <em>a lower cash target.</em>',
         stats([('$6.07B', 'Revenue, Q3 2026, +7% (+9% organic)'), ('3.2&times;', 'Book-to-bill, on $19.3B of orders'), ('$53.2B', 'Record backlog, +47% in a year'), ('15.9%', 'Segment operating margin'), ('$23.5&ndash;23.7B', '2026 revenue guidance, raised'), ('~$3.0B', '2026 free cash flow guidance, unchanged')])
         + prose('Third-quarter revenue rose 7% to $6.07 billion, ahead of the $5.92 billion analysts expected, and EPS of $3.28 beat the $2.95 forecast. Orders of $19.3 billion, three times revenue, took the backlog to a record $53.2 billion; about $11 billion of that was PAC-3 and THAAD interceptor work. Missile Solutions grew 17% excluding a business it sold. Free cash flow was $1.26 billion in the quarter (the company no longer counts proceeds from asset sales), and 2026 EPS guidance was raised to $12.25&ndash;12.35.',
                 'The less welcome news was in the 2028 framework. Growth of about 8% a year was kept, but the segment margin target slipped to about 16% from 16.3% and free cash flow to &ldquo;$3 billion or more&rdquo; from $3.5 billion, because the company will pay its 401(k) contributions in cash rather than stock, expects slightly lower margins and is spending faster on missile capacity. The shares rose 7% on the day.')
         + src([('Q3 2026 results, L3Harris', LH), ('Earnings call', LH_CALL), ('2028 framework from the slides', LH_SL)])),
        ('fin', 'Five years', 'Steady growth, <em>rising cash.</em>',
         fin_table('LHX') + prose('Revenue jumped in 2023 with the Aerojet Rocketdyne purchase. Operating margin on a GAAP basis is held down by amortization of acquired intangibles; cash flow, which adds that back, is the better measure and has grown every year. The FY2025 revenue figure is from the company&rsquo;s release.')
         + src([('L3Harris filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000202058&type=10-K')])),
        ('capital', 'Balance sheet', 'Leveraged, <em>but deleveraging.</em>',
         prose('Debt was about $11.0 billion at the start of October against $3.0 billion of cash and short-term investments, mostly from the Aerojet deal; the company plans to repay $800 million in the fourth quarter. It also holds $987 million from the Pentagon&rsquo;s preferred-stock investment in Missile Solutions, which the model treats like debt. It pays a $1.25 quarterly dividend ($5.00 a year) and management called buybacks &ldquo;highly attractive&rdquo; at the current price.')
         + src([('Q3 2026 results, L3Harris', LH)])),
        ('value', 'Valuation', 'The model gives <em>$402 a share.</em>',
         prose('Because GAAP profit understates cash generation, this model works directly from free cash flow to the firm (free cash flow plus after-tax interest), following the company&rsquo;s own path to 2028. This update follows the lower 2028 cash target and lowers long-run cash flow from 14.6% to 13.5% of revenue: paying the 401(k) in cash and the lower margin are lasting, while the extra missile spending should fade. Lower net debt offsets part of the cut.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, 2026', '$23.6B', 'Guidance midpoint'],
             ['Growth, 2027 and 2028', '7.5% a year', 'About $27B by 2028, in line with the 8% organic framework'],
             ['Cash flow to the firm', '$3.40B, then $3.50B, then 13.5% of revenue', '$3B+ free cash flow plus after-tax interest'],
             ['Growth after 2028', 'Fades to 3% by year 10', 'A straight glide to long-run economic growth'],
             ['Discount rate', '8.0%', 'Beta 0.80 (defense peers; the measured 0.61 understates risk after this year), about 17% debt'],
             ['Terminal growth', '3.0%', 'In line with long-run economic growth'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$30.2B'), ('PV of terminal value', '$54.0B'), ('Enterprise value', '$84.3B'), ('Less net debt and preferred', '$9.0B'), ('Equity value', '$75.3B'), ('Shares', '187M')], '$402')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '4% / 3%', '7.5% / 7.5%', '10% / 9%'], ['Cash flow, share of revenue', '11.5%', '13.5%', '15%'],
             ['Discount rate', '9.0%', '8.0%', '7.0%'], ['Value per share', '$215', '$402', '$626'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$411</b>, down from $439 before the results.') + sens('Discount rate', ['7.0%', '7.5%', '8.0%', '8.5%', '9.0%'], ['$513', '$450', '$400', '$359', '$325'])),
        ('implied', 'What the price assumes', 'At $278, the market <em>still doubts the targets.</em>',
         implied([['Long-run cash flow of only about 10% of revenue', '13.5%, in line with the new framework'], ['Or a discount rate of about 9.9%', '8.0%']])
         + prose('In other words, the price only makes sense if the lowered 2028 cash target is itself badly missed, or defense is treated as far riskier than its contracts suggest.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Cash conversion', 'The 2028 cash target was just cut once; missile capacity spending of about $3 billion could run longer or cost more.'],
             ['Execution', 'About 60 new production buildings and a missile ramp through 2029; fixed-price contracts can bring overruns.'],
             ['Leadership', 'A new CEO after a conduct-related exit, and shareholder law firms have opened investigations.'],
             ['Budgets', 'Defense spending depends on Congress; the Missile Solutions IPO depends on markets.'],
         ]) + prose('<b>Upside:</b> the $53 billion backlog, more interceptor orders, buybacks at today&rsquo;s price, and the Missile Solutions IPO putting a public value on the fastest-growing part of the company.')),
        ('rec', 'Rating', 'A good business <em>at a discounted price.</em>',
         prose('At $278.43 against a base case of $402 ($411 weighted), even a 9% discount rate gives $325. The quarter confirmed demand: orders tripled and the backlog is at a record. The lower 2028 cash target trims the value by about 8%, but the price still assumes far less cash than the company now plans.',
               '<b>What would change the view:</b> another cut to the cash outlook, cost overruns on the missile ramp, or new findings from the conduct investigation.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Record orders, <em>a smaller cash target.</em></h2><p>The order book is the strongest it has been; the price still reflects doubt about turning it into cash.</p></div>'),
    ])

# ---------------------------------------------------------------- American Water
AW = 'https://www.prnewswire.com/news-releases/american-water-reports-solid-third-quarter-2026-results-narrows-2026-eps-guidance-to-top-half-of-range-affirms-long-term-targets-initiates-standalone-2027-eps-guidance-reflecting-growth-of-8-302922714.html'
AW_EST = 'https://247wallst.com/cards/american-water-works-q3-2026-earnings-awk-01m624j0fkt4khpx9vmns0xqts'
R['AWK'] = dict(
    t='AWK', slug='american-water', name='American Water Works', h1='American <em>Water</em>', sector='Utilities', date='October 29, 2026', timing=', the day after its third-quarter results',
    sub='American Water is the largest U.S. water utility, and it is merging with Essential Utilities. Regulated returns make its earnings steady: the third quarter was on plan, and the first 2027 guidance points to 8% growth. But its 2.6% dividend yield is half what a 10-year Treasury pays today, which makes it hard to justify the price on dividends alone.',
    call='Hold', method='Dividend model', price=139.79, pricenote='Close, October 28, 2026, before the results', base=100, bear=69, bull=132, wt=101, max=200, tick=25,
    fieldnote='The dividend model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Dividend model', 69, 132, 100, '$69 to $132, base $100'), ('Probability-weighted', None, None, 101, '$101'),
           ('Price at writing', None, None, 139.79, '$139.79'), ('52-week range', 121, 144, None, '$121 to $144')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Regulated pipes, <em>regulated returns.</em>',
         prose('American Water supplies drinking water and wastewater service in 14 states and to military bases. State regulators set its prices to allow a fair return on the money it invests (its rate base), so profits grow as it replaces old pipes and treatment plants.',
                 'In October 2025 it agreed an all-stock merger with Essential Utilities (0.305 American Water shares per Essential share; about 69/31 ownership), creating a company with roughly $29 billion of rate base. Three states have approved it and settlements have been reached in Pennsylvania, North Carolina and Texas; closing is still expected by the end of the first quarter of 2027.')
         + src([('Merger terms', 'https://www.nasdaq.com/articles/american-water-works-essential-utilities-merge-all-stock-deal')])),
        ('results', 'Latest results', 'On plan, <em>as usual.</em>',
         stats([('$2.00', 'Adjusted EPS, Q3 2026, from $1.89'), ('$6.07&ndash;6.12', '2026 EPS guidance, top half of the range'), ('$6.53&ndash;6.63', 'First 2027 guidance, about +8%'), ('$3.58', 'Annual dividend rate'), ('$4.1B', '2027 capital investment'), ('$360M', 'Rate increases still pending')])
         + prose('Third-quarter adjusted EPS rose 6% to $2.00 (reported EPS was flat at $1.94, after merger costs), slightly below the $2.11 analysts expected because of weather and higher costs. Revenue rose 4% to $1.51 billion. Full-year guidance was narrowed to the top half of its range, $6.07&ndash;6.12, and the company gave its first 2027 guidance, $6.53&ndash;6.63 on its own, about 8% growth. The 7&ndash;9% long-term targets for earnings and dividends were affirmed.',
                 'Regulators have approved $284 million of annual revenue increases this year, including new rates in Pennsylvania and New Jersey in the quarter, and requests for another $360 million are pending. Capital spending is about $3.7 billion this year and $4.1 billion in 2027, and the five-year plan is now more than $20 billion.')
         + src([('Q3 2026 results', AW), ('Against estimates', AW_EST)])),
        ('fin', 'Five years', 'Steady earnings, <em>negative free cash flow.</em>',
         fin_table('AWK') + prose('Operating cash flow covers only about two-thirds of capital spending, so free cash flow is negative every year. That is normal for a utility: the gap is funded with new debt and occasional equity, and the investment earns a regulated return.')
         + src([('American Water filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001410636&type=10-K')])),
        ('capital', 'Balance sheet', 'Debt-funded growth, <em>by design.</em>',
         prose('Debt was about $16.3 billion at the end of September, up from $15.8 billion at the start of the year as the company borrows to fund its pipe and plant program. The company sold forward 8.1 million shares in 2025 at about $140 and still has 4.7 million to settle by year-end, so modest dilution is part of the plan.')),
        ('value', 'Valuation', 'The dividend model gives <em>$100 a share.</em>',
         prose('For a regulated utility that funds growth with debt, a free-cash-flow model does not work; the dividend is the cleanest measure of what owners receive.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Dividend, next 12 months', '$3.58 growing', '$0.895 a quarter'],
             ['Dividend growth, 5 years', '8%', 'Midpoint of the 7&ndash;9% target'],
             ['Then', 'Fades to 3.5% by year 10', 'Long-run nominal growth'],
             ['Cost of equity', '8.3%', '5.15% Treasury, beta 0.70 (utility average), 4.5% premium'],
         ], 'mid')
         + bridge([('PV of 10 years of dividends', '$34.3'), ('PV of terminal value', '$66.1'), ('Dividend yield today', '2.6%'), ('10-year Treasury', '5.15%'), ('P/E on 2026 guidance', '22.9&times;'), ('Payout ratio', '~59%')], '$100')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Dividend growth, 5 years', '6%', '8%', '9%'], ['Long-run growth', '3.0%', '3.5%', '4.0%'],
             ['Cost of equity', '9.3%', '8.3%', '7.8%'], ['Value per share', '$69', '$100', '$132'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$101</b>.') + sens('Cost of equity', ['7.0%', '7.5%', '8.0%', '8.5%', '9.0%'], ['$139', '$121', '$107', '$96', '$87'])),
        ('implied', 'What the price assumes', 'At $140, <em>a 7% cost of equity.</em>',
         implied([['A cost of equity of about 7.0%', '8.3%, with Treasuries at 5.15%'], ['Or dividends growing about 5.1% a year forever', '3.5% long run']])
         + prose('Investors are treating American Water almost like a bond. That works when interest rates fall; with the 10-year Treasury above 5%, it is a stretch.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Interest rates', 'Utility shares move inversely to bond yields; higher yields mean lower prices.'],
             ['Regulation', 'Rate cases that grant less than requested slow earnings growth.'],
             ['Merger', 'Approvals, integration costs and the share issuance to Essential holders.'],
             ['Contamination rules', 'PFAS treatment requirements raise costs, though usually recoverable in rates.'],
         ]) + prose('<b>Upside:</b> falling interest rates would lift the value quickly: at a 7% cost of equity the model gives $139.')),
        ('rec', 'Rating', 'Hold. <em>A defensive anchor, priced for lower rates.</em>',
         prose('At $139.79 against a base case of $100, the shares price in a cost of equity well below what today&rsquo;s Treasury yields justify. As a stable, low-volatility holding it still does its job in the portfolio. The third quarter changed nothing in the model: the dividend and its 7&ndash;9% growth target are the same. The shares become attractive if rates fall or the price drops toward the low $100s.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Safe business, <em>rate-sensitive price.</em></h2><p>The earnings are reliable; the valuation is a bet on interest rates.</p></div>'),
    ])

# ---------------------------------------------------------------- Boeing
BO = 'https://investors.boeing.com/investors/news/press-release-details/2026/Boeing-Reports-Third-Quarter-Results/default.aspx'
BO_CALL = 'https://www.investing.com/news/transcripts/earnings-call-transcript-boeing-q3-2026-misses-profit-view-as-shares-slide-93CH-4976410'
BO_FCF = 'https://www.tradingkey.com/news/transcripts/262243052-tradingkey'
R['BA'] = dict(
    t='BA', slug='boeing', name='Boeing', h1='Boeing', sector='Aerospace &amp; defense', date='October 28, 2026', timing=', the day after its third-quarter results',
    sub='Boeing is two years into a turnaround after the 737 MAX door-plug accident. The backlog is a record $745 billion and cash flow is positive, but the third quarter showed the recovery running about a year behind plan: the $10 billion cash target moved to 2029. The shares fell 11% to $168, below what the model gives.',
    call='Buy', method='Cash-flow model', price=168.18, pricenote='Close, October 27, 2026', base=197, bear=104, bull=292, wt=197, max=400, tick=50,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 104, 292, 197, '$104 to $292, base $197'), ('Probability-weighted', None, None, 197, '$197'),
           ('Price at writing', None, None, 168.18, '$168.18'), ('52-week range', 168, 254, None, '$168 to $254')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Half of the world&rsquo;s <em>big-jet duopoly.</em>',
         prose('Boeing Commercial Airplanes builds the 737, 767, 777 and 787; Defense, Space &amp; Security builds military aircraft, satellites and weapons; Global Services supports both fleets with parts and maintenance, its most profitable unit. With Airbus it shares a duopoly in large passenger jets, so demand is not the problem: production is.')),
        ('results', 'Latest results', 'Record backlog, <em>a slower ramp.</em>',
         stats([('$24.2B', 'Revenue, Q3 2026, +4%'), ('161', 'Jets delivered'), ('+$0.5B', 'Free cash flow, after $0.7B of settlement payments'), ('$745B', 'Record backlog'), ('~$2B', '2026 free cash flow guidance'), ('&minus;$0.34', 'Core loss per share')])
         + prose('Boeing delivered 161 aircraft in the third quarter, including 124 737s, and free cash flow was $464 million after about $0.7 billion of Justice Department settlement payments. The core loss of $0.34 a share was wider than the $0.24 analysts expected, and revenue of $24.2 billion was slightly below estimates. Commercial Airplanes lost 6.5% on sales as supply-chain and rate-change costs rose; defense earned 6.2%, helped by a $252 million gain on selling HRL Laboratories, and services 18.3%. The backlog reached a record $745 billion, not yet counting the Navy&rsquo;s F/A-XX fighter, and the 737-7 and 737-10 were certified.')
         + prose('The news was the timetable. Stabilising the 737 at 47 a month will run into 2027, with the step to 52 in the second half of 2027; the 787 move from 8 to 10 a month slipped to the end of 2026, so 787 deliveries will be at the low end of 90 to 100. Management narrowed 2026 free cash flow to about $2 billion and set about $3 billion for 2027 and $6 billion for 2028, with the $10 billion target now in 2029, about a year later than before. The 777X is still due for first delivery in 2027.')
         + src([('Q3 2026 results, Boeing', BO), ('Earnings call', BO_CALL), ('Cash-flow outlook from the call', BO_FCF)])),
        ('fin', 'Five years', 'Losses since 2019, <em>a profit in 2025.</em>',
         fin_table('BA') + prose('Boeing lost money every year from 2019 to 2024. The 2025 profit includes the gain on selling its Jeppesen navigation business, so the turnaround shows up more clearly in cash flow than in earnings.')
         + src([('Boeing filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000012927&type=10-K')])),
        ('capital', 'Balance sheet', 'Heavy debt, <em>no longer rising.</em>',
         prose('Debt was $45.9 billion against $20.7 billion of cash and investments at the end of September, with $10 billion of undrawn credit lines; debt is down from over $50 billion. Shareholders&rsquo; equity only recently turned positive after years of losses. The 2024 equity raise and asset sales were used to protect the investment-grade rating.')
         + src([('Q3 2026 results, Boeing', BO)])),
        ('value', 'Valuation', 'The model gives <em>$197 a share.</em>',
         prose('Boeing&rsquo;s profits are still distorted by the recovery, so the model works from a free cash flow path. This update moves that path a year later, in line with the new outlook; the lower share price also lowers the discount rate slightly, because debt is now a larger share of the company&rsquo;s value, which offsets most of the delay.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Free cash flow, 2026&ndash;2030', '$2B, $3B, $6B, $10B, $11.5B', 'Company outlook to 2029, then 737 at 52 a month and 787 near 12'],
             ['Then', 'Grows 6%, fading to 3% by year 10', 'Deliveries level off, then long-run economic growth'],
             ['Discount rate', '9.6%', 'Beta 1.35, about 26% debt at 6%'],
             ['Net debt', '$25.2B', 'September 30, 2026'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$71B'), ('PV of terminal value', '$109B'), ('Enterprise value', '$181B'), ('Less net debt', '$25.2B'), ('Equity value', '$155B'), ('Shares', '791M')], '$197')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Free cash flow by 2030', '$7.5B', '$11.5B', '$14B'], ['Discount rate', '10.6%', '9.6%', '8.6%'],
             ['Value per share', '$104', '$197', '$292'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$197</b>.') + sens('Discount rate', ['8.0%', '8.5%', '9.0%', '9.5%'], ['$274', '$244', '$220', '$199'])),
        ('implied', 'What the price assumes', 'At $168, <em>about $10 billion of cash by 2030.</em>',
         prose('The price implies free cash flow of roughly <b>$10 billion a year by 2030</b>, about 15% below the base case at every step, or about what Boeing now targets for 2029 with no growth after it. The market is pricing a recovery that arrives late and stops short of the pre-2019 level.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Quality and the FAA', 'Any new incident could halt the production ramp again; the 777X still needs approval for the rest of its flight tests.'],
             ['Supply chain', 'Wings are the main limit on the 737, a wing-part supplier problem will add costs for several quarters, and engines pace the 787.'],
             ['Customer deposits', 'Lower advance payments from airlines are one reason 2027 cash flow is guided to only $3 billion.'],
             ['Fixed-price defense programs', 'Air Force One and others have produced repeated charges.'],
         ]) + prose('<b>Upside:</b> the F/A-XX contract entering the backlog, defense growth that management now expects in the mid-single digits or higher, and the 777X entering service in 2027.')),
        ('rec', 'Rating', 'Below the model, <em>a year behind plan.</em>',
         prose('At $168.18 against a base case of $197, the shares now trade below the model, which already uses the later timetable. The upside depends on Boeing meeting the new dates; another slip, or a stumble on quality, would cut the value.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>The recovery is late. <em>The price now allows for it.</em></h2><p>Demand is guaranteed by the backlog; Boeing has to build the planes.</p></div>'),
    ])
