# Council programmes, workday scenes and crisis QA

Unpackaged development after 7.0.5. This work is in source only; the signed checkpoint APK is unchanged.

## A playable council programme

Each start has three chapters with visible requirements, current values, a dated consecutive-day count and direct links to the relevant reports. Missing a requirement resets the current chapter’s qualifying period. Finished chapters remain recorded. Completing a programme records the achievement in the town’s journal and leaves the simulation open; it does not create money or promise permanent prosperity.

- **Prosperous Vale:** establish essential work and food, purchase reachable care/teaching, then sustain family and public cash buffers.
- **The Frontier:** establish a viable foothold, expand modest public services within a small tax base, then retain accessible jobs and reserves.
- **Hard Times:** stabilize essentials and banking access, rebuild family buffers and services, then sustain a longer recovery.
- **Factory Country:** judge industrial growth by household conditions, complete actual adult training, and retain connected work and financial cushions.
- **Market Cross:** move beyond headline full employment to accessible services, adult learning and a sustainable civic establishment.

Ordinary chapters need 30 consecutive qualifying days; final chapters use 60 or 90. The thresholds are explicit game objectives, not forecasts or real-world standards. Adult-training completions are now recorded as a cumulative count. Old saves begin a programme at their current date without invented prior progress; existing courses and the earlier optional ambitions remain available.

Town Hall presents a compact current chapter. Agenda includes the full programme and a shared 0–100% chart of employment and funded medical/school access, sampled every ten days. The chart does not exaggerate small changes with independent scales. Explanations distinguish actual outcomes from controlled causal evidence and explain recruitment, teaching and commissioning lags. Review buttons use the real Services, Budget, Banks, People, Economy and Public Works drawers.

## Original activity on the map

Small hand-authored Canvas scenes visualize active production and funded services: a moving industrial flywheel/handling bench, harvesting and fishing, care staff with a visitor, teaching groups and worksite labor. Activity requires actual attending staff/production or purchased civic provision; samples never create economic output, cargo or residents.

Scenes favor foreground parcels and use the connected curb where appropriate. Existing foreground occlusion also applies to these actors. The per-view budget is 12 scenes in Rich detail, 7 in Balanced and 3 at high simulation speed; Performance, distant zoom, disabled effects/decor and Reduced motion omit them. Smoke and staff errands now respect actual attending workers and production. These are bounded visual samples rather than a full animation of every resident’s day.

Actual browser images and a 24-phase animated WebP are in [previews/council-programme](previews/council-programme), with source provenance. The animation samples the visual clock while economics is paused; it is not an Android frame-rate measurement.

## Crisis and workflow evidence

The inherited-risk stress deliberately creates a concentrated, paid-for legacy loan book outside today’s lending standards, then sends the investment cash to its real regional supplier and liquidates failed borrowers. This is an adversarial test, not a claim that the current underwriter would approve those loans.

Across two matched seeds and zero/full deposit guarantees, all three banks entered receivership after three firm defaults. Unguaranteed depositor losses were about $19,328 and $21,997. Full guarantees paid those losses from actual municipal cash. Within two years all four histories had three operating banks and 97–99% employment. Cash conservation and town structure passed throughout. This tests a severe inherited credit loss and re-entry path; it does not certify every systemic crisis or limited-treasury guarantee case.

Every one of the 60 authored Council choices was exercised through the actual dialog: cash, goods, structural validation, save/restore and exception checks passed. Programme probes cover all five definitions, interrupted qualifying streaks, duplicate-day/completion protection, no free grants, atomic malformed-state rejection and legacy migration. A real settlement policy workflow progresses beyond the passive school-funding constraint, through ordinary field edits and enactment, and preserves progress after restore.

New-town and successful-restore boundaries clear old messages, pending Council callbacks, trip/property selections and construction gestures. Invalid imports leave the old state intact. A strict pause check exposed repeated header repainting; unchanged header text, pause attributes and status markup now retain their DOM nodes. The regression checks both identical paused pixels and zero mutations of an unchanged pause control.

Frozen development source SHA256: `7b04be36e1883cb6d6816622f460a160108fa22528d3e69b431d6e1e28752b59`. Programme, crisis, Council-choice, workday, core release, mobile layout, contrast and controls gates passed against this assembly. This is a development subset, not the final complete candidate suite.

## Long-session work

`tools/soak_browser_session.py` runs actual requestAnimationFrame scheduling, cycles report drawers, scrolls them, pauses for archive round trips, checks state/currency/commodity invariants and records named cache bounds. It records V8 heap usage during play, with forced collection only before and after the session. Heap changes must be interpreted alongside population/building growth; this does not measure all native/GPU/canvas memory or Android thermal behavior.

The current 20-minute timed run and its subsequent isolated 2,000-resident performance check are pending at this checkpoint. Results will be in `reports/development-player-loop`. A new full immutable candidate freeze, native/device stages and APK verification remain required before final delivery. No Library retry or native-emulator retry was made in this slice.
