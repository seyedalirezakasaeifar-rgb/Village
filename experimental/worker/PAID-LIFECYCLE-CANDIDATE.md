# Disabled worker paid/lifecycle candidate

Base: public paid dispatcher 7233d8d17178307a5ebea5eb7cc106f14e42df66 (d2b7086 production source plus its published DOM-free boundaries). The dispatcher additionally includes the published bb58ac3 local review-ID check. Production startup remains synchronous; no release admission flag is enabled.

## Corrected protocol

All transport IDs are increasing safe integers. Load, step, model mutations and save-token operations additionally require increasing command IDs within the current worker epoch. Failed admitted commands consume their IDs; correcting input requires a fresh ID. A current-epoch load advances the epoch and resets command numbering. Loads during an active completed-day batch refuse. Stale loads cannot reset the town.

Presentation effects remain in an epoch/serial log until `effects-ack` with a validated `through` serial. Read/export never consume presentation effects. The bridge deduplicates effect delivery and acknowledges the delivered prefix; this is a presentation receipt, not a durable-storage acknowledgement. Export contains only canonical completed model state. A failed day fences model export/access until recovery.

Snapshots are constructed after the shared controller's committed saver microtasks drain. Paid replies cannot acknowledge provisional work. Council settlement uses the one published serializable dispatcher and its worker-local review token; the old handwritten choice settlement is removed. Controller generation is workerEpoch, never saveEpoch. Runtime outbox and effect serial are registered graph roots for rollback; command and epoch counters stay outside financial rollback.

Archive endpoint submission copies scalar request fields into an immutable packet before asynchronous execution. Caller mutation cannot turn an accepted export into a restore. Real-page clients must send the current `.status().session`, epoch and request ID; cancellation is also session scoped. Session validation precedes consuming the current ID. Native asynchronous callbacks must adopt this session contract. Save-prepare/abort/ACK are token-bound; only the original storage owner may issue ACK after its verified write. These protocol tests do not certify Android filesystem durability.

## Reproduction and evidence

```
python tools/assemble.py
npm ci --prefix experimental/worker
WORKER_PAID_TEST_OWNER=1 node experimental/worker/build.cjs
python experimental/worker/paid_composition_test.py
python experimental/worker/lifecycle_actual_test.py --worker-code experimental/worker/model.generated.js
python experimental/worker/archive_endpoint_test.py
```

`paid-composition-proof.json`: original host functions versus worker, exact canonical model/RNG for a real council choice and funded private school. Tests reservation refusal and fresh-ID recovery, plus project-creator refusal after payment and exact rollback/recovery. Fixture liquidity is transferred from regional funds, not created. Save intent must appear in the same post-drain committed reply.

`lifecycle-actual-proof.json`: adapts the exact public d51b8f0 economic fixtures to the corrected command/effect protocol. No economic stubs. It verifies duplicate steps, legitimate new steps, stale load full-state preservation, invalid/repeated/stale council IDs, export during committed-day yield, explicit effect ACK, save-token abort/retry/restore invalidation, and mutable archive-request aliasing. `independent-negative-actual-model.json` preserves the original published failures. `archive-endpoint-proof.json` covers delayed/cancelled replies, queue and epoch/session races.

The opt-in build includes ONLY the public `current-paid-owner.js` reference test owner. Normal builds exclude it and paid commands refuse until an approved owner is installed. This is not a production reservation-policy certification or a performance win claim.

## Remaining acceptance blockers

- Approved production admission owner is not available in this branch. Its separately denied/unpublished artifacts were not copied.
- Full real UI panel preparation and preview RNG ordering must be unified with worker context; the proof explicitly supplies logical panel context. The existing finite routing inventory still has unsupported command families. No unsupported financial operation may claim success.
- Native async save/load callback adoption, verified durable write ownership and actual supported-runtime end-to-end acceptance remain outstanding. API30 emulator arithmetic failures are guarded, not worked around by changing archive RNG.
- Dense throughput/input and supported-native gates must be rerun on the final composed source before promotion. Historical experimental receipts are source-specific and do not certify this source.
