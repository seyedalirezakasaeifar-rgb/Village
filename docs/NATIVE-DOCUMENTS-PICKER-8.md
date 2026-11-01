# Android DocumentsUI fixture acceptance

The lightweight DocumentsHarness previously timed out at “fixture ready” when it ran with the full game package. The full game’s `index.html` has no `qaMode` sentinel. The harness now waits for a complete WebView document and the resumed foreground TownLedger window, then checks the package, bundled fixture URL, `qaMode`, and both archive bridge methods before launching a picker. A mismatch reports the observed page identity immediately.

On API 30 with Android WebView 83.0.4103.120, the harness passed real import cancellation, real export cancellation and prepared-file cleanup, cancellation after Activity recreation, and a real synthetic Unicode export to Downloads followed by opening and importing that exact file. It also verified the host resumed with the archive request idle.

The test used the current tested wrapper `MainActivity.java` SHA-256 `7e8ddccb1e20c95900e7449dd79320aeb5569e6b608f123cfacea3bf488ca341` and synthetic test content only. No APKs, private keys, or backup payloads are included in this report. This is emulator coverage, not physical-device certification.
