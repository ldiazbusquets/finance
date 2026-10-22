"""Title Case for page titles and headings (shared by Finance and Lab)."""
import re

SMALL = {'a', 'an', 'and', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'by', 'with', 'or',
         'as', 'but', 'vs', 'vs.', 'nor', 'per', 'via', 'from', 'into'}


def _word(w, first, last):
    if '-' in w:
        ps = w.split('-')
        return '-'.join(_word(p, first if i == 0 else False, i == len(ps) - 1) for i, p in enumerate(ps))
    if not w or not w[0].isalpha():
        return w                    # numbers, entities, placeholders
    if any(c.isupper() for c in w) or any(c.isdigit() for c in w):
        return w                    # acronyms, tickers, already-capitalised names
    if w.lower() in SMALL and not first and not last:
        return w
    return w[0].upper() + w[1:]


def tc_text(s):
    # split on spaces; a word after ':' , '|' or an opening dash counts as first
    toks = s.split(' ')
    idx = [i for i, t in enumerate(toks) if t.strip()]
    out, start = [], True
    for i, t in enumerate(toks):
        lead = re.match(r'^[(\[“"‘\ue000]*', t).group(0)
        core = t[len(lead):]
        m = re.match(r'^(.*?)([.,:;!?)\]”"’\ue000]*)$', core)
        body, trail = m.group(1), m.group(2)
        last = bool(idx) and i == idx[-1]
        out.append(lead + _word(body, start, last) + trail)
        if t.strip():
            start = t in ('|', '—', '–', '·') or trail.replace('\ue000', '').endswith(':')
    return ' '.join(out)


def tc_html(fragment):
    """Title-case the text of a fragment as one phrase, leaving tags alone."""
    tags = re.findall(r'<[^>]+>', fragment)
    txt = tc_text(re.sub(r'<[^>]+>', '\ue000', fragment))
    it = iter(tags)
    return re.sub('\ue000', lambda m: next(it), txt)


def apply(html):
    html = re.sub(r'(<title>)(.*?)(</title>)', lambda m: m.group(1) + tc_text(m.group(2)) + m.group(3), html, flags=re.S)
    html = re.sub(r'(<meta (?:property|name)="(?:og|twitter):title" content=")([^"]*)', lambda m: m.group(1) + tc_text(m.group(2)), html)
    html = re.sub(r'(<h1[^>]*>)(.*?)(</h1>)', lambda m: m.group(1) + tc_html(m.group(2)) + m.group(3), html, flags=re.S)
    html = re.sub(r'(<h3[^>]*>)(.*?)(</h3>)', lambda m: m.group(1) + tc_html(m.group(2)) + m.group(3), html, flags=re.S)
    return html


if __name__ == '__main__':
    for s in ['Financial plan', 'Bond portfolio, stress-tested', 'Puerto Rico&rsquo;s economy',
              'Unemployment: Puerto Rico and the U.S.', 'Credit spreads | Research note | LDB Finance',
              'Where each method lands, per share', 'Amazon (AMZN) research', 'What if', 'How an LLM works',
              'Today&rsquo;s Treasuries, priced at par', 'Growth-company DCF', 'Year-by-year schedule', 'Growth of $10,000', '10-year minus 2-year', 'Duration and <em>convexity</em>', 'Ask <em>the filings</em>', 'L3<em>Harris</em>', 'Research with <em>the numbers</em> showing.']:
        print(tc_html(s))
