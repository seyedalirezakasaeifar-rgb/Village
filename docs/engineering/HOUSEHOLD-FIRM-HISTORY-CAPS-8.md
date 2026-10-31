# Household and firm lifetime-cap proof

Evidence-only branch based on `7500d878e60f2c882767192e2db0d036f815ceed`, synchronous production source SHA-256 `98ab6d44286d2d6300c4533d70e10819a5c102ebfc6e6a09be61b87115883388`. No production edits, codec changes, pruning or admission guards.

## Reproducible admission defects

Run `python tools/assemble.py` and `python tests/test_identity_cap_proof.py`. For just the boundary checks run `PROOF_BOUNDARY_ONLY=1 python tests/test_identity_cap_proof.py`.

Both independent fixtures start with 30 actual simulated days and pad only historical records to exactly 3,000: empty household estates (`home:-1`) or closed/demolished firms with no remaining premises. The ordinary archive is accepted before the action. The test invokes the real `addHouseholdAt` or `createFirm` creator, producing ID 3,000 and count 3,001. Its own ordinary export is rejected without changing live state or RNG. Household admission uses the supported founding-day admission path by temporarily setting day 1, then restores the actual day before validation; this isolates creator capacity, not later-day migration eligibility. Firm creation uses an actual permitted vacant site.

A test-only temporary hydrate function with ONLY the two count thresholds changed to 3,001 accepts both resulting archives through every other existing validator. The original function is restored immediately. Production limits are untouched. This proves the count threshold is the cause rather than another malformed relationship. The resulting household/firm archives are respectively 3,085,610 and 5,969,436 UTF-8 bytes. Synthetic historical padding is not evidence a natural city reached 3,000.

## Natural accumulation measured

Seed 42, settlement, 7,200 actual daily ticks / 20 years: households 67→113, firms 26→43, people 169→376, living 169→331. At year 20, 19 household estates are empty; no firms are closed/demolished in this particular trajectory. Annual samples are retained in `evidence/identity-cap-proof/result.json`. This proves empty household history accumulates naturally in this run, but does not establish a time-to-3,000 or natural firm retirement rate. Firm retirement retention is established by code paths, not claimed as observed in that trajectory.

## Reference and obligation map

| Identity | Incoming references / continuing semantics | Relevant implementation |
| --- | --- | --- |
| Household | `people[].hh`, including deceased/departed residents; complete resident roster; buildings `owner`, household `title.id`, `hh`, `units`, legacy shared-tenancy rosters; firm shareholder `owner` | `20-world`, `27-urban-evolution`, `44-migration`, `90-archive-panels` |
| Household | Cash, deposit claims, credit score/decision, active/default/repaid loan `ownerType/ownerId`; `settledLoanHistory.households[id]`; property tax/rent/compensation and firm liquidation residual payments | `10-finance`, `14-credit-decisions`, `40-development` |
| Household | Crime offender/victim household IDs and recovery payments; events/journal/UI selection and migration records; rehousing/project relationships; transit forecast household sets and fare accounts | `80-civic`, `28-urban-rehousing`, `44-migration`, `46-transit-network`, `47-transit-forecast` |
| Firm | `people[].job`, buildings `firm`, firm `title.id`, other firm ownership paths, field-owner IDs/counts, farm projects `firmId`, airport operator `firm` | `20-world`, `27-urban-evolution`, `40-development`, `90-archive-panels` |
| Firm | Cash/stock, active/default loans and settled summaries `firms[id]`, shareholder claims, suppliers/buyers via domestic freight `from/to`; regional contracts/orders/shipments/procurement and port cargo references | `10-finance`, `22-regional-markets`, `23-trade-infrastructure`, `26-logistics`, `26a-port-logistics` |
| Firm | Private school/fire provision, mall labour/retail history, training/employment references, brownfield old-site provenance, planned construction and civic project/campaign references | `29-retail-labour`, `30-brownfields`, `45-public-services`, `98-sustained-projects` |

These are required audit categories, not an assertion that arbitrary future fields can be dropped. All dense-array index identities must remain stable. Regional creditor bank ID -1 is legitimate and must survive any later archive design; it is not a household/firm ID.

`migrationReleaseTenancy` intentionally only releases the address. It preserves the estate's cash, deposits, property, shareholder and loan claims. `yearlyDemographics` removes deceased people from household membership but retains both identity records and estate. There is no general estate-to-heir dissolution transaction in these paths. Inventing one as save cleanup would change economic rules.

`liquidateFirm` pays secured creditors, records unpaid default claims, distributes only residual cash to the household shareholder and retains the closed firm. Land assembly marks it demolished after removing its building. A closed firm with premises can reopen; closed alone therefore cannot mean immutable history. A demolished firm may still be referenced by defaults, old jobs, cargo or provenance. Settled loan summaries deliberately retain borrower IDs after original receipts are compacted.

## Safe options and decision

1. Prefer a separately reviewed versioned lossless wire representation for complete inactive household/firm records, with dense logical reconstruction before existing validators. Preserve every field, ID and nested reference, using explicit active/inactive classification and independent byte/node/expansion budgets. This requires cooperative logical snapshots and native memory testing just as the person candidate does; it is not implemented or stacked here.
2. A truly quiescent runtime tombstone requires a complete reverse-reference registry, no active/default obligations, no balances/deposits/stock/property/shareholder rights, no resumable company site, and a defined estate/heir policy. Even then, preserve stable IDs and historical receipts. Current code does not establish those invariants, so destructive pruning is unsafe.
3. Summarizing financial receipts cannot dissolve the borrower identity: `settledLoanHistory` still points to it. Moving these summaries to historical names alone would lose identity semantics. Capacity guards on all births/enterprise creation are not proposed.

Residual release limitation: unchanged production can admit a valid 3,001st household or firm and reject its own archive. This branch proves and maps the risk; no safe comprehensive archival implementation is claimed. The separate person codec does not resolve these limits. Natural accumulation does not prove an unlimited-run growth rate, and no arbitrary infinite-city promise is made.
