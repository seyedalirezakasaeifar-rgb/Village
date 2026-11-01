# Retail staffing and unmet food: historical pre-fix finding

This was recorded on the earlier bundled game, SHA-256 `ad4c5ae3ee9ad3379403eb3e36b8b03b6f617d1c3639f42243523e8c8c6e9865`. The original deterministic evidence is preserved in [grocer-capacity-response-prefx.json](grocer-capacity-response-prefx.json). A later follow-up identified and fixed a wage-priority inconsistency; see [LABOUR-MOBILITY-8.md](LABOUR-MOBILITY-8.md) for the matched post-fix replay. The current harness writes [grocer-capacity-response.json](grocer-capacity-response.json).

On regional seed 909 after a 120-day external road interruption and 120-day reopening, the pre-fix day-301 town had 711 residents, full employment, 72 open job slots, and 13 groceries. No eligible unassigned workers were available. Staffed-and-stocked daily grocery capacity was 1,120 units against estimated need of 1,137.6; unmet food was 17.6 units that day and 2,627.2 over the prior 30 days. The household trace showed rotating late shoppers who could reach shops and afford purchases, but arrived after staffed capacity had been consumed.

Ten grocers had one unfilled job each and three had no staff. Grocer offers averaged about $30.8/day against an all-sector median around $32.4/day. The nominal-vs-effective wage ranking bug later explained why the initial diagnosis overemphasized this labor bottleneck. A mayor-built grocer gained stock and two vacancies, but stayed unstaffed and sold nothing. A new home produced two reachable workers who chose higher-paying tavern jobs. See the follow-up for the corrected allocator and current results.

The city’s commercial-investment forecast also did not directly see the shortage: it estimated grocery applicants from residents-per-store and applied only a small low-inventory bonus, without using unmet food or staffed sellable capacity. That separate forecast gap remains outside the follow-up fix.

This one-seed interruption/reopening run is retained as historical evidence. Do not interpret its pre-fix throughput shortfall as current behavior; the same test history after the wage-priority correction had no unmet food.
