# resources/ — App icon & splash

Capacitor (`@capacitor/assets`) inasoma folder hii wakati wa build na kutengeneza icons + splash za Android zote (mipmap-*, drawable-*).

## Faili muhimu

| Faili | Ukubwa unaopendekezwa | Kazi |
|-------|----------------------|------|
| `icon.png` | ≥ **1024×1024** PNG | App icon (home screen) |
| `splash.png` | ≥ **2732×2732** PNG | Splash screen |
| `icon-foreground.png` | ≥ 1024×1024 | Adaptive icon (Android 8+) |
| `icon-background.png` | ≥ 1024×1024 | Adaptive icon background |
| `*-master.svg` | SVG | Source design (optional) |

## Jinsi ya kuweka PNG (hatua 1)

Repo ya zamani tayari ina PNG kamili:

https://github.com/shabanihamidu19-cell/skonga-app-updated/tree/main/resources

**Njia rahisi (simu/PC):**
1. Fungua link hapo juu
2. Pakua: `icon.png`, `splash.png`, `icon-foreground.png`, `icon-background.png`, `icon-only.png`
3. Repo `skonga-ai-v1` → folder `resources/` → **Add file → Upload files**
4. Commit

**Au kutoka Termux:**
```bash
cd skonga-ai-v1
mkdir -p resources
curl -L -o resources/icon.png https://raw.githubusercontent.com/shabanihamidu19-cell/skonga-app-updated/main/resources/icon.png
curl -L -o resources/splash.png https://raw.githubusercontent.com/shabanihamidu19-cell/skonga-app-updated/main/resources/splash.png
curl -L -o resources/icon-foreground.png https://raw.githubusercontent.com/shabanihamidu19-cell/skonga-app-updated/main/resources/icon-foreground.png
curl -L -o resources/icon-background.png https://raw.githubusercontent.com/shabanihamidu19-cell/skonga-app-updated/main/resources/icon-background.png
git add resources/
git commit -m "Add app icon and splash PNGs"
git push
```

## Build (hatua 2)

GitHub Actions tayari ina hatua:

```bash
npx @capacitor/assets generate --android
npx cap sync android
./gradlew assembleDebug
```

Baada ya push ya PNG, endesha **Actions → Build Android APK** tena. Icon yako itaonekana kwenye home screen.

## Kubadilisha design

1. Badilisha SVG (`icon-master.svg` / `splash-master.svg`) au PNG
2. Export PNG kwa ukubwa sahihi (≥1024 icon, ≥2732 splash)
3. Weka kwenye `resources/` na push
