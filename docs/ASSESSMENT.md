# TownLedger: architectural and game-design assessment

Based on the supplied 5.6 source, two supplied gameplay captures, the older independent Godot/C++ project, and fresh desktop browser runs. This is a focused engineering assessment, not an exhaustive audit.

## What the baseline actually was

The current game was a WebView adaptation. Its renderer, economy, UI, banking and persistence shared a roughly 461 KB script containing embedded art. The older Godot/C++ project was a different game with a useful engine-independent simulation boundary. It was not the source of the supplied APK.

Fresh baseline play exercised 1×, 8× and 64×, a two-year economic run, map navigation and a captured town. The two-year sample completed autonomous housing, businesses and road extensions and conserved cash to a small floating-point tolerance. A short 1280×720 draw benchmark measured approximately 0.96 ms per CPU draw on this host. None of this measured Android FPS.

## Problems with concrete evidence

| Problem | Evidence / reproduction | Result in 6.0 |
| --- | --- | --- |
| Release identity was inconsistent | Settings hardcoded Harvest & Hearth 5.5 inside the supplied 5.6 release | Runtime identity generated from release.json; Java APK package metadata checked |
| Development lacked an explicit investor budget | privateContract reported the whole contract but transferred only a local share from the aggregate regional pool | Investor equity subscriptions, full contract disbursement and named counterparties |
| Congestion could erase trips | trafficUpdate removed vehicles when age exceeded 115 seconds or waiting exceeded eight seconds | Ordinary congestion no longer removes vehicles; actual trip progress tested |
| Replays depended on wall-clock activity | Economic decisions used Math.random, including shared draws with traffic spawning | Seeded economic stream, independent visual stream, serialized RNG; exact continuation tested |
| Instant stock transfers obscured freight | trade credited buyer inventory immediately | Paid goods remain in cargo accounts until a connected delivery arrives |
| Wholesale trading could circulate groceries indefinitely | After adding real travel time, retailers repeatedly bought other retailers' food | Wholesale source selection restricted to producers and depots; regression and stock conservation checks |
| A reopened firm could acquire NaN input stocks | Empty stock objects combined with subtraction from undefined | Normalized inventory arithmetic and finite/nonnegative stock validation |
| Construction advanced solely with elapsed days | Projects decremented remaining days without checking crews or inputs | Local crews and paid timber/stone deliveries, or limited prepaid external crews |
| Save validation changed some replay fields | Migration inserted default development counters missing from fresh towns | Canonical initialization and exact post-load continuation |
| Long-run demographic replacement was weak | Early long runs aged the original population toward decline | Birth decisions, independent household formation, explicit vacant-home tenancy; estates retain their balances |
| Visuals were oversized and inconsistent | Supplied screenshots and sprite scale versus tile geometry | Original projection-consistent architecture, terrain, trees, seasons, lighting and smaller UI |
| APK maintenance was unusually fragile | Python manually emitted Dalvik bytecode and binary Android metadata | Real Java compilation, SDK asset packaging, ZIP alignment and apksigner verification |

## Chosen approach

Retain and substantially rebuild the current gameplay baseline. Source is organized into 20 ordered modules covering finance, property, markets, goods accounts, development, construction, services, simulation timing, rendering, traffic, government and archives. The build assembles these into one offline script for distribution. The current saves and most existing rules remain recognizable, allowing a direct 5.6 migration.

The native reference compiled and passed its 14 core scenarios and 113,938 assertions in this environment. Its headless benchmark was also runnable. Godot, its export templates and the complete native Android toolchain were not present. Its feature set differs materially from 5.6. A native port would require actual economic feature migration, visual work, save conversion and device comparison. It was not treated as a ready-made substitute.

The revised Java host uses Android platform APIs and no third-party application runtime dependency. The build uses javac, dx or d8, aapt, zipalign and apksigner rather than manually generated executable code. The validated fallback toolchain is the distro AOSP toolchain with an API-23 compilation jar and API-36 target metadata; it is not a validated latest-AGP/Gradle configuration.

## Design and observable behavior

Normal play is governmental. Households, merchants, landlords, builders, banks and infrastructure investors act without manual building. Policies are proposed and explicitly enacted; recorded observations retain the before state and the first review at or after 180 days. Comparisons are observations, not claims of scientific causality.

Private housing proposals compare estimated operating yield against a funding hurdle. Land has a recorded owner; acquisitions pay the seller. Redevelopment preserves residents, records prepaid temporary accommodation, suspends their ordinary rent during works and restores their tenancy on completion. New facilities occupy their actual plots. Construction can stall without material deliveries or crew capacity.

The commodity ledger separately counts opening stocks, production, transformation/consumption, imports, exports and goods in transit. Wholesale prices adjust with inventory coverage and regional demand. This remains a stylized economy, not a calibrated general-equilibrium model.

Service budgets authorize paid municipal operations. When population exceeds service capacity and funds cover construction plus a reserve, the council procures additional facilities without requiring the player to paint individual schools and clinics.

Council correspondence expires into an archive after 120 days with existing policy retained. Routine petitions and elections do not force a modal. Explicitly opening a decision or restarting a town remains an intentional modal interaction.

## Important architectural limits

The modules still share one authoritative state in a single closure. This is not the handoff's ideal independent worker/native core with immutable production UI snapshots. Fixed daily steps are synchronous, and an expensive individual step can still delay a frame. The scheduler budgets work and lowers its admitted rate rather than discarding economic events.

Money uses floating-point amounts with explicit tolerances rather than integer cents. Investment records are explicit transfers; the searchable log is not a complete double-entry record of every historical wage, tax and purchase. The regional account deliberately aggregates external suppliers, investors and customers.

Traffic is a bounded visible sample of actual commuters and paid cargo. Cargo delivery is authoritative on deterministic daily routes, not on whether a sampled visual truck has crossed every screen pixel. The rail overlay represents underground connections, not a surface railway parcel network. Aircraft motion is an operating-service illustration, not an individual ticketed-flight scheduler.

The art is original code-native pixel illustration. Captures establish its actual appearance; they do not establish premium commercial art quality or replace external playtesting.

Physical Android installation, native document-picker behavior, lifecycle reliability, sustained FPS, thermals and battery use remain untested. The source and signed APK are deliverable, but those acceptance gates cannot be honestly marked passed without a device.
