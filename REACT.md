# SKONGA AI — React + React Native + TypeScript

Rewrite of the Capacitor `www/` shell.

| App | Stack | Path |
| --- | --- | --- |
| Web | React 18 + Vite + TypeScript | `apps/web` |
| Mobile | React Native (Expo 52) + TypeScript | `apps/mobile` |
| Shared | plans, chat mock, types, limits | `packages/shared` |

Capacitor Android files (`www/`, `capacitor.config.json`) remain on this branch so the existing APK path is not deleted.

## Run the new stack

```bash
cp package.workspaces.json package.json   # or merge workspaces into package.json
npm install
npm run web          # http://localhost:5173
npm run mobile       # Expo
```

## Ported UI

- Chat + New Chat + local history
- Soft free limit (8 messages) then Pro sheet
- Plans: 1 Day 620 · 1 Week 3,500 · 1 Month 5,000 · 1 Year 45,000
- Network detect: M-Pesa / Tigo / Airtel / HaloPesa
- Settings + Profile placeholders

Chat and STK are still mocks. Do not put API secrets in the client.
