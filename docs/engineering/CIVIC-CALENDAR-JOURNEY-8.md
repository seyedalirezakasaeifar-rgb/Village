# Civic-calendar resident journey acceptance

Test base: current integrated economy `68b470a` plus the calendar feature from `37d5bec` (locally cherry-picked as `5f3db80`). This follow-up edits only a confirmed expired-venue label; polished rendering remains with graphics.

`tests/test_civic_calendar_journey.py` founds a normal seed42 town and runs31 ordinary days. Treasury rises from90,000 to100,533.80 through normal game receipts before the square or preparations are bought. No resources, residents, jobs or event outcomes are injected.

The player builds/names Founders Commons, reads capacity/walking access/preparation cost, selects opening day34, authorizes preparation, cancels without refund and rebooks. Preparation is paid again only for the actual new booking; the old cancelled record remains. The opening evening has24 modelled local attendees and the completed two-evening gathering records48 visits. Visits are not falsely described as48 distinct people or commercial sales. The review explicitly separates leisure from paid commerce and states that no extra jobs, trips or transit seats are booked.

A scheduled save is restored before opening, an active save is restored across the first evening, and the finished record is restored after completion. Repeated calls to the canonical end-of-day callback on the same day, including after restoration, neither pay again nor add attendance. Actual full-town serialized comparisons are made against the restored state: loader-cleared transient service reports are not incorrectly treated as calendar mutations. The optional cooperative prototype is absent/not enabled on this base. This is repeat-commit-callback evidence, not a claim that an unintegrated asynchronous engine has passed acceptance.

The journey then pays preparation for another gathering and uses the actual compensated land-assembly review to demolish the public square. A quote captured before demolition cannot authorize afterwards; no money or state changes. The removed venue emits no crowd cue. On opening day the event becomes failed, retains its spent preparation and has no attendance. Its failed history survives save/load without resurrecting the venue. The named place remains historical. A confirmed UI defect previously called its map action “Visit the real square”; the follow-up now says “Visit the recorded site” and explicitly explains that the original venue is gone.

Finally, the actual Options → Start New Town confirmation founds another town. Calendar data and visual cues are absent. An old captured authorization cannot spend the new town's treasury. All current-town validators pass and there are no page errors.

The original calendar test also passes on this assembled source: once-only conserved payment, insufficient funding, capacity tampering, stale date, next unbooked evening, deterministic continuation, malformed saves and bounded animated/paused presentation.

Artifacts: `reports/civic-calendar-journey/controls.json`, `lost-venue-calendar.png`; the existing feature receipt under `reports/civic-calendar/` was refreshed with the current source hash. These are bounded automated journeys, not hours of human play or proof of physical Android performance. No extra vendor demand or visitor money was added. No other UI/validation defect was established in this acceptance slice.
