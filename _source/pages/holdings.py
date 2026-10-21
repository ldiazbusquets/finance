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
       ('value', 'Valuation'), ('implied', 'What the price assumes'), ('risks', 'Risks'), ('rec', 'Recommendation')]

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
        ('rec', 'Recommendation', 'Hold. <em>Fair at a 10% discount rate, rich at 12%.</em>',
         prose('At $216.47 against a base case of $166 ($180 weighted), Nvidia trades above what the model supports at its own cost of capital, but within reach of it at a lower rate. The business is in its strongest position ever. The call is <b>Hold</b>: keep the position, add only on a pullback toward the base case.',
               '<b>What would change the view:</b> next-year guidance that points to growth well above 40% would move it toward Buy; signs that cloud spending is peaking would move it toward Sell. Watch fiscal third-quarter results in November against the $108 billion guidance.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>The best business in tech, <em>priced like it.</em></h2><p>Nvidia earns more than almost any company in history; the price already counts on that continuing.</p></div>'),
    ])

# ---------------------------------------------------------------- Amazon
AM = 'https://www.aboutamazon.com/news/company-news/amazon-earnings-q2-2026-report'
R['AMZN'] = dict(
    t='AMZN', slug='amazon', name='Amazon', h1='Amazon', sector='Consumer &amp; cloud', date=DATE, timing=LATER,
    sub='Amazon is three businesses in one: the largest online store, the largest cloud (AWS) and a fast-growing advertising arm. AWS is accelerating on AI demand, but Amazon is spending more than $200 billion a year to build data centers, which has pushed free cash flow below zero. The price assumes that spending pays off handsomely.',
    call='Hold', method='Cash-flow model', price=262.63, base=153, bear=74, bull=267, wt=162, max=400, tick=50,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 74, 267, 153, '$74 to $267, base $153'), ('Probability-weighted', None, None, 162, '$162'),
           ('Price at writing', None, None, 262.63, '$262.63'), ('52-week range', 196, 287, None, '$196 to $287')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'A store, a cloud <em>and an ad network.</em>',
         prose('Amazon reports three segments. <b>North America</b> and <b>International</b> are the store: first-party retail, third-party seller services, Prime subscriptions and advertising. <b>AWS</b> rents computing, storage and AI infrastructure to companies and governments.',
               'Most of the profit comes from AWS and advertising, which ride on the store&rsquo;s traffic. Retail itself earns thin margins but funds the logistics network that keeps customers loyal. Amazon also owns a large stake in Anthropic, the AI company, which it does not value in its operating results.')
         + key('Takeaway', 'Value comes mostly from AWS and ads; the store is the moat that feeds them.')),
        ('results', 'Latest results', 'AWS is growing 37% <em>on a $170 billion base.</em>',
         stats([('$200.6B', 'Revenue, Q2 2026, +20%'), ('+37%', 'AWS growth'), ('$27.5B', 'Operating income, +43%'), ('39%', 'AWS operating margin'), ('+26%', 'Advertising growth'), ('&minus;$7.6B', 'Free cash flow, last 12 months')])
         + prose('Second-quarter revenue rose 20% to $200.6 billion. AWS revenue grew 37% to $42.2 billion with $16.6 billion of operating income, and advertising grew 26%. Net income of $62.6 billion was swollen by a $53.4 billion gain, mostly from revaluing the Anthropic stake, so it says little about the business.',
                 'The cost is in cash flow: free cash flow over the last twelve months was <b>negative $7.6 billion</b>, because purchases of property and equipment rose $66 billion in a year. Capital spending for 2026 is guided to about $220 billion. Guidance for the third quarter is $197&ndash;202 billion of revenue and $22.5&ndash;26.5 billion of operating income.')
         + src([('Q2 2026 results', AM), ('Capex guidance', 'https://betafinch.com/blog/amazon-q2-2026-earnings-capex-guidance')])),
        ('fin', 'Five years', 'Margins tripled; <em>cash flow went the other way.</em>',
         fin_table('AMZN') + prose('Operating margin rose from 2% in 2022 to about 12% as AWS and ads grew faster than retail. Net income in the last twelve months includes the Anthropic gains. Capital spending has more than doubled since 2024, so free cash flow has fallen even as profit rose.')
         + src([('Amazon filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K')])),
        ('capital', 'Balance sheet', 'Strong, <em>but now borrowing to build.</em>',
         prose('Amazon held about $123 billion of cash against $133 billion of debt in June, so net debt is small. It pays no dividend and buys back little; every spare dollar goes into data centers, chips (Trainium) and the Leo satellite network. The Anthropic stake is a sizeable asset that is <b>not</b> included in this valuation, so it is upside to the numbers below.')),
        ('value', 'Valuation', 'The model gives <em>$153 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, 2026', '$810B', 'First half plus Q3 guidance'],
             ['Growth, 2027 and 2028', '12%, then 11%', 'AWS in the 20s, retail high single digits'],
             ['Growth after that', 'Fades to 3% by year 10', 'A straight glide to long-run economic growth'],
             ['Operating margin', '13% rising to 18% by 2031', 'More AWS and advertising in the mix'],
             ['Net investment', '$130B, $100B, $70B, $50B, then $1 per $2 of new revenue', 'The data-center build peaks, then normalises'],
             ['Tax rate', '19%', 'Below the 21% federal rate after credits'],
             ['Discount rate', '10.8%', 'Beta 1.33, 4.5% premium, a little debt'],
             ['Terminal growth', '3.0%', 'With a 20% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$655B'), ('PV of terminal value', '$1.02T'), ('Enterprise value', '$1.68T'), ('Less net debt', '$10B'), ('Equity value', '$1.67T'), ('Shares', '10.9B')], '$153')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '8% / 7%', '12% / 11%', '15% / 14%'], ['Long-run operating margin', '14%', '18%', '22%'],
             ['Discount rate', '11.8%', '10.8%', '9.8%'], ['Value per share', '$74', '$153', '$267'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$162</b>.') + sens('Discount rate', ['8.5%', '9.0%', '9.5%', '10.0%'], ['$231', '$209', '$190', '$175'])),
        ('implied', 'What the price assumes', 'At $263, the build-out <em>has to earn a lot.</em>',
         implied([['A long-run operating margin near 29%', '18%; Amazon&rsquo;s best year so far was about 12%'], ['Revenue growth of about 23% a year for two years', '12% and 11%'], ['A discount rate of about 7.9%', '10.8%']])
         + prose('The market is betting that the $220 billion a year going into AI infrastructure earns AWS-like returns. The Anthropic stake, left out of the model, covers part of the gap.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['AI returns', 'If AI demand cools, Amazon is left with expensive capacity and falling AWS margins.'],
             ['Cash flow', 'Negative free cash flow leaves less room for error and more reliance on debt.'],
             ['Regulation', 'The U.S. antitrust case against the store, and scrutiny of AWS in Europe.'],
             ['Consumer slowdown', 'Retail and ads both depend on spending.'],
         ]) + prose('<b>Upside:</b> Trainium chips cutting AWS costs, advertising in Prime Video, Leo satellite internet and the value of the Anthropic stake.')),
        ('rec', 'Recommendation', 'Hold. <em>A great company in an expensive building phase.</em>',
         prose('At $262.63 against a base case of $153 ($162 weighted), the shares price in much higher long-run margins than Amazon has ever earned. The call is <b>Hold</b>: keep the core position, don&rsquo;t add until free cash flow turns back up or the price comes closer to the bull case.',
               '<b>Watch in the third-quarter report:</b> AWS growth staying above 30%, operating income against the $22.5&ndash;26.5 billion guide, and any change to the $220 billion capex plan.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Own the platform, <em>wait for the cash.</em></h2><p>The spending is a bet on AI that only pays off if AWS keeps its margins as it grows.</p></div>'),
    ])

