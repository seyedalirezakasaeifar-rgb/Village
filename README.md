# TownLedger 7.0.1 — The Working City

An offline government and town-economy game. This release rebuilds the operating model, the starting towns, monetary controls, road generation, animation and interface palette.

## Install

Source release metadata is 7.0.1 (version code 15, save schema 5). **No 7.0.1 APK was built or device-tested in this environment.** The supplied 7.0.0 APK is a separate baseline (version code 14); it is not this source release. An in-place update requires the original private signing keystore, which is not included. If you only have an APK signed with a different key, Android will reject it as an update; export your town first, then reinstall only after obtaining a compatible signed build. Do not uninstall until you have verified your archive.

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
