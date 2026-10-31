# Runtime rendering corrections

Base: `27e47f6c0576b7f02474312424d4f0e1b9cb06f4`. This is a source-only fix; no trailer inputs, APK, release, or economic changes.

Confirmed defects:

* A funded ground bus could overwrite an elevated guideway. The actual transit fixture reproduces the crossing at visual phase 10.7. Of 183 opaque overlapping pixels, the previous composition overwrote 151; the corrected composition overwrites zero. Ground actors are placed below intersecting elevated decks; elevated trains occupy the guideway plane. Actual sprite alpha determines occlusion, rather than discarding whole vehicles. Support lamps remain unchanged.
* Re-stamping translucent foreground sprites onto an already composited static scene double-blended shadows and edges near moving actors. The damaged area now starts from a cached ground/shadow underlay, then paints each intersecting static/actor layer once. Integer backing-pixel damage clips avoid fractional clip-edge blending. A seeded independent full-redraw comparison finds 464 wrong channels (maximum difference 59) with the old algorithm and zero with the correction.
* The running-state pause glyph was missing on the trailer source runtime. Play and pause are now explicit SVG paths, retaining the existing accessible labels and titles. The DOM changes only on a pause-state transition.

`src/69-actor-compositor.js` owns layer bounds, depth ordering and damage repair. The extra opaque canvas is bounded to the current viewport: 941,904 bytes at the tested 844×390 host viewport; 3,056,640 bytes in the 1280×720 case. It releases its backing store when distant/reduced-motion detail cannot produce actors. Eligibility includes the transit-specific intermediate zoom threshold. No routing, settlement, production or save fields are touched. Bounds cached on visual scene items do not enter game state.

## Evidence

`docs/previews/render-bug-audit/` includes original-algorithm/fixed/reference pixels, the real bus crossing before/after, mobile day/night/far captures, pause icon, exact source hashes and test receipts. These are controlled, funded QA towns, not a player's save. The original six trailer inputs are preserved separately. Paid-port animation was reviewed in a new six-second host-browser session; its local diagnostic animation is not published. Its pose boundary/state/bridge/LOD checks pass. The independent trailer review did not substantiate the earlier boat-turn concern or widespread disappearing textures. Fixed rail lamps were correctly excluded from the defect list.

Checks run:

* `tests/test_actor_compositor.py`: independent single-pass reference, reproduced old defect, zero corrected difference, unchanged economic state, font-independent control.
* `tests/test_bridge_occlusion.py`: actual paid bus crossing, old/fixed opaque deck pixels, unchanged state.
* `tests/test_compositor_camera.py`: 10 day/night views across zoom 1.4/.6/.4/.2/1.1 with pan, identical paused repaint, viewport cache bound and distant release, unchanged state and no runtime exceptions.
* Existing transit-art and paid-port-art suites: stable paid service, reduced-motion/distant actor early exits, continuity and inspection.
* Sprite envelope suite: 3,836 existing sprites retain exact pixels and bounded atlas accounting (run before the final underlay eligibility adjustment; sprite code unchanged).
* Real RAF large-town scenario: 128×128, all 21 deeds, 2,000 residents, three real routes at 64×. Near draw median 2.8 ms, P95 21.2 ms; RAF median 16.7 ms, P95 50 ms, P99 116.6 ms. This retains a long simulation/session tail; it is not a claim of smooth 60 FPS. Far draw median 1.2 ms, P95 26.4 ms; RAF P95 49.9 ms, P99 83.4 ms. Full receipts include tick costs and conservation checks.

The near/far runtime receipts are host Chromium measurements, not Android device FPS. Native WebView animation acceptance remains a release gate owned by integration/native review. Camera and night captures provide finite regression coverage, not a claim that every possible city occlusion is proven correct.
