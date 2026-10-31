# Renewal-cap and release-tooling checkpoint

Integrated 81339b4: the 3,000-record renewal ceiling now rejects a new paid survey before mutation. The boundary fixture passes self-export/import, preserves all existing provenance and lets active work complete. Final current-source core gates pass. Source-bound receipt: `reports/integration/renewal-limit-audio-8/receipt.json`.

Real rapid audio stress plus existing mocked race/effects tests passed on the immediately preceding source 73345dc2...; no audio engine changed afterward. See `AUDIO-RAPID-CONTROLS-8.md`. This corrects a previously unexecuted harness gap, not a product failure. Physical listening/routing remains outside host coverage.

Included deterministic `tools/check_asset_manifest.py`: sixteen referenced media files, correct case/nonempty hashes and no external/absolute media URLs. Two current runs produce identical manifest bytes. Invoke it again in final immutable APK verification; this tool does not itself inspect a signed APK. Player audio release notes and settings/provenance documentation are included with their historical source limits.

Production remains synchronous. Independent speed-sweep evidence suggests 16× is the highest responsive measured setting on one retained late host town; it is not a universal or phone guarantee. Do not enable failed cooperative/COW/presentation experiments or describe the 64× input stalls as solved. No final APK or release publication in this checkpoint.
