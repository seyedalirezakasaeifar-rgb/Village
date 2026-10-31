# Dynamic camera/cache acceptance

Base integrated source `65356a71c7180db73232801e5082daac3e6d66d7`, plus brownfield art `286009c` (replayed here as `766fee8`). Integrate the new acceptance/fallback commit after brownfield art; do not replay that art twice.

## Defect found and fixed

The first matrix crashed in `dioramaFoundation` during an expanded-neighbourhood redraw: `neighbourhoodMaterial()` returned undefined, then the foundation read `p[1]`. The palette table knew only the original five district IDs. New districts among the 21 deeds reached the missing entry. The renderer now uses its existing neutral material palette for an unlisted district ID. No economics, new art direction or district advantages change. The regression explicitly requires a two-color material for all 21 deed areas. The old lookup fails this requirement.

## Finite coverage and results

`tests/test_dynamic_camera_matrix.py` authors a 2,000-resident city, buys all 21 deeds with conserved fixture funds and builds three paid routes using the established integration fixture. An actual factory liquidation, funded quarry renewal and real paid redevelopment project cover changed property states. Redevelopment demand is authored specifically to reach that project; this is not a claimed natural growth playthrough. A render-only truck silhouette guarantees a shadow intersection without creating economic cargo.

The 36 cases combine 640×360/DPR1, 844×390/DPR2 and 1280×720/DPR3, six zoom levels, day/night, low/high detail and reduced motion. Browser DPR is subject to the game's normal backing-store cap. Deterministic camera offsets visit the renewal site, redevelopment, tall buildings, guideway, station and seeded mixed neighbourhoods.

Every case passes:

* Repeated paused final frames are identical.
* A cold full static-scene rebuild, including cleared sprite/view/night caches, reproduces the complete warm final frame exactly.
* The actor compositor's damaged pixels match an independently composed **all-static-layer** reference within the existing two-channel-value tolerance: zero channels exceed it. This reference deliberately shares the established elevation policy; the separate bridge/ground silhouette oracle remains the independent depth-policy regression.
* Serialized economic state is unchanged by these rendering operations.
* Atlas ≤48 MiB, renewal cache ≤864 KiB, repair backing stores ≤two viewports. Observed atlas maximum 10,934,528 bytes and renewal cache maximum 55,296 bytes; no unbounded cache growth is observed in this finite sequence.

The worst eight-draw warm mean across cases is 9.23 ms at zoom1.6; far zoom.2 maximum is 1.11 ms. These are host Chromium cached-paint measurements, not real RAF tails or Android performance claims. Source-hashed per-case receipts and static controls captures are in `docs/previews/camera-matrix/`. Existing paid-port continuity/state/LOD and brownfield-stage suites also pass on the same source; receipts are copied here without replacing historical evidence.

## Actual motion review

Local-only diagnostic animations are preserved in `/workspace/scratch/camera-matrix/`: transit-day.gif, transit-night.gif and bridge-crossing.gif. They contain ordinary unpaused game motion after camera/fixture setup; the bridge fixture selects initial visual frameClock10.1 before resuming, recorded in bridge-motion.json. Paid boat motion remains at `/workspace/scratch/townledger-port-art/river-session.gif`. None of these animations is uploaded or bundled. Sampled bridge/day/night frames were visually inspected; no additional flicker or crossing defect was established. This limited review does not prove all moving occlusion configurations.

`tools/qa_capture_crossing.py` reproduces the local crossing diagnostic. Native WebView animation/oracle acceptance and longer-running session latency remain release gates; no native-device claim is made.
