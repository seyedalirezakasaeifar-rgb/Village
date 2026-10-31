# Private Android host recovery harness

`RecoveryHarness.java` is Android Instrumentation for a separate test-only, debuggable APK. It is not included by the production build. It uses the unmodified production Activity/bridge and a tiny same-origin HTML page to isolate native lifecycle/dialog behavior from the full renderer workload.

On API29+, it checks handled Back, failed-save Keep playing, a never-settling save timeout, actual app-WebView renderer termination via the supported API, native recovery/recreation, retained same-origin storage, and acknowledged exit. It needs no root, security-setting changes, third-party test framework or production test hook. Programmatic dialog actions do not certify physical touch or full-game FPS. Keep the instrumented APK and signing key outside the public source tree.

The debug manifest must register `org.townledger.vale.RecoveryHarness` targeting `org.townledger.vale`, with the Activity and harness in the same test-only APK. Install with `adb install -t`, then run `adb shell am instrument -w org.townledger.vale/org.townledger.vale.RecoveryHarness`. Record its outcome, exact source/Java hashes and emulator configuration; a successful build alone is not a passing run.

For this isolated APK only, stage `host-page.html` as `assets/index.html`; leave production Java unchanged. This uses the real bundled file origin, rather than a data URL. The regular APK must retain the real game index; never publish the instrumented build as a game deliverable.
