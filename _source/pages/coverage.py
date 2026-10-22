"""Reports on SpaceX and Firefly (holdings), OpenAI, Anthropic, Anduril and Bloomberg (private), and Kratos, Axon, Palantir, AMD, Micron, Sandisk,
Lockheed Martin, Northrop Grumman, Caterpillar, ASML and SK hynix. Written October 21-22, 2026. Scenario and cycle values come from
_source/models/new_coverage.py; the cash-flow models are in lmt.py, noc.py, cat.py and asml.py."""
from rep import src, stats, table, prose, key, bridge, fin_table

DATE = 'October 21, 2026'


def scen(rows):
    return table(['', 'Bear', 'Base', 'Bull'], rows, 'allnum')


def implied(rows):
    return table(['To justify the price, you need', 'Against'], rows)


def band(h, p):
    return f'<div class="band sm"><div class="eyebrow mono">Final view</div><h2>{h}</h2><p>{p}</p></div>'


TOCP = [('overview', 'The business'), ('results', 'Latest results'), ('fin', 'The numbers'), ('capital', 'Balance sheet and ownership'),
        ('value', 'Valuation'), ('implied', 'What the price assumes'), ('risks', 'Risks'), ('rec', 'Rating')]
TOCV = [('overview', 'The business'), ('growth', 'Growth'), ('fin', 'The numbers'), ('capital', 'Funding and ownership'),
        ('value', 'Valuation'), ('implied', 'What the valuation assumes'), ('risks', 'Risks'), ('rec', 'Our view')]

R = {}

