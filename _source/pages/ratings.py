"""How every report is rated, and the neutral closing text for each.

The rating is mechanical, so it does not depend on who owns the stock:
  1. Take the report's probability-weighted value (25% bear, 50% base, 25% bull).
  2. Compare it with the price at writing.
  3. Compare that with the S&P 500 valued on the same assumptions (_source/models/market.py): on a 5.15%
     Treasury yield and a 4.5% equity premium the index is worth about 68% of its price, so a stock whose
     value is 68% of its price is exactly as expensive as the market.
  4. Buy if the stock is at least 15% cheaper than the market on that basis, Sell if at least 15% dearer,
     Hold in between. Private companies are not rated; there is no price to buy at.
Absolute values are shown unchanged next to the rating, so a reader can see both views."""

MKT = 0.678          # S&P 500 value / price on the reports' assumptions, 8% growth for five years (market.py, Oct 22, 2026)
MKT_RANGE = (0.606, 0.757)   # with 6% and 10% growth
MKT_N = 420          # companies with complete data in the calculation
BAND = 0.15
RATED = 'October 22, 2026'


def rate(wt, price):
    rel = (wt / price) / MKT - 1
    call = 'Buy' if rel >= BAND else 'Sell' if rel <= -BAND else 'Hold'
    return call, wt / price - 1, rel


