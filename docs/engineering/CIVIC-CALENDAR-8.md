# Living civic calendar: first playable gathering

Base main `1cf6af5`. First slice: voluntary market-neighbours gatherings at actual municipal squares, including mayor-named squares. No outside visitors, extra vendor purchases or arbitrary happiness/education/income rewards are introduced.

## Graphics contract

`civicGatheringCues()` returns active-only `{id,venue,x,y,name,start,end,capacity,attendance,status}` records. The coordinates and venue ID identify the actual square. Attendance is an aggregate leisure-model count of actual eligible residents, not a new simulated agent list or passenger reservation. Graphics may replace `paintCivicGathering(g,item,cue)` while retaining the cue contract and existing depth ordering. The isolated module currently decorates the actual square with original bunting and at most8 representative figures (3 in fast mode). Distant views skip the painter; crowd samples disappear below0.55 zoom. Effects/reduced-motion settings are respected. Animation uses the frozen simulation remainder, so a paused gathering stays still. No renderer file is edited, no extra traffic entities are spawned and rendering settles no money or population.

## Voluntary decision and real preparation

The existing public-place area adds a collapsed calendar. The mayor chooses a real municipal square and an opening simulated day within30 days. A gathering lasts two after-shift evenings. The default review finds the next unbooked evenings; the input can change the date. Citywide overlapping gatherings are refused to prevent double booking in this first slice. The panel preserves its expansion across reviews.

Capacity is a disclosed game assumption:24 modelled places per physical plot, capped72. Preparation costs180 plus2 per place. A standard one-plot square costs228. The review shows current eligible walking-distance residents, capacity, cost and treasury afterwards. Attendance is not guaranteed. Existing ordinary shops continue trading; no event-created inventory or revenue is claimed. The cost competes with existing service funding and other capital choices.

Lead-approved accounting helpers are isolated in `src/98zzzzzzzzzz-civic-calendar.js`:

* `reviewCivicGathering({venue,start})` is a no-payment quote. It validates actual municipal venue, connected street access, date, calendar room and overlap; captures the current town/calendar, geometry, capacity, eligibility and price.
* `authorizeCivicGathering(quote)` revalidates those conditions and sufficient finite funds before mutation. Payment is exactly `treasury -= cost`, `region += cost`, `cumulative.spending += cost`; the event stores paid cost once. The existing CIVIC PROJECT direct-transaction dialog prevents generic council reconciliation from creating a second transfer. No transferBudget/cash-account misuse or unfunded escrow exists. Repeated/stale authorizations reject without payment.
* `cancelCivicGathering(id)` closes only a scheduled/active gathering. Preparation is already spent, so cancellation has no refund. Recorded visits remain. A lost venue/street connection similarly leaves a failed event with its paid preparation retained.

## Participation assumptions and daily hook

After the ordinary end-of-day economy, a resident is eligible if the household actually bought food, stress is at most65, the person is at least12 with health at least60, has no blocked commute/public-duty assignment, and can walk at most12 road steps from the actual home to the connected square. A deterministic65% opt-in sample, with a date/event-specific ordering before the capacity cap, models local after-shift participation without always privileging the earliest household IDs. These are disclosed stylized leisure assumptions, not observed real-world attendance, individual tracked trips or a full hourly time-budget model. Public-duty residents are conservatively excluded. No wages, travel fares, route seats, goods, private fees or stress values are altered. Future paid vendors/visitors require separate real budget/inventory settlement.

`civicGatheringDay()` records at most one observation per day, total visits and distinct existing resident IDs. It wraps the existing canonical `civicCampaignDay()` callback after ordinary daily settlement. It does not replace the tick engine or cooperative busy barriers. Experimental cooperative simulation should route new preparation/cancellation commands through its committed-state command API before enabling that experiment; this slice is verified on the current default engine.

## Save and acceptance

Optional `G.civicCalendar` version1 stores at most16 bounded events; only closed history may be pruned. Scheduled/active overlap, malformed dates/counters/participants/payments and duplicate IDs reject. The existing public-place validator is wrapped, so no shared archive-adoption code is overwritten. Old saves need no calendar field.

`tests/test_civic_calendar.py` uses actual controls to build/name Willow Commons, cancel a review, authorize preparation once and open its active map gathering. On seed42 the quote sees46 eligible residents; the actual opening evening sees73 eligible and24 modelled attendees, illustrating why the forecast is not an attendance promise. The test checks conserved cash, repeated authorization rejection, once-per-day participation, actual animated/stable paused pixels without economic mutation, next available dates, cancellation without refund, insufficient funds, tampered capacity, stale date, exact continuation and malformed-save rejection. The no-funds fixture transfers existing treasury money to the existing regional account; it does not create resources.

Evidence and inspected screenshot: `reports/civic-calendar/controls.json`, `willow-commons-active.png`. Receipt source hash identifies the tested distribution. This is the first local gathering, not a claim of completed visitor economics, several-hour enjoyment, physical Android performance or experimental cooperative compatibility.
