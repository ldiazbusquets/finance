/* LDB Finance: loan and mortgage calculator. Plain JavaScript, no libraries.
   Monthly payments on a fixed-rate loan, a full amortisation schedule, extra payments,
   taxes, insurance and PMI for a mortgage, and the APR once points and fees are counted.
   The mortgage rate starts at this week's 30-year average from FRED. */
(function () {
  'use strict';
  var d = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var css = function (v) { return getComputedStyle(d).getPropertyValue(v).trim(); };
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function cm(v, dp) { return v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function usd(v, dp) { return (v < 0 ? '−' : '') + '$' + cm(Math.abs(v), dp == null ? 0 : dp); }
  function pc(v, dp) { return cm(v * 100, dp == null ? 2 : dp) + '%'; }
  function fdate(s) { var p = s.split('-'); return MON[+p[1] - 1] + ' ' + (+p[2]) + ', ' + p[0]; }
  function big(v) { return v >= 1e6 ? '$' + (v / 1e6).toFixed(2) + 'M' : usd(v); }

  /* ---------- loan maths ---------- */
  function pmt(P, r, n) { return r === 0 ? P / n : P * r / (1 - Math.pow(1 + r, -n)); }
  /* month-by-month schedule; extra goes to principal every month; PMI drops once the balance reaches 78% of the price */
  function schedule(o) {
    var r = o.rate / 12, n = Math.round(o.years * 12), base = pmt(o.P, r, n), bal = o.P, rows = [], ti = 0, tp = 0, pmiPaid = 0;
    for (var m = 1; m <= n && bal > 0.005; m++) {
      var i = bal * r, pr = Math.min(bal, base - i), ex = Math.min(bal - pr, o.extra || 0);
      var pmi = o.pmi && bal > o.price * 0.78 ? o.P * o.pmi / 12 : 0;
      bal -= pr + ex; ti += i; tp += pr + ex; pmiPaid += pmi;
      rows.push({ m: m, i: i, p: pr, ex: ex, pmi: pmi, bal: Math.max(0, bal) });
    }
    return { base: base, rows: rows, interest: ti, months: rows.length, pmiPaid: pmiPaid };
  }
  /* APR: the rate at which the payments equal what you actually received (loan less points and fees) */
  function apr(P, base, n, cost) {
    var net = P - cost; if (net <= 0) return null;
    var lo = 0, hi = 1;
    for (var k = 0; k < 100; k++) { var mid = (lo + hi) / 2, pv = mid === 0 ? base * n : base * (1 - Math.pow(1 + mid / 12, -n)) / (mid / 12); if (pv > net) lo = mid; else hi = mid; }
    return (lo + hi) / 2;
  }

  /* ---------- state ---------- */
  var KINDS = {
    mortgage: { label: 'Mortgage', price: 450000, down: 0.20, rate: 0.0740, years: 30, extra: 0, tax: 0.011, ins: 1800, hoa: 0, pmi: 0.005, points: 0, fees: 6000, income: 150000 },
    auto: { label: 'Car loan', price: 40000, down: 0.10, rate: 0.0750, years: 5, extra: 0, fees: 0, points: 0 },
    student: { label: 'Student loan', amount: 40000, rate: 0.0650, years: 10, extra: 0, fees: 0, points: 0 },
    personal: { label: 'Personal loan', amount: 15000, rate: 0.1200, years: 3, extra: 0, fees: 0, points: 0 }
  };
  var kind = 'mortgage', L = JSON.parse(JSON.stringify(KINDS.mortgage)), RATE = null;
  var SPEC = {
    price: ['Price', '$', 5000, 0, 'n'], down: ['Down payment', '%', 0.01, 0, 'pc'], amount: ['Loan amount', '$', 1000, 0, 'n'],
    rate: ['Interest rate', '%', 0.00125, 3, 'pc'], years: ['Term', 'yr', 1, 0, 'n'], extra: ['Extra each month', '$', 50, 0, 'n'],
    tax: ['Property tax', '%', 0.001, 2, 'pc'], ins: ['Home insurance', '$/yr', 100, 0, 'n'], hoa: ['HOA dues', '$/mo', 25, 0, 'n'],
    pmi: ['PMI rate', '%', 0.0005, 2, 'pc'], points: ['Points', '%', 0.0025, 2, 'pc'], fees: ['Lender fees', '$', 500, 0, 'n'], income: ['Household income', '$/yr', 5000, 0, 'n']
  };
  var HINT = { down: 'Under 20% adds PMI', rate: 'Fixed for the whole term', extra: 'Goes straight to principal', tax: 'Per year, of the price', pmi: 'Per year, until 22% equity', points: 'Paid upfront, % of the loan', fees: 'Origination and closing', income: 'Before tax, for the 28% test' };
  function shown(k) { var s = SPEC[k], v = L[k]; return s[4] === 'pc' ? (v * 100).toFixed(s[3] || 2) : cm(v, 0); }
  function box(k) {
    var s = SPEC[k];
    return '<label class="in"><span>' + s[0] + (HINT[k] ? '<small>' + HINT[k] + '</small>' : '') + '</span><div class="box"><button type="button" data-k="' + k + '" data-d="-1">−</button>' +
      '<input data-k="' + k + '" inputmode="decimal" value="' + shown(k) + '"><i>' + s[1] + '</i><button type="button" data-k="' + k + '" data-d="1">+</button></div></label>';
  }
  function loanAmt() { return L.amount != null ? L.amount : L.price * (1 - L.down); }

  function inputs() {
    var el = $('#lIn'); if (!el) return;
    var main = kind === 'mortgage' ? ['price', 'down', 'rate', 'years', 'extra', 'income'] : kind === 'auto' ? ['price', 'down', 'rate', 'years', 'extra', 'fees'] : ['amount', 'rate', 'years', 'extra', 'fees'];
    el.innerHTML = '<div class="seg" id="lKind">' + Object.keys(KINDS).map(function (k) { return '<button type="button" data-v="' + k + '"' + (k === kind ? ' class="on"' : '') + '>' + KINDS[k].label + '</button>'; }).join('') + '</div>' +
      '<div class="ins">' + main.map(box).join('') + '</div>' +
      (kind === 'mortgage' ? '<details class="more"><summary>Taxes, insurance, PMI and fees</summary><div class="ins">' + ['tax', 'ins', 'hoa', 'pmi', 'points', 'fees'].map(box).join('') + '</div></details>' : '') +
      '<div class="tsy" id="lRate"></div>';
    $$('#lKind button').forEach(function (b) {
      b.onclick = function () { kind = b.getAttribute('data-v'); L = JSON.parse(JSON.stringify(KINDS[kind])); if (kind === 'mortgage' && RATE) L.rate = RATE.v / 100; inputs(); calc(); };
    });
    $$('#lIn input[data-k]').forEach(function (inp) {
      inp.addEventListener('change', function () {
        var k = inp.getAttribute('data-k'), v = parseFloat(inp.value.replace(/[^0-9.\-]/g, ''));
        if (isFinite(v)) { L[k] = SPEC[k][4] === 'pc' ? v / 100 : v; tidy(); }
        inputs(); calc();
      });
    });
    $$('#lIn button[data-k]').forEach(function (b) {
      b.onclick = function () { var k = b.getAttribute('data-k'); L[k] = +(L[k] + SPEC[k][2] * +b.getAttribute('data-d')).toFixed(6); tidy(); inputs(); calc(); };
    });
    var more = $('#lIn details'); if (more && OPEN) more.open = true; if (more) more.addEventListener('toggle', function () { OPEN = more.open; });
    rateNote();
  }
  var OPEN = false;
  function tidy() {
    ['price', 'amount', 'extra', 'ins', 'hoa', 'fees', 'income', 'points', 'tax', 'pmi', 'rate'].forEach(function (k) { if (L[k] != null) L[k] = Math.max(0, L[k]); });
    if (L.down != null) L.down = Math.min(0.99, Math.max(0, L.down));
    L.years = Math.min(40, Math.max(1, Math.round(L.years)));
  }
  function rateNote() {
    var el = $('#lRate'); if (!el) return;
    if (kind !== 'mortgage' || !RATE) { el.innerHTML = ''; return; }
    el.innerHTML = '<span>The average 30-year fixed mortgage rate was <b>' + RATE.v.toFixed(2) + '%</b> in the week of ' + fdate(RATE.d) + ' (Freddie Mac).</span>' + (Math.abs(L.rate * 100 - RATE.v) > 0.001 ? '<button type="button" class="reset" id="lUse">Use It</button>' : '');
    var u = $('#lUse'); if (u) u.onclick = function () { L.rate = RATE.v / 100; inputs(); calc(); };
  }

  /* ---------- results ---------- */
  function calc() {
    var P = loanAmt(), n = Math.round(L.years * 12), mort = kind === 'mortgage';
    if (!(P > 0)) { $('#lOut').innerHTML = '<p class="fine">Enter a loan amount above zero.</p>'; return; }
    var pmiRate = mort && L.down < 0.2 ? L.pmi : 0;
    var S = schedule({ P: P, rate: L.rate, years: L.years, extra: L.extra, pmi: pmiRate, price: L.price || P });
    var S0 = L.extra > 0 ? schedule({ P: P, rate: L.rate, years: L.years, extra: 0, pmi: pmiRate, price: L.price || P }) : S;
    var esc = mort ? (L.price * L.tax + L.ins) / 12 + L.hoa : 0, pmi1 = mort && pmiRate ? P * pmiRate / 12 : 0;
    var total = S.base + esc + pmi1 + (L.extra || 0), cost = P * (L.points || 0) + (L.fees || 0), A = apr(P, S.base, n, cost);
    var end = new Date(); end.setMonth(end.getMonth() + S.months);
    var k = [
      [usd(S.base), 'Monthly principal and interest'],
      mort ? [usd(total), 'All-in monthly cost' + (L.extra ? ', with extra' : '')] : [usd(S.base * n), 'Total of payments, no extra'],
      [usd(S.interest), 'Total interest' + (L.extra ? ' with extra payments' : '')],
      [MON[end.getMonth()] + ' ' + end.getFullYear(), 'Paid off' + (L.extra ? ', ' + Math.round((S0.months - S.months) / 12 * 10) / 10 + ' years early' : '')],
      [A == null ? 'n/a' : pc(A), 'APR, counting points and fees'],
      L.extra ? [usd(S0.interest - S.interest), 'Interest saved by paying extra'] : [cm(S.interest / P * 100, 0) + '%', 'Interest as a share of the loan']
    ];
    var html = '<div class="kv three">' + k.map(function (x) { return '<div><b>' + x[0] + '</b><span>' + x[1] + '</span></div>'; }).join('') + '</div>';
    if (mort) {
      var parts = [['Principal and interest', S.base], ['Property tax', L.price * L.tax / 12], ['Insurance', L.ins / 12], ['HOA', L.hoa], ['PMI', pmi1], ['Extra principal', L.extra || 0]].filter(function (x) { return x[1] > 0.5; });
      var tot = parts.reduce(function (a, x) { return a + x[1]; }, 0);
      html += '<div class="split3"><div class="stack">' + parts.map(function (x, i) { return '<i style="width:' + (x[1] / tot * 100).toFixed(2) + '%;opacity:' + (1 - i * 0.14).toFixed(2) + '" title="' + x[0] + '"></i>'; }).join('') + '</div>' +
        '<ul class="sleg">' + parts.map(function (x, i) { return '<li><i style="opacity:' + (1 - i * 0.14).toFixed(2) + '"></i>' + x[0] + '<b>' + usd(x[1]) + '</b></li>'; }).join('') + '</ul></div>';
      var notes = [];
      notes.push('Loan of <b>' + usd(P) + '</b> on a ' + usd(L.price) + ' home with ' + pc(L.down, 0) + ' down.');
      if (pmiRate) notes.push('With less than 20% down you pay PMI of about <b>' + usd(pmi1) + ' a month</b> until you own 22% of the home, about ' + usd(S.pmiPaid) + ' in all.');
      if (L.income > 0) { var ratio = (total - (L.extra || 0)) / (L.income / 12); notes.push('Housing costs take <b>' + pc(ratio, 1) + '</b> of gross income. Lenders traditionally look for 28% or less' + (ratio > 0.28 ? '; this is above it.' : '.')); }
      if (cost > 0) notes.push('Points and fees of ' + usd(cost) + ' raise the true annual cost from ' + pc(L.rate) + ' to ' + (A == null ? 'n/a' : pc(A)) + '.');
      html += '<div class="lnotes">' + notes.map(function (t) { return '<p>' + t + '</p>'; }).join('') + '</div>';
    }
    $('#lOut').innerHTML = html;
    chart(S, S0, P);
    grid(P);
    table(S);
  }

  /* balance over time, with and without extra payments, over yearly interest and principal bars */
  function chart(S, S0, P) {
    var el = $('#lChart'); if (!el) return;
    var W = el.clientWidth || 640, H = 260, L0 = 58, R = 64, T = 12, B = 26, yrs = Math.ceil(S0.months / 12);
    var yr = function (rows) { var o = []; rows.forEach(function (r) { var y = Math.floor((r.m - 1) / 12); o[y] = o[y] || { i: 0, p: 0 }; o[y].i += r.i; o[y].p += r.p + r.ex; }); return o; };
    var Y1 = yr(S.rows), mxBar = Math.max.apply(null, Y1.map(function (y) { return y.i + y.p; }));
    var X = function (m) { return L0 + m / (yrs * 12) * (W - L0 - R); }, YB = function (v) { return T + (1 - v / P) * (H - T - B); }, YP = function (v) { return H - B - v / mxBar * (H - T - B) * 0.45; };
    var acc = css('--acc'), t2 = css('--t2'), t3 = css('--t3'), ln = css('--line'), g = '';
    [0, .25, .5, .75, 1].forEach(function (f) { var v = P * f; g += '<line x1="' + L0 + '" x2="' + (W - R) + '" y1="' + YB(v) + '" y2="' + YB(v) + '" stroke="' + ln + '"/><text x="' + (L0 - 8) + '" y="' + (YB(v) + 3.5) + '" text-anchor="end" fill="' + t3 + '">' + big(v) + '</text>'; });
    [0, .5, 1].forEach(function (f) { var v = mxBar * f; g += '<text x="' + (W - R + 8) + '" y="' + (YP(v) + 3.5) + '" fill="' + acc + '">' + big(v) + '</text>'; });   /* bars have their own scale, on the right */
    g += '<text x="' + (W - R + 8) + '" y="' + (YP(mxBar) - 12) + '" fill="' + t3 + '">per year</text>';
    var bw = (W - L0 - R) / yrs * 0.62;
    Y1.forEach(function (y, k) { if (!y) return; var x = X(k * 12 + 6) - bw / 2, hp = H - B - YP(y.p), hi = H - B - YP(y.i); g += '<rect x="' + x.toFixed(1) + '" y="' + (H - B - hp - hi).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + hi.toFixed(1) + '" fill="' + acc + '" opacity=".55"/><rect x="' + x.toFixed(1) + '" y="' + (H - B - hp).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + hp.toFixed(1) + '" fill="' + t2 + '" opacity=".28"/>'; });
    function path(rows) { return 'M' + X(0) + ' ' + YB(P) + rows.map(function (r) { return 'L' + X(r.m).toFixed(1) + ' ' + YB(r.bal).toFixed(1); }).join(''); }
    if (S0 !== S) g += '<path d="' + path(S0.rows) + '" fill="none" stroke="' + t2 + '" stroke-width="1.4" stroke-dasharray="4 4"/>';
    g += '<path d="' + path(S.rows) + '" fill="none" stroke="' + acc + '" stroke-width="2.2"/>';
    var every = (W < 520 ? 2 : 1) * (yrs > 20 ? 5 : yrs > 8 ? 2 : 1);
    for (var y = 0; y <= yrs; y += every) g += '<text x="' + X(y * 12) + '" y="' + (H - 6) + '" text-anchor="middle" fill="' + t3 + '">' + (y ? 'Yr ' + y : 'Start') + '</text>';
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H); el.innerHTML = g;
    $('#lLeg').innerHTML = '<span><i style="background:var(--acc);height:2px"></i>Balance</span>' + (S0 !== S ? '<span><i style="background:var(--t2);height:1px"></i>Balance without extra</span>' : '') + '<span><i style="background:var(--acc);opacity:.55;height:9px;width:9px"></i>Interest paid each year (right scale)</span><span><i style="background:var(--t2);opacity:.28;height:9px;width:9px"></i>Principal paid each year</span>';
  }

  /* monthly payment and total interest across rates and terms */
  function grid(P) {
    var el = $('#lGrid'); if (!el) return;
    var terms = kind === 'mortgage' ? [15, 20, 30] : kind === 'auto' ? [3, 5, 7] : kind === 'student' ? [5, 10, 20] : [2, 3, 5];
    var rates = [-0.01, -0.005, 0, 0.005, 0.01].map(function (x) { return Math.max(0, L.rate + x); });
    var h = '<div class="scroll"><table class="tbl lgrid"><thead><tr><th>Rate</th>' + terms.map(function (t) { return '<th>' + t + ' years</th>'; }).join('') + '</tr></thead><tbody>';
    rates.forEach(function (r, i) {
      h += '<tr' + (i === 2 ? ' class="me"' : '') + '><td>' + pc(r) + '</td>' + terms.map(function (t) { var n = t * 12, m = pmt(P, r / 12, n); return '<td><b>' + usd(m) + '</b><small>' + usd(m * n - P) + ' interest</small></td>'; }).join('') + '</tr>';
    });
    el.innerHTML = h + '</tbody></table></div>';
  }

  function table(S) {
    var el = $('#lTable'); if (!el) return;
    var ys = [], cur = null;
    S.rows.forEach(function (r) { var y = Math.floor((r.m - 1) / 12); if (!ys[y]) ys[y] = { i: 0, p: 0, ex: 0, pmi: 0, bal: 0 }; var o = ys[y]; o.i += r.i; o.p += r.p; o.ex += r.ex; o.pmi += r.pmi; o.bal = r.bal; });
    var cum = 0;
    el.innerHTML = '<div class="scroll"><table class="tbl allnum"><thead><tr><th>Year</th><th>Interest</th><th>Principal</th>' + (L.extra ? '<th>Extra</th>' : '') + (kind === 'mortgage' ? '<th>PMI</th>' : '') + '<th>Interest so far</th><th>Balance at year end</th></tr></thead><tbody>' +
      ys.map(function (o, k) { cum += o.i; return '<tr><td>' + (k + 1) + '</td><td>' + usd(o.i) + '</td><td>' + usd(o.p) + '</td>' + (L.extra ? '<td>' + usd(o.ex) + '</td>' : '') + (kind === 'mortgage' ? '<td>' + usd(o.pmi) + '</td>' : '') + '<td>' + usd(cum) + '</td><td>' + usd(o.bal) + '</td></tr>'; }).join('') + '</tbody></table></div>';
  }

  /* ---------- start ---------- */
  inputs(); calc();
  var rz; window.addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(calc, 150); });
  new MutationObserver(function () { calc(); }).observe(d, { attributes: true, attributeFilter: ['class'] });
  fetch('data/markets.json?t=' + Math.floor(Date.now() / 600000), { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (m) {
    var s = m.series && m.series.MORTGAGE30US; if (!s || !s.last) return;
    RATE = s.last; if (kind === 'mortgage') { L.rate = RATE.v / 100; KINDS.mortgage.rate = L.rate; } inputs(); calc();
  }).catch(function () {});
})();