# Closing text: what the business is, what decides the outcome, and what would change the rating.
# No mention of anyone's portfolio; ownership is stated once, in the disclosure line.
REC = {
    'NVDA': ('The best business in tech, <em>priced for it.</em>',
             'Nvidia earns more than almost any company in history and still has most of the AI accelerator market. The model values it below the price at its own cost of capital, but by less than the market as a whole is valued below its price on the same assumptions.',
             'Next-year guidance pointing to growth well above 40% would raise the value; signs that cloud AI spending is peaking would lower it. Fiscal third-quarter results in November, against $108 billion of guidance, are the next test.'),
    'AMZN': ('A great company <em>in an expensive building phase.</em>',
             'AWS growth is accelerating, but capital spending has turned free cash flow negative. The price assumes long-run margins higher than Amazon has ever earned.',
             'AWS growth staying above 30%, operating income against guidance, and any change to the $220 billion capex plan in the next report would move the value.'),
    'META': ('Strong ads, <em>heavy AI bills.</em>',
             'Advertising grew faster than expected and the legal charge is a one-off, but free cash flow is now negative and 2027 spending has no stated limit.',
             'The first 2027 capex guidance in the fourth-quarter report, the timing of the settlement payment and whether buybacks resume are the next inputs.'),
    'JPM': ('The best bank, <em>valued on its returns.</em>',
             'JPMorgan earns more on its equity than its peers, and the excess-return model capitalises that. The price needs returns above the bank&rsquo;s own through-cycle target.',
             'A change to the 16% through-cycle return target, credit losses rising faster than expected, or a move in rates that changes the cost of equity would change the value.'),
    'VRT': ('The right market, <em>execution to prove.</em>',
             'Demand for Vertiv&rsquo;s power and cooling equipment is not in doubt; delivering it on schedule is, after a quarter below its own growth range.',
             'Third-quarter organic growth against the guided 34&ndash;36% second-half pace is the main test.'),
    'LHX': ('A good business <em>at a discounted price.</em>',
             'The backlog is at a record and cash-flow guidance is intact; the selloff followed a CEO change and a delayed IPO. The bear case is close to today&rsquo;s price, which is the main warning.',
             'A cut to the $3.0 billion cash-flow guidance or new findings from the conduct investigation would lower the value.'),
    'AWK': ('A reliable business <em>with a rate-sensitive price.</em>',
             'American Water&rsquo;s earnings are among the most predictable in the market, but the price implies a cost of equity well below what today&rsquo;s Treasury yields justify.',
             'Lower long-term interest rates, or rate-case outcomes that lift allowed returns, would raise the value; higher yields would lower it.'),
    'BA': ('The recovery is priced in. <em>Execution decides the rest.</em>',
             'Boeing&rsquo;s backlog guarantees demand; the value depends on building planes at the planned rate and quality.',
             'Monthly 737 and 787 production rates, FAA decisions and free cash flow against guidance are the inputs to watch.'),
    'SPCX': ('A great asset, <em>an AI-sized bill.</em>',
             'SpaceX&rsquo;s value now depends more on its AI data centers than on rockets or Starlink. Its free cash flow is deeply negative while it builds, which this model counts.',
             'Revenue against the $33&ndash;37 billion first-quarter guidance, the pace of capital spending, and the December lock-up expiry are the next inputs.'),
    'FLY': ('A real business, <em>a risky stock.</em>',
             'The backlog is strong; launch reliability and cash burn decide the outcome. The range of values is wide because one launch or contract changes the answer.',
             'Alpha Flight 8 and the third-quarter results in November are the next tests.'),
    'KTOS': ('The same idea as Anduril, <em>at a fraction of the margin.</em>',
             'Kratos has many of the same products as Anduril and is growing, but it earns very little today, and the price assumes revenue far above its own plan.',
             'Rising margins in the 2027 guidance, or a larger production contract for its drones, would raise the value.'),
    'AXON': ('The right thesis, <em>most of it already in the price.</em>',
             'Axon has a near-monopoly in U.S. police cameras, sticky subscriptions and a fast-growing AI product line. The price assumes growth beyond the company&rsquo;s own targets.',
             'Third-quarter results on November 3, especially margins after stock pay, are the next test.'),
    'PLTR': ('The best numbers in software, <em>priced as if they last.</em>',
             'Few software companies have ever grown this fast at this size while earning these margins. The price matches the model&rsquo;s bull case: it needs about 50% growth a year for four years at a record margin.',
             'Several more quarters of 80%-plus U.S. commercial growth would lift the base case; any slowdown would hit a price with no room for one. Third-quarter results come on November 2.'),
    'AMD': ('A real challenger to Nvidia, <em>priced as one.</em>',
             'AMD leads in server CPUs and is now a credible second supplier of AI systems, with signed demand from OpenAI and Anthropic. The price sits between the base and bull cases.',
             'Third-quarter results on November 3 and the size of the fourth-quarter Helios step-up are the next test.'),
    'MU': ('The best memory market ever, <em>still a memory market.</em>',
             'Micron is executing well in the tightest memory market on record, and long-term agreements make this cycle steadier than past ones. The price assumes today&rsquo;s profit lasts well beyond 2028.',
             'The first signs of new supply, contract prices for 2027 and the December results would move the value most.'),
    'SNDK': ('The purest bet on flash, <em>at a peak-cycle price.</em>',
             'Sandisk turned a loss-making business into one with an 85% gross margin and no debt in about a year. The price sits close to the bull case, and its own contracts cap how far prices can rise.',
             'First-quarter results on October 29 will show how far flash prices are still rising.'),
    'LMT': ('The incumbent with the moat, <em>at a modest price.</em>',
             'Lockheed is the sole supplier of the interceptors and munitions now in most demand, under seven-year contracts. Anduril is taking the new drone and low-cost categories, which caps Lockheed&rsquo;s share of future budgets, but it does not touch the F-35, PAC-3, THAAD or Trident this decade.',
             'The budget after the November 3 midterms, F-35 Lot 20 funding and the 2027 guidance in January are the next inputs.'),
    'NOC': ('The most protected programs, <em>and the most political.</em>',
             'Northrop owns the B-21 and Sentinel, which no new entrant can build. Its newer bets sit where Anduril is strongest, and its growth depends on budgets the midterms put in question.',
             'The defense budget after the midterms, more B-21 charges, and whether Talon Blue wins in the next drone competition would move the value.'),
    'CAT': ('The AI power trade, <em>inside a cyclical company.</em>',
             'Caterpillar has become one of the largest suppliers of power for AI data centers, and its backlog makes the next two years visible. About 60% of the company is still construction and mining equipment, and the price assumes about 18% growth a year for two more years.',
             'Third-quarter results on October 29, especially Power &amp; Energy orders and the backlog, are the next test.'),
    'ASML': ('A monopoly, <em>priced like one.</em>',
             'Every leading-edge chip runs through ASML&rsquo;s machines, and demand is ahead of its capacity for at least two years. The price needs growth close to the model&rsquo;s bull case.',
             'EUV price increases from 2027, High-NA orders and the June 2027 investor day are the next inputs; a chip-equipment downturn is the main risk.'),
    'SKHY': ('The HBM leader, <em>at the top of the cycle.</em>',
             'SK hynix was first to HBM at scale and has the largest share of Nvidia&rsquo;s supply at a 76% margin. It is still a memory company at the top of its cycle, Samsung is gaining in HBM, and the won adds currency risk.',
             'Third-quarter results on October 29 in Seoul, HBM4 pricing for 2027 and any buyback announcement are the next inputs.'),
    'MSFT': ('The best software franchise, <em>in its most expensive build.</em>',
             'Azure is growing above 40% and Copilot has more than 30 million paid seats, but capital spending of about $257 billion this fiscal year means free cash flow is growing far more slowly than profit. The OpenAI stake adds about $29 a share at this site&rsquo;s own OpenAI value.',
             'Azure growth against the 45% guided for the first quarter, the payback on the capex, and OpenAI&rsquo;s share of the backlog are the next inputs.'),
    'GOOGL': ('Search pays for the AI build, <em>for now.</em>',
              'Cloud is the fastest-growing large cloud and Search is still growing in the high teens, but free cash flow has turned negative and Alphabet is selling shares to fund about $200 billion of capex this year.',
              'Third-quarter results on October 28, especially Search growth, Cloud backlog conversion and 2027 capex, would move the value most.'),
    'TSM': ('The factory every AI chip needs, <em>priced for its own forecast.</em>',
            'TSMC makes almost every advanced chip and is growing about 44% this year at a 66% gross margin. The price matches the model&rsquo;s base case, which follows management&rsquo;s own outlook. The concentration of production in Taiwan is a risk no model captures well.',
            'Fourth-quarter results in January with 2027 guidance, N2 pricing and the size of the 2027 capex increase are the next inputs.'),
    'GEV': ('A great business, <em>priced for a greater one.</em>',
             'GE Vernova has a sold-out gas turbine franchise, a growing grid business, net cash and rising margins. On the company&rsquo;s own 2028 targets the shares trade at about twice the model&rsquo;s value.',
             'A 2028 margin target above 20% or gas pricing still climbing through 2027 would raise the value; slot reservations failing to become firm orders would lower it. Third-quarter results come on October 28.'),
    # private companies: not rated
    'ANTHROPIC': ('The fastest-growing software company, <em>at an unknown IPO price.</em>',
                  'The base case supports roughly the May private valuation, about $1 trillion. A listing at $1.5&ndash;2 trillion would price in close to the bull case on its first day.',
                  'The prospectus&rsquo;s margins, compute commitments and the IPO price are the numbers that decide whether the shares are worth buying.'),
    'OPENAI': ('The biggest audience in AI, <em>the biggest bill.</em>',
               'There is no way to buy OpenAI directly before its expected 2027 IPO. The base case supports roughly the March valuation; the $1.4 trillion round prices in more than that, before the dilution its cash burn will require.',
               'Revenue growth against the $50 billion annual pace, progress on advertising, and the size of future funding rounds are the inputs to watch.'),
    'ANDURIL': ('A great company, <em>priced for perfection.</em>',
                'Anduril is growing like a top software company, but the scenarios value it far below the $61&ndash;90 billion private marks. An IPO that starts from those marks would price in close to the bull case.',
                'Fury production, the Army enterprise agreement and an S-1 with audited margins would show whether the private marks are justified.'),
    'BLOOMBERG': ('The Coca-Cola of financial data, <em>if it ever lists.</em>',
                  'Bloomberg is dominant, recurring and slow-changing. Near the $80 billion bankers mention, the base case needs a multiple close to the best data companies: fair but not cheap; much above $100 billion it would assume the bull case.',
                  'A prospectus with audited margins and Terminal renewal rates would replace the estimates this report relies on.'),
}

