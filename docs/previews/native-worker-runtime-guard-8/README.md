# Native worker runtime guard and synchronous fallback

This report records a source-matched Android QA run for the experimental playable worker candidate. It is a diagnostic result, not worker activation or a release certification.

## Build and device identity

- Candidate commit: `a649a55ccb752b6f1fd170e9f0689edb92dff34c` (based on integrated game `87811c52cdb9aecd13cd23beebd52f6475c6dd9c`).
- Canonical assembled game bundle: `f08cdd9cf77bed07c94722995f4e14f45ff6c9a2f85c77406badcdfc13eaa905`.
- Worker model: `70ba7c53ecef1aa5785ddb3fe0b50eb8e96a26db41bf7199eef9a1423fe15b5c`.
- Generated worker bridge: `5b1c64909d36bd5b2fb0ca115b836f8a6ae2583b42671622464948b829ae6341`.
- QA-only APK: `5d0d1527f04a3f7d9b3aaea3021591af5f7fb801fcd26464fb77ead79c0aeb7f`; installed APK pullback matched this hash.
- Isolated QA application ID: `org.townledger.vale.v8workerqa`.
- Runtime: Android API 30 emulator, Android System WebView 83.0.4103.120. The arithmetic failure is a property of this emulated runtime; no physical-device claim is made.

## Worker admission result

The runtime guard was run before worker admission. Unsigned shifts for values `2147483648`, `2218605210`, `4050171023`, and `4294967295` returned `2147483647`, rather than the expected unsigned values. `Math.imul(4294967295, 5)` returned `2147483643`, rather than `-5`. The guard rejected this runtime with:

`Unsupported arithmetic runtime: archive unchanged; update the supported WebView runtime before simulation`

The resulting state was `workerActive=false`, fallback `unsupported-runtime`, and archive unchanged. No Worker was constructed/admitted, and no worker command or worker durability roundtrip was run. The runtime guard was not bypassed.

## Synchronous fallback result

The ordinary synchronous game path remained usable. A fresh synthetic town validated with 169 residents, was paused and saved at Day 11, then background-killed and relaunched. After tapping Continue through Android UI, a QA-only observer paused after hydration and before the next animation frame. The canonical state hash before and after was exactly `267e6c30f68d1c0b58ea33b4eddc3aca8e56c47049f00214c55ca46b82df16cd` (102 top-level fields); day, population and paused status matched. Worker remained inactive.

This verifies the synchronous cold-restore fallback on this candidate. It does not validate worker command admission, worker save/readback/acknowledgement, worker parity, or worker performance.

All town data used was synthetic. This report intentionally excludes the APK, signing material and saved-game files.
