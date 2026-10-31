# Concrete civic projects: second player-experience phase

Sequential change after `ffc8f50d64f28d093c310021a1f9a6b7552ccd58` on `codex/8-player-experience`. Source SHA-256: `dbe96511846a1ae4eda713103979df519dea9ff278c4a155a245699d24f01864`.

## What changed after playing the opening

The first phase made the town easier to understand, but ordinary automated deliveries could satisfy its opening direction without an intentional investment. Directions alone still risked becoming an observation checklist. Expansion also required jumping between land, charter, map and enterprise menus without a concrete connection plan. A school promise could become “raise a number, then wait” without pricing the recurring commitment.

The new project cabinet provides three authored, condition-driven commitments. Their counterparties, geography, prices and outcomes are real. They can run together and compete for the same cash, workers and reachable sites. There is no completion subsidy, manufactured shortage, arbitrary real-time countdown or recurring interruption.

**The fresh-food circuit** names an actual shop and offers two genuinely different routes. A paid import bridge commissions 180 food from enterprise working cash, records its exact shipment IDs, follows arrivals and requires actual town food supply and an operating staffed shop. Local production spends $3,600 municipal site capital plus the existing normal startup/permit settlement, commissions a legally vacant roadside bakery and requires its recorded production, sales and accumulated operating result to demonstrate viability. It cannot complete just because unrelated automated trucks arrive. Restricting imports blocks the bridge; a reviewed replan can take the local route without undoing earlier assets or cargo.

**A gateway worth building** chooses an actual outer district and binding charter. The prospectus previews its land, water, woodland, deed and interior-road estimate. It prevents a cargo-waterfront project on the inland lake or other non-river tract. A deterministic multi-source survey finds a shortest legal corridor from the main road component into the district interior, preserving buildings and reservations. A reviewed purchase uses the existing road construction function for each tile. Pilot enterprise surveys choose legal connected sites and explain available labour, initial capital and operating risks. Existing pilots get inspection links instead of duplicate factory recommendations. Establishment remains the existing real district programme: connected activity, appropriate businesses/residents/services and 30 qualifying days. Its completed record can lead into another unestablished adjoining district.

**The school-to-work promise** identifies a household with poor usable teaching access. It offers operating the existing network or investigating a campus when physical access is inadequate. The operating preview states a daily allocation, additional authorization and a 120-day comparison, then adds education to the existing policy draft for explicit enactment. Completion requires actual target-household coverage, an actual additional adult training completion and a 20-day authorized spending reserve. Schools do not become staffed or funded because their project is adopted.

Completed projects retain a dated proof statement. Later conditions can deteriorate without rewriting the historical result. Withdrawals and replans close records while retaining purchased deeds, normal charter rules, policy commitments, commissioned assets and cargo. Passed opportunities can be restored explicitly. The cabinet remains quiet until opened from Town Hall or Agenda.

## Integration

New source: `src/98-project-opportunities.js`, sorted after `98-player-experience.js`. New styles append to `assets/mayor8.css`; the existing stylesheet link from phase one is sufficient.

Small shared hooks relative to phase one:

- `src/50-clock.js`: call `civicProjectsDay()` after `mayorJourneyDay()` in the final daily snapshot.
- `src/90-archive-panels.js`: validate `validateCivicProjects(data)` before adopting a parsed town.
- `src/80-civic.js`: recognize `CIVIC PROJECT` in `directTransactionDialog()`.
- Reassemble `assets/game.js` after integration.

The new module wraps the existing mayor desk/Agenda, council dismissal, transient reset, map construction notification and regional freight function. It does not edit renderer modules, construction algorithms, private-service economics, regional settlement algorithms or district rules.

The freight wrapper observes tracked shipments before and after the existing `regionalFreightDay()`. A removed tracked shipment represents an arrival under the current existing settlement contract; interrupted or illiquid shipments remain pending. This records UI evidence only. It is necessary because the regional recent-deliveries list retains only 36 rows and may roll over in a busy settlement. **If the lead later adds cancelled/lost cargo removal to `regionalFreightDay()`, replace this observation with an explicit successful-delivery notification rather than classifying every removal as delivered.** `civicProjectRecordArrival(order)` is the clean notification entry point; it is idempotent for recorded order IDs. No money or inventory is changed by the observer.

