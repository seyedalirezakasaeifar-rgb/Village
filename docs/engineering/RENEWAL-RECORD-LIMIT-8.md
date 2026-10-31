# Renewal creator/importer boundary: confirmed and guarded

Base dda6694. Before this patch, a valid 3,000-entry renewal archive could accept
one more paid `brownfieldAssess` through the normal API and then fail its own
`validateBrownfields` import cap. The negative result is retained with its exact
source hash. This is a genuine creator/importer mismatch, not a measured leak or
proof that an unassisted city naturally completes 3,000 renewals first.

The boundary fixture completes one real assessment/acquisition/funded preparation/
park reuse, then clones that valid completed receipt into distinct historical
identifiers with a consistent advanced ID counter. It is synthetic historical
provenance, not 2,998 claimed simulated renewals. The 3,000th assessment and refused
3,001st attempt are actual paid API actions on separate real industrial premises.
The initial boundary itself successfully imports; the old next action did not.
Other lifetime record limits may be encountered earlier in a natural town.

Fix: one shared `BROWNFIELD_RECORD_LIMIT = 3000` binds quote/admission and validator.
At capacity a new survey is declined before payment or mutation, with an explicit
renewal-ledger message. Existing acquisition/funding/preparation/reuse remain usable;
a real existing survey is acquired, funded and reaches ready while full. An
unacquired survey may be voluntarily withdrawn through the existing workflow to
free a slot. No automatic pruning, title alteration, forced relocation or deleted
provenance is introduced, and no archive-schema change is needed.

Before: actual next assessment accepted; same-version import rejected.
After: actual next assessment refused; unchanged funds/records; import succeeds.
The at-limit funded project and all historical records survive, and thirty-day
late continuation compares exactly. Existing active-industry renewal/player-path
and authentic legacy tenancy/120-day continuation regressions also pass.
Generated bundle is excluded; integration must reassemble.

## Other creator/importer limits requiring separate coordination

The read-only audit also finds import limits of 3,000 firm/household records,
8,000 person records and 10,000 loan records. Active population's 2,000 ceiling
is not a bound on historical persons, and `bankLoan` checks active borrower credit
but not total historical loan count before push. `createFirm` likewise appends
without a total retained-firm check. These are concrete code-path risks, not newly
proven natural-run failures. They are not silently called safe because forty-year
samples fit below them.

A blanket null return in createFirm would be unsafe: direct construction and funded
project completion callers must reserve capacity before spending and preserve any
already funded obligations. Birth/estate records and loan/title claims cannot be
deleted merely to satisfy an import cap. Those shared-model admission/retention APIs
need their own bounded repro and owner coordination; this patch does not alter
migration, finance or project settlement behavior opportunistically.

Existing archives above 3,000 renewal entries were already unsupported. This
prevention guard does not claim to recover them or provide unlimited industrial
redevelopment. It preserves all supported archives and stops this exact new silent
failure at the creation boundary. No whole synthetic checkpoint is published.
