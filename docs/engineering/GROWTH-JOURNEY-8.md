# Expansion journey and vacant-land planning

Base: integrated `6e8665e3cdee520148f44947e49cdc8e7ddae4c6`. Scope is existing urban/planning mechanics and feedback; economics, migration, services, rendering assets and territorial capacity are unchanged.

## Reproduced player gap and fix

The only existing neighbourhood-plan controls were in a building inspector. A newly purchased vacant tract therefore could not be protected for agriculture or designated for future residential/civic use before something was built there. This particularly undermined later purchases, where a mayor should plan the relationship between farms, homes, work and services before construction.

Public Works → Living neighbourhoods now offers **Plan vacant or occupied land on the map**. Tap owned land, including vacant outer land, to review its existing 8×8 planning block. The review shows:

- Exact block bounds and owned tile count; existing neighbourhood rule and overlapping parcel charter. Both permission layers remain authoritative.
- Existing residents, housing buildings, job capacity, productive crop tiles and distinct farm enterprises.
- Current relative income band, after-tax income per resident, rent burden and measured local care/learning. An empty block explicitly has no resident service/income measurement.
- The actual survey charge, the 90-day revision restriction, $1,800 revision price and non-refundable nature of the planning purchase.
- Existing farms, homes, workers, tenants and titles are retained. A permission change does not clear fields, displace people, grant service coverage or produce construction. Actual replacement still requires separate compensated assembly and capital.

Some global 8×8 blocks cross deed boundaries, particularly the 22-tile-wide earlier tracts. The review explicitly warns that the same block rule also applies to future-acquired portions; it grants no development rights over unowned land. No new parcel-only zoning semantics are silently introduced. Ordinary parcel charters, agricultural restrictions, brownfield reservations and transit rights remain enforced by existing placement rules.

The mobile dialog starts at its title instead of automatically focusing and scrolling to the first paid choice. Players see scope and rights before the action. Income review refreshes the derived urban snapshot on demand, avoiding an early-tick cached income label. It does not alter authoritative income or the global spatial-cache policy, and performs no per-frame scan.

## Interfaces

New module: `98zzzzzzzz-growth-planning.js`.

- `urbanLandPlanSurvey(x,y)` validates an owned integer-coordinate target and returns the current block, parcel/charter, cost/cooldown, population/property/crop, income and service context. Derived urban state is refreshed for the review.
- `reviewUrbanLandPlan(x,y)` uses the existing `URBAN PLANNING` direct-transaction dialog and `urbanPlanChange` accounting/90-day guard. It rechecks the planning record before applying a choice.
- `data-urban-land-plan` activates the map tool; `buildMode='urban_plan'` reviews a block instead of constructing anything. Its placement-preview exception only applies to that UI mode. All real building kinds retain the original `canPlace` checks.

No new saved state or schema is introduced. Existing zones, deeds and titles round-trip unchanged. Renderer, migration, economics, payroll and logistics source files are untouched. The region survey test now validates the actual 21-parcel atlas and previews every deed; it previously failed because it still hard-coded five parcels.

## Actual-control acceptance

`test_growth_land_planning.py` starts regional seed 42, advances 180 ordinary days, then purchases six adjoining deeds using real controls and existing funds. The sixth is `belt-78-2`, beyond the original five. Total deed outlay is $210,684. No agents, stock or money are injected.

The mayor cancels a vacant outer-block review without payment, then records agricultural protection there for exactly $600 despite there being no building to inspect. On an occupied agricultural block with **14 productive crop tiles**, a residential permission change preserves the complete land-use/title arrays, every person's household/job identity, household addresses, firm cash, stocks and closure states immediately across the decision. Immediate revision presents no paid action and spends nothing. After 90 ordinary days, an actual revision costs exactly $1,800. The test also verifies the cross-deed warning, save restore, total-cash conservation, and a 390px mobile review with heading focus and no horizontal overflow.

A populated block's review reports 52 residents, 14 housing buildings and 25 job capacity, with observed middle income around $23.02 after tax per resident/day, 19.5% rent burden, 43.1% local care and 29.9% learning. Its quoted income is checked directly against current household accounts. These are observations, not new bonuses or permanent wealth classes.

## Connected three-year journey and negative results

`tools/audit_growth_journey.py` reuses the existing urban trajectory harness with a bounded six-purchase cadence over three years. The same regional seed is played through ordinary time, actual deed/charter dialogs, paid road placement, retail invitations and local service construction/budget decisions. It chooses first-affordable normal council letters. It does not force successful development or replace failed invitations with fabricated outcomes. Final source hash is frozen and checked by the runner.

The journey acquires East Meadow, County Ridge, Lower River Reach, Orchard Downs, High Common and Eastern Heights (`belt-78-2`). It purchases 105 road tiles ($15,750). Population reaches 886; final treasury after the last paid actions is approximately $615,843, without new debt/resource injections. Three farms relocate through the existing paid urban-renewal process, commissioning four dwellings each. Productive fields rise from 35 at the first quarterly sample to 80 at the end; no plan permission itself deletes them.

Important limits are retained:

- Only three acquired tracts have a staffed firm at the final sample. None has resident households. Connected empty land is not a functioning suburb or an automatic migration attraction.
- Public school provision is 28.6% and care 58.7%. Capital purchases and modest authorizations did not ensure adequate recurring provision. Empty-tract coverage has no resident denominator; the new planning review makes that distinction explicit.
- The final settled income view has 25 middle-income and three higher-income blocks, with no lower-income block. Earlier quarterly cached views mostly reported middle income. This run does not demonstrate a poor-neighbourhood trajectory, and no class labels are manufactured to fill that gap. Global overlay cache behavior remains outside this scoped review fix.
- Retail invitations fail their actual confidence/recent-competition conditions. Two centres arise through normal economic investment; no successful invitation or private profit is granted by the test.
- All six district programmes remain incomplete where their actual resident/staff/service criteria are not met. The runner demonstrates repeated annexation and tradeoffs, not successful completion of every tract.

The three-year journey and the targeted new-tool controls test are complementary acceptances. The journey does not claim that the newly available planning tool caused its population growth. Persistent growth beyond the original core still requires real work, housing admission, access, service funding and mayoral investment through the existing connected systems.

## Reproduction and evidence

```
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_growth_land_planning.py
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter TOWNLEDGER_URBAN_SEEDS=42 TOWNLEDGER_URBAN_YEARS=3 TOWNLEDGER_URBAN_ARMS=planned TOWNLEDGER_URBAN_RUN=growth-journey-verified python tools/audit_growth_journey.py
```

Hashed results, compressed journey trace/final archive and inspected desktop/mobile screenshots are in `docs/previews/growth-journey/`. Relevant regressions cover planning boundaries, council review workflows and the 21-parcel region survey. No performance, new graphics, deployment or APK claim is made.
