# Agreed legacy tenancy import normalization

Dependency: `d697af218925ba47a970dd3f67406aa05de90fb9` on migration-ready. This
commit changes only the archive candidate path, regression and evidence. It does
not duplicate the migration worker's live helpers. Reassemble the lead's combined
bundle; the dependency's generated bundle is intentionally not shipped here.

`normalizeArchiveTenancies` runs after structural/member checks and before domain
validators on hydration's independent cloned candidate. It reuses
`residentHouseholdsAt(building,data)`, `housingUnitCapacity` and
`pruneLegacySharedTenants(building,data)`. Actual household objects/home references
are authoritative; hh/units are synchronized indexes.

Archives without tenancyVersion receive version 1 and sorted fixed grandfathered
rosters for their existing over-capacity dwellings. Physical capacity remains
1/4/9. All people, household IDs/home assignments, wallets, deposits, loans,
enterprise records, buildings and titles survive. A valid occupied municipal home
with an obsolete reservation becomes an occupied municipal home by retiring that
flag; ownership and all occupants remain. A bounded structured tenancyMigration
receipt and one visible ordinary town-history entry disclose these legacy changes.
Repeated normalization is idempotent. No family is erased, moved or gifted property.

Version-1 archives reject unlisted over-capacity occupants, unsupported version
markers, malformed/unsorted/duplicate roster IDs, and newly occupied reservations.
Existing rosters are pruned only through the agreed helper. Valid departed IDs
cannot become additional capacity. Invalid ownership of municipal reserves still
rejects. Failure remains atomic because no live G/cache/RNG/timeline is touched
before the normal adoption point.

Tests pass against assembled SHA-256
`f7eeae418e2f8cc14bdfce59fffe06ac35c20b904ef30d43018834e535f38e9d`:

- Authentic v6 distressed fixture: all six shared cottages, every identity and
  financial/title record preserved; migration idempotence and 120-day continuation.
- Current-version unauthorized occupants, malformed roster/version and occupied
  reserve imports rejected with unchanged caller, live archive and RNG.
- Grandfathered roster cannot gain an unrelated occupant; departure prunes it.
- Exact previously failing day-183 archive restores with household 68/person 84
  housed in municipal home 109 and its obsolete reservation retired. The generated
  source snapshot remains private; the test runs this optional case when present.
- A controlled municipal legacy repair preserves ownership/households and supports
  exact 30-day continuation, with full canonical assertion retained.
- Existing composite paid cargo/fare/provider/mall escrow atomicity, core release,
  public-life and town-situation controls/save/replay gates pass on the same source.

Final integration must retain newer road/river/native work and rerun immutable
combined acceptance. This scoped result is not another one-hour run or Android
certification. No legacy migration policy beyond the parent/balance-worker agreement
is introduced.
