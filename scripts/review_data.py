"""Which reports need reviewing? Written to data/review.json on every data update.

For each published rating (the latest row per company in data/calls.json) this checks, against today's data:
  - rating:  the published rule applied at today's close (the report's expected value from
             data/models/montecarlo.json against the S&P 500 benchmark in data/models/market.json)
             gives a different call, or one within 3 points of a threshold;
  - price:   the price has moved 15% or more since the report;
  - results: the company has filed a 10-Q or 10-K, or reported results, since the report was written;
  - due:     results are due within the next 7 days.
The values themselves never change here: only a revised report changes a value or a rating. This only says
which reports are out of date, so they can be revised first.
"""
import datetime as dt
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
BAND, NEAR, MOVE, DUE_DAYS = .15, .03, .15, 7


def load(p, default=None):
    try:
        return json.load(open(os.path.join(DATA, p)))
    except Exception:
        return default


def run(today=None):
    today = today or dt.datetime.now(dt.timezone(dt.timedelta(hours=-4))).date().isoformat()
    calls = (load('calls.json', {}) or {}).get('calls', [])
    mc = (load('models/montecarlo.json', {}) or {}).get('reports', {})
    mkt = ((load('models/market.json', {}) or {}).get('scenarios', {}).get('0.08', {}) or {}).get('value_to_price')
    px = (load('co/prices.json', {}) or {}).get('px', {})
    earn = (load('earnings.json', {}) or {}).get('rows', [])
    last = {}
    for c in calls:
        last[c['t']] = c
    rows = []
    for t, c in sorted(last.items()):
        q, m = px.get(t) or {}, mc.get(t) or {}
        now, then, since = q.get('p'), c.get('price'), c['date']
        flags = []
        row = {'t': t, 'name': c['name'], 'page': c['page'], 'call': c['call'], 'rated': since, 'price': then, 'now': now, 'asof': q.get('d')}
        if now and then:
            mv = now / then - 1
            row['move'] = round(mv, 4)
            if abs(mv) >= MOVE:
                flags.append(['price', f'Price {"up" if mv > 0 else "down"} {abs(mv) * 100:.0f}% since the report'])
        if now and m.get('mean') and mkt:
            rel = (m['mean'] / now) / mkt - 1
            call_now = 'Buy' if rel >= BAND else 'Sell' if rel <= -BAND else 'Hold'
            row['call_now'], row['rel_now'] = call_now, round(rel, 4)
            if call_now != c['call']:
                flags.append(['rating', f'At today&rsquo;s price the rule gives {call_now}, not {c["call"]}'])
            elif min(abs(rel - BAND), abs(rel + BAND)) < NEAR:
                flags.append(['near', f'Within {NEAR * 100:.0f} points of the {"Buy" if rel > 0 else "Sell"} line at today&rsquo;s price'])
        co = load(f'co/{t}.json', {}) or {}
        new = [f for f in co.get('filings', []) if f.get('form') in ('10-Q', '10-K', '20-F') and f.get('date', '') > since]
        if new:
            f = max(new, key=lambda x: x['date'])
            flags.append(['results', f'New {f["form"]} filed {f["date"]}, after the report'])
            row['filing'] = {'form': f['form'], 'date': f['date'], 'url': f.get('url')}
        for e in earn:
            if e.get('t') != t or not e.get('date'):
                continue
            if since < e['date'] <= today and not new:
                flags.append(['results', f'Results reported {e["date"]}, after the report'])
            days = (dt.date.fromisoformat(e['date']) - dt.date.fromisoformat(today)).days
            if 0 < days <= DUE_DAYS:
                flags.append(['due', f'Results due {e["date"]}'])
                row['due'] = e['date']
        row['flags'] = flags
        rows.append(row)
    order = {'rating': 0, 'results': 1, 'price': 2, 'near': 3, 'due': 4}
    rows.sort(key=lambda r: (min([order[f[0]] for f in r['flags']] or [9]), r['t']))
    out = {'updated': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'today': today,
           'rules': {'band': BAND, 'near': NEAR, 'move': MOVE, 'due_days': DUE_DAYS, 'benchmark': mkt}, 'rows': rows}
    with open(os.path.join(DATA, 'review.json'), 'w') as f:
        json.dump(out, f, indent=1)
    return sum(1 for r in rows if any(x[0] in ('rating', 'results', 'price') for x in r['flags']))


if __name__ == '__main__':
    print(run(), 'reports need review')
