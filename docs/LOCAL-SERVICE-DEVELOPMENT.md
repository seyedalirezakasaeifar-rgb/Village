# Local access, qualified staffing and delayed training

Unpackaged development after the7.0.5 checkpoint. No new APK or release version was created. The prior7.0.5 immutable build remains a separate checkpoint; a new full frozen release gate is required before delivery.

## What players can do

Services starts with medical and school provision, the limiting factor, an access map and a direct operating-budget shortcut. Detailed operating and qualification figures are expandable. Access maps distinguish full/partial/unserved physical places with color and symbols. Household inspection gives road distance, reachable places and the latest funded coverage.

Connect a cut-off neighborhood, add a closer facility where distance or capacity binds, fund additional operating work, wait for a dated regional recruitment review, or sustain adult training. Increasing a budget cannot create a missing road, building or qualified employee immediately. The interface distinguishes an insufficient allocation from a genuine recruitment delay.

## Spatial and workforce model

Medical catchments are60 road segments and school catchments40, explicit gameplay planning limits rather than real travel-time forecasts. Facility capacities are shared across reachable households. Proportional allocation gives shared shortages a fair starting distribution; residual flow reassigns overlapping places to maximize usable provision. A place cannot be counted twice. Derived geometry is cached by town, road network, facility IDs and resident/home rosters.

Local medical/support staff require skill70/100, school staff55/100, health60+, adulthood, a reachable facility and available public work time. These are abstract qualification proxies, not medical credentials. Existing private jobs are excluded. Actual public income is capped at the public wage; a paid, substantial public assignment is retained for the next workday instead of being counted as both public and private employment. Tiny partial public payments do not permanently exclude a resident from private hiring.

Regional contracted capacity supplies a recovery path without local qualifications. Founding/migrated operating arrangements are inherited once; later expansion recruits on a30-day schedule shown in Services. Retargeting does not continually restart the countdown. No service is produced without the funded payment; existing payroll/tax and regional purchase counterparties retain conservation.

Each school offers two adult-training places. A term requires120 equivalent funded teaching days and raises general skill10 points. Progress uses the trainee household’s local funded access; disconnected or unfunded courses pause, and a same-day guard prevents duplicate credit. Courses that exceed current place capacity wait. Qualification does not promise a job. Regional school staffing allows training to recover without already having local teachers.

Individual skill/health effects now use local funded coverage, with continuous responses replacing the earlier global50% health/40% learning thresholds. Saved recruitment, course and role data are validated atomically. Derived provision is recomputed after restore; legitimate recruitment dates and course progress persist.

## Evidence

Frozen development game.js SHA256: `76a48a9c41aefdd18ce2a31f0d36aedad00bf2b4c20e419d769d89f0abe304dd`. Targeted tests cover shared-capacity overlap/reordering, proportional shortages, disconnection,30-day recruitment,120-day training, same-day credit protection, malformed save rejection, access maps and budget navigation. The service purchase staircase and core release gates also pass, including deterministic continuation, cash/cargo checks, migration and unchanged paused screenshots.

Thirty two-year histories cover five starts × three seeds × baseline/withdraw-and-recover. Monthly snapshots and daily workforce checks around service cuts/recruitment transitions found no wage-cap/public-private overlap failure. Maximum monetary drift: 0.00002396. Lowest monthly baseline employment was 65%. Structural validation passed throughout.

The isolated2,000-resident/64× browser test measured draw p95 27.7ms and tick p95 12.5ms, with actual speed 64.3×. Tick cost rose and remains a profiling target; these are host results, not Android FPS. The broader economy, tutorial and final immutable candidate suite still precede packaging.

Screenshots at844×390/density2 are in previews/local-services, with source provenance. Machine-readable soak/performance evidence is retained in reports/development-local-services locally. No Library retry was made after the known helper-network failure.
