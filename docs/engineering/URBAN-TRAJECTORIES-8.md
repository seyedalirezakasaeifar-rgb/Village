# Integrated urban trajectory validation

Base: `525e47dd3967741fb59d2fd06921c1647a29a24a`, with urban, private-service viability, physical logistics, transit and art already integrated. This branch starts from that commit rather than replaying previous urban commits. Rendering and transit optimisations are outside this validation scope.

## Confirmed defects and bounded fixes

### Retail labour forecast disagreed with actual hiring

The old shopping-centre gate counted every working-age person with `job < 0`, including funded public employees. Actual job assignment deliberately excludes those employees. A naturally evolved regional seed-42 town at day 1081 has nine people counted by the old gate and **zero genuine jobseekers**; a funded centre has no staff for years.

`29-retail-labour.js` now uses reachable actual identities, public/current/previous role reservations, job-search delays and existing job-change cooldowns. Unemployed residents bid the legal wage; an employed private worker requires a real 12.1% wage premium. Private school/brigade workers are excluded from retail recruitment. Plans choose 2–8 positions from the forecast throughput, price the actual wage offer, commercial rates, overhead and profit tax, and retain the construction-plus-capital return hurdle. Completion preserves the paid staff/wage proposal; the six-tile centre's funded checkout capacity is represented by scale 2. Actual demand still sets later staffing. No customers, wages, equity or tax receipts are granted by the forecast.

Operating centres can recruit into funded vacancies. An empty operator can review a viable wage offer monthly using current local demand, current inventory cost and its own 90-day payroll reserve. Employees move between actual rosters and receive pay once through ordinary payroll. Private provider recruitment runs first; passenger/public reservations remain protected. `serviceStaff` / `serviceWage` construction fields and post-production `dispatchRegionalContracts()` ordering are unchanged.

The exact natural archive is committed as `tests/fixtures/urban-retail-unfunded-labour.json.gz`. On the same next-day replay, the old centre still has zero staff and no payroll. The corrected centre offers $32.62/day, hires one real private employee, pays that wage, and earns observed retail receipts. At day 90 it has two staff and positive operating profit. Cash and commodity accounting remain valid; there is no worker duplication or raid on funded public services. This is a causal defect replay. Whole multi-year strategies below are not isolated causal estimates.

### Reserved public housing could be occupied or privatised automatically

The mayor could pay $20,000 for a reserved replacement home, only for normal immigration/household formation to occupy it before clearance. The failure reproduced by day 92 in an ordinary regional town: the home still carried `relocationReserve: true`, but a new household occupied it, so archive restore rejected the town. General vacancy readers now exclude reserved sites. Private redevelopment also excludes municipal titles/municipal replacement housing rather than silently appropriating them. A real-control regression runs a funded reserve through one year of ordinary immigration, family formation, private investment and repeated save restores. No residents are injected and no existing household is erased to make the test pass.

### Larger projects crossed planning boundaries

Only a building's anchor checked planning permission. A vacant 2 × 2 private depot could extend into a neighbouring civic reserve. `canPlace` now applies the existing authoritative permission rule to every footprint tile. Shopping centres' manual six-tile assembly likewise checks parcel and neighbourhood permissions at every tile, including working waterfront restrictions.

A second real-control case purchases a parcel and records the employment charter: the old rule excluded cottages but permitted apartments and towers. The employment charter now excludes all three residential forms. Existing lawful buildings and already funded projects are not demolished or confiscated by these permission checks.

## Interfaces and integration hooks

New APIs: `urbanRetailLabour(site, offered?)`, `urbanRetailPlan(site, customers)`, `recruitUrbanRetailStaff(only?)`, `validateUrbanRetailLabour(data)`. Labour bid objects contain person ID, wage and real road distance, not a spawned workforce. `retailStaff` and `retailWage` are optional construction fields; old funded projects retain their previous staffing defaults. `retailHiringReview` is a validated optional firm date.

Small hooks: `30-economy` calls retail recruitment after existing private-service recruitment and before public-role reset/payroll; `40-development` uses funded retail staffing at completion and protects municipal homes from private redevelopment; `45-public-services` protects reservations in ordinary vacancy readers; `90-archive-panels` validates the new optional fields. `20-world`, `24-district-programmes` and `27-urban-evolution` enforce full-site permission and staffing-aware proposals. No passenger/freight graph, transit remapper, private provider allocation or logistics ownership code is replaced.

## Evidence design and interpretation

`tools/audit_urban_trajectories.py` uses authored scenario/seed resets, actual mayor buttons, paid road placement and staged policy enactment, plus accelerated normal clock ticks. It injects no cash, people, stock, land or successful outcome. The clock resolves council letters through their normal first-affordable choice; this is disclosed and is not a claim of human multi-hour playtesting.

Three regional seeds are followed first for three years before/after the labour correction. A longer six-year paired audit compares market-led play with an intervention arm that buys up to six adjoining districts, records real charters, pays for legal street connections, and funds schools/clinics through normal policy controls. The intervention retains a cash reserve and cannot exceed the actual slider ceilings. Initially lower/higher income cohorts are fixed from day-91 measured income per person; survivors are tracked rather than relabelled to produce a favourable result.