# ================================================================ SpaceX
SX = 'https://www.stocktitan.net/articles/spacex-q3-2026-earnings-ai-revenue-passes-starlink'
R['SPCX'] = dict(
    t='SPCX', slug='spacex', name='SpaceX', h1='Space<em>X</em>', sector='Space and AI', date=DATE, timing=', the day after its third-quarter results',
    sub='SpaceX is now three businesses: rockets, the Starlink satellite network, and since buying xAI, one of the largest AI computing operations in the world. Revenue grew 161% last quarter and AI has overtaken Starlink. The price assumes that growth keeps compounding for years.',
    call='Hold', method='Scenario model', price=162.57, pricenote='Midday, Oct 21, 2026', noauto=True, base=123, bear=43, bull=288, wt=144, max=320, tick=40,
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the Street&rsquo;s average target.',
    field=[('Scenario model', 43, 288, 123, '$43 to $288, base $123'), ('Probability-weighted', None, None, 144, '$144'),
           ('Price at writing', None, None, 162.57, '$162.57'), ('52-week range', 105, 226, None, '$105 to $226'), ('Analyst average', None, None, 223, '$223')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Rockets, a satellite network <em>and an AI cloud.</em>',
         prose('<b>Space</b> is the original business: Falcon 9 and Falcon Heavy launches for NASA, the military and commercial customers, and Starship, the fully reusable rocket meant to cut launch costs by an order of magnitude. <b>Connectivity</b> is Starlink, internet from more than 9,000 satellites for homes, ships, airlines and phones. <b>Super Intelligence (SI)</b> came with the purchase of Elon Musk&rsquo;s xAI in February 2026: the Grok models, the X platform, the Cursor coding tool, and data centers that lease computing to other AI labs.',
               'SpaceX listed on Nasdaq as SPCX on June 12, 2026, at $135 a share, valuing it at about $1.77 trillion in the largest IPO on record.')
         + key('Takeaway', 'SpaceX is now an AI infrastructure company with a launch business and a telecom network attached. AI is already more than half of revenue.')),
        ('results', 'Latest results', 'Revenue up 161%, <em>and a first operating profit.</em>',
         stats([('$14.6B', 'Revenue, Q3 2026, +161%'), ('$7.6B', 'AI (SI) revenue, nearly triple Q2'), ('$5.2B', 'Starlink revenue, +69%'), ('$2.8B', 'Operating profit'), ('$19.6B', 'Capital spending in the quarter'), ('$33&ndash;37B', 'Q1 2027 revenue guidance')])
         + prose('Third-quarter revenue of $14.6 billion beat estimates by about $1.7 billion. SI revenue was $7.6 billion, including $608 million from Cursor, as Anthropic, Google and others rented its computing. Starlink added 1.6 million subscribers to reach 13.6 million, fewer than analysts expected, but its operating profit nearly doubled to $2.4 billion. Rockets earned $1.8 billion and roughly broke even.',
                 'Net income was $4.4 billion ($0.35 a share). Management guided first-quarter 2027 revenue to <b>$33&ndash;37 billion</b>, more than double this quarter, as computing capacity grows from 1.7 GW to about 3 GW by year-end. Starship reached orbit on Flight 14 and deployed V3 Starlink satellites. The shares rose about 10% the next day.')
         + src([('Investor relations', 'https://ir.spacex.com/updates/releases-details/2026/SpaceX-to-Post-Third-Quarter-2026-Results-and-Host-Webcast-on-October-20-2026-2026-QssQGye3im/'), ('Q3 2026 results', SX), ('Fortune', 'https://fortune.com/2026/10/20/spacex-q3-profit-ai-si-elon-musk/')])),
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
        ('value', 'Valuation', 'Our scenarios give <em>$123 a share.</em>',
         prose('A ten-year cash-flow model means little for a company whose revenue may triple in a year, so this report values SpaceX on its 2030 earning power: revenue, operating margin and a multiple, discounted back at 12% a year, plus the free cash flow between now and then. That starts deeply negative (an estimated &minus;$68 billion this year, from nine months of reported cash flow and the guided fourth-quarter capital spending) and is assumed to rise in a straight line to 80% of 2030 after-tax profit.')
         + scen([['Revenue in 2030', '$250B', '$500B', '$900B'], ['Operating margin', '22%', '28%', '32%'], ['Exit multiple of after-tax profit', '20&times;', '22&times;', '25&times;'],
                 ['Value per share', '$43', '$123', '$288'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25, the cases give <b>$144</b>. Net cash of about $51 billion and 13.57 billion shares are included.')),
        ('implied', 'What the price assumes', 'At $163, <em>about $660 billion of revenue by 2030.</em>',
         implied([['About $660 billion of revenue in 2030 at a 28% margin', 'About $23 billion over the last twelve months'], ['Or margins and multiples near the bull case', 'Base case of 28% and 22&times;']])
         + prose('That sounds extreme, but management is guiding to a $140 billion annual pace by early 2027 and has talked about $500 billion to $1 trillion by the end of 2027 if its AI business scales. The price sits between the base and bull cases: it needs the AI buildout to keep paying back as fast as management says, which is under a year per data center today.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['AI demand', 'Most growth is renting computing to AI labs. If their spending slows, SpaceX is left with expensive capacity and rising debt.'],
             ['Spending', 'Capex of $70 billion or more a year means negative free cash flow for some time.'],
             ['Governance', 'Musk controls the vote; a Tesla merger or other related-party deals could be on his terms.'],
             ['Lock-up', 'Pre-IPO investors can sell from early December.'],
             ['Execution', 'Starship, V3 satellites and new data centers all have to work on schedule.'],
         ]) + prose('<b>Upside:</b> Starlink Mobile (22 million monthly users), reusable Starship lowering costs for everything else, and AI revenue scaling as guided.')),
        ('rec', 'Rating', 'Hold. <em>A great asset at a full price.</em>',
         prose('At $162.57 against a base case of $118 ($138 weighted), the price already reaches toward the bull case. The business is extraordinary, but the valuation depends on AI growth that has only just started. The call is <b>Hold</b>, sized as a speculative position, with the December lock-up expiry as a possible better entry point.')
         + band('Own the rocket company. <em>Watch the AI bill.</em>', 'SpaceX&rsquo;s value now depends more on data centers than on rockets.')),
    ])

# ================================================================ Firefly
FF = 'https://finance.biggo.com/news/US_FLY_2026-08-11'
R['FLY'] = dict(
    t='FLY', slug='firefly', name='Firefly Aerospace', h1='Firefly <em>Aerospace</em>', sector='Space', date=DATE, timing=', before its third-quarter results in November',
    sub='Firefly builds small rockets, the Blue Ghost lunar lander and spacecraft for NASA and the Pentagon. Revenue is growing fast and the backlog is $1.5 billion, but it loses money and its Alpha rocket has a mixed record. The shares are down about 70% from their high.',
    call='Hold', method='Scenario model', price=17.41, pricenote='Midday, Oct 21, 2026', noauto=True, base=18, bear=3, bull=50, wt=22, max=70, tick=10,
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Scenario model', 3, 50, 18, '$3 to $50, base $18'), ('Probability-weighted', None, None, 22, '$22'),
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
        ('value', 'Valuation', 'Our scenarios give <em>$18 a share.</em>',
         prose('With no profits yet, this report values Firefly on its 2030 revenue and the multiple of sales a profitable space company would command, discounted back at 15% a year, with more shares outstanding to fund the losses until then, and with the cash it burns until 2030 (about $0.2 billion this year, falling in a straight line to breakeven) subtracted.')
         + scen([['Revenue in 2030', '$0.7B', '$1.2B', '$2.0B'], ['Exit value to sales', '2&times;', '5&times;', '8&times;'], ['Shares by 2030', '200M', '185M', '180M'],
                 ['Value per share', '$3', '$18', '$50'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$22</b>. The range is wide on purpose: this is a company where one failed launch or one large contract changes the answer.')),
        ('implied', 'What the price assumes', 'At $17, <em>about $1 billion of revenue by 2030.</em>',
         implied([['About $1.15 billion of revenue in 2030 at 5&times; sales', '$420&ndash;450 million guided for 2026'], ['Roughly 25% annual growth from here', '659% last quarter, from a small base']])
         + prose('The market now prices Firefly slightly below the base case, a big change from the $62 high, when it priced something close to the bull case.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Launch failures', 'Alpha has failed or partly failed four times in seven flights.'],
             ['Losses and dilution', 'About $370 million lost in the last year; more share sales are likely.'],
             ['Competition', 'SpaceX rideshares undercut small rockets; Rocket Lab is further ahead.'],
             ['Government budgets', 'NASA and defense contracts drive most revenue.'],
         ]) + prose('<b>Upside:</b> Golden Dome and missile-warning work through SciTec, more NASA lunar missions, and Eclipse giving Firefly a medium rocket in 2027.')),
        ('rec', 'Rating', 'Hold. <em>Speculative, and priced like it.</em>',
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
KQ = 'https://ir.kratosdefense.com/node/32946'
R['KTOS'] = dict(
    t='KTOS', slug='kratos', name='Kratos Defense', h1='Kratos <em>Defense</em>', sector='Defense', date=DATE, timing=', ahead of its third-quarter results in early November',
    sub='Kratos makes low-cost drones, hypersonic test rockets, small jet engines and satellite ground systems. It is the closest listed company to Anduril. Revenue is growing about 20% a year, but the shares are down more than 70% from their January high because the price had run far ahead of the profits.',
    call='Watch', method='Scenario model', price=38.81, pricenote='Midday, Oct 21, 2026', noauto=True, base=24, bear=14, bull=44, wt=26, max=140, tick=20,
    disclosure='The author holds no KTOS shares.',
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Scenario model', 14, 44, 24, '$14 to $44, base $24'), ('Probability-weighted', None, None, 26, '$26'),
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
        ('value', 'Valuation', 'Our scenarios give <em>$24 a share.</em>',
         prose('Valued the same way as the other fast-growing companies here: 2030 revenue, operating margin after stock pay, and a multiple of after-tax profit, discounted back at 10% a year (Kratos&rsquo;s cost of equity from its beta of about 1.1), plus the free cash flow along the way, which starts slightly negative.')
         + scen([['Revenue in 2030', '$2.6B', '$3.2B', '$4.0B'], ['Operating margin', '6%', '9%', '12%'], ['Exit multiple', '18&times;', '22&times;', '28&times;'],
                 ['Value per share', '$14', '$24', '$44'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$26</b>. Net cash of about $1.2 billion and 200 million shares by 2030 are included. The base case already assumes revenue grows about 16% a year and the operating margin more than triples.')),
        ('implied', 'What the price assumes', 'At $39, <em>about $5.7 billion of revenue by 2030.</em>',
         implied([['About $5.7 billion of revenue in 2030 at the base margin and multiple', '$1.75&ndash;1.81 billion guided for 2026'], ['Or roughly 34% growth a year for four years', '18&ndash;23% organic growth guided']])
         + prose('Even after a 70% fall, the price sits near the bull case. At the January high of $134 it implied revenue several times larger. The analysts&rsquo; average target of $98 assumes faster growth and higher margins than this model does.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Valuation', 'Still about 4&times; sales and 40&times; next year&rsquo;s earnings for a contractor with 10% EBITDA margins.'],
             ['Cash burn and dilution', 'Negative free cash flow and heavy stock pay; another share sale is possible.'],
             ['Program wins', 'The Air Force&rsquo;s main collaborative combat aircraft awards went to rivals; Valkyrie depends on the Marines and new customers.'],
             ['Competition', 'Anduril, General Atomics and the large primes chase the same drone and missile budgets.'],
         ]) + prose('<b>Upside:</b> hypersonic testing, engines for low-cost cruise missiles, a second-source role on JASSM, Golden Dome and a larger Valkyrie order could all lift growth.')),
        ('rec', 'Rating', 'Watch. <em>Not an Anduril substitute at this price.</em>',
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
    call='Watch', method='Scenario model', price=396.30, pricenote='Midday, Oct 21, 2026', base=314, bear=147, bull=567, wt=335, max=800, tick=100,
    disclosure='The author holds no AXON shares.',
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Scenario model', 147, 567, 314, '$147 to $567, base $314'), ('Probability-weighted', None, None, 335, '$335'),
           ('Price at writing', None, None, 396.30, '$396.30'), ('52-week range', 339, 764, None, '$339 to $764'), ('Analyst average', None, None, 691, '$691')],
    toc=[('overview', 'The business'), ('results', 'Latest results'), ('fin', 'Five years'), ('ai', 'The translation thesis'), ('value', 'Valuation'), ('implied', 'What the price assumes'), ('risks', 'Risks'), ('rec', 'Rating')], chapters=[
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
        ('value', 'Valuation', 'Our scenarios give <em>$314 a share.</em>',
         prose('Valued on 2030 earning power like the other fast growers here, using operating margin <i>after</i> stock-based pay, discounted at 11% a year (beta 1.44 gives a CAPM cost of about 11.6%, trimmed slightly for the subscription base). Net debt of about $1.1 billion, 88 million shares by 2030 and the free cash flow earned along the way (a straight line from about $0.1 billion this year to 80% of 2030 after-tax profit) are included.')
         + scen([['Revenue in 2030', '$6.5B', '$8.5B', '$10.5B'], ['Operating margin after stock pay', '15%', '20%', '25%'], ['Exit multiple', '25&times;', '30&times;', '35&times;'],
                 ['Value per share', '$147', '$314', '$567'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$335</b>. The base case is close to management&rsquo;s own path: $6 billion in 2028, then about 19% growth a year.')),
        ('implied', 'What the price assumes', 'At $396, <em>about $10.7 billion of revenue by 2030.</em>',
         implied([['About $10.7 billion of revenue in 2030 at the base margin and multiple', 'Management&rsquo;s path reaches about $8.5 billion'], ['Or margins of about 25% after stock pay with base revenue', 'About 5% today, 20% in the base case']])
         + prose('After a 50% fall the stock is far cheaper than it was, but it still prices in growth beyond the company&rsquo;s own targets. Analysts&rsquo; average target of $691 assumes faster growth and a higher multiple.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Stock-based pay', 'About 16% of revenue in 2026; dilution is the main cost to shareholders.'],
             ['Margins', 'Software gross margin fell four points; memory costs hit cameras until about 2028.'],
             ['Budgets and politics', 'Police budgets, federal policy and privacy debates (drones, licence-plate readers) can slow orders.'],
             ['AI accuracy', 'Translation and report-writing errors could create legal problems in court.'],
             ['Valuation', 'Still about 44&times; next year&rsquo;s earnings.'],
         ]) + prose('<b>Upside:</b> AI Era Plan adoption across the installed base, counter-drone demand, international bookings (which tripled), enterprise customers and federal or military contracts.')),
        ('rec', 'Rating', 'Watch. <em>A great business, close to a buy point.</em>',
         prose('Axon is one of the best-positioned companies in public safety: a near-monopoly in U.S. police cameras, sticky subscriptions and an AI product line that is growing fast. Real-time translation strengthens that position. At $396.30, though, the price is above our base case of $289 ($310 weighted). A price nearer $300, or third-quarter results on November 3 that show margins recovering, would make it a Buy.')
         + band('The right thesis, <em>a slightly early price.</em>', 'AI makes Axon&rsquo;s subscription more valuable; the stock already assumes much of that.')),
    ])

# ================================================================ Palantir
PQ = 'https://www.sec.gov/Archives/edgar/data/0001321655/000132165526000039/a2026q2ex991pressrelease.htm'
R['PLTR'] = dict(
    t='PLTR', slug='palantir', name='Palantir Technologies', h1='Palantir', sector='AI software', date=DATE, timing=', ahead of its third-quarter results on November 2',
    sub='Palantir sells the software that governments and companies use to pull their data together and put AI to work on it. Revenue is growing more than 90% a year and the business is highly profitable, but at about 60 times this year&rsquo;s sales the shares price in far more than that.',
    call='Watch', method='Scenario model', price=201.72, pricenote='Close, Oct 21, 2026', base=87, bear=41, bull=216, wt=107, max=250, tick=50,
    disclosure='The author holds no PLTR shares directly.',
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Scenario model', 41, 216, 87, '$41 to $216, base $87'), ('Probability-weighted', None, None, 107, '$107'),
           ('Price at writing', None, None, 201.72, '$201.72'), ('52-week range', 106, 213, None, '$106 to $213'), ('Analyst average', None, None, 206, '$206')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'One platform, <em>two kinds of customer.</em>',
         prose('Palantir builds software that joins up an organisation&rsquo;s data and lets people, and now AI models, act on it. <b>Gotham</b> and <b>Maven</b> serve defence and intelligence agencies; <b>Foundry</b> does the same for companies; <b>AIP</b>, launched in 2023, puts large language models to work inside both. Customers usually start with a short &ldquo;bootcamp&rdquo; and expand from there.',
               'Government is still the larger half. In the U.S. it includes the Army&rsquo;s enterprise agreement of up to $10 billion over ten years, signed in 2025. The faster-growing half is <b>U.S. commercial</b>, where AIP has turned Palantir from a slow-moving consultant-heavy business into one that sells like software.')),
        ('results', 'Latest results', 'Revenue up 93%, <em>a 62% adjusted margin.</em>',
         stats([('$1.94B', 'Revenue, Q2 2026, +93%'), ('$764M', 'U.S. commercial, +149%'), ('$809M', 'U.S. government, +90%'), ('47%', 'GAAP operating margin'), ('157%', 'Net dollar retention'), ('$8.15B', '2026 revenue guidance, raised')])
         + prose('The second quarter, reported on August 3, beat estimates and brought the largest guidance raise in the company&rsquo;s history: 2026 revenue of about <b>$8.15 billion</b>, up about 82%, with U.S. commercial revenue above $3.4 billion. Adjusted free cash flow was $1.22 billion in the quarter, 63% of revenue, and the &ldquo;Rule of 40&rdquo; score (growth plus margin) reached 155%. U.S. commercial contracts signed in the quarter were worth a record $2.1 billion.',
                 'For the third quarter Palantir guided to revenue of $2.16 billion, about 12% more than the second. The shares reached a record $212.94 on October 12, then fell 7% on October 16 with other AI software names, with no company news. Results come on <b>November 2</b>.')
         + src([('Q2 2026 results', PQ), ('Guidance raise', 'https://www.tikr.com/blog/palantirs-q2-earnings-call-produced-its-largest-ever-guidance-raise-heres-what-changed'), ('October selloff', 'https://www.vantagemarkets.com/market-analysis/why-palantir-stock-fell-ai-financing-worries-pltr-october-21-2026/')])),
        ('fin', 'The numbers', 'From losses to <em>a 47% margin in four years.</em>',
         fin_table('PLTR') + prose('Palantir lost money until 2023. Since then revenue growth has sped up every year while costs grew slowly, so almost every new dollar of revenue has reached profit. Stock-based pay is still large, about $840 million over the past twelve months, but it has fallen from about half of revenue in 2021 to about 14%. The margins in this report are after stock pay. The <a href="snapshot.html?t=PLTR&amp;view=q">quarterly view</a> shows each quarter from the 10-Qs.')
         + src([('Palantir filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001321655&type=10-K')])),
        ('capital', 'Balance sheet and ownership', 'About $9.4 billion of cash <em>and no debt.</em>',
         prose('At the end of June Palantir held about $9.4 billion of cash and short-term Treasuries and had no borrowings. Dilution from stock pay is the main cost to shareholders: this model assumes about 2.6 billion diluted shares by 2030, roughly 1% a year more than today. Co-founders hold super-voting shares, so outside shareholders have little say over the company.')),
        ('value', 'Valuation', 'Our scenarios give <em>$87 a share.</em>',
         prose('Valued like the other fast growers on this site: revenue and operating margin in 2030, taxed at 21%, times an exit multiple, discounted back four years at 14% (beta 2.0 gives a CAPM cost of about 14.2%), plus net cash and the free cash flow earned along the way (a straight line from about $3.4 billion over the last twelve months to 80% of 2030 after-tax profit).')
         + scen([['Revenue in 2030', '$18B', '$28B', '$45B'], ['Growth a year from 2026', '22%', '36%', '53%'], ['Operating margin after stock pay', '40%', '50%', '55%'], ['Exit multiple', '25&times;', '30&times;', '45&times;'],
                 ['Value per share', '$41', '$87', '$216'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$107</b>. Even the base case is generous: revenue more than triples in four years and the margin stays near today&rsquo;s record.')),
        ('implied', 'What the price assumes', 'At $202, <em>the bull case.</em>',
         implied([['About $42 billion of revenue in 2030 at a 55% margin and 45&times; earnings', 'About $8 billion this year; about 50% growth a year for four years'], ['Or about $68 billion of revenue at the base margin and multiple', 'More than eight times this year&rsquo;s revenue']])
         + prose('The market is paying today for the outcome that has everything go right. That is possible for a company growing this fast, but it leaves no room for a slowdown. The analysts&rsquo; average target of $206 is close to the price; their range runs from $80 to $265.')
         + src([('Analyst targets', 'https://beinsure.com/news/palantir-stock-forecast-analysts-see-11-upside-after-selloff/')])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Valuation', 'About 60&times; this year&rsquo;s revenue: a small slowdown can mean a large fall in the price.'],
             ['Government budgets', 'About 40% of revenue is U.S. government; spending priorities and contract timing can change.'],
             ['Competition', 'Cloud providers and AI labs are building their own enterprise data and agent tools.'],
             ['Stock pay and control', 'Dilution continues, and super-voting shares leave founders in charge.'],
             ['AI software sentiment', 'The shares move with the wider AI trade, as in October&rsquo;s 7% one-day fall.'],
         ]) + prose('<b>Upside:</b> AIP spreading through large companies faster than expected, more defence work (Maven, the Army agreement, allies), and margins rising further as revenue scales.')),
        ('rec', 'Rating', 'Watch. <em>An outstanding business at a bull-case price.</em>',
         prose('Few software companies have ever grown this fast at this size while earning these margins, and the U.S. commercial business is still accelerating. At $201.72, though, the price matches our bull case and is about twice the weighted value of $100. A fall toward $100&ndash;120, or several more quarters of 80%-plus growth that lift the base case, would make it worth buying.')
         + band('The best numbers in software, <em>priced as if they last.</em>', 'Palantir has earned its premium; the shares already pay for the next four years of it.')),
    ])

# ================================================================ AMD
AQ2 = 'https://ir.amd.com/news-events/press-releases/detail/1295/'
R['AMD'] = dict(
    t='AMD', slug='amd', name='Advanced Micro Devices', h1='AMD', sector='Semiconductors', date=DATE, timing=', ahead of its third-quarter results on November 3',
    sub='AMD designs processors for PCs, servers and game consoles, and is now the main alternative to Nvidia in AI accelerators. Data center sales more than doubled last quarter and its Helios AI racks start shipping this half. The shares are up more than 140% this year.',
    call='Watch', method='Scenario model', price=552.72, pricenote='Close, Oct 21, 2026', base=353, bear=148, bull=641, wt=374, max=700, tick=100,
    disclosure='The author holds no AMD shares directly; AMD is held inside the VanEck Semiconductor ETF (SMH) in the author&rsquo;s portfolio.',
    fieldnote='The scenario model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Scenario model', 148, 641, 353, '$148 to $641, base $353'), ('Probability-weighted', None, None, 374, '$374'),
           ('Price at writing', None, None, 552.72, '$552.72'), ('52-week range', 188, 659, None, '$188 to $659'), ('Analyst average', None, None, 636, '$636')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'CPUs it leads in, <em>GPUs it is catching up in.</em>',
         prose('AMD has four businesses. <b>Data Center</b> (58% of revenue) sells EPYC server processors, where it has taken share from Intel for years, and Instinct AI accelerators. <b>Client</b> sells Ryzen PC chips, <b>Gaming</b> the chips inside the PlayStation and Xbox, and <b>Embedded</b> the Xilinx programmable chips it bought in 2022.',
               'The investment case is AI. With the MI450 series and the <b>Helios</b> rack, AMD sells a whole AI system rather than single chips. OpenAI agreed in October 2025 to deploy 6 gigawatts of AMD GPUs and received a warrant for up to 160 million AMD shares that vests as deployments and the share price hit milestones. In 2026 Anthropic agreed to deploy up to 2 gigawatts of MI450 GPUs in Helios racks, and Meta, Microsoft and Oracle are customers too.')),
        ('results', 'Latest results', 'Data center <em>up 107%.</em>',
         stats([('$11.5B', 'Revenue, Q2 2026, +50%'), ('$6.7B', 'Data Center, +107%'), ('$3.1B', 'Client, +23%'), ('56%', 'Gross margin, adjusted'), ('$1.66', 'Adjusted EPS'), ('$13.0B', 'Q3 revenue guidance')])
         + prose('Second-quarter revenue rose 50% and Data Center more than doubled. Gaming fell 31% and Embedded grew 19%. GAAP operating income was $2.0 billion and free cash flow $1.56 billion, 14% of revenue. The shares fell 7% the next day because investors wanted more.',
                 'For the third quarter AMD guided to about <b>$13.0 billion</b> of revenue and a 56% gross margin. Lisa Su described Q3 as the start of the Helios ramp, Q4 as a step up and Q1 2027 as a further step up, and management expects Data Center revenue to more than double again in 2027. The stock closed at a record $649.42 on October 6 and has fallen about 15% since. Results come on <b>November 3</b>.')
         + src([('Q2 2026 results', AQ2), ('Ramp and expectations', 'https://fool.com/investing/2026/10/19/amd-stock-is-up-over-140-this-year-i-d-still-buy-it-before-its-nov-3-report'), ('Analyst views', 'https://247wallst.com/investing/2026/10/08/amds-biggest-analyst-price-target-is-eye-opening-heres-what-it-would-take-to-reach-it/')])),
        ('fin', 'The numbers', 'Revenue doubled in four years; <em>2026 adds another 40%.</em>',
         fin_table('AMD') + prose('GAAP profit looks small next to adjusted figures because AMD still amortises the intangible assets from the Xilinx deal and pays a lot in stock (about $1.9 billion over the past twelve months). The adjusted 2025 figures add both back. This report&rsquo;s margins are GAAP, after stock pay. The <a href="snapshot.html?t=AMD&amp;view=q">quarterly view</a> shows each quarter.')
         + src([('AMD filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000002488&type=10-K')])),
        ('capital', 'Balance sheet and ownership', 'About $10 billion of net cash, <em>and a warrant to OpenAI.</em>',
         prose('At the end of June AMD had $13.1 billion of cash and short-term investments and $3.2 billion of debt. The OpenAI warrant is the unusual item: up to 160 million shares, about 10% of today&rsquo;s count, for a nominal price, with the last tranche tied to a $600 share price. This model counts all of it, so shares rise from 1.63 billion to about 1.80 billion by 2030.')),
        ('value', 'Valuation', 'Our scenarios give <em>$353 a share.</em>',
         prose('2030 revenue and operating margin, taxed at 21%, times an exit multiple, discounted back four years at 12% (beta 1.6 gives a CAPM cost of about 12.3%), plus net cash and the free cash flow earned along the way (a straight line from about $8.4 billion over the last twelve months to 80% of 2030 after-tax profit). AMD&rsquo;s own long-term targets, set in November 2025, call for revenue growth above 35% a year and earnings above $20 a share; it now says it expects to beat that figure significantly.')
         + scen([['Revenue in 2030', '$100B', '$150B', '$200B'], ['Operating margin after stock pay', '22%', '30%', '35%'], ['Exit multiple', '20&times;', '25&times;', '30&times;'],
                 ['Value per share', '$148', '$353', '$641'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$374</b>. The base case has revenue about three times this year&rsquo;s roughly $50 billion: Data Center doubling in 2027, then growth slowing to about 15% by 2030.')),
        ('implied', 'What the price assumes', 'At $553, <em>about $170 billion of revenue at bull margins.</em>',
         implied([['About $172 billion of revenue in 2030 at a 35% margin and 30&times; earnings', 'Close to our bull case'], ['Or about $237 billion of revenue at the base margin and multiple', 'Almost five times this year&rsquo;s revenue']])
         + prose('The analysts&rsquo; average target is $636 and they put the stock at about 34 times their 2027 earnings estimate. Our lower number comes mostly from valuing it on 2030 earnings, after the AI build-out has slowed, rather than on 2027.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Helios timing', 'Growth after Q3 depends on racks shipping on schedule; a slip would hit 2027.'],
             ['Nvidia', 'Nvidia still has most of the market, a software lead (CUDA) and a yearly product cadence.'],
             ['Customer concentration', 'A few AI labs and cloud providers account for most of the GPU growth.'],
             ['AI spending cycle', 'If AI data center spending slows after 2027, the highest-growth part of AMD slows with it.'],
             ['Dilution and export rules', 'The OpenAI warrant adds up to 10% more shares; China export limits already cost $800 million in 2025.'],
         ]) + prose('<b>Upside:</b> a faster Helios ramp, share gains in AI inference, more lab deals like Anthropic&rsquo;s, and continued EPYC gains in servers.')),
        ('rec', 'Rating', 'Watch. <em>The right products, a price ahead of them.</em>',
         prose('AMD is in the best position in its history: leading in server CPUs and finally a credible second supplier of AI systems, with signed demand from OpenAI and Anthropic. At $552.72, though, the price is close to our bull case and about 60% above the weighted value of $340. Third-quarter results on November 3 and the size of the fourth-quarter step-up are the next test; a price nearer $350&ndash;400, or proof that 2027 data center revenue is running well ahead of plan, would make it a Buy.')
         + band('A real challenger to Nvidia, <em>already priced as one.</em>', 'The products and customers are there; the shares have run ahead of the revenue.')),
    ])

# ================================================================ Micron
MQ = 'https://www.sec.gov/Archives/edgar/data/0000723125/000072312526000018/a2026q4ex991-pressrelease.htm'
MC = 'https://www.marketbeat.com/instant-alerts/transcript-micron-technology-q4-earnings-call-highlights-2026-09-30/'
R['MU'] = dict(
    t='MU', slug='micron', name='Micron Technology', h1='Micron', sector='Memory chips', date=DATE, timing=', after record fiscal 2026 results',
    sub='Micron is the only large U.S. maker of memory chips, and the AI boom has turned memory from a commodity into the scarcest part of a data center. Revenue more than tripled to $133 billion last year at an 87% gross margin by the end. The question is how long a famously cyclical industry can stay this tight.',
    call='Watch', method='Cycle model', price=913.67, pricenote='Close, Oct 21, 2026', base=622, bear=356, bull=1266, wt=717, max=1600, tick=200,
    disclosure='The author holds no MU shares directly; Micron is held inside the VanEck Semiconductor ETF (SMH) in the author&rsquo;s portfolio.',
    fieldnote='The cycle model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; consensus target.',
    field=[('Cycle model', 356, 1266, 622, '$356 to $1,266, base $622'), ('Probability-weighted', None, None, 717, '$717'),
           ('Price at writing', None, None, 913.67, '$913.67'), ('52-week range', 192, 1255, None, '$192 to $1,255'), ('Analyst consensus', None, None, 1555, '$1,555')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Memory, <em>and the memory AI needs most.</em>',
         prose('Micron makes the two main kinds of memory. <b>DRAM</b> (73% of last quarter&rsquo;s revenue) is the working memory in every computer, and includes <b>HBM</b>, the stacked memory that sits next to each AI accelerator. <b>NAND</b> (26%) stores data in phones, PCs and data center drives. Only three companies make DRAM at scale: Samsung, SK Hynix and Micron.',
               'AI changed the industry in two ways. HBM uses about three times the silicon of ordinary DRAM for each bit, so making it takes capacity away from everything else; and AI servers need far more memory of every kind. The result is a shortage that Micron expects to be &ldquo;much tighter&rdquo; in fiscal 2027 and 2028 than in 2026.')),
        ('results', 'Latest results', 'Revenue up 379% in a year, <em>an 87% gross margin.</em>',
         stats([('$54.2B', 'Revenue, Q4 FY2026, +31% on Q3'), ('86.8%', 'Gross margin'), ('$37.7B', 'Net income'), ('$33.2B', 'Free cash flow'), ('$68.3B', 'Net cash'), ('$61.5B', 'Q1 FY2027 revenue guidance')])
         + prose('Fiscal 2026 (to September 3) brought revenue of <b>$133.2 billion</b>, up 256%, and net income of $85 billion. In the fourth quarter DRAM prices rose in the high teens and NAND prices about 30% from the quarter before. For the first quarter of fiscal 2027 Micron guided to $61.5 billion of revenue, an 86.25% gross margin and $38.15 of adjusted earnings per share; it plans to step up buybacks from December.',
                 'Micron has also changed how it sells. It has signed 26 multi-year agreements with take-or-pay volumes, expected to cover more than 35% of revenue through 2030, with about $150 billion of remaining obligations at set prices and $32 billion of customer prepayments. More than 75% of 2027 output is already committed.')
         + src([('Q4 FY2026 results', MQ), ('Earnings call', MC)])),
        ('fin', 'The numbers', 'A loss in 2023, <em>$85 billion of profit in 2026.</em>',
         fin_table('MU') + prose('The table is the case for caution in one picture. In fiscal 2023 revenue halved and Micron lost $5.8 billion; three years later it earned $85 billion. Memory prices move with supply and demand, and every past boom has ended with new factories coming online and prices falling. Capital spending rises with the cycle too: about $25 billion in the first half of fiscal 2027 alone.')
         + src([('Micron filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000723125&type=10-K')])),
        ('capital', 'Balance sheet and supply', '$68 billion of net cash <em>and new fabs from 2027.</em>',
         prose('Micron ended fiscal 2026 with $68.3 billion of net cash. Its new capacity arrives in steps: Idaho ID1 in mid-2027, ID2 and a Japan DRAM expansion in late 2028, a Singapore NAND plant in the second half of 2028 and the first New York fab in 2030. Samsung and SK Hynix are expanding too. Morningstar, which cut its fair value to $700, expects industry supply to roughly double by 2028 and prices to fall steeply from 2029.')
         + src([('Cycle outlook', 'https://finance.yahoo.com/markets/stocks/articles/microns-blowout-q4-pushes-memory-090742260.html')])),
        ('value', 'Valuation', 'Our cycle model gives <em>$622 a share.</em>',
         prose('A single year&rsquo;s earnings is the wrong base for a memory maker, so this model values the cycle: free cash flow for fiscal 2027&ndash;2030 at each scenario&rsquo;s prices, then an exit value on <i>mid-cycle</i> earnings, all discounted at 14% (beta 2.0 gives a CAPM cost of about 14.3%), plus net cash, over about 1.10 billion shares after buybacks.')
         + scen([['Revenue, FY2027 / FY2028', '$220B / $200B', '$250B / $280B', '$290B / $350B'], ['Revenue, FY2029 / FY2030', '$130B / $110B', '$200B / $150B', '$330B / $300B'], ['Free cash flow, four years', '$211B', '$360B', '$678B'],
                 ['Mid-cycle revenue and operating margin', '$130B at 25%', '$170B at 35%', '$280B at 45%'], ['Exit multiple', '10&times;', '12&times;', '14&times;'],
                 ['Value per share', '$356', '$622', '$1,266'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$717</b>. The base case follows management&rsquo;s view (tighter through fiscal 2028) and then the usual turn as new supply arrives. Even the bear case stays well above anything Micron earned before AI.')),
        ('implied', 'What the price assumes', 'At $914, <em>record profit becomes normal.</em>',
         implied([['About $92 billion of after-tax profit a year from 2031, valued at 12&times;, after the base case&rsquo;s cash flows', 'Fiscal 2026 net income was $85 billion, at the start of the boom'], ['Or the bull case&rsquo;s four-year boom with a higher exit', 'Supply stays short through 2030']])
         + prose('The price is between our base and bull cases. Analysts are much more optimistic: their consensus target is about $1,555, and the stock trades at about 7 times next year&rsquo;s expected earnings. That multiple looks cheap only if next year&rsquo;s earnings are close to normal, which memory history argues against.')
         + src([('Analyst targets', 'https://247wallst.com/investing/2026/10/15/micron-stock-has-some-eye-popping-analyst-targets-heres-my-price-prediction/'), ('Valuation comparison', 'https://www.fool.com/coverage/better-buy/2026/10/17/micron-technology-vs-sandisk-which-ai-memory-stock-is-the-better-investment/')])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['The cycle', 'New fabs at Micron, Samsung and SK Hynix arrive from 2027&ndash;2028; prices have always fallen when they do.'],
             ['AI spending', 'Fears of AI overbuilding cut the shares 26% in July; hyperscaler capex growth is expected to slow.'],
             ['Customer concentration', 'Data centers are about 60% of revenue and a handful of buyers dominate.'],
             ['China', 'Beijing barred some infrastructure operators from buying Micron chips in 2023.'],
             ['Capital spending', 'Higher capex and depreciation will weigh on margins as prices ease.'],
         ]) + prose('<b>Upside:</b> long-term agreements that keep prices high for longer, HBM4 and custom HBM with Nvidia, and buybacks from a cash pile of nearly $70 billion.')),
        ('rec', 'Rating', 'Watch. <em>Peak conditions, priced for more.</em>',
         prose('Micron is executing brilliantly in the best memory market there has ever been, and its long-term agreements make this cycle steadier than past ones. At $913.67, though, the price assumes today&rsquo;s profit lasts well beyond 2028, about 27% above our weighted value of $717. We would rather buy nearer $700, or when the first signs of a downturn have already been priced in. Next results are expected in mid-December.')
         + band('The best memory market ever, <em>still a memory market.</em>', 'Every past boom ended with new supply; this one has a later date, not a different ending.')),
    ])

# ================================================================ Sandisk
SQ = 'https://investor.sandisk.com/news-releases/news-release-details/sandisk-reports-fiscal-fourth-quarter-2026-financial-results'
R['SNDK'] = dict(
    t='SNDK', slug='sandisk', name='Sandisk', h1='Sandisk', sector='Flash storage', date=DATE, timing=', ahead of its first-quarter results on October 29',
    sub='Sandisk makes NAND flash, the memory that stores data in phones, PCs and AI data centers. Spun off from Western Digital in February 2025, it went from losses to an 85% gross margin in a year as flash prices soared. The shares are up more than eightfold in twelve months and down about 40% from their high.',
    call='Watch', method='Cycle model', price=1378.22, pricenote='Close, Oct 21, 2026', base=636, bear=306, bull=1487, wt=766, max=2400, tick=400,
    disclosure='The author holds no SNDK shares.',
    fieldnote='The cycle model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; median target.',
    field=[('Cycle model', 306, 1487, 636, '$306 to $1,487, base $636'), ('Probability-weighted', None, None, 766, '$766'),
           ('Price at writing', None, None, 1378.22, '$1,378.22'), ('52-week range', 145, 2354, None, '$145 to $2,354'), ('Analyst median', None, None, 2225, '$2,225')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Pure flash, <em>made with Kioxia.</em>',
         prose('Sandisk sells only NAND flash. <b>Edge</b> (61% of last quarter&rsquo;s revenue) is flash for phones and PCs; <b>Datacenter</b> (33%) is enterprise SSDs, now the fastest-growing part as AI systems store and move far more data; <b>Consumer</b> is memory cards and portable drives. It makes its chips in Japan through <b>Flash Ventures</b>, a joint venture with Kioxia that shares the cost of the factories.',
               'Because it does nothing but flash, Sandisk is the most direct way to own the NAND cycle. That made it one of the best-performing stocks of the AI memory boom, and also the one most exposed if flash prices turn.')),
        ('results', 'Latest results', 'Revenue up 372%, <em>an 85% gross margin.</em>',
         stats([('$8.97B', 'Revenue, Q4 FY2026, +51% on Q3'), ('84.6%', 'Gross margin'), ('$6.90B', 'Net income'), ('$7.08B', 'Free cash flow'), ('$2.98B', 'Datacenter, +103% on Q3'), ('$10.3&ndash;10.8B', 'Q1 FY2027 revenue guidance')])
         + prose('In the quarter to July 3, revenue rose 51% from the quarter before; about two-thirds of that came from higher prices and one-third from volume. The gross margin went from about 51% in the second quarter to 78% in the third and <b>84.6%</b> in the fourth. For fiscal 2026 revenue was $20.2 billion, up 175%, and net income $11.4 billion.',
                 'For the first quarter of fiscal 2027 Sandisk guided to $10.3&ndash;10.8 billion of revenue, an 83&ndash;85% gross margin and $44&ndash;46 of adjusted earnings per share. It bought back $4.5 billion of stock in the quarter and the board added $14 billion to the buyback. Results come on <b>October 29</b>.')
         + src([('Q4 FY2026 results', SQ), ('Q1 results date', 'https://investor.sandisk.com/news-releases/news-release-details/sandisk-report-first-quarter-fiscal-year-2027-results-october-29')])),
        ('fin', 'The numbers', 'Losses until 2025, <em>$11 billion of profit in 2026.</em>',
         fin_table('SNDK') + prose('Sandisk lost money in each of its three years before the boom, including $2.1 billion in fiscal 2023, the last flash downturn. The swing to an $11.4 billion profit came almost entirely from price, which is why the same table is the main risk. Capital spending stays low because Flash Ventures carries most of the factory cost.')
         + src([('Sandisk filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0002023554&type=10-K')])),
        ('capital', 'Contracts and balance sheet', 'Price floors, <em>and price ceilings.</em>',
         prose('Sandisk now sells much of its output under multi-year agreements whose prices can move only between a floor and a ceiling. Management expects them to cover over half of its bits in fiscal 2027 and about two-thirds in fiscal 2028. The floors protect it in a downturn; the ceilings cap how much it gains if the shortage worsens. The CEO has called a mid-80s gross margin a fair return, so today&rsquo;s margin is close to the top.',
               'At the end of fiscal 2026 Sandisk had $4.8 billion of cash and had repaid all its debt. The model assumes about 150 million shares by 2030, down from about 155 million, as buybacks continue.')
         + src([('Contract structure', 'https://www.fool.com/investing/2026/10/01/micron-says-memory-supply-will-be-much-tighter-in-2028-sandisk-s-contracts-limit-how-much-it-can-gain/')])),
        ('value', 'Valuation', 'Our cycle model gives <em>$636 a share.</em>',
         prose('The same method as Micron: free cash flow for fiscal 2027&ndash;2030 at each scenario&rsquo;s prices, then an exit value on mid-cycle earnings, discounted at 15% (beta 2.1 gives a CAPM cost of about 14.6%), plus net cash.')
         + scen([['Revenue, FY2027 / FY2028', '$40B / $35B', '$45B / $50B', '$52B / $65B'], ['Revenue, FY2029 / FY2030', '$20B / $16B', '$35B / $25B', '$65B / $60B'], ['Free cash flow, four years', '$41B', '$77B', '$154B'],
                 ['Mid-cycle revenue and operating margin', '$18B at 12%', '$28B at 25%', '$50B at 40%'], ['Exit multiple', '8&times;', '10&times;', '12&times;'],
                 ['Value per share', '$306', '$636', '$1,487'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$766</b>. The base case keeps the shortage through fiscal 2028, as the industry expects, then has prices fall back toward a mid-cycle margin still well above anything Sandisk earned before.')),
        ('implied', 'What the price assumes', 'At $1,378, <em>the boom never ends.</em>',
         implied([['About $25 billion of after-tax profit a year from 2031, valued at 10&times;, after the base case&rsquo;s cash flows', 'About what Sandisk should earn in fiscal 2027, at peak prices'], ['Or the bull case: revenue of $60 billion or more and 60% cash margins through 2030', 'Contract ceilings limit how high prices can go']])
         + prose('The price sits just below our bull case. Analysts are far more optimistic, with a median target of about $2,225. At about 8 times next year&rsquo;s expected earnings the stock looks cheap, but those earnings are made at peak prices that the company&rsquo;s own contracts expect to cap.')
         + src([('Analyst targets and valuation', 'https://www.fool.com/coverage/better-buy/2026/10/17/micron-technology-vs-sandisk-which-ai-memory-stock-is-the-better-investment/')])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['The flash cycle', 'Flash prices drove almost all of the profit; new supply from 2028 could reverse them quickly.'],
             ['Single product', 'Unlike Micron, Sandisk has no DRAM or HBM to cushion a NAND downturn.'],
             ['Contract ceilings', 'Prices are capped on more than half of its bits in fiscal 2027, limiting upside.'],
             ['Kioxia', 'Its factories are shared with Kioxia, so supply and costs depend on the joint venture.'],
             ['Volatility', 'The shares fell about 40% in July on AI overbuilding fears.'],
         ]) + prose('<b>Upside:</b> enterprise SSD demand from AI inference, high-bandwidth flash for AI systems, contract floors that soften the next downturn, and large buybacks.')),
        ('rec', 'Rating', 'Watch. <em>A great quarter, a peak-cycle price.</em>',
         prose('Sandisk has turned a loss-making business into one with an 85% gross margin and no debt in about a year, and its contracts should make the next downturn milder than the last. At $1,378.22, though, the shares are close to our bull case and about 80% above the weighted value of $766. First-quarter results on October 29 will show how far prices are still rising; we would look again nearer $750.')
         + band('The purest bet on flash, <em>at a price for perfect flash.</em>', 'Sandisk earns a fortune at today&rsquo;s prices; the shares assume those prices stay.')),
    ])


# ================================================================ October 22 additions: the defense primes and Anduril, Caterpillar, and the AI chip supply chain
D22 = 'October 22, 2026'


def sens(label, cols, vals):
    return '<h3 class="sec sm">Sensitivity to the discount rate</h3>' + table([label] + cols, [['Value per share'] + vals], 'allnum')


def toc_with(extra_id, extra_label, after='results'):
    out = []
    for i, l in TOCP:
        out.append((i, l))
        if i == after:
            out.append((extra_id, extra_label))
    return out


ANDP = 'https://www.militarytimes.com/industry/techwatch/2026/06/18/us-air-force-awards-first-cca-production-contracts-to-general-atomics-anduril/'
MIDT = 'https://247wallst.com/investing/2026/10/20/defense-stocks-are-tumbling-as-wall-street-bets-on-a-democratic-sweep/'

# ================================================================ Lockheed Martin
LQ = 'https://news.lockheedmartin.com/2026-10-22-Lockheed-Martin-Reports-Third-Quarter-2026-Financial-Results'
LC = 'https://finance.biggo.com/news/US_LMT_2026-10-22'
R['LMT'] = dict(
    t='LMT', slug='lockheed-martin', name='Lockheed Martin', h1='Lockheed <em>Martin</em>', sector='Aerospace &amp; defense', date=D22, timing=', the day of its third-quarter results',
    sub='Lockheed Martin is the world&rsquo;s largest defense contractor: the F-35, the PAC-3 and THAAD missile interceptors, Sikorsky helicopters and military satellites. Its backlog just hit a record $292 billion. The question this report asks is how much of that a new kind of competitor, led by Anduril, can take.',
    call='Hold', method='Cash-flow model', price=590.20, pricenote='Close, Oct 22, 2026', base=647, bear=401, bull=973, wt=667, max=1100, tick=100,
    disclosure='The author holds no LMT shares directly.',
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 401, 973, 647, '$401 to $973, base $647'), ('Probability-weighted', None, None, 667, '$667'),
           ('Price at writing', None, None, 590.20, '$590.20'), ('52-week range', 437, 692, None, '$437 to $692')],
    toc=toc_with('threat', 'The Anduril question'), chapters=[
        ('overview', 'The business', 'Fighter jets, interceptors <em>and satellites.</em>',
         prose('Lockheed reports four segments. <b>Aeronautics</b> (about 40% of sales) builds the F-35, the F-16 and the C-130. <b>Missiles and Fire Control</b> makes the PAC-3 and THAAD interceptors, GMLRS and PrSM rockets and long-range strike missiles. <b>Rotary and Mission Systems</b> is Sikorsky helicopters, radars and ship combat systems. <b>Space</b> builds satellites, the Orion capsule and the Trident submarine-launched missile.',
               'About three-quarters of sales go to the U.S. government, and most of the rest to allies buying through it. Contracts run for years and are priced to give a steady single-digit to low-teens margin, which makes Lockheed a slow-growing, cash-generating business that pays out most of what it earns.')),
        ('results', 'Latest results', 'Sales up 11%, <em>a record $292 billion backlog.</em>',
         stats([('$20.7B', 'Sales, Q3 2026, +11%'), ('$7.97', 'Earnings per share'), ('$3.0B', 'Free cash flow'), ('$292B', 'Backlog, a record'), ('+24%', 'Missiles and Fire Control sales'), ('$80&ndash;82B', '2026 sales guidance, raised')])
         + prose('Third-quarter sales rose 11% to $20.7 billion. Missiles and Fire Control grew 24% as PAC-3, THAAD, GMLRS and PrSM production ramped, and Aeronautics 13%. Backlog jumped 27% in the quarter to $292 billion, including $52.5 billion for the PAC-3 MSE interceptor under a seven-year agreement worth up to $58.6 billion.',
                 'Lockheed raised its 2026 guidance for the second quarter running: sales of $80&ndash;82 billion, earnings of $30.35&ndash;30.75 a share and free cash flow of $7.8&ndash;8.0 billion. Management expects all four segments to grow in 2027, with a &ldquo;clear line of sight&rdquo; to high single-digit growth. The shares closed up about 7% on the day.')
         + src([('Q3 2026 results', LQ), ('Earnings call', LC), ('Share price reaction', 'https://247wallst.com/investing/2026/10/22/lockheed-martin-rises-9-as-record-backlog-lifts-outlook-rtx-gains-2-northrop-grumman-advances-3/')])),
        ('threat', 'The Anduril question', 'Where the new entrants <em>win, and where they can&rsquo;t yet.</em>',
         prose('Anduril, valued at about $90 billion in an October employee share sale, is the most visible of a group of venture-backed defense companies that build products with their own money and sell them, rather than waiting for the Pentagon to fund development. Its 2026 revenue of about $4.3 billion is roughly 5% of Lockheed&rsquo;s, but it is roughly doubling every year, and it has already won where it matters most: in June 2026 the Air Force chose <b>Anduril and General Atomics</b> to build the first collaborative combat aircraft (drone wingmen for fighters). Lockheed, Boeing and Northrop were not picked for that hardware, though all three are in the six-company pool competing to write the autonomy software.')
         + table(['Market', 'Where Lockheed stands', 'How exposed'], [
             ['Drone wingmen (CCA)', 'Lost Increment 1 hardware to Anduril and General Atomics; in the software pool', 'High: this is where cheap, fast and autonomous beats exquisite'],
             ['Low-cost missiles and counter-drone', 'Its long-range missiles are high-end; Anduril sells Barracuda cruise missiles and Roadrunner interceptors', 'Medium: a new low end of the market, not a replacement for the high end'],
             ['Missile defense (PAC-3, THAAD)', 'Sole producer, with seven-year agreements and $8B committed to new capacity', 'Low for now: years of qualification and production behind it'],
             ['F-35 and space', 'The only fifth-generation fighter in production for the U.S. and allies; 850 more U.S. jets planned', 'Low: no new entrant can build a crewed fighter or Trident this decade'],
         ])
         + prose('The threat is real but narrow so far. Anduril&rsquo;s wins come mostly in new categories the Pentagon is now funding (the 2027 request includes nearly $75 billion for unmanned and counter-drone systems), not in the programs that make up most of Lockheed&rsquo;s backlog. The bigger long-term risk is budget mix: if more money goes to large numbers of cheap autonomous systems and less to high-end platforms, the primes&rsquo; share of new spending shrinks even as their old programs keep running.')
         + src([('CCA production awards', ANDP), ('Pentagon drone budget', 'https://finance.yahoo.com/markets/stocks/articles/drone-stocks-down-defense-backlogs-115500190.html'), ('Anduril report', 'anduril.html')])),
        ('fin', 'The numbers', 'Steady sales, <em>squeezed by program charges.</em>',
         fin_table('LMT') + prose('Sales have grown about 3% a year since 2021, while operating income fell in 2024 and only partly recovered in 2025 because of losses on classified Aeronautics and Missiles programs and charges on fixed-price contracts. 2026 is the first year of a clear recovery: guidance implies about 8% sales growth and an operating margin back near 12%. The <a href="snapshot.html?t=LMT&amp;view=q">quarterly view</a> shows each quarter.')
         + src([('Lockheed Martin filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000936468&type=10-K')])),
        ('capital', 'Balance sheet and ownership', 'Buybacks paused, <em>the dividend raised again.</em>',
         prose('At the end of September Lockheed had $6.0 billion of cash and $20.5 billion of long-term debt, about $14.5 billion of net debt. It bought back no shares in the first nine months of 2026 (against $2.25 billion a year earlier) while it funds the munitions expansion and the pending purchase of Ultra Maritime, but it raised its dividend for the 24th year in a row. It expects to contribute more than $1 billion to its pension plan next year.',
                 'One item to watch: Lockheed&rsquo;s costs on the F-35 Lot 20 contract have run ahead of the funding authorized so far, and the company warns that results will suffer if negotiations on Lots 20 and later do not close. Lot 20 is now expected in 2027.')),
        ('value', 'Valuation', 'The model gives <em>$647 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Sales, 2026', '$81B', 'Guidance midpoint'],
             ['Growth, 2027 and 2028', '7%, then 6%', 'Management&rsquo;s high single-digit outlook; fades to 3% by year 10'],
             ['Operating margin', '11.5% rising to 12%', 'Segment margin plus the pension adjustment; F-35 production is accretive'],
             ['Reinvestment', '$1 for every $4 of new sales', 'Munitions capacity and working capital'],
             ['Discount rate', '8.1%', 'Beta 0.80 for defense peers (Lockheed&rsquo;s own is 0.48), 13% debt'],
             ['Terminal growth', '3.0%', 'With a 15% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$65B'), ('PV of terminal value', '$99B'), ('Enterprise value', '$164B'), ('Net debt', '&minus;$14.5B'), ('Equity value', '$150B'), ('Shares', '231.5M')], '$647')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '4% / 3%', '7% / 6%', '9% / 8%'], ['Long-run operating margin', '10.5%', '12%', '13%'],
             ['Discount rate', '9.1%', '8.1%', '7.1%'], ['Value per share', '$401', '$647', '$973'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$667</b>. The bear case is a budget squeeze after the midterms plus share lost to cheaper autonomous systems; the bull case is the munitions ramp and F-35 multi-year deal running ahead of plan.')
         + sens('Discount rate', ['7.0%', '7.5%', '8.0%', '8.5%', '9.0%'], ['$840', '$742', '$664', '$600', '$547'])),
        ('implied', 'What the price assumes', 'At $590, <em>about 4% growth.</em>',
         implied([['Sales growth of about 4% a year for two years, then the same fade', '7% and 6%'], ['Or a long-run operating margin of about 11%', '12%'], ['Or a discount rate of about 8.6%', '8.1%']])
         + prose('The price asks for less growth than management is guiding to, which is why the model sits above it. Before the results the shares were down 21% from their high as investors began to price in a Democratic Congress after the November 3 midterms, which could trim the proposed defense increase.')
         + src([('Defense stocks and the midterms', MIDT)])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Budgets and politics', 'A Democratic Congress could cut the proposed $500 billion increase or force long continuing resolutions.'],
             ['New entrants', 'Anduril and others are winning the fast-growing autonomous categories; the CCA loss shows it.'],
             ['Fixed-price programs', 'Charges on classified programs cut operating income in 2024 and 2025.'],
             ['F-35 funding', 'Lot 20 costs are already running ahead of authorized funding.'],
             ['Pension and buybacks', 'More than $1 billion of pension contributions next year and no buybacks this year.'],
         ]) + prose('<b>Upside:</b> missile defense demand that management calls &ldquo;permanent&rdquo;, a 10-year F-35 production path, Golden Dome missile-defense spending, and a return to buybacks once the munitions build-out is funded.')),
        ('rec', 'Rating', 'Hold. <em>Fairly priced, with a real but narrow threat.</em>',
         prose('Lockheed is the strongest of the primes on the work that matters most right now: interceptors and munitions, where it is the only supplier and has seven-year contracts. Anduril is taking the new drone and low-cost categories, and that will cap Lockheed&rsquo;s share of future budgets, but it does not touch the F-35, PAC-3, THAAD or Trident this decade. At $590.20 the shares are about 12% below our weighted value of $667: close to fair. We would buy nearer $550, or after the midterms if the budget holds up.')
         + band('The incumbent with the moat, <em>at about a fair price.</em>', 'Anduril wins the new categories; Lockheed still owns the ones with years of backlog.')),
    ])

# ================================================================ Northrop Grumman
NQ = 'https://www.sec.gov/Archives/edgar/data/0001133421/000113342126000037/noc-09302026xearningsrelea.htm'
NA = 'https://www.stocktitan.net/articles/northrop-grumman-q3-2026-earnings-record-backlog'
NC = 'https://www.fool.com/earnings/call-transcripts/2026/10/20/northrop-grumman-noc-q3-2026-earnings-call-transcript/'
R['NOC'] = dict(
    t='NOC', slug='northrop-grumman', name='Northrop Grumman', h1='Northrop <em>Grumman</em>', sector='Aerospace &amp; defense', date=D22, timing=', after its third-quarter results',
    sub='Northrop Grumman builds the B-21 stealth bomber, the Sentinel nuclear missile, satellites and rocket motors. Its backlog is a record $110 billion and its growth rests on two of the biggest programs in the defense budget. Anduril, valued privately at about $90 billion, is now worth more than Northrop&rsquo;s entire stock market value.',
    call='Hold', method='Cash-flow model', price=552.53, pricenote='Close, Oct 22, 2026', base=564, bear=329, bull=870, wt=582, max=1000, tick=100,
    disclosure='The author holds no NOC shares directly.',
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price and its 52-week range.',
    field=[('Cash-flow model', 329, 870, 564, '$329 to $870, base $564'), ('Probability-weighted', None, None, 582, '$582'),
           ('Price at writing', None, None, 552.53, '$552.53'), ('52-week range', 470, 774, None, '$470 to $774')],
    toc=toc_with('threat', 'The Anduril question'), chapters=[
        ('overview', 'The business', 'Bombers, ICBMs <em>and rocket motors.</em>',
         prose('Northrop has four segments. <b>Aeronautics</b> builds the B-21 Raider stealth bomber and parts of the F-35. <b>Defense Systems</b> holds <b>Sentinel</b>, the new intercontinental ballistic missile, along with munitions and missile components. <b>Mission Systems</b> makes radars, sensors and electronic warfare systems. <b>Space</b> builds satellites and is one of the largest makers of solid rocket motors.',
               'About 84% of sales go to the U.S. government. More than any other prime, Northrop&rsquo;s growth depends on two programs: the B-21 and Sentinel, both strategic nuclear systems with decades of work ahead.')),
        ('results', 'Latest results', 'Record backlog, <em>guidance raised.</em>',
         stats([('$11.1B', 'Sales, Q3 2026, +7%'), ('$7.89', 'Earnings per share'), ('$1.81B', 'Adjusted free cash flow'), ('$109.6B', 'Backlog, a record'), ('1.5&times;', 'Book-to-bill'), ('5&ndash;7%', '2027 sales growth outlook')])
         + prose('Third-quarter sales rose 7% to $11.1 billion, led by Aeronautics (+14%) and Defense Systems (+12%). Backlog reached a record $109.6 billion on $16.4 billion of new awards. Northrop kept 2026 sales guidance at $43.75&ndash;44.25 billion, raised segment operating income to $4.94&ndash;5.04 billion and adjusted earnings to $29.35&ndash;29.75 a share, and kept adjusted free cash flow at $3.1&ndash;3.5 billion.',
                 'For 2027 it expects sales growth of 5&ndash;7% with all four segments growing, margins up 10&ndash;20 basis points and free cash flow of $3.3&ndash;3.7 billion, with faster growth in 2028. The B-21 is meeting its test requirements, and the Air Force approved Sentinel&rsquo;s design maturity, allowing a first flight in 2027.')
         + src([('Q3 2026 results', NQ), ('Earnings call', NC), ('Backlog analysis', NA)])),
        ('threat', 'The Anduril question', 'Anduril is now worth <em>more than Northrop.</em>',
         prose('At about $90 billion in its October employee share sale, Anduril is valued above Northrop&rsquo;s market value of about $79 billion, on roughly a tenth of the revenue. That says more about how investors value growth than about who builds what, but the two do now compete. Northrop&rsquo;s own drone fighter, the <b>Talon Blue</b>, flew fully autonomously this quarter, yet the Air Force picked Anduril and General Atomics, not Northrop, to build the first drone wingmen in June. Anduril also makes solid rocket motors, a business where Northrop is one of the two largest suppliers and only resumed deliveries this quarter.')
         + table(['Market', 'Where Northrop stands', 'How exposed'], [
             ['Drone wingmen (CCA)', 'Talon Blue not selected for Increment 1; preparing for Increment 2; in the software pool', 'High'],
             ['Solid rocket motors', 'About $1 billion of work; deliveries resumed in Q3 after delays', 'Medium: Anduril and other new suppliers are adding capacity'],
             ['B-21 and Sentinel', 'Sole contractor on both, with production through the 2030s', 'Low: no new entrant can build a stealth bomber or ICBM'],
             ['Space and sensors', 'Large incumbent in satellites and radars', 'Medium over time, as cheaper satellite makers grow'],
         ])
         + prose('Northrop is more exposed than Lockheed to the shift toward cheap autonomous systems, because its newer bets (Talon Blue, rocket motors) sit exactly where the new entrants are strongest. Its core (the B-21 and Sentinel) is about as protected as anything in defense, but it is also the part most exposed to budget politics.')
         + src([('Talon Blue and the CCA decision', 'https://www.fool.com/investing/2026/10/17/usaf-doesnt-want-northrop-grummans-stealth-drone/'), ('CCA production awards', ANDP), ('Anduril report', 'anduril.html')])),
        ('fin', 'The numbers', 'Sales up a fifth <em>since 2021.</em>',
         fin_table('NOC') + prose('Operating income dropped in 2023 because of a $1.56 billion charge on the B-21&rsquo;s fixed-price early production lots, which Northrop is still working through (about $70&ndash;100 million of losses a quarter). 2021 figures include a gain on the sale of its IT services business. The <a href="snapshot.html?t=NOC&amp;view=q">quarterly view</a> shows each quarter.')
         + src([('Northrop Grumman filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001133421&type=10-K')])),
        ('capital', 'Balance sheet and ownership', 'Heavy investment, <em>modest free cash flow.</em>',
         prose('At the end of September Northrop had $3.7 billion of cash and $15.2 billion of debt, about $11.5 billion of net debt. It is spending heavily on new factories for the B-21, Sentinel and munitions: capital spending of about $2.1 billion in 2027, or 4.5% of sales, well above Lockheed&rsquo;s. That keeps free cash flow at about 8% of sales, which limits buybacks. Management says &ldquo;everything is on the table&rdquo; for its microelectronics and quantum businesses, including a separation.')),
        ('value', 'Valuation', 'The model gives <em>$564 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Sales, 2026', '$44.0B', 'Guidance midpoint'],
             ['Growth, 2027 and 2028', '6%, then 7%', 'Guided 5&ndash;7% for 2027, higher for 2028; fades to 3% by year 10'],
             ['Operating margin', '11.3% rising to 12%', '10&ndash;20 basis points a year, as guided'],
             ['Reinvestment', '$1 for every $3 of new sales', 'Heavy capital spending on new programs'],
             ['Discount rate', '8.0%', 'Beta 0.80 for defense peers (Northrop&rsquo;s own is 0.50), 16% debt'],
             ['Terminal growth', '3.0%', 'With a 15% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$34B'), ('PV of terminal value', '$58B'), ('Enterprise value', '$92B'), ('Net debt', '&minus;$11.5B'), ('Equity value', '$81B'), ('Shares', '143M')], '$564')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '3% / 3%', '6% / 7%', '8% / 9%'], ['Long-run operating margin', '10.5%', '12%', '13%'],
             ['Discount rate', '9.0%', '8.0%', '7.0%'], ['Value per share', '$329', '$564', '$870'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$582</b>. The bear case is a budget cut that slows the B-21 and Sentinel plus losses on fixed-price production; the bull case is faster B-21 production and a munitions ramp in 2027&ndash;2028.')
         + sens('Discount rate', ['7.0%', '7.5%', '8.0%', '8.5%', '9.0%'], ['$720', '$632', '$561', '$503', '$455'])),
        ('implied', 'What the price assumes', 'At $553, <em>roughly the plan.</em>',
         implied([['Sales growth of about 6.4% a year for two years', '6% and 7%'], ['Or a long-run operating margin of about 11.8%', '12%']])
         + prose('The price is close to our base case: investors are paying for roughly the growth management is guiding to, no more. Before its results the stock was 34% below its high and down 9% for the year, the worst of the primes, because the B-21 and Sentinel are the programs a Democratic Congress is most likely to slow.')
         + src([('Defense stocks and the midterms', MIDT)])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Budgets and politics', 'The B-21 and Sentinel are the most exposed programs if Congress trims the increase.'],
             ['Fixed-price B-21 lots', 'The early production lots are loss-making; more charges are possible.'],
             ['New entrants', 'Anduril and others are taking drones and adding rocket-motor capacity.'],
             ['Sentinel cost', 'The program&rsquo;s cost growth has drawn scrutiny; production is not yet priced.'],
             ['Cash flow', 'Heavy capital spending keeps free cash flow near 8% of sales.'],
         ]) + prose('<b>Upside:</b> faster B-21 production, a munitions and rocket-motor ramp from 2027, Golden Dome space work, and a separation of the microelectronics business.')),
        ('rec', 'Rating', 'Hold. <em>Protected programs, exposed budgets.</em>',
         prose('Northrop owns two of the most protected programs in defense, and no new entrant can build a stealth bomber or an ICBM. Its newer bets, though, sit exactly where Anduril is strongest, and its growth depends on budgets that the midterms put in question. At $552.53 the shares are about 5% below our weighted value of $582: fairly priced for the plan. We prefer Lockheed for its missile-defense backlog and would buy Northrop nearer $480.')
         + band('The most protected programs, <em>and the most political.</em>', 'Northrop&rsquo;s core is safe from Anduril; its budget is not safe from Congress.')),
    ])

