# Larger region and working water — development checkpoint

This is a source development checkpoint for 7.1.0, not a certified Android play session or a final release.

## Mayor-purchased expansion

The simulation now has a real 80 × 80 regional grid. The original 56 × 56 town keeps all its existing land, buildings, streets, private titles and coordinates. Five substantial outer districts offer 2,860 additional regional tiles, including actual new riverbank, upland and lake frontage. An outer verge remains regional land. The mayor must purchase a district deed before building, reserving agricultural land, private road development or occupying a building footprint there.

Public Works opens with **Expand the borough**, a folded land office. It provides a regional plan, district dimensions, land/water survey, price, treasury shortfall, adjacency requirement, map preview and an explicit purchase/cancel dialog. High Common requires an adjoining purchased district. A repeated purchase cannot spend twice. Cash goes to the regional land authority, with a permanent deed, public record and capital outlay. Existing private owners are not dispossessed.

A deed buys development rights, not an instant neighbourhood. Roads still cost money. Firms need a connected route, real workers, inputs, demand and capital. Utility payments require a connection to the regional grid. Clinics and schools retain physical catchments and funded staffing. New territory can therefore be useful without magically supplying all services.

Archive schema 6 migrates old 56 × 56 saves by remapping tile indices to the new stride. The original tiles, coordinates, footprints, streets, fields, projects, airfield, road wear and delivery/traffic paths are retained. Original rights remain owned; the five new outer districts start unpurchased. Invalid deeds and structures or roads outside chartered land are rejected before replacing the running town.

## Productive waterfront

**Waterfront** in Public Works contains two original businesses:

- **River Fishery:** actual attending crews produce food for the existing grocery/export economy. Fisheries sharing a water component share its finite catch capacity (1.2 food units per water tile daily). A small decorative puddle is not a fishing site. Lakes support fishing; equipment cannot manufacture more fish than the shared catch limit.
- **River Cargo Wharf:** requires shoreline, a road and a continuous water route to the north or south regional boundary. An enclosed lake has no cargo outlet. Each attending worker can handle 600 cargo units daily; the wharf earns $0.10 per unit actually loaded. No crews, no route or no orders means no handling income.

Exporters compare a regional road haulage quote against road collection plus river carriage. The cheapest available route receives the order, with shared finite wharf capacity and road fallback when it fills. Each freight fee is deducted from the actual seller's export receipts. Wharf income and the regional carrier's residual are separate payments; neither invents cash. Exporters rotate deterministically to avoid permanently favouring one firm when loading capacity is scarce.

Export cargo becomes the regional buyer's property on collection, as it already did in the regional market. Bounded manifests record that paid journey and drive visible barge activity. They are not counted again as town inventory. River imports and navigable canal construction are not implemented in this checkpoint. Local road delivery inventories retain their existing delivery delays.

New settlements inherit a funded private landing and fishery on Landing Lane. Their working capital and construction have actual regional counterparties before opening accounts. Imported old towns receive no free new firms or roads; their mayor can develop a waterfront through Public Works.

## Original visual work

Fisheries and cargo wharves have distinct timber sheds, roofing, crates, net gear and a cargo crane. Piers follow actual adjacent water. Original fishing craft and loaded/empty-return barges travel on connected water paths, with heading, hull, cargo, wake and bridge occlusion. Wharf workers carry actual loading activity; closed or unstaffed businesses do not start new work. A vessel already carrying a paid load completes its continuous outward and empty-return journey; new manifests do not teleport it or change its load at sea. Boats are visual samples of paid voyages and actual fishing, rather than a second economic simulation.

At most 32 sampled vessels are retained, with smaller visible quality budgets. The animation uses the separate visual clock, freezes while paused, never consumes the economic RNG, and is bounded by quality/speed tiers. Reduced motion and low quality omit boats. At 64× the terrain backing store has a 2.2 million pixel budget; buildings and labels retain their separate composition. The ordinary detailed ground layer remains capped at 9 million pixels despite the larger world.

## Acceptance evidence

See the tests and the exact-source gate manifest in the local development report directory. Reports are generated evidence and are not committed saves or private logs.

- `test_annexation.py`: genuinely unavailable/available new land, road/building permission, price and adjacency, insufficient funds, stale quote, cancel/confirm, duplicate purchase, cash conservation, deed persistence, invalid-save rollback and complete legacy grid migration.
- `test_annexation_networks.py`: buys Lower River Reach, builds an isolated shore business with no utility link or crew, pays for 23 road tiles to connect it, recruits three actual workers, and lands 1,395 food units over 35 days. Cash drift is below one millionth of a dollar and goods balance remains valid.
- `test_waterfront_mobile.py`: 44px land-office and waterfront controls, reachability, confirmation/cancel and construction categories at 320 × 568, 568 × 320 and 844 × 390.
- `test_waterfront.py`: continuous and pause-stable boat position across changing manifests, actual food output, shared catch, finite cargo capacity, competitive road/river quotes, paid handling, closed/unstaffed ports, inland/outlet restrictions, manifest round trip and rejection, bounded boats, render/economic independence and a 365-day accounting run. One matched sale receives a $0.1435/unit river quote versus $0.244 road haulage; its 20 units pay $2 to the wharf with no money leak.
- The synthetic 2,000-resident browser test uses the saved grid size and live camera geometry instead of a hardcoded old stride. It records founding/warmup timings separately from its measured live RAF interval. Native Android FPS remains unmeasured.

Screenshots in `docs/previews/working-river` are original Chromium pixels at 844 × 390. The three river images sample the same paused economic state at different visual-clock positions to show route continuity; the land images show the same outer tract before and after its deed. These are not Android-device screenshots.

## Remaining limitations

The map and ecology are simplified game models, not real-world calibrated geography or fisheries science. The finite 80 × 80 region is intentional. Annexation does not create a road bridge or a canal. Cargo manifests visualize regional-owned exports, not a new import supply chain. Software-only Android emulator UI remains unreliable in this executor; actual system picker, touch, Back and lifecycle checks still require a usable device/emulator. At regional-overview zoom, the Orchard Downs and County Ridge labels currently overlap; the focused district previews are legible. This needs a further hierarchy pass. Tight sprite envelopes now reduce the sampled atlas pixel allocation by 74.6%, with exact reference-pixel tests and a 48 MiB LRU storage limit. Calculated pixel storage is not total process RAM. Broad browser gates, APK assembly/signing and final package identity must be run on the final frozen candidate before handoff.
