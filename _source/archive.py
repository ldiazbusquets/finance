"""Frozen published versions of every report.

A report's live page changes when it is revised. So that any earlier call can be checked against what was actually
published, each version is kept as a frozen copy: archive/<slug>/<date>.html. A new copy is made whenever a
report's published numbers change (date, rating, base case, weighted value or price at writing). Frozen copies are
the page as it stood, with the live parts removed (scripts, today's price, Ask AI) and a banner pointing to the
current version. They are never edited afterwards. archive/index.json lists every version.

Called by build.py after the checks pass, so only checked pages are frozen.
"""
import datetime as dt
import json
import os
import re

KEYS = ('date', 'call', 'base', 'wt', 'price')


def index_path(out):
    return os.path.join(out, 'archive', 'index.json')


def load(out):
    try:
        return json.load(open(index_path(out)))
    except Exception:
        return {'note': __doc__.strip().split('\n')[0], 'reports': {}}


def key(R):
    return {k: R.get(k) for k in KEYS}


def same(a, b):
    return all(a.get(k) == b.get(k) for k in KEYS)


def earlier(idx, R):
    """versions of this report other than the one being built, newest first"""
    return [v for v in reversed(idx['reports'].get(R['slug'], [])) if not same(v, key(R))]


def freeze(html, R, when, current):
    """the page as published, without the live parts, readable two folders down"""
    head_end = html.index('</head>')
    theme = re.search(r'<script>\s*/\* light 7am.*?</script>', html, re.S)
    body = html[head_end:]
    body = re.sub(r'<script\b.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<div class="panel now" id="now">.*?<div class="revnote" id="revnote" hidden></div>\s*</div>', '', body, flags=re.S)
    head = re.sub(r'<script\b.*?</script>', '', html[:head_end], flags=re.S)
    head = re.sub(r'<link rel="canonical"[^>]*>', '', head)
    head = re.sub(r'<base [^>]*>\n?', '', head)          # reports live in reports/ and use <base>; the frozen copy has its own paths
    head = head.replace('<head>', '<head>\n<meta name="robots" content="noindex">', 1)
    if theme:
        head += theme.group(0)
    head += '<style>#tg, #mb { display: none !important; }</style>'
    html = head + body
    html = html.replace(f'href="reports/{R["slug"]}.html#', 'href="#')     # its own anchors stay on the frozen page
    html = re.sub(r'(href|src)="(?!https?:|/|#|data:|mailto:|tel:)([^"]*)"', lambda m: f'{m.group(1)}="../../{m.group(2)}"', html)
    banner = (f'<div class="archived" role="note" style="background:var(--s2);border-bottom:1px solid var(--line2);padding:12px 0;font-size:14px">'
              f'<div class="wrap"><b>Archived version</b> as published on {when}: rated {R["call"]}' + (f' at ${R["price"]:,.2f}' if isinstance(R.get('price'), (int, float)) else '') + '. '
              f'It is kept unchanged so the call can be checked. <a href="../../reports/{R["slug"]}.html" style="color:var(--acc);text-decoration:underline">Current version &rarr;</a></div></div>')
    html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + '\n' + banner, html, count=1)
    return html


def run(out, reports, today=None):
    today = today or dt.date.today().isoformat()
    idx = load(out)
    made = []
    for R in reports:
        slug = R.get('slug')
        page = os.path.join(out, 'reports', f'{slug}.html')
        if not slug or not os.path.exists(page):
            continue
        vs = idx['reports'].setdefault(slug, [])
        if vs and same(vs[-1], key(R)):
            continue
        d = os.path.join(out, 'archive', slug)
        os.makedirs(d, exist_ok=True)
        name, n = today, 2
        while os.path.exists(os.path.join(d, name + '.html')):
            name = f'{today}-{n}'; n += 1
        html = open(page, encoding='utf-8').read()
        with open(os.path.join(d, name + '.html'), 'w', encoding='utf-8') as f:
            f.write(freeze(html, R, R['date'], page))
        vs.append(dict(key(R), file=f'archive/{slug}/{name}.html', frozen=today, name=R['name']))
        made.append(f'{slug}/{name}')
    os.makedirs(os.path.dirname(index_path(out)), exist_ok=True)
    with open(index_path(out), 'w') as f:
        json.dump(idx, f, indent=1)
    return made


def versions_line(out, R):
    """a sentence for the report: its earlier published versions, linked"""
    old = earlier(load(out), R)
    if not old:
        return ''
    def money(v):
        return f'${v:,.0f}' if isinstance(v, (int, float)) else ''
    parts = [f'<a href="{v["file"]}">{v["date"]}</a> ({v["call"]}, value {money(v["base"])}' + (f'; {v["note"][0].lower()}{v["note"][1:]}' if v.get('note') else '') + ')' for v in old]
    return ' Earlier published versions, kept unchanged: ' + '; '.join(parts) + '.'
