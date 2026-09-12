/**
 * skonga-usage-identity.js
 * Ensures every request to skonga-backend-v2 carries the logged-in user id
 * so usage_events / DAU / quotas work on auth-content.
 *
 * - Header: X-Skonga-User-Id
 * - JSON body: userId (+ sessionId when missing)
 * Safe no-op when user is logged out.
 */
(function () {
  'use strict';

  var BACKEND_HINTS = [
    'skonga-backend-v2',
    '/api/chat',
    '/api/vision',
    '/api/image',
    '/api/chat-search',
    '/api/chat-title',
    '/api/payments',
  ];

  function isBackendUrl(url) {
    if (!url || typeof url !== 'string') return false;
    for (var i = 0; i < BACKEND_HINTS.length; i++) {
      if (url.indexOf(BACKEND_HINTS[i]) !== -1) return true;
    }
    return false;
  }

  function getUserId() {
    try {
      if (window._fb && window._fb.currentUser && window._fb.currentUser.uid) {
        return String(window._fb.currentUser.uid).slice(0, 128);
      }
    } catch (e) {}
    try {
      var raw = localStorage.getItem('skonga_auth_user');
      if (raw) {
        var u = JSON.parse(raw);
        if (u && u.id) return String(u.id).slice(0, 128);
      }
    } catch (e2) {}
    return null;
  }

  function getSessionId() {
    try {
      if (typeof DEVICE_SESSION_ID !== 'undefined' && DEVICE_SESSION_ID) {
        return String(DEVICE_SESSION_ID).slice(0, 128);
      }
    } catch (e) {}
    try {
      return localStorage.getItem('skonga_device_session') || null;
    } catch (e2) {
      return null;
    }
  }

  var origFetch = window.fetch;
  if (!origFetch) return;

  window.fetch = function (input, init) {
    init = init ? Object.assign({}, init) : {};
    var url =
      typeof input === 'string'
        ? input
        : input && typeof input.url === 'string'
          ? input.url
          : '';

    if (!isBackendUrl(url)) {
      return origFetch.call(this, input, init);
    }

    var uid = getUserId();
    var sid = getSessionId();

    // Headers
    var headers;
    try {
      headers = new Headers(init.headers || (input && input.headers) || {});
    } catch (e) {
      headers = new Headers();
    }
    if (uid && !headers.has('X-Skonga-User-Id')) {
      headers.set('X-Skonga-User-Id', uid);
    }
    init.headers = headers;

    // JSON body enrichment
    if (init.body && typeof init.body === 'string') {
      try {
        var j = JSON.parse(init.body);
        if (j && typeof j === 'object' && !Array.isArray(j)) {
          if (uid && !j.userId) j.userId = uid;
          if (sid && !j.sessionId) j.sessionId = sid;
          // payments use uid field
          if (uid && !j.uid && url.indexOf('/api/payments') !== -1) j.uid = uid;
          init.body = JSON.stringify(j);
        }
      } catch (e3) {
        /* non-JSON body (FormData etc.) — header still applied */
      }
    }

    return origFetch.call(this, input, init);
  };

  console.info('[SKONGA] usage-identity: userId header/body injection active');
})();
