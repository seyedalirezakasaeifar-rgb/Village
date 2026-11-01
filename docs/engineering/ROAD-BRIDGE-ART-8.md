# Raised road bridge art

Status: visual prototype rejected by the user. Retained here for mechanics/rendering integration checks while the graphics owner redesigns supports, approaches, shoreline and the wider visual system. Pixel equivalence and actor-depth checks are correctness evidence, not visual acceptance or release approval.

The renderer now turns the existing `bridgeRenderSnapshot()` into a visible raised causeway: asphalt deck, restrained center marking, twin rails, shallow bank approaches, and sparse water-side piers. The water remains visible beneath the span. A maintained bridge shows its real wear band; an under-maintained bridge keeps the span visible, closes both approaches with clear cross marks, and remains water in the river network.

The compositor uses each actual road path to place road traffic and buses on the bridge plane. Elevated metro keeps its existing separate plane. Watercraft stay under the deck wherever their silhouettes overlap it; the bridge gameplay rules continue to reject work that would interrupt an active navigation route, dock, or fishery. The art reads only the existing bridge and route state and does not change settlement, conditions, routes, or RNG.

## Verification

- `python tools/assemble.py`, `node --check assets/game.js`, and `git diff --check` pass.
- `python tests/test_road_bridge.py` passes the bridge gameplay acceptance suite, including real freight traversal, closure, and repair.
- `python tests/test_road_bridge_art.py` passes the renderer suite. Its paid 60-unit grain import follows all five actual span tiles, then feeds that real route through truck and bus deck-height checks. It verifies elevated-metro exclusion, boat-below-deck ordering, honest closed-span state, and water continuity.
- The bridge-specific paused cold redraw matched every backing-canvas channel exactly after a forced renderer-cache rebuild; the art pass left the sampled day, treasury, region, total money, world seed, and observation count unchanged.
- `python tests/test_dynamic_camera_matrix.py` passes all 36 viewport/DPR camera cases with paused cold-redraw pixel equivalence and ground-actor checks.
- Host Chromium phone captures: [open bridge](../previews/urban8/road-bridge-art-phone.png), [closed bridge](../previews/urban8/road-bridge-art-closed-phone.png); measurements and source hash: [bridge art evidence](../previews/urban8/road-bridge-art.json).
- In the seeded host fixture, the warm render benchmark measured 0.53 ms/frame before the span and 1.12 ms/frame with it on the current recovery assembly. This is one host-side comparison, not an Android frame-rate claim.

The quote code checks active waterway manifests. The independent integration state test also builds a real fishery whose fishing route crosses the proposed span and confirms that the span is refused without a treasury shortfall. Boat depth is a geometric compositor check at the shared projected plane; it is not a physical clearance or final visual-quality assessment.
