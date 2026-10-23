/* LDB Finance: "Ask AI" bubble. A small open model (Qwen3) runs privately in the visitor's browser via WebLLM (WebGPU).
   No server, no API key: questions and answers never leave the device. Context = the page being read + the site's ratings. */
(function () {
  'use strict';
  if (window.__ldbai) return; window.__ldbai = 1;
  var WLURL = 'https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm@0.2.85/lib/index.js';
  var MODELS = [['Qwen3-1.7B-q4f16_1-MLC', 'Qwen3 1.7B', 'about 1.1 GB', 'Better answers'], ['Qwen3-0.6B-q4f16_1-MLC', 'Qwen3 0.6B', 'about 0.5 GB', 'Faster, for phones']];
  var LS = 'ldbai.model', SS = 'ldbai.chat';
  var S = { eng: null, model: null, loading: null, busy: null, ctx: null, msgs: [] };
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } }
  function sget() { try { return JSON.parse(sessionStorage.getItem(SS) || '[]'); } catch (e) { return []; } }
  function sset() { try { sessionStorage.setItem(SS, JSON.stringify(S.msgs.slice(-16))); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function md(s) {  // tiny, safe markdown: escape first, then bold, inline code, bullets, line breaks
    var h = esc(s).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/`([^`]+)`/g, '<code>$1</code>');
    return h.split(/\n{2,}/).map(function (p) {
      var ls = p.split('\n');
      if (ls.every(function (l) { return /^\s*([-*•]|\d+\.)\s+/.test(l); })) return '<ul>' + ls.map(function (l) { return '<li>' + l.replace(/^\s*([-*•]|\d+\.)\s+/, '') + '</li>'; }).join('') + '</ul>';
      return '<p>' + ls.join('<br>') + '</p>';
    }).join('');
  }
  function strip(t) { return t.replace(/<think>[\s\S]*?(<\/think>|$)/g, '').trim(); }

  /* ---------- UI ---------- */
  var ICON = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 4.6L18.5 9.4l-4.7 1.8L12 16l-1.8-4.8L5.5 9.4l4.7-1.8z"/><path d="M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/></svg>';
  var root = document.createElement('div'); root.className = 'aib'; root.setAttribute('data-noai', '');
  root.innerHTML = '<button class="aib-btn" type="button" aria-label="Ask AI" aria-expanded="false">' + ICON + '<span>Ask AI</span></button>' +
    '<section class="aib-panel" role="dialog" aria-label="Ask AI" hidden>' +
    '<div class="aib-top"><div><b>Ask AI</b><span class="aib-st">Runs privately in your browser</span></div><div class="aib-hd"><button type="button" class="aib-clr" title="Clear the conversation" aria-label="Clear the conversation"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/></svg></button><button type="button" class="aib-x" aria-label="Close"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg></button></div></div>' +
    '<div class="aib-log" aria-live="polite"></div>' +
    '<div class="aib-sug"></div>' +
    '<form class="aib-in" autocomplete="off"><textarea rows="1" placeholder="Ask about this page or any company" aria-label="Your question"></textarea><button type="submit" aria-label="Send"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button></form>' +
    '<p class="aib-ft">Qwen3, a small open model, running on your device. It can be wrong; check figures against the page. Not investment advice.</p>' +
    '</section>';
  document.body.appendChild(root);
  var btn = root.querySelector('.aib-btn'), panel = root.querySelector('.aib-panel'), log = root.querySelector('.aib-log'), sug = root.querySelector('.aib-sug'),
      form = root.querySelector('form'), ta = root.querySelector('textarea'), send = form.querySelector('button'), st = root.querySelector('.aib-st');

  function open(v) {
    panel.hidden = !v; btn.setAttribute('aria-expanded', v ? 'true' : 'false'); root.classList.toggle('on', v);
    if (v) { render(); setup(); setTimeout(function () { ta.focus(); }, 60); }
  }
  btn.onclick = function () { open(panel.hidden); };
  root.querySelector('.aib-x').onclick = function () { open(false); btn.focus(); };
  root.querySelector('.aib-clr').onclick = function () { stop(); S.msgs = []; sset(); render(); };
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) open(false); });
  ta.addEventListener('input', function () { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 120) + 'px'; });
  ta.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.onsubmit(e); } });

  function suggestions() {
    var p = document.body.getAttribute('data-page') || '', h1 = (document.querySelector('h1') || {}).textContent || '';
    var name = h1.replace(/\s+/g, ' ').trim();
    if (document.querySelector('.rate')) return ['Summarize this report', 'Why is ' + name + ' rated this way?', 'What does the price assume?', 'What are the biggest risks?'];
    if (p === 'home' || location.pathname.replace(/\/$/, '').split('/').pop() === '' || /index\.html$/.test(location.pathname)) return ['What can I do on this site?', 'How do the ratings work?', 'Which companies are rated Buy?'];
    return ['Explain this page simply', 'How do the ratings work?', 'What is a DCF?'];
  }
  function render() {
    S.msgs = S.msgs.length ? S.msgs : sget();
    if (!S.msgs.length) {
      log.innerHTML = '<div class="aib-hi"><p>Ask about the page you are on, any company the site covers, or a finance idea. Answers use this page and the site&rsquo;s ratings.</p></div>';
    } else {
      log.innerHTML = S.msgs.map(function (m) { return '<div class="aib-m ' + (m.role === 'user' ? 'u' : 'a') + '">' + (m.role === 'user' ? esc(m.content) : md(m.content)) + '</div>'; }).join('');
    }
    if (S.note && S.note.parentNode !== log && (S.loading || !S.eng)) log.appendChild(S.note);
    sug.innerHTML = S.msgs.length ? '' : suggestions().map(function (s) { return '<button type="button">' + esc(s) + '</button>'; }).join('');
    Array.prototype.forEach.call(sug.querySelectorAll('button'), function (b) { b.onclick = function () { ta.value = b.textContent; form.requestSubmit ? form.requestSubmit() : form.onsubmit(); }; });
    log.scrollTop = log.scrollHeight;
  }

  /* ---------- model ---------- */
  function setup() {
    if (S.eng || S.loading) return;
    if (!navigator.gpu) {
      st.textContent = 'Not available on this device';
      note('<p>The AI runs inside your browser and needs WebGPU, which this browser does not offer. It works in Chrome or Edge on a computer and in Safari 26 on a Mac, iPhone or iPad.</p><p>In the meantime, <a href="ask.html">Ask the filings</a> answers questions about any covered company straight from its 10-K and 10-Q, no AI needed.</p>', 'gpu');
      form.classList.add('off'); return;
    }
    var saved = store(LS);
    var m = MODELS.filter(function (x) { return x[0] === saved; })[0];
    if (m) { load(m); return; }
    st.textContent = 'Choose a model to start';
    note('<p><b>One-time download.</b> The model runs on your own device, so nothing you type is sent anywhere. After the first download it loads from your browser&rsquo;s cache.</p><div class="aib-ms">' +
      MODELS.map(function (x, i) { return '<button type="button" data-m="' + i + '"><b>' + esc(x[1]) + '</b><span>' + esc(x[3]) + ' &middot; ' + esc(x[2]) + '</span></button>'; }).join('') + '</div>', 'pick');
    Array.prototype.forEach.call(log.querySelectorAll('[data-m]'), function (b) { b.onclick = function () { load(MODELS[+b.getAttribute('data-m')]); }; });
  }
  function note(html, id) {
    var old = log.querySelector('.aib-note'); if (old) old.remove(); S.note = null;
    var d = document.createElement('div'); d.className = 'aib-note'; d.setAttribute('data-id', id); d.innerHTML = html; log.appendChild(d); log.scrollTop = log.scrollHeight;
    S.note = d; return d;
  }
  function load(m) {
    var d = note('<p>Loading ' + esc(m[1]) + '&hellip;</p><div class="aib-prog"><i></i></div><small></small>', 'load');
    var bar = d.querySelector('i'), lab = d.querySelector('small');
    st.textContent = 'Loading ' + m[1] + '…';
    S.loading = import(WLURL).then(function (W) {
      return W.CreateMLCEngine(m[0], { initProgressCallback: function (r) { var p = (r.progress || 0) * 100; bar.style.width = p.toFixed(0) + '%'; lab.textContent = p >= 100 ? 'Starting the model…' : (/cache/i.test(r.text || '') ? 'Loading from cache ' : 'Downloading ') + Math.round(p) + '%'; } });
    }).then(function (eng) {
      S.eng = eng; S.model = m; S.loading = null; store(LS, m[0]);
      st.textContent = m[1] + ' · on your device'; d.remove(); S.note = null; form.classList.remove('off');
      if (S.pending) { var q = S.pending; S.pending = null; ask(q); }
    }).catch(function (e) {
      S.loading = null; store(LS, null); st.textContent = 'Could not start';
      d.innerHTML = '<p>The model could not start on this device (' + esc(String(e && e.message || e).slice(0, 90)) + '). Try the smaller model, or close other tabs to free memory.</p>';
      setTimeout(function () { var n = log.querySelector('.aib-note'); if (n) n.remove(); setup(); }, 2600);
    });
  }

  /* ---------- context: the most relevant parts of this page, plus the site's ratings ---------- */
  function chunks() {
    if (S.chunks) return S.chunks;
    var out = [], seen = {};
    var els = document.querySelectorAll('h1, .ph .sub, h2, h3, p, li, tr, .rate, .stat, .kv > div');
    Array.prototype.forEach.call(els, function (el) {
      if (el.closest('nav, footer, .aib, script, style, .menu')) return;
      if (el.matches('p, li, tr') && el.closest('.rate')) return;
      var t = (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
      if (t.length < 3 || seen[t]) return; seen[t] = 1;
      out.push({ t: t.slice(0, 700), h: /^H[1-3]$/.test(el.tagName) });
    });
    return (S.chunks = out);
  }
  var STOP = /^(the|a|an|and|or|of|to|in|on|is|are|was|for|what|why|how|does|do|this|that|it|its|with|about|me|i|you|be|by|at|as|can|from|which|who|will|would|should)$/;
  function words(s) { return (s.toLowerCase().match(/[a-z0-9$%.]+/g) || []).filter(function (w) { return w.length > 1 && !STOP.test(w); }); }
  function pageContext(q, budget) {
    budget = budget || 3200; var cs = chunks(), qw = words(q), out = [], used = 0;
    var head = cs.slice(0, 3).map(function (c) { return c.t; }).join('\n');
    var rate = document.querySelector('.rate'); if (rate) head += '\n' + rate.innerText.replace(/\s+/g, ' ').slice(0, 900);
    used = head.length;
    var general = !qw.length || /summar|explain|overview|page|report/i.test(q);
    var scored = cs.slice(3).map(function (c, i) {
      var lw = c.t.toLowerCase(), s = 0;
      qw.forEach(function (w) { if (lw.indexOf(w) >= 0) s += w.length > 4 ? 2 : 1; });
      if (c.h) s += .5; if (general) s += 1 / (1 + i * .05);
      return { c: c, s: s, i: i };
    }).filter(function (x) { return x.s > 0; }).sort(function (a, b) { return b.s - a.s; });
    var pick = [];
    for (var k = 0; k < scored.length && used < budget; k++) { var t = scored[k].c.t; if (used + t.length > budget) continue; pick.push(scored[k]); used += t.length + 1; }
    pick.sort(function (a, b) { return a.i - b.i; });
    return head + '\n' + pick.map(function (x) { return x.c.t; }).join('\n');
  }
  function siteContext(q) {
    if (!S.ctx) return '';
    var ql = q.toLowerCase(), r = S.ctx.ratings || [];
    var hit = r.filter(function (x) { return ql.indexOf(x.t.toLowerCase()) >= 0 && new RegExp('\\b' + x.t.toLowerCase() + '\\b').test(ql) || ql.indexOf(x.name.toLowerCase().split(' ')[0]) >= 0; });
    var broad = /\b(buy|sell|hold|rating|ratings|rated|covered|coverage|cover|companies|stocks|portfolio|which)\b/.test(ql);
    var list = hit.length && !broad ? hit : (broad ? r : []);
    var lines = list.map(function (x) { return x.t + ' (' + x.name + '): ' + x.call + (x.value ? ', model value $' + x.value : '') + (x.price ? ' vs price $' + x.price : '') + ' [' + x.page + ']'; });
    return (S.ctx.method ? 'How ratings work: ' + S.ctx.method + '\n' : '') + (lines.length ? 'Site ratings (Oct 2026):\n' + lines.join('\n') : '');
  }
  /* ---------- market brief: latest closes, biggest S&P 500 moves, rates, and recent headlines ---------- */
  var MKT = /\b(market|markets|stocks?|s&p|sp ?500|nasdaq|dow|index|indexes|today|yesterday|this week|last week|red|green|rall(y|ied)|sell-?off|selloff|crash|news|headlines?|fed|rates?|yields?|treasur(y|ies)|oil|brent|inflation|cpi|jobs|vix|why did|why is|what happened)\b/i;
  function getJSON(u) { return fetch(u, { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }); }
  function getMkt(q) {
    var need = MKT.test(q);
    if (!S.news) S.news = getJSON('data/news.json');
    if (need && !S.px) { S.px = getJSON('data/co/prices.json'); S.mk = getJSON('data/markets.json'); }
    return Promise.all([S.news, need ? S.px : null, need ? S.mk : null]).then(function (a) { return { news: a[0], px: a[1], mk: a[2], need: need }; });
  }
  function fd(iso) { var d = new Date(iso.length <= 10 ? iso + 'T12:00:00Z' : iso); return isNaN(d) ? iso : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'America/New_York' }); }
  function pct(a, b) { return ((a / b - 1) * 100); }
  function sgn(x, d) { return (x >= 0 ? '+' : '') + x.toFixed(d == null ? 2 : d); }
  function marketContext(q, M) {
    var out = [], names = {};
    ((S.ctx && S.ctx.ratings) || []).forEach(function (r) { names[r.t] = r.name; });
    if (M.need && M.px && M.px.px) {
      var px = M.px.px, sp = px['^GSPC'];
      if (sp && sp.pp) out.push('S&P 500 close ' + fd(sp.d) + ': ' + sp.p.toFixed(2) + ' (' + sgn(pct(sp.p, sp.pp)) + '% from ' + fd(sp.pd) + ')');
      var mv = Object.keys(px).filter(function (k) { var x = px[k]; return k[0] !== '^' && x && x.p && x.pp && sp && x.d === sp.d; }).map(function (k) { return [k, pct(px[k].p, px[k].pp)]; });
      if (mv.length > 20) {
        mv.sort(function (a, b) { return a[1] - b[1]; });
        var up = mv.filter(function (x) { return x[1] > 0; }).length;
        var lab = function (x) { return x[0] + (names[x[0]] ? ' (' + names[x[0]] + ')' : '') + ' ' + sgn(x[1], 1) + '%'; };
        out.push('S&P 500 members up / down that day: ' + up + ' / ' + (mv.length - up));
        out.push('Biggest falls: ' + mv.slice(0, 6).map(lab).join(', '));
        out.push('Biggest gains: ' + mv.slice(-6).reverse().map(lab).join(', '));
      }
    }
    if (M.need && M.mk && M.mk.series) {
      ['DGS10', 'DGS2', 'VIXCLS', 'DCOILWTICO', 'BAMLH0A0HYM2', 'DFF'].forEach(function (k) {
        var s = M.mk.series[k]; if (!s || !s.last) return;
        out.push(s.name + ': ' + s.last.v + (s.fmt === 'pct' || /Treasury|spread|funds/i.test(s.name) ? '%' : '') + ' on ' + fd(s.last.d) + (s.prev ? ' (previous ' + s.prev.v + ')' : ''));
      });
    }
    var items = (M.news && M.news.items) || [], qw = words(q), picked = [];
    if (items.length) {
      var sc = items.map(function (x, i) { var lt = x.t.toLowerCase(), s2 = 0; qw.forEach(function (w) { if (w.length > 2 && lt.indexOf(w) >= 0) s2 += w.length > 4 ? 2 : 1; }); return { x: x, s: s2, i: i }; });
      var top = sc.filter(function (o) { return o.s > 0; }).sort(function (a, b) { return b.s - a.s || a.i - b.i; }).slice(0, 10);
      var recent = M.need ? sc.slice(0, 14) : [];
      var seen = {};
      top.concat(recent).forEach(function (o) { if (!seen[o.i]) { seen[o.i] = 1; picked.push(o); } });
      picked.sort(function (a, b) { return a.i - b.i; });
    }
    var txt = '';
    if (out.length) txt += '--- Market data (from the site\'s daily data) ---\n' + out.join('\n') + '\n';
    if (picked.length) txt += '--- Recent headlines (titles only, newest first; feeds updated ' + fd(M.news.updated) + ') ---\n' + picked.map(function (o) { return '- [' + fd(o.x.d || M.news.updated) + ', ' + o.x.s + '] ' + o.x.t; }).join('\n') + '\n';
    else if (M.need) txt += '--- Recent headlines: none available ---\n';
    return txt;
  }
  function getCtx() { if (S.ctx !== null) return Promise.resolve(); return fetch('assets/ctx.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : {}; }).then(function (j) { S.ctx = j; }).catch(function () { S.ctx = {}; }); }

  /* ---------- asking ---------- */
  function stop() { S.busy = null; send.classList.remove('stop'); }
  form.onsubmit = function (e) {
    if (e) e.preventDefault();
    if (S.busy) { stop(); return; }
    var q = ta.value.trim(); if (!q) return;
    ta.value = ''; ta.style.height = 'auto';
    if (!S.eng) {
      if (form.classList.contains('off')) return;
      S.pending = q; S.msgs.push({ role: 'user', content: q }); sset(); render();
      if (!S.loading) setup(); return;
    }
    S.msgs.push({ role: 'user', content: q }); sset(); render(); ask(q);
  };
  function ask(q) {
    var el = document.createElement('div'); el.className = 'aib-m a'; el.innerHTML = '<span class="aib-dots"><i></i><i></i><i></i></span>'; log.appendChild(el); log.scrollTop = log.scrollHeight;
    var tok = {}; S.busy = tok; send.classList.add('stop'); sug.innerHTML = '';
    var MK = null;
    getCtx().then(function () { return getMkt(q); }).then(function (M) {
      MK = M;
      var title = document.title.replace(/\s*\|.*$/, '');
      var today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', timeZone: 'America/New_York' });
      var sys = 'You are the assistant on LDB Finance, a finance research website written by a finance student. Help visitors understand the page they are reading, the companies the site covers, markets and finance concepts. Today is ' + today + ' (New York). ' +
        'Rules: answer in plain English in at most about 150 words unless asked for more. Use the page excerpt, market data and headlines below for any facts and copy numbers exactly. ' +
        'You cannot browse the web: the headlines below are ALL the news you know. Never invent a cause for a market move, a news event, a price or a date. To explain why markets moved, use only the market data and headlines given, and say which headlines you are relying on. ' +
        'If the user mentions a news story that does not appear in the headlines, say plainly that you cannot see that story in the latest headlines, so you can neither confirm nor rule it out, and then explain what the data and headlines do show; do not agree or disagree with the claim. ' +
        'For general finance concepts and history you may use your own knowledge. Do not give personal buy or sell advice (you may explain the site\'s published rating and its reasons).\n\n' +
        'Current page: ' + title + ' (' + location.pathname.split('/').pop() + ')\n--- Page excerpt ---\n' + pageContext(q, M.need ? 1200 : 3200) + '\n--- End of excerpt ---\n' + marketContext(q, MK) + siteContext(q);
      var hist = S.msgs.slice(-7, -1).map(function (m) { return { role: m.role, content: m.content.slice(0, 900) }; });
      var msgs = [{ role: 'system', content: sys }].concat(hist, [{ role: 'user', content: q }]);
      return S.eng.chat.completions.create({ messages: msgs, stream: true, temperature: 0.4, top_p: 0.9, max_tokens: 420, extra_body: { enable_thinking: false } });
    }).then(function (stream) {
      var it = stream[Symbol.asyncIterator](), text = '';
      function step() {
        return it.next().then(function (r) {
          if (S.busy !== tok) { try { S.eng.interruptGenerate(); } catch (x) {} return text; }
          if (r.done) return text;
          var d = r.value.choices && r.value.choices[0] && r.value.choices[0].delta && r.value.choices[0].delta.content || '';
          if (d) { text += d; el.innerHTML = md(strip(text)) + '<span class="cur"></span>'; var near = log.scrollHeight - log.scrollTop - log.clientHeight < 80; if (near) log.scrollTop = log.scrollHeight; }
          return step();
        });
      }
      return step();
    }).then(function (text) {
      var clean = strip(text || '') || '(No answer. Try rephrasing the question.)';
      el.innerHTML = md(clean); S.msgs.push({ role: 'assistant', content: clean }); sset();
      if (S.busy === tok) stop();
    }).catch(function (e) {
      el.innerHTML = '<p>Something went wrong: ' + esc(String(e && e.message || e).slice(0, 100)) + '</p>'; stop();
    });
  }
})();
