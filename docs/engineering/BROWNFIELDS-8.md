# Brownfield renewal slice

Base: integrated `b4f6fe4d0a4d8a78ddfeed59df118560d68646af`. This branch adds closed-industrial renewal only; it does not move the migration, private-service, logistics or rendering systems.

## Player loop and accounting

Public Works now lists closed factories, quarries and sawmills whose original premises still exist. An assessment costs $300. The resulting report preserves the former enterprise name, type, coordinates, footprint, recorded age at closure and former job capacity. Acquisition separately uses `urbanClearanceQuote` / `urbanClearance`: existing property/crop compensation, occupied-household replacement requirements, creditor/liquidation handling, transit guards and paid cargo/contract restrictions still apply. Existing clearance reviews cannot bypass assessment for a closed industrial premise. Reopened firms cannot be acquired through a stale closed-site proposal. Acquisition confirmation checks the reviewed price again.

After compensation the municipality holds a reserved footprint. The full ground-work contract is paid from treasury to the external region before work starts. It costs $1,500 plus $750/tile plus $8 per recorded enterprise-age day, with the age allowance capped at $3,600. Duration is 20 workdays plus one day per 30 recorded-age days, capped at 60 workdays. Day-by-day work requires the existing street connection and open regional trade; there is no repeated same-day credit, unpaid progress or passive completion by renderer time. Existing industry nearby still affects residential suitability and rents through the original urban model.

When ready, the mayor can separately review and fund a municipal rental home, local grocer or public park. Each follows ordinary construction, planning, road, household affordability, private capital and staffing rules. Housing can remain vacant; a shop needs real customers and workers; a park provides the existing amenity rather than free revenue. The before/after record survives as `newBuilding`, `newKind`, dates and the former site identity. Retiring the original premises also retires the option of reopening that enterprise at this location. No occupants, title compensation, inventories or shipments are erased by a shortcut.

Cancelling a review changes no economic balances or authoritative site/property state. Paid assessments and ground contracts are non-refundable. Insufficient treasury cash blocks each paid step. A reserve cannot be privately built over, paved or used for an early home. Current planning rules remain authoritative at reuse; a civic/employment/agricultural plan may require the mayor's normal neighbourhood-planning intervention.

## Environmental model boundary

This is a declared industrial-ground preparation model, not a chemical exposure simulation. No greenfield, home, farm or arbitrary poor district is labelled contaminated. Eligibility comes from a real closed industrial enterprise and its surviving premises. The age proxy uses enterprise age less time since recorded closure; enterprise age can include nonproductive periods, so it is not claimed as measured emissions or exact operating days. The base contract represents site preparation even for a newly closed industrial site. Existing saves do not contain detailed chemical/process histories and none are fabricated retroactively.

Existing urban industry proximity, amenity, rent and siting effects are reused. Ground work grants no direct health bonus and does not erase pollution from neighbouring active industry. This finite slice covers closed premises; there is no new industrial relocation simulator. A controlled closure regression is explicitly distinguished from naturally occurring multi-year turnover.

## API and persistence

`30-brownfields.js` exposes `brownfieldQuote(buildingId)`, `brownfieldAssess(id)`, `brownfieldAcquire(id, reviewedTotal)`, `brownfieldFund(id)`, `brownfieldReuse(id, kind)`, `brownfieldDay()` and pure `brownfieldDescriptor(site)`.

Graphics can consume descriptors: `{id,x,y,footprint,formerName,formerKind,formerJobs,industrialAgeDays,status,remaining,newBuilding}`. States are `assessed`, `acquired`, `remediating`, `ready`, `reused`. No renderer change is included. Placement checks scan only these explicit records when considering development; daily progress scans records once per simulation tick. There is no per-frame environmental map or person/building sweep.

Optional `G.brownfields` is archived by existing `archivePayload()`. Missing legacy state remains valid and creates no records. `validateBrownfields` runs before save adoption and rejects duplicate IDs, malformed/overlapping reserves, occupied reserved tiles, invalid costs/timing/statuses, impossible dates, invalid new-use descriptors and bad references to assessed premises. New buildings receive `brownfieldOrigin` as a place-history descriptor. Acquired land follows the existing municipal assembly authority and ordinary reuse title conventions; no duplicate land-ownership economy is introduced. Legacy industrial premises without an explicit private title use the existing regional recipient fallback; employer ownership is not silently converted into a new real-estate claim. The acceptance fixture verifies this fallback receives both its compensation and contractor receipts, while the existing urban regressions cover explicit private-title compensation.

UI is isolated in `98zzzzzzz-brownfield-ui.js`, wrapping the existing Works panel. Actual controls use `data-brownfield-action=assess|acquire|fund|home|grocer|park` and `data-brownfield-id`. Dialog type `BROWNFIELD RENEWAL` uses the existing direct-transaction path, preventing a second generic council debit. Existing urban property-guard registration and district-placement hooks are reused. Only tick/archive validation need shared-file hooks. No subagents were used.

## Acceptance evidence

`tests/test_brownfield_renewal.py` uses the integrated regional seed 42 and invokes the existing enterprise liquidation function to create an explicitly controlled quarry closure. It grants no cash, residents, goods or successful customers. It then uses actual review buttons for assessment, cancellation, acquisition, funding and all three reuse alternatives on the same ready-state replay.

The quarry's owner is compensated through a $44,750 assembly transaction; assessment is $300, ground works $2,250 over 20 connected workdays, and the park costs an additional $550. Two closed-trade days make no progress. The site finishes on day 23. Cash conservation error over the normal intervening simulation is below $0.000001; town validation and archive round-trips pass. Early reuse, unfunded acquisition and malformed-cost archive adoption fail safely. Legacy state without brownfield records loads. Housing, commerce and park alternatives each pass their ordinary funding/permission paths and conserve total cash. This demonstrates reachable controls and accounting, not long-run retail success or universal service coverage.

Source-bound results and inspected screenshot are in `docs/previews/brownfields/`; the manifest records source and evidence hashes. Run with:

```
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_brownfield_renewal.py
```

The follow-up integration acceptance should exercise naturally closed/reopened industry over longer funded city growth, migration and rehousing, and have the graphics worker add reserved/working/ready treatments using the descriptor. No APK, deployment, main-branch merge or rendering-performance claim is included.
