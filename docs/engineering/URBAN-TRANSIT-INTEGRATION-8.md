# Integrated urban atlas, paid transit and city rendering

Development checkpoint following `b998856`. The authoritative source and current acceptance results are identified in `reports/integration/8-urban-transit.json`; upstream preview receipts remain historical branch evidence, with their own hashes.

## Combined systems

Integrated urban `f8f3e73` + `42e1f69`; transit `eb2e88c` + `98a5dc7` + `d654f70`; transit art `4dbf48d`; urban art `d7a9f97`. Preparatory duplicate graphics commits were not applied. Private-service construction retains its real escrow, planned staff and offered wage. Contract dispatch still receives actual fresh output before ordinary sales. Transit operations run after household daily fields reset and before employer attendance/payroll, keeping drivers, fares and household budgets accountable.

The 128-square atlas supports 21 adjoining, paid deeds. Land assembly and municipal replacement housing preserve household identities, actual accommodation, compensation, severance, credit/cargo estates and future service costs. Shopping centres remain funded six-tile businesses with real inventories and customers. Municipal bus and elevated metro networks have paid infrastructure, vehicles, qualified staff, fares, capacity and operating risk; passenger paths never become freight roads or free service-provider coverage.

Legacy atlas migration uses `candidate.transit = remapTransitState(candidate.transit, tileMapper)` on the cloned candidate. Track/path/bus-stop tile indices change; institutional IDs, depot indices, stop offsets, settled fares and staff do not. Purchases on the final atlas do not reindex live arrays at all.

## Integration defects caught

A malformed legacy transit path threw during pre-validation normalization. The old catch handler then called the normal traffic-reset routine on the *running* town. Import rejection now leaves live simulation and visual transport untouched. Adoption keeps a rollback snapshot of transport, gates, clocks and random streams; an injected post-validation initialization failure also restores the original town. Both rejection stages are exercised by the joint HTTP-origin test.

The first full-ownership network stress case failed the existing <50 ms draw-P95 gate: 69.3 ms. Profiling identified repeated terrain repaints, not passenger vehicle sampling. Changed terrain is now replayed under pixel-aligned projected chunk clips; unchanged atlas pixels remain retained. Numeric chunk keys avoid repeated per-tile string allocation. This adds a bounded 32 KiB tile-state cache rather than a second world-sized texture. Style/town/quality changes still repaint the whole ground.

A separate 0.2-zoom case exposed additional overview work. Subpixel street furniture and cast shadows are omitted, and distant forest canopies use simple original silhouettes. Buildings, guideways, economic agents and all authoritative simulations remain intact. Individual vehicles/people retain their existing distant-zoom early exits. Neither camera position nor detail level advances or settles the economy.

## Acceptance scope

Joint tests preserve live owned cargo and paid bus/rail accounts through all 21 deeds and 56/80-grid imports. An active routed depot cannot be cleared. Sixty normal settlement days retain passenger fares and cash/goods conservation. Separate real-control rehousing tests commission a vacant home, move the same family, build a replacement clinic, and continue for 120 days; farm renewal preserves its 15 crop plots, inventory and workforce. Existing school acquisition/closure remains a paid private-property transaction.

The retained-ground regression compares localized crop/street/class edits against a complete repaint at normal and fast quality. Chromium full redraw versus itself also differs at some antialiased edges; the explicit bound is <0.05% channels differing by more than 2/255, maximum 12/255. Raw differing-channel counts and self-comparison are retained. This is a bounded raster tolerance, not a claim of byte-identical Canvas output.

Dense live acceptance authors a conserved 2,000-resident stress town, purchases all deeds, pays for an eastern road corridor, relocates 29 existing test households, and builds local/outer buses plus elevated metro. Driver candidates come from existing qualified unemployed residents. The fixture transfers existing regional cash to the treasury for authoring; it is not an unassisted gameplay or balance proof. It records operating routes and actual paid rides, near and distant zoom, live RAF tails, simulation throughput and UI response. A separate 48-route complete-game case and 2,000-rider exact-equivalence/capacity fixtures cover the larger passenger-routing workload.

Screenshots use the real supported HTTP asset origin so opaque-page storage warnings do not obscure the map. The network and retail artwork have depth, pause, culling and economic-state independence tests. Core replay, migration, malformed-save atomicity, freight books, private services, contract feasibility, LOD and older-WebView API checks are included. Results remain host Chromium evidence; cold-cache hitches and physical Android GPU/thermal/lifecycle testing are separate limitations. This checkpoint is not final quality acceptance or a release APK.

## Accepted checkpoint measurements

Final source SHA-256: `293fe306631099dfaacdd37e724d4c6e3b89991f56a1e15c50f872606f662c90`.

Fifteen targeted/core invocations pass on this frozen bundle, followed by three isolated live performance checks. At 2,000 residents and requested64×:

| Host case | Draw P95 | RAF P99 | Actual paid service |
|---|---:|---:|---|
| All21deeds, three routes, zoom0.95 | 29.8ms | See receipt | Three operating routes; real fare receipts |
| All21deeds, three routes, zoom0.2 | 44.0ms | 200.0ms | Three operating routes; six rides at final sample |
| 48funded bus routes, complete city | 26.2ms | 116.6ms | 96unique drivers;22rides at final sample |

The48-route case advances307days in8.11seconds, about62.4× measured simulation rate. The all-owned atlas cases also satisfy the unchanged <50ms draw-P95, >=40× effective speed, <500ms RAF-P99 and <250ms panel-next-frame gates. These gates permit occasional hitches; they do not assert60FPS or physical-device smoothness. Cold rebuilding and 64× tail latency remain useful later profiling targets.

Warm profiling also caught a graphics override that reinstated detailed cast shadows after the original LOD guard. The authoritative diorama shadow function now performs the distant-zoom early exit, and the LOD regression passes a deliberately unreadable item collection to prove no hidden iteration occurs. Overview ground sampling follows its pixel budget independently of building/guideway sprites.
