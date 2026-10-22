/* LDB Finance: theme, menu, data loading and charts. No libraries. */
(function () {
  'use strict';
  var d = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- theme toggle (initial theme is set in <head>) ---------- */
  var sun = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var moon = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5Z"/></svg>';
  var tileRedraw = function () {};
  var tg = $('#tg'), meta = $('meta[name="theme-color"]');
  function paint() { var lt = d.classList.contains('lt'); if (tg) tg.innerHTML = lt ? sun : moon; if (meta) meta.content = lt ? '#F7F2E9' : '#0C0A08'; }
  if (tg) tg.onclick = function () {
    d.classList.toggle('lt');
    var h = new Date().getHours(), byHour = h >= 7 && h < 19;
    try { sessionStorage.setItem('theme', (d.classList.contains('lt') ? 'light' : 'dark') + '|' + byHour); } catch (e) {}
    paint(); redraw(); tileRedraw();
  };
  paint();

  /* ---------- phone menu ---------- */
  var mb = $('#mb'), menu = $('#menu');
  if (mb && menu) {
    mb.onclick = function () { var o = menu.classList.toggle('open'); mb.setAttribute('aria-expanded', o); mb.innerHTML = o ? icX : icM; };
    $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { menu.classList.remove('open'); mb.innerHTML = icM; }); });
  }
  var icM = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 8h16M4 16h16"/></svg>';
  var icX = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>';
  if (mb) mb.innerHTML = icM;

  /* ---------- window tiles behind the home hero ----------
     A grid of small "windows" that light up and dim at their own pace.
     Canvas, ~24 frames a second, paused when off screen or the tab is hidden. */
  var cv = $('#tilebg');
  if (cv && cv.getContext) {
    var ctx = cv.getContext('2d'), tiles = [], W = 0, H = 0, run = false, vis = true, last = 0, t0 = performance.now();
    var still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var SX = 16, SY = 15, TW = 10, TH = 6;
    function seed(i) { var x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
    function size() {
      var r = cv.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = r.width; H = r.height; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      tiles = []; var cols = Math.ceil(W / SX) + 1, rows = Math.ceil(H / SY) + 1, k = 0;
      for (var y = 0; y < rows; y++) for (var x = 0; x < cols; x++, k++) {
        var a = seed(k), b = seed(k + 9973), c = seed(k + 19997);
        tiles.push({ x: x * SX + 3, y: y * SY + 4, base: .05 + a * .07, peak: c < .22 ? .55 + b * .4 : .14 + b * .12, sp: .05 + b * .16, ph: a * 6.283 });
      }
      draw(performance.now());
    }
    function draw(now) {
      var lt = d.classList.contains('lt'), t = (now - t0) / 1000;
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = lt ? 'rgb(122,69,38)' : 'rgb(232,170,110)';
      var k = lt ? .55 : 1;
      for (var i = 0; i < tiles.length; i++) {
        var p = tiles[i], s = still ? .5 : Math.max(0, Math.sin(t * p.sp * 6.283 + p.ph));
        ctx.globalAlpha = (p.base + (p.peak - p.base) * s * s * s) * k;
        ctx.fillRect(p.x, p.y, TW, TH);
      }
      ctx.globalAlpha = 1;
    }
    function loop(now) {
      if (!run) return;
      if (now - last > 41) { last = now; draw(now); }
      requestAnimationFrame(loop);
    }
    function go() { var want = vis && !document.hidden && !still; if (want && !run) { run = true; requestAnimationFrame(loop); } else if (!want) run = false; }
    size();
    var rz; window.addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(size, 150); });
    document.addEventListener('visibilitychange', go);
    if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { vis = e[0].isIntersecting; go(); }).observe(cv); else go();
    tileRedraw = function () { draw(performance.now()); };
  }

  /* ---------- formatting ---------- */
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function pd(s) { var p = s.split('-'); return new Date(Date.UTC(+p[0], +p[1] - 1, +(p[2] || 1))); }
  function fdate(s, yr) { var t = pd(s); return MON[t.getUTCMonth()] + ' ' + t.getUTCDate() + (yr ? ', ' + t.getUTCFullYear() : ''); }
  function fmon(s) { var t = pd(s); return MON[t.getUTCMonth()] + ' ' + t.getUTCFullYear(); }
  function comma(v, dp) { return v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function sgn(v) { return v > 0 ? '+' : v < 0 ? '−' : ''; }
  /* change shown at display precision, so a tiny move never reads as "-0" */
  function rc(s) {
    if (s.fmt === 'rate') return s.chg == null ? null : Math.round(s.chg * 100);
    if (s.fmt === 'macro') return s.chg == null ? null : Math.round(s.chg * 10) / 10;
    if (s.fmt === 'level') return s.chg == null ? null : Math.round(s.chg * 100) / 100;
    return s.chgPct == null ? null : Math.round(s.chgPct * 100) / 100;
  }
  var F = {
    rate:  { v: function (v) { return v.toFixed(2) + '<small>%</small>'; }, t: function (v) { return v.toFixed(2) + '%'; }, c: function (x) { return sgn(x) + Math.abs(x) + ' bp'; } },
    macro: { v: function (v) { return v.toFixed(1) + '<small>%</small>'; }, t: function (v) { return v.toFixed(1) + '%'; }, c: function (x) { return sgn(x) + Math.abs(x).toFixed(1) + ' pp'; } },
    index: { v: function (v) { return comma(v, 2); }, t: function (v) { return comma(v, 2); }, c: function (x) { return sgn(x) + Math.abs(x).toFixed(2) + '%'; } },
    price: { v: function (v) { return '<small>$</small>' + v.toFixed(2); }, t: function (v) { return '$' + v.toFixed(2); }, c: function (x) { return sgn(x) + Math.abs(x).toFixed(2) + '%'; } },
    fx:    { v: function (v) { return v.toFixed(4); }, t: function (v) { return v.toFixed(4); }, c: function (x) { return sgn(x) + Math.abs(x).toFixed(2) + '%'; } },
    level: { v: function (v) { return v.toFixed(2); }, t: function (v) { return v.toFixed(2); }, c: function (x) { return sgn(x) + Math.abs(x).toFixed(2); } }
  };
  function fmt(s) { var f = F[s.fmt] || F.level; return { v: f.v, t: f.t, c: function (s2) { var x = rc(s2); return x == null ? '' : f.c(x); } }; }
  /* green/red only where up is plainly good (stock index); a rising yield or inflation rate is not "good" */
  function dir(s) { if (s.fmt !== 'index') return ''; var x = rc(s); return x > 0 ? 'up' : x < 0 ? 'dn' : ''; }
  function money(v) { if (v == null) return '—'; var a = Math.abs(v), s = v < 0 ? '−' : ''; return a >= 1e12 ? s + '$' + (a / 1e12).toFixed(2) + 'T' : a >= 1e9 ? s + '$' + (a / 1e9).toFixed(1) + 'B' : a >= 1e6 ? s + '$' + (a / 1e6).toFixed(0) + 'M' : s + '$' + comma(a, 0); }
  function pct(v, dp) { return v == null ? '—' : sgn(v) + Math.abs(v * 100).toFixed(dp == null ? 1 : dp) + '%'; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* ---------- data ---------- */
  var base = (document.body.getAttribute('data-root') || '');
  function getJSON(p) { return fetch(base + p + '?t=' + Math.floor(Date.now() / 600000), { cache: 'no-store' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }

  /* ---------- charts ---------- */
  var NS = 'http://www.w3.org/2000/svg';
  function css(v) { return getComputedStyle(d).getPropertyValue(v).trim(); }
  function spark(pts, cls) {
    if (!pts || pts.length < 2) return '';
    var W = 100, H = 30, xs = pts.map(function (p, i) { return i; }), ys = pts.map(function (p) { return p[1]; });
    var mn = Math.min.apply(null, ys), mx = Math.max.apply(null, ys), r = mx - mn || 1;
    var path = pts.map(function (p, i) { return (i ? 'L' : 'M') + (i / (pts.length - 1) * W).toFixed(2) + ' ' + (H - (p[1] - mn) / r * H).toFixed(2); }).join('');
    return '<svg class="spark" viewBox="0 0 100 30" preserveAspectRatio="none"><path d="' + path + '" fill="none" stroke="' + (cls === 'dn' ? 'var(--dn)' : cls === 'up' ? 'var(--up)' : 'var(--acc)') + '" stroke-width="1.4" vector-effect="non-scaling-stroke"/></svg>';
  }
  function niceTicks(mn, mx, n) {
    var span = mx - mn || 1, step = Math.pow(10, Math.floor(Math.log10(span / n))), err = span / n / step;
    step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
    var t = [], s = Math.floor(mn / step) * step;
    for (var v = s; v <= mx + step * .5; v += step) t.push(+v.toFixed(10));
    return t;
  }
  /* line chart: sets = [{pts:[[date,v]], color, w, dash, area}], o = {yf, zero, xYears} */
  function line(el, sets, o) {
    o = o || {};
    var W = el.clientWidth || 600, H = el.clientHeight || 260, L = 46, R = 10, T = 10, B = 26;
    var all = []; sets.forEach(function (s) { s.pts.forEach(function (p) { all.push(p); }); });
    if (!all.length) { el.innerHTML = ''; return; }
    var t0 = Math.min.apply(null, all.map(function (p) { return pd(p[0]).getTime(); })), t1 = Math.max.apply(null, all.map(function (p) { return pd(p[0]).getTime(); }));
    var ys = all.map(function (p) { return p[1]; }), mn = Math.min.apply(null, ys), mx = Math.max.apply(null, ys);
    if (o.zero) { mn = Math.min(mn, 0); mx = Math.max(mx, 0); }
    var pad = (mx - mn) * .08 || 1; mn -= pad; mx += pad;
    var ticks = niceTicks(mn, mx, 4); mn = Math.min(mn, ticks[0]); mx = Math.max(mx, ticks[ticks.length - 1]);
    var X = function (t) { return L + (t - t0) / ((t1 - t0) || 1) * (W - L - R); }, Y = function (v) { return T + (1 - (v - mn) / ((mx - mn) || 1)) * (H - T - B); };
    var g = '';
    ticks.forEach(function (v) { if (v < mn || v > mx) return; g += '<line class="gl" x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(v) + '" y2="' + Y(v) + '"/><text x="' + (L - 8) + '" y="' + (Y(v) + 3.5) + '" text-anchor="end">' + (o.yf ? o.yf(v) : v) + '</text>'; });
    if (o.zero && mn < 0) g += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(0) + '" y2="' + Y(0) + '" stroke="var(--t3)" stroke-dasharray="3 4"/>';
    /* x labels: months, or years for long ranges */
    var years = (t1 - t0) > 400 * 864e5, a = new Date(t0), labs = [], cur;
    if (years) { for (var yy = a.getUTCFullYear() + 1; Date.UTC(yy, 0, 1) <= t1; yy++) labs.push([Date.UTC(yy, 0, 1), String(yy)]); }
    else { cur = new Date(Date.UTC(a.getUTCFullYear(), a.getUTCMonth() + 1, 1)); while (cur.getTime() <= t1) { labs.push([cur.getTime(), MON[cur.getUTCMonth()]]); cur = new Date(Date.UTC(cur.getUTCFullYear(), cur.getUTCMonth() + 1, 1)); } }
    var every = Math.ceil(labs.length / Math.max(2, Math.floor((W - L) / 70)));
    labs.forEach(function (l, i) { if (i % every) return; g += '<text x="' + X(l[0]) + '" y="' + (H - 6) + '" text-anchor="middle">' + l[1] + '</text>'; });
    sets.forEach(function (s) {
      if (s.pts.length < 2) return;
      var p = s.pts.map(function (q, i) { return (i ? 'L' : 'M') + X(pd(q[0]).getTime()).toFixed(1) + ' ' + Y(q[1]).toFixed(1); }).join('');
      if (s.area) g += '<path d="' + p + 'L' + X(pd(s.pts[s.pts.length - 1][0]).getTime()).toFixed(1) + ' ' + Y(Math.max(mn, Math.min(0, mx))).toFixed(1) + 'L' + X(pd(s.pts[0][0]).getTime()).toFixed(1) + ' ' + Y(Math.max(mn, Math.min(0, mx))).toFixed(1) + 'Z" fill="' + s.color + '" opacity=".1"/>';
      g += '<path d="' + p + '" fill="none" stroke="' + s.color + '" stroke-width="' + (s.w || 1.6) + '"' + (s.dash ? ' stroke-dasharray="' + s.dash + '"' : '') + ' stroke-linejoin="round"/>';
    });
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H); el.innerHTML = g;
  }
  /* yield curve: categorical tenors */
  function curve(el, c) {
    var W = el.clientWidth || 600, H = el.clientHeight || 260, L = 40, R = 12, T = 10, B = 26, n = c.tenors.length;
    var vals = []; c.sets.forEach(function (s) { s.v.forEach(function (v) { if (v != null) vals.push(v); }); });
    if (!vals.length) { el.innerHTML = ''; return; }
    var mn = Math.min.apply(null, vals), mx = Math.max.apply(null, vals), pad = (mx - mn) * .12 || .5; mn -= pad; mx += pad;
    var ticks = niceTicks(mn, mx, 4); mn = Math.min(mn, ticks[0]); mx = Math.max(mx, ticks[ticks.length - 1]);
    var X = function (i) { return L + i / (n - 1) * (W - L - R); }, Y = function (v) { return T + (1 - (v - mn) / (mx - mn)) * (H - T - B); };
    var g = '';
    ticks.forEach(function (v) { if (v < mn || v > mx) return; g += '<line class="gl" x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(v) + '" y2="' + Y(v) + '"/><text x="' + (L - 8) + '" y="' + (Y(v) + 3.5) + '" text-anchor="end">' + v.toFixed(v % 1 ? 1 : 0) + '%</text>'; });
    var skip = W < 420 ? 2 : 1;
    c.tenors.forEach(function (t, i) { if (i % skip && i !== n - 1) return; g += '<text x="' + X(i) + '" y="' + (H - 6) + '" text-anchor="middle">' + t + '</text>'; });
    var cols = [css('--acc'), css('--t2'), css('--t3')], dash = ['', '4 4', '1 4'];
    c.sets.slice().reverse().forEach(function (s, ri) {
      var k = c.sets.length - 1 - ri, p = '', started = false;
      s.v.forEach(function (v, i) { if (v == null) return; p += (started ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1); started = true; });
      g += '<path d="' + p + '" fill="none" stroke="' + cols[k] + '" stroke-width="' + (k ? 1.4 : 2.2) + '"' + (dash[k] ? ' stroke-dasharray="' + dash[k] + '"' : '') + '/>';
      if (!k) s.v.forEach(function (v, i) { if (v != null) g += '<circle cx="' + X(i) + '" cy="' + Y(v) + '" r="2.6" fill="' + cols[0] + '"/>'; });
    });
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H); el.innerHTML = g;
  }

  /* ---------- renderers ---------- */
  var M = null, redrawers = [];
  function redraw() { redrawers.forEach(function (f) { f(); }); }
  var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(redraw, 150); });

  function tile(s, key) {
    if (!s || !s.last) return '<div class="tile"><div class="k mono">' + esc(key) + '</div><div class="v">—</div></div>';
    var f = fmt(s), dr = dir(s);
    return '<div class="tile"><div class="k"><span class="mono">' + esc(s.short || s.name) + '</span><span class="mono">' + fdate(s.last.d) + '</span></div>' +
      '<div class="v">' + f.v(s.last.v) + '</div><div class="d ' + dr + '">' + (f.c(s) || '&nbsp;') + ' <span style="color:var(--t3)">' + esc(s.chgLabel || '') + '</span></div>' + spark(s.y1, dr) + '</div>';
  }
  function row(s) {
    if (!s || !s.last) return '';
    var f = fmt(s), dr = dir(s);
    return '<tr><td>' + esc(s.name) + '<small>' + (s.note ? esc(s.note) + ' &middot; ' : '') + fdate(s.last.d) + '</small></td><td>' + f.t(s.last.v) + '</td><td class="' + dr + '">' + (f.c(s) || '—') + '</td><td>' + spark(s.y1, dr) + '</td></tr>';
  }
  function table(keys) {
    return '<div class="scroll"><table class="tbl mkt"><thead><tr><th>Series</th><th>Latest</th><th>Change</th><th>1 year</th></tr></thead><tbody>' +
      keys.map(function (k) { return row(M.series[k]); }).join('') + '</tbody></table></div>';
  }
  function waiting(el) {
    el.innerHTML = '<div class="wait"><b>Waiting for the first data update.</b> Market data is refreshed every weekday evening from the Federal Reserve (FRED). It appears here after the update runs for the first time.</div>';
  }
  function stamp() {
    if (!M || !M.updated) return '';
    var t = new Date(M.updated);
    return 'Updated ' + MON[t.getMonth()] + ' ' + t.getDate() + ', ' + t.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }

  $$('footer .yr').forEach(function (e) { e.textContent = new Date().getFullYear(); });
  var page = document.body.getAttribute('data-page');

  /* ---------- market tape: the last close, holdings, upcoming earnings and the newest calls ---------- */
  (function () {
    var nav = $('nav.top'); if (!nav) return;
    var tape = document.createElement('div');
    tape.className = 'tape'; tape.setAttribute('role', 'region'); tape.setAttribute('aria-label', 'Market tape');
    nav.parentNode.insertBefore(tape, nav.nextSibling);
    var M3 = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var dd = function (s) { var p = s.split('-'); return M3[+p[1] - 1] + ' ' + (+p[2]); };
    var sg = function (v, s) { return v > 0 ? 'up' : v < 0 ? 'dn' : ''; };
    var pctS = function (v) { return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(2) + '%'; };
    var opt = function (p) { return getJSON(p).catch(function () { return null; }); };
    Promise.all([opt('data/markets.json'), opt('data/co/prices.json'), opt('data/watchlist.json'), opt('data/earnings.json'), opt('data/calls.json')]).then(function (r) {
      var S = (r[0] && r[0].series) || {}, P = (r[1] && r[1].px) || {}, W = (r[2] && r[2].companies) || [], E = (r[3] && r[3].rows) || [], C = (r[4] && r[4].calls) || [];
      var it = [], when = null;
      function item(href, label, val, chg, cls) { it.push('<a class="ti" href="' + base + href + '"><span>' + label + '</span><b>' + val + '</b>' + (chg ? '<em class="' + (cls || '') + '">' + chg + '</em>' : '') + '</a>'); }
      function head(t) { it.push('<span class="th">' + t + '</span>'); }
      // markets, from the Federal Reserve's FRED (the S&P uses the index's own close when it is newer)
      head('Markets');
      var spx = P['^GSPC'], s5 = S.SP500;
      if (spx && spx.p) { var c = spx.pp ? (spx.p / spx.pp - 1) * 100 : null; item('markets.html', 'S&amp;P 500', spx.p.toLocaleString('en-US', { maximumFractionDigits: 2 }), c == null ? '' : pctS(c), sg(c)); when = spx.d; }
      else if (s5 && s5.last) { item('markets.html', 'S&amp;P 500', s5.last.v.toLocaleString('en-US', { maximumFractionDigits: 2 }), pctS(s5.chgPct), sg(s5.chgPct)); when = s5.last.d; }
      [['DGS10', '10Y Treasury'], ['DGS2', '2Y Treasury'], ['DFF', 'Fed funds']].forEach(function (x) { var v = S[x[0]]; if (v && v.last) { var bp = Math.round((v.chg || 0) * 100); item('markets.html', x[1], v.last.v.toFixed(2) + '%', x[0] === 'DFF' ? '' : (bp > 0 ? '+' : bp < 0 ? '−' : '') + Math.abs(bp) + ' bp', sg(bp)); } });
      var vx = S.VIXCLS; if (vx && vx.last) item('markets.html', 'VIX', vx.last.v.toFixed(2), (vx.chg > 0 ? '+' : vx.chg < 0 ? '−' : '') + Math.abs(vx.chg || 0).toFixed(2), vx.chg > 0 ? 'dn' : vx.chg < 0 ? 'up' : '');
      var oil = S.DCOILWTICO; if (oil && oil.last) item('markets.html', 'Oil (WTI)', '$' + oil.last.v.toFixed(2), pctS(oil.chgPct || 0), sg(oil.chgPct));
      var fx = S.DEXUSEU; if (fx && fx.last) item('markets.html', 'EUR/USD', fx.last.v.toFixed(4), pctS(fx.chgPct || 0), sg(fx.chgPct));
      var mg = S.MORTGAGE30US; if (mg && mg.last) item('loans.html', '30Y mortgage', mg.last.v.toFixed(2) + '%');
      // holdings
      var H = W.filter(function (c) { return c.holding && !c.private && P[c.ticker] && P[c.ticker].p; });
      if (H.length) {
        head('Holdings');
        H.forEach(function (c) { var q = P[c.ticker], ch = q.pp ? (q.p / q.pp - 1) * 100 : null; item(c.page || 'snapshot.html?t=' + c.ticker, c.ticker, '$' + q.p.toFixed(2), ch == null ? '' : pctS(ch), sg(ch)); if (!when || q.d > when) when = q.d; });
      }
      // earnings in the next seven days
      var today = new Date(); today.setHours(0, 0, 0, 0);
      var soon = E.filter(function (e) { if (!e.date || e.src !== 'Nasdaq') return false; var d = (new Date(e.date + 'T12:00:00') - today) / 864e5; return d >= -0.5 && d < 7.5; });
      if (soon.length) {
        head('Earnings');
        soon.forEach(function (e) { var d = Math.round((new Date(e.date + 'T12:00:00') - today) / 864e5 - .5); item('earnings.html', e.t, d <= 0 ? 'today' : d === 1 ? 'tomorrow' : dd(e.date), e.when || ''); });
      }
      // newest calls
      if (C.length) {
        var last = C[C.length - 1].date, nw = C.filter(function (c) { return c.date === last; }).slice(-3);
        head('New calls');
        nw.forEach(function (c) { item(c.page, c.name, c.call, '$' + c.value + ' value'); });
      }
      if (it.length < 4) { tape.remove(); return; }
      var row = it.join('<i class="tdot" aria-hidden="true"></i>');
      tape.innerHTML = '<div class="wrap"><span class="tl">' + (when ? 'As of ' + dd(when) : 'Latest') + '</span><div class="tv"><div class="tt">' + row + '<i class="tdot" aria-hidden="true"></i></div></div></div>';
      var tt = tape.querySelector('.tt');
      tt.insertAdjacentHTML('beforeend', '<span class="tcopy" aria-hidden="true">' + tt.innerHTML + '</span>');
      $$('.tcopy a', tape).forEach(function (a) { a.setAttribute('tabindex', '-1'); });
      var w = tt.scrollWidth / 2;
      tt.style.setProperty('--tdur', Math.max(30, w / 38).toFixed(0) + 's');
      tape.classList.add('on');
    });
  })();

  if (page === 'home') {
    getJSON('data/markets.json').then(function (m) {
      M = m; var el = $('#strip');
      if (!m.updated) return waiting(el);
      el.innerHTML = '<div class="tiles">' + ['SP500', 'DGS10', 'DFF', 'CPI_YOY'].map(function (k) { return tile(m.series[k], k); }).join('') + '</div>' +
        '<div class="asof"><span class="mono">' + stamp() + ' &middot; Source: FRED</span><a class="mono" href="markets.html" style="color:var(--acc)">Full dashboard &rarr;</a></div>';
      var s = m.series.SP500; if (s && s.last && $('#tagv')) { $('#tagv').textContent = comma(s.last.v, 2); $('#tagd').textContent = 'S&P 500 · ' + fmt(s).c(s) + ' on ' + fdate(s.last.d); }
    }).catch(function () { waiting($('#strip')); });
  }

  /* ---------- research notes: live figures and charts written into the prose ---------- */
  if (page === 'note') {
    getJSON('data/markets.json').then(function (m) {
      M = m; var S = m.series || {};
      var pct2 = function (v) { return v.toFixed(2) + '%'; };
      $$('[data-v]').forEach(function (e) {
        var s = S[e.getAttribute('data-v')], how = e.getAttribute('data-f') || 'v';
        if (!s || !s.last) return;
        var f = fmt(s), first = (s.y1 && s.y1[0]) || null;
        if (how === 'v') e.textContent = f.t(s.last.v);
        else if (how === 'd') e.textContent = fdate(s.last.d, true);
        else if (how === 'm') e.textContent = fmon(s.last.d);
        else if (how === 'y1' && first) e.textContent = f.t(first[1]);
        else if (how === 'c1' && first) { var x = s.last.v - first[1]; e.textContent = (s.fmt === 'rate' ? sgn(x) + Math.abs(Math.round(x * 100)) + ' bp' : sgn(x) + Math.abs(x).toFixed(1) + ' pp'); }
      });
      $$('[data-tiles]').forEach(function (e) { var ks = e.getAttribute('data-tiles').split(','); e.innerHTML = '<div class="tiles" style="--n:' + ks.length + '">' + ks.map(function (k) { return tile(S[k], k); }).join('') + '</div>'; });
      $$('[data-calc]').forEach(function (e) { var k = e.getAttribute('data-calc'); if (CALC[k]) e.innerHTML = CALC[k](m); });
      function draw() {
        $$('svg[data-chart]').forEach(function (el) {
          var c = JSON.parse(el.getAttribute('data-chart'));
          if (c.curve) { if (m.curve) curve(el, m.curve); return; }
          var sets = c.lines.map(function (l) { var s = S[l[0]]; return s ? { pts: s[c.r || 'y5'] || s.y1 || [], color: css('--' + (l[1] || 'acc')), w: l[2] || 1.6, dash: l[3] || '', area: !!l[4] } : null; }).filter(Boolean);
          line(el, sets, { zero: !!c.zero, yf: function (v) { return v.toFixed(c.dp || 0) + '%'; } });
        });
      }
      redrawers.push(draw); draw();
      $$('[data-legend]').forEach(function (e) {
        e.innerHTML = JSON.parse(e.getAttribute('data-legend')).map(function (l) { var s = S[l[0]]; return s ? '<span><i style="background:var(--' + (l[1] || 'acc') + ')' + (l[3] ? ';height:1px' : '') + '"></i>' + esc(s.name) + '</span>' : ''; }).join('');
      });
      $$('[data-stamp]').forEach(function (e) { e.textContent = stamp() + ' · Source: FRED'; });
      if (m.curve) $$('[data-curvelegend]').forEach(function (e) { e.innerHTML = m.curve.sets.map(function (s, i) { var c = ['var(--acc)', 'var(--t2)', 'var(--t3)'][i]; return '<span><i style="background:' + c + (i ? ';height:1px' : '') + '"></i>' + esc(s.label) + ' &middot; ' + fdate(s.date) + '</span>'; }).join(''); });
    }).catch(function () {});
  }
  /* small calculators used inside notes */
  var CALC = {
    /* how much a par Treasury moves when yields rise or fall one point, at today's yields */
    dur: function (m) {
      if (!m.curve) return '';
      var cur = m.curve.sets[0], ten = { '2Y': 2, '5Y': 5, '10Y': 10, '30Y': 30 };
      function price(c, y, n) { var p = 0, k = n * 2; for (var i = 1; i <= k; i++) p += c / 2 / Math.pow(1 + y / 2, i); return p + 100 / Math.pow(1 + y / 2, k); }
      var rows = Object.keys(ten).map(function (t) {
        var y = cur.v[m.curve.tenors.indexOf(t)] / 100, n = ten[t], c = y * 100;
        var up = price(c, y + .01, n) - 100, dn = price(c, y - .01, n) - 100, dm = (dn - up) / 2 / .01 / 100;
        return '<tr><td>' + n + '-year Treasury</td><td>' + (y * 100).toFixed(2) + '%</td><td>' + dm.toFixed(1) + '</td><td class="dn">' + up.toFixed(1) + '%</td><td class="up">+' + dn.toFixed(1) + '%</td></tr>';
      }).join('');
      return '<div class="scroll"><table class="tbl allr"><thead><tr><th>Bond, priced at par</th><th>Yield today</th><th>Duration</th><th>Yields +1 point</th><th>Yields &minus;1 point</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
    },
    /* how the curve has moved over the past year: steepening or flattening, and whether yields rose or fell */
    shape: function (m) {
      if (!m.curve) return '';
      var c = m.curve, i2 = c.tenors.indexOf('2Y'), i10 = c.tenors.indexOf('10Y'), now = c.sets[0].v, ago = c.sets[2].v;
      if (now[i2] == null || ago[i2] == null) return '';
      var d2 = now[i2] - ago[i2], d10 = now[i10] - ago[i10], bp = function (x) { return (x >= 0 ? '+' : '&minus;') + Math.abs(Math.round(x * 100)) + ' bp'; };
      var up = d2 + d10 > 0, steep = d10 > d2;
      var name = (up ? 'bear ' : 'bull ') + (steep ? 'steepening' : 'flattening');
      var why = up ? (steep ? 'Long yields rose more than short ones: investors want more pay for inflation and for lending long to a government that borrows heavily.' : 'Short yields rose more than long ones: the market moved to price a tighter Fed, while long-run expectations moved less.')
        : (steep ? 'Short yields fell more than long ones: the market expects the Fed to cut.' : 'Long yields fell more than short ones: investors expect slower growth or lower inflation ahead.');
      return '<p>Over the past year the 2-year moved <b>' + bp(d2) + '</b> and the 10-year <b>' + bp(d10) + '</b>, a <b>' + name + '</b>. ' + why + '</p>';
    },
    /* the yield curve's slope and the 2-year against the policy rate */
    path: function (m) {
      var s = m.series, ff = s.DFF && s.DFF.last.v, t2 = s.DGS2 && s.DGS2.last.v, t3m = s.DGS3MO && s.DGS3MO.last.v;
      if (!ff || !t2) return '';
      var gap = t2 - ff;
      return '<p>The 2-year Treasury yields <b>' + t2.toFixed(2) + '%</b> against an effective fed funds rate of <b>' + ff.toFixed(2) + '%</b>, a gap of <b>' + (gap >= 0 ? '+' : '&minus;') + Math.abs(Math.round(gap * 100)) + ' bp</b>. ' +
        (gap > .25 ? 'Investors lending for two years want more than the Fed pays overnight, which usually means they expect <b>higher</b> policy rates ahead.' : gap < -.25 ? 'Investors accept less for two years than the Fed pays overnight, which usually means they expect <b>cuts</b>.' : 'The two are close, which suggests investors expect the policy rate to stay <b>roughly where it is</b>.') +
        (t3m ? ' The 3-month bill, at ' + t3m.toFixed(2) + '%, shows where the market sees rates over the next few months.' : '') + '</p>';
    }
  };

  if (page === 'markets') {
    getJSON('data/markets.json').then(function (m) {
      M = m;
      if (!m.updated) { $$('[data-need]').forEach(function (e) { e.style.display = 'none'; }); return waiting($('#mwait')); }
      $('#mwait').style.display = 'none';
      $('#stamp').textContent = stamp();
      $('#mtiles').innerHTML = ['SP500', 'VIXCLS', 'DGS10', 'DFF'].map(function (k) { return tile(m.series[k], k); }).join('');
      $('#t-rates').innerHTML = table(['DFF', 'DGS3MO', 'DGS2', 'DGS10', 'DGS30', 'T10Y2Y', 'MORTGAGE30US']);
      $('#t-macro').innerHTML = table(['CPI_YOY', 'CORE_PCE_YOY', 'UNRATE', 'GDP_REAL']);
      $('#t-cross').innerHTML = table(['BAMLH0A0HYM2', 'DCOILWTICO', 'DEXUSEU', 'VIXCLS']);
      if (m.curve) $('#lg-curve').innerHTML = m.curve.sets.map(function (s, i) { var c = ['var(--acc)', 'var(--t2)', 'var(--t3)'][i]; return '<span><i style="background:' + c + (i ? ';height:1px' : '') + '"></i>' + esc(s.label) + ' &middot; ' + fdate(s.date) + '</span>'; }).join('');
      function draw() {
        var acc = css('--acc'), t3 = css('--t3');
        if (m.curve) curve($('#c-curve'), m.curve);
        var sp = m.series.SP500; if (sp) line($('#c-spx'), [{ pts: sp.y1, color: acc, area: true }], { yf: function (v) { return comma(v, 0); } });
        var sp2 = m.series.T10Y2Y; if (sp2) line($('#c-spread'), [{ pts: sp2.y5 || sp2.y1, color: acc, area: true }], { zero: true, yf: function (v) { return v.toFixed(1) + '%'; } });
        var ff = m.series.DFF, tn = m.series.DGS10, cp = m.series.CPI_YOY;
        if (ff && tn) line($('#c-policy'), [{ pts: ff.y5 || ff.y1, color: acc, w: 2 }, { pts: tn.y5 || tn.y1, color: t3, w: 1.4 }].concat(cp && cp.y5 ? [{ pts: cp.y5, color: css('--t2'), w: 1.2, dash: '3 4' }] : []), { zero: true, yf: function (v) { return v.toFixed(0) + '%'; } });
      }
      redrawers.push(draw); draw();
    }).catch(function () { waiting($('#mwait')); });
  }

  /* ---------- research report: the report's numbers against today's close ---------- */
  if (page === 'report') {
    var R = { t: document.body.getAttribute('data-ticker'), then: +document.body.getAttribute('data-then'), val: +document.body.getAttribute('data-val') };
    getJSON('data/co/prices.json').then(function (j) {
      var q = j && j.px && j.px[R.t]; if (!q) return;
      var m2 = function (v) { return '$' + v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
      var sg = function (v) { return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v * 100).toFixed(1) + '%'; };
      $('#nPx').textContent = m2(q.p); $('#nPxD').textContent = 'Last close, ' + fdate(q.d, true);
      var c = q.p / R.then - 1, g = q.p / R.val - 1;
      $('#nChg').textContent = sg(c); $('#nChg').className = c >= 0 ? 'up' : 'dn';
      $('#nGap').textContent = sg(g);
      if (q.lo && q.hi) $('#nRg').textContent = '$' + Math.round(q.lo).toLocaleString('en-US') + ' – $' + Math.round(q.hi).toLocaleString('en-US');
      $$('.cnow').forEach(function (ln) { var x = +ln.getAttribute('data-x0') + Math.min(q.p, +(ln.getAttribute('data-max') || 1400)) / +(ln.getAttribute('data-max') || 1400) * +ln.getAttribute('data-span'); ln.setAttribute('d', 'M' + x.toFixed(1) + ' 6V' + ln.getAttribute('data-bot')); ln.style.display = ''; }); if ($('.nowkey')) $('.nowkey').style.display = 'inline';
    }).catch(function () {});
    var toc = $$('.toc a'), chs = $$('.chap');
    if (toc.length && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) toc.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); }); }); }, { rootMargin: '-30% 0px -60% 0px' });
      chs.forEach(function (c) { io.observe(c); });
    }
  }

  if (page === 'research') {
    $$('.chip').forEach(function (c) {
      c.onclick = function () {
        $$('.chip').forEach(function (x) { x.classList.toggle('on', x === c); });
        var f = c.getAttribute('data-f');
        $$('[data-cat]').forEach(function (b) { b.style.display = f === 'all' || b.getAttribute('data-cat') === f ? '' : 'none'; });
      };
    });
    var REPORTS = {'LHX': 'l3harris.html', 'VRT': 'vertiv.html', 'AWK': 'american-water.html', 'AMZN': 'amazon.html', 'META': 'meta.html', 'JPM': 'jpmorgan.html', 'GEV': 'gev.html', 'NVDA': 'nvidia.html', 'BA': 'boeing.html', 'COST': 'costco.html', 'SPCX': 'spacex.html', 'FLY': 'firefly.html', 'ANTHROPIC': 'anthropic.html', 'OPENAI': 'openai.html', 'ANDURIL': 'anduril.html', 'KTOS': 'kratos.html', 'BLOOMBERG': 'bloomberg.html', 'AXON': 'axon.html', 'PLTR': 'palantir.html', 'AMD': 'amd.html', 'MU': 'micron.html', 'SNDK': 'sandisk.html'};
    getJSON('data/companies/index.json').then(function (ix) {
      var el = $('#cov');
      if (!ix.updated || !ix.companies || !ix.companies.length) return el.innerHTML = '<div class="wait"><b>Waiting for the first data update.</b> Company figures come straight from SEC filings and appear here after the update runs for the first time.</div>';
      $('#cstamp').textContent = 'Figures from the latest 10-K on SEC EDGAR · updated ' + fdate(ix.updated.slice(0, 10), true);
      el.innerHTML = ix.companies.filter(function (c) { return !c.private; }).map(function (c) {
        var st = { live: ['live', 'Published'], build: ['build', 'In progress'], plan: ['plan', 'Planned'] }[c.status] || ['plan', 'Planned'];
        var g = c.revGrowth;
        var pg = c.page || REPORTS[c.ticker];
        if (pg) st = ['live', 'Published'];
        return '<div class="co"><div class="nm"><b>' + (pg ? '<a href="' + esc(pg) + '">' + esc(c.name) + ' &rarr;</a>' : esc(c.name)) + '</b><span>' + esc(c.ticker) + ' &middot; ' + esc(c.sector || '') + '</span><div style="margin-top:10px"><span class="st ' + st[0] + '">' + st[1] + '</span></div></div>' +
          '<div class="m"><span class="mono">Revenue FY' + esc(String(c.fy || '').slice(-2)) + '</span><b>' + money(c.revenue) + '</b><small class="' + (g > 0 ? 'up' : g < 0 ? 'dn' : '') + '">' + (g == null ? '&nbsp;' : pct(g) + ' y/y') + '</small></div>' +
          '<div class="m"><span class="mono">Net income</span><b>' + money(c.netIncome) + '</b><small>' + (c.margin == null ? '&nbsp;' : pct(c.margin).replace('+', '') + ' margin') + '</small></div>' +
          '<div class="m hide-md"><span class="mono">Diluted EPS</span><b>' + (c.eps == null ? '—' : '$' + c.eps.toFixed(2)) + '</b><small>&nbsp;</small></div>' +
          '<div class="m"><span class="mono">Free cash flow</span><b>' + money(c.fcf) + '</b><small>' + (c.fcf == null ? 'n/a for financials' : '&nbsp;') + '</small></div>' +
          '<div class="lk">' + (pg ? '<a href="' + esc(pg) + '">Report</a>' : '') + (c.filing ? '<a href="' + esc(c.filing) + '" target="_blank" rel="noopener">10-K &#8599;</a>' : '') + '</div></div>';
      }).join('');
    }).catch(function () { $('#cov').innerHTML = '<div class="wait"><b>Waiting for the first data update.</b> Company figures appear here after the update runs for the first time.</div>'; });
  }
})();

/* report corner mark: swap the ticker for a logo file if one has been uploaded to assets/logos */
(function () {
  var m = document.querySelector('.rmark[data-logo]'); if (!m) return;
  var t = m.getAttribute('data-logo'), ext = ['svg', 'png', 'webp'], i = 0;
  (function next() {
    if (i >= ext.length) return;
    var img = new Image(); img.alt = ''; img.decoding = 'async';
    img.onload = function () {
      /* optical sizing: wide wordmarks get less height, compact marks more, so every logo carries similar weight */
      var r = img.naturalWidth && img.naturalHeight ? img.naturalWidth / img.naturalHeight : 4;
      var h = Math.max(20, Math.min(38, 38 * Math.pow(3 / r, .45)));
      h = Math.min(h, 200 / r);
      m.style.setProperty('--lh', h.toFixed(1) + 'px');
      m.textContent = ''; m.appendChild(img); m.classList.add('has');
    };
    img.onerror = function () { i++; next(); };
    img.src = 'assets/logos/' + t + '.' + ext[i];
  })();
})();
