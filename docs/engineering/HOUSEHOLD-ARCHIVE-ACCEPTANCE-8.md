# Household archive acceptance follow-up

Parent/runtime base: `ca0c6d07af3cdd380aa42b624bb66d95645edfce`.
Game bundle remains SHA-256 `218de17d31e130f8f683ab1287307380eb2ec0689b06d39a9003ef26883a1fc7`.

## Diagnosis

The preserved failure was an invalid test assumption, not a demonstrated missing current-membership check. At hardtimes seed 42, day 721, person 0 has `movedAway: true`, `deceased: false`, `job: -1`, and historical `hh: 0`. Household 0 has no members, `home: -1`, and $9.38128855803981. No current household roster contains person 0. The old test changed that historical `hh` to 1, which exists, and called the result a current household-roster mismatch. There was no current roster relationship to contradict. [Exact diagnostic receipt](evidence/household-followup/diagnosis.json).

A real malformed relationship changes a living, present person's household pointer while leaving that person in the original household's roster. The existing pre-adoption member loop already rejects this bidirectional mismatch, duplicate membership, deceased/departed people in current rosters, and active people absent from all rosters. The structural check already requires every historical household pointer to identify an existing household.

`outwardMigration` removes current membership, sets `movedAway`, releases tenancy, and retains the historical person/household records. `yearlyDemographics` similarly removes deceased people from rosters while retaining the former household. Empty estates retain financial/property identity; a later incoming household receives a new identity, rather than inheriting the old family's finances. Legacy empty estates may still have a former `home` reference pending normalization. Requiring all historical people to occur in current rosters would reject these valid archives. Without extra historical provenance, the archive cannot independently verify which existing household an unrostered historical person formerly belonged to.

## Change

The adversarial mismatch fixture now selects a living, present resident. No production validation, migration, economy or archive format changed. This fixes the false-positive acceptance gate while preserving meaningful current-membership rejection.

Added counterexamples exercise deceased and departed historical people, each with surviving family members or an empty estate, and modern or legacy schema-7 tenancy, in all three existing scenario/age cases. They require accepted empty estates, preserved household references, cash, deposits, property ownership and loan identity, and total currency. Each accepted case is then faulted with an inactive person in a current roster and with a nonexistent historical household; rejection must preserve the live archive, RNG, save timeline and caller object. All historical fixture archives must still import and validate.

## Acceptance

Evidence includes the corrected adversarial matrix, 90-day full persisted-model/RNG replay after each scenario, and the bounded core gate rerun. Presentation/traffic caches remain excluded from economic replay comparisons, as in the existing test. No codec, cooperative simulation, retention or UI changes are included. Android/device/performance/APK checks remain outside this follow-up; the unchanged runtime already has the separate recovery-batch evidence.

The final adversarial pass covers 25 corrupt-record mutations in each of settlement/day 1, regional/day 361 and hardtimes/day 721; twenty-four accepted historical-household counterexamples (twelve empty estates and twelve with surviving residents); forty-eight atomic historical-roster/household rejections; two existing historical fixture files; and exact 90-day replay in each scenario. [Raw matrix](evidence/household-followup/adversarial.json). The [final manifest](evidence/household-followup/final-manifest.json) records the bounded twenty-gate rerun and separate exact native import-script bridge check. Full model, RNG, currency and goods tests pass. Long-run release endurance, Android/emulator and performance checks were not run here.
