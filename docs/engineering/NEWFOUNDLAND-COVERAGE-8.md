# Exhaustive Newfoundland renderer coverage audit

Audited registry `src/00-foundation.js` and actual `assets/webgl-taste.js` / `assets/newfoundland-kit.js` at quality checkpoint95a9b1f (art2f12f8f). **No category is production-accepted.** Covered below means only an authored Newfoundland geometry module; it does not mean all condition, ownership, district or activity states are implemented. Canvas remains the complete fallback.

All 34 currently registered types are listed; road and special render categories follow separately.

| Registered kind | WebGL status |
|---|---|
| transit_depot | MISSING specialized form; generic building fallback is misleading |
| elevated_station | MISSING specialized form; generic building fallback is misleading |
| bank | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| worksite | MISSING specialized form; generic building fallback is misleading |
| apartment | Authored Newfoundland geometry; context/state variation incomplete |
| tower | MISSING specialized form; generic building fallback is misleading |
| factory | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| warehouse | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| office | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| college | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| airport | MISSING specialized form; generic building fallback is misleading |
| metro_station | MISSING specialized form; generic building fallback is misleading |
| repair | Tool only; routes to real road resurfacing |
| home | Authored Newfoundland geometry; context/state variation incomplete |
| grocer | Authored Newfoundland geometry; context/state variation incomplete |
| bakery | Authored Newfoundland geometry; context/state variation incomplete |
| mill | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| farm | MISSING specialized form; generic building fallback is misleading |
| forestry | MISSING specialized form; generic building fallback is misleading |
| sawmill | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| quarry | MISSING specialized form; generic building fallback is misleading |
| contractor | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| townhall | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| police | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| fire | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| clinic | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| park | MISSING specialized form; generic building fallback is misleading |
| school | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| courthouse | GENERIC PLACEHOLDER; old prototype form, not Newfoundland-specific |
| watchtower | MISSING specialized form; generic building fallback is misleading |
| square | MISSING specialized form; generic building fallback is misleading |
| wharf | MISSING specialized form; generic building fallback is misleading |
| fishery | MISSING specialized form; generic building fallback is misleading |
| tavern | Authored Newfoundland geometry; context/state variation incomplete |

## Important false-representation risks before promotion

- `tower` currently falls into the generic two-floor fallback: the current prototype does not honestly depict its high-rise residential role.
- `worksite`/redevelopment/brownfield stages are not projected. A generic completed-looking house is not a valid construction-state representation.
- `park`, `square`, `quarry`, airport and transit facilities need distinct ground/structural forms rather than generic roofed buildings. Farms/forestry need their actual land use and work areas, not a suburban house on empty grass.
- A retail centre is a `grocer` with `b.retailCentre` and a real six-tile footprint, not a new registry kind. The adapter currently drops that flag and the kit misrepresents it as an enlarged shop. It needs a separate reviewed mall module.
- Public/private school and fire variants use the same registry kinds. The adapter drops authoritative title, paid/connected provider status and capacity. No honest ownership/operating distinction is implemented yet.
- `b.condition` reaches the snapshot but is not used by the new kit. Firm closure, occupancy, financed upgrades and property appearance are not projected. Current details must not imply paid staff, maintenance or activity.
- Bridge descriptors are exported but not consumed by the WebGL geometry. Tile4 currently receives the flat road treatment rather than a water-backed raised deck: NOT bridge acceptance. Waterfront wharf/fishery generic forms and absent real cargo craft also remain missing.

## Every other visible render category

