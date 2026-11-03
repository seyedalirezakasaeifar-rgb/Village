# Retention, paid reviews and committed-day persistence

Integration base: `43d1fc0121afab18a329403b9280fa37384b3ad0`.
Assembled source SHA-256: `346992b501f8622b007dddc6bf75baadbf850f6211b8989c6c3ccfcdefc98207`.

## Scope and dependency review

Reviewed and applied the stale-review chain `f457b95c34710ab7271b303cb58034c87b1f66ce`, `24478b16588380a76e67a99f92d3670898bacdba`, `726d0a5a76512b6df8662d9c83f921b4a90d00b6`, required policy-card dependency `a17a691223c2870d2c68cdd3c3c28c7d38d849a9`, and `ccac497f0f8b7b2730c581876ece9991d6fea2de`. Then applied persistence fixes `67bf31349e8f41fe28ce33c2c46802dba2caa6d1` and `737e00024d23a0e821b69e697f8667d47f8a2b8b`.

The land-assembly UI conflicted with newer integration review-key handling. Resolution retains the newer `urbanClearanceReviewKey` argument to the authoritative transaction API, plus the candidate's target label, fresh quote comparison and focus restoration. The base's reviewed shopping-centre proposal and school placement changes remain intact. Generated game.js was regenerated from the assembled modules, rather than choosing an old bundle. No unrelated old branch trees were merged.

## Two independently reproduced negatives

1. The UI chain without committed-day persistence saves day 30 with day-29 history, before final observation/RNG publication. On the current integration base plus the five UI commits, the negative assembled source is SHA-256 `8ecf56af6ba7ef3d60250bdd4ee7d6cb15dcf6adf04998d5aa570f0fcbbab5c2` (modules at recovery-history commit `13ce2d763c71ccbdb562c52e5fda130fe6d5a55b`). The independent cold-storage test fails the terminal-history equality check. The probe was adjusted to tolerate absence of the proposed tick flag; its initial incompatible-probe attempt is retained separately. The existing historical candidate-only negative (`test_retention_midday_save.py`, source from `726d0a5`) also confirms the defect and is classified as historical evidence, not current-source acceptance.
2. The two proposed day-boundary fixes prevent the immediate partial write and resolve deferred requests truthfully, but allow a later manual save to acknowledge success for that failed partial day. The extended test reproduced this on assembled source SHA-256 `bad5c50f95177c06a61b1e815db43f9e893aad494f54a0538d102e3700022e85` (modules at `111b25104a246ac97b371129c17a22be143984cc`). Its original passing test did not cover a manual retry after a mid-tick exception. Both results remain in the evidence directory.

## Additional failure-boundary fix

A thrown tick now pauses and marks the current in-memory day failed. Deferred callers receive false; later saves, further ticks and public backup export cannot bless or advance that partial state. The prior durable town remains untouched. The UI reports the actual day failure and asks for recovery from the last saved town or a valid backup. Invalid import cannot clear the fence. A successfully validated restore or fresh founding starts a new timeline and clears it; real storage failures after a successfully committed day remain retryable normally.

This intentionally does not attempt rollback of an arbitrarily interrupted simulation. Unsaved in-memory changes since the last durable snapshot may be lost on recovery. It adds constant-size flags and checks, with no per-day deep snapshot or serialization cost. No Android, FPS, long-session or performance guarantee follows from this source inspection.

## Gameplay and review acceptance

The retention letter remains non-interrupting and targets a live household's assessed deficit. The bridge is treasury-funded, capped at $3,000 and limited to one payment until underlying departure risk clears; unresolved receipts survive ordinary archive trimming and reload. Training uses the existing eligible adult project without replacing competing work. Actual controls cover defer/Back, insufficient funds, stale/improved/departed households, exact conserved cash, repeat-click guards, receipts, eligibility and subsequent voluntary emigration. No job or retention result is guaranteed.

Paid land, planning and industrial reviews identify the quoted target, check its current identity/stage/price at confirmation, and restore focus. The policy card labels observed changes, actual sample days and missing readings, and explicitly says the readings are not causal proof. Its latest reading can be newer than an earlier retained 180-day review.

## Evidence and limits

[Final manifest](evidence/retention-followup/final-manifest.json) binds exact source, test inputs, logs, negatives and current-source acceptance. Core tests include full model/RNG replay, the corrected archive-fault/estate matrix, currency/goods accounting, storage chronology/queue/failure/retry, native host-JVM/bridge checks and core release gates. UI tests include the extended committed-day test and existing actual-control suites; existing school/assembly/private-proposal paths are also checked.

No production APK, Android compilation/emulator/picker run, performance benchmark or full long-run release endurance was run for this batch. Codecs, cooperative simulation and road bridges remain absent/disabled. No integration ref, PR merge/approval, signing, release or deployment was changed by this worker.
