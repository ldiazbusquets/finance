/* LDB Finance: fixed-income portfolio analyser. Plain JavaScript, no libraries.
   Every bond is priced off today's Treasury curve plus its own spread, so a curve that bends (not just shifts)
   moves each cash flow by the change at its own date. Settlement is on a coupon date (no accrued interest). */
(function () {
  'use strict';
  var d = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var css = function (v) { return getComputedStyle(d).getPropertyValue(v).trim(); };

  /* ---------- formatting ---------- */
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function fdate(s) { var p = s.split('-'); return MON[+p[1] - 1] + ' ' + (+p[2]) + ', ' + p[0]; }
  function cm(v, dp) { return v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function usd(v, dp) { return (v < 0 ? '−' : '') + '$' + cm(Math.abs(v), dp == null ? 0 : dp); }
  function sgnUsd(v) { var r = Math.round(v); return (r > 0 ? '+' : r < 0 ? '−' : '') + '$' + cm(Math.abs(r), 0); }
  function pc(v, dp) { return cm(v * 100, dp == null ? 2 : dp) + '%'; }
  function sgnPc(v, dp) { var r = +(v * 100).toFixed(dp == null ? 2 : dp); return (r > 0 ? '+' : r < 0 ? '−' : '') + cm(Math.abs(r), dp == null ? 2 : dp) + '%'; }
  function bp(v) { var r = Math.round(v); return (r > 0 ? '+' : r < 0 ? '−' : '') + Math.abs(r) + ' bp'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function yrs(T) { return (T % 1 ? T.toFixed(1) : T) + ' yr'; }

  /* ---------- today's market: Treasury curve and credit spreads from the nightly data file ---------- */
  var TEN = { '1M': 1 / 12, '3M': .25, '6M': .5, '1Y': 1, '2Y': 2, '3Y': 3, '5Y': 5, '7Y': 7, '10Y': 10, '20Y': 20, '30Y': 30 };
  var CURVE = [[1 / 12, .041], [.25, .042], [1, .044], [2, .046], [5, .048], [10, .05], [30, .053]], CDATE = '';
  var SPR = { tsy: 0, ig: .0090, hy: .0330 }, SDATE = '';
  var TYPES = { tsy: 'Treasury', ig: 'Investment-grade corporate', hy: 'High-yield corporate' };
  function zAt(T) {                          // the Treasury curve, straight lines between published maturities
    var c = CURVE;
    if (T <= c[0][0]) return c[0][1];
    for (var i = 1; i < c.length; i++) if (T <= c[i][0]) { var a = c[i - 1], z = c[i]; return a[1] + (z[1] - a[1]) * (T - a[0]) / (z[0] - a[0]); }
    return c[c.length - 1][1];
  }

  /* ---------- the curve move: level, slope and curvature, set at four key maturities ---------- */
  var KEYS = [2, 5, 10, 30];
  var SC = { L: 100, S: 0, C: 0, ig: 0, hy: 0 };
  function keyMoves(s) {                     // bp at 2, 5, 10 and 30 years
    return KEYS.map(function (k) { var slope = s.S * ((k - 2) / 28 - 0.5), belly = (k === 5 || k === 10) ? s.C : 0; return s.L + slope + belly; });
  }
  function moveAt(T, km) {                   // decimal yield change at maturity T: straight lines between key points, flat outside
    if (T <= KEYS[0]) return km[0] / 1e4;
    for (var i = 1; i < KEYS.length; i++) if (T <= KEYS[i]) return (km[i - 1] + (km[i] - km[i - 1]) * (T - KEYS[i - 1]) / (KEYS[i] - KEYS[i - 1])) / 1e4;
    return km[KEYS.length - 1] / 1e4;
  }
  var PRESETS = [
    { n: 'Up 1 point', L: 100, S: 0, C: 0, ig: 0, hy: 0 },
    { n: 'Down 1 point', L: -100, S: 0, C: 0, ig: 0, hy: 0 },
    { n: 'Bear steepener', L: 75, S: 100, C: 0, ig: 0, hy: 0 },
    { n: 'Bull flattener', L: -60, S: -75, C: 0, ig: 0, hy: 0 },
    { n: 'Inversion', L: 60, S: -175, C: 0, ig: 0, hy: 0 },
    { n: 'Belly sell-off', L: 0, S: 0, C: 60, ig: 0, hy: 0 },
    { n: '2022-style hikes', L: 290, S: -165, C: -80, ig: 30, hy: 170, note: 'Close to 2022: the 2-year rose about 3.7 points and the 30-year about 2.1; spreads widened.' },
    { n: 'Flight to quality', L: -100, S: 0, C: 0, ig: 150, hy: 500, note: 'Stylised crisis: Treasuries rally while corporate spreads blow out.' },
    { n: 'Credit scare', L: 0, S: 0, C: 0, ig: 100, hy: 350 }];

  /* ---------- bond math ---------- */
  function flows(b) {                        // semiannual coupons, face per $100
    var n = Math.max(1, Math.round(b.T * 2)), cf = [];
    for (var k = 1; k <= n; k++) cf.push({ t: k / 2, a: 100 * b.c / 2 + (k === n ? 100 : 0) });
    return cf;
  }
  function priceY(b, y) { var p = 0; flows(b).forEach(function (x) { p += x.a / Math.pow(1 + y / 2, x.t * 2); }); return p; }
  function priceZ(b, s, km, ds) {            // each cash flow at the curve on its own date, plus the bond's spread
    var p = 0;
    flows(b).forEach(function (x) { var r = zAt(x.t) + (km ? moveAt(x.t, km) : 0) + s + (ds || 0); p += x.a / Math.pow(1 + r / 2, x.t * 2); });
    return p;
  }
  function spreadFor(b) {                     // the spread over the curve that reproduces the bond's price at its own yield
    var P = priceY(b, b.y), lo = -0.05, hi = 0.5;
    for (var i = 0; i < 120; i++) { var m = (lo + hi) / 2; if (priceZ(b, m) > P) lo = m; else hi = m; }
    return (lo + hi) / 2;
  }
  function analyse(b) {
    var P = priceY(b, b.y), s = spreadFor(b), h = 0.0025, up = priceZ(b, s, [25, 25, 25, 25]), dn = priceZ(b, s, [-25, -25, -25, -25]);
    var D = (dn - up) / (2 * P * h), C = (dn + up - 2 * P) / (P * h * h);
    var krd = KEYS.map(function (_, i) { var km = [0, 0, 0, 0]; km[i] = 1; return (P - priceZ(b, s, km)) / (P * 1e-4); });
    return { P: P, s: s, D: D, C: C, krd: krd, mv: P / 100 * b.amt };
  }

  /* ---------- portfolio ---------- */
  var PF = [], GOAL = { on: true, amt: 150000, T: 8 };
  function starter() {
    var t = function (T) { return Math.round(zAt(T) * 8e3) / 8e3; };
    return [
      { name: '2-year Treasury', type: 'tsy', amt: 20000, c: t(2), T: 2, y: zAt(2) },
      { name: '5-year Treasury', type: 'tsy', amt: 20000, c: t(5), T: 5, y: zAt(5) },
      { name: '10-year Treasury', type: 'tsy', amt: 20000, c: t(10), T: 10, y: zAt(10) },
      { name: 'Corporate, A-rated', type: 'ig', amt: 20000, c: t(7) + .0075, T: 7, y: zAt(7) + SPR.ig },
      { name: 'High-yield corporate', type: 'hy', amt: 10000, c: t(5) + .03, T: 5, y: zAt(5) + SPR.hy },
      { name: '30-year Treasury', type: 'tsy', amt: 10000, c: t(30), T: 30, y: zAt(30) }];
  }
  function fresh(type, T) { var y = zAt(T) + SPR[type]; return { name: TYPES[type].replace('corporate', 'bond'), type: type, amt: 10000, c: Math.round(y * 8e3) / 8e3, T: T, y: y }; }

  function table() {
    var el = $('#fiT'); if (!el) return;
    el.innerHTML = '<div class="scroll"><table class="tbl pf"><thead><tr><th>Bond</th><th>Type</th><th>Face amount</th><th>Coupon</th><th>Years</th><th>Yield</th><th></th></tr></thead><tbody>' +
      PF.map(function (b, i) {
        return '<tr data-i="' + i + '"><td><input class="cell nm" data-f="name" value="' + esc(b.name) + '" aria-label="Bond name"></td>' +
          '<td><select class="cell sel" data-f="type" aria-label="Type">' + Object.keys(TYPES).map(function (k) { return '<option value="' + k + '"' + (b.type === k ? ' selected' : '') + '>' + (k === 'tsy' ? 'Treasury' : k === 'ig' ? 'Inv. grade' : 'High yield') + '</option>'; }).join('') + '</select></td>' +
          '<td><input class="cell" data-f="amt" inputmode="decimal" value="' + cm(b.amt, 0) + '" aria-label="Face amount"></td>' +
          '<td><input class="cell" data-f="c" inputmode="decimal" value="' + (b.c * 100).toFixed(3) + '" aria-label="Coupon, percent"><i>%</i></td>' +
          '<td><input class="cell" data-f="T" inputmode="decimal" value="' + b.T + '" aria-label="Years to maturity"></td>' +
          '<td><input class="cell" data-f="y" inputmode="decimal" value="' + (b.y * 100).toFixed(3) + '" aria-label="Yield, percent"><i>%</i></td>' +
          '<td><button type="button" class="x" data-del="' + i + '" aria-label="Remove">×</button></td></tr>';
      }).join('') + '</tbody></table></div>';
    $$('.cell', el).forEach(function (inp) {
      inp.onchange = function () {
        var i = +inp.closest('tr').getAttribute('data-i'), f = inp.getAttribute('data-f'), b = PF[i];
        if (f === 'name') { b.name = inp.value.slice(0, 40) || 'Bond'; run(); return; }
        if (f === 'type') { var old = SPR[b.type]; b.type = inp.value; b.y = Math.max(-0.01, b.y - old + SPR[b.type]); table(); run(); return; }
        var v = parseFloat(inp.value.replace(/[^0-9.\-]/g, ''));
        if (!isNaN(v)) {
          if (f === 'c' || f === 'y') v /= 100;
          if (f === 'amt') v = Math.max(0, v);
          if (f === 'T') v = Math.min(30, Math.max(0.5, Math.round(v * 2) / 2));
          if (f === 'c') v = Math.max(0, Math.min(0.3, v));
          if (f === 'y') v = Math.max(-0.01, Math.min(0.4, v));
          b[f] = v;
        }
        table(); run();
      };
    });
    $$('button[data-del]', el).forEach(function (x) { x.onclick = function () { PF.splice(+x.getAttribute('data-del'), 1); table(); run(); }; });
  }

  /* ---------- scenario controls ---------- */
  function controls() {
    var el = $('#fiS'); if (!el) return;
    var sl = function (k, label, hint, lo, hi) { return '<div class="sl"><label><span>' + label + ' <small>' + hint + '</small></span><b id="v' + k + '"></b></label><input type="range" data-k="' + k + '" min="' + lo + '" max="' + hi + '" step="5" value="' + SC[k] + '" aria-label="' + label + ', basis points"></div>'; };
    el.innerHTML = '<div class="chips sm" id="fiPre">' + PRESETS.map(function (p, i) { return '<button type="button" class="chip" data-p="' + i + '">' + p.n + '</button>'; }).join('') + '</div>' +
      sl('L', 'Level', 'every maturity', -300, 500) + sl('S', 'Slope', '30-year minus 2-year', -300, 300) + sl('C', 'Curvature', '5 and 10 years only', -150, 150) +
      sl('ig', 'Investment-grade spreads', 'over Treasuries', -100, 400) + sl('hy', 'High-yield spreads', 'over Treasuries', -300, 1200) +
      '<p class="fine" id="fiPreNote"></p>';
    $$('input[type=range]', el).forEach(function (r) { r.oninput = function () { SC[r.getAttribute('data-k')] = +r.value; run(); }; });
    $$('#fiPre .chip').forEach(function (c) {
      c.onclick = function () { var p = PRESETS[+c.getAttribute('data-p')]; ['L', 'S', 'C', 'ig', 'hy'].forEach(function (k) { SC[k] = p[k]; var r = $('input[data-k="' + k + '"]', el); if (r) r.value = p[k]; }); run(); };
    });
  }

  function goalControls() {
    var el = $('#fiG'); if (!el) return;
    el.innerHTML = '<div class="seg sm" style="margin-top:0"><span class="mono">Fund a goal</span><button type="button" data-g="1"' + (GOAL.on ? ' class="on"' : '') + '>On</button><button type="button" data-g="0"' + (GOAL.on ? '' : ' class="on"') + '>Off</button></div>' +
      (GOAL.on ? '<div class="ins two" style="margin-top:18px"><label class="in"><span>Amount needed<small>In today&rsquo;s dollars, paid once</small></span><div class="box nb"><input id="gA" inputmode="decimal" value="' + cm(GOAL.amt, 0) + '"><i>$</i></div></label>' +
        '<label class="in"><span>Years from now<small>A home, tuition, a payout</small></span><div class="box nb"><input id="gT" inputmode="decimal" value="' + GOAL.T + '"><i>yr</i></div></label></div>' : '');
    $$('button[data-g]', el).forEach(function (b) { b.onclick = function () { GOAL.on = b.getAttribute('data-g') === '1'; goalControls(); run(); }; });
    var a = $('#gA'), t = $('#gT');
    if (a) a.onchange = function () { var v = parseFloat(a.value.replace(/[^0-9.]/g, '')); if (!isNaN(v) && v > 0) GOAL.amt = v; a.value = cm(GOAL.amt, 0); run(); };
    if (t) t.onchange = function () { var v = parseFloat(t.value.replace(/[^0-9.]/g, '')); if (!isNaN(v)) GOAL.T = Math.min(30, Math.max(0.5, Math.round(v * 2) / 2)); t.value = GOAL.T; run(); };
  }

  /* ---------- the whole analysis ---------- */
  function run() {
    var out = $('#fiSum'); if (!out) return;
    var km = keyMoves(SC);
    ['L', 'S', 'C', 'ig', 'hy'].forEach(function (k) { var e = $('#v' + k); if (e) e.textContent = bp(SC[k]); });
    $$('#fiPre .chip').forEach(function (c) { var p = PRESETS[+c.getAttribute('data-p')]; c.classList.toggle('on', ['L', 'S', 'C', 'ig', 'hy'].every(function (k) { return p[k] === SC[k]; })); });
    var hit = PRESETS.filter(function (p) { return ['L', 'S', 'C', 'ig', 'hy'].every(function (k) { return p[k] === SC[k]; }); })[0];
    $('#fiPreNote').innerHTML = 'Curve move: ' + KEYS.map(function (k, i) { return '<b>' + k + '-yr ' + bp(km[i]) + '</b>'; }).join(' &middot; ') + (hit && hit.note ? '. ' + hit.note : '.');
    if (!PF.length) { out.innerHTML = '<div class="wait"><b>No bonds yet.</b> Add one, or load the starter portfolio.</div>'; ['#fiCurve', '#fiKrd', '#fiCf'].forEach(function (s) { var e = $(s); if (e) e.innerHTML = ''; }); $('#fiRes').innerHTML = ''; $('#fiGoal').innerHTML = ''; return; }
    var A = PF.map(function (b) { return analyse(b); }), MV = 0, yld = 0, D = 0, C = 0, mat = 0, sd = 0, K = [0, 0, 0, 0], mix = { tsy: 0, ig: 0, hy: 0 };
    A.forEach(function (a, i) {
      var b = PF[i]; MV += a.mv; yld += b.y * a.mv; D += a.D * a.mv; C += a.C * a.mv; mat += b.T * a.mv; mix[b.type] += a.mv;
      if (b.type !== 'tsy') sd += a.D * a.mv;
      a.krd.forEach(function (k, j) { K[j] += k * a.mv * 1e-4; });
    });
    yld /= MV; D /= MV; C /= MV; mat /= MV;
    out.innerHTML = '<div class="kv four">' +
      '<div><b>' + usd(MV) + '</b><span>Market value</span></div>' +
      '<div><b>' + pc(yld) + '</b><span>Yield, value-weighted</span></div>' +
      '<div><b>' + D.toFixed(2) + '</b><span>Effective duration</span></div>' +
      '<div><b>' + usd(D * MV * 1e-4) + '</b><span>DV01: one basis point</span></div>' +
      '<div><b>' + C.toFixed(1) + '</b><span>Convexity</span></div>' +
      '<div><b>' + (sd / MV).toFixed(2) + '</b><span>Spread duration</span></div>' +
      '<div><b>' + mat.toFixed(1) + '<small> yr</small></b><span>Average maturity</span></div>' +
      '<div><b>' + pc((mix.ig + mix.hy) / MV, 0) + '</b><span>In corporate bonds</span></div></div>';

    /* the scenario, bond by bond, split into the curve and the spread */
    var V1 = 0, Vr = 0, rows = '';
    A.forEach(function (a, i) {
      var b = PF[i], ds = (b.type === 'ig' ? SC.ig : b.type === 'hy' ? SC.hy : 0) / 1e4;
      var pr = priceZ(b, a.s, km) / 100 * b.amt, pf = priceZ(b, a.s, km, ds) / 100 * b.amt;
      V1 += pf; Vr += pr;
      rows += '<tr><td>' + esc(b.name) + '<small>' + TYPES[b.type] + ' &middot; ' + (b.c * 100).toFixed(2) + '% &middot; ' + yrs(b.T) + '</small></td><td>' + usd(a.mv) + '</td><td class="hide-sm">' + bp(moveAt(b.T, km) * 1e4) + '</td>' +
        '<td class="hide-sm">' + sgnUsd(pr - a.mv) + '</td><td class="hide-sm">' + (ds ? sgnUsd(pf - pr) : '&ndash;') + '</td><td class="' + (pf - a.mv >= 0 ? 'up' : 'dn') + '">' + sgnUsd(pf - a.mv) + '</td><td>' + sgnPc(pf / a.mv - 1) + '</td></tr>';
    });
    var ch = V1 - MV, rate = Vr - MV, cred = V1 - Vr, carry = yld * MV;
    $('#fiRes').innerHTML = '<div class="kv four">' +
      '<div><b class="' + (ch >= 0 ? 'up' : 'dn') + '">' + sgnUsd(ch) + '</b><span>Change in value, ' + sgnPc(ch / MV) + '</span></div>' +
      '<div><b>' + sgnUsd(rate) + '</b><span>From the Treasury curve</span></div>' +
      '<div><b>' + sgnUsd(cred) + '</b><span>From credit spreads</span></div>' +
      '<div><b>' + (ch < 0 && carry > 0 ? (-ch / carry).toFixed(1) + '<small> yr</small>' : '&ndash;') + '</b><span>' + (ch < 0 ? 'Years of income to earn it back' : 'No loss to earn back') + '</span></div></div>' +
      '<div class="scroll" style="margin-top:22px"><table class="tbl"><thead><tr><th>Bond</th><th>Value</th><th class="hide-sm">Curve move</th><th class="hide-sm">Curve effect</th><th class="hide-sm">Spread effect</th><th>Change</th><th>%</th></tr></thead><tbody>' + rows +
      '<tr class="hl"><td>Portfolio</td><td>' + usd(MV) + '</td><td class="hide-sm"></td><td class="hide-sm">' + sgnUsd(rate) + '</td><td class="hide-sm">' + sgnUsd(cred) + '</td><td>' + sgnUsd(ch) + '</td><td>' + sgnPc(ch / MV) + '</td></tr></tbody></table></div>' +
      '<p class="fine">Each bond is repriced cash flow by cash flow: every payment is discounted at the Treasury curve on its own date plus the bond&rsquo;s spread, so a twist or a bend hits short and long payments differently. Spread moves apply to corporate bonds only. &ldquo;Years of income&rdquo; divides the loss by a year of interest at today&rsquo;s yield.</p>';

    drawCurve(km);
    drawKrd(K, MV);
    drawCf();
    goal(A, MV, D, km, ch);
    drawMix(mix, MV);
  }

  /* ---------- charts ---------- */
  function svgEl(el, w, h) { el.setAttribute('viewBox', '0 0 ' + w + ' ' + h); el.innerHTML = ''; return el; }
  function nice(lo, hi, n) {
    var span = hi - lo || 1, step = Math.pow(10, Math.floor(Math.log10(span / n))), e = span / n / step;
    step *= e >= 5 ? 10 : e >= 2 ? 5 : e >= 1 ? 2 : 1;
    var out = []; for (var v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
    return out;
  }
  function drawCurve(km) {
    var el = $('#fiCurve'); if (!el) return;
    var W = el.clientWidth || 640, H = el.clientHeight || 260, L = 50, R = 16, T = 14, Bm = 34;
    svgEl(el, W, H);
    var a = [], b = [], lo = 1e9, hi = -1e9;
    for (var t = 0.25; t <= 30.001; t += 0.25) { var z0 = zAt(t) * 100, z1 = (zAt(t) + moveAt(t, km)) * 100; a.push([t, z0]); b.push([t, z1]); lo = Math.min(lo, z0, z1); hi = Math.max(hi, z0, z1); }
    var pad = Math.max(0.15, (hi - lo) * 0.12); lo -= pad; hi += pad;
    var X = function (v) { return L + v / 30 * (W - L - R); }, Y = function (v) { return T + (1 - (v - lo) / (hi - lo)) * (H - T - Bm); };
    var s = '', line = css('--line');
    nice(lo, hi, 4).forEach(function (v) { s += '<path d="M' + L + ' ' + Y(v).toFixed(1) + 'H' + (W - R) + '" stroke="' + line + '"/><text x="' + (L - 10) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end">' + v.toFixed(1) + '%</text>'; });
    [0, 2, 5, 10, 20, 30].forEach(function (v) { s += '<text x="' + X(v).toFixed(1) + '" y="' + (H - 10) + '" text-anchor="middle">' + (v ? v + 'y' : '') + '</text>'; });
    var path = function (p) { return p.map(function (q, i) { return (i ? 'L' : 'M') + X(q[0]).toFixed(1) + ' ' + Y(q[1]).toFixed(1); }).join(''); };
    s += '<path d="' + path(a) + '" fill="none" stroke="' + css('--t3') + '" stroke-width="1.6" stroke-dasharray="4 5"/>';
    s += '<path d="' + path(b) + '" fill="none" stroke="' + css('--acc') + '" stroke-width="2.2" stroke-linejoin="round"/>';
    KEYS.forEach(function (k, i) { s += '<circle cx="' + X(k).toFixed(1) + '" cy="' + Y((zAt(k) + km[i] / 1e4) * 100).toFixed(1) + '" r="4" fill="' + css('--acc') + '" stroke="' + css('--s1') + '" stroke-width="2"/>'; });
    el.innerHTML = s;
  }
  function bars(el, items, fmt, opts) {        // items: [{label, v, v2?}] ; stacked when v2 given
    var W = el.clientWidth || 640, H = el.clientHeight || 220, L = 54, R = 10, T = 14, Bm = 30;
    svgEl(el, W, H);
    var vals = items.map(function (x) { return x.v + (x.v2 || 0); }), lo = Math.min(0, Math.min.apply(null, vals)), hi = Math.max(0, Math.max.apply(null, vals));
    if (hi === lo) hi = lo + 1;
    var pad = (hi - lo) * 0.08; hi += pad; if (lo < 0) lo -= pad;
    var Y = function (v) { return T + (1 - (v - lo) / (hi - lo)) * (H - T - Bm); }, n = items.length, slot = (W - L - R) / n, bw = Math.min(54, slot * 0.62);
    var s = '', line = css('--line');
    nice(lo, hi, 4).forEach(function (v) { s += '<path d="M' + L + ' ' + Y(v).toFixed(1) + 'H' + (W - R) + '" stroke="' + line + '"/><text x="' + (L - 8) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end">' + fmt(v) + '</text>'; });
    items.forEach(function (x, i) {
      var cx = L + slot * (i + 0.5), y0 = Y(0), y1 = Y(x.v);
      s += '<rect x="' + (cx - bw / 2).toFixed(1) + '" y="' + Math.min(y0, y1).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.abs(y1 - y0).toFixed(1) + '" rx="3" fill="' + css('--acc') + '" opacity=".85"/>';
      if (x.v2) { var y2 = Y(x.v + x.v2); s += '<rect x="' + (cx - bw / 2).toFixed(1) + '" y="' + y2.toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.abs(y1 - y2).toFixed(1) + '" rx="3" fill="' + css('--t3') + '" opacity=".6"/>'; }
      if (!opts || !opts.thin || i % opts.thin === 0 || i === n - 1) s += '<text x="' + cx.toFixed(1) + '" y="' + (H - 10) + '" text-anchor="middle">' + x.label + '</text>';
    });
    s += '<path d="M' + L + ' ' + Y(0).toFixed(1) + 'H' + (W - R) + '" stroke="' + css('--t3') + '"/>';
    el.innerHTML = s;
  }
  function drawKrd(K, MV) {
    var el = $('#fiKrd'); if (!el) return;
    bars(el, KEYS.map(function (k, i) { return { label: k + '-year', v: K[i] }; }), function (v) { return '$' + cm(v, 0); });
    var tot = K.reduce(function (a, b) { return a + b; }, 0), top = 0; K.forEach(function (k, i) { if (k > K[top]) top = i; });
    $('#fiKrdNote').innerHTML = 'Dollars lost if the yield at <i>only</i> that maturity rises one basis point. Together they add up to the DV01 of ' + usd(tot) + '. Most of the risk sits at the <b>' + KEYS[top] + '-year</b> point (' + pc(K[top] / tot, 0) + ').';
  }
  function drawCf() {
    var el = $('#fiCf'); if (!el) return;
    var maxT = 0; PF.forEach(function (b) { maxT = Math.max(maxT, Math.ceil(b.T)); });
    var yrsN = Math.max(1, maxT), cp = [], pr = [];
    for (var y = 0; y < yrsN; y++) { cp.push(0); pr.push(0); }
    PF.forEach(function (b) { flows(b).forEach(function (x) { var y = Math.min(yrsN - 1, Math.ceil(x.t) - 1), coup = 100 * b.c / 2 * b.amt / 100; cp[y] += coup; if (x.a > 100 * b.c / 2 + 1e-9) pr[y] += b.amt; }); });
    bars(el, cp.map(function (c, i) { return { label: String(i + 1), v: c, v2: pr[i] }; }), function (v) { return v >= 1000 ? '$' + cm(v / 1000, 0) + 'k' : '$' + cm(v, 0); }, { thin: yrsN > 12 ? 5 : 1 });
    var inc = cp[0];
    $('#fiCfNote').innerHTML = 'Interest in copper, principal coming back in grey, by year. Next year&rsquo;s interest: <b>' + usd(inc) + '</b>.';
  }
  function drawMix(mix, MV) {
    var el = $('#fiMix'); if (!el) return;
    var buckets = [['Under 3 years', 0, 3], ['3 to 7', 3, 7], ['7 to 15', 7, 15], ['Over 15', 15, 99]], bm = [0, 0, 0, 0];
    PF.forEach(function (b) { var mv = priceY(b, b.y) / 100 * b.amt; bm[b.T <= 3 ? 0 : b.T <= 7 ? 1 : b.T <= 15 ? 2 : 3] += mv; });
    var row = function (label, v) { return '<div class="mixr"><span>' + label + '</span><i><b style="width:' + (v / MV * 100).toFixed(1) + '%"></b></i><em>' + pc(v / MV, 0) + '</em></div>'; };
    el.innerHTML = '<div class="mixg"><div><h4 class="mono">By credit</h4>' + row('Treasury', mix.tsy) + row('Investment grade', mix.ig) + row('High yield', mix.hy) + '</div>' +
      '<div><h4 class="mono">By maturity</h4>' + buckets.map(function (k, i) { return row(k[0], bm[i]); }).join('') + '</div></div>';
  }

  /* ---------- asset-liability: does the portfolio still cover the goal after the move? ---------- */
  function goal(A, MV, D, km, ch) {
    var el = $('#fiGoal'); if (!el) return;
    if (!GOAL.on) { el.innerHTML = '<p class="fine" style="margin-top:0">Turn the goal on to compare the portfolio with a payment it has to make.</p>'; return; }
    var z = zAt(GOAL.T), PV = GOAL.amt / Math.pow(1 + z / 2, GOAL.T * 2), DL = GOAL.T / (1 + z / 2);
    var PV1 = GOAL.amt / Math.pow(1 + (z + moveAt(GOAL.T, km)) / 2, GOAL.T * 2);
    var sur = MV - PV, sur1 = MV + ch - PV1, fr = MV / PV, gap = D - DL * PV / MV, need = DL * PV / MV;
    el.innerHTML = '<div class="kv four">' +
      '<div><b>' + usd(PV) + '</b><span>Cost of the goal today, at ' + pc(z) + '</span></div>' +
      '<div><b class="' + (fr >= 1 ? 'up' : 'dn') + '">' + pc(fr, 0) + '</b><span>Funded: portfolio over that cost</span></div>' +
      '<div><b>' + (gap >= 0 ? '+' : '−') + Math.abs(gap).toFixed(2) + '</b><span>Duration gap, in years</span></div>' +
      '<div><b class="' + (sur1 - sur >= 0 ? 'up' : 'dn') + '">' + sgnUsd(sur1 - sur) + '</b><span>Change in surplus after the move</span></div></div>' +
      '<p class="fine">The goal is valued like a zero-coupon Treasury maturing on its date, so rates move it too: when yields rise, the money needed today falls. ' +
      (Math.abs(gap) < 0.25 ? 'The durations are matched, so small parallel moves barely change the surplus: the portfolio is <b>immunised</b>.' :
        gap > 0 ? 'The portfolio is <b>longer</b> than the goal: rising rates hurt it more than they help the goal. A duration near <b>' + need.toFixed(1) + '</b> would match.' :
          'The portfolio is <b>shorter</b> than the goal: falling rates raise the goal&rsquo;s cost faster than the bonds gain. A duration near <b>' + need.toFixed(1) + '</b> would match.') + '</p>';
  }

  /* ---------- start ---------- */
  function start() {
    PF = starter(); table(); controls(); goalControls(); run();
    var stamp = $('#fiStamp');
    if (stamp) stamp.textContent = (CDATE ? 'Treasury curve of ' + fdate(CDATE) : 'Sample curve') + (SDATE ? ' · spreads of ' + fdate(SDATE) + ': investment grade ' + Math.round(SPR.ig * 1e4) + ' bp, high yield ' + Math.round(SPR.hy * 1e4) + ' bp' : '');
    var add = $('#fiAdd'), rs = $('#fiReset');
    if (add) add.onclick = function () { PF.push(fresh('ig', 7)); table(); run(); };
    if (rs) rs.onclick = function () { PF = starter(); table(); run(); };
    var t; addEventListener('resize', function () { clearTimeout(t); t = setTimeout(run, 150); });
    new MutationObserver(run).observe(d, { attributes: true, attributeFilter: ['class'] });
  }
  window.LDBFI = { zAt: zAt, priceY: priceY, priceZ: priceZ, spreadFor: spreadFor, analyse: analyse, keyMoves: keyMoves, moveAt: moveAt };   // for checking the math in the console
  var base = (document.querySelector('script[src*="fi.js"]') || {}).src || '';
  base = base.slice(0, base.indexOf('assets/'));
  (window.LDBget ? window.LDBget('data/markets.json').catch(function () { return null; }) : fetch(base + 'data/markets.json').then(function (r) { return r.ok ? r.json() : null; })).then(function (m) {
    var c = m && m.curve, set = c && c.sets && c.sets[0];
    if (set) { var cv = c.tenors.map(function (k, i) { return [TEN[k], set.v[i] / 100]; }).filter(function (p) { return p[0] != null && p[1] != null && !isNaN(p[1]); }); if (cv.length > 4) { CURVE = cv; CDATE = set.date || ''; } }
    var s = m && m.series;
    if (s && s.BAMLC0A0CM && s.BAMLC0A0CM.last) { SPR.ig = s.BAMLC0A0CM.last.v / 100; SDATE = s.BAMLC0A0CM.last.d; }
    if (s && s.BAMLH0A0HYM2 && s.BAMLH0A0HYM2.last) SPR.hy = s.BAMLH0A0HYM2.last.v / 100;
  }).catch(function () {}).then(start);
})();
