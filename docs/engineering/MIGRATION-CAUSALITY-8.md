# Funded migration and authoritative tenancies

Implementation is based on integrated `09e1c3b2142dd96e722003eb55a76a70279ae043`, retaining scalable service authorizations, urban reserve exclusions and the save specialist's `f40bda316` daily-cache fix. It changes live formation/migration, new municipal homes and a collapsed Community disclosure. It does not edit `90-archive-panels.js`, archive normalization, road routing, freight settlement, private-provider settlement or Android code. Regenerate the integrated bundle after applying; do not replace a newer integration bundle wholesale.

## Behaviour

New household admission requires a real unreserved dwelling slot, a connected road gateway, funded reachable positions remaining after local jobseekers, and a household budget that covers its living costs. Firms must have the published positions and cash for the current payroll; an unfunded advert does not count. Qualifications use the real private-school/fire rules. Accepted workers take those actual positions instead of being sent to a different unfunded employer by the generic allocator.

The budget includes the selected reachable grocer's price and shopping trip, road/metro/bus commuting, current seasonal utilities, rent, retained property taxes, scheduled loan payments and existing private fees. Prospective independent-school places require working staff, spare capacity and an affordable fee; that fee enters essentials. No voucher allocation is promised or spent by an assessment. Region-funded startup cash is transferred once, never created. New ordinary council-built homes remain municipal rental property rather than gifting a financed title and forcing a household to appear.

A joining family member gets the same work, address and budget review at the existing invitation cadence. Empty estates cannot receive a newcomer merely because an unrelated employer somewhere has an opening. Local formation also refuses occupied/reserved cottages and requires the young worker to reach the new address; its cash is divided from the existing family, not duplicated.

Emigration considers persistent household distress, a recurring shortfall, real local job alternatives and a better outside budget reference. The ninety-day reserve horizon reuses the existing credit model's essentials buffer. Spendable savings follow `withdrawal()` constraints: bank vault cash plus actually redeemable regional securities, sharing the finite regional cash pool across banks. Identical available wealth receives the same departure decision whether banked or in a wallet. Locked claims do not pretend to be cash. Departing people leave employer rosters; wallets leave through the regional account, while deposits, loans, titles and household IDs remain recorded. Debts/property obligations are also carried into the outside comparison, not forgiven by moving.

Outside prices come from the existing named markets. Outside income and rent are explicitly a founding-policy **reference**, not a fabricated foreign job offer or complete foreign-city simulation. Relative disposable income and forecast care/learning access affect pull. The former town-wide 88% employment immigration barrier is replaced by the address-specific assessment; a workable local opportunity can attract someone despite unrelated unemployment elsewhere. There is no new population limit; the existing engine ceiling remains.

## Tenancy agreement with the save specialist

The fixed-roster proposal `7b310464fe95d24513db165a8eb310f770fa084d` is accepted:

- Newly founded towns carry `tenancyVersion: 1`.
- `building.legacySharedTenants` is a sorted, fixed grandfathered roster; it never increases physical capacity or grants another arrival slot.
- Actual nonempty households with `home === building.id` are authoritative. `hh`/`units` are indexes.
- Live release clears only an empty household's tenancy. The household, balances, claims and titles survive. This also runs after death, not just emigration.
- Live pruning removes departed roster IDs and removes the exception once occupancy is within physical capacity. It never adds an ID.
- Existing shared cottages remain occupied and visible for a paid rehousing review. Nobody is silently deleted, moved or assigned a larger home.

The APIs are implemented in `src/44-migration.js`; the save specialist should reuse them rather than shadow them with duplicate function declarations:

| API | Contract |
|---|---|
| `residentHouseholdsAt(buildingOrId, town=G)` | Returns actual household **objects**; passing a cloned town does not consult live G. |
| `housingUnitCapacity(building)` | Returns 1/4/9 for home/apartment/tower, otherwise zero. |
| `migrationHousingStatus(building)` | Capacity, actual household IDs, vacancy, reserve/construction state, legacy roster and review flag. |
| `migrationRegisterTenancy(h,b)` | Synchronizes live tenancy and detaches only replaced empty references; no title acquisition or payment. |
| `migrationReleaseTenancy(h)` | Releases only an empty household's address and synchronizes the surviving primary tenant. |
| `pruneLegacySharedTenants(building,town=G)` | Removes departed IDs only; deletes the exception when occupancy is within capacity. |
| `migrationTenancyDay()` | Releases empty estate references and prunes existing exception rosters after urban movement. |