# ---------------------------------------------------------------- Meta
ME = 'https://www.stocktitan.net/news/META/meta-reports-second-quarter-2026-hkjfhayj8l0v.html'
R['META'] = dict(
    t='META', slug='meta', name='Meta Platforms', h1='Meta <em>Platforms</em>', sector='Communication services', date=DATE, timing=LATER,
    sub='Meta owns Facebook, Instagram, WhatsApp and Messenger, used by 3.6 billion people a day, and sells the ads in between. AI has made those ads work better and revenue is growing 28%. But Meta is spending so heavily on AI data centers that free cash flow fell to almost nothing last quarter.',
    call='Hold', method='Cash-flow model', price=694.25, base=516, bear=215, bull=894, wt=535, max=1000, tick=100,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 215, 894, 516, '$215 to $894, base $516'), ('Probability-weighted', None, None, 535, '$535'),
           ('Price at writing', None, None, 694.25, '$694.25'), ('52-week range', 520, 780, None, '$520 to $780')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Three billion people <em>and an ad auction.</em>',
         prose('Meta earns nearly all its money from advertising on its Family of Apps. AI ranks what each person sees and which ads they are shown, and tools like Advantage+ let advertisers hand the whole campaign to Meta&rsquo;s systems. Reality Labs, the headset and smart-glasses unit, loses about $4&ndash;5 billion a quarter.',
               'The strategic bet is on building its own frontier AI models and the computing to run them, both to improve ads and to create new products such as Meta AI.')
         + key('Takeaway', 'The ad machine is stronger than ever; the debate is about how much it costs to keep it ahead.')),
        ('results', 'Latest results', 'Revenue up 28%, <em>free cash flow down 91%.</em>',
         stats([('$60.8B', 'Revenue, Q2 2026, +28%'), ('3.60B', 'Daily active people, +3%'), ('+14% / +12%', 'Ad impressions / price per ad'), ('31%', 'Operating margin, from 43%'), ('$0.8B', 'Free cash flow, from $8.6B'), ('$130&ndash;145B', '2026 capital spending')])
         + prose('Revenue grew 28% to $60.8 billion, from both more ads and higher prices. Costs grew 55%, including $2.4 billion of legal charges and $1.2 billion of severance, so operating income fell 8% and EPS fell 13% to $6.18. Capital spending of $31.1 billion consumed almost all of the $31.9 billion of operating cash flow.',
                 'Meta issued about $25 billion of new long-term debt in the quarter and bought back no stock. The shares fell about 8% the next day. Guidance: third-quarter revenue of $61&ndash;64 billion, 2026 expenses of $165&ndash;169 billion and capex of $130&ndash;145 billion.')
         + src([('Q2 2026 results', ME), ('Market reaction', 'https://leverageshares.com/en-eu/insights/meta-q2-2026-earnings-ai-capex-turns-market-sentiment/')])),
        ('fin', 'Five years', 'Back to growth, <em>then into a spending wave.</em>',
         fin_table('META') + prose('2022 was the low point: revenue fell and Reality Labs spending peaked. The &ldquo;year of efficiency&rdquo; in 2023 restored margins above 40%. Capital spending has more than doubled since 2024, and free cash flow has fallen accordingly.')
         + src([('Meta filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=10-K')])),
        ('capital', 'Balance sheet', 'From net cash <em>to borrowing.</em>',
         prose('Meta had $90.3 billion of cash and securities against $83.7 billion of long-term debt in June, so it is roughly net cash neutral after years of large net cash. Buybacks have stopped for now; the $2.10 annual dividend continues. Management also warned that youth-safety trials in 2026 &ldquo;may ultimately result in a material loss.&rdquo;')),
        ('value', 'Valuation', 'The model gives <em>$516 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, 2026', '$248B', 'First half plus Q3 guidance'],
             ['Growth, 2027 and 2028', '18%, then 14%', 'AI-improved ads, slowing from 28%'],
             ['Operating margin', '34% rising to 38% by 2031', 'Depreciation from the build-out holds it below past highs'],
             ['Net investment', '$110B, $90B, $60B, $40B, then $1 per $2 of new revenue', 'Spending peaks in 2027'],
             ['Tax rate', '16%', 'Guidance of 15&ndash;17%'],
             ['Discount rate', '11.2%', 'Beta 1.42, 4.5% premium'],
             ['Terminal growth', '3.0%', 'With a 25% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$535B'), ('PV of terminal value', '$781B'), ('Enterprise value', '$1.32T'), ('Plus net cash', '$7B'), ('Equity value', '$1.32T'), ('Shares', '2.57B')], '$516')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '10% / 8%', '18% / 14%', '24% / 18%'], ['Long-run operating margin', '30%', '38%', '44%'],
             ['Discount rate', '12.2%', '11.2%', '10.2%'], ['Value per share', '$215', '$516', '$894'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$535</b>.') + sens('Discount rate', ['8.5%', '9.0%', '9.5%', '10.0%'], ['$820', '$743', '$677', '$621'])),
        ('implied', 'What the price assumes', 'At $694, margins <em>back near 50%.</em>',
         implied([['A long-run operating margin near 50%', '38%; Meta&rsquo;s peak was in the low 40s'], ['Revenue growth of about 21% a year for two years', '18% and 14%'], ['A discount rate of about 9.4%', '11.2%']])
         + prose('Meta is closer to fair value than Amazon or Vertiv: a slightly lower discount rate or slightly faster growth closes most of the gap.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['AI spending without return', 'Capex of $130&ndash;145 billion a year has to lift revenue or it simply lowers margins.'],
             ['Legal', 'Youth-safety trials, EU regulation and antitrust can cost money and limit ad targeting.'],
             ['Reality Labs', 'Losses of roughly $18&ndash;20 billion a year with no clear payoff date.'],
             ['Ad cycle', 'Advertising is the first budget cut in a slowdown.'],
         ]) + prose('<b>Upside:</b> WhatsApp business messaging, AI agents that sell for advertisers, and spending easing after 2027 would lift free cash flow quickly.')),
        ('rec', 'Recommendation', 'Hold. <em>Strong ads, heavy bills.</em>',
         prose('At $694.25 against a base case of $516 ($535 weighted), Meta trades above the model at an 11% discount rate but close to fair at 9.5%. The call is <b>Hold</b>. A move toward the low $500s, or evidence that 2027 spending will fall, would make it a Buy.',
               '<b>Watch in the third-quarter report:</b> revenue against $61&ndash;64 billion, any first view of 2027 capex, and whether buybacks resume.')
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
        ('rec', 'Recommendation', 'Hold. <em>The best bank, at a full price.</em>',
         prose('At $335.26 against a base case of $284 ($290 weighted), the shares need returns above the bank&rsquo;s own through-cycle target. The call is <b>Hold</b>; it would be a Buy below about 2.2 times book value, roughly $290.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Quality you pay for.</h2><p>JPMorgan earns more than its peers; the premium is already in the price.</p></div>'),
    ])

