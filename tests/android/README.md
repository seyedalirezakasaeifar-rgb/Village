# Private Android host recovery harness

`RecoveryHarness.java` is Android Instrumentation for a separate test-only instrumentation APK targeting a debuggable host-fixture APK. It is not included by the production build. It uses the unmodified production Activity/bridge and a tiny same-origin HTML page to isolate native lifecycle/dialog behavior from the full renderer workload.

On API29+, it checks handled Back, failed-save Keep playing, a never-settling save timeout, actual app-WebView renderer termination via the supported API, native recovery/recreation, retained same-origin storage, and acknowledged exit. It needs no root, security-setting changes, third-party test framework or production test hook. Programmatic dialog actions do not certify physical touch or full-game FPS. Keep the instrumented APK and signing key outside the public source tree.

The test APK (`org.townledger.vale.tests`) must register `org.townledger.vale.RecoveryHarness` targeting `org.townledger.vale`, declare package visibility for that target, and share its signer. Compile the test against the target classes without duplicating those classes in the test APK. Install both, using `adb install -t` for the test APK, then run `adb shell am instrument -w org.townledger.vale.tests/org.townledger.vale.RecoveryHarness`. Record its outcome, exact source/Java hashes and emulator configuration; a successful build alone is not a passing run.

For the isolated debuggable target APK only, stage `host-page.html` as `assets/index.html`; leave production Java unchanged. This uses the real bundled file origin, rather than a data URL. The regular APK must retain the real game index; never publish the instrumented build as a game deliverable.

## Reproducible scratch builds

With official platform 36 and build tools installed, build the test-only pair in a
private directory outside the repository:

```sh
python tests/android/build_harness.py --sdk /path/to/android-sdk --out /tmp/townledger-native-qa
adb install -t -r /tmp/townledger-native-qa/native-host-fixture.apk
adb install -t -r /tmp/townledger-native-qa/native-host-tests.apk
adb shell am instrument -w org.townledger.vale.tests/org.townledger.vale.RecoveryHarness
```

The script generates its own disposable debug signer and records exact Java,
fixture and APK hashes in `build-evidence.json`. It never reads a release key.
Both APKs are marked `testOnly`; production assets and manifests are unchanged.
Use an isolated emulator: these test packages share the game's package ID and
cannot upgrade an installation signed by the production key. Do not uninstall a
user's existing game to make a test signer install.

The expanded recovery harness also uses a test-only external ContentProvider to
exercise the real native worker's Unicode/BOM import, malformed and oversized
rejection, export truncation and cancellation cleanup. Chooser cancellation is
intercepted by Instrumentation, and transfer results are delivered through the
Activity result method. Those are actual Android provider/worker checks, **not**
certification of navigating a device's system document-picker UI. The provider
exists only in the test APK and is never packaged in the game.

To use the complete unchanged game assets instead of the lightweight fixture:

```sh
python tools/assemble.py
python tests/android/build_harness.py --sdk /path/to/android-sdk --out /tmp/townledger-native-qa --game
adb install -t -r /tmp/townledger-native-qa/native-host-fixture.apk
adb install -t -r /tmp/townledger-native-qa/native-host-tests.apk
adb shell am instrument -w org.townledger.vale.tests/org.townledger.vale.FullGameHarness
```

Retain the first build evidence and instrumentation output before rebuilding the
pair. FullGameHarness uses framework touch injection to found a town, checks the
actual native engine/map/panels/archive, and invokes native lifecycle callbacks.
It observes real audio media by wrapping the browser's Audio constructor without
changing the shipped scripts. This is a programmatic native test, not human touch
play, measured Android FPS, listening quality, or ActivityManager process-death
certification. Only an explicit successful instrumentation result establishes a
passed run; SDK compilation alone does not.

For the separate real system picker cancellation/recreation test, install the
lightweight fixture pair and run:

```sh
adb shell am instrument -w -e picker true org.townledger.vale.tests/org.townledger.vale.RecoveryHarness
```

This launches Android's actual DocumentsUI. Its import cancellation must release
the busy state, and export cancellation must survive Activity recreation and
remove the private prepared file. It does not select and transfer an actual file
through the picker UI; successful external-provider transfers are tested by the
separate provider cases. A boot-time ANR overlay can intercept all input; retain
that negative evidence and restore a healthy emulator before drawing conclusions.
The harness does not change system security settings or suppress ANRs.

Use `-e large true` with FullGameHarness to load a synthetic 2,000-resident town
and hold it for a 30-second memory sample while real media plays. This is a load
and memory fixture, not naturally grown population or sustained native economic
throughput. `-e audio true` skips the separate economy/panel/Back sequence for a
focused audio/lifecycle probe. Native touch targets are scrolled into view and
checked against the actual DOM hit target. Initial music can require an explicit
Next/Retry gesture after expensive founding; the audio probe uses an actual
control touch and retains before/after media state.

Capture full-game instrumentation output in a log and run the optional observer
concurrently:

```sh
python tests/android/observe_memory.py --adb /path/to/adb --log /tmp/game-instrumentation.txt --out /tmp/native-memory
```

It records timed PSS snapshots, not peaks. WebView sandbox processes are listed
separately and must have their ownership checked before their PSS is attributed
to the game. A failed optional crossfade probe remains a failed result while
independent large-city checks continue; failures are never turned into passes.
