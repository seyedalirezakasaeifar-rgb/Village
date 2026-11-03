# Bounded core integration recovery

Base: `6c02aadf293513d022f7a3868b52abe050202880` from public `codex/townledger-7.0.1`.
Runtime checkpoint: `0de299246e6fe345e361251cc6fb6c3f69a673e3` on separate `codex/8-core-integration-recovery`.
Assembled `assets/game.js` SHA-256: `218de17d31e130f8f683ab1287307380eb2ec0689b06d39a9003ef26883a1fc7`.
Production Activity SHA-256: `7e8ddccb1e20c95900e7449dd79320aeb5569e6b608f123cfacea3bf488ca341`.

Integrated only these gameplay/native changes:

- `b7df5d1d6110c05f52615e5ecb1474705de63c03` and `46eda8b5766fda31d5625e224f79443474bd4416`: preserve canonical Continue state/traffic and initialize missing regional trade.
- `60f9e320828270e9a675cd508f380a443e5b798a`: native restore progress and operation guard until renderer acknowledgement.
- `c188a6fe802982969a02e3a3aa5f719e03027658` and `dd11a82fb9f469ed58726fb7bde7a5b21d900e72`: deterministic effective, cash-backed vacancy ranking after incumbent payroll commitments.

Native source applied cleanly. The wage cherry-pick had six modify/delete conflicts because its earlier audit documents/tests were absent from this base. Those upstream files were retained, without taking their predecessor gameplay commits. The current road-distance cache optimization remains intact. Reassembly corrected the generated bundle after combining the branches. Historical imported reports retain their original source hashes; they are not evidence for this assembled source. The 104-case allocator matrix was rerun and now identifies this source hash.

The balance branch resolved to `0ba258d9a27e29bbba3e20110bccbe217629c268`; the intervening `a7acbe82986d5dc8727687ef3c7562f92f0a6346` and tip add investigations, not gameplay changes needed here. Their natural-history/late-demography conclusions do not establish universal population or food-access improvement. No such claim is made for this batch.

## Verification

Run `python tools/assemble.py` and `node --check assets/game.js`. Each Python gate runs directly from `tests/`; file-navigation gates use the repository's documented `PYTHONPATH=tools/browser_http_adapter TOWNLEDGER_USE_HTTP=1` adapter. Release gates use `TOWNLEDGER_CORE_ONLY=1`, so long-run endurance is explicitly excluded. Initial file-origin attempts were blocked by Chromium's administrator policy; their logs are retained. Two older tests needed their ignored output directories created (`reports/v7.0`, `reports/final`), then passed without source/test changes.

Source-bound results and original failure logs are in [evidence/core-recovery](evidence/core-recovery/). The manifest distinguishes initial attempts and final outcomes.

The exact Activity-injected import JavaScript was additionally executed in Chromium for success, rejection and exception: overlay/aria-busy are present during restore, one acknowledgement is emitted, and presentation clears afterward. This browser test does not certify Android dialog behavior. Host JVM ArchiveIO and BackNavigation tests passed, as did execution of the native Back script against the real browser game.

One unresolved negative result remains: `test_save_adversarial.py` accepts its `householdMismatch` mutation in the hardtimes/day-721 case. Fresh settlement and regional/day-361 rejection plus 90-day full model/RNG continuation checks pass first. The exact same failure independently reproduces on the untouched public base (`assets/game.js` SHA-256 `a450e2ab4fce7f373e511d52603b07c12b693620ac6ee66be5893e3fd44a8e74`). This batch preserves that existing failure and does not claim complete adversarial acceptance.

No SDK, adb or emulator is installed in this environment. Full Activity compilation and exact-batch Android/API30/device/picker tests were not run. Upstream API30 results are separate supporting evidence, not an exact-source native acceptance run. No APK was built, signed or released. Performance benchmarks and the full candidate release/build pipeline were not run.

Schema remains 8. Cooperative simulation, schema-9 identity codecs/admission prototypes, retention save fixes, and road bridges remain outside this batch. No main/integration ref, PR approval/merge, deployment, credentials or private saves were changed.

Follow-up: the preserved household mismatch failure was subsequently diagnosed as an inactive-person test assumption. See [household archive acceptance](HOUSEHOLD-ARCHIVE-ACCEPTANCE-8.md) for the corrected fixture and valid estate counterexamples; the original negative logs above remain unchanged.
