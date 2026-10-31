# Save recovery and chronology

## Confirmed fault

With a full local-storage quota, an older primary at day41 remained while IndexedDB successfully saved day61. Continue previously loaded the older primary first. The browser fault probe reproduced this rollback.

## Changes

On-device envelopes now carry an integrity-bound logical order, a town timeline identifier and a revision. Save order does not use simulation day or the wall clock. Founding or successfully importing starts a new timeline; deterministic exported town JSON is unchanged. Continue waits for the bounded startup read and tries intact copies in save order across local primary, local backup and IndexedDB. A failed backup-slot write does not prevent a primary replacement that fits.

Indexed writes are serialized, check the active timeline before writing, use atomic transactions, and reconcile a previously unseen higher store order before committing. A delayed callback from a replaced town cannot publish its old snapshot. Only a matching local revision can be promoted alongside an indexed commit. Completion from an earlier revision cannot change the latest save status. Both-store failures retain the running town, report failure and advise export; they are not reported as successful saves.

Earlier editions have neither order nor timeline identity. Matching copies and a lone intact legacy copy load directly. If the local and secondary legacy copies differ, Continue offers an explicit recovery choice with day/scenario information and a cancel path. It does not guess chronology from a larger simulation day or overwrite either copy on cancellation. The chosen copy receives new chronology on its next save.

## Evidence

`tests/test_save_chronology.py` injects quota, interrupted transactions, denied stores, stale callbacks, corrupted payload/metadata, clock rollback, same-day policy changes, new town/import transitions, late store heads and legacy records. Cold-page recovery checks the selected game and persisted timeline. `tests/test_save_storage.py` specifically isolates previous-local-backup recovery with IndexedDB unavailable; recovery of the newer indexed copy has its own tests. The full immutable gate manifest must bind final results to all shipped assets before release.

The app assumes one active game instance per installed WebView. This is not a cross-device/cloud-save protocol. If both storage systems are inaccessible, no local implementation can guarantee persistence; explicit export remains available.

## Long-run economic regression (prior immutable assembly)

The compensated-ledger build `129be0f8458049246c10432c85e6dc8e784ed6fe2d28b14e4a1a6ecc128f321f` completed 2,701 seconds of real-RAF expanded-town play with 91 menu/archive/cache samples, reaching day25,604 and 1,631 living residents. All sampled structural invariants passed, with no JavaScript errors. Maximum goods residual was 1.113e-8; final total-cash drift was about $0.000214. Atlas pixel storage peaked at 24,374,528 bytes and 270 sprites; sampled vessels/manifests peaked at 6/35. Post-GC JavaScript heap grew from 4.47MB to 9.57MB while buildings grew from 221 to702 and person records from657 to2,527. This does not prove leak freedom or Android frame rate, and it does not cover the later persistence implementation.

The programme test's originless browser fixture now supplies successful in-memory local storage. Its original assertion that a prior town's toast is cleared remains intact. Denied-storage warnings are tested separately rather than being mistaken for stale UI from the previous town.
