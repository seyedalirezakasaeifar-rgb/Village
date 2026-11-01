# Waterfront and continuation recovery

Base: `ecbc945c4aeeb99d27d0cf7b7cd8ee63651af785`.
Assembled source SHA-256: `884d8087368dbb6ac0a058a5baee7296e47fcc79ea72db25b478ef50a7af0582`.

## Waterfront diagnosis

The placement failure was an invalid fixture projection. It hard-coded the old 80-tile atlas origin (`RW/2=2950`) while the current 128-tile map uses 4678. Its intended fishery tap at (4,58) decoded to (-20,82), so the runtime correctly ignored an out-of-map placement and charged nothing. Later lot enumeration also used an obsolete stride of 80, and the final inspector camera retained the old origin.

The test now derives screen points from live `iso`, tile dimensions, camera and canvas geometry; verifies inverse projection for every intended tile; fits the actual road path; and uses the saved grid size for lot indices. The old projected tap is retained as a negative counterexample: the complete archive remains unchanged. Every paid placement still uses actual buttons, touch or pointer painting. No direct `construct()` calls replace user controls. The corrected journey already passed on the untouched runtime before the separate continuation fixes below. Inspector targeting, working crews, paid cargo, funded care, utility reach, books and save round trip now pass. Captures are QA diagnostics, not a visual redesign or approval.

## Real continuation defects

Immediate public farm/home creation left defaults unpublished until import: property title/base value, firm operating/cost/forecast/credit fields and household finance defaults. Census recomputation also used the previous population to calculate safety/preparedness, and omitted approval. Public construction now initializes existing system/finance/market defaults after actual assignment and before saving; transit facilities and resurfacing publish current derived figures too. New households receive their existing finance defaults at creation. Census helpers use the current population, and approval is published consistently. A legitimate zero market-confidence value is no longer replaced by a fallback during restore.

The focused test compares the entire serialized state immediately after farm/home, transit and repair transactions; no fields are excluded. Valid zero values survive. Missing legacy metadata still normalizes without changing caller objects or financial/identity records. The bridge-art test's direct cargo API fixture now performs the same derived-state recomputation as the real transaction handler, rather than saving a stale aggregate after bypassing that handler.

## Reclassification of the service exclusions

The earlier bridge report described `serviceProvision` and `privateServiceProvision` as disposable derived caches. That classification was incomplete: these fields contain paid allocations, and the private record is also the same-day exactly-once guard. An independent test on the untouched base confirms that restore erased both fields; calling the existing private purchase routine again then moved cash a second time and, for schooling, repeated learning progress, even though total currency remained conserved. Paid benefits also temporarily lost their recorded coverage. The original negatives are preserved.

The loader now validates and preserves same-day public/private receipts. Validation checks finite/coherent public payments, date/coverage bounds, provider and household references, private allocation amounts and matching totals. It does not reconstruct historical purchases from the current policy, roster or cash. A same-day enacted policy change is a valid counterexample: recorded prior purchases survive even when the new authorization is zero. Nine malformed receipt cases must reject atomically without changing the live state, RNG, chronology or caller input.

Legacy missing/unsupported observations and valid older-day observations retain the previous tolerant invalidation behavior, without moving ledger money or inventing payment history. Current valid snapshots preserve all paid receipts. Both immediate and committed-day bridge/cargo cold reload tests now compare complete canonical state, including traffic, RNG and these two fields, with **zero exclusions**. The 45-day continuation tests also compare complete state with no excluded financial, identity, road, cargo or presentation fields.

## Native continuity and measured cost

Native Java and the committed-day save fence are unchanged. Host-JVM archive/Back tests, the exact import-script bridge, actual-origin cold Continue, twelve fresh authored restore cases, composite archives and upgrade migration pass. Comparing twelve authored starts to the accepted base finds only explicit founding-journal census corrections: previously null safety, and the previously absent regional approval reading, become finite values. Every other field, including financial parties, identity, roads, cargo and RNG, matches the accepted base. Existing old journal observations are not rewritten on import.

No new per-frame or per-tick receipt-validation scan was added: the validator runs at import. A standalone host Chromium sample on actual 169-person paid-service fixtures measured median 0.010 ms (school) / 0.0315 ms (fire) per receipt validation, with unchanged model and receipt data. This excludes JSON parsing, full hydration, native IO and rendering; it is not a large-capacity, device FPS or thermal claim. Public construction adds default-initialization passes at the transaction boundary.

## Acceptance and limits

[Final manifest](evidence/waterfront-recovery/final-manifest.json) binds the source, all inputs, original negatives and final logs. All **43 functional gates pass**: twenty core gates, sixteen focused continuation/service/native/control gates and seven supplemental bridge/network checks. Full model/RNG replay, monetary/goods invariants, legacy/default counterexamples and paid receipt idempotence pass. No new exclusion was introduced; the two earlier bridge cold-recovery exclusions were removed.

No renderer/style code changed. Canvas fallback remains intact. The selected Newfoundland implementation and its visual acceptance remain separate work; diagnostic images and pixel checks do not establish that fidelity. Cooperative simulation and experimental schema-9 capacity/identity codecs remain disabled/absent. No Android device/emulator, physical performance, full APK pipeline, signing, release or integration promotion was performed. The service-cash warning remains separate and queued for independent review.
