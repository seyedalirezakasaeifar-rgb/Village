# Native asynchronous archive bridge — QA receipt

This candidate is based on integration `e3fae439e96b33bc3a62340f9a898029af674111`. The worker archive endpoint is opt-in; the production worker model remains disabled. Its synchronous archive path remains the fallback whenever the endpoint is absent.

## Changes

- Added a bounded native request registry that accepts only monotonically increasing safe IDs, recognized operations, matching epochs, and at most four outstanding requests. Duplicate, stale, refused and post-destruction completions are ignored.
- Added a streaming JSON completion parser with an 8 MiB archive limit, a bounded envelope size, required identity/status fields, and no full-object allocation for unrelated reply values.
- Routed worker export completions through the existing private `AtomicFile` staging and Android Create Document picker. Worker restore selection uses the existing bounded provider reader, shows a native busy dialog, submits restore by request ID/epoch, then requests the existing persistence owner and reports only its returned status.
- Added Back handling that requests endpoint cancellation only while a restore request is pending. After restore admission it explains that the operation is applying/saving and keeps the dialog open. Export/import remain synchronous on pages where `__workerArchiveAsync` is unavailable.

## Validation

- Host tests passed for request IDs, duplicate and stale replies, epoch matching, refusal/cancellation, the four-request bound and teardown. Existing archive I/O and Back-coordinator tests also passed.
- Built and signature-verified an isolated debug QA package with the official Android SDK 36 build tools. The installed test APK was `org.townledger.vale.qa`, version `8.0.0-async-archive-qa`, code `900011`; its SHA-256 was `3cb0923f2ae3a9b34028f6b9f1cb297a34e3b0c1e61fb46301fbbbeb48d53b40`. Its embedded `assets/game.js` SHA-256 matched source: `1784302215d01ab39d3a8acf742a7c71425ced435b79d2d34160e4694df83155`. The package used the existing development certificate, never the production signer.
- On Android 11/API 30 with WebView `83.0.4103.120`, a test-only asynchronous endpoint shim exercised the Java callback and real DocumentsUI export to Downloads, producing a 350 KiB town archive. The real Open Document picker selected that file. The shim ran the existing synchronous `__townArchive.restore` to isolate the native transport; `__townArchive.suspend()` then returned a successful persistence result, and the native completion callback released the restore dialog. This validates native callback, file-provider and UI routing, not the experimental Worker model or asynchronous model equivalence.
- On the same installed QA build, Back cancelled the actual import picker and returned to the game; the local save slots remained present. Separately, killing the QA app while its real export picker was open, then pressing Back, restarted the activity with the saved town available to Continue and removed the pending export file. This was process-death recovery, not an `Activity.recreate()` instrumentation run.

## Limits

The supported-runtime arithmetic guard fails on WebView 83, so no deterministic Worker replay was attempted and the Worker prototype remains disabled. The native callback test used an opt-in shim and does not certify real Worker bootstrap, its restore validator, or production activation. No newer Google Play system image was installed because its SDK license remains unaccepted. No physical-device, API 33+, memory-pressure, or performance certification is claimed. APKs, keys and saved towns are excluded from this report and the public source branch.
