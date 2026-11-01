# Preserve synchronous restore Back semantics

Independent review of native async plumbing found its first Back branch called async cancellation for every busy restore, including the ordinary synchronous fallback. With no registered async request, that path reports that the backup is still being read and suggests later cancellation even when synchronous adoption may already be awaiting its save acknowledgement. Previously this route simply kept the busy restore open.

The native branch now dispatches async cancellation/feedback only for a registered async restore or its admitted follow-up save. Synchronous imports and the initial read phase stay busy without entering the unrelated async cancellation state. Renderer acknowledgement still owns completion; Back never closes or re-adopts the pending town.

`tests/test_native_restore_back_dispatch.py` extracts and compiles the actual first production Back branch with the real request registry. Its synchronous/no-request case fails before this fix; all five routing states pass afterward. The registry/callback host suite also passes. These are host branch tests, not an emulated Android activity, picker or cancellation body.

MainActivity SHA-256 after the correction: `7283d9365de4efdf0633205c520c6c7b660f369420b3d4cb9e1612f9bcd2345d`. The earlier API30 receipts for unchanged `5ad7a941` Java do not cover this later one-line correction. A current APK build and actual-device/provider rerun remain required; this environment has no Android SDK/device. Worker endpoint activation and adversarial completion-parser acceptance remain gated as documented in `NATIVE-ASYNC-INTEGRATION-8.md`. No pause/speed or game simulation logic changed in this native correction.
