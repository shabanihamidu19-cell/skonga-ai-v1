/**
 * skonga-pro-onboard.js
 * #1 Reliable Pro unlock + green "Active until…" on header/sidebar
 * #2 First-run onboarding: Form + optional Combination (English UI)
 */
(function () {
  'use strict';

  var API =
    (typeof API_BASE !== 'undefined' && API_BASE) ||
    'https://skonga-backend-v2.onrender.com';
  var PRO_KEY = typeof PRO_STORAGE_KEY !== 'undefined' ? PRO_STORAGE_KEY : 'skonga_pro';
  var LAST_ORDER_KEY = 'skonga_last_order_id';
  var ONBOARD_DONE_KEY = 'skonga_onboard_done_v1';
  var EXTRAS_KEY = 'skonga_user_extras';

  var LEVEL_LABELS = {
    form1: 'Form 1',
    form2: 'Form 2',
    form3: 'Form 3',
    form4: 'Form 4 (NECTA)',
    form5: 'Form 5',
    form6: 'Form 6 (ACSEE)',
    primary7: 'Standard 7 (PSLE)',
  };

  function sessionId() {
    try {
      if (typeof DEVICE_SESSION_ID !== 'undefined' && DEVICE_SESSION_ID) return DEVICE_SESSION_ID;
    } catch (e) {}
    try {
      return localStorage.getItem('skonga_device_session_id') || '';
    } catch (e2) {
      return '';
    }
  }

  function uid() {
    try {
      return (window._fb && window._fb.currentUser && window._fb.currentUser.uid) || null;
    } catch (e) {
      return null;
    }
  }

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

  function readLocalPro() {
    try {
      if (typeof getPro === 'function') return getPro();
      var p = JSON.parse(localStorage.getItem(PRO_KEY) || 'null');
      if (!p || !p.expiresAt) return null;
      if (Date.now() >= p.expiresAt) {
        localStorage.removeItem(PRO_KEY);
        return null;
      }
      return p;
    } catch (e) {
      return null;
    }
  }

  function writeLocalPro(data) {
    if (!data || !data.expiresAt) return;
    var payload = {
      planId: data.planId || 'pro',
      planName: data.planName || 'Pro',
      expiresAt: data.expiresAt,
      activatedAt: Date.now(),
      serverVerified: true,
      orderId: data.orderId || null,
    };
    try {
      localStorage.setItem(PRO_KEY, JSON.stringify(payload));
    } catch (e) {}
    try {
      if (typeof updateSidebarProStatus === 'function') updateSidebarProStatus();
    } catch (e2) {}
    try {
      if (typeof scheduleProExpiryReminder === 'function') {
        scheduleProExpiryReminder(payload.expiresAt, payload.planName);
      }
    } catch (e3) {}
    paintProUI();
  }

  function injectProCSS() {
    if (document.getElementById('skonga-pro-css')) return;
    var s = document.createElement('style');
    s.id = 'skonga-pro-css';
    s.textContent = [
      '.hbtn-pro.is-active{',
      'background:linear-gradient(135deg,#059669,#10b981)!important;',
      'border-color:rgba(16,185,129,.55)!important;',
      'color:#ecfdf5!important;',
      'box-shadow:0 0 14px rgba(16,185,129,.35);',
      'max-width:min(58vw,220px);overflow:hidden;text-overflow:ellipsis}',
      '.hbtn-pro.is-active .pro-dot{',
      'display:inline-block;width:7px;height:7px;border-radius:50%;',
      'background:#a7f3d0;margin-right:5px;vertical-align:middle;',
      'box-shadow:0 0 6px #6ee7b7}',
      '#sidebarProStatus.pro-active{color:#34d399!important;font-weight:600}',
      '.pay-unlock-bar{margin-top:12px;padding:12px;border-radius:12px;',
      'background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.35)}',
      '.pay-unlock-bar p{margin:0 0 10px;font-size:.8rem;color:var(--text-secondary);line-height:1.4}',
      '.pay-unlock-btn{width:100%;padding:11px;border:none;border-radius:11px;',
      'background:linear-gradient(135deg,#059669,#10b981);color:#fff;',
      'font-family:var(--font-b);font-weight:600;font-size:.85rem;cursor:pointer}',
      '.pay-unlock-btn:disabled{opacity:.6}',
      /* Onboarding */
      '#skongaOnboard{position:fixed;inset:0;z-index:300;display:flex;align-items:flex-end;',
      'justify-content:center;background:rgba(0,0,0,.55);padding:0}',
      '#skongaOnboard.hidden{display:none!important}',
      '.ob-sheet{width:100%;max-width:430px;max-height:92vh;overflow:auto;',
      'border-radius:20px 20px 0 0;padding:8px 18px 28px;',
      'background:linear-gradient(180deg,#1a1230 0%,#0f0c1c 40%);',
      'border:1px solid rgba(168,85,247,.35);border-bottom:none;',
      'box-shadow:0 -12px 40px rgba(0,0,0,.45);animation:obUp .28s ease}',
      '@keyframes obUp{from{transform:translateY(40px);opacity:.6}to{transform:none;opacity:1}}',
      '.ob-handle{width:40px;height:4px;border-radius:4px;background:rgba(255,255,255,.2);',
      'margin:6px auto 14px}',
      '.ob-title{font-size:1.15rem;font-weight:700;color:#f3e8ff;margin:0 0 6px}',
      '.ob-sub{font-size:.82rem;color:var(--text-secondary);margin:0 0 16px;line-height:1.45}',
      '.ob-field{margin-bottom:14px}',
      '.ob-field label{display:block;font-size:.72rem;color:var(--text-muted);margin-bottom:6px}',
      '.ob-field select{width:100%;padding:12px 14px;border-radius:12px;',
      'border:1.5px solid rgba(168,85,247,.35);background:rgba(0,0,0,.35);',
      'color:var(--text-primary);font-family:var(--font-b);font-size:.9rem;',
      'appearance:none}',
      '#obComboWrap{display:none;padding-top:4px}',
      '#obComboWrap.show{display:block}',
      '.ob-optional{font-size:.7rem;color:#22d3ee;margin:0 0 8px}',
      '.ob-actions{display:flex;gap:10px;margin-top:8px}',
      '.ob-btn{flex:1;padding:13px;border:none;border-radius:12px;font-family:var(--font-b);',
      'font-weight:600;font-size:.88rem;cursor:pointer}',
      '.ob-btn-ghost{background:rgba(255,255,255,.06);color:var(--text-secondary);',
      'border:1px solid rgba(255,255,255,.12)}',
      '.ob-btn-primary{background:linear-gradient(135deg,#7c3aed,#a855f7);color:#fff;',
      'box-shadow:0 4px 16px rgba(124,58,237,.4)}',
    ].join('');
    document.head.appendChild(s);
  }

  function paintProUI() {
    var p = readLocalPro();
    var btn = document.getElementById('headerProBtn');
    var side = document.getElementById('sidebarProStatus');

    if (p && p.expiresAt && Date.now() < p.expiresAt) {
      var until = formatUntil(p.expiresAt);
      if (btn) {
        btn.classList.add('is-active');
        btn.innerHTML =
          '<span class="pro-dot"></span>Active until ' + until;
        btn.setAttribute('aria-label', 'Pro active until ' + until);
        btn.title = (p.planName || 'Pro') + ' · Active until ' + until;
      }
      if (side) {
        side.classList.add('pro-active');
        side.textContent =
          '✓ ' + (p.planName || 'Pro') + ' · Active until ' + until;
      }
    } else {
      if (btn) {
        btn.classList.remove('is-active');
        btn.textContent = 'Pro';
        btn.setAttribute('aria-label', 'SKONGA Pro');
        btn.title = 'Upgrade to Pro';
      }
      if (side) {
        side.classList.remove('pro-active');
        side.textContent = 'Choose a plan — pay with M-Pesa, Tigo, Airtel or Halo.';
      }
    }
  }

  async function fetchProStatus() {
    var q = new URLSearchParams();
    var s = sessionId();
    var u = uid();
    if (s) q.set('sessionId', s);
    if (u) q.set('uid', u);
    if (!s && !u) return null;
    var res = await fetch(API + '/api/payments/pro?' + q.toString(), {
      credentials: 'omit',
      cache: 'no-store',
    });
    if (!res.ok) return null;
    return res.json();
  }

  async function syncOrder(orderId) {
    if (!orderId) return null;
    var res = await fetch(API + '/api/payments/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        orderId: orderId,
        sessionId: sessionId() || undefined,
        uid: uid() || undefined,
      }),
    });
    var data = await res.json().catch(function () {
      return {};
    });
    if (!res.ok) throw new Error(data.error || 'Sync failed');
    return data;
  }

  async function statusOrder(orderId) {
    if (!orderId) return null;
    var q = new URLSearchParams();
    var s = sessionId();
    var u = uid();
    if (s) q.set('sessionId', s);
    if (u) q.set('uid', u);
    var res = await fetch(
      API + '/api/payments/status/' + encodeURIComponent(orderId) + '?' + q.toString(),
      { cache: 'no-store' }
    );
    if (!res.ok) return null;
    return res.json();
  }

  function applyProFromServer(pro, orderId) {
    if (!pro || !pro.active || !pro.expiresAt) return false;
    writeLocalPro({
      planId: pro.planId,
      planName: pro.planName,
      expiresAt: pro.expiresAt,
      orderId: orderId || pro.orderId,
    });
    return true;
  }

  /** Aggressive poll: status + pro + sync */
  async function robustPoll(orderId, maxAttempts) {
    var n = maxAttempts || 40; // ~2 min at 3s
    for (var i = 0; i < n; i++) {
      await new Promise(function (r) {
        setTimeout(r, 3000);
      });
      try {
        if (orderId) {
          var st = await statusOrder(orderId);
          if (st && st.pro && applyProFromServer(st.pro, orderId)) {
            onProUnlocked(st.pro);
            return true;
          }
          if (st && st.order && st.order.status === 'paid') {
            var syn = await syncOrder(orderId);
            if (syn && syn.pro && applyProFromServer(syn.pro, orderId)) {
              onProUnlocked(syn.pro);
              return true;
            }
          }
        }
        var pro = await fetchProStatus();
        if (pro && applyProFromServer(pro, orderId)) {
          onProUnlocked(pro);
          return true;
        }
      } catch (e) {}
    }
    return false;
  }

  function onProUnlocked(pro) {
    try {
      var icon = document.getElementById('payResultIcon');
      var title = document.getElementById('payResultTitle');
      var sub = document.getElementById('payResultSub');
      if (icon) icon.textContent = '✅';
      if (title) title.textContent = 'Payment confirmed';
      if (sub) {
        sub.textContent =
          (pro.planName || 'Pro') +
          ' is active until ' +
          formatUntil(pro.expiresAt);
      }
      enhancePayResultBar(true);
    } catch (e) {}
    try {
      if (typeof showToast === 'function') {
        showToast('SKONGA Pro activated · Active until ' + formatUntil(pro.expiresAt));
      }
    } catch (e2) {}
    paintProUI();
  }

  function enhancePayResultBar(unlocked) {
    var step = document.getElementById('payStepResult');
    if (!step) return;
    var bar = document.getElementById('payUnlockBar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'payUnlockBar';
      bar.className = 'pay-unlock-bar';
      var actions = step.querySelector('.pay-actions');
      if (actions) step.insertBefore(bar, actions);
      else step.appendChild(bar);
    }
    if (unlocked) {
      bar.innerHTML =
        '<p style="color:#34d399;font-weight:600;margin:0">✓ Pro unlocked on this device.</p>';
      return;
    }
    bar.innerHTML =
      '<p>Paid on your phone but still locked? Tap below — we re-check ClickPesa and unlock this device.</p>' +
      '<button type="button" class="pay-unlock-btn" id="payUnlockNowBtn">I paid — unlock now</button>';
    var b = document.getElementById('payUnlockNowBtn');
    if (b) {
      b.onclick = async function () {
        b.disabled = true;
        b.textContent = 'Checking payment…';
        try {
          var oid = localStorage.getItem(LAST_ORDER_KEY) || '';
          var ok = false;
          if (oid) {
            var syn = await syncOrder(oid);
            if (syn && syn.pro && applyProFromServer(syn.pro, oid)) ok = true;
          }
          if (!ok) {
            var pro = await fetchProStatus();
            if (pro && applyProFromServer(pro, oid)) ok = true;
          }
          if (ok) {
            onProUnlocked(readLocalPro() || {});
          } else {
            b.disabled = false;
            b.textContent = 'I paid — unlock now';
            if (typeof showToast === 'function') {
              showToast('Not confirmed yet. Finish PIN on phone, then try again.', true);
            }
          }
        } catch (err) {
          b.disabled = false;
          b.textContent = 'I paid — unlock now';
          if (typeof showToast === 'function') {
            showToast(err.message || 'Unlock failed', true);
          }
        }
      };
    }
  }

  function patchPayFlow() {
    // Stronger pollProUntilActive
    if (typeof window.pollProUntilActive === 'function' && !window.pollProUntilActive._robust) {
      window.pollProUntilActive = async function (u, sid, attempts) {
        var oid = '';
        try {
          oid = localStorage.getItem(LAST_ORDER_KEY) || '';
        } catch (e) {}
        enhancePayResultBar(false);
        var ok = await robustPoll(oid, attempts && attempts > 20 ? attempts : 40);
        if (!ok) enhancePayResultBar(false);
      };
      window.pollProUntilActive._robust = true;
    }

    // Capture orderId on initiate via fetch intercept for payments
    if (!window.__skongaPayFetchPatched) {
      window.__skongaPayFetchPatched = true;
      var origFetch = window.fetch.bind(window);
      window.fetch = function (input, init) {
        var url = typeof input === 'string' ? input : input && input.url ? input.url : '';
        var p = origFetch(input, init);
        if (url && url.indexOf('/api/payments/initiate') !== -1) {
          p.then(function (res) {
            try {
              var clone = res.clone();
              clone.json().then(function (data) {
                var oid = data && data.order && data.order.orderId;
                if (oid) {
                  try {
                    localStorage.setItem(LAST_ORDER_KEY, oid);
                  } catch (e) {}
                  setTimeout(function () {
                    enhancePayResultBar(false);
                    robustPoll(oid, 40);
                  }, 800);
                }
              });
            } catch (e) {}
          }).catch(function () {});
        }
        return p;
      };
    }

    // Patch updateSidebarProStatus to also paint header
    if (typeof window.updateSidebarProStatus === 'function' && !window.updateSidebarProStatus._paint) {
      var origUp = window.updateSidebarProStatus;
      window.updateSidebarProStatus = function () {
        var r = origUp.apply(this, arguments);
        paintProUI();
        return r;
      };
      window.updateSidebarProStatus._paint = true;
    }
  }

  async function launchProSync() {
    paintProUI();
    try {
      var pro = await fetchProStatus();
      if (pro && pro.active) {
        applyProFromServer(pro);
        return;
      }
      // Try last order
      var oid = localStorage.getItem(LAST_ORDER_KEY);
      if (oid) {
        var st = await statusOrder(oid);
        if (st && st.pro && st.pro.active) applyProFromServer(st.pro, oid);
      }
    } catch (e) {}
    paintProUI();
  }

  /* ═══════════ ONBOARDING ═══════════ */

  var combosCache = null;

  function loadCombos() {
    if (combosCache) return Promise.resolve(combosCache);
    return fetch(API + '/api/tahasusi', { credentials: 'omit' })
      .then(function (r) {
        return r.json();
      })
      .then(function (d) {
        combosCache = d.combinations || [];
        return combosCache;
      })
      .catch(function () {
        combosCache = [];
        return combosCache;
      });
  }

  function formNum(level) {
    var m = String(level || '').match(/form\s*([1-6])/i);
    return m ? Number(m[1]) : null;
  }

  function needsOnboarding() {
    try {
      if (localStorage.getItem(ONBOARD_DONE_KEY) === '1') return false;
      var extras = JSON.parse(localStorage.getItem(EXTRAS_KEY) || '{}');
      if (extras && extras.level) return false;
    } catch (e) {}
    return true;
  }

  function showOnboarding() {
    if (document.getElementById('skongaOnboard')) return;
    var root = document.createElement('div');
    root.id = 'skongaOnboard';
    root.innerHTML =
      '<div class="ob-sheet" role="dialog" aria-labelledby="obTitle">' +
      '<div class="ob-handle"></div>' +
      '<h2 class="ob-title" id="obTitle">Welcome to SKONGA AI</h2>' +
      '<p class="ob-sub">Set your class so suggestions and answers match your level. Takes 10 seconds.</p>' +
      '<div class="ob-field">' +
      '<label>Your class / form</label>' +
      '<select id="obLevel">' +
      '<option value="">Select your form...</option>' +
      '<option value="primary7">Standard 7 (PSLE)</option>' +
      '<option value="form1">Form 1</option>' +
      '<option value="form2">Form 2</option>' +
      '<option value="form3">Form 3</option>' +
      '<option value="form4">Form 4 (NECTA)</option>' +
      '<option value="form5">Form 5</option>' +
      '<option value="form6">Form 6 (ACSEE)</option>' +
      '</select></div>' +
      '<div id="obComboWrap">' +
      '<p class="ob-optional">Recommended for Form 5–6 · optional</p>' +
      '<div class="ob-field">' +
      '<label>What is your Combination?</label>' +
      '<select id="obCombo"><option value="">Optional — skip if unsure</option></select>' +
      '</div></div>' +
      '<div class="ob-actions">' +
      '<button type="button" class="ob-btn ob-btn-ghost" id="obSkip">Skip for now</button>' +
      '<button type="button" class="ob-btn ob-btn-primary" id="obSave">Continue</button>' +
      '</div></div>';
    document.body.appendChild(root);

    var levelEl = document.getElementById('obLevel');
    var comboWrap = document.getElementById('obComboWrap');
    var comboEl = document.getElementById('obCombo');

    function fillCombo() {
      loadCombos().then(function (list) {
        var groups = {};
        (list || []).forEach(function (c) {
          var cat = c.categoryNameEn || c.categoryNameSw || 'Other';
          if (!groups[cat]) groups[cat] = [];
          groups[cat].push(c);
        });
        var html = '<option value="">Optional — skip if unsure</option>';
        Object.keys(groups).forEach(function (cat) {
          html += '<optgroup label="' + cat.replace(/"/g, '') + '">';
          groups[cat].forEach(function (c) {
            html +=
              '<option value="' +
              c.code +
              '">' +
              c.code +
              ' — ' +
              (c.subjects || []).join(', ') +
              '</option>';
          });
          html += '</optgroup>';
        });
        if (comboEl) comboEl.innerHTML = html;
      });
    }

    levelEl.addEventListener('change', function () {
      var n = formNum(levelEl.value);
      if (n === 5 || n === 6) {
        comboWrap.classList.add('show');
        fillCombo();
        setTimeout(function () {
          try {
            comboEl.focus();
          } catch (e) {}
        }, 50);
      } else {
        comboWrap.classList.remove('show');
      }
    });

    function finish(save) {
      if (save) {
        var level = levelEl.value || '';
        var code = (comboEl && comboEl.value) || '';
        var n = formNum(level);
        if (n && n < 5) code = '';
        var subjects = [];
        if (code && combosCache) {
          var found = combosCache.find(function (c) {
            return String(c.code).toUpperCase() === String(code).toUpperCase();
          });
          if (found) subjects = found.subjects || [];
        }
        try {
          var extras = {};
          try {
            extras = JSON.parse(localStorage.getItem(EXTRAS_KEY) || '{}') || {};
          } catch (e) {}
          extras.level = level;
          extras.levelLabel = LEVEL_LABELS[level] || level || '—';
          extras.combinationCode = code;
          extras.preferredSubjects = subjects;
          localStorage.setItem(EXTRAS_KEY, JSON.stringify(extras));
          if (typeof currentUser !== 'undefined' && currentUser) {
            currentUser.level = level;
            currentUser.levelLabel = extras.levelLabel;
          }
          if (window.SKONGA_PROFILE && typeof SKONGA_PROFILE.save === 'function') {
            SKONGA_PROFILE.save(extras);
          }
        } catch (e2) {}
      }
      try {
        localStorage.setItem(ONBOARD_DONE_KEY, '1');
      } catch (e3) {}
      root.classList.add('hidden');
      setTimeout(function () {
        try {
          root.remove();
        } catch (e4) {}
      }, 200);
    }

    document.getElementById('obSkip').onclick = function () {
      finish(false);
    };
    document.getElementById('obSave').onclick = function () {
      if (!levelEl.value) {
        if (typeof showToast === 'function') showToast('Select your form to continue.', true);
        return;
      }
      finish(true);
    };
  }

  function boot() {
    injectProCSS();
    patchPayFlow();
    paintProUI();
    setTimeout(launchProSync, 1200);
    setTimeout(launchProSync, 5000);

    // Re-patch when main pay functions appear
    var tries = 0;
    var t = setInterval(function () {
      tries++;
      patchPayFlow();
      paintProUI();
      if (tries > 30) clearInterval(t);
    }, 400);

    setTimeout(function () {
      if (needsOnboarding()) showOnboarding();
    }, 1600);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  window.SKONGA_PRO_UI = {
    paint: paintProUI,
    sync: launchProSync,
    poll: robustPoll,
  };
})();
