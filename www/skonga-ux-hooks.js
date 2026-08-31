/* SKONGA UX hooks — Pro expiry reminder, AI-done notify, limit → Pro panel
 * Load after index.html main scripts (before </body>).
 */
(function () {
  var PRO_NOTIF_ID = 880011;
  var PRO_SOON_NOTIF_ID = 880012;
  var PRO_EXPIRED_FLAG = 'skonga_pro_expired_toast_at';

  function openPro() {
    try {
      if (typeof openSkongaPay === 'function') openSkongaPay();
      else if (typeof openPaySheet === 'function') openPaySheet();
    } catch (e) {}
  }

  function lnPlugin() {
    try {
      return window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.LocalNotifications;
    } catch (e) {
      return null;
    }
  }

  function isNative() {
    return typeof isNativeApp !== 'undefined'
      ? isNativeApp
      : !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());
  }

  async function scheduleAt(id, title, body, whenMs) {
    var at = new Date(whenMs);
    if (!(at.getTime() > Date.now() + 5000)) return;
    var LN = lnPlugin();
    if (LN && typeof LN.schedule === 'function') {
      try {
        if (typeof ensureNotifyChannels === 'function') await ensureNotifyChannels();
        await LN.cancel({ notifications: [{ id: id }] }).catch(function () {});
        await LN.schedule({
          notifications: [
            {
              id: id,
              title: title,
              body: body,
              schedule: { at: at, allowWhileIdle: true },
              extra: { type: 'pro_expiry' },
            },
          ],
        });
        return;
      } catch (e) {
        console.warn('[skonga-ux] LN.schedule', e);
      }
    }
    try {
      var delay = at.getTime() - Date.now();
      if (delay > 0 && delay < 2147483647) {
        setTimeout(function () {
          try {
            if (typeof showToast === 'function') showToast(title + ' — ' + body, true);
          } catch (e2) {}
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, { body: body, tag: 'skonga-pro-' + id });
          }
        }, delay);
      }
    } catch (e3) {}
  }

  window.scheduleProExpiryReminder = function scheduleProExpiryReminder(expiresAt, planName) {
    if (!expiresAt) return;
    var t = typeof expiresAt === 'number' ? expiresAt : Date.parse(expiresAt);
    if (!t || isNaN(t)) return;
    var name = planName || 'Pro';
    scheduleAt(
      PRO_NOTIF_ID,
      'SKONGA Pro imeisha',
      (name + ' imekwisha. Fungua app ulipie tena ili uendelee.').slice(0, 120),
      t
    );
    if (t - Date.now() > 26 * 60 * 60 * 1000) {
      scheduleAt(
        PRO_SOON_NOTIF_ID,
        'SKONGA Pro inaisha hivi karibuni',
        (name + ' inaisha baada ya saa 12. Lipia mapema usikose masomo.').slice(0, 120),
        t - 12 * 60 * 60 * 1000
      );
    }
  };

  function readPro() {
    try {
      var key = typeof PRO_STORAGE_KEY !== 'undefined' ? PRO_STORAGE_KEY : 'skonga_pro';
      return JSON.parse(localStorage.getItem(key) || 'null');
    } catch (e) {
      return null;
    }
  }

  function onLaunchCheckProExpiry() {
    var p = readPro();
    if (!p || !p.expiresAt) return;
    var t = typeof p.expiresAt === 'number' ? p.expiresAt : Date.parse(p.expiresAt);
    if (!t || isNaN(t)) return;
    if (t > Date.now()) {
      scheduleProExpiryReminder(t, p.planName);
      return;
    }
    try {
      var day = String(new Date().toDateString());
      if (localStorage.getItem(PRO_EXPIRED_FLAG) === day) return;
      localStorage.setItem(PRO_EXPIRED_FLAG, day);
      if (typeof showToast === 'function') {
        showToast('Kifurushi cha Pro kimeisha — bonyeza Pro ulipie tena', true);
      }
    } catch (e) {}
  }

  function enhanceUpgradeCard() {
    if (typeof showUpgradeCard !== 'function' || window.__skongaUpgradePatched) return;
    window.__skongaUpgradePatched = true;
    var orig = showUpgradeCard;
    window.showUpgradeCard = function (originalText) {
      orig(originalText);
      try {
        var cards = document.querySelectorAll('.upgrade-card');
        var card = cards[cards.length - 1];
        if (!card) return;
        card.style.cursor = 'pointer';
        card.setAttribute('role', 'button');
        card.onclick = function (ev) {
          if (ev.target && ev.target.closest && ev.target.closest('button')) return;
          openPro();
        };
        var title = card.querySelector('.upgrade-card-title');
        if (title) {
          title.style.textDecoration = 'underline';
          title.style.cursor = 'pointer';
        }
        if (!card.querySelector('.skonga-limit-hint')) {
          var hint = document.createElement('p');
          hint.className = 'skonga-limit-hint';
          hint.style.cssText = 'font-size:.72rem;color:var(--purple-light);margin:6px 0 0;cursor:pointer';
          hint.textContent = 'Bonyeza hapa au Pay now kufungua Pro';
          hint.onclick = function (e) {
            e.stopPropagation();
            openPro();
          };
          card.appendChild(hint);
        }
      } catch (e) {}
    };
  }

  function enhanceRouteError() {
    if (typeof routeError !== 'function' || window.__skongaRouteErrPatched) return;
    window.__skongaRouteErrPatched = true;
    var orig = routeError;
    window.routeError = function (err, originalText) {
      var msg = (err && err.message) || '';
      var isLimit = /quota|free limit|kikomo|limit reached|QUOTA|upgrade to pro|Daily free/i.test(msg);
      if (isLimit && typeof showUpgradeCard === 'function') {
        try {
          showUpgradeCard(originalText || '');
          return;
        } catch (e) {}
      }
      return orig(err, originalText);
    };
  }

  function enhanceAiNotify() {
    if (typeof showLocalNotificationIfHidden !== 'function' || window.__skongaAiNotifyPatched) return;
    window.__skongaAiNotifyPatched = true;
    var orig = showLocalNotificationIfHidden;
    window.showLocalNotificationIfHidden = async function (replyText) {
      try {
        await orig(replyText);
      } catch (e) {}
      try {
        var enabled = typeof appSettings !== 'undefined' && appSettings.notificationsEnabled;
        if (!enabled || !document.hidden) return;
        var LN = lnPlugin();
        if (!(isNative() && LN && typeof LN.schedule === 'function')) return;
        var preview =
          (replyText || '').replace(/\n+/g, ' ').slice(0, 90) +
          (replyText && replyText.length > 90 ? '...' : '');
        await LN.schedule({
          notifications: [
            {
              id: (Date.now() % 2000000000) + 1,
              title: 'SKONGA AI — jibu liko tayari',
              body: preview || 'AI imemaliza kujibu.',
              schedule: { at: new Date(Date.now() + 500) },
            },
          ],
        });
      } catch (e2) {}
    };
  }

  function wrapSavePro() {
    if (typeof savePro === 'function' && !window.__skongaSaveProPatched) {
      window.__skongaSaveProPatched = true;
      var orig = savePro;
      window.savePro = function (plan, phone) {
        var r = orig.apply(this, arguments);
        try {
          var p = readPro();
          if (p && p.expiresAt) scheduleProExpiryReminder(p.expiresAt, p.planName || (plan && plan.name));
        } catch (e) {}
        return r;
      };
    }
    if (typeof saveProFromServer === 'function' && !window.__skongaSaveProSrvPatched) {
      window.__skongaSaveProSrvPatched = true;
      var orig2 = saveProFromServer;
      window.saveProFromServer = function (pro, orderId) {
        var ok = orig2.apply(this, arguments);
        try {
          if (pro && pro.expiresAt) scheduleProExpiryReminder(pro.expiresAt, pro.planName);
        } catch (e) {}
        return ok;
      };
    }
  }

  function install() {
    enhanceUpgradeCard();
    enhanceRouteError();
    enhanceAiNotify();
    wrapSavePro();
    onLaunchCheckProExpiry();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      setTimeout(install, 0);
    });
  } else {
    setTimeout(install, 0);
  }
  setTimeout(install, 800);
  setTimeout(install, 2500);
})();
