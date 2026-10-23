/* LDB Finance: position sizer and portfolio x-ray. Plain JavaScript, no libraries. */
(function () {
  'use strict';
  var d = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var isn = function (v) { return typeof v === 'number' && isFinite(v); };
  var css = function (v) { return getComputedStyle(d).getPropertyValue(v).trim(); };
  function cm(v, dp) { return v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function usd(v, dp) { if (!isn(v)) return '—'; return (v < 0 ? '−' : '') + '$' + cm(Math.abs(v), dp == null ? 2 : dp); }
  function pc(v, dp) { if (!isn(v)) return '—'; return (v < 0 ? '−' : '') + cm(Math.abs(v * 100), dp == null ? 1 : dp) + '%'; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function num(s) { var v = parseFloat(String(s).replace(/[^0-9.\-]/g, '')); return isn(v) ? v : null; }
  var store = {
    get: function (k) { try { return JSON.parse(localStorage.getItem('ldbf:' + k)); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem('ldbf:' + k, JSON.stringify(v)); } catch (e) {} }
  };
  var base = (document.querySelector('script[src*="tools.js"]') || {}).src || '';
  base = base.slice(0, base.indexOf('assets/'));
  function getJSON(p) { if (window.LDBget) return window.LDBget(p); return fetch(base + p + '?t=' + Math.floor(Date.now() / 600000), { cache: 'no-store' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }

  var IX = null, PX = {}, BY = {};
  var ETF = { SPY: 'cap', VOO: 'cap', IVV: 'cap', SPLG: 'cap', SPYM: 'cap', RSP: 'eq' };
  var ETFNAME = { SPY: 'SPDR S&P 500 ETF', VOO: 'Vanguard S&P 500 ETF', IVV: 'iShares Core S&P 500 ETF', SPLG: 'SPDR Portfolio S&P 500 ETF', SPYM: 'SPDR Portfolio S&P 500 ETF', RSP: 'Invesco S&P 500 Equal Weight ETF' };

  /* ================= position sizer ================= */
  var Z = store.get('sizer') || { acct: 50000, risk: 1, entry: 100, stop: 94, target: 115, cap: 20, t: '' };
  function sizerInputs() {
    var el = $('#zIn'); if (!el) return;
    var f = function (k, label, hint, unit) {
      return '<label class="in"><span>' + label + (hint ? '<small>' + hint + '</small>' : '') + '</span><div class="box nostep"><input data-z="' + k + '" inputmode="decimal" value="' + (Z[k] == null ? '' : Z[k]) + '"><i>' + unit + '</i></div></label>';
    };
    el.innerHTML = '<label class="in tick"><span>Ticker<small>Optional: fills in the last close</small></span><div class="box nostep"><input data-z="t" value="' + esc(Z.t || '') + '" placeholder="e.g. COST" autocomplete="off" spellcheck="false"><i id="zTk"></i></div></label>' +
      '<div class="ins">' + f('acct', 'Account size', '', '$') + f('risk', 'Risk per trade', 'Share of the account you accept losing', '%') +
      f('entry', 'Entry price', '', '$') + f('stop', 'Stop price', 'Where you are wrong', '$') +
      f('target', 'Target price', 'Optional', '$') + f('cap', 'Largest position', 'Share of the account', '%') + '</div>';
    $$('input[data-z]', el).forEach(function (inp) {
      inp.addEventListener('input', function () {
        var k = inp.getAttribute('data-z');
        if (k === 't') { Z.t = inp.value.toUpperCase().replace(/[^A-Z.\-]/g, '').slice(0, 6); inp.value = Z.t; var row = BY[Z.t] || BY[Z.t.replace('-', '.')]; var p = PX[row ? row[0] : Z.t]; if (p && p.p) { Z.entry = +p.p.toFixed(2); $('input[data-z="entry"]').value = Z.entry; $('#zTk').textContent = '✓'; } else $('#zTk').textContent = ''; }
        else Z[k] = num(inp.value);
        sizer();
      });
    });
  }
  function sizer() {
    var out = $('#zOut'); if (!out) return;
    store.set('sizer', Z);
    var A = Z.acct, r = Z.risk / 100, e = Z.entry, s = Z.stop, tg = Z.target, cap = (Z.cap || 100) / 100;
    if (!(A > 0) || !(r > 0) || !(e > 0) || !(s > 0) || s === e) { out.innerHTML = '<div class="wait"><b>Fill in the account, risk, entry and stop.</b> The stop has to differ from the entry.</div>'; return; }
    var short = s > e, per = Math.abs(e - s), budget = A * r;
    var n = Math.floor(budget / per), capN = Math.floor(A * cap / e), capped = n > capN;
    if (capped) n = capN;
    var pos = n * e, risk = n * per, rr = isn(tg) && tg > 0 && tg !== e ? ((short ? e - tg : tg - e) / per) : null;
    var tgOK = rr != null && rr > 0;
    out.innerHTML = '<div class="bres"><div class="bprice"><span class="mono">' + (short ? 'Shares to sell short' : 'Shares to buy') + '</span><b>' + cm(n, 0) + '</b><small>' + usd(pos, 0) + ' position, ' + pc(pos / A) + ' of the account</small></div>' +
      '<p>' + (capped ? 'The risk budget allowed more, but the <b>' + pc(cap, 0) + ' position limit</b> caps it.' : 'If the stop at ' + usd(s) + ' is hit, the loss is about <b>' + usd(risk, 0) + '</b>, ' + pc(risk / A, 2) + ' of the account.') + '</p></div>' +
      '<div class="kv three">' +
      '<div><b>' + usd(risk, 0) + '</b><span>Money at risk</span></div>' +
      '<div><b>' + usd(per) + '</b><span>Risk per share, ' + pc(per / e) + '</span></div>' +
      '<div><b>' + (tgOK ? rr.toFixed(1) + ' : 1' : '—') + '</b><span>Reward to risk</span></div>' +
      '<div><b>' + (tgOK ? usd(n * Math.abs(tg - e), 0) : '—') + '</b><span>Gain at target</span></div>' +
      '<div><b>' + (tgOK ? pc(1 / (1 + rr), 0) : '—') + '</b><span>Win rate needed to break even</span></div>' +
      '<div><b>' + cm(Math.floor(A * 0.5 / Math.max(risk, 1)), 0) + '</b><span>Straight losses to halve the account</span></div></div>' +
      (rr != null && rr <= 0 ? '<p class="fine">The target is on the wrong side of the entry.</p>' : '');
    drawLadder(e, s, tgOK ? tg : null, short);
  }
  function drawLadder(e, s, tg, short) {
    var el = $('#zCh'); if (!el) return;
    var W = el.clientWidth || 520, H = el.clientHeight || 120, L = 12, R = 12;
    var pts = [e, s].concat(tg ? [tg] : []), lo = Math.min.apply(null, pts), hi = Math.max.apply(null, pts), pad = (hi - lo) * 0.12;
    lo -= pad; hi += pad;
    var X = function (v) { return L + (v - lo) / (hi - lo) * (W - L - R); }, y = H / 2;
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    var o = '<rect x="' + Math.min(X(e), X(s)).toFixed(1) + '" y="' + (y - 9) + '" width="' + Math.abs(X(e) - X(s)).toFixed(1) + '" height="18" rx="9" fill="' + css('--dn') + '" opacity=".35"/>';
    if (tg) o += '<rect x="' + Math.min(X(e), X(tg)).toFixed(1) + '" y="' + (y - 9) + '" width="' + Math.abs(X(tg) - X(e)).toFixed(1) + '" height="18" rx="9" fill="' + css('--up') + '" opacity=".35"/>';
    [[s, 'Stop', css('--dn')], [e, 'Entry', css('--ink')]].concat(tg ? [[tg, 'Target', css('--up')]] : []).forEach(function (p, i) {
      o += '<circle cx="' + X(p[0]).toFixed(1) + '" cy="' + y + '" r="6" fill="' + p[2] + '" stroke="' + css('--s1') + '" stroke-width="3"/>' +
        '<text x="' + X(p[0]).toFixed(1) + '" y="' + (i === 1 ? y - 20 : y + 32) + '" text-anchor="middle">' + p[1] + ' ' + usd(p[0]) + '</text>';
    });
    el.innerHTML = o;
  }

  /* ================= portfolio x-ray ================= */
  var EXAMPLE = [['VOO', 40000], ['AAPL', 12000], ['MSFT', 10000], ['NVDA', 9000], ['JPM', 8000], ['COST', 7000], ['KO', 5000], ['XOM', 4000], ['GS', 5000]];
  var H = store.get('xray') || EXAMPLE.map(function (r) { return { t: r[0], v: r[1] }; });
  function xrayTable() {
    var el = $('#xT'); if (!el) return;
    el.innerHTML = '<div class="scroll"><table class="tbl pf"><thead><tr><th>Ticker</th><th>Value</th><th class="hide-sm l">Company</th><th></th></tr></thead><tbody>' +
      H.map(function (h, i) {
        var nm = ETF[h.t] ? ETFNAME[h.t] + ' (look-through)' : BY[h.t] ? BY[h.t][1] : h.t ? '<span class="dn">Not in the S&amp;P 500 data</span>' : '';
        return '<tr data-i="' + i + '"><td><input class="cell tk" data-f="t" value="' + esc(h.t) + '" aria-label="Ticker" autocomplete="off" spellcheck="false"></td>' +
          '<td><input class="cell" data-f="v" inputmode="decimal" value="' + (isn(h.v) ? cm(h.v, 0) : '') + '" aria-label="Value in dollars"><i>$</i></td><td class="hide-sm co-nm">' + nm + '</td>' +
          '<td><button type="button" class="x" data-del="' + i + '" aria-label="Remove">×</button></td></tr>';
      }).join('') + '</tbody></table></div>';
    $$('input.cell', el).forEach(function (inp) {
      inp.onchange = function () {
        var i = +inp.closest('tr').getAttribute('data-i'), f = inp.getAttribute('data-f');
        if (f === 't') H[i].t = inp.value.toUpperCase().replace(/[^A-Z.\-]/g, '').replace('-', '.').slice(0, 6);
        else H[i].v = Math.max(0, num(inp.value) || 0);
        xrayTable(); xray();
      };
    });
    $$('button[data-del]', el).forEach(function (x) { x.onclick = function () { H.splice(+x.getAttribute('data-del'), 1); xrayTable(); xray(); }; });
  }
  function xray() {
    var out = $('#xOut'); if (!out) return;
    store.set('xray', H);
    if (!IX) { out.innerHTML = '<div class="wait">Loading company data&hellip;</div>'; return; }
    var cols = IX.cols, iM = cols.indexOf('mcap'), iS = cols.indexOf('sector'), iP = cols.indexOf('pe');
    var tot = 0, other = 0, expo = {}, sec = {}, sp = {}, spTot = 0;
    IX.rows.forEach(function (r) { if (isn(r[iM])) { spTot += r[iM]; sp[r[iS]] = (sp[r[iS]] || 0) + r[iM]; } });
    var nEq = IX.rows.filter(function (r) { return isn(r[iM]); }).length;
    H.forEach(function (h) {
      if (!(h.v > 0)) return; tot += h.v;
      if (ETF[h.t]) {
        IX.rows.forEach(function (r) { if (!isn(r[iM])) return; var w = ETF[h.t] === 'cap' ? r[iM] / spTot : 1 / nEq; expo[r[0]] = (expo[r[0]] || 0) + h.v * w; });
      } else if (BY[h.t]) expo[h.t] = (expo[h.t] || 0) + h.v;
      else other += h.v;
    });
    if (!(tot > 0)) { out.innerHTML = '<div class="wait"><b>Add a holding.</b> Enter a ticker and how much of it you own, in dollars.</div>'; return; }
    var list = Object.keys(expo).map(function (t) { return [t, expo[t]]; }).sort(function (a, b) { return b[1] - a[1]; });
    list.forEach(function (x) { var r = BY[x[0]]; sec[r[iS]] = (sec[r[iS]] || 0) + x[1]; });
    if (other) sec['Not covered'] = other;
    var hhi = 0, beta = 0, bw = 0, ey = 0, ew = 0;
    list.forEach(function (x) {
      var w = x[1] / tot; hhi += w * w;
      var p = PX[x[0]]; if (p && isn(p.b)) { beta += w * p.b; bw += w; }
      var pe = BY[x[0]][iP]; if (isn(pe) && pe > 0) { ey += w / pe; ew += w; }
    });
    var top5 = list.slice(0, 5).reduce(function (a, x) { return a + x[1]; }, 0) / tot;
    var secs = Object.keys(sp).sort(function (a, b) { return (sec[b] || 0) / tot - (sec[a] || 0) / tot || sp[b] - sp[a]; });
    if (other) secs.push('Not covered');
    var maxW = Math.max.apply(null, secs.map(function (s) { return Math.max((sec[s] || 0) / tot, (sp[s] || 0) / spTot); }));
    var bars = secs.map(function (s) {
      var a = (sec[s] || 0) / tot, b = s === 'Not covered' ? null : sp[s] / spTot, dlt = b == null ? null : a - b;
      return '<div class="xb"><span class="nm">' + esc(s) + '</span><div class="tr"><i class="me" style="width:' + (a / maxW * 100).toFixed(1) + '%"></i>' + (b == null ? '' : '<i class="ix" style="left:' + (b / maxW * 100).toFixed(1) + '%"></i>') + '</div>' +
        '<b>' + pc(a) + '</b><em class="' + (dlt == null ? '' : dlt > 0.02 ? 'up' : dlt < -0.02 ? 'dn' : '') + '">' + (dlt == null ? '' : (dlt >= 0 ? '+' : '−') + cm(Math.abs(dlt * 100), 1)) + '</em></div>';
    }).join('');
    var etfOn = H.some(function (h) { return ETF[h.t] && h.v > 0; });
    var overlap = etfOn ? H.filter(function (h) { return !ETF[h.t] && BY[h.t] && h.v > 0; }).map(function (h) { return [h.t, expo[h.t] - h.v]; }).filter(function (x) { return x[1] > 1; }) : [];
    out.innerHTML = '<div class="kv four">' +
      '<div><b>' + usd(tot, 0) + '</b><span>Total value</span></div>' +
      '<div><b>' + (1 / hhi).toFixed(0) + '</b><span>Effective number of holdings</span></div>' +
      '<div><b>' + pc(top5) + '</b><span>In the five largest exposures</span></div>' +
      '<div><b>' + (bw > 0.5 ? (beta / bw).toFixed(2) : '—') + '</b><span>Weighted beta</span></div></div>' +
      '<div class="cols eq x2"><div><h4 class="xh">Sectors <small>you <i class="lg me"></i> &middot; S&amp;P 500 <i class="lg ix"></i> &middot; difference in points</small></h4><div class="xbars">' + bars + '</div></div>' +
      '<div><h4 class="xh">Largest exposures <small>after looking through index funds</small></h4><table class="tbl xl"><tbody>' +
      list.slice(0, 10).map(function (x) { var r = BY[x[0]]; return '<tr><td>' + esc(r[1]) + '<small>' + esc(x[0]) + ' &middot; ' + esc(r[iS]) + '</small></td><td>' + usd(x[1], 0) + '</td><td>' + pc(x[1] / tot) + '</td></tr>'; }).join('') + '</tbody></table>' +
      (ew > 0.5 ? '<p class="fine">Weighted P/E of the covered stocks: <b>' + (ew / ey).toFixed(1) + '&times;</b> (earnings yield averaged, so loss-makers don&rsquo;t distort it).</p>' : '') + '</div></div>' +
      (overlap.length ? '<div class="key"><b>Overlap.</b> Your index fund already holds ' + overlap.slice(0, 4).map(function (x) { return esc(x[0]) + ' (' + usd(x[1], 0) + ' more)'; }).join(', ') + (overlap.length > 4 ? ' and ' + (overlap.length - 4) + ' more' : '') + ', on top of what you own directly.</div>' : '') +
      (1 / hhi < 12 ? '<p class="fine warnx">With fewer than about a dozen effective holdings, one company&rsquo;s bad year shows up clearly in the whole portfolio.</p>' : '');
  }

  /* ---------- start ---------- */
  sizerInputs(); sizer();
  xrayTable(); xray();
  var add = $('#xAdd'), ex = $('#xEx'), clr = $('#xClr');
  if (add) add.onclick = function () { H.push({ t: '', v: 0 }); xrayTable(); var c = $$('#xT input.tk'); if (c.length) c[c.length - 1].focus(); };
  if (ex) ex.onclick = function () { H = EXAMPLE.map(function (r) { return { t: r[0], v: r[1] }; }); xrayTable(); xray(); };
  if (clr) clr.onclick = function () { H = [{ t: '', v: 0 }]; xrayTable(); xray(); };
  Promise.all([getJSON('data/co/index.json').catch(function () { return null; }), getJSON('data/co/prices.json').catch(function () { return {}; })]).then(function (r) {
    IX = r[0]; PX = (r[1] && r[1].px) || {};
    if (IX) IX.rows.forEach(function (row) { BY[row[0]] = row; });
    xrayTable(); xray();
    if (Z.t) { var inp = $('input[data-z="t"]'); if (inp) inp.dispatchEvent(new Event('input')); }
  });
  var t; addEventListener('resize', function () { clearTimeout(t); t = setTimeout(sizer, 150); });
  new MutationObserver(function () { sizer(); }).observe(d, { attributes: true, attributeFilter: ['class'] });
})();
