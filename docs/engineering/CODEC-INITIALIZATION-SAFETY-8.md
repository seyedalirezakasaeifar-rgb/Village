# Disabled codec: capacity-safe adoption checkpoint

This is initialization/adoption safety, NOT a completed root-command/day admission guard. No leaf creator refusal was installed. The codec remains disabled. Current assembled source SHA-256: `8be2585815ad9585f3fde86d2fb00909589b44f39956c4faa0e146fe47bb970a`.

## Components and ownership

Base disabled candidate `d158eb5` includes version-3 status-neutral historical counts, with unchanged total IDs/shared budgets. Independent reviewer fixes were cherry-picked with conflict resolutions preserving that contract:

- Original `77a799d7e0f072dfddf9dd940f8ac6bbef55cefa` → local `cd25098`: canonical numeric/string byte counting.
- Original `a964174b67b7eb69f95707b7643234d6d48c855c` → local `29743cb`: all directory headers checked before value scans.
- Own `b5da5d6`: pure wire-encoding helper and capacity certification of initialized candidates, staged runtime rollback and a clear rejection explanation.
- Original `9932d345f186b966e8e3739daf993dbb5b2e30e2` → local `82496c0`: shared reconstructed-key expansion checked before defining any records.
- Original evidence/test commit `3bf70b840b8427ec029dd15cb6f203e8598e6ea3` → local `7e12cf3`; its corpus file was absent in this branch, so its complete supplied file was retained. Duplicate-version tests now use supported current version and unsupported version 4; `owns` replaces test-only Object.hasOwn for WebView83 compatibility.

The independent fixes' original reports remain pinned to their original sources. New reports under evidence/codec-initialization-safety describe this combined checkpoint. No raw saves are included.

## Admission of a loaded town

A wire can fit its input budget yet grow during legitimate initialization. The review witness removes 26 optional firm unitCost maps from an otherwise valid near-8-MiB archive; ordinary initialization restores them and previously made the accepted town unsaveable. Missing regional-trade defaults and transport numeric normalization can do the same.

`encodeInactiveLogicalArchive` now operates only on a detached logical serialization. The ordinary archivePayload wrapper still uses the original logical serializer and the disabled feature flag. Hydration first validates and normalizes a private parsed candidate. It stages that candidate synchronously, with simulationBusy set, isolated traffic/maps and model-dependent caches, then runs the existing initialization and transport normalization. It certifies the exact resulting serializer representation before resetting UI, publishing headers or advancing the save timeline. A failed capacity check restores the original G reference, RNG, traffic, crew counters, staged policy, road/index/transit/urban caches and scheduler flags. No payment, truncation, history deletion or alternate unbounded encoding is used.

The runtime snapshot preserves original object references. Old traffic/maps are detached BEFORE initialization so candidate helpers cannot clear originals. Staged modal state, touches, road paint and construction selection are not reset until capacity validation succeeds. Nested saves during staging return false because simulationBusy is true; they do not reach persistence. The previous simulationBusy value is restored on both success and failure.

This private staging relies on a single synchronous JS turn. Do not add await/yield between staging and commit/rollback: ordinary UI/readers must never observe provisional G. Progress UI needs a separate safe preparation boundary; this patch does not claim to solve native long stalls.

## Canonical wire and logical bounds

The numeric reviewer enforces the 16-MiB logical expansion bound. A separate adoption constraint is necessary: raw scientific tokens can describe a logical value below 16 MiB whose canonical WIRE is above the 8-MiB export limit. Directory parsing used for diagnostics can still return that logical value, but hydration requests self-exportability and refuses canonical wire growth before initialization or record reconstruction. Supported ordinary/legacy imports also undergo the final normalized encoding check when the experimental codec is enabled.

Limits are unchanged: 8 MiB wire, 16 MiB logical expansion, 1,000,000 nodes, 500,000 reconstructed cells, depth 24, existing field/ID limits. Rejection is explicit. The user-facing import explanation says the backup exceeds this version's archive capacity and the current town is unchanged. It does not silently fall back or delete records.

## Executable receipts

`tests/test_codec_initialization_capacity.py` passed five separate rejection witnesses:

1. Restoring optional unitCost maps exceeds wire bytes.
2. Restoring those maps exceeds node count.
3. Missing regionalTrade adds a legitimate default beyond remaining headroom.
4. Transport clock string `1e20` becomes a longer canonical numeric value during restore.
5. A raw numeric-token archive below logical 16 MiB cannot fit canonical wire 8 MiB; zero initialization calls occur.

Each preserves full model bytes, RNG, epoch/order/revision/town, exact runtime references/counters, staged modal/policy/paint/touches and live traffic. Four initialized cases inject nested save attempts: all reach zero persistence writes. Supported default restoration remains self-exportable and passes exact 30-day economic/model/RNG replay. Host rejection timings around 75–170 ms are receipts, not native or peak-performance certification.

The imported shared-key corpus passes seed 0x53a91c2d: 2,048 canonical size checks, 350 fidelity cases and 177 atomic rejections. Shared node/key-combination failures perform zero historical reconstruction and zero field definitions. Exact shared-key limit accepts; one byte over rejects before allocation.

Both owner codec suites pass 30-day replay and actual creator boundary actions. Numeric, metadata, status-transition, byte/node/record frontier and regional-creditor (-1 valid, -2 invalid) suites pass. Default-disabled core release gates pass same-seed/render independence and 120-day continuation. Ordinary production play has no new per-action serialization; the extra exact encode is restricted to experimental archive adoption.

## Remaining blockers and next boundary

Root paid-command/day admission is OPEN. Existing evidence shows actual construct taking $4,050 before capacity failure; independent caller probes also show unassigned investment, dropped completion projects, retained council charges, premature day saves, RNG advancement and credit metadata writes. These are not repaired by this adoption check. Root wrappers must encompass the first debit, factory calls, future-project reservations, final history/RNG and all UI/persistence effects; see CAPACITY-ADMISSION-DESIGN-8.md and the independent 45a6eec checklist. No unsafe leaf guard or generic live-mutate/reload wrapper is proposed as complete.

Native software-emulator combined measurements remain unacceptable for activation (roughly 19-second encode, 13-second decode, 38-second malformed rejection on older candidates). Header/shared-key fixes reduce avoidable work, but initial parsing remains and this post-initialization certification adds an encode. Native must remeasure; no UI progress, ANR, peak-memory or smoothness acceptance is claimed. Cooperative simulation is not needed for these synchronous tests and stays off.

For a separate measured fast-path candidate, retaining ordinary schema-8 wire below 8,000/3,000/3,000 IDs is reasonable ONLY with explicit opt-in selection, strict canonical byte/node/depth checks, full reference fidelity, reserved-format-marker protection, and exact raw→directory boundary tests. It must not silently weaken import validation or alter the default format before review. This checkpoint does not implement or enable that preference.

Native canonical defaults/cache fixes are separate on codex/8-native-canonical: public b7df5d1 and local a41eaff. This branch includes the same missing-trade hydration initialization needed for certification, but does not duplicate the seed/Continue fixes. Integration must preserve those independent edits.