# ================================================================ Caterpillar
CQ = 'https://www.prnewswire.com/news-releases/caterpillar-reports-second-quarter-2026-results-302841940.html'
CC = 'https://finance.biggo.com/news/US_CAT_2026-08-04'
R['CAT'] = dict(
    t='CAT', slug='caterpillar', name='Caterpillar', h1='Caterpillar', sector='Machinery &amp; power', date=D22, timing=', ahead of its third-quarter results on October 29',
    sub='Caterpillar is the world&rsquo;s largest maker of construction and mining equipment, and it has quietly become one of the biggest suppliers of power for AI data centers: gas engines, generators and turbines. Its backlog has nearly doubled to $72 billion. The shares ran past $1,000 and have fallen about 30% since.',
    call='Watch', method='Cash-flow model', price=703.84, pricenote='Close, Oct 22, 2026', base=442, bear=256, bull=676, wt=454, max=1200, tick=200,
    disclosure='The author holds no CAT shares.',
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Cash-flow model', 256, 676, 442, '$256 to $676, base $442'), ('Probability-weighted', None, None, 454, '$454'),
           ('Price at writing', None, None, 703.84, '$703.84'), ('52-week range', 510, 1073, None, '$510 to $1,073'), ('Analyst average', None, None, 922, '$922')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Bulldozers, mining trucks <em>and data-center power.</em>',
         prose('Caterpillar has three equipment segments of similar size. <b>Construction Industries</b> sells excavators, loaders and bulldozers. <b>Resource Industries</b> sells mining trucks and equipment. <b>Power &amp; Energy</b> makes engines, generator sets, gas turbines (through Solar Turbines) and rail locomotives. <b>Financial Products</b> lends to customers and dealers.',
               'Power &amp; Energy is the story. Data centers need on-site generation, both as backup and, increasingly, as their main supply where the grid cannot keep up. Caterpillar&rsquo;s power generation sales rose 72% last quarter, gas engine orders now stretch into late 2028 and turbine orders into 2029&ndash;2030. It is restarting a mothballed 10-megawatt gas engine line to add 1.5 gigawatts of capacity, on top of a target of 65 gigawatts by 2030.')),
        ('results', 'Latest results', 'The first <em>$20 billion quarter.</em>',
         stats([('$20.5B', 'Sales, Q2 2026, +24%'), ('21.9%', 'Adjusted operating margin'), ('$8.17', 'Adjusted EPS, +73%'), ('$72B', 'Backlog, +92%'), ('+72%', 'Power generation sales'), ('$5.1B', 'Free cash flow, quarter')])
         + prose('Second-quarter sales rose 24% to a record $20.5 billion and adjusted earnings per share 73%. All three segments grew: Construction 35%, Resource 20% and Power &amp; Energy 17%, with margins of 23%, 15% and 25%. Backlog reached $72 billion, up $35 billion in a year, and 59% of it is expected to ship within twelve months.',
                 'Caterpillar raised its 2026 outlook to sales growth in the mid-to-high teens and free cash flow in the top half of its $6&ndash;15 billion range, with about $2.2 billion of tariff costs. The operating profit included $392 million of expected refunds of IEEPA tariffs. Third-quarter results come on <b>October 29</b>.')
         + src([('Q2 2026 results', CQ), ('Results with segment detail, SEC', 'https://www.sec.gov/Archives/edgar/data/0000018230/000001823026000040/ex991toformcat2q2026earnin.htm'), ('Earnings call', CC)])),
        ('fin', 'The numbers', 'A record year <em>after two flat ones.</em>',
         fin_table('CAT') + prose('Sales were flat from 2023 to 2025 as construction demand cooled; operating income fell in 2025 as tariffs and lower prices hit margins. 2026 is a sharp reacceleration, driven by data-center power and a construction rebound. The table includes Cat Financial, whose loans are funded by its own debt.')
         + src([('Caterpillar filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000018230&type=10-K')])),
        ('capital', 'Balance sheet and ownership', 'Low machinery debt, <em>steady buybacks.</em>',
         prose('Caterpillar&rsquo;s balance sheet has two halves. The machinery business had $5.9 billion of cash and $11.0 billion of debt at the end of June, about $5 billion of net debt. Cat Financial carries another $35 billion of debt, matched by the loans it makes to customers, so this model leaves it out. Caterpillar bought back $1.5 billion of stock and paid $0.7 billion of dividends in the second quarter, and plans about $3.5 billion of capital spending this year.')),
        ('value', 'Valuation', 'The model gives <em>$442 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Sales, 2026', '$78B', 'Estimate: 2025&rsquo;s $67.6B plus the guided mid-to-high-teens growth'],
             ['Growth, 2027 and 2028', '8%, then 6%', 'Power backlog ships; construction slows; fades to 3% by year 10'],
             ['Operating margin', '20% rising to 21%', 'Adjusted margin, less the one-off tariff refunds'],
             ['Reinvestment', '$1 for every $3 of new sales', 'New engine and turbine capacity'],
             ['Discount rate', '9.7%', 'Beta 1.05, 3% machinery debt'],
             ['Terminal growth', '3.0%', 'With a 20% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$98B'), ('PV of terminal value', '$112B'), ('Enterprise value', '$209B'), ('Machinery net debt', '&minus;$5.0B'), ('Equity value', '$204B'), ('Shares', '462.5M')], '$442')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '0% / 2%', '8% / 6%', '12% / 10%'], ['Long-run operating margin', '17%', '21%', '23%'],
             ['Discount rate', '10.7%', '9.7%', '8.7%'], ['Value per share', '$256', '$442', '$676'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$454</b>. The bear case is the usual machinery downturn arriving as data-center orders normalise; the bull case keeps power growing at double digits through 2028.')
         + sens('Discount rate', ['8.5%', '9.0%', '9.5%', '10.0%', '10.5%'], ['$537', '$492', '$454', '$422', '$394'])),
        ('implied', 'What the price assumes', 'At $704, <em>18% growth for two years.</em>',
         implied([['Sales growth of about 18% a year in 2027 and 2028, then the same fade', '8% and 6%'], ['Or a long-run operating margin of about 34%', '21%; Caterpillar has never sustained much above 21%']])
         + prose('Even after a 30% fall the shares trade at about 32 times forward earnings, a multiple Caterpillar has rarely held outside the bottom of a downturn. Analysts are more optimistic, with an average target of about $922, though several cut their targets this month on slowing bookings, dealer inventories and the risk that data-center power demand normalises.')
         + src([('The 30% fall', 'https://www.xtb.com/int/market-analysis/news-and-research/caterpillar-shares-extend-decline-down-30-from-record-high'), ('Target cuts', 'https://www.tradingkey.com/news/market-movers/262232614-market-movers-cat-20261022')])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['The machinery cycle', 'Construction and mining equipment has always been cyclical; Construction grew 35% last quarter.'],
             ['AI spending', 'Power &amp; Energy&rsquo;s growth depends on data-center build plans that could slow after 2027.'],
             ['Tariffs and costs', 'About $2.2 billion of tariff costs this year, plus rising diesel and material costs.'],
             ['Valuation', 'At about 32 times forward earnings, a normal downturn would hit the shares hard.'],
         ]) + prose('<b>Upside:</b> a power backlog that keeps growing, turbines sold out into 2030, new engine capacity from late 2026, and more tariff refunds.')),
        ('rec', 'Rating', 'Watch. <em>A great power business inside a cyclical company.</em>',
         prose('Caterpillar has turned into one of the clearest ways to own the power needed for AI, and its backlog makes the next two years visible. But about 60% of the company is still construction and mining equipment, and even after a 30% fall the price assumes growth of about 18% a year for two more years. At $703.84 the shares are about 55% above our weighted value of $454. It is on the watchlist; we would look again nearer $500, or after a quarter that shows power orders still accelerating. Results come on October 29.')
         + band('The AI power trade, <em>at an AI price.</em>', 'The engines are sold out; the shares already know it.')),
    ])

