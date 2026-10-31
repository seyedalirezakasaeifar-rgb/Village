# Native archives, lifecycle and older WebView compatibility

Unpackaged source development after 7.0.5. The published checkpoint APK is unchanged. A separate, temporary debug APK was built outside the repository for native investigation; it is not a delivery candidate.

## Changes

- Native archive IO, UTF-8 conversion and JSON quoting run on a serial worker instead of the Activity UI thread. A busy state prevents overlapping chooser/transfer requests.
- Exports are prepared with `AtomicFile` under private application storage. Each request has its own validated filename. A launched chooser's mode and filename survive Activity recreation; the full town is not placed in an Android Bundle. Cancellation deletes the prepared file; successful destination writes truncate the chosen document.
- The transport ceiling is 8 MiB of UTF-8 bytes. Oversized multibyte text is rejected before allocating its encoded buffer. Malformed Unicode is rejected; an import BOM is accepted. Stream and provider errors leave the live town unchanged, though a failed external write can leave an incomplete destination.
- Native suspend stops the simulation and clears queued wall time. Resume and browser visibility transitions reset the clock without losing the player's own pause preference. Android Back waits for the save callback before finishing, with a three-second escape for an unresponsive renderer.
- API 33+ uses the platform Back callback; older releases retain the guarded legacy path. Newer platform classes are isolated in a nested implementation. The callback follows [Android's Back migration guidance](https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture); this does not claim a custom predictive preview animation. Build against the current Android platform jar.
- WebView debugging is enabled only when the application itself is a debug build. The production manifest does not enable debugging.

## Actual older-engine defect found and fixed

The lean Android experiment loaded the bundled page in WebView 83.0.4103.120. Opening a town produced `TypeError: Object.hasOwn is not a function`. The earlier compatibility gate removed only Array.at and had missed this dependency. Source now uses the local `owns()` helper backed by `Object.prototype.hasOwnProperty.call`. The regression removes both newer methods before loading and exercises starts, rendering, charts, policy enactment, development, Council focus and save validation.

## Evidence and limits

Assembled source: `2399c10ba2afd18a8ea173403bf877f9cb2ebdd0715cdeb67845d167ca02e278`. Host lifecycle, pure-Java archive IO, older-API, core release, repeated review workflows and archive schema gates passed against this source. Java compiled against the official API 36 jar. Pure-Java tests cover exact byte limits, multibyte/BOM round trips, malformed input, failing/null streams and private filename validation.

The software-only Android 11/API 30 experiment used 640×360, 160 dpi, one guest core, 1 GiB RAM and SwiftShader. Boot completed after approximately 7 minutes 46 seconds. Package installation was confirmed by querying package state after the first command timed out; the compatibility update later returned Success. A temporary debug build used version code 900001 and is kept outside deliverables.

The actual WebView loaded the full game source. After the compatibility fix, a native-engine probe advanced 30 days, restored its archive, validated the town and opened Economy, Services, Agenda and Policies without panel errors. Monetary drift was 0.000000017. This ran in WebView 83 with Object.hasOwn still absent, confirming the fallback rather than a newer-engine substitution.

Android System UI also displayed an ANR, and later system screenshots timed out. Therefore normal touch play, system Back, chooser cancellation/recreation, process death and background/resume are not certified by this experiment. The native engine probe is not a device performance measurement. API 33+ Back and physical Android devices remain untested. The test emulator was stopped after the bounded investigation; no security settings were changed to make it run.

Local evidence is in `reports/development-native-lifecycle` and the private native-smoke working directory. Logs, scratch APKs, private saved towns and signing material are excluded from the public repository. The new full immutable release gate still precedes delivery.