All purchases delegate to existing safe functions:

- `dispatchRegional()` for paid food orders;
- `purchaseParcel()` through the existing reviewed deed flow;
- `chooseDistrictFocus()` for actual land-use restrictions and revision costs;
- `construct()` and `flushRoadBatch()` for surveyed buildings and roads;
- existing staged policy controls and `enactPolicyPackage()` for teaching authorization.

Survey reviews hold a town/project identity and revalidate sites, current corridor, funds and import policy before committing. The cabinet returns to the relevant project after a deed or charter decision. Keyboard Tab stays in the topmost council dialog, including native survey selectors; Escape/Android Back remove the survey. Cancelling preserves expanded project reconsideration details. Loading another town clears survey markup and pending transient controls. A player may cancel a surveyed build or construct it by tapping the actual map; an exact-site construction observer attaches the resulting building to its project without duplicating the purchase.

Additive save field `G.civicProjects`, version 1:

```
{version:1, serial, lastDay, active:{food?,district?,skills?}, history:[], declined:[]}
project = {id,kind,branch,target,started,lastDay,status,
 orders:shipmentIds,arrived,firm:firmId|null,building:buildingId|null,
 output,sales,net,trainingBaseline,completed:day|null,proof:string|null}
```

Historical records additionally contain `closed`. Active records are limited to the three authored kinds, history to nine, tracked orders to 24. Validation checks identities, references, dates, counters, branch compatibility, deduplicated IDs and proof shape before changing the active town. Absent fields remain a valid legacy archive. Rendering never initializes project state or settles a transaction.

Private-service integration continues to use the shared `localCivicCoverage('school', householdId)` and `programmeMetrics()`. The module links to the lead’s Services screen for staffing and private-provider comparison; it does not invent a second provider model. No separate provider mutation API is required by this slice. If the combined game needs private commissioning directly inside a campus project, add a reviewed Services entry point and have it return the commissioned building ID; retain the provider’s existing ownership, staffing and payment functions.

## Evidence

New tests:

- `test_civic_projects.py`: actual controls for reviewed/cancelled 180-unit paid food purchase, repeat guard, delivery certificate, district adoption and geography restrictions, Android Back cleanup, $37,368 County Ridge deed, charter, 18 paid road tiles ($2,700), commissioned $9,800 factory site with the normal permit receipt, nonduplicating pilot links, explicit teaching draft/enactment, 15-day exact replay, withdrawal, passed-opportunity restoration, corrupt/legacy archives and portrait layout.
- `test_civic_project_recovery.py`: an actual import restriction blocks the bridge, reviewed replanning does not refund assets, the local bakery earns a real production/sales/cost-recovery certificate, a funded network completes actual adult training and target access, cash is conserved, proof survives later policy/time and restore clears an open survey.
- `test_civic_project_freight.py`: controlled stress fixture with 43 actual paid deliveries. Its project delivery drops out of the bounded recent log but is recorded exactly once, without cash/goods drift.

The real local-production run completed its evidence on day 22 under restricted imports. The school promise adopted on day 61 completed on day 203 after actual adult terms and usable access. These are deterministic simulated dates from seed 42, not promises for every town or real-time play-duration claims. Receipts and landscape/portrait screenshots are in `reports/civic-projects/`.

Existing mayor journey, three direction rule fixtures, scenario programme, regional freight/contract, district-choice and seven mobile-layout suites also pass. No APK or device certification was attempted.

Remaining limits: the opening/default economy still tends to recover toward very high employment and low hardship over a year without much intervention. The new projects create deliberate uses for capital and specific commitments; they do not prove a challenging multi-hour campaign. Long-run difficulty, additional market disruptions and private-provider balance remain integration work. The automated journey verifies a real deed, charter, road and factory, but does not certify every waterfront/mixed-neighbourhood site or claim an established district without its normal qualifying activity.
