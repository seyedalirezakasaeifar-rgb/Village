# Development roadmap through the overnight handoff

Target handoff: 2026-10-31 14:50 UTC (07:50 Pacific). This is a sequence of useful release cycles, not a reason to delay completed work. Preserve 7.0.2 as a stable checkpoint and keep subsequent candidates on the draft branch. Do not label intermediate candidates as completed studio-quality releases.

## Current cycle: controls, modal state, feedback and native feasibility

Finish portrait time controls and all-tab reachability; Council defer/back/focus and import draft transactions; reduce full-world scenery upload stalls. Validate supported landscape and 360×640/390×844 browser layouts. Show scenario constraints and an observe/change/review loop. Bind each QA gate and package to immutable asset hashes. Try a software-only Android emulator and record exact installation/launch/lifecycle results.

Acceptance: real clicks reach every tab and time control; topmost modal consumes Back/Escape; deferring retains correspondence without applying choices; trade changes occur only on enact; long-session save/restore preserves valid accounts. A candidate's evidence must match its delivered assets exactly.

## Economic decisions and service capacity

Investigate the service spending response with fixed-town, matched-seed spending staircases and a clear accounting model. Current inspection suggests health/school effectiveness uses the fraction of the proposed budget actually paid, not the amount purchased: a tiny fully funded allocation may receive the same service ratio as a substantial one. Verify this before changing coefficients. Model funded staffing/supplies and facility capacity, show unmet provision, and preserve explicit cash counterparties.

Compare passive, targeted investment, austerity, closed trade, restrictive credit and recovery in all starts. Separate employment, fiscal room, household resilience, public health, education and safety. Use meaningful scenario ambitions and explain bottlenecks; avoid unemployment floors, forced collapse or circular recovery gates. Validate zero spending, underfunding, facility shortages, saturation and cash conservation. Do not interpret full employment alone as an engaging scenario.

Acceptance: small spending buys proportionally limited service, spending has diminishing returns/capacity limits, unfunded promises do not provide full service, and choices produce understandable fiscal/service tradeoffs across multiple seeds without preventing recovery.

## Map and interaction polish

Review original art at phone size, zoom extremes, density changes, seasons/night, large text and reduced motion. Unify icons, status hierarchy, selection feedback, construction progress and tool cancellation. Trace vehicle/aircraft movement around junctions and runway phases; fix clipping, depth, abrupt transitions and misleading traffic feedback where observed. Reuse existing original art; avoid decorative churn.

Acceptance: readable essential controls, no clipped/hit-blocked destinations, selected properties correspond to visible parcels, construction gestures cannot accidentally place while pinching or dismissing a modal, and decorative animations respect pause/reduced motion.

## Saves, recovery and long sessions

Exercise old fixtures, legacy migration, corrupted/truncated saves, invalid enums/IDs/ownership, denied storage, interrupted import, backup rotation and exact deterministic continuation. Test native document picker, background/resume, Back and update using the same signer if the emulator supports them. Retain private signing material outside source/deliverables.

Acceptance: invalid archives leave the live town unchanged, successful restore preserves balances/ownership/cargo, backup recovery is intelligible, and lifecycle suspension saves without advancing offscreen time unexpectedly. Report unsupported native stages precisely.

## Performance and final release gate

Profile individual render stages, scene changes, camera movement and UI latency in large towns. Run one meaningful long playthrough per scenario plus targeted multi-seed stress; inspect memory/cache growth. Compare at fixed density/quality, and run timing experiments without competing emulator/build workloads.

Freeze version and assets, then run the required sequential browser/economy/archive gates; build/sign, independently verify every packaged asset, and smoke the exact APK. Capture final screenshots and machine-readable source/evidence hashes. Deliver standalone APK, exact source, QA/changelog and screenshots in Library, plus the draft PR. Leave no stale results presented as final evidence.

Final acceptance: documented evidence supports the gameplay loop, understandable consequences, resilient saves, accessible controls and bounded high-speed workload. State remaining hardware, balance and performance limitations; do not claim perfection or physical-device performance from software emulation.
