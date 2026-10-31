# Reproducible source and Android builds

## Browser build

Use Python 3 and Node.js:

```sh
python tools/assemble.py
python -m http.server 8000 --directory assets
```

Open the local server in a browser. The delivered assets also work offline from a local file and in the Android host. Edit the ordered files in `src/`, then assemble; `assets/game.js` is generated. `release.json` supplies the runtime version metadata.

## Android

The executable host is `android/app/src/main/java/org/townledger/vale/MainActivity.java`; the manifest and original launcher vector are in `android/`. It opens only the bundled game, requests no application permissions, and uses the Android document picker for backup/import.

A JDK providing `jdk.compiler`, an Android platform jar, aapt, zipalign, and d8 or dx are required. Signing uses apksigner. With a normal SDK:

```sh
ANDROID_HOME=/path/to/android-sdk python build_apk.py
ANDROID_HOME=/path/to/android-sdk python tests/verify_package.py
```

A distro tool root can instead be supplied with `TOWNLEDGER_ANDROID_TOOLS`; an explicit jar can be selected with `TOWNLEDGER_ANDROID_JAR`. The validated build used Ubuntu AOSP packages `aapt`, `dalvik-exchange`, `libandroid-23-java`, `zipalign`, `apksigner`, `libapksig-java` and their shared-library dependencies, plus JDK 17. The fallback compiles Java-7-compatible bytecode against the API-23 jar, then packages minimum API 24 and target API 36. No proprietary game assets or online build service are required.

```sh
TOWNLEDGER_ANDROID_TOOLS=/path/to/extracted-tool-root python build_apk.py
TOWNLEDGER_ANDROID_TOOLS=/path/to/extracted-tool-root python tests/verify_package.py
```

Use `TOWNLEDGER_KEYSTORE=/private/path/development-signing.p12` to retain a signer. Otherwise a development keystore is generated under `build/`. The output is `TownLedger-The-Resilient-Vale-6.1.apk`. Private keys, compiled intermediates and machine-specific tool installations are excluded from the source archive.

The verifier checks DEX checksums, package/minimum/target/version metadata, icon resources, absence of requested permissions, exact packaged assets versus source, v2/v3 signatures and alignment. It does not install the app or prove hardware performance.

## Tests

Install the Python Playwright package and provide Chromium. Set `TOWNLEDGER_BROWSER` when Chromium is not `/usr/bin/chromium`.

```sh
python -m pip install playwright
TOWNLEDGER_BROWSER=/path/to/chromium python tests/test_release.py
TOWNLEDGER_BROWSER=/path/to/chromium python tests/test_finance.py
TOWNLEDGER_BROWSER=/path/to/chromium python tests/test_landmark_randomized.py
TOWNLEDGER_BROWSER=/path/to/chromium python tests/test_2000_residents.py
TOWNLEDGER_BROWSER=/path/to/chromium python tests/test_controls.py
TOWNLEDGER_BROWSER=/path/to/chromium python tests/capture_release.py
```

`test_release.py` includes seeded replay, exact continuation, malformed-save rejection, replicated policy tests, blocked cargo, actual 5.6 migration, pause, long traffic progress and 50/25/10/5-year scenario runs. The original 5.6 assets required by its migration case are included under `reference/v5.6/`. Historical scripts are references, not active build entrypoints.

`capture_release.py` checks the actual CSS at 1280×720 and 844×390, all navigation panels, policy review, 64× playback and genuine game captures. Its season comparison deliberately holds a town and camera fixed while varying the render month; the economy is not advanced between those four art captures.

## Version 6.1 regression checks

`test_v61_regressions.py` checks an actual stranded 6.0 town, historic bank-entry limits, cumulative bank-cost errors, persistent preferences and climate rules. `test_v61_performance.py` compares real wall-clock speed in 6.0 and 6.1, including synthetic CPU throttling. It is not an Android benchmark. `test_v61_vehicle_art.py` verifies four heading-dependent car and truck rasters. Set `TOWNLEDGER_CORE_ONLY=1` for the core part of `test_release.py`; run `run_endurance.py` separately to record each long scenario with its source hash.

## Version 7.0

The output is `TownLedger-The-Working-City-7.0.apk`; version 7.0.0 / code 14 / schema 5. The same signing material used for 6.0/6.1 is required to preserve update compatibility. The build script derives filenames and metadata from `release.json`.

## Version 7.0.1 source update

Current `release.json` is 7.0.1 / code 15 / schema 5. The source adds keyboard Escape handling for drawer dismissal; returns focus to the drawer/dialog launcher; labels the Help/archive dialog, traps Tab focus inside it; and restores tutorial markup when Android Back/Escape closes temporary archive screens. The output name derived by the build is `TownLedger-The-Working-City-7.0.1.apk`.

The original private signing keystore is not present in this source archive. The previous APK's public certificate cannot be used to sign an update. Set `TOWNLEDGER_KEYSTORE` to the original keystore and provide its credentials through the build script's supported environment variables to preserve in-place update compatibility. If you instead build with a fresh development key, Android will treat it as a different signer; users must export saves and reinstall rather than update. Do not weaken APK signing or claim update compatibility without verifying the signer.

This source tree has not produced a 7.0.1 APK in the review environment: Android build-tools and the required platform `android.jar` were absent, and SDK installation was unavailable. The baseline 7.0.0 APK is not a substitute for a rebuilt package. Complete the packaging and install/update checks on a machine with the official Android SDK and an authorized signing key.

Current checks include `test_v7_model.py`, `test_v7_default_starts.py`, `test_v7_scenarios.py`, `test_v7_policy_experiments.py`, `test_v7_liquidity.py` and `test_v7_contrast.py`. The endurance harness records the source hash before opening the app and rejects changes during the run. Do not edit the assembled game while testing. `TOWNLEDGER_CORE_ONLY=1` runs the deterministic/save/stock/traffic gates separately from the long scenario suite.
