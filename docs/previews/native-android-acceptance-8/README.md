# Android acceptance evidence

These reports record source-bound checks on isolated synthetic QA towns. APKs, signing keys, raw save snapshots and personal data are excluded. The API 30 emulator used WebView 83 and software SwiftShader; results do not certify physical-device performance.

- [Async archive parser and DocumentsUI checks](01eeda-parser/ANDROID-RESULTS.md) — source `01eeda3d2ff09822b9422721f75e97fabbc9958a`.
- [Economy-tier WebGL, settings fallback and limitations](economy-29dd/ANDROID-RESULTS.md) — renderer source `29dd12af7d4aac6b22efcfe1cec1e2d59aff2c1f`.

The parser report distinguishes the later Android runtime probe from the commit's original host-only acceptance document. The economy report records the automatic Canvas fallback success and leaves resize validation explicitly incomplete.
