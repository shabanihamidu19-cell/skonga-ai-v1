/**
 * SKONGA Pro — zero-cost experiment path (#1 without paying ClickPesa)
 *
 * ClickPesa has NO sandbox (live money only). Use this to test:
 *   - green "Active until …" on header/sidebar
 *   - localStorage entitlement shape used by the real payment flow
 *
 * How to activate (dev / founder only):
 *   1) Open Pro sheet → scroll to "Test unlock" → enter code SKONGADEV
 *   2) Or open app with ?protest=1 in the URL (browser)
 *   3) Or console: skongaTestPro(1)  // days
 *
 * Real users still pay via STK; this does NOT charge anyone.
 */
(function () {
  'use strict';

  var PRO_KEY = typeof PRO_STORAGE_KEY !== 'undefined' ? PRO_STORAGE_KEY : 'skonga_pro';
  var CODE = 'SKONGADEV';

  function formatUntil(ts) {
    var d = new Date(typeof ts === 'number' ? ts : Date.parse(ts));
    if (isNaN(d.getTime())) return '';
    try {
      return d.toLocaleString(undefined, {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch (e) {
      return d.toISOString().slice(0, 16).replace('T', ' ');
    }
  }

  function injectCss() {
    if (document.getElementById('skonga-pro-test-css')) return;
    var s = document.createElement('style');
    s.id = 'skonga-pro-test-css';
    s.textContent =
      '.hbtn-pro.is-active{background:rgba(52,211,153,.15)!important;border-color:rgba(52,211,153,.45)!important;color:#34d399!important}' +
      '.hbtn-pro.is-active .pro-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#34d399;margin-right:6px;box-shadow:0 0 8px #34d399}' +
      '#sidebarProStatus.pro-active{color:#34d399!important;font-weight:600}' +
      '.pay-test-unlock{margin-top:14px;padding:12px;border-radius:12px;border:1px dashed rgba(155,92,255,.35);background:rgba(155,92,255,.06)}' +
      '.pay-test-unlock label{display:block;font-size:.75rem;color:var(--text-muted,#9ba3b7);margin-bottom:6px}' +
      '.pay-test-unlock input{width:100%;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:rgba(0,0,0,.25);color:inherit;margin-bottom:8px}' +
      '.pay-test-unlock button{width:100%;padding:10px;border:none;border-radius:10px;font-weight:600;background:linear-gradient(135deg,#9b5cff,#6d3dff);color:#fff;cursor:pointer}';
    document.head.appendChild(s);
  }

  function writePro(days, planName) {
    days = Math.max(1, Number(days) || 1);
    var expiresAt = Date.now() + days * 24 * 60 * 60 * 1000;
    var payload = {
      planId: 'test-day',
      planName: planName || 'Pro (test)',
      price: 0,
      expiresAt: expiresAt,
      activatedAt: Date.now(),
      serverVerified: false,
      source: 'local-test-unlock',
    };
    try {
      localStorage.setItem(PRO_KEY, JSON.stringify(payload));
    } catch (e) {}
    paint();
    try {
      if (typeof updateSidebarProStatus === 'function') updateSidebarProStatus();
    } catch (e2) {}
    try {
      if (typeof showToast === 'function') showToast('Pro test: Active until ' + formatUntil(expiresAt));
    } catch (e3) {}
    return payload;
  }

  function paint() {
    injectCss();
    var p = null;
    try {
      p = JSON.parse(localStorage.getItem(PRO_KEY) || 'null');
      if (p && p.expiresAt && Date.now() >= p.expiresAt) {
        localStorage.removeItem(PRO_KEY);
        p = null;
      }
    } catch (e) {
      p = null;
    }
    var btn = document.getElementById('headerProBtn');
    var side = document.getElementById('sidebarProStatus');
    if (p && p.expiresAt) {
      var until = formatUntil(p.expiresAt);
      if (btn) {
        btn.classList.add('is-active');
        btn.innerHTML = '<span class="pro-dot"></span>Active until ' + until;
        btn.title = (p.planName || 'Pro') + ' · Active until ' + until;
      }
      if (side) {
        side.classList.add('pro-active');
        side.textContent = '✓ ' + (p.planName || 'Pro') + ' · Active until ' + until;
      }
    } else {
      if (btn) {
        btn.classList.remove('is-active');
        if (btn.innerHTML.indexOf('Active until') !== -1 || btn.querySelector('.pro-dot')) {
          btn.textContent = 'Pro';
        }
      }
      if (side) side.classList.remove('pro-active');
    }
  }

  function mountTestPanel() {
    var sheet = document.getElementById('paySheet');
    if (!sheet || document.getElementById('payTestUnlock')) return;
    var host =
      document.getElementById('payStepPlans') ||
      sheet.querySelector('.pay-step') ||
      sheet;
    var box = document.createElement('div');
    box.id = 'payTestUnlock';
    box.className = 'pay-test-unlock';
    box.innerHTML =
      '<label>Test unlock (no payment — founder/experiment only)</label>' +
      '<input id="payTestCode" type="text" autocomplete="off" placeholder="Enter code SKONGADEV" />' +
      '<button type="button" id="payTestBtn">Unlock Pro 1 day (test)</button>' +
      '<p style="margin:8px 0 0;font-size:.72rem;color:var(--text-muted,#9ba3b7);line-height:1.35">ClickPesa has no free sandbox. This only stores Pro on this device so you can test Active until UI. Real users still pay STK.</p>';
    host.appendChild(box);
    var btn = document.getElementById('payTestBtn');
    var input = document.getElementById('payTestCode');
    if (btn) {
      btn.addEventListener('click', function () {
        var v = (input && input.value ? input.value : '').trim().toUpperCase();
        if (v !== CODE) {
          try {
            if (typeof showToast === 'function') showToast('Wrong test code', true);
          } catch (e) {}
          return;
        }
        writePro(1, 'Pro (test)');
        try {
          if (typeof closeSkongaPay === 'function') closeSkongaPay();
        } catch (e2) {}
      });
    }
  }

  window.skongaTestPro = function (days) {
    return writePro(days || 1, 'Pro (test)');
  };

  function boot() {
    injectCss();
    paint();
    mountTestPanel();
    try {
      if (/[?&]protest=1(?:&|$)/.test(location.search)) {
        writePro(1, 'Pro (test)');
      }
    } catch (e) {}
    // Re-paint after main app updates sidebar
    setTimeout(paint, 800);
    setTimeout(mountTestPanel, 1200);
    setTimeout(paint, 2500);
  }

  // Wrap openSkongaPay so test panel is present when sheet opens
  function patchOpen() {
    if (typeof window.openSkongaPay !== 'function' || window.openSkongaPay._testPatch) return;
    var orig = window.openSkongaPay;
    window.openSkongaPay = function () {
      var r = orig.apply(this, arguments);
      setTimeout(mountTestPanel, 50);
      return r;
    };
    window.openSkongaPay._testPatch = true;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      boot();
      patchOpen();
    });
  } else {
    boot();
    patchOpen();
  }
  setTimeout(patchOpen, 500);
})();
