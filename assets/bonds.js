/* LDB Finance: bond pricer and rate shock. Plain JavaScript, no libraries.
   Prices assume settlement on a coupon date (no accrued interest), which keeps every number checkable by hand. */
(function () {
  'use strict';
  var d = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var css = function (v) { return getComputedStyle(d).getPropertyValue(v).trim(); };
  var still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- bond math ---------- */
  function flows(b) {                       // b: {c: coupon rate, T: years, f: payments a year, F: face}
    var n = Math.max(1, Math.round(b.T * b.f)), cf = [];
    for (var k = 1; k <= n; k++) cf.push({ k: k, t: k / b.f, a: b.F * b.c / b.f + (k === n ? b.F : 0) });
    return cf;
  }
  function price(b, y) {                    // y: annual yield, compounded b.f times a year
    var r = y / b.f, p = 0;
    flows(b).forEach(function (x) { p += x.a / Math.pow(1 + r, x.k); });
    return p;
  }
  function stats(b, y) {
    var r = y / b.f, P = 0, mac = 0, cx = 0, cf = flows(b);
    cf.forEach(function (x) { var pv = x.a / Math.pow(1 + r, x.k); x.pv = pv; P += pv; mac += x.t * pv; cx += pv * x.k * (x.k + 1); });
    mac /= P;
    var mod = mac / (1 + r);
    cx = cx / (P * Math.pow(1 + r, 2) * b.f * b.f);
    return { P: P, mac: mac, mod: mod, cx: cx, dv01: mod * P * 1e-4, cf: cf, cy: b.F * b.c / P };
  }
  function ytm(b, P) {                      // bisection is slower than Newton but never misbehaves
    var lo = -0.05, hi = 1.0;
    if (price(b, lo) < P || price(b, hi) > P) return null;
    for (var i = 0; i < 200; i++) { var m = (lo + hi) / 2; if (price(b, m) > P) lo = m; else hi = m; if (hi - lo < 1e-10) break; }
    return (lo + hi) / 2;
  }

  /* ---------- today's Treasury curve, from the nightly data file ---------- */
  var TEN = { '1M': 1 / 12, '3M': .25, '6M': .5, '1Y': 1, '2Y': 2, '3Y': 3, '5Y': 5, '7Y': 7, '10Y': 10, '20Y': 20, '30Y': 30 };
  var CURVE = null, CDATE = '';
  function curveAt(T) {
    if (!CURVE) return null;
    var c = CURVE;
    if (T <= c[0][0]) return c[0][1];
    for (var i = 1; i < c.length; i++) if (T <= c[i][0]) { var a = c[i - 1], z = c[i]; return a[1] + (z[1] - a[1]) * (T - a[0]) / (z[0] - a[0]); }
    return c[c.length - 1][1];
  }

  /* ---------- formatting ---------- */
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function fdate(s) { var p = s.split('-'); return MON[+p[1] - 1] + ' ' + (+p[2]) + ', ' + p[0]; }
  function cm(v, dp) { return v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function usd(v, dp) { return (v < 0 ? '−' : '') + '$' + cm(Math.abs(v), dp == null ? 2 : dp); }
  function sgnUsd(v, dp) { return (v > 0 ? '+' : v < 0 ? '−' : '') + '$' + cm(Math.abs(v), dp == null ? 0 : dp); }
  function pc(v, dp) { return cm(v * 100, dp == null ? 2 : dp) + '%'; }
  function sgnPc(v, dp) { var r = +(v * 100).toFixed(dp == null ? 2 : dp); return (r > 0 ? '+' : r < 0 ? '−' : '') + cm(Math.abs(r), dp == null ? 2 : dp) + '%'; }
  function bp(v) { var r = Math.round(v); return (r > 0 ? '+' : r < 0 ? '−' : '') + Math.abs(r) + ' bp'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* ---------- small SVG chart helper ---------- */
  function svgEl(el, w, h) { el.setAttribute('viewBox', '0 0 ' + w + ' ' + h); el.innerHTML = ''; return el; }
  function nice(lo, hi, n) {
    var span = hi - lo || 1, step = Math.pow(10, Math.floor(Math.log10(span / n))), e = span / n / step;
    step *= e >= 5 ? 10 : e >= 2 ? 5 : e >= 1 ? 2 : 1;
    var out = []; for (var v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
    return out;
  }
  function chart(el, o) {                   // o: {x:[lo,hi], y:[lo,hi], xf, yf, series:[{pts, color, w, dash, area}], marks:[{x,y,r,color}], vline}
    var W = el.clientWidth || 640, H = el.clientHeight || 280, L = 58, R = 16, T = 14, B = 34;
    svgEl(el, W, H);
    var X = function (v) { return L + (v - o.x[0]) / (o.x[1] - o.x[0]) * (W - L - R); };
    var Y = function (v) { return T + (1 - (v - o.y[0]) / (o.y[1] - o.y[0])) * (H - T - B); };
    var line = css('--line'), t3 = css('--t3'), s = '';
    nice(o.y[0], o.y[1], 4).forEach(function (v) { s += '<path d="M' + L + ' ' + Y(v).toFixed(1) + 'H' + (W - R) + '" stroke="' + line + '"/><text x="' + (L - 10) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end">' + o.yf(v) + '</text>'; });
    nice(o.x[0], o.x[1], W < 500 ? 4 : 6).forEach(function (v) { s += '<text x="' + X(v).toFixed(1) + '" y="' + (H - 10) + '" text-anchor="middle">' + o.xf(v) + '</text>'; });
    if (o.zero != null) s += '<path d="M' + L + ' ' + Y(o.zero).toFixed(1) + 'H' + (W - R) + '" stroke="' + t3 + '" stroke-dasharray="2 3"/>';
    if (o.vline != null) s += '<path d="M' + X(o.vline).toFixed(1) + ' ' + T + 'V' + (H - B) + '" stroke="' + t3 + '" stroke-dasharray="2 3"/>';
    (o.series || []).forEach(function (sr) {
      var p = sr.pts.map(function (q, i) { return (i ? 'L' : 'M') + X(q[0]).toFixed(1) + ' ' + Y(q[1]).toFixed(1); }).join('');
      if (sr.area) s += '<path d="' + p + 'L' + X(sr.pts[sr.pts.length - 1][0]).toFixed(1) + ' ' + Y(o.y[0]) + 'L' + X(sr.pts[0][0]).toFixed(1) + ' ' + Y(o.y[0]) + 'Z" fill="' + sr.color + '" opacity=".10"/>';
      s += '<path d="' + p + '" fill="none" stroke="' + sr.color + '" stroke-width="' + (sr.w || 2) + '"' + (sr.dash ? ' stroke-dasharray="' + sr.dash + '"' : '') + ' stroke-linejoin="round" stroke-linecap="round"/>';
    });
    (o.marks || []).forEach(function (m) { s += '<circle cx="' + X(m.x).toFixed(1) + '" cy="' + Y(m.y).toFixed(1) + '" r="' + (m.r || 5) + '" fill="' + m.color + '" stroke="' + css('--s1') + '" stroke-width="3"/>'; });
    el.innerHTML = s;
  }

  /* ---------- inputs: the same stepper boxes as the valuation tool ---------- */
  function box(key, label, val, unit, hint) {
    return '<label class="in"><span>' + label + (hint ? '<small>' + hint + '</small>' : '') + '</span><div class="box"><button type="button" data-k="' + key + '" data-d="-1">−</button>' +
      '<input data-k="' + key + '" inputmode="decimal" value="' + val + '"><i>' + (unit || '') + '</i><button type="button" data-k="' + key + '" data-d="1">+</button></div></label>';
  }

  /* ================= 1. bond pricer ================= */
  var B = { F: 1000, c: 0.045, T: 10, f: 2, y: 0.045, px: 100, solve: 'price' };
  var STEP = { c: 0.00125, T: 1, y: 0.0005, px: 0.25, F: 1000 };
  var KEY = { c: 'pc', y: 'pc', T: 'n', px: 'n', F: 'n' };
  function shown(k) { var v = B[k]; return KEY[k] === 'pc' ? (v * 100).toFixed(k === 'y' ? 3 : 3).replace(/0$/, '') : k === 'px' ? v.toFixed(3) : String(v); }

  function pricerInputs() {
    var el = $('#bIn'); if (!el) return;
    el.innerHTML =
      '<div class="seg" id="bSolve"><button type="button" data-v="price"' + (B.solve === 'price' ? ' class="on"' : '') + '>I Know the Yield</button><button type="button" data-v="yield"' + (B.solve === 'yield' ? ' class="on"' : '') + '>I Know the Price</button></div>' +
      '<div class="ins">' +
      box('c', 'Coupon rate', shown('c'), '%', 'Paid on face value') +
      box('T', 'Years to maturity', shown('T'), 'yr') +
      (B.solve === 'price' ? box('y', 'Yield to maturity', shown('y'), '%', 'The market’s required return') : box('px', 'Price', shown('px'), '', 'Per $100 of face value')) +
      box('F', 'Face value', shown('F'), '$', 'Paid back at maturity') +
      '</div>' +
      '<div class="seg sm" id="bFreq"><span class="mono">Coupons a year</span>' + [1, 2, 4, 12].map(function (f) { return '<button type="button" data-v="' + f + '"' + (B.f === f ? ' class="on"' : '') + '>' + f + '</button>'; }).join('') + '</div>' +
      '<div class="tsy" id="bTsy"></div>';
    wire(el, B, STEP, function () { pricer(); });
    $$('#bSolve button').forEach(function (b) { b.onclick = function () { B.solve = b.getAttribute('data-v'); pricerInputs(); pricer(); }; });
    $$('#bFreq button').forEach(function (b) { b.onclick = function () { B.f = +b.getAttribute('data-v'); pricerInputs(); pricer(); }; });
    tsyNote();
  }
  function tsyNote() {
    var el = $('#bTsy'); if (!el) return;
    var y = curveAt(B.T);
    if (y == null) { el.innerHTML = ''; return; }
    el.innerHTML = '<span>A ' + (B.T % 1 ? B.T.toFixed(1) : B.T) + '-year Treasury yields about <b>' + pc(y) + '</b> today' + (CDATE ? ' (' + fdate(CDATE) + ')' : '') + '.</span><button type="button" class="reset" id="bUse">Use It</button>' +
      '<button type="button" class="reset" id="bPar">Price a New Treasury</button>';
    $('#bUse').onclick = function () { B.y = Math.round(y * 1e5) / 1e5; B.solve = 'price'; pricerInputs(); pricer(); };
    $('#bPar').onclick = function () { B.y = Math.round(y * 1e5) / 1e5; B.c = Math.round(y * 800) / 800; B.solve = 'price'; B.f = 2; pricerInputs(); pricer(); };
  }

  function wire(root, S, STP, done) {
    $$('button[data-k]', root).forEach(function (b) {
      b.onclick = function () {
        var k = b.getAttribute('data-k'), s = STP[k] * (+b.getAttribute('data-d'));
        S[k] = Math.max(k === 'T' ? 0.5 : k === 'F' ? 100 : k === 'px' ? 1 : k === 'c' ? 0 : -0.02, +(S[k] + s).toFixed(6));
        var inp = $('input[data-k="' + k + '"]', root); if (inp) inp.value = root === $('#bIn') ? shown(k) : S[k];
        done(k);
      };
    });
    $$('input[data-k]', root).forEach(function (inp) {
      inp.onchange = function () {
        var k = inp.getAttribute('data-k'), v = parseFloat(inp.value.replace(/[^0-9.\-]/g, ''));
        if (isNaN(v)) { inp.value = shown(k); return; }
        if (KEY[k] === 'pc') v /= 100;
        if (k === 'T') v = Math.min(100, Math.max(0.5, Math.round(v * 2) / 2));
        if (k === 'c') v = Math.max(0, Math.min(0.3, v));
        if (k === 'y') v = Math.max(-0.02, Math.min(0.5, v));
        if (k === 'px') v = Math.max(1, Math.min(300, v));
        if (k === 'F') v = Math.max(100, v);
        S[k] = v; inp.value = shown(k); done(k);
      };
    });
  }

  function pricer() {
    var out = $('#bOut'); if (!out) return;
    var y = B.y, note = '';
    if (B.solve === 'yield') {
      var Y0 = ytm(B, B.px / 100 * B.F);
      if (Y0 == null) { out.innerHTML = '<div class="wait"><b>That price has no sensible yield.</b> Try a price closer to 100.</div>'; return; }
      y = Y0; B.y = Y0;
    } else B.px = price(B, y) / B.F * 100;
    var s = stats(B, y), P = s.P, prem = P / B.F - 1;
    note = Math.abs(prem) < 0.0005 ? 'The coupon equals the yield, so the bond trades at <b>par</b>.' :
      prem > 0 ? 'The coupon is above the yield, so the bond trades at a <b>premium</b> of ' + usd(P - B.F) + ' and drifts down to par by maturity.' :
        'The coupon is below the yield, so the bond trades at a <b>discount</b> of ' + usd(B.F - P) + ' and drifts up to par by maturity.';
    out.innerHTML =
      '<div class="bres"><div class="bprice"><span class="mono">' + (B.solve === 'yield' ? 'Yield to maturity' : 'Price') + '</span>' +
      (B.solve === 'yield' ? '<b>' + pc(y, 3) + '</b><small>At a price of ' + B.px.toFixed(3) + ' per $100</small>' : '<b>' + usd(P) + '</b><small>' + (P / B.F * 100).toFixed(3) + ' per $100 of face value</small>') +
      '</div><p>' + note + '</p></div>' +
      '<div class="kv three">' +
      '<div><b>' + pc(s.cy) + '</b><span>Current yield</span></div>' +
      '<div><b>' + s.mac.toFixed(2) + '<small> yr</small></b><span>Macaulay duration</span></div>' +
      '<div><b>' + s.mod.toFixed(2) + '</b><span>Modified duration</span></div>' +
      '<div><b>' + s.cx.toFixed(1) + '</b><span>Convexity</span></div>' +
      '<div><b>' + usd(s.dv01) + '</b><span>DV01, per bond</span></div>' +
      '<div><b>' + sgnPc(-s.mod * 0.01 + 0.5 * s.cx * 1e-4, 2) + '</b><span>If yields rise 1 point</span></div>' +
      '</div>';
    drawPY(s, y);
    drawCF(s);
    tsyNote();
  }

  function drawPY(s, y) {
    var el = $('#cPY'); if (!el) return;
    var lo = Math.max(-0.01, y - 0.04), hi = y + 0.04, pts = [], tan = [], ymin = 1e9, ymax = -1e9;
    for (var i = 0; i <= 80; i++) {
      var yy = lo + (hi - lo) * i / 80, p = price(B, yy) / B.F * 100, t = s.P / B.F * 100 * (1 - s.mod * (yy - y));
      pts.push([yy * 100, p]); tan.push([yy * 100, t]); ymin = Math.min(ymin, p, t); ymax = Math.max(ymax, p, t);
    }
    var pad = (ymax - ymin) * 0.06;
    chart(el, { x: [lo * 100, hi * 100], y: [ymin - pad, ymax + pad], xf: function (v) { return v.toFixed(v % 1 ? 1 : 0) + '%'; }, yf: function (v) { return v.toFixed(0); },
      vline: y * 100,
      series: [{ pts: tan, color: css('--t3'), w: 1.4, dash: '4 5' }, { pts: pts, color: css('--acc'), w: 2.2, area: true }],
      marks: [{ x: y * 100, y: s.P / B.F * 100, color: css('--ink') }] });
  }
  function drawCF(s) {
    var el = $('#cCF'); if (!el) return;
    var W = el.clientWidth || 640, H = el.clientHeight || 150, L = 8, R = 8, T = 12, Bm = 26;
    svgEl(el, W, H);
    var cf = s.cf, n = cf.length, last = cf[n - 1];
    var bw = Math.max(1, (W - L - R) / n * 0.62), X = function (t) { return L + (t / last.t) * (W - L - R - bw) ; };
    var coupPV = function (k) { return B.F * B.c / B.f / Math.pow(1 + B.y / B.f, k); };
    var cmax = B.c > 0 ? coupPV(1) : 0, hmax = Math.max(cmax * 4, (cf[n - 1].pv) * (cmax > 0 ? 0 : 1) || 1);
    var cut = cf[n - 1].pv > hmax;                 /* the face value dwarfs the coupons, so its bar is cut and labelled */
    var Y = function (v) { return (H - Bm) - Math.min(v, hmax) / hmax * (H - Bm - T); };
    var acc = css('--acc'), t3 = css('--t3'), out = '';
    cf.forEach(function (x) {
      var coup = coupPV(x.k);
      out += '<rect x="' + X(x.t).toFixed(1) + '" y="' + Y(coup).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + ((H - Bm) - Y(coup)).toFixed(1) + '" fill="' + acc + '" opacity=".8"/>';
      if (x.k === n) {
        out += '<rect x="' + X(x.t).toFixed(1) + '" y="' + Y(x.pv).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + (Y(coup) - Y(x.pv)).toFixed(1) + '" fill="' + t3 + '" opacity=".55"/>';
        if (cut) out += '<path d="M' + (X(x.t) - 3).toFixed(1) + ' ' + (T + 14) + 'l' + (bw + 6).toFixed(1) + ' -5M' + (X(x.t) - 3).toFixed(1) + ' ' + (T + 20) + 'l' + (bw + 6).toFixed(1) + ' -5" stroke="' + css('--s1') + '" stroke-width="3"/>';
        out += '<text x="' + (X(x.t) - 6).toFixed(1) + '" y="' + (T + 30) + '" text-anchor="end">Face value, worth ' + usd(x.pv - coup, 0) + ' today</text>';
      }
    });
    var mx = X(s.mac) + bw / 2;
    out += '<path d="M' + mx.toFixed(1) + ' ' + T + 'V' + (H - Bm) + '" stroke="' + css('--ink') + '" stroke-dasharray="2 3"/><text x="' + (mx + (mx > W - 140 ? -6 : 6)).toFixed(1) + '" y="' + ((H - Bm) - (H - Bm - T) * 0.5).toFixed(1) + '" text-anchor="' + (mx > W - 140 ? 'end' : 'start') + '">Duration ' + s.mac.toFixed(1) + ' yr</text>';
    out += '<path d="M' + L + ' ' + (H - Bm) + 'H' + (W - R) + '" stroke="' + css('--line2') + '"/><text x="' + L + '" y="' + (H - 8) + '">Today</text><text x="' + (W - R) + '" y="' + (H - 8) + '" text-anchor="end">' + (B.T % 1 ? B.T.toFixed(1) : B.T) + ' years</text>';
    el.innerHTML = out;
  }

  /* ================= 2. rate shock ================= */
  var PF = [];        // {name, amt (face), c, T, y}
  var SH = { s: 100, l: 100 };   // bp shift at the 2-year and 30-year points
  var PRESETS = [
    ['Up 1 point', 100, 100], ['Down 1 point', -100, -100], ['Bear steepener', 25, 125], ['Bull flattener', -100, -25],
    ['Inversion', 150, -25], ['2022 again', 400, 230]];
  function ladder() {
    return [['2-year Treasury', 2], ['5-year Treasury', 5], ['10-year Treasury', 10], ['30-year Treasury', 30]].map(function (r) {
      var y = curveAt(r[1]); y = y == null ? 0.045 : y;
      return { name: r[0], amt: 25000, c: Math.round(y * 800) / 800, T: r[1], y: Math.round(y * 1e5) / 1e5 };
    });
  }
  function shiftAt(T) {                      // linear between the 2-year and 30-year points, flat outside
    var t = Math.min(1, Math.max(0, (T - 2) / 28));
    return (SH.s + (SH.l - SH.s) * t) / 1e4;
  }
  function pfTable() {
    var el = $('#pfT'); if (!el) return;
    el.innerHTML = '<div class="scroll"><table class="tbl pf"><thead><tr><th>Bond</th><th>Face amount</th><th>Coupon</th><th>Years</th><th>Yield</th><th></th></tr></thead><tbody>' +
      PF.map(function (b, i) {
        return '<tr data-i="' + i + '"><td><input class="cell nm" data-f="name" value="' + esc(b.name) + '" aria-label="Bond name"></td>' +
          '<td><input class="cell" data-f="amt" inputmode="decimal" value="' + cm(b.amt, 0) + '" aria-label="Face amount"></td>' +
          '<td><input class="cell" data-f="c" inputmode="decimal" value="' + (b.c * 100).toFixed(3) + '" aria-label="Coupon, percent"><i>%</i></td>' +
          '<td><input class="cell" data-f="T" inputmode="decimal" value="' + b.T + '" aria-label="Years to maturity"></td>' +
          '<td><input class="cell" data-f="y" inputmode="decimal" value="' + (b.y * 100).toFixed(3) + '" aria-label="Yield, percent"><i>%</i></td>' +
          '<td><button type="button" class="x" data-del="' + i + '" aria-label="Remove">×</button></td></tr>';
      }).join('') + '</tbody></table></div>';
    $$('input.cell', el).forEach(function (inp) {
      inp.onchange = function () {
        var i = +inp.closest('tr').getAttribute('data-i'), f = inp.getAttribute('data-f'), b = PF[i];
        if (f === 'name') { b.name = inp.value.slice(0, 40) || 'Bond'; shock(); return; }
        var v = parseFloat(inp.value.replace(/[^0-9.\-]/g, ''));
        if (!isNaN(v)) {
          if (f === 'c' || f === 'y') v /= 100;
          if (f === 'amt') v = Math.max(0, v);
          if (f === 'T') v = Math.min(100, Math.max(0.5, Math.round(v * 2) / 2));
          if (f === 'c') v = Math.max(0, Math.min(0.3, v));
          if (f === 'y') v = Math.max(-0.02, Math.min(0.5, v));
          b[f] = v;
        }
        pfTable(); shock();
      };
    });
    $$('button[data-del]', el).forEach(function (x) { x.onclick = function () { PF.splice(+x.getAttribute('data-del'), 1); pfTable(); shock(); }; });
  }

  function shockInputs() {
    var el = $('#sIn'); if (!el) return;
    el.innerHTML = '<div class="chips sm" id="sPre">' + PRESETS.map(function (p, i) { return '<button type="button" class="chip" data-p="' + i + '">' + p[0] + '</button>'; }).join('') + '</div>' +
      '<div class="sl"><label><span>Short end <small>2-year yield</small></span><b id="sSv"></b></label><input type="range" id="sS" min="-300" max="500" step="5" value="' + SH.s + '" aria-label="Change in the 2-year yield, basis points"></div>' +
      '<div class="sl"><label><span>Long end <small>30-year yield</small></span><b id="sLv"></b></label><input type="range" id="sL" min="-300" max="500" step="5" value="' + SH.l + '" aria-label="Change in the 30-year yield, basis points"></div>';
    $('#sS').oninput = function () { SH.s = +this.value; shock(); };
    $('#sL').oninput = function () { SH.l = +this.value; shock(); };
    $$('#sPre .chip').forEach(function (c) { c.onclick = function () { var p = PRESETS[+c.getAttribute('data-p')]; SH.s = p[1]; SH.l = p[2]; $('#sS').value = SH.s; $('#sL').value = SH.l; shock(); }; });
  }

  function shock() {
    var out = $('#sOut'); if (!out) return;
    $('#sSv').textContent = bp(SH.s); $('#sLv').textContent = bp(SH.l);
    $$('#sPre .chip').forEach(function (c) { var p = PRESETS[+c.getAttribute('data-p')]; c.classList.toggle('on', p[1] === SH.s && p[2] === SH.l); });
    if (!PF.length) { out.innerHTML = '<div class="wait"><b>No bonds yet.</b> Add one, or load the Treasury ladder.</div>'; $('#cSh').innerHTML = ''; return; }
    var V0 = 0, V1 = 0, DV = 0, rows = '', dur = 0;
    PF.forEach(function (b) {
      var bb = { F: 100, c: b.c, T: b.T, f: 2 }, s = stats(bb, b.y), dy = shiftAt(b.T);
      var v0 = s.P / 100 * b.amt, v1 = price(bb, b.y + dy) / 100 * b.amt;
      var dEst = -s.mod * dy * v0, cEst = dEst + 0.5 * s.cx * dy * dy * v0;
      V0 += v0; V1 += v1; DV += s.dv01 / 100 * b.amt; dur += s.mod * v0;
      rows += '<tr><td>' + esc(b.name) + '<small>' + (b.c * 100).toFixed(2) + '% coupon &middot; ' + b.T + ' yr</small></td><td>' + usd(v0, 0) + '</td><td class="hide-sm">' + bp(dy * 1e4) + '</td><td class="' + (v1 - v0 >= 0 ? 'up' : 'dn') + '">' + sgnUsd(v1 - v0) + '</td><td>' + sgnPc(v1 / v0 - 1) + '</td><td class="hide-sm">' + sgnUsd(dEst) + '</td><td class="hide-sm">' + sgnUsd(cEst) + '</td></tr>';
    });
    var ch = V1 - V0, md = dur / V0;
    out.innerHTML = '<div class="kv four">' +
      '<div><b>' + usd(V0, 0) + '</b><span>Market value today</span></div>' +
      '<div><b class="' + (ch >= 0 ? 'up' : 'dn') + '">' + sgnUsd(ch) + '</b><span>Change after the shock, ' + sgnPc(ch / V0) + '</span></div>' +
      '<div><b>' + md.toFixed(2) + '</b><span>Portfolio modified duration</span></div>' +
      '<div><b>' + usd(DV, 0) + '</b><span>DV01: value of one basis point</span></div></div>' +
      '<div class="scroll" style="margin-top:22px"><table class="tbl"><thead><tr><th>Bond</th><th>Value</th><th class="hide-sm">Yield move</th><th>Change</th><th>%</th><th class="hide-sm">Duration guess</th><th class="hide-sm">+ convexity</th></tr></thead><tbody>' + rows +
      '<tr class="hl"><td>Portfolio</td><td>' + usd(V0, 0) + '</td><td class="hide-sm"></td><td class="' + (ch >= 0 ? 'up' : 'dn') + '">' + sgnUsd(ch) + '</td><td>' + sgnPc(ch / V0) + '</td><td class="hide-sm"></td><td class="hide-sm"></td></tr></tbody></table></div>' +
      '<p class="fine">&ldquo;Change&rdquo; reprices every cash flow at the new yield. The two right-hand columns are the shortcuts: duration alone, and duration plus convexity. The gap between them grows with the size of the move.</p>';
    drawShock(V0);
  }
  function drawShock(V0) {
    var el = $('#cSh'); if (!el) return;
    var full = [], lin = [], lo = 1e18, hi = -1e18, tot = 0;
    PF.forEach(function (b) { var st = stats({ F: 100, c: b.c, T: b.T, f: 2 }, b.y); tot += st.mod * st.P / 100 * b.amt; });
    for (var s = -300; s <= 500; s += 10) {
      var v = 0; PF.forEach(function (b) { v += price({ F: 100, c: b.c, T: b.T, f: 2 }, b.y + s / 1e4) / 100 * b.amt; });
      var pnl = (v - V0) / V0 * 100, ln = -tot / V0 * s / 1e4 * 100;
      full.push([s, pnl]); lin.push([s, ln]); lo = Math.min(lo, pnl, ln); hi = Math.max(hi, pnl, ln);
    }
    var cur = 0; PF.forEach(function (b) { cur += price({ F: 100, c: b.c, T: b.T, f: 2 }, b.y + shiftAt(b.T)) / 100 * b.amt; });
    var pad = (hi - lo) * 0.06;
    chart(el, { x: [-300, 500], y: [lo - pad, hi + pad], xf: function (v) { return (v > 0 ? '+' : '') + v; }, yf: function (v) { return (v > 0 ? '+' : '') + v.toFixed(0) + '%'; }, zero: 0, vline: 0,
      series: [{ pts: lin, color: css('--t3'), w: 1.4, dash: '4 5' }, { pts: full, color: css('--acc'), w: 2.2 }],
      marks: SH.s === SH.l ? [{ x: SH.s, y: (cur - V0) / V0 * 100, color: css('--ink') }] : [] });
    $('#cShNote').textContent = SH.s === SH.l ? 'The dot is the shock you picked.' : 'Your shock twists the curve (' + bp(SH.s) + ' at 2 years, ' + bp(SH.l) + ' at 30), so it is not on this parallel-shift line.';
  }

  /* ---------- start ---------- */
  function start() {
    pricerInputs(); pricer();
    PF = ladder(); pfTable(); shockInputs(); shock();
    var add = $('#pfAdd'), lad = $('#pfLad');
    if (add) add.onclick = function () { var y = curveAt(7); y = y == null ? 0.045 : y; PF.push({ name: 'New bond', amt: 10000, c: Math.round(y * 800) / 800, T: 7, y: Math.round(y * 1e5) / 1e5 }); pfTable(); shock(); };
    if (lad) lad.onclick = function () { PF = ladder(); pfTable(); shock(); };
    var t; addEventListener('resize', function () { clearTimeout(t); t = setTimeout(function () { pricer(); shock(); }, 150); });
    new MutationObserver(function () { pricer(); shock(); }).observe(d, { attributes: true, attributeFilter: ['class'] });
  }
  var base = (document.querySelector('script[src*="bonds.js"]') || {}).src || '';
  base = base.slice(0, base.indexOf('assets/'));
  fetch(base + 'data/markets.json?t=' + Math.floor(Date.now() / 600000), { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (m) {
    var c = m && m.curve, set = c && c.sets && c.sets[0];
    if (set) { CURVE = c.tenors.map(function (k, i) { return [TEN[k], set.v[i] / 100]; }).filter(function (p) { return p[0] != null && p[1] != null && !isNaN(p[1]); }); CDATE = set.date || ''; var y10 = curveAt(10); if (y10 != null) { B.y = Math.round(y10 * 1e5) / 1e5; B.c = Math.round(y10 * 800) / 800; } }
  }).catch(function () {}).then(start);
})();
