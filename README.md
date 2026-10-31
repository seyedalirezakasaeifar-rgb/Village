# TownLedger 7.1.0 development — The Working City

Current source extends the signed 7.0.5 checkpoint. These changes have not yet been packaged as a new release:

- [Local services, staffing and training](docs/LOCAL-SERVICE-DEVELOPMENT.md)
- [Credit, household budgets and physical markets](docs/CREDIT-AND-MARKETS-DEVELOPMENT.md)
- [Council programmes and original workday animation](docs/COUNCIL-PROGRAMME-DEVELOPMENT.md)
- [Native archives, lifecycle and older WebView](docs/NATIVE-ARCHIVE-DEVELOPMENT.md)
- [Portable seeds and clearer phone controls](docs/MAP-AND-SEEDS-DEVELOPMENT.md)
- [Mayor-purchased districts and productive waterfront](docs/REGION-AND-WATERFRONT-DEVELOPMENT.md)

An offline government and town-economy game. This release rebuilds the operating model, the starting towns, monetary controls, road generation, animation and interface palette.

## Current 7.1.0 source

The 80 × 80 region preserves the original town and offers five substantial outer districts for explicit mayoral purchase. Public Works previews costs and boundaries before a deed is acquired. Fisheries produce real food within shared water limits; staffed river wharves earn paid freight income when their routes beat regional road haulage. Original docks, working crews, fishing craft and cargo barges follow those businesses. Current archives use schema 6 and remap legacy 56 × 56 maps without taking their original property rights. This source checkpoint has not yet been packaged as a new release.

## Earlier signed checkpoint

Version 7.0.5 (code 19, save schema 5) has a signed development APK built with the official Android SDK. Package assets, signature, DEX integrity and alignment were verified. Android installation and device gameplay have not been run. The new development signer differs from the older baseline; export and verify your town backup before uninstalling an older installation if Android refuses the update. The original private signing key is not included.

This development slice makes health and school allocations purchase capacity-limited services, reports operating bottlenecks, and introduces original terrain/frontage/lighting/activity layers. See [phase notes](docs/MATERIALS-AND-JOURNEYS-7.0.5.md). It also improves large-town rendering at 64×, zoom-dependent street labels, high-density screen alignment, construction feedback and archive validation. See [QA and changes](docs/QA-7.0.5.md) for measurements and remaining limitations.

New towns use a connected hierarchy of named through roads, collectors and local streets. Existing saves retain their buildings, roads and residents. Their economic rules migrate to schema 5. Keep an old export if you want to retain the prior simulation rules; older builds reject new schema-5 archives.

## Play

Drag to pan, pinch to zoom, tap a property to inspect it. Set policies, then enact the proposal. **Policy interest rate** is under Monetary policy and credit; Banks and Economy include shortcuts. Quotes adjust gradually, variable loans reprice monthly, and contracts marked fixed retain their agreed rate. Legacy loans without a rate-type field migrate as fixed contracts.

The government also sets a treasury-funded retirement pension. An ageing population changes the cost. Budgets remain constrained by cash and credit. Public Works is optional; firms and investors develop the town themselves. Seasons and weather remain off by default.

## The economic rebuild

- Inventory purchases reduce cash, with material costs recognized as goods are sold. Operating statements separate sales, goods sold, payroll, other costs, tax and inventory purchases.
- Output requires workers and inputs. Order forecasts, inventories, prices, transport and actual buying power limit sales. Hiring responds to sustained sales; unpaid workers leave.
- Firms retain working and debt reserves, then distribute surplus to real shareholders. This includes regional owners of founding firms. Property earnings and estates also circulate through actual counterparties.
- Houses do not automatically create unemployed residents. Completed homes can remain vacant; migration needs employment opportunities. Retirement releases jobs and pension transfers are funded.
- Starting populations and staffing are reauthored. Market Cross has an explicit regional export specialization and a normal mix of ages rather than hundreds of additional working-age residents without a sustainable employment base.
- Interest policy affects bank quotes, variable debt, saving/consumption preferences and investment return hurdles. Lower taxes and rates cannot create missing customers, materials or skill by decree.

## Other work

One high-contrast UI palette replaces conflicting legacy themes; drawers have more usable height; rate controls retain quarter-point precision. Roads use named connected blocks and readable hierarchy. Pedestrians walk, vehicles follow road tangents, and a recognizable twin turboprop taxis, takes off, climbs, approaches and lands on a cleared, marked runway. Aviation uses a 19-seat service and staffing/fuel costs.

Escape now dismisses the open drawer or the topmost temporary Help/archive flow, matching Android Back. Drawer and dialog dismissal restore keyboard focus to their launcher; the Help/archive dialog is labeled and keeps Tab focus within the modal, and temporary archive screens restore the tutorial for its next opening.

## Build and evidence

Run `python tools/assemble.py`; build with `python build_apk.py` and the tools in [docs/BUILD.md](docs/BUILD.md). Retain the original signer for update compatibility; private keys and SDK binaries are excluded from the source archive. The source release metadata does not mean a signed APK is available.

Read [QA-REPORT-7.0.md](QA-REPORT-7.0.md), [docs/ECONOMY-7.0.md](docs/ECONOMY-7.0.md) and [docs/SAVES.md](docs/SAVES.md). Current evidence is in `reports/v7.0/`. Source modules share a closure and daily processing is synchronous; this is not a new native engine.

This is an original stylized economic model, not a calibrated forecast of a real country. Physical Android performance, system file pickers, thermals and sustained memory behaviour still require device testing. No claim of perfection, exhaustive bug removal or commercial art parity is made.
