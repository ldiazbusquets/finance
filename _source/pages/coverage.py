"""Reports on SpaceX and Firefly (holdings) and on OpenAI, Anthropic and Anduril (private, on the watchlist).
Written October 21, 2026. Scenario values come from _source/models/new_coverage.py."""
from rep import src, stats, table, prose, key, bridge, fin_table

DATE = 'October 21, 2026'


def scen(rows):
    return table(['', 'Bear', 'Base', 'Bull'], rows, 'allnum')


def implied(rows):
    return table(['To justify the price, you need', 'Against'], rows)


def band(h, p):
    return f'<div class="band sm"><div class="eyebrow mono">Final view</div><h2>{h}</h2><p>{p}</p></div>'


TOCP = [('overview', 'The business'), ('results', 'Latest results'), ('fin', 'The numbers'), ('capital', 'Balance sheet and ownership'),
        ('value', 'Valuation'), ('implied', 'What the price assumes'), ('risks', 'Risks'), ('rec', 'Recommendation')]
TOCV = [('overview', 'The business'), ('growth', 'Growth'), ('fin', 'The numbers'), ('capital', 'Funding and ownership'),
        ('value', 'Valuation'), ('implied', 'What the valuation assumes'), ('risks', 'Risks'), ('rec', 'Our view')]

R = {}

