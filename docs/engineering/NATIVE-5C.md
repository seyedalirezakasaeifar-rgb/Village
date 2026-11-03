# Current-source API30 native evidence

Candidate 5c503015e9572329393f01242732b7ca0bed7708; assembled assets/game.js SHA256 cc9f02a1c84a8e4aadc5df3d22bf8a9a382ed7c1ee5210742bff4cc5d31bfce6. Clean scratch build verified source, build receipt and signed APK embedded asset hashes all match. The builder now rejects mismatched assets before returning an APK.

API30 emulator5556 / Android11 / WebView83 native full-game harness passed. Strict synthetic day1 process-death recovery passed with process change and identical full-state hashes. Details and exact APK identity are in [receipt](../previews/native-5c/evidence.json).

The DocumentsHarness failed before picker launch: `window.qaMode` did not become available within 60 seconds; zero checks passed. At failure, launcher was foreground, so provider/picker were not tested. District and gathering UI interactions remain unverified. No physical-device performance claim.
