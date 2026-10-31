# Color-independent map overlays

This pass makes map status readable by shape and symbol as well as color. The status key appears inside the existing Town Signals control only while an overlay is active, leaving the map controls and footer untouched. Building badges are drawn only on a dirty redraw and at zoom ≥0.45; distant views keep the existing lighter overlay rendering. The badge pass is static, so pause and reduced-motion behavior remain stable.

Road status uses a circle with `+` for a direct street edge and a square with `X` without one. Enterprise badges show profitable, non-profitable active, and closed states with different shapes and glyphs; hardship and land-value bands also use distinct marks. The formerly blank crime overlay now marks actual recorded theft sites from the last 30 days and counts repeated cases at each site. It does not create incidents. Service-access marks have a dark outline and a high-contrast symbol for full, partial, or no reachable places. Transit distinguishes buses with solid routes and square stops from metro with dashed routes and circular stops. Neighbourhood labels now carry plan letters (`A`, `C`, `M`) and boundaries use distinct line patterns.

## Screenshots

These source-bound paused captures use the validated 2,000-resident visual fixture, seed 42, five simulated days, low visual quality and reduced motion. The actual incident system records five theft cases in this fixture; no incidents were injected. Overlay rendering leaves the saved game and RNG unchanged.

- [Road access, before](../previews/overlay-clarity-8/before-844x390-roads.png) · [after](../previews/overlay-clarity-8/after-844x390-roads.png) · [after with mobile UI](../previews/overlay-clarity-8/after-844x390-roads-ui.png)
- [Night business overlay](../previews/overlay-clarity-8/after-844x390-business-night-ui.png)
- [Real incident locations](../previews/overlay-clarity-8/before-844x390-crime.png) · [after](../previews/overlay-clarity-8/after-844x390-crime-ui.png)
- [Neighbourhood plan overlay](../previews/overlay-clarity-8/after-844x390-neighbourhoods-ui.png)
- [Portrait service map with enlarged key](../previews/overlay-clarity-8/after-390x844-schoolAccess-ui.png)
- [Night transit, active bus and elevated route](../previews/overlay-clarity-8/after-844x390-transit-night.png); the fixture carried two routes and six rides on day 6. [Capture metadata](../previews/overlay-clarity-8/night-transit.json) records its source hash, plus a portrait 390×844 DPR-2 run with no errors.
- [`captures.json`](../previews/overlay-clarity-8/captures.json) records before/after source hashes, viewports, incident state and legend text.

## Verification

`python tools/assemble.py`, `python tests/test_overlay_legibility.py`, `python tests/test_transit_art.py`, `python tests/test_urban_art.py`, `python tests/test_dynamic_camera_matrix.py`, and `python tests/test_mobile_rendering.py` passed. The overlay check exercises roads, business, hardship, actual crime locations, land value, transit, metro, medical/school access, neighbourhoods and deed boundaries. It confirms paused game/RNG state is unchanged, cold redraw pixels match, distant LOD skips individual badges, and the status key does not overlap map controls or the footer at 844×390, 568×320, 390×844 and 360×640. The existing mobile suite also passed seven viewport/orientation/DPR layouts without overflow or browser errors.

On host Chromium, the 40-draw sample for the 2,000-resident town measured 1.07 ms with overlays off and 1.40 ms with road badges on (about 0.33 ms additional in this run). These sub-millisecond timings are noisy host measurements, not Android frame-rate claims.
