# Commercial district evolution and observation freshness

## What changed

Market streets now emerge from observable activity rather than a painted plan: at least two staffed grocery/tavern businesses with recent sales, at least 12 residents inside the local grocery road catchment, and no active farm in the block. Mixed employment can coexist with a market centre; it is reported independently as an employment-quarter tag. Residents within 24 road steps and residents within reach of a stocked, staffed grocer are reported separately. Neither number guarantees an affordable purchase. Market character changes only after the 90-day review; the review now commits the current observed character, and empty blocks dissolve under the existing 180-day rule.

Financial-district descriptors require at least two open banks, actual deposits or loans, and a post-founding bank entrant in that block. Founding banks remain visible as a banking node but cannot, by themselves, turn a neighbourhood into a financial district. This code does not build bank branches or change bank-market economics. The current banking model has townwide depositor/loan books and no branch-specific staffing, customer access, or account routing. A player-built second copy would therefore add no local financial service. Existing automatic entry is a new institution, not a spatial branch; it remains governed by its existing population, confidence and capital gates.

## Interfaces

`urbanSpatial().profiles[key]` adds these read-only indicators: `retailActiveBusinesses`, `retailStaffedWorkers`, `retailSalesTrend`, `retailRevenueTrend`, `retailResidentsWithin24`, `retailStockedResidentsWithin24`, `industrialBusinesses`, `foundingBankBranches`, `expandedBankBranches`, and `observedTags`. `urbanBuildingDescriptor(buildingOrId)` carries the same fields, alongside the existing income, rent, condition, service and Newfoundland streetscape cues. Observed tags are multi-valued; renderer style cues remain descriptive and do not alter the simulation.

`invalidateUrban()` is O(1). Writers that can change observed income, retail sales/staffing/stock, bank balances or business ownership call it at transaction/day boundaries. `urbanSpatial()` reuses its derived whole-town snapshot until day, topology, building count, planning revision or explicit writer invalidation changes. UI and renderer reads do not mutate model state, RNG, ledgers or bank books.

## Evidence and limits

Natural six-year settlement runs for seeds 42 and 101 produced market-centre blocks, including mixed employment, while all observed banks were still founding institutions and no financial district formed. A natural 20-year seed-42 settlement run produced markets but no later bank entrant, so Finance remained absent. A no-staff/no-sales adversity check removed the market tag. These observations demonstrate that the new label follows real activity; they do not prove that all normal cities will form a market or finance district.

The observation contract test exercises a 90-day character transition, a real one-dollar household deposit into an existing bank, same-day income recomputation after a production-day transaction, read-only RNG and cash invariance, and archive load. The 20-year replay compares after archive tenancy normalization because load canonicalizes the ordering of one apartment's tenant ID list; no other saved fields diverged. See `docs/previews/urban8/commercial-districts.json` and `docs/previews/urban8/profile-observation-contract.json` for source hashes and measured runs.

No cash, inventory, hiring, deposit, loan, migration, or investment threshold was changed. Regional-seed diagnosis was not completed, and no private bank-branch expansion is claimed.
