# Disabled combined identity codec candidate

Dependency: person-codec candidate `f93a87ca331669c7a7907453799f009eb8adbfa0`, itself based on integrated `7500d878`. This is a separate review branch, not a second independent codec or production activation. Original person-candidate docs/evidence describe its previous version-1 format; this document specifies the version-2 extension.

## Wire contract and logical state

The envelope remains `format: TownLedgerInactivePeople`, schema 9 / logical schema 8. Version 2 adds exactly `entities.households` and `entities.firms`, each a directory `{total,fields,rows}`. Payload arrays contain complete active records; historical directory rows use `[originalId, ascendingFieldIndices, values]`. All fields and nested values remain present, including unknown biography/heir metadata, absent-versus-null distinctions and safe own `__proto__` keys. No financial summarization, ID reuse, reindexing, tombstone mutation rules or changes to estate law are introduced.

Household history means only `people` is an empty array. It does NOT mean assets, claims, ownership or debts are absent. Firm history means BOTH `closed === true` and `demolished === true`; a merely closed company remains active for this representation because it may reopen. These are wire partition predicates only: a historical firm's cargo, defaults, balances or ownership remain complete and operational after decoding. A household gaining members or a firm changing its flags moves sections on the next export without identity changes.

Version 1 remains readable with its original person-only allowance and original 3,000 household/firm limits. A version-1 envelope cannot smuggle expanded household/firm arrays. Version 2 reconstructs household and firm dense arrays before person estate-reference validation; all existing domain validators then run on logical schema 8. Unrecognized envelope versions and malformed directories reject before adoption. Ordinary schema-8 archives retain all original count limits.

`archiveLogicalPayload()` is still the complete logical serializer. `archivePayload()` emits the version-2 wire only when explicitly enabled. Cooperative builds remain hard-blocked from enabling; rollback owners must use complete logical snapshots or the shared decoder, never direct `JSON.parse(wire).payload` as runtime state. No prototype scheduling code is changed. Disabling while any live identity count exceeds old limits is refused to prevent accidental downgrade. No preference persists activation.

## One shared allocation budget

All three directories share 8 MiB UTF-8 encoded, 16 MiB conservative decoded expansion, 500,000 reconstructed cells, 1,000,000 visited nodes and depth 24. They do not receive additive byte/cell/node allowances. Expansion accounting starts with the whole wire plus per-record overhead, then adds decoded key overhead across households, firms AND people. A combined key-expansion attack that would fit each estate directory separately is rejected by the shared bound before all fields are allocated.

Person counts remain active 8,000 / historical 16,000 / total 24,000, dictionary 64 fields. Each household/firm category is active 3,000 / historical 6,000 / total 9,000, dictionary 128 fields; keys at most 128 characters. Maximum directory totals sum to 42,000, but shared byte/node/cell limits may reject combinations below these counts, especially rich records. These are intersecting limits, not a promise all maxima fit simultaneously. A record is never truncated to make it fit. Encoding fails explicitly rather than returning an unimportable archive.

These bounds constrain representation expansion, not Android peak heap. Encoding holds the existing logical model plus serialization, parsed and validation candidates. Existing dense runtime loops remain unchanged. Native memory/latency measurement and improved transient allocation are required before considering activation.

## Evidence and limits

Assembled source SHA-256 `ea2d0d6f388e2089e916d842352a2e3467b75b41f0a776f443409fd962174ddb`.

`test_estate_firm_codec.py` passes simultaneous real creator actions from accepted 3,000-record historical arrays to 3,001 households AND firms. Household action uses founding-day admission for a controlled capacity proof, restoring the day before export; this is not a natural 3,000-household trajectory. Full decoded logical JSON equals the original before existing hydration initialization. Initial hydration still applies its established defaults/recomputed statistics to newly created entities; exact continuation is tested from that canonical hydrated state rather than suppressing differences.

Fixture retains estate cash/deposits/property title/custom heir metadata, deceased person's estate/employment references, firm stock/cash/shareholder, live domestic freight to/from a demolished firm, unpaid default loan with regional creditor bank -1, and both household/firm settled-loan summaries. Full-field equality is stronger than selecting only balances. Exact 30-day complete model/RNG continuation passes (only existing transport visual snapshots excluded as in prior replay tests). Thirteen malformed classes, truncation, caller object/live state/RNG/save-order atomicity, version-1 compatibility and version-1 cap isolation pass.

Combined boundary wire is 6,101,949 bytes versus 8,741,249 logical bytes; host encode/decode 421/222 ms. Heap sampled after adversarial tests reached 225.7 MB; after forced test GC 36.7 MB. Neither is a measured peak or Android guarantee. This is a significant unresolved activation concern.

Person-codec regression also passes actual 8,000→8,001 birth, 16,000 historical-person capacity, Unicode/null/prototype safety, old fixtures and mixed cargo/fares/provider/mall preservation. Detailed source-bound reports are under `evidence/estate-firm-codec`. No whole saves are published.

Production remains disabled and schema 8 unchanged. Independent review, explicit schema rollout/recovery UX, cooperative rollback integration, native memory/latency acceptance and broader combined capacity testing remain blockers to enabling. The candidate is finite and does not claim unlimited city history. Loan-retention/regional-creditor changes are preserved.

Default-disabled core release gates passed with `TOWNLEDGER_CORE_ONLY=1 TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_release.py`. `test_loan_history_limit.py` and `test_regional_loan_summary.py` both passed. These are targeted candidate checks, not a final release soak or native certification.
