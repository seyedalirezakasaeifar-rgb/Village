# Independent identity codec review

Candidate `f93a87ca331669c7a7907453799f009eb8adbfa0`, reviewed without source activation. All opt-in flags were confined to fresh browser test pages. Production default remains false. The synchronous production path can use this codec without integrating the failed cooperative experiment: that controller is absent from the synchronous candidate. The current conservative function-presence gate correctly refuses an unintegrated cooperative build, including an idle/disabled controller.

## Reproduced acceptance evidence

The owner suite passed independently: real birth crossing8000→8001, every person field and selected financial/cargo/provider references, two authentic legacy fixtures,30-day replay,16,000 inactive rows, and its malformed/expansion matrix. Receipt text is retained under `docs/previews/codec-independent/`.

The separate `tools/review_inactive_person_codec.py` witness compares two fresh pages from the same real-birth boundary: original unencoded runtime continuation versus decode followed by continuation. All model state and RNG match after45 days. Before continuation it compares every logical collection apart from documented derived service/stats/visual caches. It reverses both active and inactive directory order, checks dense original IDs, nested high-ID references, Unicode, missing versus null, and safe own `__proto__` data. Duplicate/id dictionary, logical/payload schema, out-of-range estate/home ownership, negative stock, invalid deposit and million-node padding mutations reject without changing caller objects, live state, RNG or save chronology.

Bounds are coherent for this representation:8MiB UTF-8 input,24,000 dense logical identities,8,000 active/16,000 inactive,64 fields,500,000 cells,1,000,000 traversed nodes, depth24, and a conservative16MiB logical-text expansion estimate. JSON parsing occurs before the node/depth traversal, so these are not a proof of peak parser/native memory safety. Native memory/latency acceptance remains necessary. Existing domain validators run after expansion; no identity/reference reindexing occurs.

## Edge cases requiring a decision

1. **Reserved marker downgrade:** starting from an ordinary small town, enable the codec and create its wire value. Set `wire.payload.format='TownLedgerInactivePeople'`. Import succeeds. Disabling is allowed because the logical population is below8000; the resulting ordinary archive cannot be imported, since the parser interprets its retained root marker as a codec envelope. The accepted payload therefore violates the claimed safe downgrade path. Reject the reserved payload marker or define an unambiguous transport discriminator/downgrade policy; do not silently discard logical fields.
2. **Schema rollout contract:** with the flag enabled, setting logical `G.schema=9` causes `archivePayload()` to throw `Unsupported inactive identity format`: the encoder derives `logicalSchema` from the town, while the decoder accepts only8. The current wire9/logical8 candidate works. If activation means incrementing `RELEASE.schema` to9, serialization must be adapted and retested. If wire9 intentionally coexists with logical schema8, document that explicitly. This is not a reason to integrate the failed cooperative engine.

No prototype or codec was activated in a production source file. These edge cases are recorded separately from the passed boundary/replay claims. Combined household/firm version2 review is subsequent work, not covered by this person-only checkpoint.
