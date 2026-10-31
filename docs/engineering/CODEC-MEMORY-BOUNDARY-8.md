# Disabled codec memory and admission-boundary review

Runtime change `d1f963a`, dependent on disabled combined candidate `aecf8e3`. No activation, native wrapper, economic, creator or cooperative changes. Branch remains separate from the monthly-review committed-boundary fix; tested base is still `7500d878` plus codec candidate commits, not newer integration main.

## Small optimization

The encoder previously parsed the whole logical archive, built/serialized the wire envelope, then parsed the full wire again to validate it. It now validates its existing private candidate directly, passing the UTF-8 byte count already computed. That candidate came entirely from the original logical JSON parse, so decoding it cannot mutate live state. The encoded return string is produced before candidate reconstruction. This removes one full wire parse and redundant byte-count serialization; strict decoded/encoded budgets and all domain adoption validation remain unchanged. Independent serialized-round-trip/full-field equivalence remains exercised by codec gates.

## Reproducible host profile

`CODEC_PROFILE_BASELINE=1 CODEC_PROFILE_LABEL=before-stable python tests/profile_identity_codec.py`, then `CODEC_PROFILE_LABEL=after-stable python tests/profile_identity_codec.py`. The baseline substitutes the exact prior codec module into the current assembled source without changing repository files. Source hashes: before `ea2d0d6f388e2089e916d842352a2e3467b75b41f0a776f443409fd962174ddb`; after `b9f015806b20e5795bdb1814373b25a8786247c7c67f634ac9104c4c79d4f12f`.

Each source has four separate fresh Chromium processes: 518,791-byte realistic 360-day town or 6,101,949-byte combined historical fixture, each with ordinary GC or explicit forced GC. Each scenario performs twelve cycles of valid import, malformed object import and export. Four heap samples are taken per cycle, plus after 50 ms idle. Forced GC occurs outside operations before the first cycle and after each idle interval; ordinary scenarios never invoke it. The malformed object fixture intentionally includes its caller-owned parsed input alongside the import candidate, a realistic worst-case API attack rather than a claim all native text imports allocate identically. Strict complete-model comparison runs after sampling to avoid counting assertion copies as operational heap.

| Fixture / GC | Median import ms, before→after | Median malformed ms | Median export ms | Max sampled heap MB |
| --- | --- | --- | --- | --- |
| Small / ordinary | 25.8→22.6 | 10.2→10.5 | 33.6→23.1 | 94.5→79.4 |
| Small / forced between cycles | 23.5→23.8 | 10.1→9.8 | 29.5→20.9 | 36.0→27.9 |
| Combined / ordinary | 214.8→216.7 | 108.0→108.0 | 394.1→299.2 | 361.8→386.5 |
| Combined / forced between cycles | 214.5→221.7 | 110.3→112.5 | 398.2→309.7 | 116.2→101.5 |

Export medians improved about 24% on the combined ordinary-GC fixture. There is no demonstrated ordinary-GC maximum-heap improvement: its sampled maximum increased in the stabilized pair, and preliminary runs varied substantially with collection timing. This change reduces known duplicate work, not a guarantee of reduced native peak memory.

After forced GC, combined retained samples ranged 34.4–36.1 MB before and 36.1–36.6 MB after; small retained samples were about 17.8–18.5 MB in both. No continuing retained growth was observed within twelve cycles; this is not a long-session leak proof. Ordinary post-idle combined samples after optimization ranged 50.4–341.3 MB, ending at 143.2 MB, so idle time alone must not be mistaken for collection. Samples do not measure intra-operation peaks, WebView/native memory, DOM/image buffers or physical-device latency. Forced GC is test-only and is not added to production.

Initial profiling byte/model equality assertions failed. A field trace isolated derived preparedness 77→76 in the manually constructed large fixture: its creator calls bypassed normal caller recomputation, and `defensePower` inside the `recompute` object assignment uses the previous `G.stats.population` before the new stats object is assigned. No money/identity/RNG difference was observed in the trace. The harness now performs explicit canonical warmup before sampling and retains a strict complete-model comparison after every scenario; all eight final scenario checks passed. The original field trace is preserved. No production canonical assertion is weakened, and this profile does not claim arbitrary unnormalized archives restore byte-identically.

## Confirmed shared-budget admission blocker

The negative test starts from a valid near-8-MiB experimental archive and invokes actual permitted `createFirm` calls. On the third action, live firm count becomes 29, then export throws `Archive exceeds encoded byte budget`. The previous successful candidate was 8,388,186 bytes against the 8,388,608-byte limit, with 28 firms. This is synthetic near-boundary padding, not a claim naturally generated towns already reach this size.

A persistence spy confirms `save()` returns false before any `persistSnapshot` call; no oversized bytes are written. Reloading the prior valid candidate succeeds and restores 28 firms, dropping the failed action. Thus durable rejection is fail-closed, but creator admission is NOT atomic with archive capacity. We cannot confirm creators cannot cross the shared budget. There is no silent fallback, raising the limit or destructive pruning.

Safe current operational behavior is to KEEP THE CODEC DISABLED. For a diagnostic enabled town that hits capacity, stop making changes and restore its last verified valid backup; this abandons uncommitted changes, so it is not an acceptable production admission policy. The branch explicitly leaves activation blocked. Supporting continued play requires pre-commit admission/reservation covering every creator and history-growth path, with complete rollback of RNG, goods/accounting, property, ownership and transient caches on refusal, plus clear capacity UI. Adding a serializer-only rollback would be unsafe and is not attempted. Household/person deaths and later record-field growth also consume representation budgets, so a guard only in `createFirm` would be incomplete.

## Acceptance and remaining limits

Both codec regression suites pass after optimization: lossless fields, real identity admission boundaries, exact 30-day model/RNG replay, old imports, shared expansion rejection and atomic malformed adoption. The combined suite additionally exercises regional creditor -1, rejection of -2, inconsistent summary totals/buckets/owners and nonmonotonic receipt IDs. Cooperative refusal remains explicit; no cooperative integration is required to run this synchronous diagnostic candidate. The extended eighteen-fault regression sampled 488.6 MB after its adversarial allocations and 38.3 MB after test-only forced GC; that additional high sample is retained in its report and reinforces the native activation blocker. No new release-ready or Android smoothness claim is made.

Evidence consists only of reports/hashes, not complete synthetic saves. Independent review, native peak memory/latency and comprehensive capacity-safe admission remain blockers. The final monthly-review UI save fix is a separate integration acceptance concern.