# ---------------------------------------------------------------- Vertiv
VR = 'https://www.nasdaq.com/press-release/vertiv-reports-strong-second-quarter-2026-diluted-eps-growth-53-adjusted-diluted-eps'
R['VRT'] = dict(
    t='VRT', slug='vertiv', name='Vertiv', h1='Vertiv', sector='Electrical equipment', date=DATE, timing=LATER,
    sub='Vertiv makes the power and cooling equipment inside data centers, from backup power to the liquid cooling that AI chips now need. Sales are guided up 30% this year, but the shares have fallen by almost half from their peak after a quarter that missed the company&rsquo;s own growth range.',
    call='Hold', method='Cash-flow model', price=203.56, base=117, bear=65, bull=188, wt=122, max=400, tick=50,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 65, 188, 117, '$65 to $188, base $117'), ('Probability-weighted', None, None, 122, '$122'),
           ('Price at writing', None, None, 203.56, '$203.56'), ('52-week range', 148, 380, None, '$148 to $380')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Keeping AI chips <em>powered and cool.</em>',
         prose('Vertiv sells uninterruptible power supplies, switchgear and power distribution, thermal management (including liquid cooling for GPUs), and the service that keeps them running. Its customers are cloud companies, colocation operators and enterprises building data centers, now increasingly for AI.',
                 'As each rack of AI chips draws more power and generates more heat, the equipment Vertiv sells per megawatt rises. Its main competitors are Schneider Electric and Eaton.')),
        ('results', 'Latest results', 'Profit up 50%, <em>growth below plan.</em>',
         stats([('$3.27B', 'Sales, Q2 2026, +24%'), ('17.8%', 'Organic growth, vs 20&ndash;24% guided'), ('22.6%', 'Adjusted operating margin'), ('$0.93B', 'Adjusted free cash flow'), ('$13.8&ndash;14.2B', '2026 sales guidance'), ('30&ndash;32%', '2026 organic growth guidance')])
         + prose('Second-quarter sales rose 24% to $3.27 billion and adjusted EPS rose 60%, but organic growth of 17.8% fell short of the 20&ndash;24% the company itself had guided. Management blamed the timing of multi-phase projects and supply-chain sequencing and declined to size the shortfall; the stock fell 17% that day. It has also stopped disclosing orders and backlog.',
                 'At the same time it raised full-year guidance: sales of $13.8&ndash;14.2 billion, 30&ndash;32% organic growth and adjusted EPS of $6.65&ndash;6.75. That implies about 40% organic growth in the second half, which the third-quarter report will test.')
         + src([('Q2 2026 results', VR), ('Analysis of the miss', 'https://research.aardvarklabs.co/research/vrt/earnings/2026-q2/vrt-2026-q2-recap')])),
        ('fin', 'Five years', 'Sales doubled; <em>margins nearly tripled.</em>',
         fin_table('VRT') + prose('Operating margin rose from about 4% in 2022 to near 19% in the last twelve months, and free cash flow went from negative to over $2.9 billion.')
         + src([('Vertiv filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001674101&type=10-K')])),
        ('capital', 'Balance sheet', 'From leveraged <em>to net cash.</em>',
         prose('Vertiv was formed from a private-equity buyout and carried heavy debt. It now holds about $2.8 billion of cash against $2.9 billion of debt, essentially net cash neutral, with $5.6 billion of liquidity. It is spending on bolt-on acquisitions in liquid cooling and services.')),
        ('value', 'Valuation', 'The model gives <em>$117 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Sales, 2026', '$14.0B', 'Guidance midpoint'],
             ['Growth, 2027 and 2028', '25%, then 16%', 'AI build-out continues, then slows'],
             ['Operating margin', '22.5% rising to 24.5%', 'Adjusted margin less acquisition amortization'],
             ['Reinvestment', '$1 for every $3 of new sales', 'Factories, working capital and acquisitions to add capacity'],
             ['Discount rate', '13.1%', 'Beta 1.83, 4.5% premium'],
             ['Terminal growth', '3.0%', 'With a 25% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$25B'), ('PV of terminal value', '$21B'), ('Enterprise value', '$46B'), ('Net debt', '&asymp; $0'), ('Equity value', '$46B'), ('Shares', '393M')], '$117')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '12% / 8%', '25% / 16%', '35% / 22%'], ['Long-run operating margin', '21%', '24.5%', '27%'],
             ['Discount rate', '14.1%', '13.1%', '12.1%'], ['Value per share', '$65', '$117', '$188'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$122</b>.') + sens('Discount rate', ['9.0%', '10.0%', '11.0%', '12.0%'], ['$205', '$174', '$150', '$132'])
         + key('Read', 'Vertiv&rsquo;s beta of 1.83 gives it the highest discount rate of any holding. At 9%, the price is about fair.')),
        ('implied', 'What the price assumes', 'At $204, <em>33% growth for two years.</em>',
         implied([['Sales growth of about 33% a year in 2027 and 2028', '25% and 16%'], ['A long-run operating margin near 42%', '24.5%'], ['A discount rate of about 9.0%', '13.1%']])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Execution', 'One quarter already missed its own range; another would hurt credibility further.'],
             ['Visibility', 'With orders and backlog no longer disclosed, demand is harder to check.'],
             ['Data-center spending', 'Results depend on a small number of very large customers&rsquo; build plans.'],
             ['Competition', 'Schneider, Eaton and new liquid-cooling entrants are chasing the same projects.'],
         ]) + prose('<b>Upside:</b> a third quarter that delivers the guided 34&ndash;36% organic growth would show the miss was timing, and the stock is already 46% below its high.')),
        ('rec', 'Recommendation', 'Hold. <em>Down a lot, still not cheap at its risk.</em>',
         prose('At $203.56 against a base case of $117 ($122 weighted), Vertiv is fully valued at its high cost of capital, though the bull case ($188) is close to the price. The call is <b>Hold</b>; add only after a clean third quarter.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>The right market, <em>prove the execution.</em></h2><p>Demand is not the issue; delivering it on schedule is.</p></div>'),
    ])