# Why the value differs from the analysts' average target, where one is shown.
STREET = {
    'PLTR': 'The analysts&rsquo; average of about $206 is close to the price. The gap with this model is mostly the exit multiple (30&times; base against the 45&times; or more the price implies) and a 14% discount rate from Palantir&rsquo;s beta of about 2.',
    'AMD': 'Analysts average about $636 and value AMD on about 34 times their 2027 earnings. This model values it on 2030 earnings, after the AI build-out has slowed, with a 25&times; exit multiple in the base case.',
    'MU': 'Analysts average about $1,555 and use about 7 times next year&rsquo;s earnings. This model instead values the whole cycle, with prices falling back to a mid-cycle margin of 35% from 2029, which is the main source of the gap.',
    'SNDK': 'Analysts&rsquo; median of about $2,225 rests on next year&rsquo;s peak earnings. This model assumes flash prices fall back after 2028, to a mid-cycle margin of 25%.',
    'AXON': 'Analysts average about $691, assuming faster growth than the company&rsquo;s own path and a higher multiple. This model follows management&rsquo;s path to about $8.5 billion of 2030 revenue.',
    'KTOS': 'Analysts average about $98, assuming faster growth and margins well above the 9% base case here. Kratos has never earned more than a low single-digit operating margin.',
    'SPCX': 'Analysts average about $223, assuming AI revenue keeps compounding near management&rsquo;s guidance. The base case here reaches $500 billion of 2030 revenue, below the $660 billion the price implies.',
    'FLY': 'Analysts average about $38, closer to this model&rsquo;s bull case; the base case here assumes about $1.2 billion of 2030 revenue at 5&times; sales.',
    'CAT': 'Analysts average about $922 and value Caterpillar on near-term earnings at a premium multiple. This model fades growth to 3% by year ten and holds the margin near 21%, its best level so far.',
    'ASML': 'Analysts average about $2,079, assuming EUV price increases and capacity additions lift growth and margins well into the 2030s. The base case here has growth of 22% then 15% and a 44% margin, discounted at 11%.',
    'SKHY': 'Analysts&rsquo; consensus of about $253 rests on today&rsquo;s earnings at about 8 times. This model assumes memory prices fall back after 2028, as in every past cycle.',
    'MSFT': 'Analysts average about $559, a little above the price. The model&rsquo;s lower value comes mostly from the net investment of $180 billion in fiscal 2027 and a 10% discount rate; at 8.5% it reaches $486.',
    'GOOGL': 'Analysts average about $435, about 29 times consensus core earnings. This model holds the operating margin near 35% and deducts heavy net investment through 2030.',
    'TSM': 'Analysts average about $529, assuming growth stays above 25% for longer. The base case here follows TSMC&rsquo;s own forecast and fades growth from 2029.',
    'GEV': 'Analysts average about $1,172 and value GE Vernova on earnings well beyond 2028 at premium multiples. This model uses the company&rsquo;s own 2028 targets and then fades growth.',
}
