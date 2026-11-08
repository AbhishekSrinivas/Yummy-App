# Yummy

![Yummy](assets/icon-only.png)

A personal recipe book that runs entirely on the phone or tablet. Recipes are pasted in as text, read like a book with page turns, scaled to the number of people eating, and can be read aloud. There are no accounts and no server.

Download the latest APK from the [releases page](https://github.com/AbhishekSrinivas/Yummy-App/releases/latest).

| Home | Steps | Tablet landscape |
|---|---|---|
| ![](docs/screenshots/home.png) | ![](docs/screenshots/steps.png) | ![](docs/screenshots/tablet-landscape.png) |

## What it does

- 27 bundled South Indian and other vegetarian recipes with photos, categories and time groups (Instant, Quick, Normal)
- Add recipes by pasting text or importing a zip with images; titles can be reviewed on import
- Book reader with page turns, a two-page spread in landscape, step checkboxes and timers
- People-eating stepper that scales ingredient amounts and the quantities written inside the steps
- Metric and US units, ingredient swaps, grocery list, weekly plan, pantry and cooking stats
- Read aloud with highlighting, speed options and a choice of ingredients only or the whole recipe
- Favorites, search across recipes, ingredients and tips, and A-Z or custom ordering
- Editorial and lime glass themes, light, dark and true black modes
- Fonts are bundled, so everything works offline

## Install

On Android, open the latest release, download `Yummy.apk`, and allow installs from your browser or file manager when asked. The APK is rebuilt on every push to `main`. It is debug-signed, so installing a new one over the old one keeps your data.

You can also serve the `www` folder from any static host and add it to the home screen.

## Build

Needs Python 3 and Node 18+.

```bash
python3 src/build.py          # writes www/index.html
npm install
npx cap add android           # first time only
npx @capacitor/assets generate --android --iconBackgroundColor '#1E5B3A'
npx cap sync android
cd android && ./gradlew assembleDebug
```

The APK ends up in `android/app/build/outputs/apk/debug/`. Pushing to `main` or running the **Build Android APK** workflow does the same thing on GitHub.

## Layout

```
src/index.src.html   app source, a single readable file
src/fonts/           bundled Lexend, Playfair Display and Barlow Condensed
src/build.py         inlines the fonts and writes www/index.html
www/index.html       built app that the Android wrapper loads
assets/              app icon
docs/screenshots/    images used in this README
.github/workflows/   APK build and release
capacitor.config.json  Android wrapper settings
```

## Editing

Change `src/index.src.html`, run `python3 src/build.py`, and commit both. The bundled recipes are the `DEFAULTS` list in the source. Existing installs pick up changed bundled recipes without losing photos or notes.
