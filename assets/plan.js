/* LDB Finance: financial planner. Plain JavaScript, no libraries.
   A yearly cash-flow model of one household from today to the end of the plan, run 1,000 times with random
   market returns. Everything is calculated in nominal dollars and shown in today's dollars. */
(function () {
  'use strict';
  var d = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var css = function (v) { return getComputedStyle(d).getPropertyValue(v).trim(); };

  /* ---------- formatting ---------- */
  function cm(v, dp) { return v.toLocaleString('en-US', { minimumFractionDigits: dp || 0, maximumFractionDigits: dp || 0 }); }
  function usd(v) { var a = Math.abs(v); return (v < 0 ? '−' : '') + '$' + (a >= 1e6 ? cm(a / 1e6, 2) + 'M' : cm(a, 0)); }
  function kusd(v) { var a = Math.abs(v); return (v < 0 ? '−' : '') + '$' + (a >= 1e6 ? cm(a / 1e6, 1) + 'M' : a >= 1e3 ? cm(a / 1e3, 0) + 'k' : cm(a, 0)); }
  function pc(v, dp) { return cm(v * 100, dp == null ? 0 : dp) + '%'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* ---------- the household ---------- */
  var P = {
    age: 30, ret: 65, end: 95,
    inc: 85000, g: 0.03, tax: 0.22,
    spend: 60000, retPct: 0.80, retTax: 0.12,
    cash: 15000, inv: 40000,
    ss: 24000, ssAge: 67,
    eq0: 0.90, eq1: 0.50,
    infl: 0.025, rs: 0.075, vs: 0.16, rb: 0.045, vb: 0.06, rc: 0.03,
    debts: [{ n: 'Student loan', b: 28000, r: 0.055, p: 300 }, { n: 'Car loan', b: 12000, r: 0.07, p: 350 }],
    goals: [{ n: 'Home down payment', a: 50000, at: 36 }]
  };
  var N = 1000;

  /* ---------- random numbers: seeded, so the same inputs always give the same answer ---------- */
  function rng(seed) { var s = seed >>> 0; return function () { s = (s + 0x6D2B79F5) >>> 0; var t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function gauss(R) { var u = 0, v = 0; while (u === 0) u = R(); v = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

  /* ---------- one life ---------- */
  function life(o, draws, rec) {
    var yrs = o.end - o.age, cash = o.cash, port = o.inv, debts = o.debts.map(function (x) { return { n: x.n, b: x.b, r: x.r, p: x.p, int: 0, off: x.b > 0 ? null : o.age }; });
    var fail = null, rows = [], nw = [], wd0 = null, short = 0;
    for (var t = 0; t <= yrs; t++) {
      var a = o.age + t, f = Math.pow(1 + o.infl, t), working = a < o.ret;
      var eq = working ? o.eq0 + (o.eq1 - o.eq0) * Math.min(1, t / Math.max(1, o.ret - o.age)) : o.eq1;
      var gross = 0, tax = 0, spend = 0, debtPay = 0, goal = 0, ss = 0, wd = 0, save = 0;
      debts.forEach(function (x) {
        if (x.b <= 0) return;
        var i = x.b * x.r, pay = Math.min(x.p * 12, x.b + i);
        x.int += i; x.b = x.b + i - pay; debtPay += pay;
        if (x.b <= 0.5) { x.b = 0; x.off = a; }
      });
      o.goals.forEach(function (gl) { if (gl.at === a) goal += gl.a * f; });
      if (working) {
        gross = o.inc * Math.pow(1 + o.g, t); tax = gross * o.tax; spend = o.spend * f;
        save = gross - tax - spend - debtPay - goal;
      } else {
        ss = a >= o.ssAge ? o.ss * f : 0;
        spend = o.spend * o.retPct * f;
        var need = spend + debtPay + goal - ss;
        wd = need > 0 ? need / (1 - o.retTax) : need;
        tax = need > 0 ? wd - need : 0;
        if (wd0 === null && port + cash > 0) wd0 = wd / (port + cash);
        save = -wd;
      }
      /* the year's money: surplus tops up the emergency fund (six months of spending), the rest is invested */
      var target = (working ? o.spend : o.spend * o.retPct) * f / 2;
      if (save >= 0) { var top = Math.max(0, Math.min(save, target - cash)); cash += top; port += save - top; }
      else { var need2 = -save, fromCash = Math.min(cash, need2); cash -= fromCash; port -= need2 - fromCash; }
      if (port < 0 && working) { short += -port / f; port = 0; }   /* before retirement a shortfall means a goal is not fully paid for, not that the plan has failed */
      if (port < 0 && fail === null) { fail = a; }
      if (fail !== null) { port = Math.min(port, 0); }
      var r = eq * draws[t][0] + (1 - eq) * draws[t][1];
      if (port > 0) port *= 1 + r;
      cash *= 1 + o.rc;
      var debt = debts.reduce(function (s, x) { return s + x.b; }, 0);
      nw.push((port + cash - debt) / f);
      if (rec) rows.push({ a: a, gross: gross / f, tax: tax / f, spend: spend / f, debt: debtPay / f, goal: goal / f, ss: ss / f, save: save / f, port: port / f, cash: cash / f, eq: eq, nw: (port + cash - debt) / f });
    }
    return { fail: fail, nw: nw, rows: rows, debts: debts, wd0: wd0, short: short };
  }
  var DC = {}, DKEY = '';
  function draws(o, seed, shock) {
    var key = [o.age, o.end, o.rs, o.vs, o.rb, o.vb, shock ? o.ret : 0].join('|');
    if (key !== DKEY && !shock) { DC = {}; DKEY = key; }
    var ck = (shock ? 's' + o.ret + ':' : '') + seed;
    if (!shock && DC[ck]) return DC[ck];
    var R = rng(seed), yrs = o.end - o.age, out = [], rho = 0.1;
    for (var t = 0; t <= yrs; t++) {
      var z1 = gauss(R), z2 = rho * z1 + Math.sqrt(1 - rho * rho) * gauss(R);
      var s = o.rs + o.vs * z1, b = o.rb + o.vb * z2;
      if (shock && o.age + t === o.ret) { s = -0.30; b = 0.02; }
      out.push([s, b]);
    }
    if (!shock) DC[ck] = out;
    return out;
  }
  function sim(o, shock) {
    var paths = [], fails = 0, ages = [], wd0 = [], shorts = 0;
    for (var i = 0; i < N; i++) { var L = life(o, draws(o, 1000 + i, shock)); paths.push(L.nw); if (L.fail !== null) { fails++; ages.push(L.fail); } else ages.push(o.end + 1); if (L.wd0 != null) wd0.push(L.wd0); if (L.short > 1) shorts++; }
    var yrs = o.end - o.age, pct = function (arr, q) { var s = arr.slice().sort(function (a, b) { return a - b; }); return s[Math.min(s.length - 1, Math.max(0, Math.floor(q * (s.length - 1))))]; };
    var p10 = [], p50 = [], p90 = [];
    for (var t = 0; t <= yrs; t++) { var col = paths.map(function (p) { return p[t]; }); p10.push(pct(col, 0.1)); p50.push(pct(col, 0.5)); p90.push(pct(col, 0.9)); }
    return { ok: 1 - fails / N, p10: p10, p50: p50, p90: p90, age10: pct(ages, 0.1), wd0: wd0.length ? pct(wd0, 0.5) : null, short: shorts / N };
  }
  function avgPath(o) {                 // the same household with average returns every year, for the cash-flow table
    var yrs = o.end - o.age, dr = []; for (var t = 0; t <= yrs; t++) dr.push([o.rs, o.rb]);
    return life(o, dr, true);
  }
  function clone(o, ch) { var c = JSON.parse(JSON.stringify(o)); for (var k in ch) c[k] = ch[k]; return c; }

  /* ---------- inputs ---------- */
  var FIELDS = [
    ['You', [['age', 'Age today', '', 1, 'yr'], ['ret', 'Retire at', '', 1, 'yr'], ['end', 'Plan to age', 'Longer is safer', 1, 'yr']]],
    ['Income', [['inc', 'Salary', 'Before tax, a year', 1000, '$'], ['g', 'Raises', 'A year, on average', 0.005, '%'], ['tax', 'Tax rate', 'All taxes, as a share of pay', 0.01, '%']]],
    ['Spending', [['spend', 'Spending', 'A year, not counting debt payments', 1000, '$'], ['retPct', 'In retirement', 'Share of today’s spending', 0.05, '%'], ['retTax', 'Tax on withdrawals', 'In retirement', 0.01, '%']]],
    ['Savings', [['cash', 'Cash', 'Emergency fund, savings account', 1000, '$'], ['inv', 'Investments', '401(k), IRA and brokerage', 1000, '$']]],
    ['Social Security', [['ss', 'Benefit', 'A year, in today’s dollars', 1000, '$'], ['ssAge', 'Starting at', '62 to 70', 1, 'yr']]],
    ['Investing', [['eq0', 'Stocks today', 'The rest in bonds', 0.05, '%'], ['eq1', 'Stocks at retirement', 'Shifts gradually', 0.05, '%']]]];
  var ASSUME = [['infl', 'Inflation', '', 0.0025, '%'], ['rs', 'Stock return', 'Average, a year', 0.0025, '%'], ['vs', 'Stock volatility', '', 0.01, '%'], ['rb', 'Bond return', 'Average, a year', 0.0025, '%'], ['vb', 'Bond volatility', '', 0.005, '%'], ['rc', 'Cash return', '', 0.0025, '%']];
  var LIM = { age: [16, 80], ret: [30, 80], end: [70, 110], g: [-0.05, 0.15], tax: [0, 0.6], retPct: [0.3, 1.5], retTax: [0, 0.5], ssAge: [62, 70], eq0: [0, 1], eq1: [0, 1], infl: [-0.01, 0.12], rs: [-0.05, 0.2], vs: [0, 0.5], rb: [-0.05, 0.15], vb: [0, 0.3], rc: [-0.02, 0.1] };
  function shown(k, u) { var v = P[k]; if (u !== '%') return cm(v, 0); var x = Math.round(v * 10000) / 100; return String(x); }
  function box(k, label, hint, step, u) {
    return '<label class="in"><span>' + label + (hint ? '<small>' + hint + '</small>' : '') + '</span><div class="box"><button type="button" data-k="' + k + '" data-s="' + (-step) + '">−</button><input data-k="' + k + '" data-u="' + u + '" inputmode="decimal" value="' + shown(k, u) + '"><i>' + (u === '$' ? '$' : u) + '</i><button type="button" data-k="' + k + '" data-s="' + step + '">+</button></div></label>';
  }
  function clamp(k, v) { var l = LIM[k]; if (l) v = Math.min(l[1], Math.max(l[0], v)); else v = Math.max(0, v); if (k === 'ret') v = Math.max(P.age + 1, v); if (k === 'end') v = Math.max(P.ret + 1, v); return v; }
  function inputs() {
    var el = $('#plIn'); if (!el) return;
    el.innerHTML = FIELDS.map(function (g) { return '<div class="plg"><h4 class="mono">' + g[0] + '</h4><div class="ins">' + g[1].map(function (f) { return box.apply(null, f); }).join('') + '</div></div>'; }).join('');
    var as = $('#plAs'); if (as) as.innerHTML = '<div class="ins three">' + ASSUME.map(function (f) { return box.apply(null, f); }).join('') + '</div>';
    $$('#plIn button[data-k], #plAs button[data-k]').forEach(function (b) { b.onclick = function () { var k = b.getAttribute('data-k'); P[k] = clamp(k, +(P[k] + +b.getAttribute('data-s')).toFixed(6)); refresh(); }; });
    $$('#plIn input[data-k], #plAs input[data-k]').forEach(function (inp) {
      inp.onchange = function () { var k = inp.getAttribute('data-k'), v = parseFloat(inp.value.replace(/[^0-9.\-]/g, '')); if (!isNaN(v)) { if (inp.getAttribute('data-u') === '%') v /= 100; P[k] = clamp(k, v); } refresh(); };
    });
  }
  function lists() {
    var el = $('#plDebt'); if (el) {
      el.innerHTML = '<table class="tbl pf"><thead><tr><th>Debt</th><th>Balance</th><th>Rate</th><th>Monthly</th><th></th></tr></thead><tbody>' + P.debts.map(function (x, i) {
        return '<tr data-i="' + i + '"><td><input class="cell nm" data-f="n" value="' + esc(x.n) + '" aria-label="Debt name"></td><td><input class="cell" data-f="b" inputmode="decimal" value="' + cm(x.b) + '" aria-label="Balance"></td><td><input class="cell" data-f="r" inputmode="decimal" value="' + (x.r * 100).toFixed(2) + '" aria-label="Interest rate, percent"><i>%</i></td><td><input class="cell" data-f="p" inputmode="decimal" value="' + cm(x.p) + '" aria-label="Monthly payment"></td><td><button type="button" class="x" data-del="' + i + '" aria-label="Remove">×</button></td></tr>';
      }).join('') + '</tbody></table>';
      wireList(el, P.debts);
    }
    var gl = $('#plGoal'); if (gl) {
      gl.innerHTML = '<table class="tbl pf"><thead><tr><th>Goal</th><th>Cost today</th><th>At age</th><th></th></tr></thead><tbody>' + P.goals.map(function (x, i) {
        return '<tr data-i="' + i + '"><td><input class="cell nm" data-f="n" value="' + esc(x.n) + '" aria-label="Goal"></td><td><input class="cell" data-f="a" inputmode="decimal" value="' + cm(x.a) + '" aria-label="Cost in today’s dollars"></td><td><input class="cell" data-f="at" inputmode="decimal" value="' + x.at + '" aria-label="Age"></td><td><button type="button" class="x" data-del="' + i + '" aria-label="Remove">×</button></td></tr>';
      }).join('') + '</tbody></table>';
      wireList(gl, P.goals);
    }
  }
  function wireList(el, arr) {
    $$('.cell', el).forEach(function (inp) {
      inp.onchange = function () {
        var i = +inp.closest('tr').getAttribute('data-i'), f = inp.getAttribute('data-f');
        if (f === 'n') arr[i].n = inp.value.slice(0, 40) || 'Item';
        else { var v = parseFloat(inp.value.replace(/[^0-9.\-]/g, '')); if (!isNaN(v)) arr[i][f] = f === 'r' ? Math.max(0, Math.min(0.4, v / 100)) : f === 'at' ? Math.round(Math.max(P.age, Math.min(P.end, v))) : Math.max(0, v); }
        refresh();
      };
    });
    $$('button[data-del]', el).forEach(function (x) { x.onclick = function () { arr.splice(+x.getAttribute('data-del'), 1); refresh(); }; });
  }

  /* ---------- results ---------- */
  var timer;
  function refresh() { inputs(); lists(); clearTimeout(timer); timer = setTimeout(run, 30); }
  function run() {
    var base = sim(P), avg = avgPath(P), retRow = avg.rows[Math.max(0, Math.min(avg.rows.length - 1, P.ret - P.age - 1))];
    var tone = base.ok >= 0.85 ? 'up' : base.ok >= 0.7 ? '' : 'dn';
    var monthsCash = P.cash / (P.spend / 12), ssShare = P.ss / (P.spend * P.retPct);
    $('#plSum').innerHTML = '<div class="kv four">' +
      '<div><b class="' + tone + '">' + pc(base.ok) + '</b><span>Chance the money lasts to ' + P.end + '</span></div>' +
      '<div><b>' + usd(base.p50[P.ret - P.age]) + '</b><span>Middle outcome at ' + P.ret + ', in today&rsquo;s dollars</span></div>' +
      '<div><b>' + (base.age10 > P.end ? P.end + '+' : base.age10) + '</b><span>Age the money lasts to, worst 10% of markets</span></div>' +
      '<div><b>' + (base.wd0 != null ? pc(base.wd0, 1) : '&ndash;') + '</b><span>First-year withdrawal rate</span></div>' +
      '<div><b class="' + (monthsCash >= 6 ? 'up' : monthsCash >= 3 ? '' : 'dn') + '">' + cm(monthsCash, 1) + '</b><span>Months of spending in cash</span></div>' +
      '<div><b>' + pc(Math.min(1, ssShare)) + '</b><span>Of retirement spending covered by Social Security</span></div>' +
      '<div><b>' + usd(Math.max(0, retRow ? retRow.save : 0) / 12) + '</b><span>Saving a month, the year before retiring</span></div>' +
      '<div><b>' + pc(P.eq0) + ' &rarr; ' + pc(P.eq1) + '</b><span>Stocks, today to retirement</span></div></div>';
    $('#plWarn').innerHTML = base.short > 0.005 ? '<p class="plwarn">In ' + pc(base.short) + ' of markets, savings were not enough to pay for every goal on time. The model pays what it can and carries on; consider a later date or a smaller amount.</p>' : '';
    fan(base);
    flows(avg);
    debts(avg);
    scenarios(base);
  }
  function fan(s) {
    var el = $('#plFan'); if (!el) return;
    var W = el.clientWidth || 800, H = el.clientHeight || 320, L = 62, R = 16, T = 14, B = 32;
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    var n = s.p50.length, hi = Math.max.apply(null, s.p90) * 1.05, lo = Math.min(0, Math.min.apply(null, s.p10));
    var X = function (i) { return L + i / (n - 1) * (W - L - R); }, Y = function (v) { return T + (1 - (v - lo) / (hi - lo)) * (H - T - B); };
    var line = css('--line'), acc = css('--acc'), t3 = css('--t3'), out = '';
    var step = Math.pow(10, Math.floor(Math.log10((hi - lo) / 4))), e = (hi - lo) / 4 / step; step *= e >= 5 ? 10 : e >= 2 ? 5 : e >= 1 ? 2 : 1;
    for (var v = Math.ceil(lo / step) * step; v <= hi; v += step) out += '<path d="M' + L + ' ' + Y(v).toFixed(1) + 'H' + (W - R) + '" stroke="' + line + '"/><text x="' + (L - 8) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end">' + kusd(v) + '</text>';
    for (var a = Math.ceil(P.age / 10) * 10; a <= P.end; a += 10) out += '<text x="' + X(a - P.age).toFixed(1) + '" y="' + (H - 10) + '" text-anchor="middle">' + a + '</text>';
    var up = s.p90.map(function (v, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1); }).join(''), dn = s.p10.map(function (v, i) { return 'L' + X(n - 1 - i).toFixed(1) + ' ' + Y(s.p10[n - 1 - i]).toFixed(1); }).join('');
    out += '<path d="' + up + dn + 'Z" fill="' + acc + '" opacity=".14"/>';
    out += '<path d="' + s.p10.map(function (v, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1); }).join('') + '" fill="none" stroke="' + t3 + '" stroke-width="1.2" stroke-dasharray="3 4"/>';
    out += '<path d="' + s.p50.map(function (v, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1); }).join('') + '" fill="none" stroke="' + acc + '" stroke-width="2.4"/>';
    var rx = X(P.ret - P.age); out += '<path d="M' + rx.toFixed(1) + ' ' + T + 'V' + (H - B) + '" stroke="' + css('--ink') + '" stroke-dasharray="2 4" opacity=".6"/><text x="' + (rx + 6).toFixed(1) + '" y="' + (T + 12) + '">Retire at ' + P.ret + '</text>';
    if (lo < 0) out += '<path d="M' + L + ' ' + Y(0).toFixed(1) + 'H' + (W - R) + '" stroke="' + t3 + '"/>';
    el.innerHTML = out;
  }
  function flows(avg) {
    var el = $('#plFlow'); if (!el) return;
    var pick = avg.rows.filter(function (r, i) { return i === 0 || r.a === P.ret || r.a === P.ret - 1 || r.a === P.ssAge || (r.a - P.age) % 5 === 0 || i === avg.rows.length - 1 || r.goal > 0; });
    el.innerHTML = '<table class="tbl"><thead><tr><th>Age</th><th>Pay</th><th class="hide-sm">Taxes</th><th>Spending</th><th class="hide-sm">Debt</th><th class="hide-sm">Goals</th><th class="hide-sm">Social Security</th><th>Saved or withdrawn</th><th>Net worth</th></tr></thead><tbody>' +
      pick.map(function (r) { return '<tr' + (r.a === P.ret ? ' class="hl"' : '') + '><td>' + r.a + '</td><td>' + (r.gross ? kusd(r.gross) : '&ndash;') + '</td><td class="hide-sm">' + kusd(r.tax) + '</td><td>' + kusd(r.spend) + '</td><td class="hide-sm">' + (r.debt ? kusd(r.debt) : '&ndash;') + '</td><td class="hide-sm">' + (r.goal ? kusd(r.goal) : '&ndash;') + '</td><td class="hide-sm">' + (r.ss ? kusd(r.ss) : '&ndash;') + '</td><td class="' + (r.save >= 0 ? 'up' : 'dn') + '">' + (r.save >= 0 ? '+' : '') + kusd(r.save) + '</td><td>' + kusd(r.nw) + '</td></tr>'; }).join('') + '</tbody></table>';
  }
  function debts(avg) {
    var el = $('#plDebtOut'); if (!el) return;
    if (!P.debts.length) { el.innerHTML = '<p class="fine" style="margin-top:0">No debts entered.</p>'; return; }
    var hi = P.debts.slice().sort(function (a, b) { return b.r - a.r; })[0];
    el.innerHTML = '<div class="kv" style="grid-template-columns:repeat(' + Math.min(3, avg.debts.length) + ',minmax(0,1fr))">' + avg.debts.map(function (x) { return '<div><b>' + (x.off != null ? 'Age ' + x.off : 'Not paid off') + '</b><span>' + esc(x.n) + ' paid off &middot; ' + usd(x.int) + ' interest</span></div>'; }).join('') + '</div>' +
      '<p class="fine">Interest is in the dollars of each year, added up. Extra money is worth most on the highest-rate debt, here the <b>' + esc(hi.n) + '</b> at ' + pc(hi.r, 2) + ': every dollar there earns that rate for sure, which beats the average bond return in this plan' + (hi.r > P.rb ? '' : ' only if it is higher than ' + pc(P.rb, 1)) + '.</p>';
  }
  function scenarios(base) {
    var el = $('#plSc'); if (!el) return;
    var rows = [['Your plan', base.ok],
      ['Retire 2 years earlier', sim(clone(P, { ret: Math.max(P.age + 1, P.ret - 2) })).ok],
      ['Retire 2 years later', sim(clone(P, { ret: Math.min(P.end - 1, P.ret + 2) })).ok],
      ['Stocks fall 30% the year you retire', sim(P, true).ok],
      ['Inflation 1 point higher (pay keeps up, investment returns do not)', sim(clone(P, { infl: P.infl + 0.01, g: P.g + 0.01 })).ok],
      ['Spend $250 a month less', sim(clone(P, { spend: Math.max(0, P.spend - 3000) })).ok],
      ['Spend 10% less in retirement', sim(clone(P, { retPct: P.retPct * 0.9 })).ok],
      ['Social Security at 70', sim(clone(P, { ssAge: 70, ss: P.ss * Math.pow(1.08, Math.max(0, 70 - P.ssAge)) })).ok]];
    el.innerHTML = '<table class="tbl"><thead><tr><th>What if</th><th>Chance the money lasts</th><th>Change</th></tr></thead><tbody>' + rows.map(function (r, i) {
      var dlt = r[1] - base.ok; return '<tr' + (i ? '' : ' class="hl"') + '><td>' + r[0] + '</td><td><span class="plbar"><i style="width:' + (r[1] * 100).toFixed(1) + '%"></i></span>' + pc(r[1]) + '</td><td class="' + (dlt > 0.004 ? 'up' : dlt < -0.004 ? 'dn' : '') + '">' + (i ? (dlt >= 0 ? '+' : '−') + cm(Math.abs(dlt * 100), 0) + ' pts' : '') + '</td></tr>';
    }).join('') + '</tbody></table>' +
      '<p class="fine">Delaying Social Security assumes the benefit grows 8% for each year after ' + P.ssAge + ', the rule for claiming after full retirement age. Every row uses the same 1,000 market paths, so the differences come only from the change.</p>';
    solve(base);
  }
  function solve(base) {
    var el = $('#plSolve'); if (!el) return;
    var goal = 0.85, extra = null, early = null;
    if (base.ok < goal) {
      var lo = 0, hi = 6000;
      if (sim(clone(P, { spend: Math.max(0, P.spend - hi * 12) })).ok >= goal) {
        for (var i = 0; i < 12; i++) { var m = (lo + hi) / 2; if (sim(clone(P, { spend: Math.max(0, P.spend - m * 12) })).ok >= goal) hi = m; else lo = m; }
        extra = hi;
      }
    }
    var lo2 = P.age + 1, hi2 = Math.min(P.end - 1, 80);   /* later retirement only helps, so search by halving */
    if (sim(clone(P, { ret: hi2 })).ok >= goal) {
      while (lo2 < hi2) { var mid = Math.floor((lo2 + hi2) / 2); if (sim(clone(P, { ret: mid })).ok >= goal) hi2 = mid; else lo2 = mid + 1; }
      early = hi2;
    }
    el.innerHTML = '<div class="kv three">' +
      '<div><b>' + (base.ok >= goal ? 'Already there' : extra != null ? usd(Math.ceil(extra / 10) * 10) : 'Over $6,000') + '</b><span>' + (base.ok >= goal ? 'The plan clears 85% as it stands' : 'More to save each month to reach 85%') + '</span></div>' +
      '<div><b>' + (early != null ? early : 'After 80') + '</b><span>Earliest retirement age at 85% or better</span></div>' +
      '<div><b>' + pc(base.ok) + '</b><span>Today&rsquo;s chance, for comparison</span></div></div>' +
      '<p class="fine">85% is a common planning bar: high enough to be safe, low enough that the plan does not over-save for the worst markets in history. Saving more is modelled as spending less, since both leave more money to invest.</p>';
  }

  /* ---------- start ---------- */
  function start() {
    refresh();
    var ad = $('#plAddD'), ag = $('#plAddG');
    if (ad) ad.onclick = function () { P.debts.push({ n: 'Credit card', b: 3000, r: 0.22, p: 150 }); refresh(); };
    if (ag) ag.onclick = function () { P.goals.push({ n: 'New goal', a: 20000, at: Math.min(P.end, P.age + 5) }); refresh(); };
    var t; addEventListener('resize', function () { clearTimeout(t); t = setTimeout(run, 200); });
    new MutationObserver(run).observe(d, { attributes: true, attributeFilter: ['class'] });
  }
  window.LDBPLAN = { life: life, sim: sim, avgPath: avgPath, P: P };
  var base = (document.querySelector('script[src*="plan.js"]') || {}).src || '';
  base = base.slice(0, base.indexOf('assets/'));
  fetch(base + 'data/markets.json?t=' + Math.floor(Date.now() / 600000)).then(function (r) { return r.ok ? r.json() : null; }).then(function (m) {
    var s = m && m.series;
    if (s && s.T10YIE && s.T10YIE.last) { P.infl = Math.round(s.T10YIE.last.v * 4) / 400; var n = $('#plInfl'); if (n) n.textContent = 'Inflation starts at the market’s 10-year breakeven, ' + s.T10YIE.last.v.toFixed(2) + '%, rounded.'; }
    if (s && s.DGS3MO && s.DGS3MO.last) P.rc = Math.round(Math.max(0, s.DGS3MO.last.v - 0.5) * 4) / 400;
  }).catch(function () {}).then(start);
})();