The save specialist owns pure candidate normalization, grandfathering existing imported groups, retiring an obsolete reserve on an already occupied municipal home, version-1 roster-growth rejection and atomic import validation. This branch neither invents an imported roster nor blanket-rejects supported old shared cottages. The authentic v6 fixture's six shared cottages load, retain every recorded balance/title/person, accept no extra household and continue for 120 days in the regression.

## Gameplay/diagnostic interface

`migrationAssessment(home, profiles, capital=2500, joining=null)` is a no-payment forecast. It returns `eligible`, `reasons`, `housing`, actual job `offers` (firm, wage, distance, fare and mode), `expectedNet`, `essentials`, itemized `budget`, `foodShop`, `surplus`, `outside`, `services`, and `pullProbability`. Profiles carry age, skill and health; inspection does not draw random profiles. The outside object marks `referenceOnly: true`. School quotes mark `forecastOnly: true` and include the private fee. Quotes do not reserve a route seat or future supplier stock.

`migrationEmigrationAssessment(h)` returns spendable/locked claims, a conservative recurring-income estimate, real local offers, essentials/debt, reserve runway, outside comparison, reasons and departure probability. Its prospective-offer fares are netted from income; they are not charged again to essentials. `migrationSpendable(h)` performs no withdrawal and reports `cash`, `claims`, `spendable`, `locked`, and redeemable securities.

`migrationDiagnostics()` supplies current inherited overcrowding and bounded recent decisions. `sessionCounts` separately tracks births, deaths, immigration and emigration from `observedSinceDay`; it is derived, not persisted, and resets after loading. The UI labels that boundary instead of inventing old census history. The existing annual-age shortcut remains; births are recorded at their source before any annual ageing.

Public-service attraction uses persisted paid roles, ready staffing contracts, facility access and available authorization. It does **not** read the ephemeral `serviceProvision` report, which loading clears. A regression caught a warm/cold forecast changing from 68% pull to 100%; all three seeded assessments now match exactly before and after save/load. First-day inherited service arrangements follow the existing civic staffing rule. These are capacity/funding forecasts, not claimed actual purchases.

## Acceptance and limits

Final tested game SHA-256: `7346c074abb8f107a59afc410c0563ab03b2f675c6baa908e04b1ce35e9b35b4`.

Source-bound evidence is in `docs/evidence/migration-causality8/`. The regression covers estate refill, death estates, equal available wealth, constrained bank redemption, unfunded/inaccessible jobs, household affordability, service effects, live outside-price effects, private learning fees/capacity, warm/cold quote equality, municipal ownership, fixed-roster pruning and authentic legacy preservation/continuation.

The final natural run covers seed 42 for 30 years and seeds 101/909 for three years each, after ordinary one-year founding periods. It reconciles population daily and records **zero** missing-home, unregistered-household or over-capacity-building days throughout. Seed 42 finishes with 472 residents, 100% employment and 2% hardship; its intervention identity is `175 + 239 births + 96 immigrants − 20 deaths − 18 emigrants = 472`. This is a retained outcome, not a target the implementation forces. Maximum cash drift is $0.0001362; commodity error is 2.81e-9 units. The earlier long phase runs are retained with their own hashes; an intermediate run whose immutable-source guard rejected a source update is explicitly excluded from final acceptance.

Core deterministic/render-independent replay, 120-day continuation, malformed-save atomicity, authentic migration, cargo/cash/goods gates, the save specialist's urban-cache regression, paid private-service flows, seven responsive layouts and the older-WebView API check pass on this final bundle. The isolated 2,000-resident host check advances 311 days in 8.04 seconds, with 19.1 ms draw P95 and 183.3 ms RAF P99; all existing UI/error/conservation gates pass. These are host measurements, not Android certification or a promise of 60 FPS.

Remaining work belongs to combined integration: apply the save specialist's agreed candidate normalization/validator, preserve current road/river/native changes, reassemble, and run the combined immutable acceptance. Forecasts remain stylized: no complete foreign labour/housing census, no guaranteed future payroll/seat/stock, and no automatic free rehousing. Existing service-operation coefficients, taxes, private production rates and civic rewards were not retuned. Changes are confined to disclosed migration choices and tenancy handling, rather than artificial fiscal penalties.
