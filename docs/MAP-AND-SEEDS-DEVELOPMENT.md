# Portable founding seeds and a clearer phone map

Unpackaged source development after 7.0.5. Existing signed checkpoint APKs are unchanged.

## Confirmed founding defect

The founding-lot comparator called the seeded random generator during sorting. That comparator was inconsistent: its result for the same pair could change, and different engines could make different numbers of comparisons. A controlled alternate-sort test reproduced the failure: settlement seed 42 started with total cash 15,505,254 under the native sort and 15,467,827 under stable insertion sorting, with different RNG states.

Each candidate lot now receives one seeded rank before sorting. Rank and tile ID form a stable, consistent order. Fifteen authored starts—five scenarios × three seeds—produce identical complete opening archives and RNG state under both algorithms. This directly tests the identified mechanism; it is not a claim of exhaustive cross-engine numerical equivalence.

New towns change once relative to the previous generation algorithm. Existing archives keep their streets, buildings, balances and saved RNG state; loading does not regenerate a town.

## A useful map hierarchy

The map has two actionable summaries. Town Crier opens the public record; the compact economic card opens Economy. The latter includes paused status and initial map guidance, replacing separate overlapping banners. Guidance disappears after map interaction, and these summaries leave the map clear while a drawer is open. Closing a drawer restores focus to a visible launcher, including the two map buttons.

Food disconnection and substantial unfilled essential demand are reported before a positive market assessment. Weak funded care/learning remains visible even when employment is strong. The card shows actual care/school coverage rather than duplicating the employment KPI and calling the whole town prosperous. No economic coefficients were adjusted for these messages.

Navigation now has twelve consistent vector icons. Six governance actions precede six reports/options. Small landscape phones use two rows of six with 44-pixel targets, instead of clipping the last destinations; larger landscape screens retain a single row. Portrait uses the existing two-row layout. Header time controls remain reachable down to 568×320, including a deliberately long date and large treasury. Million-dollar header values use a compact suffix with the exact amount retained in the title and full financial reports. Safety remains in Town Hall when the narrowest landscape header prioritizes cash, work and time controls.

Map controls have 44-pixel targets; portrait places them in a two-by-two group to avoid the Crier. Ordinary-selector and physical-edge fallbacks improve older WebView styling without requiring :is selectors or inset shorthand.

## Evidence

Frozen source SHA256: `1aacc0d583efd54e6367e1fcfe2e5a4348d875d7a82df182d82dcba5cb7548fc`.

Twelve development gates passed with every shipped asset fingerprint held fixed: alternate-sort starts, map interaction/focus, seven mobile layouts, contrast, controls, older APIs, programme progression, core release checks, eight default-start histories, fifteen three-year scenario histories, matched policy/recovery experiments and live large-town performance.

The 2,000-resident/requested64× host run measured draw p95 32.7ms, tick p95 14.4ms and reported speed64.9×; no browser errors were recorded. These are host results, not Android FPS. Full immutable release QA remains required after the new land/water features.

Fixed-seed phone comparisons are in [previews/map-hierarchy](previews/map-hierarchy), with separate before/after asset provenance. The narrow two-row navigation uses more vertical space in exchange for making every destination visible and touchable. Actual screenshot pixels were inspected; the improvement is not inferred from document overflow alone.

## Required next feature phase

The user's latest request adds substantial mayor-purchased land parcels and productive waterfront activity with visible boats/docks. Those features are not implemented in this checkpoint. They take priority over further optional polish. Purchases need real treasury settlement, clear ownership/buildability, confirmation, repeated-purchase protection and migration; water activity needs real jobs, production/trade/logistics and bounded animation, not decorative boats alone.