# ================================================================ ASML
XQ = 'https://www.stocktitan.net/articles/asml-q3-2026-earnings-ai-chip-machine-demand'
XV = 'https://investor.asml.com/news-releases/news-release-details/asml-reports-eu11.7-billion-total-net-sales-and-eu5.0-billion-net-income-q3-2026'
R['ASML'] = dict(
    t='ASML', slug='asml', name='ASML Holding', h1='ASML', sector='Chip equipment', date=D22, timing=', after its third-quarter results',
    sub='ASML, based in the Netherlands, is the only company in the world that makes extreme ultraviolet (EUV) lithography machines, without which no leading-edge chip can be made. Sales are up 36% this year, it says demand will outrun its capacity through 2028, and its shares trade in New York as ADRs. All figures are converted to U.S. dollars at $1.123 per euro.',
    call='Watch', method='Cash-flow model', price=1560.54, pricenote='Close, Oct 22, 2026', base=1081, bear=524, bull=1653, wt=1085, max=2200, tick=200,
    disclosure='The author holds no ASML shares directly; ASML is held inside the VanEck Semiconductor ETF (SMH) in the author&rsquo;s portfolio.',
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Cash-flow model', 524, 1653, 1081, '$524 to $1,653, base $1,081'), ('Probability-weighted', None, None, 1085, '$1,085'),
           ('Price at writing', None, None, 1560.54, '$1,560.54'), ('52-week range', 946, 2000, None, '$946 to $2,000'), ('Analyst average', None, None, 2079, '$2,079')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'The only maker <em>of the machine every chip needs.</em>',
         prose('Lithography machines print a chip&rsquo;s circuits onto silicon wafers with light. ASML makes three kinds: <b>EUV</b>, which only it can build and which is needed for every leading-edge logic chip and, increasingly, for DRAM and HBM memory; older <b>DUV</b> machines, where it competes with Nikon and Canon; and <b>High-NA EUV</b>, the next generation, now being tested by chipmakers. About 28% of sales come from servicing and upgrading the machines already installed.',
               'An EUV machine costs about $200 million and takes many months to build, so ASML&rsquo;s sales follow its customers&rsquo; factory plans: TSMC, Samsung, Intel, SK Hynix and Micron. The AI build-out has pushed all of them to add leading-edge capacity at once.')),
        ('results', 'Latest results', 'Sales up 55%, <em>demand ahead of supply.</em>',
         stats([('&euro;11.7B', 'Sales, Q3 2026, +55%'), ('57.5%', 'Gross margin'), ('&euro;5.0B', 'Net income'), ('17', 'EUV machines sold'), ('&euro;14.2&ndash;15.2B', 'Q4 sales guidance'), ('&euro;44&ndash;45B', '2026 sales guidance, +36%')])
         + prose('Third-quarter sales rose 55% to &euro;11.7 billion ($13.1 billion), with a record 57.5% gross margin and 121 machines sold, including 17 EUV. Net income of &euro;5.0 billion included a &euro;510 million gain on its stake in Mistral AI. Customer prepayments rose &euro;5.7 billion in the quarter, the clearest sign of new orders now that ASML no longer reports bookings.',
                 'ASML guided to &euro;14.2&ndash;15.2 billion of fourth-quarter sales and &euro;44&ndash;45 billion for 2026, up 36%, at a 56% gross margin. It plans to raise EUV and DUV capacity by 30% in 2027 and says even that will not meet customer demand in 2027 or 2028; price increases should come through partly in 2027 and fully from 2028. China fell to 23% of machine sales from 42% a year earlier.')
         + src([('Q3 2026 results', XV), ('Analysis', XQ)])),
        ('fin', 'The numbers', 'Flat for two years, <em>then up a third.</em>',
         table(['', '2023', '2024', '2025', '2026 guidance'], [
             ['Sales', '&euro;27.6B', '&euro;28.3B', '&euro;32.7B', '&euro;44&ndash;45B'],
             ['In U.S. dollars, at $1.123', '$31.0B', '$31.7B', '$36.7B', '$49&ndash;51B'],
             ['Gross margin', '51.3%', '51.3%', '52.8%', 'about 56%'],
             ['Net income', '&euro;7.8B', '&euro;7.6B', '&euro;9.6B', '&mdash;'],
         ], 'allnum')
         + prose('ASML reports in euros under IFRS, in an annual report filed with the SEC as a 20-F, so the site&rsquo;s automatic tables do not cover it; these figures come from its results releases. Sales stalled in 2023&ndash;2024 as memory makers cut spending and China export rules tightened, then accelerated as AI demand reached every leading-edge customer at once.')
         + src([('2025 results', 'https://www.dukascopy.com/swiss/it/marketwatch/market-news/Stock-Analysis/154194/'), ('ASML filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000937966&type=20-F')])),
        ('capital', 'Balance sheet and ownership', 'Net cash, <em>and &euro;12 billion of buybacks.</em>',
         prose('At the end of September ASML had &euro;12.7 billion of cash and short-term investments against bonds of roughly &euro;3 billion (an estimate; the latest balance sheet has the exact figure), giving about &euro;9 billion ($10 billion) of net cash. It bought back &euro;4.1 billion of stock in the quarter under a program of up to &euro;12 billion running to 2028, and pays an interim dividend of &euro;1.88 a share in November. Each ADR is one ordinary share; there are about 383 million.')),
        ('value', 'Valuation', 'The model gives <em>$1,081 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Sales, 2026', '$50.0B', 'Guidance midpoint, &euro;44.5B at $1.123'],
             ['Growth, 2027 and 2028', '22%, then 15%', '30% more capacity plus price; fades to 3% by year 10'],
             ['Operating margin', '41.5% rising to 44%', 'Q3 was 44.4%; R&amp;D stays high for High-NA'],
             ['Reinvestment', '$1 for every $3 of new sales', 'New capacity and working capital'],
             ['Discount rate', '11.0%', 'Beta 1.30, no net debt'],
             ['Terminal growth', '3.0%', 'With a 30% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$195B'), ('PV of terminal value', '$209B'), ('Enterprise value', '$404B'), ('Net cash', '$10B'), ('Equity value', '$414B'), ('Shares', '383M')], '$1,081')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '8% / 5%', '22% / 15%', '30% / 20%'], ['Long-run operating margin', '36%', '44%', '47%'],
             ['Discount rate', '12.0%', '11.0%', '10.0%'], ['Value per share', '$524', '$1,081', '$1,653'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$1,085</b>. The bear case is the chip-equipment downturn that usually follows a capacity boom; the bull case is shortage pricing and High-NA adoption lifting margins toward 47%.')
         + sens('Discount rate', ['9.5%', '10.0%', '10.5%', '11.0%', '11.5%'], ['$1,336', '$1,239', '$1,155', '$1,081', '$1,016'])),
        ('implied', 'What the price assumes', 'At $1,561, <em>26% growth for two years.</em>',
         implied([['Sales growth of about 26% a year in 2027 and 2028, then the same fade', '22% and 15%'], ['Or a long-run operating margin far above anything ASML has earned', '44%'], ['Or a discount rate near 9%', '11.0%']])
         + prose('ASML has never been cheap: its monopoly in EUV has earned it a premium for a decade. At about 25 times next year&rsquo;s expected earnings the shares are pricing in something close to our bull case. The analysts&rsquo; average target is about $2,079. The shares fell about 7% today as Lam Research warned that clean-room space and parts will limit the whole chip-equipment industry into 2027.')
         + src([('Analyst targets', 'https://www.marketbeat.com/instant-alerts/price-asml-nasdaq-asml-shares-climb-28-heres-what-happened-2026-10-21/'), ('Supply warning', 'https://247wallst.com/investing/2026/10/22/chip-stocks-fall-as-supply-warning-deepens-ai-selloff-marvell-and-amd-sink-8-intel-drops-7/')])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['The equipment cycle', 'Chipmakers buy in waves; a pause after the AI build-out would hit orders hard.'],
             ['Supply limits', 'Its own capacity and its suppliers&rsquo; cap how fast sales can grow through 2028.'],
             ['China and export rules', 'China fell from 42% to 23% of machine sales in a year; new rules could cut more.'],
             ['Customer concentration', 'TSMC, Samsung, SK Hynix, Micron and Intel buy almost all EUV machines.'],
             ['Currency', 'Results are in euros; a stronger euro lowers the dollar value of the ADR&rsquo;s earnings.'],
         ]) + prose('<b>Upside:</b> EUV price increases from 2027, High-NA adoption, memory makers moving more layers to EUV, and a new 2030 target at the June 2027 investor day.')),
        ('rec', 'Rating', 'Watch. <em>The best moat in chips, at a full price.</em>',
         prose('No company in the AI supply chain has a stronger position: every leading-edge chip runs through ASML&rsquo;s machines, and demand is ahead of its capacity for at least two years. At $1,560.54, though, the price needs growth close to our bull case, about 44% above our weighted value of $1,085. ASML is already part of the portfolio through SMH. As a direct holding we would look again nearer $1,100.')
         + band('A monopoly, <em>priced like one.</em>', 'The machines are irreplaceable; the shares already assume it.')),
    ])

