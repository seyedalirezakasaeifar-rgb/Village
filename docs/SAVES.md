# Save and installation migration

## Install alongside 5.6

6.0 uses package `org.townledger.vale`. The supplied 5.6 app used `org.townledger.android`, and its private update signing key was not supplied. The new package avoids forcing an uninstall or overwriting the old installation. Both can remain installed.

In 5.6, export the town from Options. Open 6.0, choose Options, and import that JSON/text archive. Desktop/browser mode provides a paste box; the new Android host opens the system document picker. Keep the original export until you have confirmed the imported town.

## Schema

The legacy `version: 3` field is retained for compatibility. New saves add `schema: 4`, release identity, RNG state, property investors, cargo, commodity accounts, price history, policy observations and visual trip state. Future schema numbers are rejected.

Legacy 5.6 and compatible earlier version-2/3 JSON towns are validated and supplied with missing fields. Missing commodity accounts take their opening inventory from the imported town, including any cargo already present. This does not invent past production history.

Restore validates map dimensions, tiles, footprints, household memberships, job ownership, loans, new investor balances and cargo counterparties before committing state. A rejected import leaves the current town intact. Exact seeded continuation and an authentic supplied-5.6 export are tested; an in-place upgrade on the user's physical phone is not tested.

## Recoverable autosaves

The primary key is `townledger-v6`, containing a serialized payload and FNV checksum. The previous valid primary is retained as `townledger-v6-backup`. Each individual localStorage replacement is atomic; the two-key operation is not a database transaction. Loading tries primary, backup and then legacy keys. Options exposes recovery of the previous autosave. IndexedDB remains a best-effort second storage route.

After a valid v6 save, the redundant legacy raw copy is removed to avoid storing three large payloads under the browser quota. Exports are raw JSON and remain user-controlled. Very large towns can exceed browser or device storage limits; the Options saving status and manual exports should be checked.

Checksums detect accidental corruption, not malicious editing. This is an offline single-player game with no anti-cheat claim.

## Signing continuity

The new APK is development signed. Its signing material is separate from the distributable source. Keep the private signing archive private if preparing future builds. The generated development keystore uses the conventional development password `android`; it is not production publishing credentials. New releases must retain that signer to update the 6.0 package without uninstalling.

## Updating 6.0 to 6.1

6.1 retains `org.townledger.vale` and the exact RSA development signing certificate used for 6.0. The version code rises from 12 to 13. The APK is therefore prepared for an in-place update; actual device installation is untested here. Do not uninstall the old app to update without first exporting the town.

Compatible 6.0 archives remain schema 4. Missing `climateSeasons` and `climateWeather` fields default to false. Climate choices are part of an archive; display and autosave preferences are separate local settings. Empty estates now settle existing cash and redeemable deposits to external heirs after 360 days, and property-investor surplus pays regional shareholders. These are cash transfers, not a reset of the economy.

## Updating to 7.0

7.0 retains the package and signer, with version code 14. Schema 5 adds operating inventory costs, order and sales trends, company treasury distributions, pensions, retirement handling, monetary controls and the new economic rules. Legacy loans without a rate-type field retain fixed rates. Newly issued variable-rate contracts adjust with the benchmark. Presentation preferences persist locally; climate rules remain in the town archive.

An imported city retains its physical streets, buildings and residents. The new named street plan and reauthored starting demographics apply to new towns. Existing economic results will change under the new rules; retain a previous export if preserving the old model matters. Older builds reject schema-5 saves rather than silently interpreting their balances with old rules.
