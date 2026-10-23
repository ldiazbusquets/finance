/* LDB Finance: portfolio risk. Plain JavaScript, no libraries.
   Uses weekly total returns (dividends included) prepared by the nightly data job in data/risk/.
   Everything is historical: it describes how the mix behaved, not how it will. */
(function () {
  'use strict';
  var d = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var css = function (v) { return getComputedStyle(d).getPropertyValue(v).trim(); };
  var base = (document.querySelector('script[src*="risk.js"]') || {}).src || '';
  base = base.slice(0, base.indexOf('assets/'));

  /* ---------- formatting ---------- */
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function fdate(s) { var p = s.split('-'); return MON[+p[1] - 1] + ' ' + (+p[2]) + ', ' + p[0]; }
  function fri(s) { var p = s.split('-'), d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2] + 4)); return MON[d.getUTCMonth()] + ' ' + d.getUTCDate() + ', ' + d.getUTCFullYear(); }   /* weeks are dated by their Monday */
  function cm(v, dp) { return v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function usd(v) { return (v < 0 ? '−' : '') + '$' + cm(Math.abs(Math.round(v)), 0); }
  function pc(v, dp) { var r = +(v * 100).toFixed(dp == null ? 1 : dp); return (r < 0 ? '−' : '') + cm(Math.abs(r), dp == null ? 1 : dp) + '%'; }
  function sgnPc(v, dp) { var r = +(v * 100).toFixed(dp == null ? 1 : dp); return (r > 0 ? '+' : r < 0 ? '−' : '') + cm(Math.abs(r), dp == null ? 1 : dp) + '%'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* ---------- statistics ---------- */
  function mean(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]; return s / a.length; }
  function cov(a, b) { var ma = mean(a), mb = mean(b), s = 0; for (var i = 0; i < a.length; i++) s += (a[i] - ma) * (b[i] - mb); return s / (a.length - 1); }
  function sd(a) { return Math.sqrt(cov(a, a)); }
  function quant(a, q) { var s = a.slice().sort(function (x, y) { return x - y; }), p = (s.length - 1) * q, lo = Math.floor(p), hi = Math.ceil(p); return s[lo] + (s[hi] - s[lo]) * (p - lo); }
  function annRet(r) { var g = 1; r.forEach(function (x) { g *= 1 + x; }); return Math.pow(g, 52 / r.length) - 1; }
  function mvar(w, S) { var v = 0; for (var i = 0; i < w.length; i++) for (var j = 0; j < w.length; j++) v += w[i] * w[j] * S[i][j]; return v; }
  function matvec(S, w) { return S.map(function (row) { var s = 0; for (var j = 0; j < w.length; j++) s += row[j] * w[j]; return s; }); }
  function simplex(v) {                    // Euclidean projection onto {w >= 0, sum w = 1}
    var u = v.slice().sort(function (a, b) { return b - a; }), css2 = 0, rho = 0, th = 0;
    for (var i = 0; i < u.length; i++) { css2 += u[i]; var t = (css2 - 1) / (i + 1); if (u[i] - t > 0) { rho = i; th = t; } }
    return v.map(function (x) { return Math.max(0, x - th); });
  }
  function frontier(mu, S) {               // long-only: minimise risk minus lambda x return, for a range of lambdas
    var n = mu.length, L = 0;
    S.forEach(function (row) { var s = 0; row.forEach(function (x) { s += Math.abs(x); }); L = Math.max(L, s); });
    var step = 1 / (L || 1), w = mu.map(function () { return 1 / n; }), out = [];
    var lams = [0]; for (var k = 0; k < 40; k++) lams.push(0.002 * Math.pow(1.22, k));
    lams.forEach(function (lam) {
      for (var it = 0; it < 1500; it++) {
        var g = matvec(S, w).map(function (x, i) { return x - lam * mu[i]; });
        w = simplex(w.map(function (x, i) { return x - step * g[i]; }));
      }
      var r = 0; w.forEach(function (x, i) { r += x * mu[i]; });
      out.push({ w: w.slice(), r: r, v: Math.sqrt(Math.max(0, mvar(w, S))) });
    });
    return out;
  }

  /* ---------- data ---------- */
  var IDX = null, CACHE = {}, RF = 0.04, RFNOTE = '', TB = null;
  function series(t) {
    if (CACHE[t]) return CACHE[t];
    CACHE[t] = fetch(base + 'data/risk/' + encodeURIComponent(t) + '.json', { cache: 'force-cache' }).then(function (r) { if (!r.ok) throw new Error(t); return r.json(); }).then(function (j) { return j.r; });
    CACHE[t].catch(function () { delete CACHE[t]; });
    return CACHE[t];
  }

  /* ---------- state ---------- */
  var PRESETS = {
    'Balanced': [['VOO', 40000], ['VEA', 15000], ['AVUV', 10000], ['BND', 25000], ['GLD', 10000]],
    '60 / 40': [['VOO', 60000], ['BND', 40000]],
    'All stocks': [['VTI', 70000], ['VXUS', 30000]],
    'Tech-heavy': [['QQQ', 45000], ['SMH', 20000], ['NVDA', 15000], ['MSFT', 10000], ['VOO', 10000]],
    'Dividend': [['SCHD', 40000], ['VYM', 25000], ['JNJ', 10000], ['PG', 10000], ['KO', 15000]]
  };
  var H = PRESETS['Balanced'].map(function (x) { return { t: x[0], amt: x[1] }; }), LOOK = 156, PRE = 'Balanced';

  function table() {
    var el = $('#rkT'); if (!el) return;
    el.innerHTML = '<div class="scroll"><table class="tbl pf"><thead><tr><th>Ticker</th><th>Name</th><th>Amount</th><th>Weight</th><th></th></tr></thead><tbody>' +
      H.map(function (h, i) {
        var tot = H.reduce(function (s, x) { return s + x.amt; }, 0), nm = IDX && IDX.names[h.t];
        return '<tr data-i="' + i + '"><td><input class="cell tk" data-f="t" list="rkList" value="' + esc(h.t) + '" aria-label="Ticker" autocapitalize="characters" spellcheck="false"></td>' +
          '<td class="nmc">' + (nm ? esc(nm) : '<span class="dn">Not found</span>') + '</td>' +
          '<td><input class="cell" data-f="amt" inputmode="decimal" value="' + cm(h.amt, 0) + '" aria-label="Amount, dollars"></td>' +
          '<td class="mono">' + pc(tot ? h.amt / tot : 0) + '</td>' +
          '<td><button type="button" class="x" data-del="' + i + '" aria-label="Remove">×</button></td></tr>';
      }).join('') + '</tbody></table></div>';
    $$('.cell', el).forEach(function (inp) {
      inp.onchange = function () {
        var i = +inp.closest('tr').getAttribute('data-i'), f = inp.getAttribute('data-f');
        if (f === 't') H[i].t = inp.value.trim().toUpperCase().replace(/[^A-Z0-9.\-]/g, '').slice(0, 8);
        else { var v = parseFloat(inp.value.replace(/[^0-9.]/g, '')); if (!isNaN(v)) H[i].amt = Math.max(0, v); }
        PRE = ''; table(); presets(); run();
      };
    });
    $$('button[data-del]', el).forEach(function (x) { x.onclick = function () { H.splice(+x.getAttribute('data-del'), 1); PRE = ''; table(); presets(); run(); }; });
  }
  function presets() {
    var el = $('#rkPre'); if (!el) return;
    el.innerHTML = Object.keys(PRESETS).map(function (k) { return '<button type="button" class="chip' + (k === PRE ? ' on' : '') + '" data-p="' + esc(k) + '">' + k + '</button>'; }).join('');
    $$('.chip', el).forEach(function (c) { c.onclick = function () { PRE = c.getAttribute('data-p'); H = PRESETS[PRE].map(function (x) { return { t: x[0], amt: x[1] }; }); table(); presets(); run(); }; });
    var lk = $('#rkLook');
    if (lk) { lk.innerHTML = '<span class="mono">Look back</span>' + [[52, '1 year'], [156, '3 years'], [260, '5 years']].map(function (x) { return '<button type="button" data-w="' + x[0] + '"' + (LOOK === x[0] ? ' class="on"' : '') + '>' + x[1] + '</button>'; }).join(''); $$('button', lk).forEach(function (b) { b.onclick = function () { LOOK = +b.getAttribute('data-w'); presets(); run(); }; }); }
  }

  /* ---------- the analysis ---------- */
  var token = 0;
  function run() {
    var me = ++token, out = $('#rkOut');
    var hs = H.filter(function (h) { return h.amt > 0 && h.t; });
    var merged = {}; hs.forEach(function (h) { merged[h.t] = (merged[h.t] || 0) + h.amt; });
    var tick = Object.keys(merged);
    if (!IDX) { out.innerHTML = '<div class="wait"><b>Weekly return data is not available yet.</b> It is prepared by the nightly data job; check back after the next update.</div>'; return; }
    var bad = tick.filter(function (t) { return !IDX.names[t]; });
    if (bad.length) { out.innerHTML = '<div class="wait"><b>No data for ' + bad.map(esc).join(', ') + '.</b> The tool covers every S&amp;P 500 company, the companies researched here and about fifty common ETFs. Start typing a ticker to see the list.</div>'; return; }
    if (tick.length < 1) { out.innerHTML = '<div class="wait"><b>Add a holding</b> to see its risk.</div>'; return; }
    if (tick.length > 15) { out.innerHTML = '<div class="wait"><b>Up to 15 different holdings.</b> Combine the smallest ones to stay under the limit.</div>'; return; }
    var need = tick.indexOf('SPY') < 0 ? tick.concat(['SPY']) : tick.slice();
    Promise.all(need.map(series)).then(function (all) {
      if (me !== token) return;
      var by = {}; need.forEach(function (t, i) { by[t] = all[i]; });
      var N = IDX.dates.length, start = N, i0;
      for (i0 = N - 1; i0 >= 1 && N - i0 <= LOOK; i0--) { if (need.some(function (t) { return by[t][i0] == null; })) break; start = i0; }
      var weeks = N - start, short = weeks < LOOK - 1;
      if (weeks < 26) { out.innerHTML = '<div class="wait"><b>Not enough shared history.</b> At least one holding has traded for less than six months, so there is not enough data to measure risk.</div>'; return; }
      var R = tick.map(function (t) { return by[t].slice(start); }), SPY = by.SPY.slice(start), dates = IDX.dates.slice(start);
      var tot = 0; tick.forEach(function (t) { tot += merged[t]; });
      var w = tick.map(function (t) { return merged[t] / tot; });
      var P = []; for (var k = 0; k < weeks; k++) { var s = 0; for (var j = 0; j < tick.length; j++) s += w[j] * R[j][k]; P.push(s); }
      render({ tick: tick, w: w, R: R, P: P, SPY: SPY, dates: dates, tot: tot, short: short, weeks: weeks });
    }).catch(function () { if (me === token) out.innerHTML = '<div class="wait"><b>Some of the data could not be loaded.</b> Check your connection and try again.</div>'; });
  }

  function stats(r, rfw) {
    var ex = r.map(function (x) { return x - rfw; }), dn = ex.map(function (x) { return Math.min(0, x); });
    var dd = Math.sqrt(dn.reduce(function (s, x) { return s + x * x; }, 0) / r.length) * Math.sqrt(52);
    var g = 1, pk = 1, mdd = 0, pkI = 0, tr = 0, trP = 0, curve = [1], dds = [0];
    r.forEach(function (x, i) { g *= 1 + x; curve.push(g); if (g > pk) { pk = g; pkI = i + 1; } var ddn = g / pk - 1; dds.push(ddn); if (ddn < mdd) { mdd = ddn; tr = i + 1; trP = pkI; } });
    var ar = annRet(r), vol = sd(r) * Math.sqrt(52);
    return { ar: ar, vol: vol, sharpe: (ar - RF) / vol, sortino: (ar - RF) / (dd || 1e-9), mdd: mdd, tr: tr, trP: trP, curve: curve, dds: dds };
  }

  function render(o) {
    if (TB) { var vals = TB.filter(function (p) { return p[0] >= o.dates[0]; }).map(function (p) { return p[1]; }); if (vals.length) { RF = mean(vals) / 100; RFNOTE = ', the average 3-month Treasury yield over the same weeks'; } }
    var out = $('#rkOut'), rfw = Math.pow(1 + RF, 1 / 52) - 1;
    var sp = stats(o.P, rfw), sb = stats(o.SPY, rfw);
    var beta = cov(o.P, o.SPY) / cov(o.SPY, o.SPY), te = sd(o.P.map(function (x, i) { return x - o.SPY[i]; })) * Math.sqrt(52);
    var corrSP = cov(o.P, o.SPY) / (sd(o.P) * sd(o.SPY));
    var var95 = -quant(o.P, 0.05), tail = o.P.filter(function (x) { return x <= -var95; }), cvar = -mean(tail);
    var n = o.tick.length, S = [], C = [];
    for (var i = 0; i < n; i++) { S.push([]); C.push([]); for (var j = 0; j < n; j++) { var c = cov(o.R[i], o.R[j]); S[i].push(c * 52); C[i].push(c / (sd(o.R[i]) * sd(o.R[j]))); } }
    var pv = mvar(o.w, S), Sw = matvec(S, o.w), rc = o.w.map(function (x, k) { return x * Sw[k] / pv; });
    var mu = o.R.map(function (r) { return mean(r) * 52; });   /* mean-variance works with average returns */
    var lp = o.dates[o.dates.length - 1].split('-'), le = new Date(Date.UTC(+lp[0], +lp[1] - 1, +lp[2] + 4)), range = fdate(o.dates[0]) + ' to ' + MON[le.getUTCMonth()] + ' ' + le.getUTCDate() + ', ' + le.getUTCFullYear();

    out.innerHTML =
      '<p class="mono rkrange">' + o.weeks + ' weeks, ' + range + (o.short ? ' &middot; shortened: one holding has less history' : '') + '</p>' +
      '<div class="kv four">' +
      '<div><b class="' + (sp.ar >= 0 ? 'up' : 'dn') + '">' + sgnPc(sp.ar) + '</b><span>Return a year (S&amp;P 500 ' + sgnPc(sb.ar) + ')</span></div>' +
      '<div><b>' + pc(sp.vol) + '</b><span>Volatility a year (S&amp;P 500 ' + pc(sb.vol) + ')</span></div>' +
      '<div><b>' + sp.sharpe.toFixed(2) + '</b><span>Sharpe ratio (S&amp;P 500 ' + sb.sharpe.toFixed(2) + ')</span></div>' +
      '<div><b>' + sp.sortino.toFixed(2) + '</b><span>Sortino ratio (S&amp;P 500 ' + sb.sortino.toFixed(2) + ')</span></div>' +
      '<div><b class="dn">' + pc(sp.mdd) + '</b><span>Worst fall from a peak (S&amp;P 500 ' + pc(sb.mdd) + ')</span></div>' +
      '<div><b>' + beta.toFixed(2) + '</b><span>Beta to the S&amp;P 500</span></div>' +
      '<div><b>' + usd(var95 * o.tot) + '</b><span>1-week loss exceeded 1 week in 20 (' + pc(var95) + ')</span></div>' +
      '<div><b>' + usd(cvar * o.tot) + '</b><span>Average loss in those weeks (' + pc(cvar) + ')</span></div></div>' +
      '<p class="fine">Sharpe and Sortino use a risk-free rate of ' + pc(RF, 2) + RFNOTE + '. Tracking error against the S&amp;P 500: ' + pc(te) + ' a year; correlation ' + corrSP.toFixed(2) + '. The 1-in-20 figures are historical value at risk (VaR) and expected shortfall (CVaR) for one week.</p>';

    growth(o, sp, sb);
    contrib(o, rc);
    heat(o, C);
    front(o, mu, S);
    worst(o);
  }

  /* ---------- charts ---------- */
  function svgEl(el, w, h) { el.setAttribute('viewBox', '0 0 ' + w + ' ' + h); el.innerHTML = ''; return el; }
  function nice(lo, hi, n) {
    var span = hi - lo || 1, step = Math.pow(10, Math.floor(Math.log10(span / n))), e = span / n / step;
    step *= e >= 5 ? 10 : e >= 2 ? 5 : e >= 1 ? 2 : 1;
    var out = []; for (var v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
    return out;
  }
  function lines(el, xs, sets, yfmt, opts) {
    var W = el.clientWidth || 640, H = el.clientHeight || 260, L = 58, R = 14, T = 12, Bm = 30;
    svgEl(el, W, H);
    var lo = 1e9, hi = -1e9; sets.forEach(function (s) { s.v.forEach(function (v) { lo = Math.min(lo, v); hi = Math.max(hi, v); }); });
    if (opts && opts.zeroTop) hi = Math.max(hi, 0);
    var pad = (hi - lo) * 0.06 || 1; lo -= pad; hi += opts && opts.zeroTop ? 0 : pad;
    var n = xs.length, X = function (i) { return L + i / (n - 1) * (W - L - R); }, Y = function (v) { return T + (1 - (v - lo) / (hi - lo)) * (H - T - Bm); };
    var s = '', line = css('--line');
    nice(lo, hi, 4).forEach(function (v) { s += '<path d="M' + L + ' ' + Y(v).toFixed(1) + 'H' + (W - R) + '" stroke="' + line + '"/><text x="' + (L - 8) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end">' + yfmt(v) + '</text>'; });
    var ticks = W < 500 ? 3 : 5;
    for (var k = 0; k <= ticks; k++) { var ix = Math.round(k / ticks * (n - 1)), p = xs[ix].split('-'); s += '<text x="' + X(ix).toFixed(1) + '" y="' + (H - 9) + '" text-anchor="' + (k === 0 ? 'start' : k === ticks ? 'end' : 'middle') + '">' + MON[+p[1] - 1] + ' ' + p[0].slice(2) + '</text>'; }
    sets.forEach(function (st) {
      var p = st.v.map(function (v, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1); }).join('');
      if (st.area) s += '<path d="' + p + 'L' + X(n - 1).toFixed(1) + ' ' + Y(Math.max(lo, 0)).toFixed(1) + 'L' + X(0) + ' ' + Y(Math.max(lo, 0)).toFixed(1) + 'Z" fill="' + st.color + '" opacity=".14"/>';
      s += '<path d="' + p + '" fill="none" stroke="' + st.color + '" stroke-width="' + (st.w || 2) + '"' + (st.dash ? ' stroke-dasharray="' + st.dash + '"' : '') + ' stroke-linejoin="round"/>';
    });
    el.innerHTML = s;
  }
  function growth(o, sp, sb) {
    var xs = [o.dates[0]].concat(o.dates);
    lines($('#rkG'), xs, [{ v: sb.curve.map(function (x) { return x * 10000; }), color: css('--t3'), w: 1.5, dash: '4 5' }, { v: sp.curve.map(function (x) { return x * 10000; }), color: css('--acc'), w: 2.2 }], function (v) { return '$' + cm(v / 1000, v < 20000 ? 1 : 0) + 'k'; });
    lines($('#rkD'), xs, [{ v: sb.dds.map(function (x) { return x * 100; }), color: css('--t3'), w: 1.3, dash: '4 5' }, { v: sp.dds.map(function (x) { return x * 100; }), color: css('--dn'), w: 1.8, area: true }], function (v) { return v.toFixed(0) + '%'; }, { zeroTop: true });
    $('#rkGNote').innerHTML = '$10,000 in this mix, rebalanced every week, against the S&amp;P 500 (dashed). It ended at <b>' + usd(sp.curve[sp.curve.length - 1] * 10000) + '</b>; the index at ' + usd(sb.curve[sb.curve.length - 1] * 10000) + '.';
    $('#rkDNote').innerHTML = 'How far below its last high the mix was each week. Its deepest fall bottomed out in the week ending <b>' + fri(o.dates[Math.max(0, sp.tr - 1)]) + '</b>.';
  }
  function contrib(o, rc) {
    var el = $('#rkC'); if (!el) return;
    var rows = o.tick.map(function (t, i) { return { t: t, w: o.w[i], r: rc[i] }; }).sort(function (a, b) { return b.r - a.r; });
    var mx = Math.max.apply(null, rows.map(function (x) { return Math.max(x.w, x.r); }));
    el.innerHTML = '<div class="rcl"><span></span><span class="mono">Share of money</span><span class="mono">Share of risk</span></div>' + rows.map(function (x) {
      return '<div class="rcr"><b>' + esc(x.t) + '</b><div><i class="wb" style="width:' + (x.w / mx * 100).toFixed(1) + '%"></i><em>' + pc(x.w, 0) + '</em></div><div><i class="rb" style="width:' + (Math.max(0, x.r) / mx * 100).toFixed(1) + '%"></i><em>' + pc(x.r, 0) + '</em></div></div>';
    }).join('');
    var top = rows[0];
    $('#rkCNote').innerHTML = top.r > top.w * 1.25 ? '<b>' + esc(top.t) + '</b> is ' + pc(top.w, 0) + ' of the money but ' + pc(top.r, 0) + ' of the risk: it moves more, and moves with everything else.' :
      'Risk is spread roughly in line with the money. A holding that takes more risk than money moves more, or moves with the rest.';
  }
  function heat(o, C) {
    var el = $('#rkH'); if (!el) return;
    var n = o.tick.length, acc = css('--acc'), s = '<div class="hm" style="grid-template-columns:56px repeat(' + n + ',minmax(0,1fr))"><span></span>' + o.tick.map(function (t) { return '<span class="hx">' + esc(t) + '</span>'; }).join('');
    for (var i = 0; i < n; i++) {
      s += '<span class="hy">' + esc(o.tick[i]) + '</span>';
      for (var j = 0; j < n; j++) { var c = C[i][j], a = Math.abs(c); s += '<span class="hc" style="background:' + (c >= 0 ? 'color-mix(in srgb, ' + acc + ' ' + Math.round(a * 60) + '%, transparent)' : 'color-mix(in srgb, var(--up) ' + Math.round(a * 60) + '%, transparent)') + '" title="' + esc(o.tick[i]) + ' and ' + esc(o.tick[j]) + ': ' + c.toFixed(2) + '">' + (n <= 8 ? c.toFixed(2) : '') + '</span>'; }
    }
    el.innerHTML = s + '</div>';
  }
  function front(o, mu, S) {
    var el = $('#rkF'); if (!el) return;
    var n = mu.length;
    if (n < 2) { el.innerHTML = ''; $('#rkFT').innerHTML = '<p class="fine">Add a second holding to see the frontier.</p>'; return; }
    var fr = frontier(mu, S), mv = fr[0], ms = fr.reduce(function (b, p) { return (p.r - RF) / p.v > (b.r - RF) / b.v ? p : b; }, fr[0]);
    var cur = { r: o.w.reduce(function (s, w, i) { return s + w * mu[i]; }, 0), v: Math.sqrt(mvar(o.w, S)) };
    var pts = o.tick.map(function (t, i) { return { t: t, r: mu[i], v: Math.sqrt(S[i][i]) }; });
    var W = el.clientWidth || 640, H = el.clientHeight || 300, L = 52, R = 18, T = 14, Bm = 34;
    svgEl(el, W, H);
    var all = pts.concat(fr, [cur]), x0 = 0, x1 = Math.max.apply(null, all.map(function (p) { return p.v; })) * 1.08;
    var y0 = Math.min(0, Math.min.apply(null, all.map(function (p) { return p.r; }))), y1 = Math.max.apply(null, all.map(function (p) { return p.r; }));
    var py = (y1 - y0) * 0.1; y0 -= py; y1 += py;
    var X = function (v) { return L + (v - x0) / (x1 - x0) * (W - L - R); }, Y = function (v) { return T + (1 - (v - y0) / (y1 - y0)) * (H - T - Bm); };
    var s = '', line = css('--line'), acc = css('--acc'), t3 = css('--t3'), ink = css('--ink');
    nice(y0, y1, 4).forEach(function (v) { s += '<path d="M' + L + ' ' + Y(v).toFixed(1) + 'H' + (W - R) + '" stroke="' + line + '"/><text x="' + (L - 8) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end">' + (v * 100).toFixed(0) + '%</text>'; });
    nice(x0, x1, W < 500 ? 3 : 5).forEach(function (v) { s += '<text x="' + X(v).toFixed(1) + '" y="' + (H - 10) + '" text-anchor="middle">' + (v * 100).toFixed(0) + '%</text>'; });
    s += '<text x="' + (W - R) + '" y="' + (H - 22) + '" text-anchor="end">Volatility →</text><text x="' + (L + 6) + '" y="' + (T + 10) + '">Average return a year</text>';
    var fp = fr.slice().sort(function (a, b) { return a.v - b.v; }).map(function (p, i) { return (i ? 'L' : 'M') + X(p.v).toFixed(1) + ' ' + Y(p.r).toFixed(1); }).join('');
    s += '<path d="' + fp + '" fill="none" stroke="' + acc + '" stroke-width="2.2" stroke-linejoin="round"/>';
    pts.forEach(function (p) { s += '<circle cx="' + X(p.v).toFixed(1) + '" cy="' + Y(p.r).toFixed(1) + '" r="4" fill="none" stroke="' + t3 + '" stroke-width="1.5"/><text x="' + (X(p.v) + 7).toFixed(1) + '" y="' + (Y(p.r) + 4).toFixed(1) + '">' + esc(p.t) + '</text>'; });
    var dot = function (p, col, lab, dy) { return '<circle cx="' + X(p.v).toFixed(1) + '" cy="' + Y(p.r).toFixed(1) + '" r="6" fill="' + col + '" stroke="' + css('--s1') + '" stroke-width="2.5"/><text x="' + (X(p.v) - 9).toFixed(1) + '" y="' + (Y(p.r) + (dy || 4)).toFixed(1) + '" text-anchor="end" class="lb">' + lab + '</text>'; };
    s += dot(mv, t3, 'Least risk', 4) + dot(ms, acc, 'Best Sharpe', -8) + dot(cur, ink, 'Yours', 16);
    el.innerHTML = s;
    $('#rkFT').innerHTML = '<div class="scroll"><table class="tbl"><thead><tr><th>Holding</th><th>Yours</th><th>Least risk</th><th>Best Sharpe</th></tr></thead><tbody>' +
      o.tick.map(function (t, i) { return '<tr><td>' + esc(t) + '</td><td>' + pc(o.w[i], 0) + '</td><td>' + pc(mv.w[i], 0) + '</td><td>' + pc(ms.w[i], 0) + '</td></tr>'; }).join('') +
      '<tr class="hl"><td>Average return / volatility</td><td>' + pc(cur.r) + ' / ' + pc(cur.v) + '</td><td>' + pc(mv.r) + ' / ' + pc(mv.v) + '</td><td>' + pc(ms.r) + ' / ' + pc(ms.v) + '</td></tr></tbody></table></div>' +
      '<p class="fine">The frontier is the best return the same holdings offered for each level of risk over this period, with no borrowing or short selling. It is fitted to the past: returns that high rarely repeat, and small changes in the dates can swing the &ldquo;best&rdquo; weights a lot. Treat it as a description of what happened, not a recommended mix.</p>';
  }
  function worst(o) {
    var el = $('#rkW'); if (!el) return;
    var idx = o.P.map(function (x, i) { return i; }).sort(function (a, b) { return o.P[a] - o.P[b]; }).slice(0, 6);
    el.innerHTML = '<table class="tbl"><thead><tr><th>Week ending</th><th>Your mix</th><th>S&amp;P 500</th><th class="hide-sm">In dollars</th></tr></thead><tbody>' + idx.map(function (i) {
      var p = o.dates[i].split('-'), dt = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2] + 4)), lab = MON[dt.getUTCMonth()] + ' ' + dt.getUTCDate() + ', ' + dt.getUTCFullYear();
      return '<tr><td>' + lab + '</td><td class="dn">' + sgnPc(o.P[i]) + '</td><td>' + sgnPc(o.SPY[i]) + '</td><td class="hide-sm">' + usd(o.P[i] * o.tot) + '</td></tr>';
    }).join('') + '</tbody></table>';
  }

  /* ---------- start ---------- */
  function start() {
    if (IDX) {
      var dl = document.createElement('datalist'); dl.id = 'rkList';
      dl.innerHTML = Object.keys(IDX.names).map(function (t) { return '<option value="' + esc(t) + '">' + esc(IDX.names[t]) + '</option>'; }).join('');
      document.body.appendChild(dl);
      var st = $('#rkStamp'); if (st) st.textContent = 'Weekly returns through ' + fdate(IDX.dates[IDX.dates.length - 1]) + ' · ' + Object.keys(IDX.names).length + ' tickers';
    }
    table(); presets(); run();
    var add = $('#rkAdd'); if (add) add.onclick = function () { H.push({ t: 'VOO', amt: 10000 }); PRE = ''; table(); presets(); run(); };
    var t; addEventListener('resize', function () { clearTimeout(t); t = setTimeout(run, 200); });
    new MutationObserver(function () { run(); }).observe(d, { attributes: true, attributeFilter: ['class'] });
  }
  window.LDBRISK = { simplex: simplex, frontier: frontier, quant: quant, annRet: annRet };
  Promise.all([
    fetch(base + 'data/risk/index.json?t=' + Math.floor(Date.now() / 3600000)).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }),
    (window.LDBget ? window.LDBget('data/markets.json').catch(function () { return null; }) : fetch(base + 'data/markets.json').then(function (r) { return r.ok ? r.json() : null; })).catch(function () { return null; })
  ]).then(function (x) {
    IDX = x[0];
    var m = x[1], tb = m && m.series && m.series.DGS3MO;
    if (tb && tb.y5 && tb.y5.length) TB = tb.y5;
    start();
  });
})();