# ================================================================ SK hynix
HQ = 'https://news.skhynix.com/en/q2-2026-business-results/'
HC = 'https://www.investing.com/news/transcripts/earnings-call-transcript-sk-hynix-posts-record-q2-2026-results-as-shares-fall-93CH-4818480'
R['SKHY'] = dict(
    t='SKHY', slug='sk-hynix', name='SK hynix', h1='SK <em>hynix</em>', sector='Memory chips', date=D22, timing=', ahead of its third-quarter results on October 29 in Seoul',
    sub='SK hynix, based in South Korea, makes about half of the world&rsquo;s HBM, the stacked memory that sits beside every Nvidia AI chip. Its operating margin reached 76% last quarter. Since July its shares have also traded in New York as ADRs (ten ADRs equal one Korean share). Figures are in won, converted at about &#8361;1,327 per dollar.',
    call='Watch', method='Cycle model', price=131.69, pricenote='ADR close, Oct 22, 2026', base=111, bear=60, bull=215, wt=124, max=280, tick=40,
    disclosure='The author holds no SK hynix shares or ADRs.',
    fieldnote='Per ADR, in dollars: the cycle model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its range since the July listing and the analysts&rsquo; consensus target.',
    field=[('Cycle model', 60, 215, 111, '$60 to $215, base $111'), ('Probability-weighted', None, None, 124, '$124'),
           ('Price at writing', None, None, 131.69, '$131.69'), ('Range since listing', 125, 200, None, '$125 to $200'), ('Analyst consensus', None, None, 253, '$253')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'The leader <em>in AI memory.</em>',
         prose('SK hynix makes <b>DRAM</b>, the working memory in every computer, and <b>NAND</b> flash for storage. Its edge is <b>HBM</b>: high-bandwidth memory made by stacking DRAM chips, which Nvidia and other AI chipmakers place next to each accelerator. SK hynix was first to supply HBM at scale to Nvidia and held about 50% of the market in the second quarter, ahead of Samsung (33%) and Micron (18%). It began mass shipments of the newest generation, <b>HBM4</b>, for Nvidia&rsquo;s Vera Rubin platform this year.',
               'It is the same industry as <a href="micron.html">Micron</a>, with the same cycle: three companies make nearly all the world&rsquo;s DRAM, and prices rise and fall with the balance between their new factories and demand.')),
        ('results', 'Latest results', 'A 76% operating margin, <em>and a sixth record coming.</em>',
         stats([('&#8361;79.3T', 'Revenue, Q2 2026, +257% (about $60B)'), ('76%', 'Operating margin'), ('&#8361;60.5T', 'Operating profit (about $46B)'), ('&#8361;69.4T', 'Net cash (about $52B)'), ('&#8361;77T', 'Q3 operating profit, consensus'), ('~10', 'Customers on long-term agreements')])
         + prose('Second-quarter revenue rose 257% from a year earlier to &#8361;79.3 trillion and operating profit 557% to &#8361;60.5 trillion, a 76% margin. Net profit of &#8361;93.9 trillion was even higher than operating profit because of large gains outside its operations. HBM4 mass shipments began in the quarter and ramp through the second half; the company has signed long-term agreements of about five years, with deposits and volume commitments, with about ten customers.',
                 'Korean analysts expect third-quarter operating profit of about &#8361;77 trillion, a sixth straight record, as DRAM prices rose about 22% and NAND about 15% in the quarter. Results come on <b>October 29</b> in Seoul (the evening of October 28 in New York). On October 22 Bernstein estimated that Samsung overtook SK hynix in HBM revenue in the third quarter, $8.7 billion to $7.6 billion, and the ADRs fell about 8%.')
         + src([('Q2 2026 results', HQ), ('Earnings call', HC), ('Q3 expectations', 'https://www.mt.co.kr/en/industry/2026/10/19/2026101913371799572'), ('Bernstein HBM estimate', 'https://www.investing.com/news/stock-market-news/bernstein-says-samsung-overtook-sk-hynix-in-hbm-revenue-in-3q26-93CH-4965188')])),
        ('fin', 'The numbers', 'A loss in 2023, <em>&#8361;98 trillion of profit in half a year.</em>',
         table(['&#8361; trillion', '2023', '2024', '2025', 'H1 2026'], [
             ['Revenue', '32.8', '66.2', '97.1', '131.9'],
             ['Operating profit', '&minus;7.7', '23.5', '47.2', '98.2'],
             ['Operating margin', '&minus;24%', '35%', '49%', '74%'],
             ['Net profit', '&minus;9.1', '19.8', '42.9', '134.3'],
             ['Revenue in US$, at &#8361;1,327', '$25B', '$50B', '$73B', '$99B'],
         ], 'allnum')
         + prose('SK hynix reports in won under Korean accounting standards, so the site&rsquo;s automatic SEC tables do not cover it; these figures come from its results releases. The swing from a &#8361;7.7 trillion operating loss in 2023 to &#8361;98 trillion of operating profit in the first half of 2026 is the memory cycle in one row. First-half 2026 net profit includes large non-operating gains. Dollar figures use today&rsquo;s exchange rate, so earlier years are shown at a stronger won than they were.')
         + src([('2025 results', 'https://www.storagenewsletter.com/2026/02/10/sk-hynix-fiscal-4q25-and-fy25-financial-results/'), ('Q2 2026 results', HQ)])),
        ('capital', 'Balance sheet and supply', '&#8361;69 trillion of net cash, <em>new fabs from 2027.</em>',
         prose('At the end of June SK hynix had &#8361;88 trillion of cash against &#8361;18.6 trillion of debt. In July it listed ADRs on the Nasdaq under SKHY, issuing up to 17.79 million new shares (about 2.4% more) for up to about $29 billion; this model adds that to net cash, about $80 billion in all. Capital spending will reach the high &#8361;40 trillions this year (about $35 billion). New capacity comes from the M15X fab, pulled forward, and the first Yongin cleanroom in early 2027.',
               'Management says it does not expect its investment plans to cause oversupply soon and that tight conditions should last &ldquo;for a considerable period&rdquo;. It is weighing more shareholder returns, with analysts expecting buybacks of more than &#8361;30 trillion.')),
        ('value', 'Valuation', 'Our cycle model gives <em>$111 an ADR.</em>',
         prose('The same method as Micron: free cash flow for 2027&ndash;2030 at each scenario&rsquo;s prices, then an exit value on <i>mid-cycle</i> earnings, all discounted at 14% (a high beta plus Korea and memory-cycle risk), plus net cash, over about 7.4 billion ADR-equivalents (an estimate of 740 million Korean shares outstanding after the July offering, net of treasury shares).')
         + scen([['Revenue, 2027 / 2028', '$280B / $230B', '$330B / $350B', '$380B / $450B'], ['Revenue, 2029 / 2030', '$150B / $120B', '$240B / $180B', '$400B / $350B'], ['Free cash flow, four years', '$228B', '$417B', '$763B'],
                 ['Mid-cycle revenue and operating margin', '$150B at 25%', '$210B at 35%', '$320B at 45%'], ['Exit multiple', '10&times;', '12&times;', '14&times;'],
                 ['Value per ADR', '$60', '$111', '$215'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$124</b>. This year&rsquo;s revenue should be about &#8361;340 trillion ($256 billion), an estimate from the first two quarters and analysts&rsquo; third- and fourth-quarter forecasts; the base case grows it another 30% in 2027 as HBM4 ramps, then has prices fall as new supply arrives from 2028, to a mid-cycle margin still far above anything before AI.')),
        ('implied', 'What the price assumes', 'At $132, <em>today&rsquo;s profits last.</em>',
         implied([['About $80 billion of after-tax profit a year from 2031, valued at 12&times;, after the base case&rsquo;s cash flows', '2025 net profit was &#8361;42.9T, about $32B'], ['Or the bull case: revenue staying above $350 billion through 2030', 'New supply from all three makers arrives from 2027&ndash;2028']])
         + prose('The price sits just above our weighted value. Analysts are far more optimistic, with a consensus target of about $253, and the shares trade at about 8 times trailing earnings. As with Micron, that multiple looks cheap only if peak earnings are close to normal.')
         + src([('Analyst targets', 'https://www.marketbeat.com/instant-alerts/price-sk-hynix-nasdaq-skhy-shares-up-25-heres-why-2026-10-21/')])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['The cycle', 'Every past memory boom ended when new fabs came online; Samsung, Micron and SK hynix are all adding capacity.'],
             ['HBM share', 'Samsung is gaining ground and may have overtaken SK hynix in HBM revenue in the third quarter.'],
             ['Customer concentration', 'Nvidia is the largest HBM buyer by far.'],
             ['China', 'CXMT, China&rsquo;s DRAM maker, is closing the technology gap at the low end.'],
             ['Currency', 'A 10% stronger won cuts pre-tax profit by about &#8361;1.2 trillion and changes the dollar value of everything here.'],
         ]) + prose('<b>Upside:</b> HBM4 prices up sharply through 2027, long-term agreements that smooth the next downturn, large buybacks, and a cash pile that could approach $100 billion.')),
        ('rec', 'Rating', 'Watch. <em>The best position in memory, at peak conditions.</em>',
         prose('SK hynix earned the AI memory boom: first to HBM at scale, the largest share of Nvidia&rsquo;s supply and a 76% margin. Compared with Micron it looks cheaper, only about 6% above our weighted value against Micron&rsquo;s 27%. But it is still a memory company at the top of its cycle, Samsung is catching up in HBM, and its home currency adds a risk Micron does not have. At $131.69 we would watch the October 29 results; nearer $110, our base case, it would be the better of the two memory makers to own.')
         + band('The HBM leader, <em>closer to fair than its rivals.</em>', 'The cycle still decides; the price leaves less to go wrong than Micron&rsquo;s.')),
    ])


# ================================================================ October 22 additions, batch 2: Microsoft, Alphabet, TSMC
MSQ = 'https://news.microsoft.com/source/2026/07/29/microsoft-cloud-and-ai-strength-fuels-fourth-quarter-results-4/'
MSC = 'https://valueaddvc.com/pulse/microsoft-azure-100-billion-fy27-capex-2026'
R['MSFT'] = dict(
    t='MSFT', slug='microsoft', name='Microsoft', h1='Microsoft', sector='Software &amp; cloud', date=D22, timing=', ahead of its first-quarter fiscal 2027 results',
    sub='Microsoft sells the software most businesses run on and rents the second-largest cloud in the world, Azure, which just passed $100 billion of annual revenue growing 43%. It also owns about 27% of OpenAI. The question is what all the AI spending, about $257 billion this fiscal year, will earn.',
    call='Hold', method='Cash-flow model', price=521.08, pricenote='Close, Oct 22, 2026', base=377, bear=220, bull=559, wt=383, max=700, tick=100,
    disclosure='The author holds no MSFT shares directly.',
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Cash-flow model', 220, 559, 377, '$220 to $559, base $377'), ('Probability-weighted', None, None, 383, '$383'),
           ('Price at writing', None, None, 521.08, '$521.08'), ('52-week range', 349, 554, None, '$349 to $554'), ('Analyst average', None, None, 559, '$559')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Office, Windows, <em>and the cloud behind them.</em>',
         prose('Microsoft reports three segments. <b>Productivity and Business Processes</b> (42% of last quarter&rsquo;s revenue) is Microsoft 365, LinkedIn and Dynamics. <b>Intelligent Cloud</b> (44%) is Azure, server software and GitHub. <b>More Personal Computing</b> (14%) is Windows, Xbox, Surface and search advertising.',
               'AI runs through all three: Copilot is sold inside Microsoft 365 (more than 30 million paid seats), and Azure rents computing to companies building AI, including OpenAI, in which Microsoft holds about 27% after OpenAI&rsquo;s 2025 restructuring.')),
        ('results', 'Latest results', 'Azure up 43%, <em>past $100 billion a year.</em>',
         stats([('$90.0B', 'Revenue, Q4 FY2026, +18%'), ('$40.6B', 'Operating income, +18%'), ('+43%', 'Azure growth'), ('$678B', 'Commercial backlog, +84%'), ('$331.8B', 'Revenue, fiscal 2026, +18%'), ('$255&ndash;260B', 'Fiscal 2027 capex guidance')])
         + prose('In the quarter to June, revenue rose 18% to $90.0 billion and operating income 18% to $40.6 billion. Intelligent Cloud grew 32%, Productivity 14% and More Personal Computing fell 4%. Earnings of $4.81 a share included a $3.2 billion gain on Microsoft&rsquo;s stake in Anthropic. For the full fiscal year revenue was $331.8 billion and operating income $155.2 billion.',
                 'Contracted backlog rose 84% to $678 billion, though only about 25% excluding OpenAI, so one customer drives most of it. Microsoft guided first-quarter Azure growth to about 45% and fiscal 2027 capital spending to $255&ndash;260 billion including finance leases, up from about $190 billion. The shares fell about 28% in the first half of 2026 and then rose 39% in the third quarter, the best quarter since 1991.')
         + src([('Q4 FY2026 results', MSQ), ('Capex guidance', MSC), ('Share price and targets', 'https://247wallst.com/investing/2026/10/01/microsoft-just-had-its-best-quarter-since-1991/')])),
        ('fin', 'The numbers', 'Profits up 85% in three years, <em>capex up fourfold.</em>',
         fin_table('MSFT') + prose('Revenue grew 57% between fiscal 2023 and 2026 and net income 85%, while capital spending (excluding finance leases) went from $28 billion to $116 billion. Free cash flow still rose, to about $67 billion, but it is now growing far more slowly than profit. Fiscal 2026 net income includes gains on the OpenAI and Anthropic stakes.')
         + src([('Microsoft filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K')])),
        ('capital', 'Balance sheet and ownership', 'Net cash, <em>and a quarter of OpenAI.</em>',
         prose('At the end of June Microsoft had $76.8 billion of cash and investments against $40.3 billion of debt. It owns about 27% of OpenAI on an as-converted basis, accounted for under the equity method, and has funded almost all of a $13 billion commitment. This model adds the stake at 27% of this site&rsquo;s own OpenAI base-case value of $790 billion, about $213 billion (an estimate; OpenAI is private). It returned $10.2 billion through dividends and buybacks last quarter.')),
        ('value', 'Valuation', 'The model gives <em>$377 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, fiscal 2026', '$331.8B', 'Reported'],
             ['Growth, fiscal 2027 and 2028', '17%, then 15%', 'Azure near 40%, the rest slower; fades to 3% by year 10'],
             ['Operating margin', '45%', 'Fiscal 2026 was 46.8%; AI depreciation rises'],
             ['Net investment, fiscal 2027&ndash;2030', '$180B, $140B, $100B, $70B', 'Capex less depreciation as the build-out peaks; then $1 per $2 of new revenue'],
             ['Discount rate', '10.0%', 'Beta 1.09, almost no net debt'],
             ['Terminal growth', '3.0%', 'With a 25% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$927B'), ('PV of terminal value', '$1,623B'), ('Enterprise value', '$2,550B'), ('Net cash and OpenAI stake', '$250B'), ('Equity value', '$2,800B'), ('Shares', '7.43B')], '$377')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, FY2027 / FY2028', '12% / 10%', '17% / 15%', '21% / 18%'], ['Long-run operating margin', '40%', '45%', '48%'],
             ['Net investment, first year', '$200B', '$180B', '$160B'], ['Discount rate', '11.0%', '10.0%', '9.0%'],
             ['Value per share', '$220', '$377', '$559'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$383</b>. The OpenAI stake is worth about $29 a share of that; without it the base case is about $348.')
         + sens('Discount rate', ['8.5%', '9.0%', '9.5%', '10.0%', '10.5%'], ['$486', '$443', '$407', '$376', '$350'])),
        ('implied', 'What the price assumes', 'At $521, <em>about 23% growth for two years.</em>',
         implied([['Revenue growth of about 23% a year in fiscal 2027 and 2028, then the same fade', '17% and 15%'], ['Or a long-run operating margin far above anything Microsoft has earned', '45%'], ['Or a discount rate near 8.7%', '10.0%']])
         + prose('The price asks for growth well above the company&rsquo;s recent 15&ndash;18%, or a quicker payback on the AI build-out than the model assumes. Analysts&rsquo; average target is about $559.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Capital spending', 'About $257 billion this fiscal year; if AI demand slows, the depreciation stays.'],
             ['OpenAI concentration', 'Most of the backlog growth comes from one customer, which is also diversifying to other clouds.'],
             ['Copilot pricing', 'Seats are growing, but it is not yet clear how much extra revenue per user AI adds.'],
             ['Competition', 'Amazon and Google are adding cloud capacity just as fast; Google Cloud grew 82% last quarter.'],
         ]) + prose('<b>Upside:</b> Azure growth staying above 40%, Copilot pricing moving to per-seat plus usage, and OpenAI&rsquo;s value rising toward its latest private marks.')),
        ('rec', 'Rating', 'Hold.',
         prose('placeholder')
         + band('The best software franchise, <em>in its most expensive build.</em>', 'Azure and Copilot are working; the capex bill decides the return.')),
    ])

