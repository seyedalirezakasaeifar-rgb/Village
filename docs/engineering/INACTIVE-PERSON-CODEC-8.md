# Experimental lossless inactive-person archive codec

Base: `5c503015e9572329393f01242732b7ca0bed7708`. Production remains OFF and release schema remains 8. This is a review candidate, not an activated long-play fix.

## Representation contract

With `window.__inactivePersonCodec.enable(true)`, `archivePayload()` returns a JSON envelope with `format: "TownLedgerInactivePeople"`, `version: 1`, `schema: 9`, `logicalSchema: 8`, `payload` and `inactive`. The payload contains all ordinary archive fields, schema 9, and complete active people. Inactive means exactly `deceased === true || movedAway === true`.

`inactive` contains total person count, a sorted unique field-name dictionary excluding `id`, and rows `[originalId, ascendingFieldIndices, correspondingValues]`. Presence indices preserve missing fields versus explicit null. Every JSON field, nested value and original ID is retained. Decoding reconstructs the dense original people array and schema 8 before existing migration/domain validation. No person, household, inheritance, employment, migration or financial reference is reindexed. Unknown person fields survive. Own `__proto__` values use safe property definitions.

`archiveLogicalPayload()` is the original unencoded complete logical serializer. The cooperative rollback owner must use complete logical snapshots, or explicitly decode this envelope before reading `snapshot.people`. Direct JSON.parse of the wire archive is NOT a logical snapshot. Enabling is hard-blocked whenever the cooperative controller function exists, even while idle, until that integration is reviewed. The controller itself is unchanged. Disabling while a live town has over 8,000 identities is also blocked; load a smaller legacy town first. There is no persisted experimental preference.

## Budgets and failure behavior

Wire UTF-8 bytes: 8 MiB. Decoded expansion upper bound: 16 MiB, calculated before rebuilding fields from encoded bytes plus object/key overhead. Active people: 8,000; inactive: 16,000; total: 24,000; dictionary fields: 64 of at most 128 characters; decoded cells: 500,000; traversed nodes: 1,000,000; nesting depth: 24. These are independent bounds, so the total record maximum need not be attainable for unusually large records. Existing household/firm/financial limits still apply.

Only a successfully validated versioned envelope receives the expanded identity allowance. Ordinary archives retain the existing 8,000 limit. Unsupported versions, duplicate IDs, holes, malformed rows, hidden active people, invalid estate references, truncation and oversized expansion reject on a private candidate before live adoption. Caller objects, live state, RNG and save ordering remain unchanged. The encoder validates its independently parsed output before returning it. It fails explicitly if any bound is exceeded; it does not drop history, freeze births or silently emit an ordinary oversized archive.

## Evidence

`python tools/assemble.py`; `python tests/test_inactive_person_codec.py`; and `TOWNLEDGER_CORE_ONLY=1 TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_release.py` passed. Tested assembled SHA-256: `cf245639bc410847c00372c19ec58974812e1480eb762df14968913003b8931e`. Detailed metrics are in `evidence/inactive-person-codec/result.json`; no whole saves are published.

A real `birthsAndGenerations()` transition crossed 8,000 to 8,001 identities. The old ordinary archive was rejected, the encoded archive restored every person/household/firm/bank/loan field and exact 30-day model/RNG continuation. Two authentic repository legacy fixtures and a mixed cargo/fare/provider/mall fixture passed. Twelve malformed classes plus truncation/oversize preserved live state and input objects. Expansion amplification was specifically rejected by the decoded-byte guard.

At 8,001 identities the wire was 978,595 bytes versus 1,346,563 logical bytes; host encode/decode took 125/84 ms. At 16,000 inactive / 16,167 total, wire size was 1,914,692 bytes and combined encode/decode took 363 ms. After adversarial allocations, sampled host heap was 108 MB, falling to 18.2 MB after forced GC; this is neither peak allocation nor an Android memory certification. Forced GC occurred only in the test harness after simulation.

## Required before activation

Independent review/tests, an intentional schema-9 rollout and recovery UX, cooperative snapshot integration, and physical/native mobile memory and latency measurement remain outstanding. Older builds cannot read wire schema 9. The flag must not be silently enabled in a production build. Dense runtime person loops remain unchanged and are not certified smooth at the largest bound. Household and firm lifetime caps remain separate unresolved limitations. The representation is finite, not a claim of unlimited city history.
