# 7.0.4 development slice: purchased services and a living town

This phase advances two connected parts of the game. Service allocations purchase limited provision instead of receiving full effectiveness whenever any budget is paid. The first original art slice gives the town richer ground materials, shop identity, lighting, shadows and productive-building activity. These are intermediate improvements within the overnight roadmap.

## Service economy

The same-town baseline staircase confirmed that a $1 medical budget provided the same aggregate health improvement as $1,000. Medical and school effectiveness used paid/proposed fractions. The new model specifies operating standards: five clinic teams per 350 residents, ten school staff per 260 residents, the current public wage (minimum $24) and the existing 65% payroll share. These are explicit gameplay planning standards, not clinical or educational forecasts.

Purchases are capped by authorization, available treasury cash, resident need and facility capacity. Unused authorization stays in the treasury. The existing payroll transfer distributes local public wages and tax; remaining operating purchases pay regional staff and suppliers. The whole payment retains explicit counterparties. More spending raises coverage until demand or buildings bind. Health and aggregate education move gradually with coverage. Repeated extra buildings no longer grant unlimited aggregate improvement without provision.

Services now reports daily authorization, actual purchases, retained funds, operating need and the limiting capacity. Economy flags low provision. Budget distinguishes full authorization from actual spending. Restored towns refresh derived provision on their next simulated day rather than displaying stale reports from earlier rules.

Transit payments now occur before household fares, and fare relief uses actual payment. Unfunded outreach no longer increases safety or reduces incident risk; unfunded militia commitments no longer provide the authorized-budget benefit. Road-service reporting uses maintenance need rather than awarding full coverage for a tiny paid allocation.

Tests cover zero/tiny/larger/saturated budgets, no facility, insufficient cash, conserved money and unfunded-promise counterfactuals. The matched regional seed42 trial at day361 showed passive policy around $995k treasury/health70/education46; service investment around $639k/health78/education57; austerity around $1.17m/health61/education43. Employment alone remained100%, making service and fiscal outcomes important independent dimensions. These figures are experimental trial evidence; final candidate evidence carries its own source hash.

Remaining modeling work includes explicit staff qualifications/training supply and a review of individual skill/health thresholds. Do not equate the new aggregate coverage model with a calibrated real economy.

## Original visual slice

The new code-native art layer follows the existing miniature-town identity. Actual water boundaries gain shore stones and reeds; water has layered ripples, meadows gain soft vegetation patches, shops gain striped awnings and frontage planting, and industrial sites gain stacked materials. Directional cast shadows and a warm-to-cool screen wash establish a coherent light direction. Existing night, decoration, effects and quality controls are retained.

Short staff errands appear at staffed, productive or trading businesses and follow their frontage toward connected road access. They share the existing depth-sorted actor and foreground-occlusion path. Activity is capped at five sites at64× and twelve in Balanced/twenty in Rich detail, and is suppressed by reduced motion or disabled effects. Static detail and shadows remain cached; half-resolution high-speed ground keeps the existing workload tier. This is a first slice; fuller transport animation, terrain composition, building variety and lighting controls remain on the roadmap.

## Reliability and compatibility

The exact paused-screenshot gate initially failed. Pausing now draws its final map immediately, paused panels stop timed automatic refresh, and the synchronous test reset renders the requested world/panel before returning. The screenshot equality assertion was retained and passed.

Deleting Array.at reproduced a real startup/rendering error (`ids.at is not a function`). All game uses now use a small negative-index helper. Workflow checks with Array.at absent cover rendering, development, charts, policy enactment and Council focus. This does not certify every API or syntax feature of an older engine; the software emulator's WebView83 remains a native compatibility target.

Run `tools/qa_candidate.py` for the immutable full gate and build pipeline. Preserve 7.0.3 as the prior stable checkpoint. Do not present partial trial reports as final candidate evidence.
