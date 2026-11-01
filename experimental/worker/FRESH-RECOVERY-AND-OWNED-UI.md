# Command-owner UI and fresh saved-state recovery — disabled

This isolated composition extends f77ceddb with public command-only owner20723d3/e13a21b and compatible cash traversal change1b78718. It retains the same100-module source SHA2567619b1fafdf5f05a8a3d8c79ea5669aaa13f5262957dd34a3e7c1b3479681461. It does not yet contain new model669c908 or graphics01da3f104. No production startup is changed.

## Explicit build/start contract

Default worker builds exclude BOTH owner implementations. `WORKER_PAID_COMMAND_OWNER=1 node experimental/worker/build.cjs` includes the actual command owner; it does not automatically initialize it. Mixing that flag with WORKER_PAID_TEST_OWNER is rejected by the builder. The reference owner is never promoted.

Trusted composition code may initialize the loaded worker using:

```js
const real = await __workerRealView.enable(code, committedArchive, {
  initializeAuthority: async ask => {
    const result = await ask({type:'initialize-command-owner'});
    if (!result.ordinaryDayReady) throw Error('Automatic creator scope unavailable');
  }
});
```

The callback is retained only in the main-thread trusted composition closure. No function or source crosses postMessage. The finite initialization message requires current epoch/command admission, an unowned loaded model and the compiled factory plus actual published creator guards. It uses the existing one shared root and exact workerExecution/completion handshake. Missing factories/creators/initial checks refuse. Authority status separates command mode/reference status from global capacity certification, which remains false.

Actual paid choice UI shows pending state while the frozen last completed city remains available for panning. A model refusal restores the review for a fresh-ID retry. A committed command shows recorded/pending-save; only the existing save owner returning true plus the worker token ACK marks its archive confirmed. Failed storage remains unsaved; retry invokes save only, never the paid action again. After admission Back/duplicate input cannot cancel or replay financial work. Metadata timings are bounded last-attempt/last-save records, not a second journal or storage owner.

## Recovery and lifecycle

Ordinary failed days preserve the existing validated in-place load barrier. Capacity deferral is not a fatal failure and does not trigger recovery. A halted rollback root or unavailable/uncertain runtime requires a fresh realm. The explicit Recover saved town confirmation names the saved day and warns that later unsaved changes are not retained; cancelling does nothing.

Recovery uses only an original-save-owner-confirmed archive or a checksum-valid existing on-device save candidate, never a serialized view or partial worker model. A separate new worker checks runtime arithmetic, hydrates the archive in isolation, loads the complete canonical state, reinitializes the same command authority and compares complete model/RNG before adoption. No weaker/unowned fallback is accepted. The old realm is terminated and its Blob URL revoked only when preparation succeeds. Recovery writes no new archive and preserves the previous saved payload/identity. Browser storage confirmation is not physical/native durability certification.

New realm adoption uses a strictly greater worker epoch; owner generation binds that epoch. Native archive session also rotates. Empty old endpoints can be retired; retired references refuse all submissions. Active archive operations prevent retirement/recovery rather than disappearing. Local async promises correlate both session and ID. Old worker callbacks are instance-guarded, outstanding replies are rejected explicitly, transport/command counters never move backward, and old save tokens cannot address the replacement. Save ownership and native callback semantics remain unchanged.

The worker builder now explicitly excludes `saveStorePromise=discoverIndexedDB()` page startup. The original main-thread owner still discovers and writes storage. Previously, a saved same-origin IndexedDB entry could make a worker execute a Continue-button DOM callback and fail with `$ is not defined`; the saved-town recovery test exposed this. No fake DOM is added and no model work is skipped.

## Evidence

- `fresh_recovery_ui_test.py`: actual command-only owner and actual recovery confirmation/cancel controls; fatal callback, same-owner fresh recovery, unchanged stored payload/no recovery write, retired/stale native sessions, exact-ID late old-worker callback rejection, ordinary failure in-place recovery, and committed payment plus failed storage/retry without second payment.
- `archive_endpoint_test.py`: delayed/cancelled/duplicate/epoch races plus pending retirement refusal and retired-client rejection.
- `default_owner_gate_test.py`: default has no owner and makes no admission claim; empty save neither writes nor reports a persisted/committed town.
- `profile_owned_real_ui.py`: browser-only timing of the actual Agenda/review/choice path, real canvas pans, original save writer and full model/RNG hash comparison against synchronous original UI. Models stay in the browser; only compact metrics/hashes return to Python. Generated late fixture remains778 living residents/3108 historical person records. The fixture is normalized through current original hydration before measurement; a disclosed conserved regional transfer supplies5000 treasury. This is a repeated benchmark, not ordinary play.

Three fresh late-town samples measured model/UI confirmation634–651ms (worker reply550–553ms, including real Agenda preparation), save-owner/token confirmation850–887ms from action start, pending input-to-RAF P95 32–37ms, and maximum frame gaps67–83ms. Original synchronous writer call blocked78–87ms; total owner write took151–164ms including async completion. Exact browser hashes match. These are tiny host samples, not p95 guarantees, physical-device acceptance or sustained1–64× play. Earlier2.20/3.17-second figures included full-model transfer into Python and are superseded as reply latency evidence, not a claimed game speedup. Snapshot application and synchronous storage still cause measurable hitches.

Remaining gates: clean new-model/graphics composition, full command inventory/realtime admission, failed/late native picker/process lifecycle, actual supported WebView durable write/restore, and global bytes/nodes/history/other creator limits. Paid ownership protects its finite allowlist only; it does not make all automatic days transactional or promise unlimited saveability.

For independent acceptance runner0167da9, the finite `--init-type` is **initialize-command-owner**. Build with WORKER_PAID_COMMAND_OWNER=1. The trusted options callback shown above is additionally required when testing same-owner fresh recovery; a late one-off manual init without that retained callback deliberately cannot recover into weaker authority. The status region uses role=status/aria-live=polite and the game root exposes aria-busy during model confirmation. Model/readback/save-ACK phases are distinct. This source is f77's model, so a669 current-model oracle must wait for a clean model port rather than overriding its oracle to make this old-model candidate pass. The timing receipt is bound to its own recorded worker/bridge hashes; later accessibility-only edits are not an additional performance certification.
