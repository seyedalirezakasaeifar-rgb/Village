# Combined-world review and sprite-cache tail reduction

Based directly on integrated `525e47dd3967741fb59d2fd06921c1647a29a24a`; do not replay earlier graphics/transit/urban commits. Apply this scoped follow-up and regenerate the bundle. No simulation, routing, topology, economic ownership, archives or climate rules changed.

## Concrete finding and fix

The renderer was caching120 detached-home IDs despite the authored pixels depending only on six massing styles, two garden paving patterns, and (at night) three window-light patterns. Each neighbourhood/condition combination multiplied these duplicate canvases, causing avoidable rasterization and atlas churn. The cache now uses that exact visual signature while passing the original stable ID variant to the artist. House shapes and diversity do not change.

`test_house_atlas_equivalence.py` compares all120 ID variants × three condition states × day/night:720 exact PNG and emission-metadata comparisons against the unshared implementation. All pass with unchanged economic state. Peak specimen-cache bytes fall from9,246,720 to2,696,960, a70.8% reduction. Existing3,836-item envelope/byte-accounting checks also pass; their actual atlas uses200 sprites /17.8MB. An unused rent-pressure field was removed from appearance keys because no artist uses it; nonhousing now avoids allocating an unused neighbourhood descriptor on every frame.

Profiling was extended past the old5,000-sample limit, which exhausted sprite samples during fixture initialization. It also measures `spriteFor`. In the matched all21deeds /2,000resident /three-route far case, cache-stage time across the instrumented session falls190.0→101.1ms despite more draws. The paired warm interval records draw P95 44.4→29.1ms, draw P99 66.0→48.1ms, and RAF P99 183.3→133.4ms. Profiling includes authored initialization/warmup stages; eight-second host runs have timing variation and are not a calibrated device study. `paired-profile-summary.json` preserves both hashes and stage counts; the earlier233ms RAF-P99 sample is retained in `before-far.json`.

The remaining RAF tail includes simulation/tick work and cold GPU/browser behavior; this patch does not claim to eliminate every hitch or achieve60FPS. Final uninstrumented near/far receipts are in `final-near.json` / `final-far.json`, each bound to its exact final source.

## Actual combined visual review

`capture_visual_acceptance.py` uses a real loopback HTTP origin serving shipped assets. A conserved authored2,000-resident town purchases all21deeds, builds local/outer bus routes and elevated metro, and advances15 economic days. Captures review near/far detail and an actual eastern station/road/house crossing, including night masking. Separate genuinely funded retail and paid private school/fire fixtures exercise their actual render descriptors in the same integrated application. They are controlled examples, not a claim of organically achieving all developments in one town.

The near/far, rail crossing/night, market hall/night and private provider frames are committed under `docs/previews/visual-acceptance`. Visible rail stays on public street alignment, foreground houses occlude deck/vehicles, and no parcel is cleared by painting. Far individual actors/shadows remain early-culled; existing unreadable-collection LOD checks pass. Atlas/envelope, transit art and urban art gates pass on the integrated source. No new depth or footprint defect was found in these cases.

A real readability issue was corrected: the overview freight legend disappeared against dense roofs. It now has a restrained contrast backing and avoids top-right map controls on narrow screens. Market counts still describe owned loads including queues/outside legs; no new economic meaning is introduced.

Outstanding: physical Android GPU/thermal/lifecycle validation, subjective long play, and remaining simulation-side64× tail latency. The transit worker retains routing ownership. No APK/signing/deployment work performed. Owned production files are the renderer cache signature, urban appearance key and overview legend; tools/tests/media accompany them.
