# Fire-response access audit

## Finding

The mayor previously saw only **Emergency readiness**, a townwide scalar derived from actual paid defense budget and the count of municipal fire stations. The incident simulation uses a separate property-level factor: strongest of the municipal response and active private-brigade response. The municipal value is road-distance weighted and scaled by `defensePower`; the independent value requires an open staffed brigade on the same connected road graph and uses current usable capacity and household membership/spillover. On an incident, damage is `random(1,16) × (1 − localResponse × 0.78)`. The factor reduces damage; it neither prevents fires nor provides a location-specific incident probability. The dispatch animation selects the closest connected response building and is not itself the protection calculation.

That meant a 76/100 emergency-readiness display did not tell the mayor whether a particular home had road access to a station. A deterministic seed-42 property had a municipal response factor of 58.7%, implying 45.8% less condition damage *if a fire occurs*. Removing the two road tiles at its portal in a test fixture reduced local municipal/private response to zero while citywide readiness stayed 76. Restoring the road restored the original response. This was misleading-by-omission, not a mismatch in the local fire-response formula.

## Change

A selected property now reports townwide readiness separately from road access, municipal response, the nearest reachable public station, independent brigade response, nearest staffed/reachable private brigade, combined strongest response, and estimated incident-damage reduction. It explicitly says fire remains possible, the readout is not an incident-risk estimate, and response is not guaranteed. A fire-response overlay colors properties by their current combined factor (red <10%, amber 10–49%, green ≥50%) and shows percentages at close zoom. The overlay uses a derived cache keyed by day, road graph, property/station set, private-provider state, funding and population; the displayed value reuses the actual incident response functions.

The existing independent-service description and public funding rules remain unchanged. The response map does not change fire probabilities, staffing, fees, damage, dispatch or provider economics.

## Controlled acceptance

`tests/test_fire_response_disclosure.py` uses a seed-42 town and real map selection plus the mayor-facing Community → Fire & rescue reach → response-map control. No fire event is injected. With a connected public station, the inspected home reports 13 road segments, 58.7% municipal/combined response and 45.8% modeled damage reduction. A temporary test-only local-road break makes the same home unreachable with zero local response despite 76/100 citywide readiness; the overlay cache invalidates and returns to its original values when roads are restored.

A separately labeled controlled independent-brigade fixture funds no public fire budget, assigns two actual workers, obtains 180 usable service capacity and 159.3 memberships, and reports 19.4% private response / 15.1% modeled damage reduction at 13 road segments. No incident is forced and no free money or people are added; the fixture transfers existing balances and validates the town. The base natural-town save replays 30 days identically; total cash drift is under $0.000001. All test scenarios validate and emit no browser errors.

Source hash: `e3ccd0d8c71ebc8fb5ab84f320d2d8354f9f8bf9119b4883e4b9170a4003b971`.
Evidence: `docs/previews/urban8/fire-response-audit.json`.
