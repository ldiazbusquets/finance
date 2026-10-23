/* LDB Finance: wealth-management tools. Plain JavaScript, no libraries; everything runs in the browser.
   1. Retirement withdrawals: a fixed inflation-adjusted withdrawal against Guyton-Klinger style guardrails,
      through 2,000 simulated markets.
   2. Tax-loss harvesting: harvesting losses stock by stock (direct indexing) against harvesting a single index fund,
      through 300 simulated markets.
   Both use seeded random numbers, so the same inputs always give the same answer. */
(function () {
  'use strict';
  var d = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var css = function (v) { return getComputedStyle(d).getPropertyValue(v).trim(); };
  function cm(v, dp) { return v.toLocaleString('en-US', { minimumFractionDigits: dp || 0, maximumFractionDigits: dp || 0 }); }
  function usd(v) { var a = Math.abs(v), s = v < 0 ? '−' : ''; return a >= 1e6 ? s + '$' + (a / 1e6).toFixed(2) + 'M' : s + '$' + cm(Math.round(a)); }
  function pc(v, dp) { return (v < 0 ? '−' : '') + cm(Math.abs(v) * 100, dp == null ? 1 : dp) + '%'; }
  function rng(seed) { var s = seed >>> 0; return function () { s = (s + 0x6D2B79F5) >>> 0; var t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function gauss(r) { var u = 0, v = 0; while (u === 0) u = r(); while (v === 0) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(6.283185307 * v); }
  function pct(a, p) { var s = a.slice().sort(function (x, y) { return x - y; }); return s[Math.min(s.length - 1, Math.max(0, Math.floor(p * s.length)))]; }

  /* ---------- shared inputs: the same +/- boxes as the other tools ---------- */
  function inputsUI(el, S, SPEC, HINT, keys, done) {
    function shown(k) { var s = SPEC[k], v = S[k]; return s[3] === 'pc' ? (v * 100).toFixed(s[4] == null ? 1 : s[4]) : cm(v); }
    el.innerHTML = '<div class="ins">' + keys.map(function (k) {
      var s = SPEC[k];
      return '<label class="in"><span>' + s[0] + (HINT[k] ? '<small>' + HINT[k] + '</small>' : '') + '</span><div class="box"><button type="button" data-k="' + k + '" data-d="-1" aria-label="Less">−</button>' +
        '<input data-k="' + k + '" inputmode="decimal" aria-label="' + s[0] + '" value="' + shown(k) + '"><i>' + s[1] + '</i><button type="button" data-k="' + k + '" data-d="1" aria-label="More">+</button></div></label>';
    }).join('') + '</div>';
    function clamp(k) { var s = SPEC[k]; S[k] = Math.max(s[5], Math.min(s[6], S[k])); }
    $$('input[data-k]', el).forEach(function (inp) {
      inp.addEventListener('change', function () {
        var k = inp.getAttribute('data-k'), v = parseFloat(inp.value.replace(/[^0-9.\-]/g, ''));
        if (isFinite(v)) { S[k] = SPEC[k][3] === 'pc' ? v / 100 : v; clamp(k); }
        inp.value = shown(k); done();
      });
    });
    $$('button[data-k]', el).forEach(function (b) {
      b.onclick = function () { var k = b.getAttribute('data-k'); S[k] = +(S[k] + SPEC[k][2] * +b.getAttribute('data-d')).toFixed(6); clamp(k); $('input[data-k="' + k + '"]', el).value = shown(k); done(); };
    });
  }

  /* ---------- a small line chart with shaded ranges ---------- */
  function chart(el, o) {   // o: {x:[lo,hi], y:[lo,hi], xf, yf, bands:[{lo:[], hi:[], color}], lines:[{pts:[], color, dash, w}]}
    var W = el.clientWidth || 640, H = el.clientHeight || 260, L = 64, R = 12, T = 12, B = 28;
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    var X = function (v) { return L + (v - o.x[0]) / (o.x[1] - o.x[0]) * (W - L - R); };
    var Y = function (v) { return T + (1 - (v - o.y[0]) / (o.y[1] - o.y[0])) * (H - T - B); };
    var line = css('--line'), t3 = css('--t3'), s = '';
    for (var i = 0; i <= 4; i++) { var v = o.y[0] + (o.y[1] - o.y[0]) * i / 4; s += '<path d="M' + L + ' ' + Y(v).toFixed(1) + 'H' + (W - R) + '" stroke="' + line + '"/><text x="' + (L - 8) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end" fill="' + t3 + '" style="font:11px var(--mono)">' + o.yf(v) + '</text>'; }
    var step = Math.max(1, Math.round((o.x[1] - o.x[0]) / 6));
    for (var x = o.x[0]; x <= o.x[1]; x += step) s += '<text x="' + X(x).toFixed(1) + '" y="' + (H - 8) + '" text-anchor="middle" fill="' + t3 + '" style="font:11px var(--mono)">' + o.xf(x) + '</text>';
    (o.bands || []).forEach(function (b) {
      var top = b.hi.map(function (v, i) { return X(o.x[0] + i).toFixed(1) + ' ' + Y(v).toFixed(1); });
      var bot = b.lo.map(function (v, i) { return X(o.x[0] + i).toFixed(1) + ' ' + Y(v).toFixed(1); }).reverse();
      s += '<path d="M' + top.join('L') + 'L' + bot.join('L') + 'Z" fill="' + b.color + '" fill-opacity=".16"/>';
    });
    (o.lines || []).forEach(function (l) {
      s += '<path d="M' + l.pts.map(function (v, i) { return X(o.x[0] + i).toFixed(1) + ' ' + Y(v).toFixed(1); }).join('L') + '" fill="none" stroke="' + l.color + '" stroke-width="' + (l.w || 2) + '"' + (l.dash ? ' stroke-dasharray="5 4"' : '') + '/>';
    });
    el.innerHTML = s;
  }
  function kv(rows) { return '<div class="kv">' + rows.map(function (r) { return '<div><b' + (r[2] ? ' class="' + r[2] + '"' : '') + '>' + r[0] + '</b><span>' + r[1] + '</span></div>'; }).join('') + '</div>'; }

  /* =====================================================================
     1. Retirement withdrawals: fixed versus guardrails
     ===================================================================== */
  var G = { P: 1500000, w: 0.05, eq: 0.60, yrs: 30, infl: 0.025, band: 0.20, adj: 0.10 };
  var GSPEC = { P: ['Portfolio at retirement', '$', 50000, 'n', 0, 10000, 1e9], w: ['First-year withdrawal', '%', 0.0025, 'pc', 2, 0.01, 0.12],
    eq: ['In stocks', '%', 0.05, 'pc', 0, 0, 1], yrs: ['Years it must last', 'yr', 1, 'n', 0, 5, 50], infl: ['Inflation', '%', 0.0025, 'pc', 2, 0, 0.1],
    band: ['Guardrail width', '%', 0.05, 'pc', 0, 0.05, 0.5], adj: ['Size of each cut or raise', '%', 0.01, 'pc', 0, 0.01, 0.5] };
  var GHINT = { w: 'Of the starting portfolio', eq: 'The rest in bonds', band: 'Above or below the first-year rate', adj: 'Applied to spending', infl: 'A year, held constant' };
  var MKT = { rs: 0.075, vs: 0.16, rb: 0.045, vb: 0.06, rho: 0.1, N: 2000 };

  function gsim(S, w0) {
    var r = rng(20261023), N = MKT.N, Y = S.yrs, out = { fixOK: 0, grOK: 0, fixEnd: [], grEnd: [], grReal: [], fixBal: [], grBal: [], grMin: [], cuts: 0 };
    for (var y = 0; y <= Y; y++) { out.grReal.push([]); out.fixBal.push([]); out.grBal.push([]); }
    var mS = Math.log(1 + MKT.rs) - MKT.vs * MKT.vs / 2, mB = Math.log(1 + MKT.rb) - MKT.vb * MKT.vb / 2;
    for (var n = 0; n < N; n++) {
      var pf = S.P, pg = S.P, wf = S.P * w0, wg = S.P * w0, rate0 = w0, okF = true, okG = true, lastRet = 0, minReal = 1, cut = false, cpi = 1;
      out.fixBal[0].push(pf); out.grBal[0].push(pg);
      for (var t = 1; t <= Y; t++) {
        if (t > 1) {
          wf *= 1 + S.infl;
          /* guardrails: no inflation raise after a losing year if spending is already above its starting rate */
          if (!(lastRet < 0 && wg / pg > rate0)) wg *= 1 + S.infl;
          var cur = wg / Math.max(pg, 1);
          if (cur > rate0 * (1 + S.band) && Y - t >= 15) { wg *= 1 - S.adj; cut = true; }       /* capital preservation: not in the last 15 years */
          else if (cur < rate0 * (1 - S.band)) wg *= 1 + S.adj;                                    /* prosperity */
        }
        var z1 = gauss(r), z2 = MKT.rho * z1 + Math.sqrt(1 - MKT.rho * MKT.rho) * gauss(r);
        var ret = S.eq * (Math.exp(mS + MKT.vs * z1) - 1) + (1 - S.eq) * (Math.exp(mB + MKT.vb * z2) - 1);
        cpi = Math.pow(1 + S.infl, t - 1);
        if (okF) { pf -= wf; if (pf < 0) { pf = 0; okF = false; } pf *= 1 + ret; }
        var take = okG ? Math.min(wg, pg) : 0;
        if (okG) { pg -= wg; if (pg < 0) { pg = 0; okG = false; } pg *= 1 + ret; }
        var real = take / cpi / (S.P * w0);
        minReal = Math.min(minReal, real);
        out.grReal[t].push(real); out.fixBal[t].push(pf); out.grBal[t].push(pg);
        lastRet = ret;
      }
      if (okF) out.fixOK++; if (okG) out.grOK++;
      out.fixEnd.push(pf / Math.pow(1 + S.infl, Y)); out.grEnd.push(pg / Math.pow(1 + S.infl, Y)); out.grMin.push(minReal); if (cut) out.cuts++;
    }
    return out;
  }
  function safeRate(S) {                     /* highest fixed first-year rate that lasts in 90% of markets */
    var lo = 0.01, hi = 0.12, keep = MKT.N; MKT.N = 600;
    for (var k = 0; k < 14; k++) { var m = (lo + hi) / 2; if (gsim(S, m).fixOK / MKT.N >= 0.9) lo = m; else hi = m; }
    MKT.N = keep; return lo;
  }
  function guard() {
    var o = gsim(G, G.w), N = MKT.N, Y = G.yrs, sr = safeRate(G);
    var med = [], lo = [], hi = [], fb = [], gb = [];
    for (var t = 1; t <= Y; t++) { med.push(pct(o.grReal[t], .5)); lo.push(pct(o.grReal[t], .1)); hi.push(pct(o.grReal[t], .9)); }
    for (t = 0; t <= Y; t++) { fb.push(pct(o.fixBal[t], .5) / Math.pow(1 + G.infl, t)); gb.push(pct(o.grBal[t], .5) / Math.pow(1 + G.infl, t)); }
    var first = G.P * G.w;
    $('#gOut').innerHTML = kv([
      [pc(o.fixOK / N, 0), 'Fixed withdrawal: chance the money lasts ' + Y + ' years'],
      [pc(o.grOK / N, 0), 'Guardrails: chance the money lasts', o.grOK > o.fixOK ? 'up' : ''],
      [pc(sr, 2), 'Highest fixed rate that lasts in 90% of markets'],
      [usd(first), 'First-year spending, both plans'],
      [pc(pct(o.grMin, .1), 0), 'Guardrails, a bad market (10th percentile): lowest spending, in today&rsquo;s dollars, as a share of the first year'],
      [pc(o.cuts / N, 0), 'Guardrails: share of markets with at least one cut']
    ]);
    chart($('#gChart'), { x: [1, Y], y: [0, Math.max(1.6, pct(hi, .99) * 1.05)], xf: function (v) { return 'Yr ' + v; }, yf: function (v) { return Math.round(v * 100) + '%'; },
      bands: [{ lo: lo, hi: hi, color: css('--acc') }], lines: [{ pts: med, color: css('--acc') }, { pts: med.map(function () { return 1; }), color: css('--t3'), dash: true, w: 1.5 }] });
    var top = Math.max(pct(fb, .99), pct(gb, .99), G.P) * 1.1;
    chart($('#gBal'), { x: [0, Y], y: [0, top], xf: function (v) { return 'Yr ' + v; }, yf: function (v) { return v >= 1e6 ? '$' + (v / 1e6).toFixed(1) + 'M' : '$' + Math.round(v / 1e3) + 'k'; },
      lines: [{ pts: fb, color: css('--t3'), dash: true }, { pts: gb, color: css('--acc') }] });
    $('#gNote').innerHTML = 'Fixed: <b>' + pc(o.fixOK / N, 0) + '</b> of ' + cm(N) + ' markets last ' + Y + ' years, median ending balance ' + usd(pct(o.fixEnd, .5)) + ' in today&rsquo;s dollars. ' +
      'Guardrails: <b>' + pc(o.grOK / N, 0) + '</b>, median ending balance ' + usd(pct(o.grEnd, .5)) + '. The trade is visible in the first chart: guardrails buy their higher success rate with spending that moves with the market.';
  }
  function guardInit() {
    var el = $('#gIn'); if (!el) return;
    inputsUI(el, G, GSPEC, GHINT, ['P', 'w', 'eq', 'yrs', 'infl', 'band', 'adj'], guard);
    var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(guard, 200); });
    window.addEventListener('themechange', guard);
    guard();
  }

  /* =====================================================================
     2. Tax-loss harvesting: single fund versus stock by stock
     ===================================================================== */
  var H = { P: 500000, yrs: 10, n: 100, idio: 0.25, thr: 0.10, gains: 20000, tg: 0.238, to: 0.37, fee: 0.0015 };
  var HSPEC = { P: ['Amount invested', '$', 25000, 'n', 0, 10000, 1e9], yrs: ['Years', 'yr', 1, 'n', 0, 1, 30], n: ['Stocks held directly', '', 10, 'n', 0, 10, 500],
    idio: ['Stock-specific volatility', '%', 0.05, 'pc', 0, 0, 0.8], thr: ['Harvest when a position is down', '%', 0.01, 'pc', 0, 0.01, 0.5],
    gains: ['Other capital gains each year', '$', 5000, 'n', 0, 0, 1e8], tg: ['Tax rate on capital gains', '%', 0.01, 'pc', 1, 0, 0.5],
    to: ['Tax rate on income', '%', 0.01, 'pc', 0, 0, 0.6], fee: ['Extra cost of direct indexing', '%', 0.0005, 'pc', 2, 0, 0.02] };
  var HHINT = { idio: 'A year, on top of the market', thr: 'Below its cost; checked monthly', gains: 'From other investments, a business, a house', tg: 'Federal 20% + 3.8%', to: 'For the $3,000 a year of losses against income', fee: 'A year, above an index fund', n: 'Equal weights' };

  function tlh(S, paths) {
    var r = rng(7), M = S.yrs * 12, mu = Math.log(1.075) / 12 - 0.16 * 0.16 / 24, sm = 0.16 / Math.sqrt(12), si = S.idio / Math.sqrt(12);
    var res = { yearDI: [], yearETF: [], saveDI: [], saveETF: [], alphaDI: [], alphaETF: [], alphaDIheld: [], basisDI: [] };
    for (var y = 0; y < S.yrs; y++) { res.yearDI.push([]); res.yearETF.push([]); }
    for (var p = 0; p < paths; p++) {
      var n = S.n, px = [], basis = [], sh = [], etf = 1, etfBasis = 1, etfSh = S.P;
      for (var i = 0; i < n; i++) { px.push(1); basis.push(1); sh.push(S.P / n); }
      var bankDI = 0, bankETF = 0, saveDI = 0, saveETF = 0, sideDI = 0, sideETF = 0;
      for (var m = 1; m <= M; m++) {
        var zm = mu + sm * gauss(r);
        etf *= Math.exp(zm);
        for (i = 0; i < n; i++) px[i] *= Math.exp(zm + si * gauss(r) - si * si / 2);
        /* harvest: sell any position down by the threshold, buy a similar stock at once (so the wash-sale rule is not triggered) */
        var lossDI = 0, lossETF = 0;
        for (i = 0; i < n; i++) if (px[i] < basis[i] * (1 - S.thr)) { lossDI += sh[i] * (basis[i] - px[i]); basis[i] = px[i]; }
        if (etf < etfBasis * (1 - S.thr)) { lossETF += etfSh * (etfBasis - etf); etfBasis = etf; }
        bankDI += lossDI; bankETF += lossETF;
        res.yearDI[Math.floor((m - 1) / 12)].push(lossDI); res.yearETF[Math.floor((m - 1) / 12)].push(lossETF);
        sideDI *= Math.exp(zm); sideETF *= Math.exp(zm);
        if (m % 12 === 0) {
          /* year end: losses offset other gains, then up to $3,000 of income; the rest carries forward. Savings are invested in the market */
          [['DI'], ['ETF']].forEach(function (k) {
            var bank = k[0] === 'DI' ? bankDI : bankETF, g = Math.min(bank, S.gains), rest = bank - g, inc = Math.min(rest, 3000), save = g * S.tg + inc * S.to;
            if (k[0] === 'DI') { bankDI = rest - inc; saveDI += save; sideDI += save; } else { bankETF = rest - inc; saveETF += save; sideETF += save; }
          });
          /* the extra cost of holding stocks directly */
          for (i = 0; i < n; i++) px[i] *= 1 - S.fee;
        }
      }
      var vDI = 0, bDI = 0; for (i = 0; i < n; i++) { vDI += sh[i] * px[i]; bDI += sh[i] * basis[i]; }
      var vE = etfSh * etf, bE = etfSh * etfBasis, base = S.P * etf, baseTax = Math.max(0, base - S.P) * S.tg;
      /* after-tax value if sold at the end, against simply holding the index fund and selling it */
      var aDI = vDI + sideDI - Math.max(0, vDI - bDI - bankDI) * S.tg, aE = vE + sideETF - Math.max(0, vE - bE - bankETF) * S.tg, a0 = base - baseTax;
      var held = vDI + sideDI;   /* never sold: the gain is passed on at a stepped-up basis or given away */
      res.alphaDI.push(Math.pow(aDI / a0, 1 / S.yrs) - 1); res.alphaETF.push(Math.pow(aE / a0, 1 / S.yrs) - 1); res.alphaDIheld.push(Math.pow(held / base, 1 / S.yrs) - 1);
      res.saveDI.push(saveDI); res.saveETF.push(saveETF); res.basisDI.push(bDI / vDI);
    }
    return res;
  }
  function harvest() {
    var paths = 300, o = tlh(H, paths), Y = H.yrs;
    var di = o.yearDI.map(function (a) { var s = 0; a.forEach(function (v) { s += v; }); return s / paths / H.P; });
    var et = o.yearETF.map(function (a) { var s = 0; a.forEach(function (v) { s += v; }); return s / paths / H.P; });
    var totDI = di.reduce(function (a, b) { return a + b; }, 0), totE = et.reduce(function (a, b) { return a + b; }, 0);
    $('#hOut').innerHTML = kv([
      [pc(totDI, 0), 'Losses harvested over ' + Y + ' years, stock by stock, as a share of the amount invested (average market)'],
      [pc(totE, 0), 'The same, harvesting a single index fund'],
      [usd(pct(o.saveDI, .5)), 'Tax saved, stock by stock (median market)'],
      [pc(pct(o.alphaDI, .5), 2), 'After-tax gain a year over holding the fund, if everything is sold at the end', pct(o.alphaDI, .5) >= 0 ? 'up' : 'dn'],
      [pc(pct(o.alphaDIheld, .5), 2), 'The same if the stocks are never sold (passed on or given away)', 'up'],
      [pc(1 - pct(o.basisDI, .5), 0), 'How far the cost basis has fallen below market value by the end']
    ]);
    chart($('#hChart'), { x: [1, Y], y: [0, Math.max(0.05, Math.max.apply(null, di) * 1.15)], xf: function (v) { return 'Yr ' + v; }, yf: function (v) { return Math.round(v * 100) + '%'; },
      lines: [{ pts: di, color: css('--acc') }, { pts: et, color: css('--t3'), dash: true }] });
    $('#hNote').innerHTML = 'Most of the harvest comes in the first years. Every loss taken resets a position to a lower cost, so later rises build untaxed gains that are taxed when sold: harvesting defers tax more than it removes it. ' +
      'The deferral is worth most to someone who never sells (the gain is passed on at a stepped-up basis or donated) and to someone with other gains to offset each year.';
  }
  function harvestInit() {
    var el = $('#hIn'); if (!el) return;
    inputsUI(el, H, HSPEC, HHINT, ['P', 'yrs', 'n', 'idio', 'thr', 'gains', 'tg', 'to', 'fee'], harvest);
    var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(harvest, 200); });
    window.addEventListener('themechange', harvest);
    harvest();
  }

  function init() { guardInit(); harvestInit(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