ALQ = 'https://finance.yahoo.com/markets/stocks/articles/alphabet-q2-2026-earnings-revenue-203058727.html'
ALP = 'https://www.top1markets.com/news/alphabet-q3-2026-earnings-preview-cloud-capex'
ALS = 'https://valueaddvc.com/pulse/google-94b-spacex-124b-anthropic-stakes-2026'
R['GOOGL'] = dict(
    t='GOOGL', slug='alphabet', name='Alphabet', h1='Alphabet', sector='Internet &amp; cloud', date=D22, timing=', ahead of its third-quarter results on October 28',
    sub='Alphabet owns Google Search, YouTube, Android and Google Cloud, which grew 82% last quarter. It is spending about $200 billion this year on AI data centers and has started selling new shares to help pay for it. It also owns stakes in SpaceX and Anthropic worth more than $200 billion.',
    call='Hold', method='Cash-flow model', price=324.22, pricenote='Close, Oct 22, 2026 (Class A)', base=249, bear=139, bull=380, wt=254, max=500, tick=100,
    disclosure='The author holds no Alphabet shares directly.',
    fieldnote='The cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Cash-flow model', 139, 380, 249, '$139 to $380, base $249'), ('Probability-weighted', None, None, 254, '$254'),
           ('Price at writing', None, None, 324.22, '$324.22'), ('52-week range', 252, 409, None, '$252 to $409'), ('Analyst average', None, None, 435, '$435')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'Search pays for <em>everything else.</em>',
         prose('<b>Google Services</b> (79% of last quarter&rsquo;s revenue) is Search, YouTube, Android, Chrome and subscriptions such as YouTube Premium and Google One. <b>Google Cloud</b> (21%) rents computing, including Google&rsquo;s own TPU AI chips, and sells Workspace and the Gemini models to businesses. <b>Other Bets</b> includes Waymo.',
               'Search still produces most of the profit. The AI question for Alphabet runs both ways: Gemini and AI Overviews have to keep Search growing while chatbots compete for the same questions, and Cloud has become one of the main ways AI labs rent computing.')),
        ('results', 'Latest results', 'Cloud up 82%, <em>free cash flow negative.</em>',
         stats([('$119.8B', 'Revenue, Q2 2026, +24%'), ('34%', 'Operating margin'), ('$24.8B', 'Google Cloud, +82%'), ('$514B', 'Cloud backlog'), ('&minus;$5.9B', 'Free cash flow, first negative quarter'), ('$195&ndash;205B', '2026 capex guidance')])
         + prose('Second-quarter revenue rose 24% to $119.8 billion and operating income 30% to $40.8 billion. Search grew 17%, YouTube ads 13% and Cloud 82%, with Cloud&rsquo;s operating income tripling to $8.8 billion. Net income of $112.1 billion included about $98 billion of unrealized gains on the SpaceX and Anthropic stakes.',
                 'Capital spending was $44.9 billion in the quarter and free cash flow turned negative for the first time. Alphabet raised 2026 capex guidance to $195&ndash;205 billion, sold $49.6 billion of new shares in June, issued $20.3 billion of bonds and plans a $40 billion at-the-market share program. The shares fell 7% the next day. Third-quarter results come on <b>October 28</b>.')
         + src([('Q2 2026 results', ALQ), ('Q3 preview and funding', ALP)])),
        ('fin', 'The numbers', 'Profits more than doubled; <em>so did capex.</em>',
         fin_table('GOOGL') + prose('Revenue grew 42% between 2022 and 2025 and capital spending almost tripled. The last twelve months&rsquo; net income of about $244 billion is inflated by gains on investments; operating income of $148 billion is the better guide. The <a href="snapshot.html?t=GOOGL&amp;view=q">quarterly view</a> shows each quarter.')
         + src([('Alphabet filings, SEC EDGAR', 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K')])),
        ('capital', 'Balance sheet and ownership', 'Selling shares <em>to fund the build.</em>',
         prose('Alphabet&rsquo;s June share sale and bond issue mark a turn for a company that had bought back stock for years. This model counts net cash of about $100 billion (an estimate after the new funding) plus the stakes disclosed in its June 10-Q: about 6% of SpaceX, worth $94.1 billion, and about 14% of Anthropic, about $124 billion. The stakes alone add about $18 a share, and about $26 with net cash. Most of the SpaceX stake cannot be sold until lock-ups end.',
               'The at-the-market program will add shares; the model uses about 12.25 billion, a little above today&rsquo;s count. Larry Page and Sergey Brin control the vote through Class B shares.')
         + src([('Stakes disclosed', ALS)])),
        ('value', 'Valuation', 'The model gives <em>$249 a share.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, 2026', '$490B', 'Estimate: first half plus a second half growing as in Q2'],
             ['Growth, 2027 and 2028', '15%, then 13%', 'Cloud fast, Search low teens; fades to 3% by year 10'],
             ['Operating margin', '34% rising to 35%', 'Q2 was 34%; depreciation rises with capex'],
             ['Net investment, 2027&ndash;2030', '$150B, $120B, $90B, $60B', 'Capex less depreciation; then $1 per $2 of new revenue'],
             ['Discount rate', '10.1%', 'Beta 1.13, little net debt'],
             ['Terminal growth', '3.0%', 'With a 25% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$1,075B'), ('PV of terminal value', '$1,658B'), ('Enterprise value', '$2,733B'), ('Net cash and stakes', '$318B'), ('Equity value', '$3,051B'), ('Shares', '12.25B')], '$249')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '9% / 7%', '15% / 13%', '19% / 17%'], ['Long-run operating margin', '30%', '35%', '38%'],
             ['Net investment, first year', '$180B', '$150B', '$130B'], ['Discount rate', '11.1%', '10.1%', '9.1%'],
             ['Value per share', '$139', '$249', '$380'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$254</b>. The bear case is AI chatbots taking search share while the capex keeps rising; the bull case is Cloud and Gemini turning the spending into a second Search-sized business.')
         + sens('Discount rate', ['8.5%', '9.0%', '9.5%', '10.0%', '10.5%'], ['$324', '$296', '$273', '$254', '$237'])),
        ('implied', 'What the price assumes', 'At $324, <em>about 20% growth for two years.</em>',
         implied([['Revenue growth of about 20% a year in 2027 and 2028, then the same fade', '15% and 13%'], ['Or a long-run operating margin of about 46%', '35%'], ['Or a discount rate near 8.5%', '10.1%']])
         + prose('Analysts average about $435. They value Alphabet at about 29 times consensus core earnings and give more credit for Cloud&rsquo;s $514 billion backlog than this model does.')),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Search and AI chatbots', 'If ChatGPT and others take commercial queries, Search growth slows where the profit is.'],
             ['Capital spending', 'About $200 billion this year and more in 2027; free cash flow is already negative.'],
             ['Dilution', 'The share sale and at-the-market program reverse years of buybacks.'],
             ['Antitrust', 'Remedies in the U.S. search and ad-tech cases could change how Google pays for distribution and sells ads.'],
         ]) + prose('<b>Upside:</b> Cloud backlog converting faster, TPUs sold to other AI labs, Waymo scaling, and the SpaceX and Anthropic stakes rising further.')),
        ('rec', 'Rating', 'Hold.',
         prose('placeholder')
         + band('Search pays for the AI build, <em>for now.</em>', 'Cloud is working; the question is how long Search can fund the rest.')),
    ])

