# Verified district composition and service-cache correction

Base `848bf1bfb8fdddc3155ba5a7773348d28073ade4`; assembled source SHA-256 `3af2f8355807bfa3c23482b25816f657ae618970dfeb4e38dc6c34aa3140115c`.

This composition ports district candidate `ff837b3eabb921ced2b5266d8a009cea8bbfdeb2` and independently isolates the service-access correction from `ff9f0d067aef13978b8a07c11ef91f4b2c673d68`. It does **not** import the broader `ba7149fc` farm-relocation/expansion changes or `fb48ad1b` follow-on. Their separate journey review remains outstanding. Accepted deed canonicalization, frontage culling, native wrapper, paid receipts, funded vacancy allocation and committed-save protocol remain present. Experimental renderer/worker/admission/identity codecs stay disabled or absent.

## Former hold resolved

The independent original failure oracles now find no cached-versus-fresh profile differences after an ordinary regional day. Their complete model snapshot is unchanged. The actual observed market character remains proposed through days 721/751/781 and commits at day 811, without RNG use. Repeated descriptor reads retain the same cache and leave complete archive, money and RNG unchanged. Normal bank deposits/income changes invalidate observation caches at writer boundaries; reads do not invalidate or rebuild them repeatedly.

Natural six-year seed-42/101 towns produce active market and downtown observations, including market/employment overlap. Operating staff, recent sales and road-reachable households support the market tag; it disappears in the controlled no-staff/no-sales case. No financial district appears in the natural samples: the banks remain the three founding institutions. No decorative branches, local financial-access benefit, new jobs or income bonus are manufactured.

Renderer contract: most `urbanBuildingDescriptor` economic/access fields are **8 × 8 block aggregates**, not per-building worker/customer/bank-account counts. Building kind and physical condition are property-level. Consumers must not duplicate block totals into per-building populations or accounts. The Newfoundland family/streetscape cues are a data handoff, not implemented mesh fidelity or visual acceptance.

## A real replay regression was found and fixed

The preexisting retail-proposal control test passes on public source `78f4c3b5…` at 848bf1b. The district-only composition (`49acb751…`) fails the same replay. All nine differences are enumerated: six service-access/staffing fields, two civic-training day counters and person 107's skill. This was not dismissed as harmless derived state or as a public-baseline failure. `tools/review_service_access_regression.py` reconstructs the three immutable source combinations and reproduces **public pass / district-only failure / corrected composition pass** with all differences visible.

The extra early service-access reader exposed an underlying cache dependency on `G.stats.population`, a published rollup that can lag the household rows used by that very allocation. The isolated correction derives served/coverage population from the same living household demand rows. It changes no payroll formula, wage, authorization or purchase cap. It is not a normalization or a skipped field: the complete replay now agrees.

Independent effect checks perturb only the published aggregate across twelve controlled stale-stat cases in three authored scenarios, without adding people/workers or changing balances. Every fixed allocation matches the unchanged live demand; normal allocations, policy outlooks and the **entire state after actual normal purchases** are identical with the old allocator when the census is consistent. Across four normal 370-day scenario journeys, all **2,960 health/school purchase boundaries** see a published census matching live demand, with conserved currency. These are bounded checks, not a universal claim about arbitrary corrupted aggregates. Correcting previously stale training/access can change later economic outcomes; no trajectory neutrality is asserted.

## Exact tenancy-order provenance

The paired 20-year experiment uses public 848bf1b and the final composition, with both wire hashes recorded. The public source's first cold restore changes exactly:

- `.buildings.84.units.1`: 135 → 128
- `.buildings.84.units.3`: 128 → 135

Here 84 is an array index. Each individual tenant list retains the same members; all other complete state fields, household/person identities, home assignments, claims, finance, cargo and RNG remain identical. Both sources contain byte-identical archive-tenancy normalization and tenancy-writer files. Feeding either exact archive to both loaders produces identical complete results. Normalization is idempotent. After that explicit existing import contract, thirty-day replay agrees completely, including traffic/visual state, with zero excluded fields.

The final composition's fresh day-7201 case needs **no initial cold normalization at all**. Its population is 360 versus 426 in the accepted public source's 20-year sample; the district-only intermediate had 365. These are observed trajectories, not an isolated causal balance estimate or a claim of improved population. An ordinary-resource regional two-year route reaches 778 residents, compared with 765 in the earlier public audit; school/health pressures remain recorded. There is no universal solvency/growth claim.

The repaired independent spatial-kernel oracle still passes all four Float32 arrays, block metadata, seven mutation/invalidation cases and 180-day complete-state comparison through day 901. The historical missing-fixture failure remains preserved in 13633d49; it was replaced with a committed ordinary-resource checkpoint rather than silently skipped.

## Source-matched checks and measured cost

**43 final functional scripts pass** (20 core, 17 focused, four owner/kernel, paired tenancy provenance and the purchase-boundary oracle). All final results and preserved negatives are bound in [the manifest](evidence/commercial-district-integration/manifest.json). Two early driver mistakes (a hard-coded legacy residential label and a mistyped trajectory-test filename) are retained and corrected. The profile report now records actual day 2161 separately from 2160 elapsed days. One parallel committed-save test hit its promise-count assertion; an isolated diagnostic passed. The driver had left Continue's real clock running. It now explicitly pauses through the actual control before controlled replay/fault phases and additionally checks the entire persisted payload on failure; no production save-fence weakening was made.

A standalone alternating host profile on the same earned 765-person archive measured median test-step wall time 599.4 → 633.3 ms for 20 days, and 936.1 → 1046.3 ms for 30 days including a monthly boundary: about +5.7% / +11.8%. Cold spatial CPU rose 20.8 → 43.2 ms and 31.8 → 78.5 ms respectively. This measured observation cost is a further optimization target, not a smoothness or speed improvement. The samples use seven-day warmups and three alternating repeats; no renderer/GPU, physical input, native memory or thermal performance acceptance is implied.

Core release checks run in core-only mode; the older 115-year result is not reassigned to this source. No Android/device or selected-style visual acceptance, signing, packaging, release or integration promotion is performed here.
