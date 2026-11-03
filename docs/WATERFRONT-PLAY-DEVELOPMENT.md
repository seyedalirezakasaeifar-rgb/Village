# Survey navigation, working voyages and long-run accounting

Development checkpoint, not the final Android delivery. Source/evidence identities are recorded in `docs/previews/waterfront-play/evidence.json`.

## A complete mayoral journey

The browser journey uses normal buttons, touch placement, mouse road painting, the Services budget shortcut and actual RAF simulation. Read-only instrumentation chooses reproducible coordinates; it does not construct buildings or transfer money.

The mayor previews and purchases Lower River Reach, opens an isolated fishery, paints a connection to the existing town, and adds a wharf, home, clinic and grocer. Crews cannot attend the isolated business. After the road connects, real recruitment, fishing, freight and utility purchases begin. The test then enacts a medical allocation of $170/day through the operating-budget shortcut and waits for regional recruitment. In the recorded session, care coverage improves from 40.9% to 98.9%; it is not instantly granted by constructing a clinic.

The new fishery employs two people and the new wharf one. The latter handles roughly 37 units/day and loses about $29/day: a lightly used second port is not a cash machine. Its inspector now reports utilization and the cargo needed to cover actual daily costs. The new household has a utility connection. The archive survives a round trip and money/goods remain conserved.

## Legible land and placement

Regional overview uses numbered pins and an accessible district selector, with an explicit Review action. All five pins fit the actual canvas and avoid the survey toolbar at 844×390, 568×320 and 320×568. Selection previews a district; Review opens its deed. Back/Escape returns from the survey, and choosing a construction tool leaves survey mode so later property taps work normally.

The map can zoom far enough out to fit the genuine 80×80 region on a small phone. The bottom survey toolbar reserves its own space in overview and district framing. Numbered markers do not overlap; tapping nearby markers chooses the nearest one.

Waterfront hover and rejection feedback now distinguish reserved/occupied land, missing road, missing fishing water, enclosed lake versus regional river outlet, isolation and insufficient treasury. Invalid placement spends nothing. Native Back's JavaScript contract now dismisses an active construction tool and flushes a road gesture; drawers and dialogs retain priority. Actual Android input still needs device/emulator confirmation.

## Original living water

Paid cargo keeps a stable vessel and load while new orders arrive. Rounded corners stay inside navigable water cells. A barge pauses and turns over 1.2 seconds at its destination, then returns empty. A complete visual voyage is tested for continuous position/heading, bounded movement, pause stability and an unchanged economic archive.

Boat inspection opens its actual business accounts and highlights the connected water route. Surface glints, working pier dollies, fishing nets, hull movement and active-only wakes add life within existing quality budgets. Reduced motion stops these effects. Closed ports do not start new work, and their next-day cargo, receipts and capacity counters reset to zero; reopening is tested.

## The extended run found a real numerical issue

The earlier candidate's requested 45-minute browser run reached day 25,167 but failed its stricter commodity threshold after 44 minutes: residual 0.001052 units. The town remained structurally valid; monetary drift was $0.000178. Named caches stayed bounded. This was not reported as a passed soak.

Commodity counters now retain floating-point carry and use compensated balance reporting. No stock, cash, price, wage or policy coefficient is adjusted to balance the books. Carry is optional for legacy saves and validated against finite roundoff bounds; historical residuals are not reset.

A matched 25,166-day comparison replaces only the counter-addition function in the reference variant. Naive accumulation leaves 0.001182945 units of residual; the compensated version leaves 0.000000009390. The complete physical-economy fingerprints match exactly. The million-increment analytical test also passes, and malformed carry/counters are rejected atomically. Evaluated source hashes identify both variants.

All 36 candidate gates pass on the frozen current assets. A separate 2,000-resident/64× browser measurement records warm draw p95/p99 of 36.2/45.3ms, tick p95 16.0ms and 63.3× effective speed. These remain host-browser measurements, not native Android FPS. The final release still requires exact-source packaging and the remaining native/transfer acceptance work.
