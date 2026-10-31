# Annexed district growth outlook

The charter office now has an **Inspect growth outlook** control for every owned outer district. It reviews the selected deed on demand and shows its main-road connection, residents, household capacity and vacancies, active and funded local jobs, legal connected cottage sites, present citywide housing demand, vacant units elsewhere, and the current private home-investment ranking. The outlook refreshes from live ownership, zoning, district-charter and road state; it does not run on every frame or change the simulation RNG.

When a legal roadside home lot exists, the mayor can choose **Visit Cottage site**. This opens the map at that surveyed location with the ordinary $20,000 Cottage tool selected. Nothing is charged until the player taps the map. The report also assesses one ordinary two-adult household against current funded reachable jobs, food, access, budget and service conditions. This forecast describes one sample and does not guarantee a move; the actual construction action runs the game's existing household-admission rules.

## Diagnosis from the three-year regional replay

The saved seed-42 journey ended on day 1081 with 886 residents and six purchased outer tracts. The deeds were not blocked by disconnected streets, lack of construction capital or an ineligible household market. East Meadow had 67 of 67 road tiles on the main network. It had no homes, residents or vacant units, though a legal connected cottage site existed at (59, 14). Citywide home demand was 100/100, pressure 65/100, and vacant household units were zero. Regional developer capital stood at $3,747,999; municipal cash was $615,843.

The actual private housing search ranked a core cottage site at (42, 33) with score 17.46 ahead of East Meadow's strongest lot at (59, 14), score 2.63. The local private build quote cleared its return hurdle by about $1,020. A two-adult sample at the East Meadow site passed current admission checks with two funded, reachable job offers, a reachable grocer, $59.23/day net pay and $27.68/day essentials; its modeled pull was 86%. That explains the empty tract: investors preferred established core sites while all existing housing units were occupied. It was not a road or household-eligibility defect. The outlook now gives the player those reasons and an affordable, deliberate way to act.

The real-control replay followed that path: the player reviewed the outlook, visited (59, 14), and built a cottage through the existing tool for $20,000. The model then admitted two residents through its normal randomized assessment. No households, funds, roads, land or goods were injected. Total account balance remained conserved, the town validator passed, and the next 30 days replayed exactly after save and restore (excluding transient vehicle/render state).

The sample site had no local learning coverage, and the two adults had no school-age learners. Child households still require the normal education and service checks. More distant deeds can also be blocked by an industry charter or agricultural plan; the report names those permission barriers instead of presenting them as weak market demand. Farm titles and production are not changed by the outlook or by building on a separate vacant lot.

## Passenger-service access and civic limits

The sample job review distinguishes a road commute's modeled travel cost from a paid bus/elevated-metro fare. For an offered paid-transit job, it shows the route name and mode, current driver staffing, capacity/reserved seats, and whether at least one seat is available through a capacity-aware journey. This is a point-in-time forecast only; it reserves no seat, and real household arrival repeats the live budget/capacity checks. Clinics and schools remain separate, funded, street-distance catchments. The report shows their forecast coverage and explicitly says that passenger routes do not extend civic coverage. This avoids advertising a transit stop as free health or school access.

The underlying passenger engine was already acceptance-tested through actual bus/elevated-route controls, paid fares, driver payroll, finite seats, a broken elevated alignment, bus detour, 21 repeated district purchases, occupied-home redevelopment by a stop, and exact archive continuation in `tests/test_transit_network.py` and `tests/test_transit_combined_redevelopment.py`. A real seed-42 founding test also purchased East Meadow ($30,606), constructed a road into the new parcel, opened a cottage, then paid $9,000 for a depot and $13,300 for a frequent bus route from that parcel to a live grocer. On day two that route was staffed by four existing residents, operated at 98 peak seats and 38.8-minute headway for $139.63/day, and carried/charged two actual boardings. The new household remained unemployed: there were no funded reachable vacancies, so the route did not invent jobs or promise an arrival. This exposes a realistic boundary of the feature: transit can make a real destination reachable without creating a position or extending civic catchments.

## Verification

```
python tools/assemble.py
node --check assets/game.js
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter:tests python tests/test_parcel_growth_outlook.py
```

The source-hashed control result and inspected prospectus screenshot are in [`docs/previews/parcel-growth-outlook`](../previews/parcel-growth-outlook/).
