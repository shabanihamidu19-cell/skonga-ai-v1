# SKONGA AI v1.0

Tanzanian student AI assistant (Capacitor Android) with **soft free limits** and **mobile-money payments** (M-Pesa, Tigo, Airtel, Halo).

## What's new in v1.0

- When free message limit is reached → polite Swahili message, **no forced upgrade**
- Pay via **M-Pesa / Tigo / Airtel / Halo** (`www/pay.html`)
- Demo/mock chat messages removed
- Google Sign-In removed from the app UI (email login only)
- Voice input off by default (unreliable on many Android WebViews)

## Setup

```bash
npm install
npx cap add android   # first time only
npx cap sync android
```

Open Android Studio → Run.

## Structure

- `www/index.html` — main app
- `www/pay.html` — SKONGA Pay (STK Push)
- `www/sw.js` — offline shell cache
- `capacitor.config.json` — Capacitor config

## License

MIT — KCL Platform TZ
