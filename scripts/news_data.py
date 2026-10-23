"""Market headlines for the Ask AI bubble.

Reads a few public RSS feeds once a weekday and keeps the last few days of headlines
(title, source, time, link) in data/news.json. Only headlines are stored, never article text.
The in-browser model may use them to say what was in the news; it is told it knows nothing beyond them.
"""
import html, json, os, re, sys, time, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'news.json')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
      'Accept': 'application/rss+xml, application/xml, text/xml, */*'}
FEEDS = [
    ('CNBC', 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114'),     # top news
    ('CNBC', 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069'),      # markets
    ('CNBC', 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258'),      # economy
    ('MarketWatch', 'https://feeds.content.dowjones.io/public/rss/mw_topstories'),
    ('MarketWatch', 'https://feeds.content.dowjones.io/public/rss/mw_marketpulse'),
    ('Yahoo Finance', 'https://finance.yahoo.com/news/rssindex'),
    ('Federal Reserve', 'https://www.federalreserve.gov/feeds/press_all.xml'),
]
KEEP_DAYS = 4
MAX_ITEMS = 160


def fetch(url):
    for i in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
                return r.read()
        except Exception as e:
            if i:
                raise
            time.sleep(3)


def clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))
    return re.sub(r'\s+', ' ', s).strip()


def when(s):
    try:
        d = parsedate_to_datetime(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        try:
            return datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(timezone.utc)
        except Exception:
            return None


def parse(raw, source):
    out = []
    root = ET.fromstring(raw)
    items = root.findall('.//item')
    ns = '{http://www.w3.org/2005/Atom}'
    if not items:
        items = root.findall('.//' + ns + 'entry')
    for it in items:
        def g(tag):
            el = it.find(tag)
            if el is None:
                el = it.find(ns + tag)
            return el
        t = g('title')
        title = clean(t.text if t is not None else '')
        if len(title) < 12:
            continue
        lk = g('link')
        link = (lk.text or lk.get('href') or '').strip() if lk is not None else ''
        d = g('pubDate')
        if d is None:
            d = g('updated')
        if d is None:
            d = g('published')
        dt = when(d.text if d is not None and d.text else '')
        out.append({'t': title[:220], 's': source, 'd': dt.strftime('%Y-%m-%dT%H:%MZ') if dt else '', 'u': link[:400]})
    return out


def run():
    old = []
    try:
        old = json.load(open(OUT)).get('items', [])
    except Exception:
        pass
    new, ok = [], 0
    for source, url in FEEDS:
        try:
            got = parse(fetch(url), source)
            new += got; ok += 1
            print(f'  {source}: {len(got)} headlines')
        except Exception as e:
            print(f'  FAIL {source} {url[:60]}: {e}', file=sys.stderr)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)).strftime('%Y-%m-%dT%H:%MZ')
    seen, items = set(), []
    for x in sorted(new + old, key=lambda x: x.get('d', ''), reverse=True):
        k = re.sub(r'[^a-z0-9]', '', x['t'].lower())[:80]
        if k in seen or (x.get('d') and x['d'] < cutoff):
            continue
        seen.add(k); items.append(x)
    items = items[:MAX_ITEMS]
    if not ok and old:
        print('  no feeds reachable; keeping the previous headlines')
        return len(old)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'note': 'Headlines only, from public RSS feeds.', 'items': items},
                  f, separators=(',', ':'), ensure_ascii=False)
    return len(items)


if __name__ == '__main__':
    print(run(), 'headlines')
