/* LDB Finance valuation tool: search an S&P 500 company, get a DCF (or a
   bank model), a dividend model where it fits, peer multiples and a summary
   chart. All maths runs in the browser from the nightly data files. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var fn = function (t) { return t.replace(/\./g, '-'); };
  var bust = '?t=' + Math.floor(Date.now() / 600000);
  function getJSON(p) { if (window.LDBget) return window.LDBget(p); return fetch(p + bust, { cache: 'no-store' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var clip = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var isn = function (v) { return typeof v === 'number' && isFinite(v); };
  function last(a) { if (!a) return null; for (var i = a.length - 1; i >= 0; i--) if (isn(a[i])) return a[i]; return null; }
  function lastIdx(a) { if (!a) return -1; for (var i = a.length - 1; i >= 0; i--) if (isn(a[i])) return i; return -1; }
  function median(a) { a = a.filter(isn).sort(function (x, y) { return x - y; }); if (!a.length) return null; var m = a.length >> 1; return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; }
  function q(a, p) { a = a.filter(isn).sort(function (x, y) { return x - y; }); if (!a.length) return null; var i = (a.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return a[lo] + (a[hi] - a[lo]) * (i - lo); }
  function avgRatio(num, den, n, idx) {
    var out = [];
    for (var i = idx; i > idx - n && i >= 0; i--) if (isn(num[i]) && isn(den[i]) && den[i] !== 0) out.push(num[i] / den[i]);
    return out.length ? out.reduce(function (a, b) { return a + b; }, 0) / out.length : null;
  }
  function cagr(a, n, idx) {
    for (var k = Math.min(n, idx); k >= 1; k--) { var x0 = a[idx - k], x1 = a[idx]; if (isn(x0) && isn(x1) && x0 > 0 && x1 > 0) return Math.pow(x1 / x0, 1 / k) - 1; }
    return null;
  }

  /* ---------- formatting ---------- */
  function usd(v, dp) { if (!isn(v)) return '—'; var s = v < 0 ? '−' : ''; return s + '$' + Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: dp == null ? 2 : dp, maximumFractionDigits: dp == null ? 2 : dp }); }
  function big(v) { if (!isn(v)) return '—'; var a = Math.abs(v), s = v < 0 ? '−' : ''; return a >= 1e12 ? s + '$' + (a / 1e12).toFixed(2) + 'T' : a >= 1e9 ? s + '$' + (a / 1e9).toFixed(1) + 'B' : a >= 1e6 ? s + '$' + (a / 1e6).toFixed(0) + 'M' : s + '$' + a.toFixed(0); }
  function pc(v, dp) { if (!isn(v)) return '—'; return (v < 0 ? '−' : '') + Math.abs(v * 100).toFixed(dp == null ? 1 : dp) + '%'; }
  function sp(v, dp) { if (!isn(v)) return '—'; return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v * 100).toFixed(dp == null ? 1 : dp) + '%'; }
  function mx(v) { return isn(v) ? v.toFixed(1) + '×' : '—'; }
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function fd(s) { if (!s) return ''; var p = s.split('-'); return MON[+p[1] - 1] + ' ' + (+p[2]) + ', ' + p[0]; }

  /* ---------- state ---------- */
  var IX = null, PX = {}, RF = null, RFd = null, CO = null, A = null, AUTO = null;
  var ERP_DEFAULT = 0.045;
  var SNAP = document.body.getAttribute('data-page') === 'snapshot', WL = {};

  /* ---------- search ---------- */
  var inp = $('#q'), list = $('#sug'), sel = -1, hits = [];
  function search(s) {
    s = s.trim().toUpperCase(); if (!s || !IX) return [];
    var a = [], b = [];
    IX.rows.forEach(function (r) {
      var t = r[0], n = r[1].toUpperCase();
      if (t === s || t.replace('.', '') === s.replace('.', '')) a.unshift(r);
      else if (t.indexOf(s) === 0) a.push(r);
      else if (n.indexOf(s) === 0 || n.indexOf(' ' + s) >= 0) b.push(r);
    });
    return a.concat(b).slice(0, 8);
  }
  function showSug() {
    hits = search(inp.value); sel = hits.length ? 0 : -1;
    if (!hits.length) { list.classList.remove('open'); list.innerHTML = inp.value.trim() && IX ? '<div class="none">No S&amp;P 500 company matches “' + esc(inp.value.trim()) + '”</div>' : ''; if (inp.value.trim() && IX) list.classList.add('open'); return; }
    list.innerHTML = hits.map(function (r, i) { return '<button type="button" data-i="' + i + '"' + (i === sel ? ' class="on"' : '') + '><b>' + esc(r[0]) + '</b><span>' + esc(r[1]) + '</span><em>' + esc(r[2]) + '</em></button>'; }).join('');
    list.classList.add('open');
  }
  function pick(r) { list.classList.remove('open'); inp.value = ''; inp.blur(); open(r[0]); }
  if (inp) {
    inp.addEventListener('input', showSug);
    inp.addEventListener('focus', function () { if (inp.value) showSug(); });
    inp.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); if (!hits.length) return; sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + hits.length) % hits.length; $$('button', list).forEach(function (b, i) { b.classList.toggle('on', i === sel); }); }
      else if (e.key === 'Enter') { e.preventDefault(); if (hits[sel]) pick(hits[sel]); }
      else if (e.key === 'Escape') { list.classList.remove('open'); }
    });
    list.addEventListener('mousedown', function (e) { var b = e.target.closest('button'); if (b) { e.preventDefault(); pick(hits[+b.getAttribute('data-i')]); } });
    document.addEventListener('click', function (e) { if (!e.target.closest('.search')) list.classList.remove('open'); });
  }
  $$('[data-pick]').forEach(function (b) { b.onclick = function () { open(b.getAttribute('data-pick')); }; });

  /* ---------- load ---------- */
  Promise.all([
    getJSON('data/co/index.json').catch(function () { return null; }),
    getJSON('data/co/prices.json').catch(function () { return {}; }),
    getJSON('data/markets.json').catch(function () { return {}; }),
    getJSON('data/watchlist.json').catch(function () { return {}; })
  ]).then(function (r) {
    ((r[3] && r[3].companies) || []).forEach(function (c) { if (c.page) WL[c.ticker] = c; });
    IX = r[0] && r[0].rows && r[0].rows.length ? r[0] : null;
    PX = (r[1] && r[1].px) || {};
    var s10 = r[2] && r[2].series && r[2].series.DGS10;
    if (s10 && s10.last) { RF = s10.last.v / 100; RFd = s10.last.d; }
    if (!IX) { $('#status').innerHTML = '<div class="wait"><b>Company data is on its way.</b> The S&amp;P 500 figures are collected by the nightly update. Once it has run, search any company here.</div>'; return; }
    $('#count').textContent = IX.rows.length + ' companies · updated ' + fd(IX.updated.slice(0, 10));
    var qp = new URLSearchParams(location.search), t = qp.get('t');
    if (qp.get('view') === 'q') FINMODE = 'q';
    if (t) open(t.toUpperCase());
  });

  function open(t) {
    if (!IX) return;
    var row = IX.rows.find(function (r) { return r[0] === t || fn(r[0]) === fn(t); });
    if (!row) { $('#status').innerHTML = '<div class="wait">' + esc(t) + ' is not in the S&amp;P 500 list yet.</div>'; return; }
    $('#status').innerHTML = '<div class="wait">Loading ' + esc(row[1]) + '&hellip;</div>';
    getJSON('data/co/' + fn(row[0]) + '.json').then(function (d) {
      CO = d; CO.row = row; CO.p = PX[row[0]] || null;
      try { history.replaceState(null, '', '?t=' + encodeURIComponent(row[0])); } catch (e) {}
      document.title = row[1] + ' (' + row[0] + ') ' + (SNAP ? 'snapshot' : 'valuation') + ' | LDB Finance';
      AUTO = assume(CO); A = JSON.parse(JSON.stringify(AUTO));
      $('#status').innerHTML = '';
      $('#out').hidden = false;
      renderStatic(); if (SNAP) renderSnap(); else renderModel();
      $('#out').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }).catch(function () { $('#status').innerHTML = '<div class="wait">Figures for ' + esc(row[1]) + ' are still being collected. Check back after the next update.</div>'; });
  }

  /* the latest quarter, when it is newer than the last annual report */
  function newQ(c) {
    var Q = c && c.q, e = c && c.ends && c.ends[c.ends.length - 1];
    return Q && Q.ttm && Q.end && (!e || Q.end > e) && (isn(Q.ttm.rev) || isn(Q.ttm.ni)) ? Q : null;
  }
  function mon(s) { var p = s.split('-'); return MON[+p[1] - 1] + ' ' + p[0]; }

  /* ---------- automatic assumptions ---------- */
  function assume(c) {
    var f = c.f, i = lastIdx(f.rev) >= 0 ? lastIdx(f.rev) : lastIdx(f.ni), rf = RF || 0.043;
    var price = c.p && c.p.p, shares = c.sh || last(f.dil);
    var tax = avgRatio(f.tax, f.pretax, 3, i); tax = isn(tax) && tax > 0 ? clip(tax, 0.10, 0.30) : 0.21;
    var beta = c.p && isn(c.p.b) ? clip(c.p.b, 0.4, 2.5) : 1.0;
    /* debt from the latest year only: an old year's figure would be stale, and a missing one is flagged, not read as zero */
    var debtNow = i >= 0 && isn(f.debt[i]) ? f.debt[i] : null, debt = debtNow || 0, cash = last(f.cash) || 0;
    var kd = null, di = lastIdx(f.debt);
    if (isn(f.intexp[i]) && di >= 0 && f.debt[di] > 0) kd = f.intexp[i] / ((f.debt[di] + (isn(f.debt[di - 1]) ? f.debt[di - 1] : f.debt[di])) / 2);
    kd = isn(kd) ? clip(kd, rf + 0.005, rf + 0.06) : rf + 0.015;
    var gT = Math.max(0.01, Math.min(0.025, rf - 0.01));
    var a = {
      model: c.model === 'bank' ? 'bank' : 'dcf', rf: rf, beta: beta, erp: ERP_DEFAULT, kd: kd, tax: tax, gT: gT,
      price: price, shares: shares, debt: debt, cash: cash, debtMissing: debtNow === null
    };
    if (a.model === 'dcf') {
      var g1 = cagr(f.rev, 3, i); a.g1 = isn(g1) ? clip(g1, -0.05, c.model === 'reit' ? 0.10 : 0.25) : 0.04;
      var m0 = isn(f.ebit[i]) && f.rev[i] ? f.ebit[i] / f.rev[i] : null, mT = avgRatio(f.ebit, f.rev, 3, i);
      a.flagMargin = false;
      if (!isn(mT) || mT <= 0.02) { mT = 0.10; a.flagMargin = true; }
      a.m0 = isn(m0) ? clip(m0, -0.5, 0.7) : mT; a.mT = clip(mT, -0.1, 0.6);
      a.da = clip(avgRatio(f.da, f.rev, 3, i) || 0.04, 0, 0.4);
      a.capex = clip(avgRatio(f.capex, f.rev, 3, i) || a.da, 0, 0.5);
      var nwc = null;
      if (isn(f.ca[i]) && isn(f.cl[i]) && f.rev[i]) nwc = ((f.ca[i] - (f.cash[i] || 0)) - (f.cl[i] - (f.debtcur[i] || 0))) / f.rev[i];
      a.nwc = isn(nwc) ? clip(nwc, -0.15, 0.3) : 0;
      /* return on new capital for the terminal value: the company's own recent return on capital, kept in a sensible band */
      var roic = [];
      for (var j2 = i; j2 > i - 3 && j2 >= 0; j2--) {
        var ic = (f.debt[j2] || 0) + (f.eq[j2] || 0) - (f.cash[j2] || 0);
        if (isn(f.ebit[j2]) && ic > 0) roic.push(f.ebit[j2] * (1 - tax) / ic);
      }
      a.ronic = roic.length ? clip(roic.reduce(function (x, y) { return x + y; }, 0) / roic.length, 0.10, 0.30) : 0.15;
      a.rev0 = f.rev[i];
    } else {
      var roe = [], j;
      for (j = i; j > i - 3 && j >= 1; j--) if (isn(f.ni[j]) && isn(f.eq[j]) && isn(f.eq[j - 1])) roe.push(f.ni[j] / ((f.eq[j] + f.eq[j - 1]) / 2));
      a.roe = roe.length ? clip(roe.reduce(function (x, y) { return x + y; }, 0) / roe.length, -0.05, 0.35) : 0.10;
      a.bv = last(f.eq); a.gB = Math.min(0.03, rf - 0.005);
    }
    a.fy = (c.ends[i] || '').slice(0, 4); a.fyEnd = c.ends[i];
    /* a 10-Q newer than the last 10-K: start from the trailing twelve months and the latest balance sheet */
    var Q = newQ(c);
    if (Q) {
      var tt = Q.ttm, bs = Q.bs || {};
      if (isn(bs.debt)) { a.debt = bs.debt; a.debtMissing = false; }
      if (isn(bs.cash)) a.cash = bs.cash;
      if (a.model === 'dcf' && tt.rev > 0) {
        a.rev0 = tt.rev;
        if (isn(tt.ebit)) a.m0 = clip(tt.ebit / tt.rev, -0.5, 0.7);
      }
      if (a.model === 'bank' && isn(bs.eq)) a.bv = bs.eq;
      a.ttm = Q.end;
    }
    if (a.model === 'dcf') {
      /* high-growth inputs: the fastest of the 3-year pace, last year, and the run-rate since the last 10-K */
      var g3 = cagr(f.rev, 3, i), gl = i > 0 && f.rev[i] > 0 && f.rev[i - 1] > 0 ? f.rev[i] / f.rev[i - 1] - 1 : null, gq = null;
      if (Q && Q.ttm.rev > 0 && f.rev[i] > 0) { var mo = (new Date(Q.end) - new Date(c.ends[i])) / 2629800000; if (mo >= 5.5) gq = Math.pow(Q.ttm.rev / f.rev[i], 12 / mo) - 1; }
      var gs = [g3, gl, gq].filter(isn), gx = gs.length ? Math.max.apply(null, gs) : 0.04;
      a.g0 = clip(gx, 0, 0.6); a.hold = a.g0 > 0.3 ? 2 : 3;
      a.gm = c.model !== 'reit' && (Math.max(isn(g3) ? g3 : 0, isn(gl) ? gl : 0) > 0.15 || gq > 0.25) ? 'growth' : 'std';
      if (a.gm === 'growth' && a.m0 > a.mT) a.mT = a.m0;   /* a fast grower's margin is usually still rising, so start from today's */
      var eqN = Q && Q.bs && isn(Q.bs.eq) ? Q.bs.eq : last(f.eq), ic = (a.debt || 0) + (eqN || 0) - (a.cash || 0);
      a.s2c = ic > 0 && a.rev0 > 0 ? clip(a.rev0 / ic, 0.8, 4) : 4;
    }
    /* bull, base and bear: the same model with growth, margin and discount rate moved together */
    var r05 = function (x) { return Math.round(x * 200) / 200; };
    if (a.model === 'dcf') {
      var gb = a.gm === 'growth' ? a.g0 : a.g1, sg = r05(clip(Math.abs(gb) * 0.3, 0.02, 0.10)), sm = r05(clip(Math.abs(a.mT) * 0.15, 0.01, 0.05));
      a.bearDg = -sg; a.bullDg = sg; a.bearDm = -sm; a.bullDm = sm; a.bearDw = 0.01; a.bullDw = -0.01;
    } else { a.bearDg = -0.02; a.bullDg = 0.02; a.bearDm = 0; a.bullDm = 0; a.bearDw = 0.005; a.bullDw = -0.005; }
    a.pBear = 0.25; a.pBase = 0.5; a.pBull = 0.25;
    return a;
  }

  /* ---------- models ---------- */
  function ke(a) { return a.rf + a.beta * a.erp; }
  function wacc(a) {
    var E = (a.price || 0) * (a.shares || 0), D = Math.max(0, a.debt || 0);
    if (!E) return ke(a);
    return E / (E + D) * ke(a) + D / (E + D) * a.kd * (1 - a.tax);
  }
  function dcf(a, o) {
    o = o || {};
    var g1 = a.g1 + (o.dg || 0), mT = a.mT + (o.dm || 0), W = (o.w != null ? o.w : wacc(a)), gT = o.gT != null ? o.gT : a.gT;
    var rows = [], rev = a.rev0, pv = 0;
    for (var t = 1; t <= 10; t++) {
      var g = t <= 5 ? g1 : g1 + (gT - g1) * (t - 5) / 5;
      var r0 = rev; rev = rev * (1 + g);
      var m = t <= 5 ? a.m0 + (mT - a.m0) * t / 5 : mT;
      var ebit = rev * m, nopat = ebit > 0 ? ebit * (1 - a.tax) : ebit;
      var cxp = a.capex > a.da + 0.01 ? a.capex + (a.da + 0.01 - a.capex) * t / 10 : a.capex;
      var da = rev * a.da, cx = rev * cxp, dn = a.nwc * (rev - r0);
      var fcff = nopat + da - cx - dn, df = Math.pow(1 + W, t);
      pv += fcff / df;
      rows.push({ t: t, g: g, rev: rev, m: m, ebit: ebit, nopat: nopat, reinv: cx - da + dn, fcff: fcff, pv: fcff / df });
    }
    var L = rows[9];
    var nopat11 = L.ebit * (1 + gT) * (1 - a.tax);
    var reinvRate = clip(gT / Math.max(a.ronic, gT + 0.001), 0, 1);
    var tvf = nopat11 * (1 - reinvRate);
    var tv = W > gT ? tvf / (W - gT) : NaN, pvtv = tv / Math.pow(1 + W, 10);
    var ev = pv + pvtv, eq = ev - (a.debt || 0) + (a.cash || 0), ps = a.shares ? eq / a.shares : NaN;
    return { rows: rows, W: W, gT: gT, pv: pv, tv: tv, pvtv: pvtv, ev: ev, eq: eq, ps: ps, tvShare: pvtv / ev };
  }
  /* high growth: starting growth holds for a few years, then fades in a straight line to the terminal rate by year 10;
     margin moves to its target by year 7; reinvestment is the new revenue divided by sales-to-capital */
  function dcfG(a, o) {
    o = o || {};
    var g0 = a.g0 + (o.dg || 0), mT = a.mT + (o.dm || 0), W = (o.w != null ? o.w : wacc(a)), gT = o.gT != null ? o.gT : a.gT;
    var H = clip(Math.round(a.hold), 0, 9), s2c = Math.max(0.2, a.s2c), rows = [], rev = a.rev0, pv = 0;
    for (var t = 1; t <= 10; t++) {
      var g = t <= H ? g0 : g0 + (gT - g0) * (t - H) / (10 - H);
      var r0 = rev; rev = rev * (1 + g);
      var m = a.m0 + (mT - a.m0) * Math.min(1, t / 7);
      var ebit = rev * m, nopat = ebit > 0 ? ebit * (1 - a.tax) : ebit;
      var reinv = (rev - r0) / s2c, fcff = nopat - reinv, df = Math.pow(1 + W, t);
      pv += fcff / df;
      rows.push({ t: t, g: g, rev: rev, m: m, ebit: ebit, nopat: nopat, reinv: reinv, fcff: fcff, pv: fcff / df });
    }
    var L = rows[9], nopat11 = L.ebit * (1 + gT) * (1 - a.tax);
    var tvf = nopat11 * (1 - clip(gT / Math.max(a.ronic, gT + 0.001), 0, 1));
    var tv = W > gT ? tvf / (W - gT) : NaN, pvtv = tv / Math.pow(1 + W, 10);
    var ev = pv + pvtv, eq = ev - (a.debt || 0) + (a.cash || 0), ps = a.shares ? eq / a.shares : NaN;
    return { rows: rows, W: W, gT: gT, pv: pv, tv: tv, pvtv: pvtv, ev: ev, eq: eq, ps: ps, tvShare: pvtv / ev };
  }
  function model(a, o) { return a.gm === 'growth' ? dcfG(a, o) : dcf(a, o); }
  function scen(a, k) {
    var d = k === 'base' ? { g: 0, m: 0, w: 0 } : { g: a[k + 'Dg'] || 0, m: a[k + 'Dm'] || 0, w: a[k + 'Dw'] || 0 }, r;
    if (a.model === 'dcf') { var W = Math.max(a.gT + 0.005, wacc(a) + d.w); r = model(a, { dg: d.g, dm: d.m, w: W }); return { ps: Math.max(0, r.ps), g: (a.gm === 'growth' ? a.g0 : a.g1) + d.g, m: a.mT + d.m, w: W }; }
    var K = Math.max(a.gB + 0.005, ke(a) + d.w); r = bank(a, { droe: d.g, k: K }); return { ps: Math.max(0, r.ps), g: a.roe + d.g, w: K };
  }
  function scenarios(a) {
    var o = { bear: scen(a, 'bear'), base: scen(a, 'base'), bull: scen(a, 'bull') };
    var pw = [a.pBear, a.pBase, a.pBull].map(function (x) { return Math.max(0, x || 0); }), tot = pw[0] + pw[1] + pw[2];
    o.tot = tot; o.wt = tot > 0 && [o.bear, o.base, o.bull].every(function (x) { return isn(x.ps); }) ? (pw[0] * o.bear.ps + pw[1] * o.base.ps + pw[2] * o.bull.ps) / tot : NaN;
    o.p = pw.map(function (x) { return tot > 0 ? x / tot : 0; });
    return o;
  }
  function bank(a, o) {
    o = o || {};
    var roe = a.roe + (o.droe || 0), K = (o.k != null ? o.k : ke(a)), g = o.g != null ? o.g : a.gB;
    var bvps = a.bv && a.shares ? a.bv / a.shares : NaN;
    var pb = K > g ? (roe - g) / (K - g) : NaN;
    return { roe: roe, K: K, g: g, bvps: bvps, pb: pb, ps: bvps * pb };
  }
  function ddm(c, a) {
    var f = c.f, i = lastIdx(f.dps); if (i < 4) return null;
    for (var j = i; j > i - 5; j--) if (!(f.dps[j] > 0)) return null;
    var ni = f.ni[i], div = f.div[i] || f.dps[i] * (c.sh || last(f.dil));
    if (!(ni > 0) || !(div / ni >= 0.4)) return null;   /* the model only suits companies that pay out much of what they earn */
    var d0 = f.dps[i], gD = clip(cagr(f.dps, 5, i) || 0, 0, 0.10), K = ke(a), gT = a.gT;
    function val(k) {
      var v = 0, d = d0; for (var t = 1; t <= 5; t++) { d *= 1 + gD; v += d / Math.pow(1 + k, t); }
      return k > gT ? v + d * (1 + gT) / (k - gT) / Math.pow(1 + k, 5) : NaN;
    }
    return { d0: d0, gD: gD, K: K, base: val(K), lo: val(K + 0.005), hi: val(Math.max(gT + 0.005, K - 0.005)), payout: div / ni };
  }
  function peers(row) {
    var cols = IX.cols, same = IX.rows.filter(function (r) { return r[0] !== row[0] && r[3] === row[3] && isn(r[4]); });
    if (same.length < 4) same = same.concat(IX.rows.filter(function (r) { return r[0] !== row[0] && r[2] === row[2] && r[3] !== row[3] && isn(r[4]); }));
    var lm = Math.log(row[4] || 1e10);
    same.sort(function (x, y) { return Math.abs(Math.log(x[4]) - lm) - Math.abs(Math.log(y[4]) - lm); });
    return same.slice(0, 8).sort(function (x, y) { return y[4] - x[4]; });
  }
  function comps(c, a, ps) {
    var f = c.f, sh = a.shares, D = a.debt || 0, C = a.cash || 0, out = [];
    var eps = last(f.eps), rev = last(f.rev), ebitda = isn(last(f.ebit)) ? last(f.ebit) + (last(f.da) || 0) : null, bv = last(f.eq);
    var Q = newQ(c);
    if (Q) {
      var tt = Q.ttm;
      if (isn(tt.eps)) eps = tt.eps;
      if (isn(tt.rev)) rev = tt.rev;
      if (isn(tt.ebit)) ebitda = tt.ebit + (isn(tt.da) ? tt.da : (last(f.da) || 0));
      if (Q.bs && isn(Q.bs.eq)) bv = Q.bs.eq;
    }
    function add(key, name, metric, toPrice) {
      var v = ps.map(function (r) { return r[IX.cols.indexOf(key)]; }).filter(function (x) { return isn(x) && x > 0 && x < 200; });
      if (v.length < 3 || !isn(metric) || metric <= 0) return;
      out.push({ key: key, name: name, n: v.length, med: median(v), lo: toPrice(q(v, 0.25)), base: toPrice(median(v)), hi: toPrice(q(v, 0.75)) });
    }
    if (c.model !== 'reit') add('pe', 'P/E', eps, function (m) { return m * eps; });
    if (a.model === 'dcf') {
      if (c.model === 'reit') add('pb', 'P/B', bv, function (m) { return m * bv / sh; });
      add('evEbitda', 'EV/EBITDA', ebitda, function (m) { return (m * ebitda - D + C) / sh; });
      add('evSales', 'EV/Sales', rev, function (m) { return (m * rev - D + C) / sh; });
    } else {
      add('pb', 'P/B', bv, function (m) { return m * bv / sh; });
    }
    return out;
  }

  /* ---------- rendering ---------- */
  function renderStatic() {
    var c = CO, r = c.row, p = c.p, f = c.f;
    var mcap = p && c.sh ? p.p * c.sh : r[4];
    var tenk = (c.filings || []).find(function (x) { return x.form === '10-K'; });
    var range = '';
    if (p && isn(p.lo) && isn(p.hi) && p.hi > p.lo) {
      var pos = clip((p.p - p.lo) / (p.hi - p.lo), 0, 1) * 100;
      range = '<div class="rng"><span class="mono">52-week range</span><div class="bar"><i style="left:' + pos.toFixed(1) + '%"></i></div><div class="ends"><span>' + usd(p.lo) + '</span><span>' + usd(p.hi) + '</span></div></div>';
    }
    $('#co').innerHTML =
      '<div class="cohd"><div><div class="mono">' + esc(r[0]) + ' &middot; ' + esc(r[2]) + '</div><h2 class="coname">' + esc(r[1]) + '</h2><p class="cosub">' + esc(r[3]) + '</p></div>' +
      '<div class="copx"><div class="mono">Last close' + (p ? ' &middot; ' + fd(p.d) : '') + '</div><div class="big num">' + (p ? usd(p.p) : '—') + '</div>' +
      '<div class="facts"><span><em>Market value</em>' + big(mcap) + '</span><span><em>Beta</em>' + (p && isn(p.b) ? p.b.toFixed(2) : '—') + '</span><span><em>Latest 10-K</em>' + (tenk ? '<a href="' + esc(tenk.url) + '" target="_blank" rel="noopener">FY' + esc((c.ends[lastIdx(f.rev)] || '').slice(0, 4)) + ' &#8599;</a>' : '—') + '</span></div>' + range + '</div></div>';
    renderFinancials(); renderFilings();
  }

  function inputRow(key, label, val, step, unit, hint) {
    var disp = unit === '%' ? (val * 100).toFixed(step < 0.001 ? 2 : 1) : unit === 'x' ? val.toFixed(2) : unit === 'n' ? String(Math.round(val)) : val;
    return '<label class="in"><span>' + label + (hint ? '<small>' + hint + '</small>' : '') + '</span><div class="box"><button type="button" data-k="' + key + '" data-d="-' + step + '">−</button>' +
      '<input data-k="' + key + '" data-u="' + unit + '" inputmode="decimal" value="' + disp + '"><i>' + (unit === '%' ? '%' : unit === 'x' ? '' : '') + '</i><button type="button" data-k="' + key + '" data-d="' + step + '">+</button></div></label>';
  }

  function renderModel() {
    var a = A, c = CO, html = '', res, auto = AUTO;
    var price = a.price;
    var lines = [];
    var G = a.model === 'dcf' && a.gm === 'growth', SC = scenarios(a);
    res = a.model === 'dcf' ? model(a) : bank(a);
    lines.push({ name: a.model === 'dcf' ? (G ? 'Cash flow, high growth' : 'Discounted cash flow') : 'Excess return (bank)', lo: Math.min(SC.bear.ps, SC.bull.ps), base: res.ps, hi: Math.max(SC.bear.ps, SC.bull.ps), main: true });
    var dd = ddm(c, a);
    if (dd && isn(dd.base) && dd.base > 0) {
      var dl = { name: 'Dividend discount', lo: Math.min(dd.lo, dd.hi), base: dd.base, hi: Math.max(dd.lo, dd.hi) };
      if (c.model === 'reit') { lines[0].main = false; dl.main = true; lines.unshift(dl); } else lines.push(dl);
    }
    var ps = peers(c.row), cp = comps(c, a, ps);
    cp.forEach(function (x) { if (isn(x.base) && x.base > 0) lines.push({ name: x.name + ' vs peers', lo: Math.min(x.lo, x.hi), base: x.base, hi: Math.max(x.lo, x.hi) }); });
    if (c.p && isn(c.p.lo)) lines.push({ name: '52-week range', lo: c.p.lo, base: null, hi: c.p.hi, ref: true });

    /* what the price implies */
    var implied = impliedTxt(c, a, res, G, price, dd);

    /* verdict */
    var v = lines[0].base, up = isn(v) && price ? v / price - 1 : null, fitV = fitNote(c, a, isn(SC.wt) && price ? SC.wt / price - 1 : up);
    $('#verdict').innerHTML =
      '<div class="vd"><div><div class="mono">' + esc(lines[0].name) + ' &middot; base case</div><div class="big num">' + (isn(v) && v > 0 ? usd(v) : 'n/a') + '</div><p>' +
      (isn(up) && v > 0 ? 'Estimated value per share is <b class="' + (up >= 0 ? 'up' : 'dn') + '">' + (up >= 0 ? sp(up) + ' above' : sp(up).replace('−', '') + ' below') + '</b> the last close of ' + usd(price) + '.' : isn(v) && v <= 0 ? 'With these assumptions the cash flows don\u2019t cover the company\u2019s debt, so there is no positive value. Try a recovery in margins or growth below.' : 'Not enough data to compare with the share price.') +
      '</p>' + (isn(SC.wt) && SC.wt > 0 && price ? '<p class="impl">Weighting bear, base and bull ' + SC.p.map(function (x) { return Math.round(x * 100); }).join('/') + ' gives <b>' + usd(SC.wt) + '</b>, ' + (SC.wt >= price ? sp(SC.wt / price - 1) + ' above' : sp(SC.wt / price - 1).replace('−', '') + ' below') + ' the last close.</p>' : '') + (implied ? '<p class="impl">' + implied + '</p>' : '') + '</div><div class="vnote">' + (a.model === 'bank' ? 'Banks and insurers are valued on what they earn on their equity rather than on cash flow, since debt is their raw material.' : c.model === 'reit' ? 'Real-estate trusts reinvest heavily and pay out most earnings, so read the cash-flow value alongside the dividend model.' : G ? 'Built for fast growers: growth starts high, holds for a few years, then fades to the long-run rate by year 10, and reinvestment grows with each new dollar of revenue.' : 'Ten years of projected free cash flow, discounted at the company’s cost of capital, plus a terminal value.') +
      (a.flagMargin ? ' <b>Its recent operating margin is near or below zero, so the model assumes it reaches 10%.</b> Adjust this below.' : '') + (fitV ? '<p class="warn"><b>Treat this value with caution.</b> ' + fitV + '</p>' : '') + '</div></div>';

    /* football field */
    renderField(lines, price);

    /* assumptions + workings */
    var f = c.f;
    if (a.model === 'dcf') {
      html += '<div class="cols2"><div class="panel"><div class="hd"><div><h3 class="sec">Assumptions</h3><p>Filled in from the company’s last three years. Change any of them.</p></div><button class="reset" id="reset" type="button">Reset</button></div>' +
        '<div class="gmr"><div class="seg gm" role="group" aria-label="Model"><button type="button" data-gm="std" class="' + (G ? '' : 'on') + '" aria-pressed="' + !G + '">Steady</button><button type="button" data-gm="growth" class="' + (G ? 'on' : '') + '" aria-pressed="' + G + '">High Growth</button></div><p class="sx">' + (AUTO.gm === 'growth' ? 'Recent growth is fast, so high growth is the default.' : 'High growth suits companies growing well above 15% a year.') + '</p></div>' +
        '<div class="ins">' +
        (G ? inputRow('g0', 'Starting growth', a.g0, 0.01, '%', 'Year 1, then fades to terminal') +
          inputRow('hold', 'Years at full growth', a.hold, 1, 'n', 'Before the fade starts') +
          inputRow('mT', 'Operating margin', a.mT, 0.005, '%', 'Reached by year 7 (now ' + pc(a.m0) + ')') +
          inputRow('s2c', 'Sales to capital', a.s2c, 0.1, 'x', 'New revenue per $1 reinvested') +
          inputRow('tax', 'Tax rate', a.tax, 0.005, '%') +
          inputRow('gT', 'Terminal growth', a.gT, 0.0025, '%', 'After year 10') +
          inputRow('ronic', 'Return on new capital', a.ronic, 0.01, '%', 'Sets terminal reinvestment')
        : inputRow('g1', 'Revenue growth', a.g1, 0.005, '%', 'Years 1–5, then fades') +
        inputRow('mT', 'Operating margin', a.mT, 0.005, '%', 'Reached by year 5 (now ' + pc(a.m0) + ')') +
        inputRow('tax', 'Tax rate', a.tax, 0.005, '%') +
        inputRow('capex', 'Capex', a.capex, 0.0025, '%', a.capex > a.da + 0.01 ? '% of revenue, eases toward depreciation' : '% of revenue') +
        inputRow('da', 'Depreciation', a.da, 0.0025, '%', '% of revenue') +
        inputRow('nwc', 'Working capital', a.nwc, 0.005, '%', '% of revenue added') +
        inputRow('gT', 'Terminal growth', a.gT, 0.0025, '%', 'After year 10') +
        inputRow('ronic', 'Return on new capital', a.ronic, 0.01, '%', 'Sets terminal reinvestment')) +
        '</div></div>' +
        '<div class="panel"><div class="hd"><div><h3 class="sec">Discount rate</h3><p>Weighted cost of capital (WACC).</p></div></div><div class="ins">' +
        inputRow('rf', 'Risk-free rate', a.rf, 0.0025, '%', RFd ? '10-year Treasury, ' + fd(RFd) : '10-year Treasury') +
        inputRow('beta', 'Beta', a.beta, 0.05, 'x', c.p && c.p.bn ? 'Two years of weekly returns' : 'Market average') +
        inputRow('erp', 'Equity risk premium', a.erp, 0.0025, '%') +
        inputRow('kd', 'Cost of debt', a.kd, 0.0025, '%', 'Before tax') +
        '</div><dl class="wacc"><dt>Cost of equity</dt><dd>' + pc(ke(a), 2) + '</dd><dt>Debt / capital</dt><dd>' + pc(a.debt / ((a.price || 0) * (a.shares || 0) + a.debt || 1)) + '</dd><dt>WACC</dt><dd class="hl">' + pc(res.W, 2) + '</dd></dl></div></div>';
      html += scenPanel(a, SC, price);
      html += '<div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Projected free cash flow</h3><p>' + (G ? 'Net reinvestment is each year’s new revenue divided by sales to capital. ' : '') + (a.ttm ? 'The twelve months to ' + fd(a.ttm) + ', from the latest 10-Q, are the base year.' : 'Fiscal year ' + esc(a.fy) + ' is the base year.') + ' Figures in billions.</p></div></div><div class="scroll"><table class="tbl proj"><thead><tr><th></th>' +
        res.rows.map(function (r) { return '<th>Y' + r.t + '</th>'; }).join('') + '</tr></thead><tbody>' +
        [['Revenue', 'rev', 1e9], ['Growth', 'g', 0], ['Operating margin', 'm', 0], ['Operating income', 'ebit', 1e9], ['After-tax operating income', 'nopat', 1e9], ['Net reinvestment', 'reinv', 1e9], ['Free cash flow', 'fcff', 1e9], ['Present value', 'pv', 1e9]].map(function (row) {
          return '<tr' + (row[1] === 'fcff' ? ' class="hl"' : '') + '><td>' + row[0] + '</td>' + res.rows.map(function (r) { var x = r[row[1]]; return '<td>' + (row[2] ? (x / row[2]).toFixed(1) : pc(x)) + '</td>'; }).join('') + '</tr>';
        }).join('') + '</tbody></table></div>' +
        '<div class="bridge">' + [['PV of 10 years', res.pv], ['PV of terminal value', res.pvtv], ['Enterprise value', res.ev], ['Less debt', -(a.debt || 0)], ['Plus cash', a.cash || 0], ['Equity value', res.eq]].map(function (x) { return '<div><span class="mono">' + x[0] + '</span><b class="num">' + big(x[1]) + '</b></div>'; }).join('') +
        '<div class="res"><span class="mono">Per share</span><b class="num">' + usd(res.ps) + '</b></div></div>' +
        (res.tvShare > 0.8 ? '<p class="warn">The terminal value is ' + pc(res.tvShare, 0) + ' of the total, so the result leans heavily on long-run assumptions.</p>' : '') + '</div>';
      /* sensitivity */
      var ws = [-0.01, -0.005, 0, 0.005, 0.01].map(function (d) { return res.W + d; }), gs = [-0.01, -0.005, 0, 0.005, 0.01].map(function (d) { return res.gT + d; });
      html += sens('Value per share: WACC against terminal growth', 'WACC', 'Terminal growth', ws, gs, function (w, g) { return w > g + 0.002 ? model(a, { w: w, gT: g }).ps : NaN; }, price);
    } else {
      html += '<div class="cols2"><div class="panel"><div class="hd"><div><h3 class="sec">Assumptions</h3><p>Return on equity is the average of the last three years.</p></div><button class="reset" id="reset" type="button">Reset</button></div><div class="ins">' +
        inputRow('roe', 'Return on equity', a.roe, 0.005, '%', 'Sustainable level') +
        inputRow('gB', 'Long-run growth', a.gB, 0.0025, '%') +
        inputRow('rf', 'Risk-free rate', a.rf, 0.0025, '%', RFd ? '10-year Treasury, ' + fd(RFd) : '') +
        inputRow('beta', 'Beta', a.beta, 0.05, 'x') +
        inputRow('erp', 'Equity risk premium', a.erp, 0.0025, '%') +
        '</div></div><div class="panel"><div class="hd"><div><h3 class="sec">Workings</h3><p>Justified price-to-book = (ROE − g) ÷ (cost of equity − g).</p></div></div>' +
        '<div class="bridge">' + [['Book value per share', usd(res.bvps)], ['Cost of equity', pc(res.K, 2)], ['Justified P/B', mx(res.pb)]].map(function (x) { return '<div><span class="mono">' + x[0] + '</span><b class="num">' + x[1] + '</b></div>'; }).join('') +
        '<div class="res"><span class="mono">Per share</span><b class="num">' + usd(res.ps) + '</b></div></div></div></div>';
      html += scenPanel(a, SC, price);
      var roes = [-0.02, -0.01, 0, 0.01, 0.02].map(function (d) { return res.roe + d; }), ks = [-0.01, -0.005, 0, 0.005, 0.01].map(function (d) { return res.K + d; });
      html += sens('Value per share: cost of equity against return on equity', 'Cost of equity', 'Return on equity', ks, roes, function (k, r) { return k > res.g + 0.002 ? bank(a, { k: k, droe: r - a.roe }).ps : NaN; }, price);
    }
    if (dd) html += '<div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Dividend discount</h3><p>Last dividend ' + usd(dd.d0) + ' a share, growing ' + pc(dd.gD) + ' a year for five years (its recent pace), then ' + pc(a.gT) + '. Payout ratio ' + pc(dd.payout, 0) + '.</p></div><div class="big num" style="font-size:28px">' + usd(dd.base) + '</div></div></div>';
    html += compsTable(ps, cp);
    $('#model').innerHTML = html;
    wire();
  }

  function scenPanel(a, SC, price) {
    var dcfm = a.model === 'dcf', gl = dcfm ? 'Revenue growth' : 'Return on equity', wl = dcfm ? 'WACC' : 'Cost of equity';
    var col = function (k, name) {
      var s = SC[k], up = price && isn(s.ps) ? s.ps / price - 1 : null, K = k.charAt(0).toUpperCase() + k.slice(1);
      var ins = k === 'base' ? '<p class="sx">Uses the assumptions above.</p>' :
        inputRow(k + 'Dg', gl + ', vs base', a[k + 'Dg'], dcfm ? 0.005 : 0.0025, '%') + (dcfm ? inputRow(k + 'Dm', 'Margin, vs base', a[k + 'Dm'], 0.005, '%') : '') + inputRow(k + 'Dw', wl + ', vs base', a[k + 'Dw'], 0.0025, '%');
      return '<div class="sc ' + k + '"><div class="sh"><span class="mono">' + name + '</span><span class="pr">' + Math.round(SC.p[['bear', 'base', 'bull'].indexOf(k)] * 100) + '% weight</span></div>' +
        '<b class="num sv">' + (isn(s.ps) ? usd(s.ps, 0) : '—') + '</b><span class="su ' + (up >= 0 ? 'up' : 'dn') + '">' + (isn(up) ? sp(up) + ' vs last close' : '') + '</span>' +
        '<dl class="sk"><dt>' + gl + '</dt><dd>' + pc(s.g) + '</dd>' + (dcfm ? '<dt>' + (a.gm === 'growth' ? 'Target margin' : 'Operating margin') + '</dt><dd>' + pc(s.m) + '</dd>' : '') + '<dt>' + wl + '</dt><dd>' + pc(s.w, 2) + '</dd></dl>' +
        '<div class="ins one">' + inputRow('p' + K, 'Probability', a['p' + K], 0.05, '%') + ins + '</div></div>';
    };
    var wt = SC.wt, up = price && isn(wt) ? wt / price - 1 : null;
    return '<div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Bear, base and bull</h3><p>The same model run three ways: ' + (dcfm ? 'growth, margin and the discount rate' : 'return on equity and the cost of equity') + ' move together. Set how likely you think each one is.</p></div>' +
      '<div class="pw"><span class="mono">Probability-weighted</span><b class="num">' + (isn(wt) ? usd(wt) : '—') + '</b><small class="' + (up >= 0 ? 'up' : 'dn') + '">' + (isn(up) ? sp(up) + ' vs ' + usd(price) : '') + '</small></div></div>' +
      '<div class="scn">' + col('bear', 'Bear') + col('base', 'Base') + col('bull', 'Bull') + '</div>' +
      (Math.abs(SC.tot - 1) > 0.001 ? '<p class="warn">The probabilities add up to ' + pc(SC.tot, 0) + ', so they are scaled to 100%.</p>' : '') + '</div>';
  }

  function impliedTxt(c, a, res, G, price, dd) {
    var implied = '';
    if (price && a.model === 'dcf' && !(c.model === 'reit' && dd)) {
      var f0 = function (dg) { return model(a, { dg: dg }).ps - price; }, lo = -0.4, hi = 1.0;
      if (isn(f0(lo)) && isn(f0(hi)) && f0(lo) < 0 && f0(hi) > 0) {
        for (var it = 0; it < 50; it++) { var mid = (lo + hi) / 2; if (f0(mid) > 0) hi = mid; else lo = mid; }
        var gi = (G ? a.g0 : a.g1) + (lo + hi) / 2, gh = cagr(c.f.rev, 3, lastIdx(c.f.rev));
        implied = 'At ' + usd(price) + ', the market is pricing in revenue growth of about <b>' + pc(gi) + ' a year</b> ' + (G ? 'for ' + Math.round(a.hold) + ' years before it fades' : 'for five years') + (isn(gh) ? ', against ' + pc(gh) + ' over the last three.' : '.');
      } else if (isn(f0(hi)) && f0(hi) < 0) implied = 'Even very fast growth doesn\u2019t reach today\u2019s price with these margins and this discount rate; the market expects more than the model allows.';
    } else if (price && a.model === 'bank' && isn(res.bvps) && res.bvps > 0) {
      var roeI = res.g + price / res.bvps * (res.K - res.g);
      implied = 'At ' + usd(price) + ', the market is pricing in a lasting return on equity of about <b>' + pc(roeI) + '</b>, against ' + pc(AUTO.roe) + ' recently.';
    }

    return implied;
  }

  function sens(title, rl, cl, rows, cols, fnv, price) {
    var h = '<div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">' + title + '</h3><p>Green is above the last close, red below. The middle cell is the base case.</p></div></div><div class="scroll"><table class="tbl sens"><thead><tr><th>' + rl + ' ↓ / ' + cl + ' →</th>' + cols.map(function (g) { return '<th>' + pc(g) + '</th>'; }).join('') + '</tr></thead><tbody>';
    rows.forEach(function (w, i) {
      h += '<tr><td>' + pc(w, 1) + '</td>' + cols.map(function (g, j) { var v = fnv(w, g); return '<td class="' + (i === 2 && j === 2 ? 'base ' : '') + (isn(v) && price ? (v >= price ? 'up' : 'dn') : '') + '">' + (isn(v) && v > 0 ? usd(v, 0) : '—') + '</td>'; }).join('') + '</tr>';
    });
    return h + '</tbody></table></div></div>';
  }

  function compsTable(ps, cp) {
    if (!ps.length) return '';
    var r = CO.row, ci = function (k) { return IX.cols.indexOf(k); }, bank = A.model === 'bank';
    var keys = bank ? [['pe', 'P/E'], ['pb', 'P/B']] : CO.model === 'reit' ? [['evEbitda', 'EV/EBITDA'], ['evSales', 'EV/Sales'], ['pb', 'P/B']] : [['pe', 'P/E'], ['evEbitda', 'EV/EBITDA'], ['evSales', 'EV/Sales']];
    var h = '<div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Peers</h3><p>Closest in size within ' + esc(r[3]) + (ps.some(function (p) { return p[3] !== r[3]; }) ? ' and the wider ' + esc(r[2]) + ' sector' : '') + '. Multiples on the latest twelve months reported.</p></div></div><div class="scroll"><table class="tbl"><thead><tr><th>Company</th><th>Market value</th>' + keys.map(function (k) { return '<th>' + k[1] + '</th>'; }).join('') + '</tr></thead><tbody>';
    h += '<tr class="me"><td>' + esc(r[1]) + '<small>' + esc(r[0]) + '</small></td><td>' + big(r[4]) + '</td>' + keys.map(function (k) { return '<td>' + mx(r[ci(k[0])]) + '</td>'; }).join('') + '</tr>';
    ps.forEach(function (p) { h += '<tr><td><a href="?t=' + encodeURIComponent(p[0]) + '" data-open="' + esc(p[0]) + '">' + esc(p[1]) + '</a><small>' + esc(p[0]) + '</small></td><td>' + big(p[4]) + '</td>' + keys.map(function (k) { return '<td>' + mx(p[ci(k[0])]) + '</td>'; }).join('') + '</tr>'; });
    h += '<tr class="med"><td>Peer median</td><td></td>' + keys.map(function (k) { return '<td>' + mx(median(ps.map(function (p) { return p[ci(k[0])]; }).filter(function (x) { return isn(x) && x > 0 && x < 200; }))) + '</td>'; }).join('') + '</tr>';
    h += '<tr class="med"><td>Implied value per share</td><td></td>' + keys.map(function (k) { var x = cp.find(function (y) { return y.key === k[0]; }); return '<td>' + (x && x.base > 0 ? usd(x.base) : '—') + '</td>'; }).join('') + '</tr>';
    return h + '</tbody></table></div></div>';
  }

  /* when the automatic model can't be trusted for this company: say why instead of showing a reading */
  function fitNote(c, a, gap) {
    var f = c.f, Q = newQ(c);
    if (a.model !== 'bank' && a.debtMissing && (last(f.intexp) || 0) > 0)
      return 'It pays interest, but its debt is missing from the filings data this site reads, so the model would count it as debt-free and overstate its value.';
    if (isn(gap) && gap > 1.5) return 'The model puts its value at more than 2.5 times the price. A gap that large usually means the model doesn\u2019t fit the company (a carmaker or lender with a finance arm, a one-off loss, or an unusual balance sheet), not a bargain.';
    if (isn(gap) && gap < -0.8) return 'The model puts its value at less than a fifth of the price. A gap that large usually means the model doesn\u2019t fit the company (very early profits, heavy reinvestment or a one-off), not that it is worthless.';
    return null;
  }

  /* ---------- research snapshot: the same model, written up as a short report ---------- */
  function renderSnap() {
    var c = CO, f = c.f, a = A, r = c.row, price = a.price, i = lastIdx(f.rev) >= 0 ? lastIdx(f.rev) : lastIdx(f.ni), Q = newQ(c);
    var bankM = a.model === 'bank', G = !bankM && a.gm === 'growth', SC = scenarios(a), res = bankM ? bank(a) : model(a), dd = ddm(c, a);
    var base = res.ps, wt = SC.wt, gap = isn(wt) && price ? wt / price - 1 : null;
    var rep = WL[r[0]], h = '', fit = fitNote(c, a, gap);
    /* a published report carries the rating; otherwise the model gives a plain reading, never dressed up as a rating */
    var sig = rep && rep.call ? ['Our rating', esc(rep.call), 'From the published report' + (rep.date ? ', ' + esc(rep.date) : '')] :
      fit ? ['Model reading', 'Not reliable here', 'See the note below'] :
      !isn(gap) ? ['Model reading', 'Not enough data', 'No rating: this company has no published report'] :
      ['Model reading', gap > 0.15 ? 'Looks undervalued' : gap < -0.15 ? 'Looks overvalued' : 'Close to fair value', 'Automatic, not a rating. ' + (gap > 0.15 ? 'The price is below the model\u2019s value' : gap < -0.15 ? 'The price is above the model\u2019s value' : 'The price is near the model\u2019s value')];
    var yr = function (j) { var e = c.ends[j] || ''; return 'FY' + (e.slice(5, 7) === '01' && +e.slice(8, 10) <= 7 ? +e.slice(0, 4) - 1 : e.slice(0, 4)); };
    /* signal strip */
    h += '<div class="snapv"><div class="call"><span class="mono">' + sig[0] + '</span><b>' + sig[1] + '</b><small>' + sig[2] + '</small></div>' +
      '<div><span class="mono">Base case</span><b class="num">' + (isn(base) && base > 0 ? usd(base, 0) : 'n/a') + '</b><small>' + (bankM ? 'Excess-return model' : G ? 'Cash-flow model, high growth' : 'Cash-flow model') + '</small></div>' +
      '<div><span class="mono">Probability-weighted</span><b class="num">' + (isn(wt) && wt > 0 ? usd(wt, 0) : 'n/a') + '</b><small>Bear, base, bull at 25/50/25</small></div>' +
      '<div><span class="mono">Gap to price</span><b class="num ' + (fit ? '' : gap >= 0 ? 'up' : 'dn') + '">' + (isn(gap) && !fit ? sp(gap) : '—') + '</b><small>Weighted value vs ' + usd(price) + '</small></div></div>' +
      (fit ? '<p class="warn snapfit"><b>' + (rep && rep.call ? 'About the automatic figures.' : 'Why there is no reading.') + '</b> ' + fit + (rep && rep.call ? ' The rating and value in the published report are the reviewed view.' : ' The figures below are shown for reference only.') + '</p>' : '');
    if (rep && rep.page) h += '<a class="snaprep" href="' + esc(rep.page) + '"><div><span class="mono">Published report' + (rep.date ? ' &middot; ' + esc(rep.date) : '') + '</span><b>' + (rep.call ? esc(rep.call) + (rep.value ? ', value ' + usd(rep.value, 0) + ' a share' : '') : 'Written research on ' + esc(r[1])) + '</b><small>The reviewed view, with sources. The automatic figures below use only reported numbers.</small></div><span class="go">Read it &rarr;</span></a>';
    /* the story in the numbers */
    var pts = [];
    var g3 = cagr(f.rev, 3, i), gl = i > 0 && f.rev[i] > 0 && f.rev[i - 1] > 0 ? f.rev[i] / f.rev[i - 1] - 1 : null;
    if (isn(f.rev[i])) {
      var t = 'Revenue was <b>' + big(f.rev[i]) + '</b> in ' + yr(i) + (isn(g3) ? ', growing ' + pc(g3) + ' a year over three years' : '') + (isn(gl) ? ' and ' + sp(gl) + ' in the latest year' : '') + '.';
      if (isn(g3) && isn(gl)) t += gl > g3 + 0.03 ? ' Growth is <b>speeding up</b>.' : gl < g3 - 0.03 ? ' Growth is <b>slowing</b>.' : ' Growth is <b>steady</b>.';
      if (Q && isn(Q.ttm.rev)) t += ' Over the twelve months to ' + fd(Q.end) + ' it was ' + big(Q.ttm.rev) + '.';
      pts.push(['Growth', t]);
    }
    if (!bankM) {
      var mN = isn(f.ebit[i]) && f.rev[i] ? f.ebit[i] / f.rev[i] : null, m3 = i >= 3 && isn(f.ebit[i - 3]) && f.rev[i - 3] ? f.ebit[i - 3] / f.rev[i - 3] : null;
      if (Q && isn(Q.ttm.ebit) && Q.ttm.rev) mN = Q.ttm.ebit / Q.ttm.rev;
      if (isn(mN)) pts.push(['Margins', 'Operating margin is <b>' + pc(mN) + '</b>' + (isn(m3) ? (mN > m3 + 0.01 ? ', up from ' : mN < m3 - 0.01 ? ', down from ' : ', about the same as ') + pc(m3) + ' three years earlier' : '') + '.' + (mN < 0.05 ? ' That is thin, so small changes in costs move profit a lot.' : mN > 0.3 ? ' That is high, a sign of pricing power.' : '')]);
      var cfo = Q && isn(Q.ttm.cfo) ? Q.ttm.cfo : f.cfo[i], cx = Q && isn(Q.ttm.capex) ? Q.ttm.capex : f.capex[i], ni = Q && isn(Q.ttm.ni) ? Q.ttm.ni : f.ni[i];
      if (isn(cfo) && isn(cx)) {
        var fcf = cfo - cx, conv = ni > 0 ? fcf / ni : null;
        pts.push(['Cash', 'Free cash flow was <b>' + big(fcf) + '</b>' + (isn(conv) ? ', ' + pc(conv, 0) + ' of net income' : '') + '. ' + (fcf < 0 ? 'It spends more than it brings in, usually because of heavy investment.' : isn(conv) && conv >= 0.9 ? 'Reported profit is backed by cash.' : isn(conv) && conv < 0.6 ? 'Cash lags reported profit: heavy investment, working capital or one-off gains.' : 'Cash broadly tracks profit.')]);
      }
      var D = a.debt || 0, C = a.cash || 0, eb = (Q && isn(Q.ttm.ebit) ? Q.ttm.ebit : f.ebit[i]) + ((Q && isn(Q.ttm.da) ? Q.ttm.da : f.da[i]) || 0);
      if (a.debtMissing) pts.push(['Balance sheet', 'Its debt is <b>not in the filings data</b> this site reads (it reports it under its own labels), so the balance sheet can\u2019t be summarised here.' + ((last(f.intexp) || 0) > 0 ? ' It paid ' + big(last(f.intexp)) + ' of interest last year, so it does have debt.' : '')]);
      else pts.push(['Balance sheet', C >= D ? 'It holds <b>more cash than debt</b> (' + big(C) + ' against ' + big(D) + ').' : 'Debt exceeds cash on hand by <b>' + big(D - C) + '</b>' + (eb > 0 ? ', about ' + ((D - C) / eb).toFixed(1) + ' times operating profit before depreciation' + ((D - C) / eb > 3 ? ', on the high side.' : ', a comfortable level.') : '.') + ' Marketable securities are not counted as cash here.']);
    } else {
      var roe = a.roe, bv0 = i >= 3 ? f.eq[i - 3] : null;
      pts.push(['Returns', 'Return on equity has averaged <b>' + pc(roe) + '</b> over three years, against a cost of equity of about ' + pc(ke(a)) + '. ' + (roe > ke(a) ? 'It earns more than investors require, which justifies a price above book value.' : 'It earns less than investors require, which argues for a price below book value.')]);
      if (isn(bv0) && bv0 > 0 && isn(f.eq[i])) pts.push(['Book value', 'Shareholders&rsquo; equity grew ' + pc(Math.pow(f.eq[i] / bv0, 1 / 3) - 1) + ' a year over three years, to ' + big(f.eq[i]) + '.']);
    }
    var s0 = i >= 3 ? f.dil[i - 3] : null, s1 = (Q && Q.dil) || f.dil[i];
    var sh = isn(s0) && isn(s1) && s0 > 0 ? s1 / s0 - 1 : null, dps = Q && isn(Q.ttm.dps) ? Q.ttm.dps : f.dps[i];
    var ret = [];
    if (dps > 0) ret.push('pays ' + usd(dps) + ' a share in dividends' + (price ? ' (a ' + pc(dps / price) + ' yield)' : ''));
    if (isn(sh)) ret.push(sh < -0.02 ? 'has cut its share count ' + pc(-sh) + ' in three years through buybacks' : sh > 0.02 ? 'has issued shares, ' + sp(sh) + ' in three years' : 'has kept its share count about flat');
    if (ret.length) pts.push(['Shareholders', 'It ' + ret.join(' and ') + '.']);
    h += '<div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">The story in the numbers</h3><p>Read straight from the 10-K and 10-Q filings.</p></div></div><dl class="story">' +
      pts.map(function (p) { return '<dt>' + p[0] + '</dt><dd>' + p[1] + '</dd>'; }).join('') + '</dl></div>';
    /* revenue and margin chart */
    h += snapChart(c);
    /* valuation */
    var dcfm = !bankM, gl2 = dcfm ? 'Revenue growth' : 'Return on equity', wl = dcfm ? 'WACC' : 'Cost of equity';
    var row = function (lab, fnv) { return '<tr><td>' + lab + '</td>' + ['bear', 'base', 'bull'].map(function (k) { return '<td>' + fnv(SC[k], k) + '</td>'; }).join('') + '</tr>'; };
    h += '<div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Valuation: bear, base and bull</h3><p>' + (dcfm ? (G ? 'Ten years of cash flow with growth starting high and fading' : 'Ten years of cash flow plus a terminal value') + ', filled in from the company&rsquo;s own history.' : 'Value from what the bank earns on its equity against what investors require.') + '</p></div><a class="pill gh sm" href="valuation.html?t=' + encodeURIComponent(r[0]) + '">Change the assumptions &rarr;</a></div>' +
      '<div class="scroll"><table class="tbl snapt"><thead><tr><th></th><th>Bear</th><th>Base</th><th>Bull</th></tr></thead><tbody>' +
      row(gl2, function (s) { return pc(s.g); }) + (dcfm ? row(G ? 'Target margin' : 'Operating margin', function (s) { return pc(s.m); }) : '') + row(wl, function (s) { return pc(s.w, 1); }) +
      row('Value per share', function (s) { return '<b>' + (isn(s.ps) && s.ps > 0 ? usd(s.ps, 0) : '—') + '</b>'; }) +
      row('Against the price', function (s) { return isn(s.ps) && price ? '<span class="' + (s.ps >= price ? 'up' : 'dn') + '">' + sp(s.ps / price - 1) + '</span>' : '—'; }) +
      '</tbody></table></div>';
    var imp = impliedTxt(c, a, res, G, price, dd);
    if (imp) h += '<p class="impl2">' + imp + '</p>';
    if (dd && isn(dd.base) && dd.base > 0) h += '<p class="impl2">A dividend model, using its last dividend growing ' + pc(dd.gD) + ' a year, gives <b>' + usd(dd.base) + '</b>.</p>';
    h += '</div>';
    var ps = peers(r), cp = comps(c, a, ps);
    h += compsTable(ps, cp);
    $('#snap').innerHTML = h;
    $$('#snap [data-open]').forEach(function (x) { x.onclick = function (e) { e.preventDefault(); open(x.getAttribute('data-open')); }; });
  }

  function snapChart(c) {
    var f = c.f, n = c.ends.length, idx = [];
    for (var i = Math.max(0, n - 6); i < n; i++) if (isn(f.rev[i]) && f.rev[i] > 0) idx.push(i);
    if (idx.length < 3) return '';
    var mx = Math.max.apply(null, idx.map(function (i) { return f.rev[i]; }));
    var mg = idx.map(function (i) { return isn(f.ebit[i]) ? f.ebit[i] / f.rev[i] : null; }), ok = mg.filter(isn);
    var lo = Math.min(0, Math.min.apply(null, ok)), hi = Math.max.apply(null, ok.concat([0.05])), k = idx.length;
    var Y = function (v) { return 30 - (v - lo) / (hi - lo || 1) * 24; };   /* the margin line sits in the top band, above the bars */   /* percent from the top of the plot */
    var pts = idx.map(function (_, j) { return isn(mg[j]) ? [(j + 0.5) / k * 100, Y(mg[j])] : null; });
    var path = pts.filter(Boolean).map(function (p, j) { return (j ? 'L' : 'M') + p[0].toFixed(2) + ' ' + p[1].toFixed(2); }).join('');
    var yr = function (e) { return e.slice(5, 7) === '01' && +e.slice(8, 10) <= 7 ? +e.slice(0, 4) - 1 : e.slice(0, 4); };
    var cols = idx.map(function (i, j) {
      return '<div class="cc"><div class="cbar"><span>' + big(f.rev[i]) + '</span><i style="height:' + (f.rev[i] / mx * 58).toFixed(1) + '%"></i></div><em>' + (isn(mg[j]) ? pc(mg[j], 0) : '') + '</em><small>' + yr(c.ends[i]) + '</small></div>';
    }).join('');
    var lastM = ok.length ? mg[mg.length - 1] : null;
    return '<div class="panel" style="margin-top:16px"><div class="hd"><div><h3 class="sec">Revenue and operating margin</h3><p>Bars are revenue by fiscal year; the line and the figures under each bar are operating margin.</p></div><div class="lgd"><span><i class="b"></i>Revenue</span>' + (isn(lastM) ? '<span><i class="l"></i>Operating margin</span>' : '') + '</div></div>' +
      '<div class="snapc"><div class="cplot">' + cols + (path ? '<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><path d="' + path + '" vector-effect="non-scaling-stroke"/></svg>' + pts.map(function (p) { return p ? '<b style="left:' + p[0].toFixed(2) + '%;top:calc((100% - 44px) * ' + (p[1] / 100).toFixed(4) + ')"></b>' : ''; }).join('') : '') + '</div></div></div>';
  }

  function renderField(lines, price) {
    var vals = [];
    lines.forEach(function (l) { [l.lo, l.base, l.hi].forEach(function (v) { if (isn(v) && v > 0) vals.push(v); }); });
    if (isn(price)) vals.push(price);
    if (!vals.length) { $('#field').innerHTML = ''; return; }
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals), pad = (hi - lo) * 0.08 || hi * 0.1;
    lo = Math.max(0, lo - pad); hi += pad;
    var X = function (v) { return ((v - lo) / (hi - lo) * 100).toFixed(2) + '%'; };
    var h = '<div class="ff">';
    lines.forEach(function (l) {
      if (!(isn(l.lo) && isn(l.hi)) || l.hi <= 0) return;
      var a = Math.max(lo, Math.min(l.lo, l.hi)), b = Math.max(l.lo, l.hi);
      h += '<div class="ffr' + (l.main ? ' main' : '') + (l.ref ? ' ref' : '') + '"><span class="lab">' + esc(l.name) + '</span><div class="trk"><i class="rg" style="left:' + X(a) + ';width:calc(' + X(b) + ' - ' + X(a) + ')"></i>' +
        (isn(l.base) && l.base > 0 ? '<b class="bs" style="left:' + X(l.base) + '"></b>' : '') + '<em style="left:' + X(a) + '">' + usd(a, 0) + '</em><em class="r" style="left:' + X(b) + '">' + usd(b, 0) + '</em></div></div>';
    });
    if (isn(price)) h += '<div class="ffo"><div class="pxl' + ((price - lo) / (hi - lo) > 0.6 ? ' r' : '') + '" style="left:' + X(price) + '"><span>Last close ' + usd(price) + '</span></div></div>';
    h += '</div>';
    $('#field').innerHTML = '<div class="panel"><div class="hd"><div><h3 class="sec">Value per share, by method</h3><p>Bars show the low-to-high range for each method; the dot is the base case. The line is today’s price.</p></div></div>' + h + '</div>';
  }

  var FINMODE = 'a';
  function filingFor(end, form) {
    var best = null;
    (CO.filings || []).forEach(function (x) { if (x.per && (!form || x.form === form) && Math.abs((new Date(x.per) - new Date(end)) / 864e5) <= 7) best = best || x; });
    return best;
  }
  function finToggle(qok) {
    return qok ? '<div class="seg" role="tablist"><button type="button" data-fm="a" class="' + (FINMODE === 'a' ? 'on' : '') + '">Annual · 10-K</button><button type="button" data-fm="q" class="' + (FINMODE === 'q' ? 'on' : '') + '">Quarterly · 10-Q</button></div>' : '';
  }
  function wireFin() { $$('#fin [data-fm]').forEach(function (b) { b.onclick = function () { FINMODE = b.getAttribute('data-fm'); renderFinancials(); }; }); }
  function renderQuarterly() {
    var c = CO, Q = c.qs, f = Q.f, n = Q.ends.length, k = Math.min(8, n), idx = [], bank = c.model === 'bank';
    for (var i = n - k; i < n; i++) idx.push(i);
    var yo = function (key, i) { return i >= 4 && isn(f[key][i]) && f[key][i - 4] ? (f[key][i] - f[key][i - 4]) / Math.abs(f[key][i - 4]) : null; };
    var rows = [
      ['Revenue', function (i) { return big(f.rev[i]); }],
      ['Growth vs year-ago quarter', function (i) { var v = yo('rev', i); return isn(v) ? '<span class="' + (v >= 0 ? 'up' : 'dn') + '">' + sp(v) + '</span>' : '—'; }]
    ];
    if (!bank) rows.push(['Gross margin', function (i) { return f.gp[i] && f.rev[i] ? pc(f.gp[i] / f.rev[i]) : '—'; }], ['Operating margin', function (i) { return isn(f.ebit[i]) && f.rev[i] ? pc(f.ebit[i] / f.rev[i]) : '—'; }]);
    rows.push(['Net income', function (i) { return big(f.ni[i]); }], ['Diluted EPS', function (i) { return usd(f.eps[i]); }],
      ['EPS vs year-ago quarter', function (i) { var v = yo('eps', i); return isn(v) && f.eps[i - 4] > 0 ? '<span class="' + (v >= 0 ? 'up' : 'dn') + '">' + sp(v) + '</span>' : '—'; }]);
    if (!bank) rows.push(['Operating cash flow', function (i) { return big(f.cfo[i]); }], ['Free cash flow', function (i) { return isn(f.cfo[i]) && isn(f.capex[i]) ? big(f.cfo[i] - f.capex[i]) : '—'; }],
      ['Cash and investments', function (i) { return big(f.cash[i]); }], ['Net debt', function (i) { return isn(f.debt[i]) ? big(f.debt[i] - (f.cash[i] || 0)) : '—'; }]);
    var L = n - 1, lr = yo('rev', L), le = yo('eps', L), om = isn(f.ebit[L]) && f.rev[L] ? f.ebit[L] / f.rev[L] : null, om0 = L >= 4 && isn(f.ebit[L - 4]) && f.rev[L - 4] ? f.ebit[L - 4] / f.rev[L - 4] : null;
    var sum = 'In ' + Q.lab[L] + ' (the quarter to ' + fd(Q.ends[L]) + ') revenue was <b>' + big(f.rev[L]) + '</b>' + (isn(lr) ? ', ' + (lr >= 0 ? 'up ' : 'down ') + pc(Math.abs(lr)) + ' from a year earlier' : '') +
      (isn(f.eps[L]) ? '; diluted EPS was <b>' + usd(f.eps[L]) + '</b>' + (isn(le) && f.eps[L - 4] > 0 ? ' (' + sp(le) + ')' : '') : '') +
      (!bank && isn(om) ? '; operating margin ' + pc(om) + (isn(om0) ? ' against ' + pc(om0) + ' a year ago' : '') : '') + '.';
    var fq = filingFor(Q.ends[L]);
    var bars = (function () {
      var v = idx.map(function (i) { return f.rev[i]; }), mxv = Math.max.apply(null, v.filter(isn).concat([1]));
      return '<div class="qbars">' + idx.map(function (i) { var h = isn(f.rev[i]) && f.rev[i] > 0 ? f.rev[i] / mxv * 100 : 0, g = yo('rev', i); return '<div><i style="height:' + h.toFixed(1) + '%"></i><b>' + big(f.rev[i]) + '</b><span>' + esc(Q.lab[i]) + '</span><small>' + esc(Q.lab[i].replace(' FY', '·')) + '</small>' + (isn(g) ? '<em class="' + (g >= 0 ? 'up' : 'dn') + '">' + sp(g, 0) + '</em>' : '<em>&nbsp;</em>') + '</div>'; }).join('') + '</div>';
    })();
    $('#fin').innerHTML = '<div class="panel"><div class="hd"><div><h3 class="sec">Quarter by quarter</h3><p>Each quarter on its own, from the company’s 10-Q filings. The fourth quarter is the 10-K year minus the first nine months, and cash flow is worked out from the year-to-date figures the filings report.</p></div>' + finToggle(true) + '</div>' +
      (Q.warn ? '<p class="qwarn">These quarters don’t add up exactly to the company’s 10-K, usually because of a restatement, a spin-off or a change in how revenue is reported. Use the linked filings for exact figures.</p>' : '') +
      '<p class="qsum">' + sum + (fq ? ' <a href="' + esc(fq.url) + '" target="_blank" rel="noopener">Read the ' + esc(fq.form) + ' &#8599;</a>' : '') + '</p>' + bars +
      '<div class="scroll"><table class="tbl fin"><thead><tr><th>Fiscal quarter</th>' +
      idx.map(function (i) { var x = filingFor(Q.ends[i]); return '<th>' + (x ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener" title="' + esc(x.form) + ' filed ' + fd(x.date) + '">' + esc(Q.lab[i]) + '</a>' : esc(Q.lab[i])) + '<small>' + mon(Q.ends[i]) + '</small></th>'; }).join('') + '</tr></thead><tbody>' +
      rows.map(function (r) { return '<tr><td>' + r[0] + '</td>' + idx.map(function (i) { return '<td>' + r[1](i) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div></div>';
    wireFin();
  }

  function renderFinancials() {
    var qok = CO.qs && CO.qs.ends && CO.qs.ends.length >= 2;
    if (FINMODE === 'q' && qok) return renderQuarterly();
    var c = CO, f = c.f, n = c.ends.length, k = Math.min(5, n), idx = [], Q = newQ(c);
    for (var i = n - k; i < n; i++) idx.push(i);
    if (Q) {                       /* add the trailing twelve months as one more column */
      var g = {};
      Object.keys(f).forEach(function (key) { g[key] = f[key].slice(); g[key][n] = isn(Q.ttm[key]) ? Q.ttm[key] : null; });
      ['debt', 'cash', 'eq', 'debtcur', 'assets', 'ca', 'cl'].forEach(function (key) { if (g[key]) g[key][n] = Q.bs && isn(Q.bs[key]) ? Q.bs[key] : null; });
      f = g; idx.push(n);
    }
    var bank = c.model === 'bank';
    var rows = [
      ['Revenue', function (i) { return big(f.rev[i]); }],
      ['Revenue growth', function (i) { return i > 0 && i < n && f.rev[i] && f.rev[i - 1] ? sp(f.rev[i] / f.rev[i - 1] - 1) : '—'; }],
    ];
    if (!bank) rows.push(['Gross margin', function (i) { return f.gp[i] && f.rev[i] ? pc(f.gp[i] / f.rev[i]) : '—'; }], ['Operating margin', function (i) { return isn(f.ebit[i]) && f.rev[i] ? pc(f.ebit[i] / f.rev[i]) : '—'; }]);
    rows.push(['Net income', function (i) { return big(f.ni[i]); }], ['Diluted EPS', function (i) { return usd(f.eps[i]); }]);
    if (!bank) rows.push(['Free cash flow', function (i) { return isn(f.cfo[i]) && isn(f.capex[i]) ? big(f.cfo[i] - f.capex[i]) : '—'; }], ['Net debt', function (i) { return isn(f.debt[i]) ? big(f.debt[i] - (f.cash[i] || 0)) : '—'; }]);
    rows.push(['Return on equity', function (i) { return i > 0 && isn(f.ni[i]) && f.eq[i] > 0 && f.eq[i - 1] > 0 ? pc(f.ni[i] / ((f.eq[i] + f.eq[i - 1]) / 2)) : '—'; }], ['Dividend per share', function (i) { return f.dps[i] ? usd(f.dps[i]) : '—'; }]);
    $('#fin').innerHTML = '<div class="panel"><div class="hd"><div><h3 class="sec">Five years of results</h3><p>From the company’s 10-K annual reports on SEC EDGAR' + (Q ? ', plus the twelve months to ' + fd(Q.end) + ' from its latest 10-Q. Balance-sheet figures in that column are as of the quarter end.' : '.') + '</p></div>' + finToggle(qok) + '</div><div class="scroll"><table class="tbl fin' + (Q ? ' ttm' : '') + '"><thead><tr><th>Fiscal year</th>' +
      idx.map(function (i) { return '<th>' + (i === n ? 'TTM ' + mon(Q.end) : 'FY' + c.ends[i].slice(0, 4)) + '</th>'; }).join('') + '</tr></thead><tbody>' +
      rows.map(function (r) { return '<tr><td>' + r[0] + '</td>' + idx.map(function (i) { return '<td>' + r[1](i) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div></div>';
    wireFin();
  }

  function renderFilings() {
    var fl = CO.filings || [];
    $('#filings').innerHTML = fl.length ? '<div class="eyebrow mono" style="margin-top:40px">Filings</div><div class="fil">' + fl.map(function (x) { var lab = ''; if (x.per && CO.qs) { var j = CO.qs.ends.findIndex(function (e) { return Math.abs((new Date(e) - new Date(x.per)) / 864e5) <= 7; }); if (j >= 0) lab = x.form === '10-K' ? 'FY' + CO.qs.lab[j].slice(-2) : CO.qs.lab[j]; } if (!lab && x.per) lab = 'Period to ' + mon(x.per); return '<a href="' + esc(x.url) + '" target="_blank" rel="noopener"><b>' + esc(x.form) + (lab ? ' <small>' + esc(lab) + '</small>' : '') + '</b><span>Filed ' + fd(x.date) + '</span><i>&#8599;</i></a>'; }).join('') + '</div>' : '';
  }

  /* ---------- inputs ---------- */
  function tidy() {
    if (isn(A.hold)) A.hold = clip(Math.round(A.hold), 0, 9);
    if (isn(A.s2c)) A.s2c = Math.max(0.2, A.s2c);
    ['pBear', 'pBase', 'pBull'].forEach(function (k) { if (isn(A[k])) A[k] = clip(A[k], 0, 1); });
  }
  function wire() {
    $$('#model input[data-k]').forEach(function (el) {
      el.addEventListener('change', function () {
        var k = el.getAttribute('data-k'), u = el.getAttribute('data-u'), v = parseFloat(el.value.replace(/[^0-9.\-]/g, ''));
        if (!isn(v)) return renderModel();
        A[k] = u === '%' ? v / 100 : v; tidy(); renderModel();
      });
    });
    $$('#model button[data-k]').forEach(function (b) {
      b.onclick = function () { var k = b.getAttribute('data-k'); A[k] = +(A[k] + parseFloat(b.getAttribute('data-d'))).toFixed(5); tidy(); renderModel(); };
    });
    $$('#model [data-gm]').forEach(function (b) { b.onclick = function () { A.gm = b.getAttribute('data-gm'); renderModel(); }; });
    $$('#model [data-open]').forEach(function (a) { a.onclick = function (e) { e.preventDefault(); open(a.getAttribute('data-open')); }; });
    var r = $('#reset'); if (r) r.onclick = function () { A = JSON.parse(JSON.stringify(AUTO)); renderModel(); };
  }
})();
