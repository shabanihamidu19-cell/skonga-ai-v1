#!/usr/bin/env python3
"""
Replace Firebase auth module with SKONGA auth-content-service client.
Keeps window._fb API so the rest of the app does not break.
"""
from pathlib import Path
import re
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "www/index.html")
html = p.read_text(encoding="utf-8")

AUTH_MODULE = r'''<script type="module">
/* SKONGA Auth — auth-content-service (Firebase disabled for trials)
   Same window._fb bridge shape so main UI code stays unchanged. */
const AUTH_BASE = 'https://skonga-auth-content-service.onrender.com';
const LS_TOKEN = 'skonga_auth_token';
const LS_USER  = 'skonga_auth_user';

const AUTH_ERRORS = {
  INVALID_EMAIL: 'Invalid email address.',
  WEAK_PASSWORD: 'Password must be at least 6 characters.',
  EMAIL_EXISTS: 'This email already has an account.',
  INVALID_CREDENTIALS: 'Invalid email or password.',
  UNAUTHORIZED: 'Session expired. Please sign in again.',
  NETWORK: 'No network connection. Check your internet.',
};
const authErr = (code, fallback) => AUTH_ERRORS[code] || fallback || 'An error occurred. Please try again.';

function loadStored() {
  try {
    const token = localStorage.getItem(LS_TOKEN);
    const userRaw = localStorage.getItem(LS_USER);
    const user = userRaw ? JSON.parse(userRaw) : null;
    return { token, user };
  } catch {
    return { token: null, user: null };
  }
}

function saveSession(token, user) {
  if (token) localStorage.setItem(LS_TOKEN, token);
  else localStorage.removeItem(LS_TOKEN);
  if (user) localStorage.setItem(LS_USER, JSON.stringify(user));
  else localStorage.removeItem(LS_USER);
}

function toFbUser(user) {
  if (!user) return null;
  return {
    uid: user.id,
    email: user.email,
    displayName: user.name || (user.email ? user.email.split('@')[0] : 'User'),
    photoURL: null,
    providerData: [{ providerId: 'password' }],
  };
}

function emitAuth(user) {
  window._fb.currentUser = user;
  window.dispatchEvent(new CustomEvent('fbAuthChanged', { detail: user }));
}

async function api(path, { method = 'GET', body, token } = {}) {
  const headers = { 'Content-Type': 'application/json', Accept: 'application/json' };
  if (token) headers.Authorization = 'Bearer ' + token;
  let res;
  try {
    res = await fetch(AUTH_BASE + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    const err = new Error('network');
    err.code = 'NETWORK';
    throw err;
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.error || 'Request failed');
    err.code = data.code || 'ERROR';
    err.status = res.status;
    throw err;
  }
  return data;
}

const stored = loadStored();

window._fb = {
  ready: true,
  currentUser: toFbUser(stored.user),
  idToken: stored.token || null,
  authBase: AUTH_BASE,
  err: (code) => authErr(code),

  async signIn(email, pass) {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: { email, password: pass },
    });
    saveSession(data.token, data.user);
    window._fb.idToken = data.token;
    const u = toFbUser(data.user);
    emitAuth(u);
    return { user: u };
  },

  async signUp(name, email, pass) {
    const data = await api('/api/auth/signup', {
      method: 'POST',
      body: { email, password: pass, name },
    });
    saveSession(data.token, data.user);
    window._fb.idToken = data.token;
    const u = toFbUser(data.user);
    emitAuth(u);
    return { user: u };
  },

  async signInGoogle() {
    const err = new Error('Google sign-in disabled');
    err.code = 'auth/operation-not-allowed';
    throw err;
  },

  async logout() {
    saveSession(null, null);
    window._fb.idToken = null;
    emitAuth(null);
  },

  async refreshToken() {
    const token = localStorage.getItem(LS_TOKEN);
    if (!token) return null;
    try {
      const data = await api('/api/auth/me', { token });
      if (data.user) {
        saveSession(token, data.user);
        const u = toFbUser(data.user);
        window._fb.currentUser = u;
        window._fb.idToken = token;
        return token;
      }
    } catch {
      saveSession(null, null);
      window._fb.idToken = null;
      emitAuth(null);
    }
    return null;
  },
};

// Restore session into profile UI
if (window._fb.currentUser) {
  queueMicrotask(() => emitAuth(window._fb.currentUser));
} else {
  queueMicrotask(() => emitAuth(null));
}

console.info('[SKONGA Auth] Using auth-content-service →', AUTH_BASE);
</script>'''

# Replace first type=module script block (Firebase)
pat = re.compile(
    r'<script type="module">.*?</script>',
    re.DOTALL,
)
m = pat.search(html)
if not m:
    print("FAIL: no type=module script found")
    sys.exit(1)

html = html[: m.start()] + AUTH_MODULE + html[m.end() :]
print("OK: Firebase module → auth-content client")

# Ensure AUTH note near API_BASE
if "AUTH_BASE" not in html.split("API_BASE")[0][-200:]:
    html = html.replace(
        "const API_BASE = 'https://skonga-backend-v2.onrender.com';",
        "const API_BASE = 'https://skonga-backend-v2.onrender.com';\n"
        "// Auth: handled by module script → auth-content-service (not Firebase)\n"
        "// const AUTH_BASE = 'https://skonga-auth-content-service.onrender.com';",
        1,
    )
    print("OK: API_BASE comment")

# userId already may be wired; ensure pattern exists
if "userId: (window._fb && window._fb.currentUser" not in html:
    old = """formHint: getStudentFormHint(),
      })"""
    new = """formHint: getStudentFormHint(),
        userId: (window._fb && window._fb.currentUser && window._fb.currentUser.uid) || null,
      })"""
    if old in html:
        html = html.replace(old, new, 1)
        print("OK: userId on chat")
    else:
        print("SKIP: chat body")
else:
    print("OK: userId already present")

# Friendlier Google error (if button still visible)
html = html.replace(
    "showToast(window._fb.err(e.code), true)",
    "showToast(e.code==='auth/operation-not-allowed'?'Google sign-in is off. Use email.':(window._fb.err(e.code)||e.message), true)",
    1,
)

p.write_text(html, encoding="utf-8")
print("Wrote", p.resolve())
