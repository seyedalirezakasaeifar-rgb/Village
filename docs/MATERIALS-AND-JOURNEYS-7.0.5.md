# 7.0.5 development slice: distinct properties and purposeful journeys

This phase extends the living-town art direction and connects map activity to inspectable economic assignments. It remains intermediate overnight work.

## Building identity

Original code-native civic stone bands, dressed corners and entrance stairs distinguish public institutions from glazed shopfronts, industrial cladding/clerestory glazing, and three residential parcel treatments. Appearance responds to maintained/weathered/distressed condition, occupied/vacant homes, trading/closed enterprises, and productive capital scale. A funded enterprise expansion (scale1.4+) receives rooftop equipment. Static sprite and viewport cache keys include these states so a change cannot leave stale artwork. Low-detail mode omits extra material work.

The fixed-camera capture tool compares the preserved7.0.4 APK against the final source in town, shop, industry and shoreline views, recording both source hashes. These captures are evidence of the material slice, not a claim that the full planned art transformation is complete.

## Transport and interaction

A confirmed purpose/style bug gave vehicles a new type without updating their old randomly chosen speed. Purpose assignment now sets pedestrian, truck and car speeds consistently. Commuter samples include return-home journeys as well as trips to an actual employer; freight samples retain a real consignment and destination.

Tap a moving trip to open the Journey Inspector. It shows the assignment, origin/destination, road path and available consignment accounting, with links to both properties. The highlighted route follows the sampled trip. The interface explains that the visible sample is not every economic journey. Closing the inspector removes its route overlay.

Aircraft taxi paths use cubic curves with runway-aligned endpoint tangents. Departure movement follows the takeoff acceleration without a position jump; landing descent meets the runway at zero altitude and the rollout decelerates to the taxi transition. Geometry tests sample both sides of all visible phase boundaries. The intentional offscreen flight interval remains.

A separate accounting defect was also found: finishing a visual commuter increased the delivered-consignment counter. Visual trip completion no longer increments economic arrivals; only freight completion does. Historical counters in older saves may retain earlier mixed counts; no unsupported history correction is invented. A counterfactual test runs visual traffic without advancing the economy and verifies unchanged cash and consignment arrivals.

## Pause diagnosis

The exact paused-screen regression was intermittent. Pixel/DOM comparison isolated a42×44 region at the play button, with identical DOM. Crops showed its CSS transform transition finishing after the paused screenshot. The play control now has no timed transition; the exact equality assertion remains. This complements immediate paused drawing and stopping timed paused panel refresh from the previous phase.

## Validation and remaining work

Targeted tests cover appearance cache states, transport purpose speeds, taxi/runway/touchdown continuity, trip inspection and links, separation of visual/economic arrival accounting, mobile layout and the unmodified core pause gate. The immutable full candidate gate runs once after this coherent asset freeze; its manifest is authoritative for final validation.

The next meaningful economic slice is local service access and qualified staffing/training. The next major art slice should extend architecture volumes/material families and worksite/transport activity across districts, rather than adding unrelated decorative effects. Native software-emulator resource limits and full older-engine certification remain open.