TQ = 'https://www.fool.com/earnings/call-transcripts/2026/10/15/tsmc-tsm-q3-2026-earnings-call-transcript/'
R['TSM'] = dict(
    t='TSM', slug='tsmc', name='TSMC', h1='TSMC', sector='Semiconductors', date=D22, timing=', after its third-quarter results',
    sub='Taiwan Semiconductor Manufacturing Company makes almost every advanced chip in the world, including Nvidia&rsquo;s, AMD&rsquo;s and Apple&rsquo;s. Revenue is growing about 44% this year at a 66% gross margin. Its shares trade in New York as ADRs (one ADR is five Taiwan shares); figures are in U.S. dollars.',
    call='Hold', method='Cash-flow model', price=412.35, pricenote='ADR close, Oct 22, 2026', base=411, bear=208, bull=620, wt=412, max=800, tick=100,
    disclosure='The author holds no TSM shares directly; TSMC is held inside the VanEck Semiconductor ETF (SMH) in the author&rsquo;s portfolio.',
    fieldnote='Per ADR: the cash-flow model&rsquo;s bear-to-bull range, the probability-weighted value, the price, its 52-week range and the analysts&rsquo; average target.',
    field=[('Cash-flow model', 208, 620, 411, '$208 to $620, base $411'), ('Probability-weighted', None, None, 412, '$412'),
           ('Price at writing', None, None, 412.35, '$412.35'), ('52-week range', 267, 487, None, '$267 to $487'), ('Analyst average', None, None, 529, '$529')],
    toc=TOCP, chapters=[
        ('overview', 'The business', 'The world&rsquo;s <em>chip factory.</em>',
         prose('TSMC does not design chips; it manufactures them for the companies that do. It makes nearly all of the most advanced ones: Nvidia&rsquo;s AI accelerators, Apple&rsquo;s processors, AMD&rsquo;s CPUs and GPUs, and the custom AI chips Google, Amazon and others design. It also packages them together with memory (CoWoS), which has been the tightest bottleneck in AI hardware.',
               'Its edge is manufacturing at the leading edge, now the 2-nanometer (N2) process, at a scale and yield no rival matches. Most production is in Taiwan, with new fabs in Arizona, Japan and Germany.')),
        ('results', 'Latest results', 'Revenue up 41%, <em>a 66% gross margin.</em>',
         stats([('$46.7B', 'Revenue, Q3 2026, +41%'), ('66.4%', 'Gross margin'), ('58.7%', 'Operating margin'), ('+44%', '2026 revenue growth, in dollars'), ('$52.3&ndash;54.3B', 'Q4 revenue guidance'), ('$60&ndash;64B', '2026 capex')])
         + prose('Third-quarter revenue rose 41% in dollars to $46.7 billion and profit about 69%. The gross margin of 66.4% slipped 1.3 points from the second quarter as the 2-nanometer ramp diluted it. N2 was 8% of wafer revenue, and its capacity should more than double in 2027.',
                 'TSMC guided fourth-quarter revenue to $52.3&ndash;54.3 billion and expects about 44% growth for 2026. Management said its forecast of mid-to-high-50s% annual growth in AI accelerator revenue through 2029 will &ldquo;probably&rdquo; be higher, but warned that overseas fabs will dilute the gross margin by 3&ndash;4 points in later years. Capital spending of $60&ndash;64 billion this year will rise &ldquo;even more significantly&rdquo; in 2026&ndash;2028.')
         + src([('Q3 2026 earnings call', TQ)])),
        ('fin', 'The numbers', 'Revenue nearly doubled <em>in two years.</em>',
         table(['', '2023', '2024', '2025', '2026 estimate'], [
             ['Revenue', '$69.3B', '$90.1B', '$122.4B', 'about $176B'],
             ['Revenue, NT$', 'NT$2,162B', 'NT$2,894B', 'NT$3,809B', '&mdash;'],
             ['Gross margin', '54.4%', '56.1%', '59.9%', 'about 66%'],
             ['Operating margin', '42.6%', '45.7%', '50.8%', 'about 58%'],
             ['Capital spending', '$30.4B', '$29.8B', '$40.9B', '$60&ndash;64B'],
         ], 'allnum')
         + prose('TSMC reports in New Taiwan dollars and files a 20-F with the SEC as a foreign company, so the site&rsquo;s automatic tables do not cover it; these figures come from its results releases. The 2026 column uses the first three quarters and fourth-quarter guidance.')
         + src([('2025 results', 'https://telecomlead.com/semiconductor/tsmc-delivers-record-2025-revenue-and-profit-as-ai-chip-demand-fuels-growth-us-expansion-accelerates-124150'), ('TSMC investor relations', 'https://investor.tsmc.com/fundamentals')])),
        ('capital', 'Balance sheet and ownership', 'Cash-rich, <em>spending more each year.</em>',
         prose('TSMC holds far more cash than debt; this model uses net cash of about $60 billion (an estimate from its latest balance sheet). It pays a quarterly dividend it intends to keep raising. There are about 25.9 billion Taiwan shares, or 5.19 billion ADR-equivalents.')),
        ('value', 'Valuation', 'The model gives <em>$411 an ADR.</em>',
         table(['Assumption', 'Base case', 'Basis'], [
             ['Revenue, 2026', '$176B', 'About 44% growth, company guidance'],
             ['Growth, 2027 and 2028', '25%, then 20%', 'AI demand and N2; fades to 3% by year 10'],
             ['Operating margin', '57% easing to 54%', 'Overseas fabs dilute by 3&ndash;4 points over time'],
             ['Reinvestment', '$1 for every $1.30 of new revenue', 'Capex far above depreciation'],
             ['Discount rate', '10.7%', 'Beta 1.24, net cash'],
             ['Terminal growth', '3.0%', 'With a 25% return on new capital'],
         ], 'mid')
         + bridge([('PV of 10 years of cash flow', '$901B'), ('PV of terminal value', '$1,171B'), ('Enterprise value', '$2,072B'), ('Net cash', '$60B'), ('Equity value', '$2,132B'), ('ADR-equivalents', '5.19B')], '$411')
         + '<h3 class="sec sm">Bear, base and bull</h3>' + scen([
             ['Growth, 2027 / 2028', '12% / 8%', '25% / 20%', '32% / 25%'], ['Long-run operating margin', '48%', '54%', '57%'],
             ['Discount rate', '11.7%', '10.7%', '9.7%'], ['Value per ADR', '$208', '$411', '$620'], ['Probability', '25%', '50%', '25%']])
         + prose('Weighted 25/50/25: <b>$412</b>. The bear case is the usual chip downturn after a capacity boom plus heavier overseas dilution; the bull case is AI demand running ahead of TSMC&rsquo;s own forecast.')
         + sens('Discount rate', ['9.5%', '10.0%', '10.5%', '11.0%', '11.5%'], ['$495', '$457', '$425', '$396', '$371'])),
        ('implied', 'What the price assumes', 'At $412, <em>about the base case.</em>',
         implied([['Revenue growth of about 21% a year for two years, then the same fade', '25% and 20%'], ['Or a long-run operating margin of about 54%', '54%']])
         + prose('The price matches the base case almost exactly: investors are paying for the growth TSMC itself is forecasting, no more. Analysts average about $529. The shares fell 4.5% on October 22 in the chip-equipment selloff that followed Lam Research&rsquo;s supply warning.')
         + src([('Analyst targets', 'https://www.marketbeat.com/instant-alerts/filing-guardian-partners-inc-sells-2395-shares-of-taiwan-semiconductor-manufacturing-company-ltd-tsm-2026-10-22/')])),
        ('risks', 'Risks', 'What could go wrong, <em>and what could go right.</em>',
         table(['Risk', 'Why it matters'], [
             ['Taiwan', 'Most capacity is in Taiwan; any conflict or blockade would be the largest single risk to the chip industry.'],
             ['The chip cycle', 'Capacity booms have always been followed by downturns; capex is rising sharply.'],
             ['Overseas costs', 'Arizona, Japan and Germany fabs cost more to run and dilute margins.'],
             ['Customer concentration', 'Apple and Nvidia are a large share of revenue.'],
             ['Tariffs and export rules', 'U.S. chip tariffs and China export limits could change where and for whom it builds.'],
         ]) + prose('<b>Upside:</b> AI accelerator growth above management&rsquo;s forecast, N2 pricing, advanced packaging capacity, and a stronger Taiwan dollar lifting dollar results.')),
        ('rec', 'Rating', 'Hold.',
         prose('placeholder')
         + band('The factory every AI chip needs, <em>priced for its own forecast.</em>', 'The price pays for the plan; the risk is geography and the cycle.')),
    ])
