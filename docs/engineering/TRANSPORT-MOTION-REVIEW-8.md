# Transport motion review

The close-zoom review found an abrupt facing change when a funded bus or elevated shuttle reversed at either endpoint. The vehicle pose changed its direction sign on the exact endpoint phase; the art layer already eased ordinary track corners but left this reversal sharp. `transitTerminalHeading` now eases a half turn across a short terminal window while keeping the existing route, position, service, and cargo state intact.

The transit-art regression samples both endpoints of every real fixture route at 0.01 phase intervals. Maximum successive heading change is 5.62 degrees. It also verifies actual funded bus and elevated service, visual-state immutability, zoom LOD, reduced motion, stable paused pixels, a real camera pan, and that resuming advances the animation clock by 0.35 seconds. Current source bundle SHA-256: `5202ab97b2dba28cde95134f67378afca68786d8d0f212931477b88d87f0e814`.

The freight fixture advanced a real reviewed import through its ordinary settlement steps, then sampled its existing subday render progress from 2% through 98% during the inbound water leg. The full order completed with no browser errors. The images show the vessel’s approach and the dock at the route end. No extra simulation steps, trade settlements, or balance changes occurred between subday samples.

Validation passed with `tests/test_transit_art.py`, `tests/test_paid_port_art.py`, `tests/test_port_freight.py`, and `tests/test_transit_network.py`. The Playwright viewport was 844×390 for the vessel sequence, and 844×520 for transit cycles, the terminal turn, pause/resume, and pan. These checks ran in host Chromium; Android WebView was not available for this review.

Local review captures are in `/tmp/transport-full-cycle/`: `paid-boat-arrival.png`, `rail-terminal-after.png`, and the bus/elevated full-cycle contact sheets. They are review evidence only and are not part of the app bundle.