Quarterly observations are censored samples: moves between samples, demographic changes and intervening firm conditions can be missed. A farmer's sampled field count can rise after relocation through genuine later planting. Neighbourhood income bands are relative observed income labels, not assigned traits, wage bonuses or crime modifiers. Learning figures combine resident-based public coverage with private paid-learner equivalents and differ with pupil ages; cohort comparisons must not be interpreted as identical school-age enrolment rates. Liquid savings exclude property equity. Wages, pensions, rental receipts, dividends and aid remain actual funded sources.

The paired whole-town strategies diverge in later random/council events and cannot identify an isolated treatment effect. Negative profit quarters, low savings, delayed access and unstaffed sites are retained in the compressed traces and summary. Subjective fun and Android/device performance remain separate acceptance gates.

## Shared-model finding for the integration lead

At the seed-42 intervention endpoint, the town has about 1,151 residents and eight operating school facilities with essentially full geographic access. The public standard requires about $1,907/day; the policy slider cannot exceed $500/day. Observed public coverage is consequently about 26%, despite sufficient facilities, treasury reserves and purchased additional sites. Health has the same fixed $500 ceiling. This is a legacy small-town policy bound, not a missing school-building bonus. A public-budget ceiling that scales to a larger borough is an integration/balance decision; this urban branch does not silently change shared fiscal rules. Any increase must retain actual staffing, spending and skill/access constraints rather than granting universal coverage.

## Completed six-year results

| Seed | Strategy | Residents | Centres / small shops | Observed moves | Farm relocations | Deeds |
|---|---|---:|---:|---:|---:|---:|
| 42 | market | 1159 | 4 / 17 | 12 | 6 | 0 |
| 42 | planned | 1151 | 4 / 17 | 18 | 7 | 6 |
| 101 | market | 1093 | 4 / 16 | 6 | 5 | 0 |
| 101 | planned | 1123 | 4 / 16 | 10 | 5 | 6 |
| 909 | market | 1155 | 4 / 19 | 20 | 6 | 0 |
| 909 | planned | 1136 | 3 / 18 | 10 | 6 | 6 |

These six runs cover 36 simulated town-years. All 23 centres have staffed quarterly observations after construction; 59 centre-quarter observations still have negative profit. Small shops grow from ten to 16–19 open stores; one small-shop closure is retained. Across the paired runs there are 35 observed farm relocations, 76 observed household moves and 29 district-character changes. The smallest observed gap between different characters is 180 days, above the 90-day rule. Sampled farm acreage never falls at relocation. All measured cash deviations remain below $0.00002 and every quarter passes the game's cash/commodity/identity checks. Separate stronger housing checks verify actual addresses, unit capacities and rosters on all six final archives plus 60 further days.

Each intervention buys six actual adjoining deeds for $210,684, including one beyond the original five, and pays $13,800–$15,000 for real street tiles. Annexed land hosts staffed businesses/farm operations; it does **not** automatically produce residential suburbs. Most residential charter targets remain unfinished without resident households. This is a consequence to show the mayor, not a free population bonus.

The initially lower-income cohorts' median liquid reserves rise from roughly $1,186–$1,196/person to $1,725–$2,495/person by year six. Higher-income cohorts reach roughly $8,123–$9,819/person. Actual wages, rent receipts, dividends, pensions and aid explain the ledger differences; labels confer no benefit or penalty. Household size, ageing and new household formation also change per-person income, so these are not estimates of individual wage growth. Wealth inequality persists. The intervention improves observed learning/care but lower-income savings are lower than the comparison in two of three seeds. Seed 101 experiences substantial early hardship before recovery; seed 909's intervention also has temporary hardship in years four/five. These negative outcomes are retained.

Three default-settlement runs add 18 simulated town-years on the final source. Their year-six populations are 297, 266 and 268, with five to seven small stores and no centres: none reaches the 320-resident prerequisite. Repeated invitations correctly do not inject a successful development. This slow natural unlock is relevant to pacing: active projects, deliberate housing/job investment and the authored larger-city start matter; passive stability alone is not evidence of fun.

### Provenance

The regional six-year trace source is `e8c372fda91343403d082476de3a51aa26016bc4c1aec046d8fd2661e8c41245`. The final source is `d8333d0086b3dd8e3b6da23374fe1bba24469e98b6ffb250a6675e0389f8b27f`; its only subsequent engine difference from that trace is the narrow employment-charter exclusion for apartments/towers. The actual-control boundary test covers that final permission fix. Final-code continuation checks load all six natural checkpoints without retroactively confiscating existing rights. The default-settlement six-year runs use the final source. Before/after three-year labour traces and the exact matched natural-archive next-day replay are retained separately with their own hashes. No result is presented as coming from a different source revision.

Full compressed observations, summaries and six reproducible regional checkpoints are under `docs/previews/urban8/trajectories/`; `manifest.json` records artifact hashes. Targeted source-hashed reports are `retail-labour-viability.json`, `reservation-lifecycle.json`, `trajectory-checkpoints.json`, and the normal core/urban suites. No APK, deployment, main-branch merge or Android performance claim is included.
