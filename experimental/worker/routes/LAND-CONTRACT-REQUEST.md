# Land/renewal route integration checkpoint

Inspected exact base `0a14b9e88bb5b133fec78336b7742ce9879e3bd3`; production remains disabled. No central implementation edited. Registration contract is pending from worker owner: current adapter causal types, bridge paid queues and serializable root dispatch are closed hard-coded allowlists. REALTIME-CORE-CONTROLS.md defines behavior but not a route extension API. Do not invent a second dispatcher or root.

Required owner contract: module inclusion/registration hook on worker and main; finite DTO family name and request/epoch sequencing; authoritative review creation and one-use token ownership; paid-root execution hook; preview/view effects schema; complete-day queue and pending/duplicate handling; save-drain/commit semantics; cancellation/review invalidation and source-port responsibility. Existing workerPaidDispatch is the paid-scope/drain boundary; workerInScope must not be nested. No callback or G object crosses structured clone.

## Mapped original bodies

| Control family | Original entry/model body | Important integration condition |
| --- | --- | --- |
| parcel-buy | requestParcelPurchase / purchaseParcel | original land-purchase descriptor, current adjacency/price/treasury |
| regionalApproaches | regionalApproachPlan / buildRegionalApproaches | original reviewed corridor, no protected titles overwritten |
| district-focus paid revision | chooseDistrictFocus | initial free route already exists; revision30days/$1200 |
| district-admission | reviewDistrictAdmission | illustrative read-only forecast, no settlers/jobs/seats reserved |
| district-finish | reviewDistrictFinish / civicProjectReviewBuild / construct | current project ID/site-list signature; one site only |
| district-budget | existing policies navigation | view/focus only, not a budget purchase |
| civic-recharter | civicReviewRecharter | existing project identity and subsequent current charter quote |
| civic-watch-project | openCivicProjects('district') | view navigation only |
| urban-clear | reviewUrbanClearance / urban clearance model | owner/tenants/crops/workers/cargo and actual rehousing protected |
| urban-plan | urbanPlanChange | outer survey cost600/1800; current target/plan/day key;90day revision |
| public-place | original named-place review | original property/capital/dated baseline, no duplicate record |
| brownfield-action | brownfieldAssess/Acquire/Fund/Reuse/Withdraw | current target/site-stage signature; outer charge inside root |
| urban-farm-renew | reviewUrbanFarmRenewal / urbanFarmRenewal | reviewKey plus titles/cargo/destination/regional capital |
| urban-rehousing | urbanRehousingQuote / commissionUrbanRehousing | reserved dwelling/project, no invented household |
| road-remove-tool | local map tool -> reviewRoadRemoval / retireRoadTile | map mode itself free; authoritative road impact/key before purchase |
| bridge-repair | reviewBridgeRepair / repairRoadBridge | condition/day/treasury key; cost>0 |
| bridge-remove | reviewBridgeRemoval / decommissionBridge | passenger/freight/rehousing protections, current salvage/key |

Road_bridge construction is also currently refused by main construct wrapper. It is adjacent scope, not counted as one of the three requested removal/repair identifiers: owner must confirm who routes bank survey/commitRoadBridge. Original bridge review already has road-works descriptor.

## Test gates prepared

Use original actual controls on funded published regional-42-planned fixture, with eligible fixture variants only where original prerequisites require them. Capture complete G/RNG before review, cancellation, no-op/refusal and authorization. Compare successful actions to exact original-source UI oracle, including history, compensation, claims and IDs. Stale quote after actual day/funds/target change must refuse without charging or consuming RNG; duplicate token must not replay. Retain pending UI until worker ACK, no save effect before commit; original saver readback precedes durable ACK. Do not claim direct model tests equal actual UI integration. Navigation/diagnostic routes are not paid transactions. Existing baseline runner856f944 provides land acquisition/initial charter/urban-plan/farm-prerequisite actual-control paths; it does not certify eligible farm settlement, brownfield lifecycle or bridges.

Source port: current public01eeda3 has later model/native fixes than worker669 base. Preserve original algorithms and run exact oracles against the source actually composed; worker owner retains central port ownership.
