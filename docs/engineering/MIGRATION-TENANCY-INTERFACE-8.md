# Live migration / archive coordination

Agreement with save proposal `7b310464fe95d24513db165a8eb310f770fa084d`: `tenancyVersion: 1` marks newly founded towns, and imported legacy overcapacity uses the exact fixed `building.legacySharedTenants` roster. Household `home` plus nonempty `people` is authoritative. Capacity remains 1/4/9; a grandfathered roster never creates arrival capacity.

This branch owns live APIs in `44-migration.js`:

- `residentHouseholdsAt(buildingOrId, town=G)` returns the actual household objects. It also accepts a cloned archive candidate without consulting live G when town is supplied.
- `housingUnitCapacity(building)` returns 1/4/9 or zero.
- `migrationHousingStatus(building)` returns physical capacity, actual IDs, vacancy, reserve/construction state, legacy roster and review requirement.
- `migrationRegisterTenancy(h,b)` registers an existing funded household and clears only stale empty tenancy references. It does not acquire a title or transfer anyone's balances.
- `migrationReleaseTenancy(h)` releases only an empty household's old tenancy, retaining the household, titles, bank claims and loans.
- `pruneLegacySharedTenants(building,town=G)` only removes departed IDs; it never adds a roster member. It removes the exception once physical occupancy is within capacity. `migrationTenancyDay()` applies this after ordinary urban movement each day.

`20-world.js` creates the marker for new towns. No migration fields or exception rosters are invented for the running town by an import observer. The save specialist owns `normalizeLegacyTenancies(candidate)`, archive validation, municipal stale-reserve retirement and imported-roster rejection. This branch deliberately does not edit `90-archive-panels.js` or reject legacy shared cottages. Existing overcapacity remains visible for paid rehousing review; no resident is discarded, moved or assigned an extra apartment automatically.

The branch is rebased on integrated checkpoint `09e1c3b2142dd96e722003eb55a76a70279ae043`, retaining the upstream cache fix `f40bda316b1f06cb523ce588e57359d5bb81c27f` and scalable service authorizations. Initial development used a local cache cherry-pick; it is no longer a separate integration dependency. Apply only the migration commits after the current integrated checkpoint. Urban reserve-filter prevention `98a6f996` may overlap the `45-public-services.js` filters: preserve its replacement-home exclusion alongside the authoritative vacancy guard.
