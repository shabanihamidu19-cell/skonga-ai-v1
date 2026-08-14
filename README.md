# SKONGA AI

Tanzanian student AI assistant — Capacitor Android shell + web UI, soft free limits, **mobile-money payments** (M-Pesa, Tigo, Airtel, Halo).

**Owner:** KCL Platform TZ · **Repo:** [skonga-ai-v1](https://github.com/shabanihamidu19-cell/skonga-ai-v1)

---

## Status (August 2026)

| Layer | State | Notes |
|--------|--------|--------|
| **Frontend (www)** | ~95% | English UI, Pro header, in-app pay sheet, Settings/Profile, theme, preferred name |
| **Legal pages** | Ready to host | `legal/` — Terms + Privacy (EN + SW). Deploy separately; app opens in browser |
| **Capacitor / APK** | CI builds debug | `.github/workflows/build-android.yml` → artifact `skonga-ai-debug-apk` |
| **Firebase config** | Template only | `android-config/google-services.json` — replace with real project values |
| **Backend / API** | **Not built** | Chat, STK Push, Pro entitlements, auth still client/local or mock |
| **Release signing** | Optional | Needs GitHub Secrets for signed release APK |

**Remaining to production:** backend + real STK + real AI API + legal deploy + signed APK + store listing.

---

## What's in the app today

- Chat UI (no mock history on first open)
- Soft free-message limit → polite English message → **Pro** (not forced)
- **Pro plans (in-app sheet):** 1 Day TSh 620 · 1 Week 3,500 · 1 Month 5,000 · 1 Year 45,000
- Phone + network detect → Confirm → STK flow UI (still needs live payment API)
- Sidebar: New Chat, history, Profile + Settings at bottom
- Header **Pro** button
- Theme: Dark / Light / Auto
- "How should SKONGA call you?" + welcome greeting
- Terms / Privacy open **external browser** (not in-app legal body)
- Clear history stays in Settings
- Profile sheet (email login UI; Firebase hooks partially present)
- Android back closes sheets before exiting (requires `@capacitor/app` + rebuild)
- Offline banner when network is down

### Known fixes applied via scripts

Run after `git pull` if your local `www/index.html` is older:

```bash
python3 scripts/restore_and_keep_ui.py   # only if index was truncated (~22KB)
python3 scripts/fix_profile.py
python3 scripts/fix_panels_close.py
```

Then commit + push + rebuild APK.

---

## Project structure

```
skonga-ai-v1/
├── www/
│   ├── index.html      # Main SPA (chat, pay sheet, settings, profile)
│   ├── pay.html        # Standalone pay page (fallback / browser)
│   ├── manifest.json
│   ├── sw.js
│   └── icon-512.png
├── legal/              # Static Terms & Privacy (EN + SW) — host on Pages/Firebase
│   ├── index.html
│   ├── terms.html / terms-sw.html
│   ├── privacy.html / privacy-sw.html
│   └── assets/
├── resources/          # Icon + splash masters for Capacitor assets
├── android-config/
│   └── google-services.json   # TEMPLATE — do not ship secrets in public forks
├── scripts/            # One-shot HTML patch helpers (Termux-friendly)
├── .github/workflows/
│   └── build-android.yml
├── capacitor.config.json
├── package.json
└── README.md
```

---

## Plans (client-side constants)

| Plan   | Price (TZS) | Duration |
|--------|-------------|----------|
| 1 Day  | 620         | 24 hours |
| 1 Week | 3,500       | 7 days   |
| 1 Month| 5,000       | 30 days  |
| 1 Year | 45,000      | 365 days |

Pro state is stored in `localStorage` (`skonga_pro`) until backend verifies STK + issues entitlement.

---

## Build APK

### GitHub Actions (recommended)

1. Push to `main` (or **Actions → Build Android APK → Run workflow**)
2. Download artifact **skonga-ai-debug-apk**
3. Install on device (allow unknown sources)

### Local / Termux (advanced)

```bash
npm install
npx cap add android    # once
npx cap sync android
cd android && ./gradlew assembleDebug
```

Signed release needs repo secrets:  
`ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`.

---

## Legal (your zip)

Source: `legal/` (from `skonga-legal.zip`).

| File | Purpose |
|------|--------|
| `legal/index.html` | Legal center hub |
| `legal/terms.html` | Terms (English) |
| `legal/privacy.html` | Privacy (English) |
| `legal/terms-sw.html` | Masharti (Kiswahili) |
| `legal/privacy-sw.html` | Sera ya Faragha (Kiswahili) |

**Placeholders** filled with defaults (`support@skonga.ai`, `privacy@skonga.ai`, `https://skonga-ai.web.app`, date **14 August 2026**).  
**Before public launch:** replace emails, website URL, AI providers, payment providers, and retention text so they match the **live** backend.

### Deploy legal (example)

```bash
# Firebase Hosting (example)
firebase deploy --only hosting
# or GitHub Pages / Netlify / Cloudflare Pages — publish the legal/ folder
```

Point app links (`EXTERNAL_LEGAL` in `www/index.html`) to:

- Terms: `https://<your-domain>/terms.html`
- Privacy: `https://<your-domain>/privacy.html`

---

## Backend & API — what is still missing

The app UI is ready to wire. Nothing below is production-complete yet.

| Service | Purpose | Suggested approach |
|---------|---------|-------------------|
| **Chat API** | Stream / reply for student questions | HTTPS API + your chosen LLM (do not put API keys in the APK) |
| **Auth** | Email (and optional Google) session | Firebase Auth or custom JWT |
| **Entitlements** | Server truth for Pro / free quota | After STK success, set `pro_until` on user |
| **STK Push** | Real M-Pesa / Tigo / Airtel / Halo | Aggregator (e.g. Selcom, ClickPesa, Flutterwave, or operator APIs) + callback URL |
| **Webhook** | Payment confirmation | Idempotent update of subscription |
| **Rate limits** | Free tier enforcement | Per device/account daily counters on server |
| **Legal / support** | Hosted terms + contact | Static `legal/` + support inbox |

**Never** ship LLM or payment secrets inside `www/` or the APK. Use a backend proxy.

---

## My tasks (owner checklist)

Use this as the live work queue. Check off as you go.

### A. Frontend / APK (almost done)

- [ ] Run `fix_profile.py` + `fix_panels_close.py` on device tree; confirm Profile opens and Pro **X** closes
- [ ] Confirm Android **back** closes sheets (after rebuild with `@capacitor/app`)
- [ ] Replace `android-config/google-services.json` with real Firebase Android app config (`tz.co.kclplatform.skonga` or your package)
- [ ] Align `capacitor.config.json` `appId` with Play Console package name
- [ ] Generate final icons/splash from `resources/` in CI (already attempted in workflow)
- [ ] Remove offline false-positives if any (banner when online)
- [ ] Smoke-test: New Chat, Settings theme, preferred name, Clear History, Pro flow UI

### B. Legal & trust

- [ ] Deploy `legal/` to production HTTPS domain
- [ ] Update `EXTERNAL_LEGAL` URLs in `www/index.html` to that domain
- [ ] Replace placeholder provider names with real AI + payment vendors
- [ ] Confirm support / privacy email inboxes exist and are monitored
- [ ] (Optional) Lawyer review of Terms/Privacy for Tanzania + app stores

### C. Backend (next major phase)

- [ ] Design API: `POST /chat`, `GET /me`, `POST /pay/stk`, `POST /pay/callback`, `GET /entitlement`
- [ ] Implement STK initiate + callback; store payment reference + plan + phone
- [ ] Issue Pro entitlement only after confirmed payment
- [ ] Proxy LLM calls; log usage for free-tier limits
- [ ] Secure CORS + auth for mobile origin
- [ ] Staging environment + test numbers for mobile money

### D. Release

- [ ] Create upload keystore; add GitHub Actions secrets; build **signed** release APK/AAB
- [ ] Play Console listing (screenshots, description EN/SW, content rating, privacy policy URL)
- [ ] Privacy policy URL must match deployed `legal/privacy.html`
- [ ] Internal testing track → production

### E. Ops

- [ ] Crash/analytics (optional Firebase Crashlytics) — after privacy text matches
- [ ] Support channel (email / WhatsApp business)
- [ ] Backup strategy for payment and user tables

---

## Quick Termux sync

```bash
cd ~/skonga-ai-v1
git pull origin main
python3 scripts/fix_profile.py
python3 scripts/fix_panels_close.py
git add -A
git status
git commit -m "Sync fixes + legal + README tasks"
git push origin main
```

---

## License

MIT — KCL Platform TZ  
Legal documents in `legal/` are product policies, not the MIT license text.