# ================================================================ SpaceX
SX = 'https://www.stocktitan.net/articles/spacex-q3-2026-earnings-ai-revenue-passes-starlink'
R['SPCX'] = dict(
    t='SPCX', slug='spacex', name='SpaceX', h1='Space<em>X</em>', sector='Space and AI', date=DATE, timing=', the day after its third-quarter results',
    sub='SpaceX is now three businesses: rockets, the Starlink satellite network, and since buying xAI, one of the largest AI computing operations in the world. Revenue grew 161% last quarter and AI has overtaken Starlink. The price assumes that growth keeps compounding for years.',
    call='Hold', method='Scenario model', price=162.57, pricenote='Midday, Oct 21, 2026', noauto=True, base=118, max=320, tick=40,
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the Street&rsquo;s average target.',
    field=[('Scenario model', 44, 270, 118, '$44 to $270, base $118'), ('Probability-weighted', None, None, 138, '$138'),
           ('Price at writing', None, None, 162.57, '$162.57'), ('52-week range', 105, 226, None, '$105 to $226'), ('Analyst average', None, None, 223, '$223')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Rockets, a satellite network <em>and an AI cloud.</em>',
         prose('<b>Space</b> is the original business: Falcon 9 and Falcon Heavy launches for NASA, the military and commercial customers, and Starship, the fully reusable rocket meant to cut launch costs by an order of magnitude. <b>Connectivity</b> is Starlink, internet from more than 9,000 satellites for homes, ships, airlines and phones. <b>Super Intelligence (SI)</b> came with the purchase of Elon Musk&rsquo;s xAI in February 2026: the Grok models, the X platform, the Cursor coding tool, and data centers that lease computing to other AI labs.',
               'SpaceX listed on Nasdaq as SPCX on June 12, 2026, at $135 a share, valuing it at about $1.77 trillion in the largest IPO on record.')
         + key('Takeaway', 'You now own an AI infrastructure company with a launch business and a telecom network attached. AI is already more than half of revenue.')),
        ('results', 'Latest results', 'Revenue up 161%, <em>and a first operating profit.</em>',
         stats([('$14.6B', 'Revenue, Q3 2026, +161%'), ('$7.6B', 'AI (SI) revenue, nearly triple Q2'), ('$5.2B', 'Starlink revenue, +69%'), ('$2.8B', 'Operating profit'), ('$19.6B', 'Capital spending in the quarter'), ('$33&ndash;37B', 'Q1 2027 revenue guidance')])
         + prose('Third-quarter revenue of $14.6 billion beat estimates by about $1.7 billion. SI revenue was $7.6 billion, including $608 million from Cursor, as Anthropic, Google and others rented its computing. Starlink added 1.6 million subscribers to reach 13.6 million, fewer than analysts expected, but its operating profit nearly doubled to $2.4 billion. Rockets earned $1.8 billion and roughly broke even.',
                 'Net income was $4.4 billion ($0.35 a share). Management guided first-quarter 2027 revenue to <b>$33&ndash;37 billion</b>, more than double this quarter, as computing capacity grows from 1.7 GW to about 3 GW by year-end. Starship reached orbit on Flight 14 and deployed V3 Starlink satellites. The shares rose about 10% the next day.')
         + src([('Q3 2026 results', SX), ('Earnings call summary', 'https://finance.biggo.com/news/US_SPCX_2026-10-20'), ('Fortune', 'https://fortune.com/2026/10/20/spacex-q3-profit-ai-si-elon-musk/')])),
        ('fin', 'The numbers', 'Profitable operations, <em>spending far more than it earns.</em>',
         table(['Segment, Q3 2026', 'Revenue', 'Growth', 'Operating profit'], [
             ['Super Intelligence (AI)', '$7.6B', '+~830%', '$0.4B ($1.6B before Cursor stock pay)'],
             ['Connectivity (Starlink)', '$5.2B', '+69%', '$2.4B'],
             ['Space (launch)', '$1.8B', '+6%', '&minus;$0.0B'],
             ['Company', '$14.6B', '+161%', '$2.8B'],
         ], 'mid')
         + prose('Over the first nine months of 2026, operations brought in $13.1 billion of cash, but capital spending was $48.1 billion, almost all of it AI data centers. Fourth-quarter capex is guided at $35&ndash;40 billion. Over the last twelve months revenue was about $23 billion and the company lost about $8.9 billion, because earlier quarters carried large losses.')),
        ('capital', 'Balance sheet and ownership', '$90 billion of cash, <em>and Musk in control.</em>',
         prose('SpaceX held $89.9 billion of cash and short-term investments against $38.8 billion of debt and leases in September, thanks to the IPO. Analysts expect debt to rise sharply as the data-center build continues.',
               'Musk owns about 42% of the shares but about 82% of the votes through ten-vote Class B shares, so public shareholders cannot change the strategy. Insiders are locked up for a year; other pre-IPO investors can start selling around <b>December 8</b>, which could add supply. Musk has also said a merger with Tesla is possible but not certain.')),
        ('value', 'Valuation', 'Our scenarios give <em>$118 a share.</em>',
         prose('A ten-year cash-flow model means little for a company whose revenue may triple in a year, so this report values SpaceX on its 2030 earning power: revenue, operating margin and a multiple, discounted back at 12% a year.')
         + scen([['Revenue in 2030', '$250B', '$500B', '$900B'], ['Operating margin', '22%', '28%', '32%'], ['Exit multiple of after-tax profit', '20&times;', '22&times;', '25&times;'],
                 ['Value per share', '$44', '$118', '$270'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25, the cases give <b>$138</b>. Net cash of about $51 billion and 13.57 billion shares are included.')),
        ('implied', 'What the price assumes', 'At $163, <em>about $700 billion of revenue by 2030.</em>',
         implied([['About $700 billion of revenue in 2030 at a 28% margin', 'About $23 billion over the last twelve months'], ['Or margins and multiples near the bull case', 'Base case of 28% and 22&times;']])
         + prose('That sounds extreme, but management is guiding to a $140 billion annual pace by early 2027 and has talked about $500 billion to $1 trillion by the end of 2027 if its AI business scales. The price sits between the base and bull cases: it needs the AI buildout to keep paying back as fast as management says, which is under a year per data center today.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['AI demand', 'Most growth is renting computing to AI labs. If their spending slows, SpaceX is left with expensive capacity and rising debt.'],
             ['Spending', 'Capex of $70 billion or more a year means negative free cash flow for some time.'],
             ['Governance', 'Musk controls the vote; a Tesla merger or other related-party deals could be on his terms.'],
             ['Lock-up', 'Pre-IPO investors can sell from early December.'],
             ['Execution', 'Starship, V3 satellites and new data centers all have to work on schedule.'],
         ]) + prose('<b>Upside:</b> Starlink Mobile (22 million monthly users), reusable Starship lowering costs for everything else, and AI revenue scaling as guided.')),
        ('rec', 'Recommendation', 'Hold. <em>A great asset at a full price.</em>',
         prose('At $162.57 against a base case of $118 ($138 weighted), the price already reaches toward the bull case. The business is extraordinary, but the valuation depends on AI growth that has only just started. The call is <b>Hold</b>, sized as a speculative position, with the December lock-up expiry as a possible better entry point.')
         + band('Own the rocket company. <em>Watch the AI bill.</em>', 'SpaceX&rsquo;s value now depends more on data centers than on rockets.')),
    ])

# ================================================================ Firefly
FF = 'https://finance.biggo.com/news/US_FLY_2026-08-11'
R['FLY'] = dict(
    t='FLY', slug='firefly', name='Firefly Aerospace', h1='Firefly <em>Aerospace</em>', sector='Space', date=DATE, timing=', before its third-quarter results in November',
    sub='Firefly builds small rockets, the Blue Ghost lunar lander and spacecraft for NASA and the Pentagon. Revenue is growing fast and the backlog is $1.5 billion, but it loses money and its Alpha rocket has a mixed record. The shares are down about 70% from their high.',
    call='Hold', method='Scenario model', price=17.41, pricenote='Midday, Oct 21, 2026', noauto=True, base=20, max=70, tick=10,
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Scenario model', 4, 52, 20, '$4 to $52, base $20'), ('Probability-weighted', None, None, 24, '$24'),
           ('Price at writing', None, None, 17.41, '$17.41'), ('52-week range', 16, 62, None, '$16 to $62'), ('Analyst average', None, None, 38, '$38')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Rockets, moon landers <em>and missile defense.</em>',
         prose('Firefly, based in Cedar Park, Texas, has four product lines. <b>Alpha</b> is a small rocket that carries about a ton to low orbit. <b>Blue Ghost</b> is a lunar lander: in March 2025 it made the first fully successful commercial landing on the Moon. <b>Elytra</b> is a spacecraft that can serve as a satellite or carry payloads around the Moon. <b>Eclipse</b>, a larger rocket built with Northrop Grumman, is due to fly no earlier than 2027. Its SciTec division adds defense software for missile warning, which gives Firefly a role in the Golden Dome missile-defense program.',
               'Firefly went public in August 2025 at $45 a share, raising $868 million at a valuation of about $10 billion.')),
        ('results', 'Latest results', 'First $100 million quarter, <em>record backlog.</em>',
         stats([('$117.7M', 'Revenue, Q2 2026, +659%'), ('$1.5B', 'Record backlog'), ('20.3%', 'Gross margin'), ('&minus;$61M', 'Adjusted EBITDA'), ('$940M', 'Liquidity, cash and credit line'), ('$420&ndash;450M', '2026 revenue guidance')])
         + prose('Second-quarter revenue reached $117.7 million, almost all from spacecraft work for NASA lunar missions and defense. Launch revenue was only $9.4 million, because Alpha flies rarely. Net loss was $92.3 million. Management kept 2026 revenue guidance at $420&ndash;450 million, with 95% of the midpoint already booked, and plans three Alpha launches this year, with Flight 8 in the fourth quarter.')
         + src([('Q2 2026 results summary', FF), ('Firefly investor news', 'https://investors.fireflyspace.com/news')])),
        ('fin', 'The numbers', 'Growth is real; <em>profit is years away.</em>',
         table(['', 'Value'], [['Revenue, last twelve months', '$287M'], ['Net loss, last twelve months', '&minus;$370M'], ['Gross margin, Q2 2026', '20.3%'],
                                ['Alpha flight record', '7 flights: 3 successes, 2 partial, 2 failures'], ['Blue Ghost', '1 landing, 1 success; Mission 2 and a far-side mission in development']], 'mid')
         + prose('Alpha&rsquo;s record is the weak point: a failure in April 2025 and an explosion during a ground test in September 2025 grounded it until a successful flight in March 2026. Launch is what would lift margins, so the cadence of Alpha flights matters more than any single contract.')),
        ('capital', 'Balance sheet and ownership', 'Enough cash, <em>with dilution along the way.</em>',
         prose('Firefly had $635 million of cash and an undrawn $305 million credit line in June. It has sold shares twice since the IPO, including an offering at $48 in May 2026, and registered shares for resale by former SciTec owners, which has weighed on the price. Expect more share sales before it turns profitable. AE Industrial Partners is the largest investor; Northrop Grumman invested $50 million alongside the Eclipse partnership.')),
        ('value', 'Valuation', 'Our scenarios give <em>$20 a share.</em>',
         prose('With no profits yet, this report values Firefly on its 2030 revenue and the multiple of sales a profitable space company would command, discounted back at 15% a year, with more shares outstanding to fund the losses until then.')
         + scen([['Revenue in 2030', '$0.7B', '$1.2B', '$2.0B'], ['Exit value to sales', '2&times;', '5&times;', '8&times;'], ['Shares by 2030', '200M', '185M', '180M'],
                 ['Value per share', '$4', '$20', '$52'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$24</b>. The range is wide on purpose: this is a company where one failed launch or one large contract changes the answer.')),
        ('implied', 'What the price assumes', 'At $17, <em>about $1 billion of revenue by 2030.</em>',
         implied([['About $1.06 billion of revenue in 2030 at 5&times; sales', '$420&ndash;450 million guided for 2026'], ['Roughly 25% annual growth from here', '659% last quarter, from a small base']])
         + prose('The market now prices Firefly slightly below the base case, a big change from the $62 high, when it priced something close to the bull case.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Launch failures', 'Alpha has failed or partly failed four times in seven flights.'],
             ['Losses and dilution', 'About $370 million lost in the last year; more share sales are likely.'],
             ['Competition', 'SpaceX rideshares undercut small rockets; Rocket Lab is further ahead.'],
             ['Government budgets', 'NASA and defense contracts drive most revenue.'],
         ]) + prose('<b>Upside:</b> Golden Dome and missile-warning work through SciTec, more NASA lunar missions, and Eclipse giving Firefly a medium rocket in 2027.')),
        ('rec', 'Recommendation', 'Hold. <em>Speculative, and priced like it.</em>',
         prose('At $17.41 against a base case of $20 ($24 weighted), the price is close to fair for a business this uncertain, after a 70% fall. The call is <b>Hold</b>, kept within the speculative part of the portfolio. Alpha Flight 8 and the third-quarter results in November are the next tests.')
         + band('A real business, <em>a risky stock.</em>', 'The backlog is strong; the rocket record and the cash burn decide the outcome.')),
    ])

# ================================================================ private companies
PRIV = 'This company is private, so there is no share price; values are for the whole company. The author holds no shares.'

R['ANTHROPIC'] = dict(
    t='ANTHROPIC', slug='anthropic', name='Anthropic', h1='Anthropic', sector='AI (private)', date=DATE, timing=', ahead of its expected IPO in mid-November',
    sub='Anthropic makes Claude, the AI models used by businesses and developers. Revenue has grown more than tenfold in a year and the company is preparing what could be one of the largest IPOs ever. This report asks what it is worth, and what price would make sense to buy at.',
    call='IPO watch', private=True, price=965, base=847, max=2200, tick=250, suffix='B',
    disclosure=PRIV + ' This report was drafted with help from Claude, an AI model made by Anthropic.',
    cells=[('Last private valuation', '$965B', 'Series H, May 2026'), ('Revenue, Q3 2026', '$16.8B', 'Up 45% from Q2, reported'), ('Model value', '$847B', 'Base case; $972B weighted')],
    fieldnote='Company values in billions: the scenario model&rsquo;s range, the probability-weighted value, the last private round and the valuations discussed for the IPO.',
    field=[('Scenario model', 163, 2033, 847, '$163B to $2,033B, base $847B'), ('Probability-weighted', None, None, 972, '$972B'),
           ('Series H, May 2026', None, None, 965, '$965B'), ('IPO talk', 1500, 2000, None, '$1.5T to $2T')],
    toc=TOCV, chapters=[
        ('overview', 'The business', 'Claude, sold mostly <em>to businesses.</em>',
         prose('Anthropic was founded in 2021 by Dario and Daniela Amodei and other former OpenAI researchers. It sells access to its Claude models through its own apps and API and through Amazon Web Services and Google Cloud. Most revenue comes from businesses and developers rather than consumers, led by coding: Claude Code has become one of its largest products.',
               'It is a public benefit corporation, and an independent Long-Term Benefit Trust holds a special class of shares with the right to elect directors, a structure meant to keep safety ahead of short-term profit.')),
        ('growth', 'Growth', '$4.6 billion last year, <em>$16.8 billion last quarter.</em>',
         stats([('~$4.6B', 'Revenue, 2025 (leaked draft S-1)'), ('$4.8B', 'Revenue, Q1 2026'), ('~$11.6B', 'Revenue, Q2 2026'), ('$16.8B', 'Revenue, Q3 2026, +45%'), ('$65B+', 'Annual run-rate by July'), ('Mid-Nov', 'Expected IPO')])
         + prose('Revenue has grown faster than at almost any company of its size. Third-quarter revenue of $16.8 billion, reported by Bloomberg and the Financial Times from investor presentations, was up 45% from the second quarter, but some investors noted that monthly growth is slowing. OpenAI has argued that Anthropic counts sales through cloud partners at their gross value, which flatters the comparison; the public S-1 will settle how revenue is reported.')
         + src([('Bloomberg: Q3 revenue', 'https://www.bloomberg.com/news/articles/2026-10-14/anthropic-revenue-jumps-to-16-8-billion-in-quarter-before-ipo'), ('IPO status', 'https://decodethefuture.org/en/anthropic-s1-ipo-filing-explained/'), ('Reuters via Manila Times', 'https://www.manilatimes.net/2026/10/21/business/foreign-business/openai-raising-funds-before-anthropic-ipo/2450125')])),
        ('fin', 'The numbers', 'Profitable operations, <em>enormous commitments.</em>',
         table(['', 'Figure', 'Status'], [['Operating loss, 2025', 'About $8B', 'Leaked draft S-1'], ['Net loss, 2025', 'About $42B, mostly non-cash', 'Leaked draft S-1'],
                                          ['Operating profit, Q2 2026', 'About $0.6B, adjusted', 'Reported'], ['Compute commitments', 'About $518B, mostly non-cancellable', 'Reported'],
                                          ['Cash-flow breakeven', '2028', 'Reported target']])
         + prose('Anthropic reached an adjusted operating profit in the second quarter, rare for an AI lab, but it has committed to more than half a trillion dollars of computing with Amazon, Google, SpaceX and others. Those contracts are the main risk if growth slows. None of these figures is audited yet; the public S-1 will be the first full set.')),
        ('capital', 'Funding and ownership', 'Valued at $965 billion <em>in May.</em>',
         prose('The last private round was a $65 billion Series H at a $965 billion valuation in May 2026. Amazon owns an estimated 15&ndash;21% (non-voting) and Google about 14%. A confidential S-1 was submitted on June 1; the listing is expected on Nasdaq in mid-November, led by Morgan Stanley, Goldman Sachs, JPMorgan and Citi. Investors have discussed valuations from about $1.5 trillion to $2 trillion.')),
        ('value', 'Valuation', 'Our scenarios give <em>about $850 billion.</em>',
         prose('This report values the company on 2030 earning power: revenue, operating margin and a multiple of after-tax profit, discounted back at 15% a year to reflect the risk of a young business. It does not deduct the new shares that may be issued to fund the buildout.')
         + scen([['Revenue in 2030', '$120B', '$250B', '$450B'], ['Operating margin', '15%', '30%', '40%'], ['Exit multiple', '20&times;', '25&times;', '25&times;'],
                 ['Company value today', '$163B', '$847B', '$2.03T'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>about $970 billion</b>, almost exactly the May round.')),
        ('implied', 'What the valuation assumes', 'At $2 trillion, <em>almost $600 billion of revenue.</em>',
         implied([['$965B (May round): about $285B of revenue in 2030 at a 30% margin', 'About $67B annualised today'], ['$1.5T: about $445B', ''], ['$2T: about $590B', 'Close to the bull case']])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Competition', 'OpenAI, Google and open models compete on price; model leads are short.'],
             ['Commitments', 'About $518B of compute contracts must be paid even if growth slows.'],
             ['Concentration', 'Amazon and Google channels were about half of 2025 revenue.'],
             ['Governance', 'The Benefit Trust and founder voting control limit shareholders&rsquo; say.'],
             ['IPO pricing', 'A $1.5&ndash;2T listing would leave little room for error.'],
         ]) + prose('<b>Upside:</b> AI agents and coding tools growing into a large share of software spending, with margins rising as computing gets cheaper.')),
        ('rec', 'Our view', 'Wait for the price, <em>not the date.</em>',
         prose('The business supports roughly the May valuation, about $1 trillion. A listing at $1.5&ndash;2 trillion would price in close to the bull case on day one. That supports the plan to wait for a post-IPO dip: an entry near $1&ndash;1.2 trillion would leave room for things to go only moderately right.')
         + band('The fastest-growing software company, <em>if the price is right.</em>', 'Buy the business at a valuation the base case supports, not at the IPO&rsquo;s first price.')),
    ])

R['OPENAI'] = dict(
    t='OPENAI', slug='openai', name='OpenAI', h1='Open<em>AI</em>', sector='AI (private)', date=DATE, timing='',
    sub='OpenAI makes ChatGPT, used by more than a billion people a week. It is the most valuable private company in AI and is raising money at about $1.4 trillion, but it also expects to burn hundreds of billions of dollars before it turns a profit. An IPO is planned for 2027.',
    call='Watch', private=True, price=852, base=790, max=2000, tick=250, suffix='B', disclosure=PRIV,
    cells=[('Last valuation', '$852B', '$122B round, March 2026'), ('Annual revenue pace', '$50B', 'Company figure, October'), ('Model value', '$790B', 'Base case; $874B weighted')],
    fieldnote='Company values in billions: the scenario model&rsquo;s range, the probability-weighted value, the March round and the round now being discussed.',
    field=[('Scenario model', 136, 1779, 790, '$136B to $1,779B, base $790B'), ('Probability-weighted', None, None, 874, '$874B'),
           ('March 2026 round', None, None, 852, '$852B'), ('Round in talks', None, None, 1400, '$1.4T')],
    toc=TOCV, chapters=[
        ('overview', 'The business', 'ChatGPT, <em>and everything built on it.</em>',
         prose('OpenAI sells ChatGPT subscriptions to consumers and businesses, API access to developers, and since 2026 advertising inside ChatGPT. It converted from a capped-profit structure into a public benefit corporation, OpenAI Group PBC, in October 2025. The nonprofit OpenAI Foundation controls it and owns about a quarter; Microsoft owns about 27%.')),
        ('growth', 'Growth', 'A billion users, <em>$50 billion a year.</em>',
         stats([('$3.7B', 'Revenue, 2024'), ('$13.1B', 'Revenue, 2025'), ('$6.7B', 'Revenue, Q2 2026'), ('$50B', 'Annual pace, October (company)'), ('1B+', 'Weekly ChatGPT users'), ('$1B', 'Advertising run-rate, August')])
         + prose('OpenAI says its annual revenue pace reached $50 billion after the launch of its newest model and expects $70 billion by year-end. It books revenue net of the share paid to partners such as Microsoft, which makes its figures look smaller than Anthropic&rsquo;s on a like-for-like basis. Growth stalled for several months in early 2026 before picking up again.')
         + src([('Reuters via Manila Times', 'https://www.manilatimes.net/2026/10/21/business/foreign-business/openai-raising-funds-before-anthropic-ipo/2450125'), ('Financial fact sheet', 'https://www.useluminix.com/reports/company-overviews/openai-financial-fact-sheet-june-2026')])),
        ('fin', 'The numbers', 'Big revenue, <em>bigger losses.</em>',
         table(['', 'Figure', 'Status'], [['Operating loss, 2025', 'About $21B', 'Leaked financials'], ['Expected cash burn, 2026&ndash;2030', 'About $278B in total', 'Leaked plan'],
                                          ['Compute plans', 'About $856B through 2030 (Azure, Oracle, Stargate)', 'Reported'], ['Profit', 'Not expected before 2029&ndash;2030', 'Reported plans']])
         + prose('OpenAI spends far more on computing than it earns. Its plan relies on partners (Microsoft, Oracle, SoftBank&rsquo;s Stargate venture) financing much of the infrastructure, and on raising new money roughly every year until revenue catches up.')),
        ('capital', 'Funding and ownership', '$852 billion in March, <em>$1.4 trillion in talks.</em>',
         prose('In March 2026 OpenAI closed a $122 billion round at $852 billion, anchored by Amazon ($50 billion), Nvidia ($30 billion) and SoftBank ($30 billion). In October it was reported to be raising about $30 billion more at a valuation above $1.4 trillion, before Anthropic&rsquo;s IPO. Sam Altman has said listing in 2026 would be ill-advised; the IPO is expected in 2027.')),
        ('value', 'Valuation', 'Our scenarios give <em>about $790 billion.</em>',
         prose('Valued on 2030 earning power and discounted at 15% a year, before the new shares OpenAI will issue to cover its cash burn, which would lower each existing share&rsquo;s value.')
         + scen([['Revenue in 2030', '$150B', '$280B', '$450B'], ['Operating margin', '10%', '25%', '35%'], ['Exit multiple', '20&times;', '25&times;', '25&times;'],
                 ['Company value today', '$136B', '$790B', '$1.78T'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>about $870 billion</b>, close to the March round.')),
        ('implied', 'What the valuation assumes', 'At $1.4 trillion, <em>about $500 billion of revenue.</em>',
         implied([['$852B: about $300B of revenue in 2030 at a 25% margin', 'About $50B annualised today'], ['$1.4T: about $500B', 'Above the base case']])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Cash burn', 'Hundreds of billions to fund before profit; each round dilutes.'],
             ['Competition', 'Anthropic leads in business and coding; Google bundles AI free.'],
             ['Partners', 'Microsoft is an investor, supplier and competitor at once.'],
             ['Governance', 'The nonprofit foundation controls the company.'],
         ]) + prose('<b>Upside:</b> the largest consumer AI audience, advertising, devices and agents could make ChatGPT the main way people use the internet.')),
        ('rec', 'Our view', 'Not investable yet; <em>fair near $850 billion.</em>',
         prose('Until the 2027 IPO there is no way to buy OpenAI directly. The base case supports roughly the March valuation; the $1.4 trillion round prices in more than the base case. Indirect exposure already comes through Microsoft, Nvidia, Oracle and Amazon.')
         + band('The biggest audience in AI, <em>the biggest bill.</em>', 'Its value depends on turning a billion users into profit before the money runs out.')),
    ])

R['ANDURIL'] = dict(
    t='ANDURIL', slug='anduril', name='Anduril', h1='Anduril', sector='Defense (private)', date=DATE, timing='',
    sub='Anduril builds autonomous drones, missiles and the software that links them, and sells them to the U.S. military and its allies. Revenue is roughly doubling every year and it is valued at about $90 billion, priced more like a software company than a defense contractor. An IPO is expected around 2027.',
    call='Wait for IPO', private=True, price=90, base=20, max=110, tick=10, suffix='B', disclosure=PRIV,
    cells=[('Latest valuation', '$90B', 'Employee tender, October 2026'), ('Revenue, 2026 guidance', '$4.3B', 'Up from $2.2B in 2025'), ('Model value', '$20B', 'Base case; $28B weighted')],
    fieldnote='Company values in billions: the scenario model&rsquo;s range, the probability-weighted value, the May round and the October employee tender.',
    field=[('Scenario model', 4, 67, 20, '$4B to $67B, base $20B'), ('Probability-weighted', None, None, 28, '$28B'),
           ('Series H, May 2026', None, None, 61, '$61B'), ('Employee tender, Oct', None, None, 90, '$90B')],
    toc=TOCV, chapters=[
        ('overview', 'The business', 'Weapons built <em>like tech products.</em>',
         prose('Anduril was founded in 2017 by Palmer Luckey, Trae Stephens, Brian Schimpf (now CEO) and others. It designs and builds its own products and sells them, rather than waiting for the Pentagon to fund development. Its range includes the <b>Fury</b> collaborative combat aircraft, <b>Roadrunner</b> reusable interceptors, <b>Barracuda</b> low-cost cruise missiles, <b>Ghost Shark</b> underwater drones and surveillance towers, all linked by <b>Lattice</b>, its AI command software.',
               'Production is moving to <b>Arsenal-1</b>, a plant of nearly $1 billion in Ohio designed to build up to 150 Fury aircraft a year.')),
        ('growth', 'Growth', '$236 million in 2022, <em>$4.3 billion planned for 2026.</em>',
         stats([('$1.0B', 'Revenue, 2024'), ('$2.2B', 'Revenue, 2025'), ('~$4.3B', '2026 guidance'), ('Up to $20B', 'Army enterprise agreement, 10 years'), ('A$1.7B', 'Ghost Shark, Australia'), ('$1.98B', 'Kuwait counter-drone sale')])
         + prose('Revenue has roughly doubled every year. In March 2026 the U.S. Army signed an enterprise agreement worth up to $20 billion over ten years that consolidates more than 120 contracts. Anduril is still loss-making: it guided to an operating loss of about $1.2 billion in 2026 as it builds factories.')
         + src([('Revenue and contracts', 'https://valueaddvc.com/blog/anduril-revenue-2-2b-in-2025-4-3b-2026-guidance-and-the-contract-breakdown'), ('May 2026 round', 'https://siliconangle.com/2026/05/13/anduril-doubles-valuation-61b-new-5b-funding-round/'), ('Employee tender', 'https://valueaddvc.com/blog/anduril-valuation-2026-90b-employee-tender-100b-talks')])),
        ('fin', 'The numbers', 'Fast growth, <em>still losing money.</em>',
         table(['', '2022', '2023', '2024', '2025', '2026 guidance'], [['Revenue', '$0.24B', '$0.42B', '$1.0B', '$2.2B', '~$4.3B']], 'allnum')
         + prose('Anduril does not publish full financial statements. The reported 2026 operating loss of about $1.2 billion reflects heavy spending on Arsenal-1 and new products; management has pointed to operating breakeven later in the decade.')),
        ('capital', 'Funding and ownership', '$14 billion to $90 billion <em>in two years.</em>',
         prose('Anduril was valued at $14 billion in August 2024, $30.5 billion in June 2025 and $61 billion in May 2026, when it raised $5 billion led by Thrive Capital and Andreessen Horowitz. An employee share sale that opened on October 13 values it at $90 billion ($94.80 a share). Talks about a round near $100 billion were reported in July but not confirmed. No S-1 has been filed.')),
        ('value', 'Valuation', 'Our scenarios give <em>about $20 billion.</em>',
         prose('Valued on 2030 earning power and discounted at 13% a year. The bull case gives it Palantir-like margins and a 35&times; multiple.')
         + scen([['Revenue in 2030', '$8B', '$14B', '$22B'], ['Operating margin', '5%', '12%', '18%'], ['Exit multiple', '20&times;', '25&times;', '35&times;'],
                 ['Company value today', '$4B', '$20B', '$67B'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>about $28 billion</b>, well below where private investors value it.')),
        ('implied', 'What the valuation assumes', 'At $90 billion, <em>a software company&rsquo;s economics.</em>',
         implied([['At defense-contractor margins (12%): about $62B of revenue in 2030', '$4.3B guided for 2026'], ['At software-like margins (25%) and a 35&times; multiple: about $21B', 'The bull case']])
         + prose('Private investors are paying for growth well beyond 2030, and for the chance that Anduril becomes a new prime contractor with software margins. Traditional defense primes such as L3Harris trade at a fraction of that multiple.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Valuation', 'At about 21&times; 2026 revenue it is priced far above any defense company.'],
             ['Budgets', 'Almost all revenue depends on U.S. and allied defense spending.'],
             ['Execution', 'Arsenal-1 and Fury production must ramp on time.'],
             ['Competition', 'Lockheed, RTX, General Atomics, Shield AI and Saronic all chase the same programs.'],
         ]) + prose('<b>Upside:</b> the Army agreement, collaborative combat aircraft orders and exports could keep revenue doubling.')),
        ('rec', 'Our view', 'A great company <em>priced for perfection.</em>',
         prose('Anduril is growing like a top software company, but our scenarios value it far below the $61&ndash;90 billion private marks. For the plan to buy on IPO day, the numbers argue for patience: early public prices are likely to start from those marks, and the base case does not support them. L3Harris, rated Buy in its own report, offers defense exposure at a much lower price in the meantime.')
         + band('Watch it, <em>don&rsquo;t chase it.</em>', 'The business is excellent; the valuation already assumes it stays that way for a decade.')),
    ])

# ================================================================ Kratos (watchlist, not held)
KQ = 'https://www.stocktitan.net/news/KTOS/kratos-reports-second-quarter-2026-financial-iz9i8yyotxfi.html'
R['KTOS'] = dict(
    t='KTOS', slug='kratos', name='Kratos Defense', h1='Kratos <em>Defense</em>', sector='Defense', date=DATE, timing=', ahead of its third-quarter results in early November',
    sub='Kratos makes low-cost drones, hypersonic test rockets, small jet engines and satellite ground systems. It is the closest listed company to Anduril. Revenue is growing about 20% a year, but the shares are down more than 70% from their January high because the price had run far ahead of the profits.',
    call='Watch', method='Scenario model', price=38.81, pricenote='Midday, Oct 21, 2026', noauto=True, base=23, max=140, tick=20,
    disclosure='The author holds no KTOS shares.',
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Scenario model', 14, 42, 23, '$14 to $42, base $23'), ('Probability-weighted', None, None, 26, '$26'),
           ('Price at writing', None, None, 38.81, '$38.81'), ('52-week range', 38, 134, None, '$38 to $134'), ('Analyst average', None, None, 98, '$98')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Cheap drones, rockets <em>and engines.</em>',
         prose('Kratos, based in San Diego, sells to the Pentagon in two segments. <b>Government Solutions</b> (about 83% of revenue) includes hypersonic and rocket systems such as Zeus and Erinyes, small turbojet and turbofan engines for missiles and drones, microwave electronics, and satellite ground networks. <b>Unmanned Systems</b> builds target drones and the <b>XQ-58 Valkyrie</b>, a low-cost jet drone designed to fly alongside crewed fighters, which the Marine Corps is buying.',
               'Its strategy is the same as Anduril&rsquo;s: spend its own money to build cheap, &ldquo;attritable&rdquo; weapons before the government asks for them. The difference is that Kratos is public, so you can see the cost of that strategy every quarter.')),
        ('results', 'Latest results', 'Revenue up 31%, <em>guidance raised, cash still going out.</em>',
         stats([('$458.8M', 'Revenue, Q2 2026, +30.5%'), ('19.1%', 'Organic growth'), ('$38.2M', 'Adjusted EBITDA, 8.3% margin'), ('$2.08B', 'Backlog'), ('$15.0B', 'Bid pipeline'), ('$1.75&ndash;1.81B', '2026 revenue guidance, raised')])
         + prose('Second-quarter revenue beat guidance, led by rocket systems (+50% organic) and engines (+43%). Net income was only $4.4 million ($0.02 a share) and the company had a small operating loss, because it is spending heavily on new factories. Management raised 2026 revenue guidance to $1.75&ndash;1.81 billion and expects free cash flow of <b>minus $85&ndash;105 million</b> this year, with $250&ndash;275 million of investment, including the Prometheus rocket-motor joint venture and capacity for about 40 Valkyries a year from 2028.')
         + src([('Q2 2026 results', KQ), ('Earnings call', 'https://www.fool.com/earnings/call-transcripts/2026/08/11/kratos-ktos-q2-2026-earnings-call-transcript/')])),
        ('fin', 'The numbers', 'Fast growth, <em>thin profit.</em>',
         table(['', 'Value'], [['Revenue, last twelve months', '$1.52B (+25%)'], ['Net income, last twelve months', '$31M'], ['Adjusted EBITDA guidance, 2026', '$173&ndash;176M (about 10%)'],
                                ['Free cash flow guidance, 2026', '&minus;$85 to &minus;105M'], ['Stock-based pay guidance, 2026', '$60&ndash;64M'], ['Trailing P/E', 'About 230&times;']], 'mid')
         + prose('Margins are low because much of the work is cost-plus or fixed-price government contracting and because development spending runs through the income statement. Management expects the 2027 EBITDA margin to rise about one percentage point; 2027 guidance comes with the third-quarter results.')),
        ('capital', 'Balance sheet and ownership', '$1.4 billion of cash, <em>paid for with new shares.</em>',
         prose('Kratos held $1.44 billion of cash in June and almost no borrowings beyond about $140 million of finance leases, after raising roughly $1 billion by selling stock earlier in 2026. The share count is about 188 million. The cash covers the factory build-out, but stock-based pay of about $60 million a year keeps adding shares.')),
        ('value', 'Valuation', 'Our scenarios give <em>$23 a share.</em>',
         prose('Valued the same way as the other fast-growing companies here: 2030 revenue, operating margin after stock pay, and a multiple of after-tax profit, discounted back at 10% a year (Kratos&rsquo;s cost of equity from its beta of about 1.1).')
         + scen([['Revenue in 2030', '$2.6B', '$3.2B', '$4.0B'], ['Operating margin', '6%', '9%', '12%'], ['Exit multiple', '18&times;', '22&times;', '28&times;'],
                 ['Value per share', '$14', '$23', '$42'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$26</b>. Net cash of about $1.2 billion and 200 million shares by 2030 are included. The base case already assumes revenue grows about 16% a year and the operating margin more than triples.')),
        ('implied', 'What the price assumes', 'At $39, <em>about $6 billion of revenue by 2030.</em>',
         implied([['About $6.1 billion of revenue in 2030 at the base margin and multiple', '$1.75&ndash;1.81 billion guided for 2026'], ['Or roughly 35% growth a year for four years', '18&ndash;23% organic growth guided']])
         + prose('Even after a 70% fall, the price sits near the bull case. At the January high of $134 it implied revenue several times larger. The analysts&rsquo; average target of $98 assumes faster growth and higher margins than this model does.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Valuation', 'Still about 4&times; sales and 40&times; next year&rsquo;s earnings for a contractor with 10% EBITDA margins.'],
             ['Cash burn and dilution', 'Negative free cash flow and heavy stock pay; another share sale is possible.'],
             ['Program wins', 'The Air Force&rsquo;s main collaborative combat aircraft awards went to rivals; Valkyrie depends on the Marines and new customers.'],
             ['Competition', 'Anduril, General Atomics and the large primes chase the same drone and missile budgets.'],
         ]) + prose('<b>Upside:</b> hypersonic testing, engines for low-cost cruise missiles, a second-source role on JASSM, Golden Dome and a larger Valkyrie order could all lift growth.')),
        ('rec', 'Recommendation', 'Watch. <em>Not an Anduril substitute at this price.</em>',
         prose('Kratos is a real, growing business with many of the same products as Anduril, but at $38.81 it trades well above our base case of $23 ($26 weighted) and earns very little today. Your earlier instinct to skip it still holds on the numbers. A price in the mid-$20s, or proof that margins are rising in the 2027 guidance, would change the view.')
         + band('Same idea as Anduril, <em>at a fraction of the margin.</em>', 'Revenue growth is real; the profits that would justify the price are not here yet.')),
    ])

# ================================================================ Bloomberg LP (private)
SEM = 'https://www.semafor.com/article/07/28/2026/bloombergs-post-mike-moves-are-in-motion'
R['BLOOMBERG'] = dict(
    t='BLOOMBERG', slug='bloomberg', name='Bloomberg LP', h1='Bloomberg <em>LP</em>', sector='Financial data (private)', date=DATE, timing='',
    sub='Bloomberg LP rents the Terminal to more than 300,000 finance professionals and runs one of the world&rsquo;s largest newsrooms. It has never published its financials. In July it held early talks with bankers about an IPO or a stake sale, while saying Michael Bloomberg has no plans to sell.',
    call='IPO watch', private=True, price=80, base=62, max=110, tick=10, suffix='B', disclosure=PRIV,
    cells=[('Bankers&rsquo; estimate', '$80B+', 'Reported by Semafor, July 2026'), ('Revenue', '~$15B', 'Outside estimates, not disclosed'), ('Model value', '$62B', 'Base case; $64B weighted')],
    fieldnote='Company values in billions: the scenario model&rsquo;s range, the probability-weighted value, bankers&rsquo; estimate and the price Bloomberg paid to buy back Merrill Lynch&rsquo;s stake in 2008.',
    field=[('Scenario model', 35, 96, 62, '$35B to $96B, base $62B'), ('Probability-weighted', None, None, 64, '$64B'),
           ('Bankers&rsquo; estimate', None, None, 80, '$80B'), ('Merrill buyback, 2008', None, None, 22, '$22B')],
    toc=TOCV, chapters=[
        ('overview', 'The business', 'The Terminal, <em>and everything around it.</em>',
         prose('Founded in 1981 to sell bond prices to traders, Bloomberg LP now makes most of its money from the <b>Terminal</b>, which costs about $30,000 a year per user and is found on almost every trading desk. Around it sit enterprise data feeds, indices, trading and risk software, and <b>Bloomberg Media</b>: Bloomberg News (about 2,700 journalists), Businessweek, television, radio and Bloomberg.com.',
               'The pieces reinforce each other: the news makes the Terminal more useful, and Terminal revenue pays for the newsroom. Decades of proprietary prices and articles are also valuable training data for AI models, which is one reason an AI lab or exchange could want a stake.')),
        ('growth', 'Growth', 'About $15 billion of revenue, <em>growing slowly and steadily.</em>',
         stats([('~$15B', 'Annual revenue (Forbes)'), ('~74%', 'Share from Terminals (BCG Expand)'), ('~67%', 'Share of the terminal market'), ('300,000+', 'Terminal users'), ('~$30,000', 'Price per Terminal per year'), ('~26,000', 'Employees')])
         + prose('Bloomberg does not report results, so all figures are outside estimates. Revenue has grown slowly for years, mostly through annual price increases rather than more users. The Terminal&rsquo;s closest rival is LSEG&rsquo;s Workspace (formerly Refinitiv Eikon); FactSet, S&amp;P Global and newer AI research tools compete in parts of the market.')
         + src([('Semafor, July 2026', SEM), ('Bloomberg&rsquo;s response', 'https://www.thewrap.com/industry-news/business/bloomberg-responds-semafor-ipo-report/'), ('IPO explainer', 'https://www.forex.com/en-us/news-and-analysis/bloomberg-ipo-everything-you-need-to-know-about-bloomberg/')])),
        ('fin', 'The numbers', 'Almost nothing <em>is public.</em>',
         table(['', 'Figure', 'Status'], [['Revenue', 'About $14.4&ndash;15B', 'Outside estimates'], ['Profit margins', 'Not disclosed; widely described as highly profitable', 'Unknown'],
                                          ['Debt', 'Not disclosed', 'Unknown'], ['Terminal renewal rate', 'Not disclosed', 'Unknown']])
         + prose('A prospectus would be the first look at margins, renewal rates and how much the newsroom costs. Those numbers decide the value far more than any estimate here.')),
        ('capital', 'Funding and ownership', 'Owned 88% <em>by its founder.</em>',
         prose('Michael Bloomberg, now 84, owns an estimated 88% and has said the company will eventually pass to Bloomberg Philanthropies. He recently moved some shares to the foundation, which would reduce taxes if the company listed or sold a stake. In 2008 Bloomberg bought back Merrill Lynch&rsquo;s 20% stake for $4.4 billion, which valued the whole company at about $22 billion.',
               'In July 2026 Semafor reported early, informal talks with bankers about an IPO or another transaction. The company replied that &ldquo;Mike controls the firm&rdquo; and has no plans to sell. There is no filing, date or exchange. A minority stake sold to an AI lab, exchange or asset manager is as likely as a public listing, and might never reach retail investors.')
         + src([('Merrill Lynch buyback, 2008', 'https://www.willkie.com/news/2008/07/willkie-advises-bloomberg-in-buyback-agreement-w__')])),
        ('value', 'Valuation', 'Our scenarios give <em>about $62 billion.</em>',
         prose('A mature, stable business, so a lower discount rate than the other private companies: 9% a year. Margins are an assumption, because Bloomberg has never disclosed them.')
         + scen([['Revenue in 2030', '$16B', '$18B', '$20B'], ['Operating margin', '22%', '28%', '33%'], ['Exit multiple', '18&times;', '22&times;', '26&times;'],
                 ['Company value today', '$35B', '$62B', '$96B'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>about $64 billion</b>. The multiple matters most. Quality data companies such as S&amp;P Global and MSCI have often traded near 30&times; earnings; at 30&times; the base case gives about <b>$85 billion</b>.')),
        ('implied', 'What the valuation assumes', 'At $80 billion, <em>a premium multiple or faster growth.</em>',
         implied([['$80B: about $23B of revenue in 2030 at a 28% margin and 22&times;', 'About $15B today'], ['Or the base case at about 28&times; earnings', 'Near what top data companies trade at']])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['No deal', 'Bloomberg says there are no plans to sell; it may never list.'],
             ['Retail access', 'A stake sale to an AI lab or exchange would leave nothing for individual investors.'],
             ['Control', 'Even after a listing, the founder and foundation would likely control the vote.'],
             ['AI tools', 'Cheaper AI research tools could slow Terminal price increases.'],
             ['Unknown numbers', 'Margins, debt and renewal rates are unpublished.'],
         ]) + prose('<b>Upside:</b> pricing power, recurring revenue and a data archive that AI developers would pay to use.')),
        ('rec', 'Our view', 'A KO-like business, <em>but price still matters.</em>',
         prose('Your view that Bloomberg is a buy-and-hold business, more like Coca-Cola or Costco than SpaceX, fits what is known: dominant, recurring and slow-changing. Even so, the IPO price decides the return. Near the $80 billion bankers mention, the base case needs a multiple close to the best data companies, which is fair but not cheap. Much above $100 billion it would assume the bull case. The prospectus&rsquo;s margins and renewal rates are the numbers to read first.')
         + band('The Coca-Cola of financial data, <em>if it ever lists.</em>', 'Worth owning at a fair price; there is no deal yet.')),
    ])

# ================================================================ Axon (watchlist, not held)
AQ = 'https://investor.axon.com/2026-08-05-Axon-reports-Q2-2026-revenue-of-904-million,-up-35-year-over-year'
R['AXON'] = dict(
    t='AXON', slug='axon', name='Axon Enterprise', h1='Axon', sector='Public safety technology', date=DATE, timing=', ahead of its third-quarter results on November 3',
    sub='Axon makes the TASER, the body cameras most U.S. police wear, and the cloud software that stores and analyses the video. It is now adding AI on top: report writing, transcription and real-time translation through the camera. Revenue has grown more than 30% for ten straight quarters, yet the shares are down about half from their 2025 peak.',
    call='Watch', method='Scenario model', price=396.30, pricenote='Midday, Oct 21, 2026', base=289, max=800, tick=100,
    disclosure='The author holds no AXON shares.',
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Scenario model', 132, 531, 289, '$132 to $531, base $289'), ('Probability-weighted', None, None, 310, '$310'),
           ('Price at writing', None, None, 396.30, '$396.30'), ('52-week range', 339, 764, None, '$339 to $764'), ('Analyst average', None, None, 691, '$691')],
    toc=[('overview', 'The business'), ('results', 'Latest results'), ('fin', 'Five years'), ('ai', 'The translation thesis'), ('value', 'Valuation'), ('implied', 'What the price assumes'), ('risks', 'Risks'), ('rec', 'Recommendation')], chapters=[
        ('overview', 'The business', 'Devices that feed <em>a software subscription.</em>',
         prose('Axon sells two things. <b>Connected Devices</b> (56% of revenue) are TASER energy weapons, Axon Body cameras, in-car and fixed cameras, drones and, since buying Dedrone in 2024, counter-drone systems. <b>Software &amp; Services</b> (44%) is Axon Evidence, the cloud where agencies store and share footage, plus records, dispatch and AI tools. Devices are sold inside five- to ten-year bundles, so about 95% of revenue is tied to subscription plans and customers rarely switch.',
               'The <b>AI Era Plan</b>, an add-on of about $199 per officer a year, includes Draft One (police reports written from camera audio), transcription and <b>real-time translation</b>. Revenue from it grew almost 700% in the past year.')),
        ('results', 'Latest results', 'Revenue up 35%, <em>margins under pressure.</em>',
         stats([('$904M', 'Revenue, Q2 2026, +35%'), ('$1.64B', 'Annual recurring revenue, +39%'), ('126%', 'Net revenue retention'), ('$15.1B', 'Future contracted bookings, +41%'), ('26.8%', 'Adjusted EBITDA margin'), ('32&ndash;34%', '2026 revenue growth guidance, raised')])
         + prose('Second-quarter revenue beat estimates by about $28 million. TASER grew 21%, and Platform Solutions (drones, counter-drone, fixed cameras) more than doubled, with Dedrone passing $100 million in the quarter. Management raised 2026 growth guidance to 32&ndash;34% and set 2028 targets of <b>$6 billion of revenue</b> and a 28% adjusted EBITDA margin.',
                 'The shares fell anyway. The software gross margin dropped about four points to 71.3% as services and new products grew, memory chips raised camera costs, and free cash flow was roughly zero. In September Axon sold <b>$1 billion of 0% convertible notes</b>, which investors read as a sign of dilution ahead. Results for the third quarter come on <b>November 3</b>.')
         + src([('Q2 2026 results', AQ), ('Q2 slides and reaction', 'https://www.investing.com/news/company-news/axon-q2-2026-slides-show-35-growth-but-shares-fall-on-margin-worries-93CH-4839831'), ('Convertible notes', 'https://finance.yahoo.com/markets/stocks/articles/1-billion-reason-why-axon-193446212.html')])),
        ('fin', 'Five years', 'Revenue tripled <em>in four years.</em>',
         fin_table('AXON') + prose('GAAP profit is small because stock-based pay is very large: guided at $590&ndash;620 million in 2026, about 16% of revenue, including a one-off CEO award. Adjusted EBITDA adds that back, which is why the two measures tell such different stories. The <a href="snapshot.html?t=AXON&amp;view=q">quarterly view</a> shows each quarter from the 10-Qs.')
         + src([('Axon filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001069183&type=10-K')])),
        ('ai', 'The translation thesis', 'Can AI translation <em>be a game changer?</em>',
         prose('Real-time translation already ships. Through <b>Axon Assistant</b>, an officer presses a button on an Axon Body 4 or Body Mini camera, picks a language (or lets it detect one), and the camera speaks the translation aloud; the reply is translated back into English. It covers more than 50 languages and became generally available on August 1, 2025. Frederick, Maryland, ran 1,027 translated conversations in five weeks of testing; officers said quality varied by language, and certified interpreters are still used for investigations.',
               'The economics are what matter for the stock. Translation is sold inside the AI Era Plan rather than as a separate device, so its value shows up as higher revenue per officer on a camera base Axon already owns. In the U.S. about one in five people speaks a language other than English at home, so the feature is useful on almost every shift, which helps agencies justify the upgrade.',
               '<b>Military and federal use</b> is a real but early opportunity. Federal agencies added more than 22,000 body cameras and evidence licenses in 2026, the VA bought TASER 10s, and in October DHS selected Dedrone for counter-drone protection. Axon does not report military revenue separately, and armed forces have their own translation programs and suppliers, so this report treats military translation as upside rather than part of the base case.')
         + key('Takeaway', 'Translation is a strong reason to upgrade, but it is a feature Axon sells to customers it already has, not a new product line. It supports the 2028 targets more than it changes them.')
         + src([('Translation in Frederick, Md.', 'https://www.governing.com/artificial-intelligence/police-body-cameras-are-learning-to-speak-50-languages'), ('Renton police rollout', 'https://www.kiro7.com/news/local/renton-police-debut-bodycam-that-translates-over-50-languages-real-time/KMK2544CHBFZLAJTLTO7VVAKU4/'), ('Federal momentum', 'https://www.tikr.com/blog/axon-stock-fell-6-in-a-day-and-is-down-31-in-2026-time-to-sell-or-load-up')])),
        ('value', 'Valuation', 'Our scenarios give <em>$289 a share.</em>',
         prose('Valued on 2030 earning power like the other fast growers here, using operating margin <i>after</i> stock-based pay, discounted at 11% a year (beta 1.44 gives a CAPM cost of about 11.6%, trimmed slightly for the subscription base). Net debt of about $1.1 billion and 88 million shares by 2030 are included.')
         + scen([['Revenue in 2030', '$6.5B', '$8.5B', '$10.5B'], ['Operating margin after stock pay', '15%', '20%', '25%'], ['Exit multiple', '25&times;', '30&times;', '35&times;'],
                 ['Value per share', '$132', '$289', '$531'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$310</b>. The base case is close to management&rsquo;s own path: $6 billion in 2028, then about 19% growth a year.')),
        ('implied', 'What the price assumes', 'At $396, <em>about $11.5 billion of revenue by 2030.</em>',
         implied([['About $11.5 billion of revenue in 2030 at the base margin and multiple', 'Management&rsquo;s path reaches about $8.5 billion'], ['Or margins of about 27% after stock pay with base revenue', 'About 5% today, 20% in the base case']])
         + prose('After a 50% fall the stock is far cheaper than it was, but it still prices in growth beyond the company&rsquo;s own targets. Analysts&rsquo; average target of $691 assumes faster growth and a higher multiple.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Stock-based pay', 'About 16% of revenue in 2026; dilution is the main cost to shareholders.'],
             ['Margins', 'Software gross margin fell four points; memory costs hit cameras until about 2028.'],
             ['Budgets and politics', 'Police budgets, federal policy and privacy debates (drones, licence-plate readers) can slow orders.'],
             ['AI accuracy', 'Translation and report-writing errors could create legal problems in court.'],
             ['Valuation', 'Still about 44&times; next year&rsquo;s earnings.'],
         ]) + prose('<b>Upside:</b> AI Era Plan adoption across the installed base, counter-drone demand, international bookings (which tripled), enterprise customers and federal or military contracts.')),
        ('rec', 'Recommendation', 'Watch. <em>A great business, close to a buy point.</em>',
         prose('Axon is one of the best-positioned companies in public safety: a near-monopoly in U.S. police cameras, sticky subscriptions and an AI product line that is growing fast. Real-time translation strengthens that position. At $396.30, though, the price is above our base case of $289 ($310 weighted). A price nearer $300, or third-quarter results on November 3 that show margins recovering, would make it a Buy.')
         + band('The right thesis, <em>a slightly early price.</em>', 'AI makes Axon&rsquo;s subscription more valuable; the stock already assumes much of that.')),
    ])