# ---------------------------------------------------------------- L3Harris
LH = 'https://www.nasdaq.com/press-release/l3harris-technologies-reports-robust-second-quarter-2026-results-2026-07-29'
R['LHX'] = dict(
    t='LHX', slug='l3harris', name='L3Harris', h1='L3<em>Harris</em>', sector='Aerospace &amp; defense', date=DATE, timing=LATER,
    sub='L3Harris makes satellites, secure communications, sensors and, since buying Aerojet Rocketdyne, the rocket motors inside U.S. missiles. Orders are at a record and missile demand is rising, yet the shares have fallen about a third from their high after a CEO exit and a delayed IPO. On its own cash-flow targets, the stock looks cheap.',
    call='Buy', method='Cash-flow model', price=248.77, base=436, bear=231, bull=652, wt=439, max=800, tick=100,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 231, 652, 436, '$231 to $652, base $436'), ('Probability-weighted', None, None, 439, '$439'),
           ('Price at writing', None, None, 248.77, '$248.77'), ('52-week range', 232, 379, None, '$232 to $379')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Space, communications <em>and missiles.</em>',
         prose('L3Harris has three segments. <b>Space &amp; Mission Systems</b> builds satellites, sensors and aircraft systems. <b>Communications &amp; Spectrum Dominance</b> makes tactical radios and electronic warfare equipment, its most profitable unit. <b>Missile Solutions</b> makes solid rocket motors and propulsion for interceptors such as THAAD and PAC-3, a bottleneck for U.S. munitions supply.',
                 'In January 2026 the Pentagon committed a $1 billion investment in Missile Solutions ahead of a planned IPO of that business; L3Harris has since pushed the IPO to mid-2027.')),
        ('results', 'Latest results', 'Record orders, <em>a raised outlook.</em>',
         stats([('$5.88B', 'Revenue, Q2 2026, +8%'), ('1.2&times;', 'Book-to-bill'), ('$42B', 'Record backlog'), ('16.0%', 'Segment operating margin'), ('$23.2&ndash;23.7B', '2026 revenue guidance'), ('~$3.0B', '2026 free cash flow guidance')])
         + prose('Second-quarter revenue rose 8%, orders of $7.3 billion took the backlog to a record $42 billion, and Missile Solutions grew 14%. The company raised its 2026 revenue and EPS guidance and kept free cash flow at about $3.0 billion. Its 2028 framework targets about $27 billion of revenue and $3.5 billion of free cash flow.',
                 'The shares fell anyway, first on the IPO delay and debt, then in August when the board removed CEO Christopher Kubasik for a conduct violation and named insider Sam Mehta as his successor.')
         + src([('Q2 2026 results', LH), ('CEO change, 8-K', 'https://www.sec.gov/Archives/edgar/data/0000202058/000020205826000066/lhxleadershipchangepressre.htm'), ('2028 framework', 'https://www.tikr.com/blog/the-pentagon-invested-1-billion-in-l3harris-heres-what-analysts-say')])),
        ('fin', 'Five years', 'Steady growth, <em>rising cash.</em>',
         fin_table('LHX') + prose('Revenue jumped in 2023 with the Aerojet Rocketdyne purchase. Operating margin on a GAAP basis is held down by amortization of acquired intangibles; cash flow, which adds that back, is the better measure and has grown every year. The FY2025 revenue figure is from the company&rsquo;s release.')
         + src([('L3Harris filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000202058&type=10-K')])),
        ('capital', 'Balance sheet', 'Leveraged, <em>but deleveraging.</em>',
         prose('Debt is about $11.0 billion against $1.5 billion of cash, mostly from the Aerojet deal, with net interest of about $560 million a year. The company also received $973 million from the Pentagon&rsquo;s preferred-stock investment in Missile Solutions, which the model treats like debt. It pays a $4.90 annual dividend and is buying back stock.')),
        ('value', 'Valuation', 'The model gives <em>$436 a share.</em>',
         prose('Because GAAP profit understates cash generation, this model works directly from free cash flow to the firm (free cash flow plus after-tax interest), following the company&rsquo;s own path to 2028.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, 2026', '$23.45B', 'Guidance midpoint'],
             ['Growth, 2027 and 2028', '7.5% a year', 'Reaches the $27B 2028 target'],
             ['Cash flow to the firm', '$3.65B, then $3.95B, then 14.6% of revenue', '$3.0&ndash;3.5B free cash flow plus after-tax interest'],
             ['Growth after 2028', 'Fades to 3% by year 10', 'A straight glide to long-run economic growth'],
             ['Discount rate', '7.9%', 'Beta 0.80 (defense peers; the measured 0.61 understates risk after this year), about 19% debt'],
             ['Terminal growth', '3.0%', 'In line with long-run economic growth'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$32.7B'), ('PV of terminal value', '$59.3B'), ('Enterprise value', '$92.1B'), ('Less net debt and preferred', '$10.5B'), ('Equity value', '$81.6B'), ('Shares', '187M')], '$436')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '4% / 3%', '7.5% / 7.5%', '10% / 9%'], ['Cash flow, share of revenue', '12.5%', '14.6%', '15.5%'],
             ['Discount rate', '8.9%', '7.9%', '6.9%'], ['Value per share', '$231', '$436', '$652'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$439</b>.') + sens('Discount rate', ['7.0%', '7.5%', '8.0%', '8.5%', '9.0%'], ['$547', '$480', '$427', '$383', '$346'])),
        ('implied', 'What the price assumes', 'At $249, the market <em>doubts the targets.</em>',
         implied([['Long-run cash flow of only about 9% of revenue', '14.6%, in line with guidance'], ['Or a discount rate of about 10.9%', '7.9%']])
         + prose('In other words, the price only makes sense if the 2028 cash targets are badly missed or defense is treated as being as risky as a tech stock.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Leadership', 'A new CEO after a conduct-related exit, and shareholder law firms have opened investigations.'],
             ['Execution', 'About 60 new production buildings and a missile ramp through 2029; fixed-price contracts can bring overruns.'],
             ['Debt', 'Interest of about $560 million a year limits flexibility.'],
             ['Budgets', 'Defense spending depends on Congress; the IPO depends on markets.'],
         ]) + prose('<b>Upside:</b> missile demand, space programs, and the Missile Solutions IPO putting a public value on the fastest-growing part of the company.')),
        ('rec', 'Recommendation', 'Buy. <em>A good business at a discounted price.</em>',
         prose('At $248.77 against a base case of $436 ($439 weighted), even a 9% discount rate gives $346. The selloff reflects real but temporary problems: a CEO change and a delayed IPO. The call is <b>Buy</b>, with the bear case ($231) close to today&rsquo;s price as the main warning.',
               '<b>What would change the view:</b> a cut to the $3.0 billion cash-flow guidance or new findings from the conduct investigation.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Headline risk, <em>not business risk.</em></h2><p>The backlog is at a record; the price reflects the boardroom, not the order book.</p></div>'),
    ])

