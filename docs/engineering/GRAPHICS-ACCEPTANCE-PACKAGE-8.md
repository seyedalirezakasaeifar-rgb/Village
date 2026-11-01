# Graphics acceptance handoff

## Exact source and composition

Renderer/fixes/evidence tip: `a3c1f94c9c84b8d06a2dfe26a818b6f51c0efea5`, branch `codex/8-webgl-actor-options`. Accepted model base: `669c908706af997375680674390e46fd132a970a`. Exact changed runtime file list, bytes, SHA-256 hashes and all34 registered categories are in `GRAPHICS-ACCEPTANCE-MANIFEST-8.json`. Later packaging commits change documentation only.

The integration reviewer owns the final composed model. Merge source hooks against its current modules and regenerate `assets/game.js` using `python tools/assemble.py`; do not overwrite a newer assembled economic model with this branch's bundle. Runtime additions are all `assets/webgl-*.js`, four `assets/newfoundland-*.js`, the pinned vendor module/license, the late snapshot source adapter, and scoped hooks in preferences/waterfront/transit/locator. `assets/index.html` loads the tiny module entry after game.js. Preserve the original startup ordering fix and both ded5834/dfe4a2c actor fixes.

Three.js0.160.1 is bundled offline at `assets/vendor/three-0.160.1.module.js`, from official npm package, with its complete MIT notice in `assets/vendor/THREE-LICENSE.txt`. Preserve that notice in APK/source distribution. Our modules, geometry and small procedural materials are original project art. Public heritage photographs and the private generated concept are references only and are not bundled; no CDN/hotlinked assets or extra credentials are required.

## Startup, controls and settings

Recommendation: keep normal release startup **Canvas**, as currently implemented. WebGL is opt-in `?cityArt=webgl`; no query means the complete Canvas renderer without loading Three/art. Do not silently make the high reference tier the default. For QA only, add `cityBadge=1`; do not ship the badge in normal release URLs.

Within opted-in3D, existing quality preferences map Performance→Economy, Balanced→capability/observed-frame adaptive, Rich→explicit reference. Balanced on software or unclassified GPU falls back to Canvas; identified hardware starts Balanced with measured guard. Adaptive Balanced median>100ms→Economy; adaptive Economy>400ms→Canvas after the documented initial sample. Hidden/busy intervals are ignored. These thresholds are conservative protection, not smoothness guarantees. Explicit Rich is not silently downgraded and preferences are never rewritten by fallback. A real preference change can retry after fallback; camera is retained.

`cityQuality=economy` and `cityQuality=reference` are forced diagnostic tiers and bypass automatic frame fallback. The historical `cityQuality=low` is an expensive old diagnostic tier, **not Economy**. Do not use it for weak-device acceptance.

Actual WebGL controls implemented: pointer/touch drag, two-finger pinch, wheel/zoom buttons, full128-atlas overview, portrait resize, ray→actual property/road picking, inspect/follow, original onTap placement and road dragbrush, overlays, locator/camera synchronization, context-loss Canvas fallback and quality retry. They dispatch original commands rather than independently mutate authority. Controls remain subject to source-matched final tests; specialized paid workflows are validated by gameplay owners, not certified merely by ray accuracy. Partial simulation/road batches return no unsafe snapshot/actor reads. Renderer refresh consumes committed revision; it must not be pointed at an independently mutated Worker model.

## Architectural coverage

All34 registered kinds have a route:5 residential/shop modules;17 civic/commercial/working modules;10 specialized modules; worksite stage fencing; repair remains a tool. The manifest enumerates every kind. Retail-centre flag has its own lawful multi-tile form. Real construction/renewal stays a site rather than rendering a completed building. Concave non-site titles deliberately use bounded per-cell fallback; no geometry fills private-title voids. A represented category is **not** complete art-direction or state acceptance.

Remaining visual limits: repeated silhouettes and broad lawns persist; attached rows occur only where legal actual adjoining homes permit them. Civic/industrial forms are generalized original adaptations, not landmark replicas. Condition/provider/tenure/project data is projected, but every state is not expressed with equal detail. No absent church/community-hall/private bank-branch entities are invented. Rich/Economy have intentionally different detail; distant actors and trim are culled without suppressing the economy. Canvas remains the fuller established visual fallback.

## Evidence and performance limits

Representative same-town/camera tier pair (source29) is in branch `codex/8-webgl-running-soak`, commit `d28ddf139a6dc7076342f19715f05c26a070a547`: `docs/previews/webgl-running-soak-29/economy-representative.png` and `reference-representative.png`. Both use archiveSHA4cfc3956f1eacadaf5dc3d2cd4bcd6c182bb4b18a50897be4ca575e709da2084. These are actual development views, not the generated concept or a promise of its fidelity. Fixed-source Rich representative and five evolving-city samples are in `docs/previews/webgl-rich-retest-8/`; both-tier actual control captures in `docs/previews/webgl-tier-actor-resources-8/`.

Host serial Economy benchmark on same scene reduced oldlow median242ms/p95267ms to Economy median41ms/p9552ms, triangles137826→15450, calls23→20. Host wheel next-frame median64ms/p9574ms includes automation. SwiftShader is software rendering; neither submissionCPU nor these samples certify physical-phone FPS. Explicit Rich remains expensive. Native WebView83 functional probes and newer exact-source acceptance are owned by native reviewer, not inferred from host screenshots.

Frozen29 Economy completed30minutes but exposed a Traffic cache defect; Rich stopped133seconds on a boat transition defect. Both are preserved as negative evidence. Fixed Rich sourcef26d696 completed1803.65seconds/58 exact paused pixel/archive/RNG checks, zero errors/findings, actual funded actions and river deliveries, context loss/retry. Post-GC heap15.63–18.74MB with real model growth. Additional sequential Economy/Rich lifecycle test confirms both option roundtrips, bounded warmed resources, unchanged archive, idle pause and complete disposal0geometry/0texture. No leak-proof or physical performance certification is claimed.

## Final exact-head gate

When reviewer supplies its composed commit, run focused tests there: `test_webgl_paused_actor_options.py`, `test_webgl_paused_boat_lod.py`, `test_webgl_tier_actor_resources.py`, `test_webgl_night_overlays.py`, `test_webgl_dpr.py`, plus Node economy envelope/actor/static-batch/quality-policy oracles. Verify assembler output, startup before/after town, actual touch/placement, bridge/transit depth and overlays on that source; retain failure frames. Browser tests must use supported HTTP origin. Do not reuse older-source passing results as final composition certification. Native source-matched functionality and safe default/fallback are release gates; no broad new art is planned while integration runs.
