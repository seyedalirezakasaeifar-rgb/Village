# 7.1.0 region/waterfront candidate QA

Source SHA-256: `c482b89614ecb09bccf8a0ddfda8c944f740d01a1bed9da5cbb58764627a9781`.

All 32 candidate gates passed against this frozen JavaScript and unchanged asset set. The official SDK produced a signed development APK (version 7.1.0, code 20); package assets, manifest, real DEX, resources, absence of requested permissions, v2/v3 signature and ZIP alignment passed verification. This is an intermediate development candidate, not a store release or a claim of completed device QA.

APK SHA-256: `4fb6134f4e5ae6ea80b5ddba2e355ae1e298ca10fd454e12cedc9c2945c9614c`. The persistent development signer is unchanged and remains outside the repository. The older baseline signer is different; preserve a verified export before any uninstall required by Android.

## Browser measurements

The real-RAF test used a synthetic 2,000-resident town with 713 buildings at 844 × 390 and requested 64×. During its measured eight-second interval it completed 312 days at 63.3× effective speed. Warm renderer p95/p99 were 34.5/43.5 ms; tick p95 was 19.1 ms. RAF p95 was 33.3 ms, with 6 intervals over 50 ms. Monetary drift was 0.00000570. Founding/loading timings are retained separately, rather than mixed into the warmed interval. These are host Chromium measurements, not Android FPS.

Tight sprite envelopes reproduced 1,547 old padded sprite instances across an actual town, housing variants and all building kinds/condition samples, comparing 126,730,240 pixels without a mismatch. The sampled atlas used 27,652,608 calculated RGBA pixel bytes versus 108,789,760 for the former padding: 74.6% less retained pixel storage. This is not a measured reduction in total process RAM. The atlas now has an LRU limit of 600 entries and 48 MiB of calculated pixel storage. Repeated preference-driven clears reset the byte counter and repopulate it exactly.

## Test coverage

- `test_sprite_envelopes.py`
- `test_annexation.py`
- `test_annexation_networks.py`
- `test_waterfront.py`
- `test_waterfront_mobile.py`
- `test_seed_sort_stability.py`
- `test_map_hierarchy.py`
- `test_host_lifecycle.py`
- `test_native_archive_io.py`
- `test_council_programme.py`
- `test_credit_crisis.py`
- `test_council_accounting.py`
- `test_workday_scenes.py`
- `test_credit_cashflow.py`
- `test_household_markets.py`
- `test_local_civic_services.py`
- `test_transport_visual_states.py`
- `test_service_provision.py`
- `test_older_webview_api.py`
- `test_archive_schema.py`
- `test_review_workflows.py`
- `test_mobile_rendering.py`
- `test_controls.py`
- `test_v7_contrast.py`
- `test_release.py`
- `test_v7_model.py`
- `test_v7_default_starts.py`
- `test_v7_scenarios.py`
- `test_v7_liquidity.py`
- `test_v7_policy_experiments.py`
- `test_regional_tradeoffs.py`
- `test_v7_live_large_town.py`

The region/waterfront phase includes genuine outer territory, affordability/adjacency/stale quotes, cancel/confirm/repeat protection, paused treasury feedback, complete legacy map migration, atomic invalid imports, a paid road extension and productive fishery on purchased riverbank, finite shared catch, staff/route/price-dependent cargo revenue, manifest conservation, continuous/pause-stable boats, 44px controls at three phone sizes, long economic counterfactuals and old-WebView/native archive/lifecycle unit coverage.

## Limits and next work

The APK was statically verified; this candidate has not received a reliable Android touch, system Back, document-picker or lifecycle play session. The previous software-only emulator could load and exercise the engine but its System UI suffered ANRs. No native FPS claim is made.

This earlier APK has overlapping regional-overview labels; the later [development source](WATERFRONT-PLAY-DEVELOPMENT.md) resolves them. The finite map, simplified ecological limits and visual samples of regional-owned exports are game abstractions. River imports/canals are not implemented. Further art/playability passes, prolonged expanded-region browser testing and final immutable release QA are still required.
