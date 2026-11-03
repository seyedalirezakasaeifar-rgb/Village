# Integration checkpoint: trading town

The integration branch retains the private institution economy while incorporating the first visual-world slice and the mayor's desk/directions. Private provider coverage feeds `programmeMetrics()` and `districtMetrics()`; ownership filters, escrow accounting and qualified staffing were preserved. Conflicts in the daily-settlement hook and archive validator were resolved by retaining both service and journey logic. The distribution bundle was reassembled from all modules.

Development metadata is now version 8.0.0, code 22, schema 7. This schema bump is required by authoritative regional cargo and private construction escrow, not by the additive guide alone. Previous schema-6 and older supported saves remain importable; schema-7 exports are intentionally rejected by the old 7.1.1 application. No new APK has been published at this checkpoint.

Integrated tests passed: mayor control journey and all three direction-rule fixtures; private school and brigade invitations, construction, reserved-capital save/restore, fee clients and licensing; matched public/none/private/voucher flows, sustained learning, paused-public-course fallback, closure, viable recapitalization and zero-fee exit; archive schema bounds; seven responsive layouts; world-art state independence, paused determinism, freight continuity and far-zoom LOD; regional cash/commodity flows and core release gates. Each report contains its own assembled source hash. Some tests precede the final ownership-only correction; private entry, private flows, mayor journey and core gates were rerun after it. Full immutable release acceptance remains later work.

Provider investment now uses one bounded catchment BFS per candidate site rather than repeated home-by-home shortest-route lookups. Paused public training does not prevent a family purchasing a private course. New region-funded service providers belong to their actual regional investors, not a randomly gifted household shareholder.

These are integrated development gates, not proof of physical-device performance, subjective music/art quality or a multi-hour human play experience. The earlier passive economic samples remain healthy; that is reliability evidence and does not itself establish engaging difficulty. Continue authored opportunities, logistics/resource decisions, long-session play and recovery testing before release.

## Integrated art and performance follow-up

Both visual commits (`eae3e91`, then `f3af3fb`) and the mayor experience commit (`ffc8f50`) are integrated. The generated bundle retains version 8.0.0 / code 22 / schema 7, private service logic, transaction-dialog accounting, journey validation and all daily hooks. Disabled seasons remain disabled: tree art uses the existing presentation month and never changes climate options.

A real integration regression was found despite passing the old paint-only gate. Repeated whole-town public access scans inside each private-provider household/candidate query, plus home-anchored fire routing, stalled the simulation. The uncached 2,000-resident run had 28.1 ms median / 88.5 ms P95 ticks and a 1,450 ms RAF P99. It simulated 154 days in 9.27 seconds; its last speed indicator fell to about 7x.

Public-school access is now mapped once per relevant day/network/provision/population, and public fire responses are cached with station-anchored route trees. Investor catchments use one bounded BFS per candidate. Pointwise comparisons against uncached public access pass after funding, day and road changes. Three repeated whole-town school lookups require one access scan rather than repeated household scans.

The final isolated 2,000-resident / 713-building run simulated 310 days in 8.03 seconds (about 63.7x from days and elapsed time): 9.4 ms median / 24.0 ms P95 ticks, 40.5 ms P95 draw and 116.7 ms RAF P99. Intermediate unchanged cache runs simulated 309 and 311 days in about 8 seconds. These are host Chromium measurements, not Android FPS. Curated before/after JSON remains in reports/integration; negative evidence was retained.

The large-town gate now checks simulation throughput, RAF tail and UI response as well as paint. It would reject the discovered 7x / 1.45-second-stall regression. Final provider fees display cents, and malformed non-private escrow is rejected before adopting an archive. Private invitations, escrow rejection and cached service equivalence passed after these final corrections. Full final immutable release QA remains pending.
