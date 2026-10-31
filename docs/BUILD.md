# Build and verify TownLedger 7.0.3

Run `python3 tools/assemble.py` after editing the ordered `src/` modules. Python 3 and Node.js are required. Serve `assets/` with `python3 -m http.server 8000 --directory assets` for browser play.

## Android

The validated pipeline uses the official Android SDK platform 36 and build-tools 36.0.0, Java 21 or later, Java 8 bytecode, d8, aapt, zipalign and apksigner. Install those SDK components with the SDK manager, then run:

```sh
ANDROID_HOME=/path/to/sdk TOWNLEDGER_KEYSTORE=/private/path/townledger-development.p12 python3 tools/build_android.py
ANDROID_HOME=/path/to/sdk python3 tests/verify_package.py
```

The script creates a development signer when the supplied path does not exist. Retain it privately for subsequent compatible builds. Its default development password is `android`; protect the file with filesystem permissions. Never commit it or put it in a source or delivery archive. For distribution, use an authorized release signing process. The original baseline key is unavailable; this build does not promise an in-place update from it.

Output: `TownLedger-The-Working-City-7.0.3.apk`. Version, code and package come from `release.json`. The verifier checks exact assets, DEX integrity, manifest metadata, requested permissions, signatures and alignment. Reports under `reports/` are generated and ignored. Neither script installs or launches the APK.

## Browser QA

Install `requirements-test.txt` and provide Chromium at `/usr/bin/chromium` (older scripts also accept `TOWNLEDGER_BROWSER`). Run scripts individually; historical reference tests are not a pytest suite.

```sh
python3 tests/test_archive_schema.py
python3 tests/test_mobile_rendering.py
python3 tests/test_v7_live_large_town.py
python3 tests/test_controls.py
python3 tests/test_v7_contrast.py
TOWNLEDGER_CORE_ONLY=1 python3 tests/test_release.py
python3 tests/test_v7_scenarios.py
```

The first three load bundled HTML in Chromium directly and do not need file URL access. Older scripts use local file navigation; environments that forbid it need an approved local HTTP server adapter. Run performance measurements alone, without concurrent builds or simulation tests. Absolute timing assertions are host-specific; preserve the JSON and describe the host and scenario. Live performance uses an authored synthetic town and real requestAnimationFrame callbacks. It is not an Android FPS benchmark.
