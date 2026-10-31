# Candidate tenancy normalization proposal — coordination pending

No production validator/tenancy normalization edits have been made. This proposal
is for agreement with the balance worker through the parent before shared edits.
Intended production overlap: a pure helper adjacent to `validateArchiveRecords`
and its pre-validation call in `src/90-archive-panels.js`. New-town marker creation
and live registration/pruning must be coordinated with the balance worker.

## Authoritative inputs and API

- `residentHouseholdsAt(buildingOrId, town=G)` returns households with nonempty
  `people` and `home === building.id`. Neither `building.hh` nor `building.units`
  establishes vacancy; those are synchronized indexes of the actual households.
- `housingUnitCapacity(building)` returns 1/4/9 for home/apartment/tower. A legacy
  exception never increases this value or admits an extra household.
- `normalizeLegacyTenancies(candidate)` operates only on the cloned import
  candidate and returns a deterministic migration report. No money, goods, person,
  household, property title, loan, building ID, footprint or home assignment changes.

Proposed archive fields: `tenancyVersion: 1` plus a sorted, unique
`building.legacySharedTenants` roster of grandfathered household IDs only where
actual household count exceeds physical capacity. These are additive migration
metadata, not a new housing asset or a security/anti-cheat guarantee.

## Existing duplicate cottage occupants

An archive lacking the version marker predates the common vacancy guard. Build
actual occupancy once, in O(buildings + households). For each occupied dwelling
over capacity, preserve all existing families and wallets, record their exact
sorted IDs as its grandfathered shared-tenancy roster, and synchronize `hh`/`units`
without deleting or relocating anyone. Mark the archive's tenancy version and
report the affected buildings/households explicitly after successful restore.

On version-1 archives, new over-capacity groups without an existing matching roster
are rejected atomically. An exception can shrink, never gain household IDs. Live
registration/departure prunes departed IDs; remove the exception when occupancy
returns within physical capacity. Occupancy-aware vacancy readers refuse further
admission. Existing titles, deposits, loans and estate records remain intact.

The committed authentic v6 distressed fixture has six such cottages, each with two
living households. A blanket capacity rejection would break that supported input.
The proposed grandfathering preserves its physical and financial history while
stopping further refill. It should be visible as an inherited overcrowding issue,
not displayed as six newly created apartments or silently called repaired housing.

## Municipal reserve already occupied by the old bug

The exact day-183 cold-reload failure on the fixed-cache source is a different
legacy inconsistency: home 109 is municipal, `relocationReserve: true`, but household
68/person 84 moved into it via normal `householdFormation` on day 180. All three
checksum-valid store copies are rejected only by `validateUrbanRehousing`.

For an archive lacking the tenancy marker, if a municipal home has valid municipal
title/owner and actual occupants, retire its obsolete reservation flag, preserve
all occupants and municipal ownership, and report that it is now an occupied
municipal dwelling rather than a vacant replacement reserve. Do not change rent,
fees, wallets, people, buildings, titles or location. Malformed/nonmunicipal reserve
ownership still rejects. For version-1 archives, a newly occupied reserved home is
an error; the live vacancy fix must prevent it.

Urban commit `98a6f99618e27e7d30306a7f4c890ac019ef004a` already contains the prevention
filter in `householdFormation`, ordinary immigration and housing readers. This
proposal does not duplicate that implementation or weaken its reserve validator.

## Evidence and required regression

`docs/previews/save8/cold-rejection/` contains the exact app outcome, all candidate
metadata and failed validator. The welcome screen stays open with "No valid town
could be recovered"; there is no pending dialog. Increasing the test timeout would
not recover this state.

Regressions should cover both authentic historical fixtures, exact day-183 archive,
unchanged household/person/home/asset records and total money, candidate independence,
repeat normalization idempotence, version-1 unapproved duplicate rejection, forbidden
roster growth, departure pruning, bad municipal ownership rejection and subsequent
canonical continuation. A failed import must leave the live game, RNG and timeline
unchanged. Final acceptance should use the lead's combined immutable checkpoint.