| Category | WebGL audit status / required check |
|---|---|
| Ordinary roads/curbs/intersections | Basic state-driven tiles present; no full wear/class hierarchy, bridge elevation or road-paint gesture acceptance |
| Road bridges/ramps/abutments | Missing true elevated structure and road/water actor layers |
| Elevated guideways/metro supports/stops | Missing real network geometry and transit vehicles |
| Road vehicles, freight, pedestrians, emergency crews | Missing actual economic/schedule poses; do not fill with fake activity |
| River craft, port approach/loading/departure | Missing real cargo/fishing state and water/deck conflict checks |
| Airfield/runway/aircraft | Missing specialized site/route/aircraft rendering |
| Trees/vegetation | Original instanced-capable silhouettes exist but current crowns/trunks remain separate meshes; no ecosystem/property-maintenance context |
| Crops/fields/forest lots/quarry works | Missing land-use projection, plot-specific materials and actual seasonal-disabled behavior checks |
| Continuous natural terrain and shoreline | Plain ground/water tiles only; needs actual shore geometry, natural planting, no invented land or altered navigation |
| Construction, upgrades, demolition and brownfield reuse | Missing committed real-stage descriptors and appropriate geometry |
| Gathering/market square/civic venue | Missing actual setup/attendance/status cues; square currently wrong generic fallback |
| Night windows/lamp emission/weather/reduced motion | Missing complete state/option integration; seasons must remain disabled |
| Ownership/condition/closure/provider markers | Missing new-style semantics despite complete Canvas fallback |
| District/deed/land/service/traffic overlays | Not projected into WebGL; current HTML controls still mostly update the covered Canvas view |
| Region locator/bookmarks/named-place labels | Not connected to WebGL camera yet |
| Touch pinch, road drag paint, all build/network tools | Incomplete; inspector and single road tap were tested, not all tools |

`bus_depot` and `skytrain_station` appear as legacy references in some planning code but are not in the34-type registry audited here. Confirm migration ownership before adding phantom types or promising assets for them.

## Actual context available and adapter gaps

| Authoritative source | Available meaning | Current WebGL projection gap |
|---|---|---|
| `urbanDescriptor(x,y)` / cached `urbanSpatial()` | Actual density/work, land plan, agricultural context, named district/character, measured income band/per-person income, rent burden, condition, amenities and land value | Entire district context currently omitted |
| `propertyAppearance(b)` | Maintained/weathered/distressed condition; occupied/vacant or trading/closed status; funded firm scale investment | Omitted except raw condition, which art ignores |
| `b.title`, owner, municipalRehousing/relocationReserve | Actual public/private title and reserved municipal housing | Omitted |
| Actual building kind/footprint/retailCentre | Dwelling/commercial role and legal land envelope | Kind/footprint present; mall/upgrade/redevelopment role flags omitted |
| `providerVisualState(b)` | Public vs independent, real closed/connected/active/clients/capacity | Omitted |
| `brownfieldDescriptor`, project/redevelopment records | Assessment/secured/paid work/cleared/reuse stage and real progress | Omitted |
| `publicPlaceCues`, `civicGatheringCues` | Named real venues, real calendar/attendance | Omitted |
| Bridge/transit/port/vehicle pose APIs | Actual network geometry and paid cargo/service movement | Bridge identity only; other committed geometry/poses omitted |

Compute/cache these descriptors at the authoritative committed projection boundary. Do not make the renderer recompute routes, household accounts, affordability, income bands or staffing each frame. The existing `__cityVisualSnapshot`/revision/action seam can be replaced by the integration owner's committed worker contract; preserve the synchronous fallback until that exact-source integration passes.

## District art rules for the coming research matrix

- Higher/middle/lower-income neighbourhoods must use measured income/rent context. Paint colours remain varied across all bands. Lower income must not automatically produce grime, damage, missing trees or visibly neglected roofs; those require actual property condition/maintenance state.
- Suburbs and downtown follow actual density, legal lot size, building kind, access and district plan. Income alone must not enlarge a lot, add floors/capacity or connect buildings across a vacant title.
- Markets follow actual retail/customer activity, public squares and the real retail-centre flag. Financial quarters follow actual bank/office concentration and legal footprints; do not invent a rich district where the model has none.
- Public/private service forms need legible institutional identity and actual owner/provider signage. Active crew, open entrance and equipment cues require funded/connected/operating state.
- Harbour, farm and industrial modules must respect actual water/land use, work footprints, circulation and cargo/service descriptors. Decorative details are allowed; fabricated economic transactions or crews are not.

## Required cross-category acceptance

For every authored module: correct legal multi-tile envelope (including nonrectangular/title boundaries), street-facing entrances, plausible floor/vehicle/tree scale, front/rear/party-wall treatment, roof thickness/dormer proportion, contact/directional shadow, night/closed/condition state, camera edge/clipping and ray-picked identity. Test real shared-street rows, corner lots, bridge/water crossings, paid actors and expansion/removal/live refresh. Existing40 geometry tests cover five kit kinds×four orientations×attachment on one-tile fixtures; they do NOT certify every multi-tile type or all live actor states.