# ---------------------------------------------------------------- American Water
AW = 'https://newsroom.amwater.com/2026-07-29-AMERICAN-WATER-REPORTS-SOLID-SECOND-QUARTER-2026-RESULTS-AFFIRMS-2026-EPS-GUIDANCE-AND-LONG-TERM-TARGETS'
R['AWK'] = dict(
    t='AWK', slug='american-water', name='American Water Works', h1='American <em>Water</em>', sector='Utilities', date=DATE, timing=LATER,
    sub='American Water is the largest U.S. water utility, and it is merging with Essential Utilities. Regulated returns make its earnings steady, growing 7&ndash;9% a year. But its 2.6% dividend yield is half what a 10-year Treasury pays today, which makes it hard to justify the price on dividends alone.',
    call='Hold', method='Dividend model', price=135.79, base=100, bear=69, bull=132, wt=101, max=200, tick=25,
    fieldnote='The dividend model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Dividend model', 69, 132, 100, '$69 to $132, base $100'), ('Probability-weighted', None, None, 101, '$101'),
           ('Price at writing', None, None, 135.79, '$135.79'), ('52-week range', 121, 146, None, '$121 to $146')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Regulated pipes, <em>regulated returns.</em>',
         prose('American Water supplies drinking water and wastewater service in 14 states and to military bases. State regulators set its prices to allow a fair return on the money it invests (its rate base), so profits grow as it replaces old pipes and treatment plants.',
                 'In October 2025 it agreed an all-stock merger with Essential Utilities (0.305 American Water shares per Essential share; about 69/31 ownership), creating a company with roughly $29 billion of rate base. Closing is expected by the end of the first quarter of 2027.')
         + src([('Merger terms', 'https://www.nasdaq.com/articles/american-water-works-essential-utilities-merge-all-stock-deal')])),
        ('results', 'Latest results', 'On plan, <em>as usual.</em>',
         stats([('$1.61', 'EPS, Q2 2026, from $1.49'), ('$6.02&ndash;6.12', '2026 EPS guidance'), ('7&ndash;9%', 'Long-term EPS and dividend growth'), ('$3.58', 'Annual dividend rate'), ('$3.7B', '2026 capital investment'), ('$494M', 'Rate increases still pending')])
         + prose('Second-quarter EPS rose 8% and full-year guidance was affirmed. Regulators have approved $216 million of annual revenue increases this year, and requests for another $494 million are pending in six states. The merger has three state approvals so far.')
         + src([('Q2 2026 results', AW)])),
        ('fin', 'Five years', 'Steady earnings, <em>negative free cash flow.</em>',
         fin_table('AWK') + prose('Operating cash flow covers only about two-thirds of capital spending, so free cash flow is negative every year. That is normal for a utility: the gap is funded with new debt and occasional equity, and the investment earns a regulated return.')
         + src([('American Water filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001410636&type=10-K')])),
        ('capital', 'Balance sheet', 'Debt-funded growth, <em>by design.</em>',
         prose('Debt is about $16 billion against $11.7 billion of equity. The company sold forward 8.1 million shares in 2025 at about $140 and still has 4.7 million to settle by year-end, so modest dilution is part of the plan.')),
        ('value', 'Valuation', 'The dividend model gives <em>$100 a share.</em>',
         prose('For a regulated utility that funds growth with debt, a free-cash-flow model does not work; the dividend is the cleanest measure of what owners receive.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Dividend, next 12 months', '$3.58 growing', '$0.895 a quarter'],
             ['Dividend growth, 5 years', '8%', 'Midpoint of the 7&ndash;9% target'],
             ['Then', 'Fades to 3.5% by year 10', 'Long-run nominal growth'],
             ['Cost of equity', '8.3%', '5.15% Treasury, beta 0.70 (utility average), 4.5% premium'],
         ], 'mid')
         + bridge([('PV of 10 years of dividends', '$34.3'), ('PV of terminal value', '$66.1'), ('Dividend yield today', '2.6%'), ('10-year Treasury', '5.15%'), ('P/E on 2026 guidance', '22.4&times;'), ('Payout ratio', '~59%')], '$100')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Dividend growth, 5 years', '6%', '8%', '9%'], ['Long-run growth', '3.0%', '3.5%', '4.0%'],
             ['Cost of equity', '9.3%', '8.3%', '7.8%'], ['Value per share', '$69', '$100', '$132'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$101</b>.') + sens('Cost of equity', ['7.0%', '7.5%', '8.0%', '8.5%', '9.0%'], ['$139', '$121', '$107', '$96', '$87'])),
        ('implied', 'What the price assumes', 'At $136, <em>a 7% cost of equity.</em>',
         implied([['A cost of equity of about 7.1%', '8.3%, with Treasuries at 5.15%'], ['Or dividends growing about 5% a year forever', '3.5% long run']])
         + prose('Investors are treating American Water almost like a bond. That works when interest rates fall; with the 10-year Treasury above 5%, it is a stretch.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Interest rates', 'Utility shares move inversely to bond yields; higher yields mean lower prices.'],
             ['Regulation', 'Rate cases that grant less than requested slow earnings growth.'],
             ['Merger', 'Approvals, integration costs and the share issuance to Essential holders.'],
             ['Contamination rules', 'PFAS treatment requirements raise costs, though usually recoverable in rates.'],
         ]) + prose('<b>Upside:</b> falling interest rates would lift the value quickly: at a 7% cost of equity the model gives $139.')),
        ('rec', 'Recommendation', 'Hold. <em>A defensive anchor, priced for lower rates.</em>',
         prose('At $135.79 against a base case of $100, the shares price in a cost of equity well below what today&rsquo;s Treasury yields justify. As a stable, low-volatility holding it still does its job in the portfolio. The call is <b>Hold</b>; it becomes attractive if rates fall or the price drops toward the low $100s.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>Safe business, <em>rate-sensitive price.</em></h2><p>The earnings are reliable; the valuation is a bet on interest rates.</p></div>'),
    ])

