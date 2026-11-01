# Current public model composition

The worker experiment is merged with immutable public `01eeda3d2ff09822b9422721f75e97fabbc9958a`. Production remains disabled and the full synchronous game remains available. No family files have been altered or promoted in this port. Existing creator safeguards, neighbourhood history/pulse and native parser/completion fixes are retained.

`test_core_actual_ui.py` with `WORKER_ORACLE_COMMIT=01eeda3d2ff09822b9422721f75e97fabbc9958a` passes ten trusted actual UI actions against untouched public source, full model/RNG after each. The independent paid UI runner with that same oracle passes all11 gates, including writer hold/readback/token ordering. Its historical `currentModelCovered:false` metadata is hardcoded to669; the explicit oracleCommit/oracleSha256 and entireCurrentOracleModelAndRng gate establish the actual01eeda comparison. We did not change the independent runner to conceal that metadata.

`current-native-source-parity.json` proves MainActivity, WorkerArchiveReply, WorkerArchiveReplyFields and WorkerArchiveRequests are byte-identical to01eeda. `test_native_worker_archive_callbacks.py` passes ID/epoch/duplicate/cancel/lifecycle and pure-Java duplicate-member/parser compilation gates. Those tests do not execute Android JsonReader or certify a device.

The real Settings backup/restore controls now choose current `AndroidArchive.requestWorkerExport/Import` when native is present. Missing async methods refuse rather than exporting stale host state through legacy synchronous helpers. `test_native_ui_dispatch.py` exercises actual buttons with a labelled Java bridge mock and proves archive unchanged. It is not physical native acceptance.

Earlier realtime performance receipts remain attributed to their retained669 source hashes. No new01eeda smoothness claim is inferred from them. Full routing, family UI journeys, long-task budgets and actual native durability remain pending. Coverage remains35 retained identifiers/51 pending operations before family composition; the example calendar module is not counted as another game control.
