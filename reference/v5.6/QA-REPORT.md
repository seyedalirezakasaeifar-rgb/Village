# TownLedger 5.6 — Rebuild and QA report

## Audit objectives

The user requested a substantial visual and gameplay overhaul while keeping the game primarily autonomous: richer original pixel art, visible growth, differentiated buildings, more understandable economy, enjoyable governmental decision-making, and improved performance. Rather than replacing the economic model with decorative animations, this release enhances the presentation of the existing household, business, banking, housing and municipal policy systems.

## Implemented changes

**Original sprite overhaul:** sixteen individual cottage renderings with roof structures, different colors, windows, porch or garden elements; distinctly illustrated shops, civic and industrial buildings; eight tree silhouettes adapted for each of three seasonal groups; enlarged images for farmstead, station, airport, factory, high-rise, warehouse, school and college. Sprite creation tools and PNGs are in the source archive. Sprites are cached and use nearest-neighbor drawing for crisp pixel edges.

**World composition:** initial homes distributed into multiple road-accessible residential clusters while preserving full household records; more varied landscape palette instead of harsh grass checkerboard; live pedestrian figures only on connected streets, with 24-actor cap and on-screen culling. Existing real multi-tile reservations, crop plots and animated airport/metro assets remain.

**Economy visibility:** the new Economy panel draws values from actual resident and firm records, sector profitability, jobs, housing capacity, open construction projects, bank deposits, outstanding debt and closures. A compact, non-blocking market pulse is updated as the simulation advances; notable macro shifts produce occasional stories. Numeric policy 'cabinet' presets are staged rather than silently enacted.

**Interaction:** warm pixel-compatible council interface, readable map overlay, retains zoom/pan, save and inspect controls. Routine policy petitions and elections remain accessible without interrupting time acceleration.

## Automated test evidence

The following completed test cases passed on the build's source and game code:

- `test_rework.py`: new Economy screen navigation, display of real firm/bank statistics, non-blocking 365-day sim and election handling, actual staged policy proposal and explicit enactment.
- `test_financial_endurance.py`: four scenarios over 10 simulated years, with 69–81 company insolvencies per scenario, bank credit, company turnover, and cash conservation to better than $0.00002 in each tested run. No bank failures occurred naturally in these four runs; a dedicated failure regression exists separately.
- `test_longrun.py`: four scenarios over five simulated years, including stable live population, employment references and elections.
- `test_road_integrity.py`: 20 road-network simulations, no road or financial integrity errors, observed host benchmark about 0.91 ms per draw at the script's test viewport.
- `test_landmark_randomized.py`: forty independent randomized town layouts for land reservations and no overlap during growth.
- `test_2000_residents.py`: 2,000 synthetic residents, 120 simulated days, ~27.67 ms per simulated day on testing host. This is not device FPS, and 64x real-time simulation in large towns can still lag.
- `test_market_city.py`: autonomous private housing, business and road investments, and sensitivity of growth to stricter zoning.
- `test_finance.py`: lending, repayment, bank receivership, company liquidation, depositor handling, density reversal, ledger consistency.
- `test_landmark_geometry.py`: land footprints, airport and metro animation and road exclusions.
- `test_policy.py`, `test_audit_regressions.py`, `test_upgrade_compat.py`: policy response, malformed save protections, and compatibility migration. Upgrade test started from a 5.3 save, not a physical-phone 5.5 save.
- `test_browser.py`: basic browser rendering and navigation.
- `test_controls.py`: its assertions and browser-console check reached completion and reported no errors, but the harness hung at shutdown on one run, so do not count this as a cleanly terminated full test run.

APK version/package audit: `tests/verify_package.py` checked **this release** (versionCode 11, versionName 5.6.0, label `TownLedger: The Living Borough`, min SDK 24, package `org.townledger.android`, valid DEX and manifest, zip entries and v2 protected content/signature). The signing certificate file SHA-256 matches the version 5.5 certificate file; signature checks do not constitute an install test. APK SHA-256 `2d6a2faf153ad847289c2788913e1e1bbf613ea90150b9de685ce374e6bdc92c`.

## Not verified and remaining issues

- No physical Android device was available to measure frame rate, thermal performance, memory or prolonged app behavior.
- A large-screen screenshot and Android-sized screenshots were reviewed, but this is not professional playtesting or expert art direction. It is a significant visual iteration, not an exact replica of the craft of Stardew Valley.
- Some graphics are still procedurally generated, and the road/terrain geometry remains based on the original canvas system.
- The simulation is an economic sandbox, not an empirically calibrated dynamic general-equilibrium model. Sector productivity, wages, land prices, interest rates and institutions remain stylized and subject to balancing.
- Natural bank failures were not observed in the four ten-year default scenarios; the failure mechanism is exercised by forced stress tests.
- Existing public works mode allows optional manual construction even though the intended experience prioritizes autonomous development.
- A user who has not exported an old save should back up through Options before attempting to update.

## Build outputs

- `TownLedger-The-Living-Borough-5.6.apk` — signed Android application.
- `TownLedger-The-Living-Borough-5.6-source.zip` — full working source, tests, build program and original artwork generation scripts; excludes the private signing key.
- `TownLedger-The-Living-Borough-5.6-preview.png` — screenshot from the running game renderer, not concept art.
