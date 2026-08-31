/* SKONGA AI — APK / web update checker (VidMate-style)
 * Include before </body>: <script src="./update-check.js"></script>
 *
 * On launch, fetches version.json from GitHub. If remote version is newer
 * than APP_VERSION, shows a dialog and opens the APK download URL.
 *
 * Also loads skonga-ux-hooks.js (Pro expiry reminder, limit→Pro, AI notify).
 */
(function () {
  var VERSION_URL =
    'https://raw.githubusercontent.com/shabanihamidu19-cell/skonga-ai-v1/main/version.json';
  var CHECK_DELAY_MS = 2500;
  var SNOOZE_KEY = 'skonga_update_snooze_until';
  var SNOOZE_HOURS = 24;

  function currentVersion() {
    if (typeof APP_VERSION !== 'undefined' && APP_VERSION) return String(APP_VERSION);
    return '0.0.0';
  }

  function cmpVersion(a, b) {
    var pa = String(a || '0').split('.').map(function (x) { return parseInt(x, 10) || 0; });
    var pb = String(b || '0').split('.').map(function (x) { return parseInt(x, 10) || 0; });
    var n = Math.max(pa.length, pb.length);
    for (var i = 0; i < n; i++) {
      var x = pa[i] || 0;
      var y = pb[i] || 0;
      if (x > y) return 1;
      if (x < y) return -1;
    }
    return 0;
  }

  function isSnoozed() {
    try {
      var until = parseInt(localStorage.getItem(SNOOZE_KEY) || '0', 10);
      return until && Date.now() < until;
    } catch (e) {
      return false;
    }
  }

  function snooze() {
    try {
      localStorage.setItem(
        SNOOZE_KEY,
        String(Date.now() + SNOOZE_HOURS * 60 * 60 * 1000)
      );
    } catch (e) {}
  }

  function openUrl(url) {
    if (!url) return;
    try {
      if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Browser) {
        window.Capacitor.Plugins.Browser.open({ url: url });
        return;
      }
    } catch (e) {}
    try {
      window.open(url, '_blank');
    } catch (e2) {
      window.location.href = url;
    }
  }

  function showUpdateUI(remote) {
    var body =
      'SKONGA AI ' +
      (remote.version || '') +
      ' is ready.\n\n' +
      (remote.message || 'Bug fixes and improvements.') +
      '\n\nDownload and install the new APK?';

    var go = false;
    try {
      go = window.confirm(body);
    } catch (e) {
      go = true;
    }

    if (go && remote.apkUrl) {
      openUrl(remote.apkUrl);
    } else {
      snooze();
    }

    try {
      if (typeof showToast === 'function' && remote.version) {
        showToast('Update ' + remote.version + ' available');
      }
    } catch (e) {}
  }

  async function checkAppUpdate() {
    if (isSnoozed()) return;
    var local = currentVersion();
    try {
      var res = await fetch(VERSION_URL + '?t=' + Date.now(), {
        cache: 'no-store',
        credentials: 'omit',
      });
      if (!res.ok) return;
      var remote = await res.json();
      if (!remote || !remote.version) return;

      if (cmpVersion(remote.version, local) > 0) {
        showUpdateUI(remote);
      }
    } catch (e) {}
  }

  function schedule() {
    setTimeout(function () {
      checkAppUpdate();
    }, CHECK_DELAY_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', schedule);
  } else {
    schedule();
  }

  window.checkAppUpdate = checkAppUpdate;

  // Load UX hooks (Pro expiry, limit → Pro panel, AI reply notify)
  try {
    if (!document.querySelector('script[src*="skonga-ux-hooks"]')) {
      var s = document.createElement('script');
      s.src = './skonga-ux-hooks.js';
      s.async = false;
      (document.body || document.documentElement).appendChild(s);
    }
  } catch (e) {}
})();