# ---------------------------------------------------------------- Boeing
BO = 'https://finance.biggo.com/news/US_BA_2026-07-28'
R['BA'] = dict(
    t='BA', slug='boeing', name='Boeing', h1='Boeing', sector='Aerospace &amp; defense', date=DATE, timing=LATER,
    sub='Boeing is two years into a turnaround after the 737 MAX door-plug accident. Deliveries are at their highest since 2018, cash flow has turned positive and the backlog is a record $715 billion. The price assumes the recovery reaches roughly $11 billion of annual free cash flow, which is about what the model expects.',
    call='Hold', method='Cash-flow model', price=190.47, base=197, bear=105, bull=291, wt=197, max=400, tick=50,
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 105, 291, 197, '$105 to $291, base $197'), ('Probability-weighted', None, None, 197, '$197'),
           ('Price at writing', None, None, 190.47, '$190.47'), ('52-week range', 177, 254, None, '$177 to $254')],
    toc=TOC, chapters=[
        ('overview', 'The business', 'Half of the world&rsquo;s <em>big-jet duopoly.</em>',
         prose('Boeing Commercial Airplanes builds the 737, 767, 777 and 787; Defense, Space &amp; Security builds military aircraft, satellites and weapons; Global Services supports both fleets with parts and maintenance, its most profitable unit. With Airbus it shares a duopoly in large passenger jets, so demand is not the problem: production is.')),
        ('results', 'Latest results', 'Most deliveries <em>since 2018.</em>',
         stats([('$24.6B', 'Revenue, Q2 2026, +8%'), ('171', 'Jets delivered'), ('+$0.6B', 'Free cash flow, first positive in a while'), ('$715B', 'Record backlog'), ('$1&ndash;3B', '2026 free cash flow guidance'), ('&minus;$0.76', 'Core loss per share')])
         + prose('Boeing delivered 171 aircraft in the second quarter, including 129 737 MAXs, and free cash flow turned positive at $631 million. It still reported a core loss, including a $280 million charge on the Air Force One program. The 737 is ramping toward 47 a month, with a new line in Everett and a next step to 52; the 787 is at 8 a month, held back by engine supply; the 777X remains on track for first delivery in 2027.')
         + src([('Q2 2026 results summary', BO)])),
        ('fin', 'Five years', 'Losses since 2019, <em>a profit in 2025.</em>',
         fin_table('BA') + prose('Boeing lost money every year from 2019 to 2024. The 2025 profit includes the gain on selling its Jeppesen navigation business, so the turnaround shows up more clearly in cash flow than in earnings.')
         + src([('Boeing filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000012927&type=10-K')])),
        ('capital', 'Balance sheet', 'Heavy debt, <em>falling.</em>',
         prose('Debt is about $45.6 billion against $20.0 billion of cash in June, down from over $50 billion. Shareholders&rsquo; equity only recently turned positive after years of losses. The 2024 equity raise and asset sales were used to protect the investment-grade rating.')),
        ('value', 'Valuation', 'The model gives <em>$197 a share.</em>',
         prose('Boeing&rsquo;s profits are still distorted by the recovery, so the model works from a free cash flow path.')
         + table(['Assumption', 'Base case', 'Basis'], [
             ['Free cash flow, 2026&ndash;2030', '$2B, $6B, $9B, $10.5B, $11.5B', '2026 guidance, then production ramps toward 47&ndash;52 a month'],
             ['Then', 'Grows 6%, fading to 3% by year 10', 'Deliveries level off, then long-run economic growth'],
             ['Discount rate', '9.7%', 'Beta 1.35, about 23% debt at 6%'],
             ['Net debt', '$25.6B', 'June 30, 2026'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$76B'), ('PV of terminal value', '$105B'), ('Enterprise value', '$181B'), ('Less net debt', '$25.6B'), ('Equity value', '$156B'), ('Shares', '791M')], '$197')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Free cash flow by 2030', '$7.5B', '$11.5B', '$14B'], ['Discount rate', '10.7%', '9.7%', '8.7%'],
             ['Value per share', '$105', '$197', '$291'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$197</b>.') + sens('Discount rate', ['8.0%', '8.5%', '9.0%', '9.5%'], ['$280', '$251', '$226', '$205'])),
        ('implied', 'What the price assumes', 'At $190, <em>about $11 billion of cash by 2030.</em>',
         prose('The price implies free cash flow of roughly <b>$11 billion a year by 2030</b>, almost exactly the base case and close to the level Boeing reached before 2019. The market is pricing in a successful recovery, but not more than that.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Quality and the FAA', 'Any new incident could halt the production ramp again.'],
             ['Supply chain', 'Engines (787) and parts beyond 52 a month on the 737.'],
             ['Fixed-price defense programs', 'Air Force One and others have produced repeated charges.'],
             ['Labor', 'Engineering union talks ahead of an October contract expiry.'],
         ]) + prose('<b>Upside:</b> faster rate increases, the 737-7 and -10 certifications, and the 777X entering service in 2027.')),
        ('rec', 'Recommendation', 'Hold. <em>Fairly priced for the recovery.</em>',
         prose('At $190.47 against a base case of $197, Boeing is roughly fairly valued: the price assumes the turnaround works, no more. The call is <b>Hold</b>. The upside depends on beating the plan; a stumble on quality or production would hit the shares hard.')
         + '<div class="band sm"><div class="eyebrow mono">Final view</div><h2>The recovery is priced in. <em>Execution decides the rest.</em></h2><p>Demand is guaranteed by the backlog; Boeing has to build the planes.</p></div>'),
    ])
