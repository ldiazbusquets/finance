"""Bring the three finance tools that began in LDB Lab (Options Builder, Market Maker, Kelly Challenge) into LDB Finance.

The originals in labtools/ are self-contained pages. This keeps their markup and scripts unchanged and
scopes their CSS under a .labtool wrapper, so it cannot leak into the rest of the site. The Lab's colour tokens are
mapped onto Finance's copper theme. Charts and game boards stay on dark glass in both themes, as they did in the
Lab, because their scripts draw in light colours.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'labtools')

DROP = re.compile(r'^(nav\b|nav |\.mark\b|\.btn\b|\.tbtn\b|footer\b|html\.theming|html\.lt nav|html\.lt\.scrolled|html\.lt \.mark|html\.lt \.btn|html\.lt footer|html\.lt \.tbtn)')

# Finance tokens for the Lab's variable names; panels/boxes keep a dark copper glass
TOKENS = """
.labtool { --ln2: var(--line2); --soft: var(--t2); --dim: var(--t3); --pill: color-mix(in srgb, var(--ink) 7%, transparent); --pill-on: color-mix(in srgb, var(--ink) 16%, transparent);
  --gs1: var(--s1); --gs2: var(--s2); --gln2: var(--line2); --mint: var(--acc); --orange: var(--ink); --bone: var(--ink); --crim: var(--acc);
  --teal: #6BD38A; --good: #6BD38A; --lock: #F06262; --gold: #F2C14C; --warm: #F2C14C; --mag: #C59BF5; --g: 0px; color: var(--ink); }
.labtool .panel, .labtool .box, .labtool .toast, .labtool .tape, .labtool .over, .labtool .pc {
  --bg: #0C0A08; --s1: #13100D; --s2: #1A1612; --gs1: #13100D; --gs2: #1A1612; --line: rgba(255,248,239,.08); --line2: rgba(255,248,239,.14); --ln2: rgba(255,248,239,.14); --gln2: rgba(255,248,239,.14);
  --pill: rgba(255,248,239,.07); --pill-on: rgba(255,248,239,.16); --ink: #FFF8EF; --soft: #B9AB9C; --dim: #A08670; --acc: #D9A273; --mint: #D9A273; --crim: #D9A273; --orange: #FFF8EF; --bone: #FFF8EF; color: var(--ink); }
"""
AFTER = """
html.lt .labtool .panel, html.lt .labtool .box, html.lt .labtool .toast, html.lt .labtool .tape, html.lt .labtool .over, html.lt .labtool .pc,
.labtool .panel, .labtool .box, .labtool .toast, .labtool .tape, .labtool .over, .labtool .pc { --soft: #B9AB9C; --dim: #A08670; --ink: #FFF8EF; }
.labtool .page { padding: 34px 0 40px; max-width: none; }
.labtool .act kbd, .labtool kbd { color: #34383B; opacity: 1; }
.labtool .edu { margin-top: 28px; }
"""


def split_rules(css):
    """yield (selector, body) for top-level rules; nested @media blocks are returned with body = inner css"""
    i, n = 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0:
            break
        sel = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == '{':
                depth += 1
            elif css[k] == '}':
                depth -= 1
            k += 1
        yield sel, css[j + 1:k - 1]
        i = k


def scope_sel(s):
    s = s.strip()
    if not s:
        return None
    if DROP.match(s) or s in ('html', 'body', ':root', '*', 'a', 'html.lt body', ':focus-visible') or s.startswith('button, input'):
        return None
    if s.startswith('html.lt body'):
        return None
    if s.startswith('html.lt '):
        return 'html.lt .labtool ' + s[len('html.lt '):]
    if s.startswith('body.'):
        m = re.match(r'body(\.[\w-]+)(.*)', s)
        return f'body{m.group(1)} .labtool{m.group(2)}'
    if s.startswith('body '):
        return '.labtool ' + s[5:]
    return '.labtool ' + s


def scope(css):
    out = []
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    for sel, body in split_rules(css):
        if sel.startswith('@keyframes') or sel.startswith('@font-face'):
            out.append(f'{sel} {{{body}}}')
        elif sel.startswith('@media') or sel.startswith('@supports'):
            inner = scope(body)
            if inner.strip():
                out.append(f'{sel} {{\n{inner}\n}}')
        elif sel.startswith('@'):
            continue
        else:
            sels = [scope_sel(x) for x in sel.split(',')]
            sels = [x for x in sels if x]
            if sels:
                out.append(', '.join(sels) + ' {' + body + '}')
    return '\n'.join(out)


def port(name):
    h = open(os.path.join(SRC, name + '.html'), encoding='utf-8').read()
    title = re.search(r'<title>(.*?)\s*\|', h).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)
    styles = re.findall(r'<style(?: id="([^"]*)")?>(.*?)</style>', h, re.S)
    css = '\n'.join(scope(body) for sid, body in styles if sid in ('', 'ldb-theme-css'))
    body = h[h.index('<div class="page">'):h.index('<footer>')]
    body = body.replace('href="./#tools"', 'href="tools.html"')
    # the tool's own script, without the footer year line (Finance has its own footer)
    scripts = re.findall(r'<script>(.*?)</script>', h[h.index('</footer>'):], re.S)
    js = '\n'.join(scripts).replace("document.getElementById('yr').textContent = new Date().getFullYear();", '')
    js = js.replace("document.body.classList.toggle('noan'", "document.body.classList.toggle('noan'")
    html = f'<style>\n{TOKENS}\n{css}\n{AFTER}\n</style>\n<section class="tight labtool" style="padding-top:0"><div class="wrap">\n{body}\n</div></section>\n'
    return title, desc, html, f'\n<script>\n{js}\n</script>'
