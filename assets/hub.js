/* LDB Finance research hub: track record, screener, compare, earnings, insiders and funds, ask the filings.
   Everything runs in the browser from the JSON files the nightly update writes. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var page = document.body.getAttribute('data-page');
  var bust = '?d=' + new Date().toISOString().slice(0, 13);
  function getJSON(p) { return fetch(p + bust, { cache: 'no-store' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function opt(p) { return getJSON(p).catch(function () { return null; }); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var isn = function (v) { return typeof v === 'number' && isFinite(v); };
  var fn = function (t) { return t.replace(/\./g, '-'); };
  function big(v) { if (!isn(v)) return '—'; var a = Math.abs(v), s = v < 0 ? '−' : ''; return a >= 1e12 ? s + '$' + (a / 1e12).toFixed(2) + 'T' : a >= 1e9 ? s + '$' + (a / 1e9).toFixed(1) + 'B' : a >= 1e6 ? s + '$' + (a / 1e6).toFixed(0) + 'M' : a >= 1e3 ? s + '$' + (a / 1e3).toFixed(0) + 'K' : s + '$' + a.toFixed(0); }
  function usd(v, dp) { if (!isn(v)) return '—'; return (v < 0 ? '−' : '') + '$' + Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: dp == null ? 2 : dp, maximumFractionDigits: dp == null ? 2 : dp }); }
  function pc(v, dp) { if (!isn(v)) return '—'; return (v < 0 ? '−' : '') + Math.abs(v * 100).toFixed(dp == null ? 1 : dp) + '%'; }
  function sp(v, dp) { if (!isn(v)) return '—'; return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v * 100).toFixed(dp == null ? 1 : dp) + '%'; }
  function pts(v) { if (!isn(v)) return '—'; return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v * 100).toFixed(1) + ' pts'; }
  function mx(v) { return isn(v) ? v.toFixed(1) + '×' : '—'; }
  function cls(v) { return isn(v) ? (v > 0 ? 'up' : v < 0 ? 'dn' : '') : ''; }
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function fd(s, yr) { if (!s) return '—'; var p = s.split('-'); return MON[+p[1] - 1] + ' ' + (+p[2]) + (yr === false ? '' : ', ' + p[0]); }
  function days(a, b) { return Math.round((new Date(b) - new Date(a)) / 864e5); }
  function median(a) { a = a.filter(isn).sort(function (x, y) { return x - y; }); if (!a.length) return null; var m = a.length >> 1; return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; }
  function last(a) { if (!a) return null; for (var i = a.length - 1; i >= 0; i--) if (isn(a[i])) return a[i]; return null; }
  function row(ix, r) { var o = {}; ix.cols.forEach(function (c, i) { o[c] = r[i]; }); return o; }
  function wait(el, html) { el.innerHTML = '<div class="wait">' + html + '</div>'; }

  /* ---------- company search box (index.json) ---------- */
  function picker(input, list, rows, onPick) {
    var hits = [], sel = -1;
    function search(s) {
      s = s.trim().toLowerCase(); if (!s) return [];
      var out = [];
      rows.forEach(function (r) {
        var t = r.t.toLowerCase(), n = (r.name || '').toLowerCase(), sc = t === s ? 0 : t.indexOf(s) === 0 ? 1 : n.indexOf(s) === 0 ? 2 : n.indexOf(s) >= 0 ? 3 : 9;
        if (sc < 9) out.push([sc, -(r.mcap || 0), r]);
      });
      return out.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; }).slice(0, 8).map(function (x) { return x[2]; });
    }
    function show() {
      list.innerHTML = hits.map(function (r, i) { return '<button type="button" data-i="' + i + '"' + (i === sel ? ' class="on"' : '') + '><b>' + esc(r.t) + '</b><span>' + esc(r.name) + '</span><em>' + esc(r.sector || '') + '</em></button>'; }).join('');
      list.classList.toggle('open', hits.length > 0);
    }
    input.addEventListener('input', function () { hits = search(input.value); sel = hits.length ? 0 : -1; show(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); if (!hits.length) return; sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + hits.length) % hits.length; show(); }
      else if (e.key === 'Enter') { e.preventDefault(); if (hits[sel]) go(hits[sel]); }
      else if (e.key === 'Escape') list.classList.remove('open');
    });
    list.addEventListener('mousedown', function (e) { var b = e.target.closest('button'); if (b) { e.preventDefault(); go(hits[+b.getAttribute('data-i')]); } });
    document.addEventListener('click', function (e) { if (!e.target.closest('.search')) list.classList.remove('open'); });
    function go(r) { list.classList.remove('open'); input.value = ''; hits = []; onPick(r); }
  }

  /* ---------- small line chart (several series) ---------- */
  var PAL = ['var(--acc)', 'var(--ink)', '#5B8A72', '#7A6BB0'];
  function lines(series, labels, fmt) {
    var W = 640, H = 220, L = 46, R = 10, T = 12, B = 26, vals = [];
    series.forEach(function (s) { s.v.forEach(function (x) { if (isn(x)) vals.push(x); }); });
    if (!vals.length) return '';
    var lo = Math.min.apply(null, vals.concat([0])), hi = Math.max.apply(null, vals);
    if (hi === lo) hi = lo + 1;
    var pad = (hi - lo) * .08; lo -= lo < 0 ? pad : 0; hi += pad;
    var n = labels.length, X = function (i) { return L + (n === 1 ? (W - L - R) / 2 : i * (W - L - R) / (n - 1)); }, Y = function (v) { return T + (hi - v) / (hi - lo) * (H - T - B); };
    var g = '';
    for (var k = 0; k <= 4; k++) { var v = lo + (hi - lo) * k / 4, y = Y(v); g += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '" class="gl"/><text x="' + (L - 6) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="end">' + esc(fmt(v)) + '</text>'; }
    if (lo < 0 && hi > 0) g += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(0).toFixed(1) + '" y2="' + Y(0).toFixed(1) + '" class="zl"/>';
    labels.forEach(function (l, i) { if (n <= 8 || i % 2 === n % 2 - 1 + 1) g += '<text x="' + X(i).toFixed(1) + '" y="' + (H - 6) + '" text-anchor="middle">' + esc(l) + '</text>'; });
    series.forEach(function (s, j) {
      var d = '', pen = false;
      s.v.forEach(function (x, i) { if (isn(x)) { d += (pen ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(x).toFixed(1); pen = true; } else pen = false; });
      g += '<path d="' + d + '" fill="none" stroke="' + PAL[j % 4] + '" stroke-width="2"/>';
      s.v.forEach(function (x, i) { if (isn(x)) g += '<circle cx="' + X(i).toFixed(1) + '" cy="' + Y(x).toFixed(1) + '" r="2.6" fill="' + PAL[j % 4] + '"/>'; });
    });
    return '<svg class="hchart" viewBox="0 0 ' + W + ' ' + H + '" role="img">' + g + '</svg><div class="hlgd">' + series.map(function (s, j) { return '<span><i style="background:' + PAL[j % 4] + '"></i>' + esc(s.name) + '</span>'; }).join('') + '</div>';
  }

  /* ---------- quarterly helpers ---------- */
  function lastQ(d) {
    var q = d && d.qs; if (!q || !q.ends || q.ends.length < 2) return null;
    var f = q.f, L = q.ends.length - 1, Y = L - 4;
    var om = function (i) { return i >= 0 && isn(f.ebit[i]) && f.rev[i] ? f.ebit[i] / f.rev[i] : null; };
    var yo = function (k) { return Y >= 0 && isn(f[k][L]) && f[k][Y] ? (f[k][L] - f[k][Y]) / Math.abs(f[k][Y]) : null; };
    var fil = null;
    (d.filings || []).forEach(function (x) { if (!fil && x.per && Math.abs(days(x.per, q.ends[L])) <= 7) fil = x; });
    return { lab: q.lab[L], end: q.ends[L], rev: f.rev[L], revY: yo('rev'), om: om(L), omY: om(Y), omP: om(L - 1), ni: f.ni[L], eps: f.eps[L], epsY: Y >= 0 ? f.eps[Y] : null,
             fcf: isn(f.cfo[L]) && isn(f.capex[L]) ? f.cfo[L] - f.capex[L] : null, cash: f.cash[L], debt: f.debt[L], warn: q.warn, fil: fil,
             prevRev: Y >= 0 ? f.rev[Y] : null, prevEbit: Y >= 0 ? f.ebit[Y] : null, ebit: f.ebit[L], gm: isn(f.gp[L]) && f.rev[L] ? f.gp[L] / f.rev[L] : null, gmY: Y >= 0 && isn(f.gp[Y]) && f.rev[Y] ? f.gp[Y] / f.rev[Y] : null };
  }

  /* =====================================================================================
     TRACK RECORD
     ===================================================================================== */
  if (page === 'track') {
    Promise.all([getJSON('data/calls.json'), opt('data/co/prices.json'), opt('data/markets.json')]).then(function (r) {
      var calls = r[0].calls || [], P = (r[1] && r[1].px) || {}, spx = r[2] && r[2].series && r[2].series.SP500;
      var hist = (spx && (spx.y1 || [])) || [], spNow = spx && spx.last && spx.last.v, spNowD = spx && spx.last && spx.last.d;
      function spAt(d) { var v = null; hist.forEach(function (x) { if (x[0] <= d) v = x[1]; }); return v; }
      var latest = {};
      calls.forEach(function (c) { latest[c.t] = latest[c.t] && latest[c.t].date > c.date ? latest[c.t] : c; });
      var rows = Object.keys(latest).map(function (t) {
        var c = latest[t], px = P[t] && P[t].p, ret = px ? px / c.price - 1 : null, s0 = spAt(c.date), sret = s0 && spNow ? spNow / s0 - 1 : null;
        var rel = isn(ret) && isn(sret) ? ret - sret : null, exp = c.value > c.price ? 1 : -1, age = days(c.date, (P[t] && P[t].d) || c.date);
        var verdict = !isn(rel) ? '—' : age < 30 ? 'Too early' : (c.call === 'Buy' ? (rel > 0 ? 'Ahead' : 'Behind') : (rel * exp > 0 ? 'On track' : 'Off track'));
        var prev = calls.filter(function (x) { return x.t === t && x.date < c.date; });
        return { c: c, px: px, ret: ret, sret: sret, rel: rel, gap: px ? px / c.value - 1 : null, age: age, verdict: verdict, prev: prev };
      }).sort(function (a, b) { return (b.c.held - a.c.held) || ((b.rel == null ? -9 : b.rel) - (a.rel == null ? -9 : a.rel)); });
      var scored = rows.filter(function (x) { return isn(x.rel); }), mature = rows.filter(function (x) { return isn(x.rel) && x.age >= 30; });
      var avg = function (a, k) { return a.length ? a.reduce(function (s, x) { return s + x[k]; }, 0) / a.length : null; };
      var good = mature.filter(function (x) { return x.verdict === 'Ahead' || x.verdict === 'On track'; }).length;
      $('#tsum').innerHTML = '<div><b>' + rows.length + '</b><span>Calls logged</span></div><div><b class="' + cls(avg(scored, 'ret')) + '">' + sp(avg(scored, 'ret')) + '</b><span>Average return since</span></div><div><b class="' + cls(avg(scored, 'rel')) + '">' + sp(avg(scored, 'rel')) + '</b><span>Average against the S&amp;P 500</span></div><div><b>' + (mature.length ? good + ' of ' + mature.length : '—') + '</b><span>' + (mature.length ? 'Calls on track (30+ days old)' : 'Hit rate starts after 30 days') + '</span></div>';
      $('#ttab').innerHTML = '<thead><tr><th>Company</th><th>Date</th><th>Call</th><th>Price then</th><th>Value</th><th>Last close</th><th>Return</th><th>S&amp;P 500</th><th>Difference</th><th>Price vs value</th><th>Verdict</th></tr></thead><tbody>' +
        rows.map(function (x) {
          var c = x.c;
          return '<tr><td><a href="' + esc(c.page) + '">' + esc(c.name) + '</a><small>' + esc(c.t) + (c.held ? ' · held' : ' · watchlist') + (x.prev.length ? ' · earlier: ' + x.prev.map(function (p) { return esc(p.call) + ' ' + fd(p.date, false); }).join(', ') : '') + '</small></td><td>' + fd(c.date) + '</td><td><span class="callb ' + esc(c.call.toLowerCase().replace(/\s.*/, '')) + '">' + esc(c.call) + '</span></td><td>' + usd(c.price) + '</td><td>' + usd(c.value, 0) + '</td><td>' + usd(x.px) + '</td><td class="' + cls(x.ret) + '">' + sp(x.ret) + '</td><td>' + sp(x.sret) + '</td><td class="' + cls(x.rel) + '">' + sp(x.rel) + '</td><td>' + sp(x.gap) + '</td><td>' + esc(x.verdict) + '</td></tr>';
        }).join('') + '</tbody>';
    }).catch(function () { wait($('#ttab'), 'The track record could not load. Try again in a moment.'); });
  }

  /* =====================================================================================
     SCREENER
     ===================================================================================== */
  if (page === 'screener') {
    var F = [
      ['mcapB', 'Market value at least', '$B', 'min'], ['pe', 'P/E at most', '×', 'max'], ['g1', 'Revenue growth at least', '%', 'min'], ['om', 'Operating margin at least', '%', 'min'],
      ['fcfy', 'Free-cash-flow yield at least', '%', 'min'], ['nde', 'Net debt / EBITDA at most', '×', 'max'], ['dy', 'Dividend yield at least', '%', 'min'], ['roe', 'Return on equity at least', '%', 'min'], ['qg', 'Latest-quarter growth at least', '%', 'min']];
    var PRE = {
      'Quality growth': { g1: 15, om: 20, nde: 2 }, 'Value': { pe: 15, fcfy: 6 }, 'Dividend payers': { dy: 3, nde: 3 },
      'Fast growers': { qg: 25 }, 'Fortress balance sheet': { nde: 0, om: 15 }, 'Mega caps': { mcapB: 200 }
    };
    var COLS = [['t', 'Company'], ['mcap', 'Market value'], ['pe', 'P/E'], ['evEbitda', 'EV/EBITDA'], ['g1', 'Revenue growth'], ['g3', '3-year growth'], ['qg', 'Latest quarter'], ['om', 'Op. margin'], ['fcfy', 'FCF yield'], ['nde', 'Net debt/EBITDA'], ['dy', 'Dividend'], ['roe', 'ROE']];
    var state = { f: {}, sector: '', uni: 'all', sort: 'mcap', dir: -1, n: 60, pick: [] };
    getJSON('data/co/index.json').then(function (ix) {
      var rows = ix.rows.map(function (r) { return row(ix, r); });
      var secs = {}; rows.forEach(function (r) { if (r.sector) secs[r.sector] = 1; });
      $('#presets').innerHTML = Object.keys(PRE).map(function (k) { return '<button class="chip" type="button" data-pre="' + esc(k) + '">' + esc(k) + '</button>'; }).join('') + '<button class="chip" type="button" data-pre="">Clear</button>';
      $('#filters').innerHTML = '<label><span>Sector</span><select id="fsec"><option value="">All sectors</option>' + Object.keys(secs).sort().map(function (s) { return '<option>' + esc(s) + '</option>'; }).join('') + '</select></label>' +
        '<label><span>Universe</span><select id="funi"><option value="all">S&amp;P 500 and covered</option><option value="sp">S&amp;P 500 only</option><option value="cov">Covered on this site</option></select></label>' +
        F.map(function (x) { return '<label><span>' + esc(x[1]) + '</span><div class="fin"><input type="number" step="any" data-f="' + x[0] + '" placeholder="any"><em>' + x[2] + '</em></div></label>'; }).join('');
      var COV = {};
      opt('data/watchlist.json').then(function (w) { ((w && w.companies) || []).forEach(function (c) { COV[c.ticker] = c; }); draw(); });
      function pass(r) {
        if (state.sector && r.sector !== state.sector) return false;
        if (state.uni === 'sp' && !r.sp) return false;
        if (state.uni === 'cov' && !COV[r.t]) return false;
        for (var k in state.f) {
          var lim = state.f[k]; if (!isn(lim)) continue;
          var spec = F.filter(function (x) { return x[0] === k; })[0], v = k === 'mcapB' ? (r.mcap || 0) / 1e9 : r[k];
          if (spec[2] === '%') lim = lim / 100;
          if (!isn(v)) return false;
          if (spec[3] === 'min' ? v < lim : v > lim) return false;
        }
        return true;
      }
      function cell(k, v) {
        if (k === 'mcap') return big(v);
        if (k === 'pe' || k === 'evEbitda' || k === 'nde') return mx(v);
        if (k === 'g1' || k === 'g3' || k === 'qg') return '<span class="' + cls(v) + '">' + sp(v) + '</span>';
        return pc(v);
      }
      function draw() {
        var list = rows.filter(pass);
        list.sort(function (a, b) {
          var x = a[state.sort], y = b[state.sort];
          if (state.sort === 't') return state.dir * String(x).localeCompare(String(y));
          if (!isn(x)) return 1; if (!isn(y)) return -1; return state.dir * (x - y);
        });
        $('#scount').textContent = list.length + ' compan' + (list.length === 1 ? 'y' : 'ies');
        $('#stab').innerHTML = '<thead><tr><th></th>' + COLS.map(function (c) { return '<th data-s="' + c[0] + '" class="srt' + (state.sort === c[0] ? ' on' : '') + '">' + c[1] + (state.sort === c[0] ? (state.dir > 0 ? ' ↑' : ' ↓') : '') + '</th>'; }).join('') + '</tr></thead><tbody>' +
          list.slice(0, state.n).map(function (r) {
            var cov = COV[r.t];
            return '<tr><td class="ck"><input type="checkbox" data-pk="' + esc(r.t) + '"' + (state.pick.indexOf(r.t) >= 0 ? ' checked' : '') + ' aria-label="Compare ' + esc(r.t) + '"></td><td><a href="snapshot.html?t=' + encodeURIComponent(r.t) + '">' + esc(r.name) + '</a><small>' + esc(r.t) + ' · ' + esc(r.sub || r.sector || '') + (cov && cov.page ? ' · <a href="' + esc(cov.page) + '">report</a>' : '') + (r.sp ? '' : ' · not in S&amp;P 500') + '</small></td>' +
              COLS.slice(1).map(function (c) { return '<td>' + cell(c[0], r[c[0]]) + '</td>'; }).join('') + '</tr>';
          }).join('') + '</tbody>' + (list.length > state.n ? '<tfoot><tr><td colspan="' + (COLS.length + 1) + '"><button class="pill gh sm" type="button" id="more">Show ' + Math.min(60, list.length - state.n) + ' more</button></td></tr></tfoot>' : '');
        $$('#stab th[data-s]').forEach(function (th) { th.onclick = function () { var k = th.getAttribute('data-s'); if (state.sort === k) state.dir *= -1; else { state.sort = k; state.dir = k === 't' || k === 'pe' || k === 'evEbitda' || k === 'nde' ? 1 : -1; } draw(); }; });
        $$('#stab [data-pk]').forEach(function (cb) { cb.onchange = function () { var t = cb.getAttribute('data-pk'), i = state.pick.indexOf(t); if (cb.checked && i < 0) { if (state.pick.length >= 4) { cb.checked = false; return; } state.pick.push(t); } else if (!cb.checked && i >= 0) state.pick.splice(i, 1); cmp(); }; });
        var m = $('#more'); if (m) m.onclick = function () { state.n += 60; draw(); };
      }
      function cmp() { var a = $('#cmpgo'); a.hidden = state.pick.length < 2; a.href = 'compare.html?t=' + state.pick.map(encodeURIComponent).join(','); a.textContent = 'Compare ' + state.pick.join(', ') + ' →'; }
      $('#fsec').onchange = function () { state.sector = this.value; state.n = 60; draw(); };
      $('#funi').onchange = function () { state.uni = this.value; state.n = 60; draw(); };
      $$('#filters [data-f]').forEach(function (inp) { inp.oninput = function () { var v = parseFloat(inp.value); state.f[inp.getAttribute('data-f')] = isn(v) ? v : null; state.n = 60; $$('#presets .chip').forEach(function (c) { c.classList.remove('on'); }); draw(); }; });
      $$('#presets [data-pre]').forEach(function (b) {
        b.onclick = function () {
          var p = PRE[b.getAttribute('data-pre')] || {};
          state.f = {}; $$('#filters [data-f]').forEach(function (inp) { var k = inp.getAttribute('data-f'); inp.value = p[k] != null ? p[k] : ''; state.f[k] = p[k] != null ? p[k] : null; });
          $$('#presets .chip').forEach(function (c) { c.classList.toggle('on', c === b && b.getAttribute('data-pre')); });
          state.n = 60; draw();
        };
      });
      draw();
    }).catch(function () { wait($('#stab'), 'Company data is on its way. It appears after the nightly update.'); });
  }

  /* =====================================================================================
     COMPARE
     ===================================================================================== */
  if (page === 'compare') {
    var picked = [], IXR = [], DATA = {}, WL = {};
    Promise.all([getJSON('data/co/index.json'), opt('data/watchlist.json')]).then(function (r) {
      IXR = r[0].rows.map(function (x) { return row(r[0], x); });
      ((r[1] && r[1].companies) || []).forEach(function (c) { WL[c.ticker] = c; });
      picker($('#q'), $('#sug'), IXR, function (x) { add(x.t); });
      var q = new URLSearchParams(location.search).get('t');
      (q ? q.split(',') : ['NVDA', 'AMZN', 'META']).slice(0, 4).forEach(function (t) { add(t.trim().toUpperCase(), true); });
      load();
    }).catch(function () { wait($('#cmp'), 'Company data is on its way. It appears after the nightly update.'); });
    function add(t, quiet) {
      if (picked.indexOf(t) >= 0 || !IXR.some(function (r) { return r.t === t; })) return;
      if (picked.length >= 4) picked.shift();
      picked.push(t); if (!quiet) load();
    }
    function load() {
      $('#picked').innerHTML = picked.map(function (t) { return '<button class="chip on" type="button" data-rm="' + esc(t) + '">' + esc(t) + ' ✕</button>'; }).join('') + (picked.length < 2 ? '<span class="mono" style="align-self:center">Add at least two companies</span>' : '');
      $$('#picked [data-rm]').forEach(function (b) { b.onclick = function () { picked.splice(picked.indexOf(b.getAttribute('data-rm')), 1); load(); }; });
      history.replaceState(null, '', 'compare.html' + (picked.length ? '?t=' + picked.join(',') : ''));
      Promise.all(picked.map(function (t) { return DATA[t] ? Promise.resolve(DATA[t]) : getJSON('data/co/' + fn(t) + '.json').then(function (d) { DATA[t] = d; return d; }).catch(function () { return null; }); })).then(draw);
    }
    function draw() {
      if (!picked.length) { $('#cmp').innerHTML = ''; return; }
      var C = picked.map(function (t) {
        var d = DATA[t] || {}, ir = IXR.filter(function (r) { return r.t === t; })[0] || {}, q = lastQ(d), f = d.f || {};
        var rev = d.q && d.q.ttm && isn(d.q.ttm.rev) ? d.q.ttm.rev : last(f.rev);
        return { t: t, d: d, ir: ir, q: q, rev: rev, gm: last(f.gp) && last(f.rev) ? last(f.gp) / last(f.rev) : null, nd: isn(last(f.debt)) ? last(f.debt) - (last(f.cash) || 0) : null };
      });
      var R = [
        ['Price', function (c) { return usd(c.ir.price); }], ['Market value', function (c) { return big(c.ir.mcap); }],
        ['P/E', function (c) { return mx(c.ir.pe); }, 'lo'], ['EV/EBITDA', function (c) { return mx(c.ir.evEbitda); }, 'lo'], ['EV/Sales', function (c) { return mx(c.ir.evSales); }, 'lo'],
        ['Revenue, latest year', function (c) { return big(c.rev); }], ['Revenue growth', function (c) { return sp(c.ir.g1); }, 'hi', 'g1'], ['3-year growth', function (c) { return sp(c.ir.g3); }, 'hi', 'g3'],
        ['Latest quarter growth', function (c) { return sp(c.ir.qg) + (c.ir.qlab ? ' <small>' + esc(c.ir.qlab) + '</small>' : ''); }, 'hi', 'qg'],
        ['Gross margin', function (c) { return pc(c.gm); }, 'hi', 'gm'], ['Operating margin', function (c) { return pc(c.ir.om); }, 'hi', 'om'], ['Net margin', function (c) { return pc(c.ir.nm); }, 'hi', 'nm'],
        ['Return on equity', function (c) { return pc(c.ir.roe); }, 'hi', 'roe'], ['Free-cash-flow yield', function (c) { return pc(c.ir.fcfy); }, 'hi', 'fcfy'],
        ['Net debt', function (c) { return big(c.nd); }], ['Net debt / EBITDA', function (c) { return mx(c.ir.nde); }, 'lo', 'nde'], ['Dividend yield', function (c) { return pc(c.ir.dy); }, 'hi', 'dy'], ['Beta', function (c) { return isn(c.ir.beta) ? c.ir.beta.toFixed(2) : '—'; }],
        ['Our call', function (c) { var w = WL[c.t]; return w && w.page ? '<a href="' + esc(w.page) + '">' + esc(w.call) + (w.value ? ' · $' + w.value : '') + '</a>' : '—'; }]
      ];
      function best(rw) {
        if (!rw[2] || !rw[3]) return -1;
        var vals = C.map(function (c) { return rw[3] === 'gm' ? c.gm : c.ir[rw[3]]; }), b = -1, bv = null;
        vals.forEach(function (v, i) { if (isn(v) && (bv == null || (rw[2] === 'hi' ? v > bv : v < bv))) { bv = v; b = i; } });
        return C.length > 1 ? b : -1;
      }
      var head = '<thead><tr><th></th>' + C.map(function (c) { return '<th><a href="snapshot.html?t=' + encodeURIComponent(c.t) + '">' + esc(c.t) + '</a><small>' + esc(c.ir.name || '') + '</small></th>'; }).join('') + '</tr></thead>';
      var body = '<tbody>' + R.map(function (rw) { var b = best(rw); return '<tr><td>' + rw[0] + '</td>' + C.map(function (c, i) { return '<td' + (i === b ? ' class="best"' : '') + '>' + rw[1](c) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody>';
      // quarterly charts: revenue growth vs a year earlier, and operating margin
      var labs = [], gs = [], ms = [];
      C.forEach(function (c) {
        var q = c.d.qs; if (!q) return;
        var n = q.ends.length, k = Math.min(8, n - 4);
        if (k < 1) return;
        var g = [], m = [], l = [];
        for (var i = n - k; i < n; i++) { g.push(q.f.rev[i] && q.f.rev[i - 4] ? q.f.rev[i] / q.f.rev[i - 4] - 1 : null); m.push(isn(q.f.ebit[i]) && q.f.rev[i] ? q.f.ebit[i] / q.f.rev[i] : null); l.push(MON[+q.ends[i].slice(5, 7) - 1] + ' ' + q.ends[i].slice(2, 4)); }
        while (g.length < 8) { g.unshift(null); m.unshift(null); l.unshift(''); }
        if (l.join('').length > labs.join('').length) labs = l;
        gs.push({ name: c.t, v: g }); ms.push({ name: c.t, v: m });
      });
      var charts = gs.length ? '<div class="grid2" style="margin-top:16px"><div class="panel"><div class="hd"><div><h3 class="sec">Revenue growth by quarter</h3><p>Each quarter against the same quarter a year earlier, from 10-Q filings.</p></div></div>' + lines(gs, labs, function (v) { return Math.round(v * 100) + '%'; }) + '</div>' +
        '<div class="panel"><div class="hd"><div><h3 class="sec">Operating margin by quarter</h3><p>Operating income as a share of revenue.</p></div></div>' + lines(ms, labs, function (v) { return Math.round(v * 100) + '%'; }) + '</div></div>' : '';
      $('#cmp').innerHTML = '<div class="panel"><div class="hd"><div><h3 class="sec">Side by side</h3><p>Latest fiscal year, or the latest twelve months where a newer 10-Q exists. The strongest figure in each row is highlighted.</p></div></div><div class="scroll"><table class="tbl cmpt">' + head + body + '</table></div></div>' + charts;
    }
  }

  /* =====================================================================================
     EARNINGS HUB
     ===================================================================================== */
  if (page === 'earnings') {
    Promise.all([opt('data/earnings.json'), getJSON('data/watchlist.json')]).then(function (r) {
      var E = r[0], wl = (r[1].companies || []).filter(function (c) { return !c.private; }), W = {};
      wl.forEach(function (c) { W[c.ticker] = c; });
      var today = new Date().toISOString().slice(0, 10);
      if (E && E.rows) {
        $('#estamp').textContent = 'Updated ' + fd(E.updated.slice(0, 10)) + '. Holdings are marked.';
        var up = E.rows.filter(function (x) { return x.date && x.date >= today; }), m = '';
        $('#ecal').innerHTML = up.length ? '<div class="ecal">' + up.map(function (x) {
          var w = W[x.t] || {}, dd = days(today, x.date), mo = x.date.slice(0, 7), hd = mo !== m ? '<div class="emo mono">' + MON[+x.date.slice(5, 7) - 1] + ' ' + x.date.slice(0, 4) + '</div>' : ''; m = mo;
          return hd + '<div class="erow"><div class="ed"><b>' + (+x.date.slice(8, 10)) + '</b><span>' + ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][new Date(x.date + 'T12:00:00').getDay()] + '</span></div><div class="en"><b>' + esc(x.name) + '</b><span>' + esc(x.t) + (w.holding ? ' · <i class="held">Held</i>' : '') + (x.when ? ' · ' + esc(x.when) : '') + (x.epsEst ? ' · EPS estimate ' + esc(x.epsEst) : '') + '</span></div>' +
            '<div class="ex"><span class="' + (x.src === 'Nasdaq' ? 'conf' : 'estm') + '">' + (x.src === 'Nasdaq' ? 'Confirmed' : 'Estimated') + '</span><small>' + (dd === 0 ? 'Today' : dd === 1 ? 'Tomorrow' : 'In ' + dd + ' days') + '</small></div>' +
            '<div class="el">' + (w.page ? '<a href="' + esc(w.page) + '">Report</a>' : '') + '<a href="snapshot.html?t=' + encodeURIComponent(x.t) + '&amp;view=q">Quarters</a></div></div>';
        }).join('') + '</div>' : '<p class="mono">No dates in the next few weeks.</p>';
      } else wait($('#ecal'), 'Earnings dates appear after the next nightly update.');
      return Promise.all(wl.map(function (c) { return opt('data/co/' + fn(c.ticker) + '.json'); })).then(function (ds) {
        var rows = [];
        ds.forEach(function (d, i) { var q = lastQ(d); if (q) rows.push({ c: wl[i], q: q }); });
        rows.sort(function (a, b) { return ((b.q.fil && b.q.fil.date) || b.q.end).localeCompare((a.q.fil && a.q.fil.date) || a.q.end); });
        $('#eq').innerHTML = '<thead><tr><th>Company</th><th>Quarter</th><th>Revenue</th><th>vs year ago</th><th>Op. margin</th><th>Change</th><th>EPS</th><th>vs year ago</th><th>Filing</th></tr></thead><tbody>' + rows.map(function (x) {
          var q = x.q, eg = isn(q.eps) && q.epsY > 0 ? q.eps / q.epsY - 1 : null;
          return '<tr><td><a href="snapshot.html?t=' + encodeURIComponent(x.c.ticker) + '&amp;view=q">' + esc(x.c.name) + '</a><small>' + esc(x.c.ticker) + (x.c.holding ? ' · held' : '') + (q.warn ? ' · check filing' : '') + '</small></td><td>' + esc(q.lab) + '<small>' + fd(q.end) + '</small></td><td>' + big(q.rev) + '</td><td class="' + cls(q.revY) + '">' + sp(q.revY) + '</td><td>' + pc(q.om) + '</td><td class="' + cls(isn(q.om) && isn(q.omY) ? q.om - q.omY : null) + '">' + (isn(q.om) && isn(q.omY) ? pts(q.om - q.omY) : '—') + '</td><td>' + usd(q.eps) + '</td><td class="' + cls(eg) + '">' + sp(eg) + '</td><td>' + (q.fil ? '<a href="' + esc(q.fil.url) + '" target="_blank" rel="noopener">' + esc(q.fil.form) + ' ' + fd(q.fil.date, false) + ' ↗</a>' : '—') + '</td></tr>';
        }).join('') + '</tbody>';
      });
    }).catch(function () { wait($('#ecal'), 'The earnings hub could not load. Try again in a moment.'); });
  }

  /* =====================================================================================
     INSIDERS AND FUNDS
     ===================================================================================== */
  if (page === 'insiders') {
    Promise.all([opt('data/insiders.json'), opt('data/funds.json'), opt('data/watchlist.json')]).then(function (r) {
      var I = r[0], Fd = r[1], W = {};
      ((r[2] && r[2].companies) || []).forEach(function (c) { W[c.ticker] = c; });
      if (I && I.companies) {
        var ks = Object.keys(I.companies).sort(function (a, b) { var x = I.companies[a], y = I.companies[b]; return (y.buyVal + y.sellVal) - (x.buyVal + x.sellVal); });
        $('#isum').innerHTML = '<thead><tr><th>Company</th><th>Buys</th><th>Bought</th><th>Sells</th><th>Sold</th><th>Latest trade</th><th></th></tr></thead><tbody>' + ks.map(function (t) {
          var c = I.companies[t], l = c.rows[0];
          return '<tr><td>' + esc(c.name) + '<small>' + esc(t) + (W[t] && W[t].holding ? ' · held' : '') + '</small></td><td>' + c.buys + '</td><td class="' + (c.buyVal ? 'up' : '') + '">' + big(c.buyVal || null) + '</td><td>' + c.sells + '</td><td class="' + (c.sellVal ? 'dn' : '') + '">' + big(c.sellVal || null) + '</td><td>' + (l ? fd(l.d) + '<small>' + esc(l.who) + ', ' + esc(l.type.toLowerCase()) + '</small>' : '—') + '</td><td>' + (c.rows.length ? '<button class="pill gh sm" type="button" data-it="' + esc(t) + '">Trades</button>' : '') + '</td></tr>';
        }).join('') + '</tbody>';
        function det(t) {
          var c = I.companies[t];
          $('#idet').innerHTML = '<h3 class="sec sm">' + esc(c.name) + ': open-market trades</h3><div class="scroll"><table class="tbl"><thead><tr><th>Insider</th><th>Date</th><th>Type</th><th>Shares</th><th>Price</th><th>Value</th><th>Owns after</th><th>Plan</th><th>Form 4</th></tr></thead><tbody>' + c.rows.map(function (x) {
            return '<tr><td>' + esc(x.who) + '<small>' + esc(x.title || '') + '</small></td><td>' + fd(x.d) + '</td><td class="' + (x.type === 'Buy' ? 'up' : 'dn') + '">' + x.type + '</td><td>' + (isn(x.sh) ? Math.round(x.sh).toLocaleString('en-US') : '—') + '</td><td>' + usd(x.px) + '</td><td>' + big(x.val) + '</td><td>' + (isn(x.after) ? Math.round(x.after).toLocaleString('en-US') : '—') + '</td><td>' + (x.plan ? '10b5-1' : '—') + '</td><td><a href="' + esc(x.url) + '" target="_blank" rel="noopener">' + fd(x.filed, false) + ' ↗</a></td></tr>';
          }).join('') + '</tbody></table></div>';
        }
        $$('#isum [data-it]').forEach(function (b) { b.onclick = function () { det(b.getAttribute('data-it')); $('#idet').scrollIntoView({ behavior: 'smooth', block: 'start' }); }; });
      } else wait($('#isum'), 'Insider trades appear after the next nightly update.');
      if (Fd && Fd.funds) {
        $('#fstamp').textContent = 'Latest 13F filings, read ' + fd(Fd.updated.slice(0, 10)) + '. Filed 45 days after each quarter; U.S. stock positions only.';
        var mine = Object.keys(W).filter(function (t) { return Fd.held[t]; });
        var own = mine.length ? '<h3 class="sec sm">Who owns the companies covered here</h3><div class="scroll"><table class="tbl"><thead><tr><th>Company</th><th>Held by</th></tr></thead><tbody>' + mine.map(function (t) {
          return '<tr><td>' + esc(W[t].name) + '<small>' + esc(t) + (W[t].holding ? ' · held' : '') + '</small></td><td style="white-space:normal;text-align:left">' + Fd.held[t].map(function (h) { return esc(h.fund) + ' <small style="display:inline">' + big(h.val) + ', ' + pc(h.pct) + ' of fund</small>'; }).join(' · ') + '</td></tr>';
        }).join('') + '</tbody></table></div>' : '';
        $('#funds').innerHTML = own + '<div class="fgrid">' + Fd.funds.map(function (f) {
          var mxp = f.top.length ? f.top[0].pct : 1;
          return '<div class="fund"><div class="fh"><div><b>' + esc(f.fund) + '</b><span>' + esc(f.mgr) + '</span></div><a class="mono" href="' + esc(f.url) + '" target="_blank" rel="noopener">13F ' + fd(f.period, true) + ' ↗</a></div><p class="mono">' + big(f.total) + ' in ' + f.n + ' positions</p>' +
            f.top.slice(0, 10).map(function (h) { var cov = h.t && W[h.t]; return '<div class="fb"><span>' + (h.t ? '<a href="' + esc(cov && cov.page ? cov.page : 'snapshot.html?t=' + encodeURIComponent(h.t)) + '"' + (cov ? ' class="cov"' : '') + '>' + esc(h.name) + '</a>' : esc(h.name)) + '</span><i style="width:' + (h.pct / mxp * 100).toFixed(1) + '%"></i><em>' + pc(h.pct) + '</em></div>'; }).join('') + '</div>';
        }).join('') + '</div>';
      } else wait($('#funds'), 'Fund holdings appear after the next nightly update.');
    });
  }

  /* =====================================================================================
     ASK THE FILINGS
     ===================================================================================== */
  if (page === 'ask') {
    var CUR = null, IX = null, ROWS = [], WLA = {}, EARN = null, INS = null, FUNDS = null;
    var SUGG = ['How did the latest quarter go?', 'Why did the operating margin change?', 'Is revenue growth speeding up or slowing down?', 'How much free cash flow does it make?', 'How strong is the balance sheet?', 'Is it expensive compared with its peers?', 'Are insiders buying or selling?', 'When does it report next?'];
    Promise.all([getJSON('data/co/index.json'), opt('data/watchlist.json'), opt('data/earnings.json'), opt('data/insiders.json'), opt('data/funds.json')]).then(function (r) {
      IX = r[0]; ROWS = IX.rows.map(function (x) { return row(IX, x); });
      ((r[1] && r[1].companies) || []).forEach(function (c) { WLA[c.ticker] = c; });
      EARN = r[2]; INS = r[3]; FUNDS = r[4];
      picker($('#q'), $('#sug'), ROWS, function (x) { pick(x.t); });
      var t = new URLSearchParams(location.search).get('t');
      pick((t || 'NVDA').toUpperCase());
    }).catch(function () { wait($('#alog'), 'Company data is on its way. It appears after the nightly update.'); });
    $('#asugg').innerHTML = SUGG.map(function (s) { return '<button class="chip" type="button">' + esc(s) + '</button>'; }).join('');
    $$('#asugg .chip').forEach(function (b) { b.onclick = function () { $('#aq').value = b.textContent; submit(); }; });
    $('#aform').addEventListener('submit', function (e) { e.preventDefault(); submit(); });

    function pick(t) {
      var ir = ROWS.filter(function (r) { return r.t === t; })[0];
      if (!ir) { $('#acur').textContent = t + ' is not covered yet'; return; }
      $('#acur').textContent = 'Loading ' + ir.name + '…';
      getJSON('data/co/' + fn(t) + '.json').then(function (d) {
        CUR = { t: t, ir: ir, d: d, q: lastQ(d) };
        $('#acur').innerHTML = '<b>' + esc(ir.name) + '</b> · ' + esc(t) + ' · <a href="snapshot.html?t=' + encodeURIComponent(t) + '">snapshot</a>';
        history.replaceState(null, '', 'ask.html?t=' + encodeURIComponent(t));
        $('#aq').focus();
      }).catch(function () { $('#acur').textContent = 'Figures for ' + ir.name + ' are still being collected'; });
    }

    /* ---- facts: every number the answer may use, each with its source ---- */
    function facts(C) {
      var d = C.d, f = d.f || {}, q = d.qs, ir = C.ir, out = [], n = (d.ends || []).length;
      function add(k, text, src) { out.push({ id: 'F' + (out.length + 1), k: k, text: text, src: src }); }
      function fy(e) { return 'FY' + (e.slice(5, 7) === '01' && +e.slice(8, 10) <= 7 ? +e.slice(0, 4) - 1 : e.slice(0, 4)); }
      var k10 = (d.filings || []).filter(function (x) { return x.form === '10-K'; })[0];
      for (var i = Math.max(0, n - 3); i < n; i++) {
        var om = isn(f.ebit[i]) && f.rev[i] ? f.ebit[i] / f.rev[i] : null, g = i > 0 && f.rev[i - 1] ? f.rev[i] / f.rev[i - 1] - 1 : null;
        add('annual', fy(d.ends[i]) + ': revenue ' + big(f.rev[i]) + (isn(g) ? ' (' + sp(g) + ')' : '') + ', operating income ' + big(f.ebit[i]) + (isn(om) ? ' (' + pc(om) + ' margin)' : '') + ', net income ' + big(f.ni[i]) + ', diluted EPS ' + usd(f.eps[i]) + (isn(f.cfo[i]) && isn(f.capex[i]) ? ', free cash flow ' + big(f.cfo[i] - f.capex[i]) : '') + (f.dps[i] ? ', dividend ' + usd(f.dps[i]) + ' a share' : ''), '10-K ' + fy(d.ends[i]));
      }
      if (q) {
        var L = q.ends.length;
        for (var j = Math.max(0, L - 5); j < L; j++) {
          var qom = isn(q.f.ebit[j]) && q.f.rev[j] ? q.f.ebit[j] / q.f.rev[j] : null, qg = j >= 4 && q.f.rev[j - 4] ? q.f.rev[j] / q.f.rev[j - 4] - 1 : null, gm = isn(q.f.gp[j]) && q.f.rev[j] ? q.f.gp[j] / q.f.rev[j] : null;
          add('quarter', q.lab[j] + ' (to ' + fd(q.ends[j]) + '): revenue ' + big(q.f.rev[j]) + (isn(qg) ? ' (' + sp(qg) + ' vs a year earlier)' : '') + (isn(gm) ? ', gross margin ' + pc(gm) : '') + (isn(qom) ? ', operating margin ' + pc(qom) : '') + ', net income ' + big(q.f.ni[j]) + ', EPS ' + usd(q.f.eps[j]) + (isn(q.f.cfo[j]) && isn(q.f.capex[j]) ? ', free cash flow ' + big(q.f.cfo[j] - q.f.capex[j]) : ''), (j === L - 1 ? '10-Q' : 'Filings') + ' ' + q.lab[j]);
        }
        var Lb = L - 1;
        if (isn(q.f.cash[Lb]) || isn(q.f.debt[Lb])) add('balance', 'At ' + fd(q.ends[Lb]) + ': cash and investments ' + big(q.f.cash[Lb]) + ', debt ' + big(q.f.debt[Lb]) + (isn(q.f.debt[Lb]) ? ', net debt ' + big(q.f.debt[Lb] - (q.f.cash[Lb] || 0)) : ''), '10-Q ' + q.lab[Lb]);
      }
      var sec = ROWS.filter(function (r) { return r.sub === ir.sub && r.t !== ir.t; }), med = function (k) { return median(sec.map(function (r) { return r[k]; })); };
      add('value', 'Price ' + usd(ir.price) + ', market value ' + big(ir.mcap) + ', P/E ' + mx(ir.pe) + ', EV/EBITDA ' + mx(ir.evEbitda) + ', free-cash-flow yield ' + pc(ir.fcfy) + ', dividend yield ' + pc(ir.dy) + ', beta ' + (isn(ir.beta) ? ir.beta.toFixed(2) : '—'), 'Last close and SEC data');
      if (sec.length >= 2) add('peers', 'Peers in ' + ir.sub + ' (' + sec.length + ' companies): median P/E ' + mx(med('pe')) + ', median EV/EBITDA ' + mx(med('evEbitda')) + ', median revenue growth ' + sp(med('g1')) + ', median operating margin ' + pc(med('om')), 'S&P 500 peers');
      add('growth', 'Revenue growth: latest fiscal year ' + sp(ir.g1) + ', three-year average ' + sp(ir.g3) + ', latest quarter ' + sp(ir.qg) + '; return on equity ' + pc(ir.roe) + ', net debt to EBITDA ' + mx(ir.nde), 'SEC data');
      var w = WLA[C.t]; if (w && w.page) add('report', 'LDB Finance report (' + w.date + '): ' + w.call + (w.value ? ', value $' + w.value + ' a share' : ''), 'Report: ' + w.page);
      var e = EARN && EARN.rows && EARN.rows.filter(function (x) { return x.t === C.t; })[0];
      if (e && e.date) add('next', 'Next earnings report: ' + fd(e.date) + (e.when ? ', ' + e.when : '') + (e.src === 'Nasdaq' ? ' (confirmed)' : ' (estimated from past filing dates)') + (e.epsEst ? '; EPS estimate ' + e.epsEst : ''), e.src === 'Nasdaq' ? 'Nasdaq calendar' : 'Estimate');
      var ins = INS && INS.companies && INS.companies[C.t];
      if (ins) add('insiders', 'Insiders over the past year: ' + ins.buys + ' open-market buys (' + big(ins.buyVal || 0) + ') and ' + ins.sells + ' sells (' + big(ins.sellVal || 0) + ')' + (ins.rows[0] ? '; latest: ' + ins.rows[0].who + ' ' + ins.rows[0].type.toLowerCase() + ' on ' + fd(ins.rows[0].d) + (ins.rows[0].plan ? ' under a 10b5-1 plan' : '') : ''), 'SEC Form 4');
      var hf = FUNDS && FUNDS.held && FUNDS.held[C.t];
      if (hf) add('funds', 'Held by ' + hf.map(function (h) { return h.fund + ' (' + big(h.val) + ', ' + pc(h.pct) + ' of its portfolio)'; }).join('; '), 'SEC 13F');
      if (k10) out.forEach(function (x) { if (/^10-K/.test(x.src)) x.url = k10.url; });
      var qfil = C.q && C.q.fil; if (qfil) out.forEach(function (x) { if (/^10-Q/.test(x.src)) x.url = qfil.url; });
      return out;
    }

    /* ---- deterministic answers: the numbers are computed, not generated ---- */
    var INT = [
      ['why', /why|drove|driv|cause|reason|explain|happen/],
      ['margin', /margin|profitab|cost|expense/],
      ['growth', /grow|revenue|sales|top.?line|accelerat|slow/],
      ['quarter', /quarter|latest|recent|last (q|report|result)|earnings (result|report)|how did|results?/],
      ['cash', /cash flow|free cash|fcf|cash generat|capex|spend/],
      ['balance', /debt|balance|leverage|cash pile|liquid|borrow|solvent/],
      ['value', /valu|expensive|cheap|p\/?e|multiple|worth|overpriced|undervalued|buy|sell|price target|peers?/],
      ['dividend', /dividend|payout|yield/],
      ['insiders', /insider|ceo (sold|bought|buy|sell)|executive|director|form 4/],
      ['funds', /fund|buffett|ackman|own(s|ed|er)|holder|13f|institution/],
      ['next', /when|next (report|earnings|quarter)|report date|earnings date|calendar/],
      ['eps', /eps|earnings per share|net income|profit/]
    ];
    function intents(qs) { var s = qs.toLowerCase(), o = []; INT.forEach(function (x) { if (x[1].test(s)) o.push(x[0]); }); if (!o.length) o = ['quarter', 'value']; if (o.indexOf('why') >= 0 && o.indexOf('margin') < 0 && o.indexOf('growth') < 0) o.push('margin'); return o.slice(0, 3); }
    function answer(qs, C, FX) {
      var it = intents(qs), q = C.q, ir = C.ir, f = C.d.f || {}, name = ir.name, P = [], used = {};
      function cite(k) { var x = FX.filter(function (y) { return y.k === k; }); x.forEach(function (y) { used[y.id] = 1; }); return x.length ? ' <sup>' + x.map(function (y) { return y.id; }).join(', ') + '</sup>' : ''; }
      it.forEach(function (k) {
        if (k === 'quarter' && q) {
          P.push('In ' + q.lab + ' (the quarter to ' + fd(q.end) + '), ' + name + ' had revenue of <b>' + big(q.rev) + '</b>' + (isn(q.revY) ? ', ' + (q.revY >= 0 ? 'up ' : 'down ') + pc(Math.abs(q.revY)) + ' from a year earlier' : '') + '. ' + (isn(q.om) ? 'Its operating margin was ' + pc(q.om) + (isn(q.omY) ? ' against ' + pc(q.omY) + ' a year before' : '') + '. ' : '') + (isn(q.eps) ? 'Diluted EPS was ' + usd(q.eps) + (q.epsY > 0 ? ' (' + sp(q.eps / q.epsY - 1) + ')' : '') + '.' : '') + cite('quarter') + (q.warn ? ' <i>These quarters do not add up exactly to the 10-K, so check the filing for exact figures.</i>' : ''));
        }
        if (k === 'why' && q && isn(q.ebit) && isn(q.prevEbit) && q.prevRev) {
          var m0 = q.prevEbit / q.prevRev, m1 = q.ebit / q.rev, dE = q.ebit - q.prevEbit, volume = (q.rev - q.prevRev) * m0, mix = q.rev * (m1 - m0);
          P.push('Operating income moved from ' + big(q.prevEbit) + ' to ' + big(q.ebit) + ' over the year (' + (dE >= 0 ? '+' : '−') + big(Math.abs(dE)).replace('−', '') + '). Splitting that change: about <b>' + big(volume) + '</b> came from ' + (q.rev >= q.prevRev ? 'higher' : 'lower') + ' revenue at last year&rsquo;s margin, and about <b>' + big(mix) + '</b> from the margin itself moving ' + pts(m1 - m0) + '. ' +
            (isn(q.gm) && isn(q.gmY) ? 'Gross margin went from ' + pc(q.gmY) + ' to ' + pc(q.gm) + ', so ' + (Math.abs(q.gm - q.gmY) >= Math.abs(m1 - m0) * .6 ? 'most of the margin change came from the cost of what it sells (pricing, mix or input costs).' : 'most of the margin change came from operating expenses such as R&amp;D, selling and overhead, not from the cost of goods.') : 'The filings do not split out gross margin, so the cause inside costs cannot be separated here.') + cite('quarter') +
            ' <i>The filings give the numbers; for the reasons management gives, read the 10-Q&rsquo;s discussion section.</i>');
        }
        if (k === 'margin' && it.indexOf('why') < 0) {
          var am = (C.d.ends || []).slice(-3).map(function (e, i, a) { var j = C.d.ends.length - a.length + i; return isn(f.ebit[j]) && f.rev[j] ? pc(f.ebit[j] / f.rev[j]) : '—'; });
          P.push('Operating margin over the last three fiscal years: ' + am.join(', ') + '.' + cite('annual') + (q && isn(q.om) ? ' In the latest quarter it was ' + pc(q.om) + (isn(q.omP) ? ', against ' + pc(q.omP) + ' the quarter before' : '') + (isn(q.omY) ? ' and ' + pc(q.omY) + ' a year earlier' : '') + '.' + cite('quarter') : '') + (isn(ir.om) ? ' Peers in ' + esc(ir.sub) + ' have a median operating margin shown below.' + cite('peers') : ''));
        }
        if (k === 'growth') {
          var gq = C.d.qs, tr = '';
          if (gq && gq.ends.length >= 6) {
            var L = gq.ends.length - 1, g1 = gq.f.rev[L] && gq.f.rev[L - 4] ? gq.f.rev[L] / gq.f.rev[L - 4] - 1 : null, g0 = gq.f.rev[L - 1] && gq.f.rev[L - 5] ? gq.f.rev[L - 1] / gq.f.rev[L - 5] - 1 : null;
            if (isn(g1) && isn(g0)) tr = ' Growth against a year earlier went from ' + sp(g0) + ' in ' + gq.lab[L - 1] + ' to ' + sp(g1) + ' in ' + gq.lab[L] + ', so it is <b>' + (g1 > g0 + 0.01 ? 'speeding up' : g1 < g0 - 0.01 ? 'slowing down' : 'holding steady') + '</b>.' + cite('quarter');
          }
          P.push('Revenue grew ' + sp(ir.g1) + ' in the latest fiscal year and ' + sp(ir.g3) + ' a year on average over three years.' + cite('growth') + tr);
        }
        if (k === 'eps' && it.indexOf('quarter') < 0) {
          var n = (C.d.ends || []).length;
          P.push('Net income was ' + big(last(f.ni)) + ' in the latest fiscal year, or ' + usd(last(f.eps)) + ' a diluted share' + (n > 1 && f.eps[n - 2] > 0 && isn(f.eps[n - 1]) ? ' (' + sp(f.eps[n - 1] / f.eps[n - 2] - 1) + ' on the year before)' : '') + '.' + cite('annual') + (q && isn(q.eps) ? ' The latest quarter&rsquo;s EPS was ' + usd(q.eps) + '.' + cite('quarter') : ''));
        }
        if (k === 'cash') {
          var n2 = (C.d.ends || []).length - 1, fcf = isn(f.cfo[n2]) && isn(f.capex[n2]) ? f.cfo[n2] - f.capex[n2] : null, conv = isn(fcf) && f.ni[n2] > 0 ? fcf / f.ni[n2] : null;
          P.push(ir.model === 'bank' ? 'Free cash flow is not a useful measure for a bank, because lending and deposits run through its cash flow. Look at return on equity (' + pc(ir.roe) + ') instead.' + cite('growth') :
            'In the latest fiscal year operating cash flow was ' + big(f.cfo[n2]) + ' and capital spending ' + big(f.capex[n2]) + ', leaving free cash flow of <b>' + big(fcf) + '</b>' + (isn(conv) ? ', ' + Math.round(conv * 100) + '% of net income' : '') + '.' + cite('annual') + ' At today&rsquo;s price that is a free-cash-flow yield of ' + pc(ir.fcfy) + '.' + cite('value') + (q && isn(q.fcf) ? ' The latest quarter produced ' + big(q.fcf) + '.' + cite('quarter') : ''));
        }
        if (k === 'balance') {
          var nd = q && isn(q.debt) ? q.debt - (q.cash || 0) : null;
          P.push(ir.model === 'bank' ? 'For a bank, debt and deposits are the raw material of the business, so net debt is not meaningful; capital ratios in the 10-Q are the better measure.' :
            (q ? 'At ' + fd(q.end) + ' it had ' + big(q.cash) + ' of cash and investments against ' + big(q.debt) + ' of debt, ' + (isn(nd) ? (nd <= 0 ? 'so it holds <b>net cash of ' + big(-nd) + '</b>' : 'so <b>net debt was ' + big(nd) + '</b>') : '') + '.' + cite('balance') : '') + (isn(ir.nde) ? ' That is ' + mx(ir.nde) + ' its annual EBITDA' + (ir.nde < 1 ? ', a very comfortable level' : ir.nde < 3 ? ', a moderate level' : ', on the high side') + '.' + cite('growth') : ''));
        }
        if (k === 'value') {
          var sec = ROWS.filter(function (r) { return r.sub === ir.sub && r.t !== ir.t; }), mpe = median(sec.map(function (r) { return r.pe; })), mev = median(sec.map(function (r) { return r.evEbitda; }));
          P.push('At ' + usd(ir.price) + ' the shares trade at ' + mx(ir.pe) + ' earnings and ' + mx(ir.evEbitda) + ' EBITDA.' + cite('value') + (sec.length >= 2 && isn(mpe) && isn(ir.pe) ? ' Peers in ' + esc(ir.sub) + ' trade at a median ' + mx(mpe) + ' earnings' + (isn(mev) ? ' and ' + mx(mev) + ' EBITDA' : '') + ', so it is <b>' + (ir.pe > mpe * 1.15 ? 'more expensive than its peers' : ir.pe < mpe * .85 ? 'cheaper than its peers' : 'priced roughly in line with its peers') + '</b> on earnings' + (isn(ir.g1) && sec.length ? ', with revenue growth of ' + sp(ir.g1) + ' against a peer median of ' + sp(median(sec.map(function (r) { return r.g1; }))) : '') + '.' + cite('peers') : '') +
            (WLA[C.t] && WLA[C.t].value ? ' This site&rsquo;s report rates it <b>' + esc(WLA[C.t].call) + '</b> with a value of $' + WLA[C.t].value + ' a share.' + cite('report') : ' For a full cash-flow value, open the <a href="valuation.html?t=' + encodeURIComponent(C.t) + '">automatic model</a>.') + ' <i>This is analysis, not a recommendation to buy or sell.</i>');
        }
        if (k === 'dividend') P.push(last(f.dps) ? 'It paid ' + usd(last(f.dps)) + ' a share in dividends in the latest fiscal year, a yield of ' + pc(ir.dy) + ' at today&rsquo;s price.' + cite('annual') + cite('value') : name + ' does not pay a regular dividend according to its latest 10-K.' + cite('annual'));
        if (k === 'insiders') { var ins = INS && INS.companies && INS.companies[C.t]; P.push(ins ? 'Over the past year insiders made ' + ins.buys + ' open-market purchase' + (ins.buys === 1 ? '' : 's') + ' (' + big(ins.buyVal || 0) + ') and ' + ins.sells + ' sale' + (ins.sells === 1 ? '' : 's') + ' (' + big(ins.sellVal || 0) + ').' + cite('insiders') + ' Sales are common for pay and diversification, and many are pre-scheduled under 10b5-1 plans, so buys usually say more than sells. <a href="insiders.html">See every trade</a>.' : 'Insider trades are tracked for the companies covered on this site. ' + name + ' is not one of them yet.'); }
        if (k === 'funds') { var hf = FUNDS && FUNDS.held && FUNDS.held[C.t]; P.push(hf ? 'Among the well-known investors tracked here, it is held by ' + hf.map(function (h) { return h.fund + ' (' + big(h.val) + ')'; }).join(', ') + '.' + cite('funds') : 'None of the well-known funds tracked on <a href="insiders.html">Insiders and funds</a> listed it in their latest 13F.'); }
        if (k === 'next') { var e = EARN && EARN.rows && EARN.rows.filter(function (x) { return x.t === C.t; })[0]; P.push(e && e.date ? name + ' reports next on <b>' + fd(e.date) + '</b>' + (e.when ? ', ' + e.when : '') + (e.src === 'Nasdaq' ? '.' : ' (estimated from its past filing dates; the company has not confirmed it yet).') + cite('next') : 'The next report date is not available yet.'); }
      });
      if (!P.length) P.push('The filings for ' + name + ' do not have figures for that yet.');
      return { html: P.map(function (p) { return '<p>' + p + '</p>'; }).join(''), used: Object.keys(used) };
    }

    var LOG = [];
    function submit() {
      var qs = $('#aq').value.trim(); if (!qs) return;
      if (!CUR) { $('#acur').textContent = 'Pick a company first'; return; }
      var FX = facts(CUR), a = answer(qs, CUR, FX), id = 'a' + LOG.length;
      LOG.push(1);
      var shown = FX.filter(function (x) { return a.used.indexOf(x.id) >= 0; });
      var card = document.createElement('div');
      card.className = 'panel acard'; card.id = id;
      card.innerHTML = '<div class="aq"><span class="mono">' + esc(CUR.t) + '</span><b>' + esc(qs) + '</b></div><div class="ans">' + a.html + '</div>' +
        (AI.eng ? '<div class="aiw"><span class="mono">AI summary · ' + esc(AI.name) + ', on your device</span><div class="ait"><span class="cur"></span></div></div>' : '') +
        (shown.length ? '<details class="srcs"><summary>Sources (' + shown.length + ')</summary>' + shown.map(function (x) { return '<p><b>' + x.id + '</b> ' + esc(x.text) + ' <span class="mono">' + (x.url ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener">' + esc(x.src) + ' ↗</a>' : esc(x.src)) + '</span></p>'; }).join('') + '</details>' : '');
      $('#alog').insertBefore(card, $('#alog').firstChild);
      $('#aq').value = '';
      if (AI.eng) aiWrite(qs, FX, card.querySelector('.ans').textContent, card.querySelector('.ait'));
    }

    /* ---- optional: an AI model in the browser rewrites the computed answer in plain English ---- */
    var AI = { eng: null, name: '', busy: null };
    var WLURL = 'https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm@0.2.85/lib/index.js';
    var MODELS = [['Qwen3-1.7B-q4f16_1-MLC', 'Qwen3 1.7B', 'about 1.1 GB'], ['Qwen3-0.6B-q4f16_1-MLC', 'Qwen3 0.6B', 'about 0.5 GB']];
    (function () {
      var box = $('#aimode');
      if (!navigator.gpu) { box.innerHTML = '<p class="mono">Plain-English AI summaries need WebGPU (Chrome or Edge on a computer, or Safari 26). Answers below are computed straight from the filings either way.</p>'; return; }
      box.innerHTML = '<div class="aion"><div><b>AI summaries</b><span>Optional. A small open model (Qwen3) runs privately in your browser and rewrites each answer in plain English, using only the figures shown. Downloads once.</span></div><div class="aibtn">' + MODELS.map(function (m, i) { return '<button class="pill gh sm" type="button" data-m="' + i + '">' + esc(m[1]) + ' · ' + esc(m[2]) + '</button>'; }).join('') + '</div></div><div class="aiprog" hidden><i></i><span></span></div>';
      $$('#aimode [data-m]').forEach(function (b) {
        b.onclick = function () {
          var m = MODELS[+b.getAttribute('data-m')], pg = $('#aimode .aiprog'), bar = pg.querySelector('i'), lab = pg.querySelector('span');
          $$('#aimode [data-m]').forEach(function (x) { x.disabled = true; }); pg.hidden = false; lab.textContent = 'Starting…';
          import(WLURL).then(function (W) { return W.CreateMLCEngine(m[0], { initProgressCallback: function (r) { var p = (r.progress || 0) * 100; bar.style.width = p.toFixed(0) + '%'; lab.textContent = p >= 100 ? 'Starting the model…' : 'Downloading ' + Math.round(p) + '%'; } }); })
            .then(function (eng) { AI.eng = eng; AI.name = m[1]; pg.hidden = true; $('#aimode .aion').innerHTML = '<div><b>AI summaries on</b><span>' + esc(m[1]) + ' is running on your device. New answers get a plain-English summary.</span></div>'; })
            .catch(function (e) { lab.textContent = 'The model could not start on this device (' + String(e && e.message || e).slice(0, 80) + '). Computed answers still work.'; $$('#aimode [data-m]').forEach(function (x) { x.disabled = false; }); });
        };
      });
    })();
    function aiWrite(qs, FX, computed, el) {
      var sys = 'You are a careful equity research assistant. Answer the question about the company in 3 to 5 plain-English sentences for a finance student. Use ONLY the computed answer and facts provided; copy every number exactly as written and do not add any other numbers, news or opinions. If the facts do not answer the question, say so. Do not give buy or sell advice.';
      var user = 'Company: ' + CUR.ir.name + ' (' + CUR.t + ')\nQuestion: ' + qs + '\n\nComputed answer:\n' + computed + '\n\nFacts:\n' + FX.map(function (x) { return x.id + ': ' + x.text; }).join('\n');
      var text = '', tok = {}; AI.busy = tok;
      AI.eng.chat.completions.create({ messages: [{ role: 'system', content: sys }, { role: 'user', content: user }], stream: true, temperature: 0.3, max_tokens: 260, extra_body: { enable_thinking: false } }).then(function (stream) {
        var it = stream[Symbol.asyncIterator]();
        function step() { return it.next().then(function (r) { if (r.done || AI.busy !== tok) return; var d = r.value.choices && r.value.choices[0] && r.value.choices[0].delta && r.value.choices[0].delta.content || ''; if (d) { text += d; el.innerHTML = esc(text.replace(/<think>[\s\S]*?(<\/think>|$)/g, '').trim()) + '<span class="cur"></span>'; } return step(); }); }
        return step();
      }).then(function () {
        var clean = text.replace(/<think>[\s\S]*?(<\/think>|$)/g, '').trim();
        // flag any number in the AI text that is not in the facts, so a made-up figure cannot pass silently
        var src = computed + ' ' + FX.map(function (x) { return x.text; }).join(' '), bad = (clean.match(/\$?\d[\d,.]*\s?(%|B|M|T|×)?/g) || []).filter(function (n) { var c = n.replace(/[^\d.]/g, ''); return c.length > 1 && src.replace(/,/g, '').indexOf(c) < 0; });
        el.innerHTML = esc(clean || '(no summary)') + (bad.length ? '<small class="aiwarn">Check: ' + esc(bad.slice(0, 3).join(', ')) + ' ' + (bad.length === 1 ? 'is' : 'are') + ' not in the sources.</small>' : '');
      }).catch(function (e) { el.textContent = 'The AI summary failed: ' + String(e && e.message || e).slice(0, 80); });
    }
  }
})();
