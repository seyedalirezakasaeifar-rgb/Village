# Native exit and renderer recovery

## Back and completed saves

The old host automatically finished the Activity after three seconds without a JavaScript reply. It also finished after calling suspend, without waiting for the asynchronous secondary-store write. A busy renderer or a quota-only indexed save could therefore lose a pending action.

Back now has an identity-checked request. JavaScript first closes the topmost game layer. At the root it suspends simulation/audio, waits for a completed on-device save, and acknowledges the native request. A small native saving dialog prevents intervening touches while leaving. Native code exits only after a successful acknowledgement. A four-second timeout cancels that request, resumes the game and reports that Back did not close it; late acknowledgements cannot finish a later session. Backgrounding also cancels the request.

If both stores fail, the running town remains available. The player explicitly chooses Keep playing/export or Leave without saving. There is no silent automatic exit on a missing callback or failed save.

## Renderer loss

On API26 and later, the guarded renderer-loss callback removes and destroys the failed WebView without deleting its persistent storage. It distinguishes a crash from Android reclaiming the renderer and offers Reopen game or Close. Reopening creates a fresh view; Continue uses the newest valid completed save. Unsaved changes are not promised to survive a killed renderer. The dialog is deferred while the Activity is backgrounded. Late archive imports do not call into a destroyed view; their source backup remains unchanged.

The earlier software emulator produced SystemUI ANRs and a renderer-termination message. That observation does not establish the cause of termination or Android FPS. These changes are defensive recovery around the native host, rather than an attribution of emulator slowness to the economy.

## Evidence and limits

`BackNavigationTest.java` runs on the host JVM and checks request identity, duplicates, expiry, pause and stale acknowledgements. `test_native_back_recovery.py` executes the exact Java-generated script in a real-origin browser, including a deliberately held indexed commit and both-store failure. It checks that open layers dismiss before saving, that exit acknowledgement waits, and that failed saves retain the town. Lifecycle/audio and persistence regressions also pass. Production Java compiles against the official Android36 SDK, with API26/33 types isolated behind guarded nested classes.

Native dialog presentation, renderer-kill recovery and provider behavior still need a reliable device/emulator test. Host-JVM/browser tests and SDK compilation do not certify those Android UI paths.

A separate [Android host harness](../tests/android/README.md) isolates these native paths in a test-only APK with a lightweight same-origin page. It can terminate only its own WebView renderer through the supported API and check recovery/persistent data. Its run remains pending until an explicit instrumentation result is recorded; it does not substitute for full-game touch, provider or physical-device testing.

## Actual Android host result

The standard separate instrumentation APK passed **nine native host checks** on the API30 software emulator: handled-layer acknowledgement, failed-save retention, Keep playing/resume, hung-save timeout, rejection of a late saved acknowledgement, actual supported renderer termination, recovery without finishing the host, recreated-view persistence, and acknowledged successful exit. Android reported the intentional termination as `didCrash=false`; it was not a SystemUI ANR. The [curated evidence](previews/native-recovery/evidence.json) binds the unchanged production Java files, harness, fixture and APK hashes.

The initial self-targeting harness failed to resolve its Activity before executing any checks. A normal debuggable target plus a separately signed test-only instrumentation APK then exercised the supported route successfully. The emulator stopped after the test. No root or security-setting changes were used.

These are actual Android host/dialog/renderer/storage checks with a lightweight same-origin page and programmatic framework actions. Full-game physical touch, device FPS/thermals and the system document picker remain separate, unverified acceptance stages.
