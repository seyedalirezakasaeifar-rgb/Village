# Evidence-based Newfoundland district profiles

This change extends the derived urban profile in `src/27-urban-evolution.js` and the existing mayor-facing neighbourhood inspector. It adds no income, rent, service, banking, relocation, or investment bonus. Profile data are recomputed from current buildings, households, jobs, bank books and the live service allocator; only the already-supported district name/character and 90-day review record are archived.

## What the current game supports

Lower, middle and higher income bands already compare observed after-tax household income per resident with the town median (below 0.72×, above 1.4×, otherwise middle). They do not assign wages or property condition. Real farms and crop titles, operating grocery/tavern businesses, employment capacity, household addresses, public service catchments, bank branches, deposits and loans already exist. The spatial inspector now reports them together with mean road distance to the town hall, housing capacity, staffed workers, funded clinic/school access, and road-catchment reach.

Observed categories use those inputs:

- **Downtown mixed-use** requires resident households, housing units and job capacity at or above observed town medians, a road path to the town hall at or below median block distance, and local retail or bank presence.
- **Suburban neighbourhood** requires resident households beyond median town-hall road distance, at or below median housing capacity and job capacity, and no local retail, heavy industry or farm.
- **Market centre** requires at least two staffed grocer/tavern businesses with actual recent sales, and at least 12 residents within a 24-step road catchment of its local grocery stores. It can overlap with employment; active farms remain excluded.
- **Financial district** requires at least two open bank institutions, actual deposits or outstanding loans, at least one post-founding bank entrant in the block, and no farm. Scenario-start banks alone are reported as a banking node, not promoted to a district.
- **Agricultural belt** remains grounded in active farm businesses and low resident count. No block receives a finance or market classification while it contains a farm.

Observed character is held for 90 days before the archived district character changes; emptied districts still dissolve after 180 days. `urbanBuildingDescriptor(buildingOrId)` is the read-only renderer handoff. It returns `buildingCue`, `streetscapeCue`, observed pattern, measured income band, rent burden, physical condition, bank activity and service-access values. Income and condition are separate fields so artwork can vary house form without equating low income with neglect.

## Newfoundland form cues for the renderer

The source descriptions below are generalized from the supplied Newfoundland heritage references. The descriptors are style guidance, not historical claims about a simulated building and not copies of the cited landmarks. Roof/building families are proposed visual adaptations; the renderer remains responsible for silhouettes, meshes, materials, seasonality and detail.

| Model entity / observed setting | Exported cue | Documented regional reference | Game-design inference |
| --- | --- | --- | --- |
| Dense downtown home | `nl-historic-town-row` | Attached two-to-three storey clapboard, varied dormers or bays, tight setback, front steps. [Heritage Newfoundland, 1892–1940 architecture](https://www.heritage.nf.ca/articles/society/architecture-1892-1940.php) | Mixed attached houses inside an observed dense mixed-use block. |
| Home near natural water | `nl-outport-house` | Saltbox/modified saltbox or biscuit-box massing, simple sash, garden and shed. [Newfoundland folk architecture](https://www.heritage.nf.ca/articles/arts/newfoundland-folk-architecture.php) | Nearby water does not model harbour orientation or a fishing livelihood. |
| Higher-income home | `nl-merchant-house` | Larger detached mansard/Queen Anne forms, verandah, bays and garden. [Angel House](https://www.heritage.nf.ca/articles/society/angel-house.php) | Generalized family choice only; no landmark is copied. |
| Lower-income home | `nl-compact-worker-house` | Compact attached, semi-detached or detached timber form with restrained trim and shared yard. [Bannerman Park worker housing](https://www.historicplaces.ca/en/rep-reg/place-lieu.aspx?id=5543&pid=0) | Care/decay remains controlled by `condition`, never by income band. |
| Outer residential area | `nl-new-suburb-house` | Cape Cod, bungalow, split-level and townhome infill; lawns and neighbourhood services. [Churchill Park](https://www.heritage.nf.ca/articles/society/churchill-park.php) | Form selection follows observed outer-road-distance and housing capacity. |
| Operating market street / centre | `nl-market-streetfront` | Ground-floor display shops with residential/office upper floors. [Commercial Chambers Building](https://www.heritage.nf.ca/articles/society/commercial-chambers-building.php) | Covered stalls/market-hall elements are explicit gameplay adaptation. |
| Bank branch | `nl-stone-brick-bank` | Generalized symmetrical classical/Italianate stone or brick bank forms. [Bank of Montreal, St. John’s](https://www.historicplaces.ca/en/rep-reg/place-lieu.aspx?id=2329), [Bank of Nova Scotia](https://www.historicplaces.ca/en/rep-reg/place-lieu.aspx?id=6133&pid=0) | A financial district is emitted only where multiple live branches have real books. |
| School/college/court | `nl-institutional-brick-stone` | Symmetrical brick/stone institutional windows and modest forecourt. [Presentation Convent and School](https://www.heritage.nf.ca/articles/society/presentation-convent-and-school.php) | Shared restrained civic family cue. |
| Clinic | `nl-cottage-clinic` | Practical cottage-hospital scale. [Louie A. Hall](https://www.heritage.nf.ca/articles/society/louie-a-hall.php) | Gameplay adaptation; this is not a hospital entity. |
| Fire station | `nl-fire-apparatus-hall` | — | Apparatus doors are an operational visual cue, not a historical claim. |
| Wharf/fishery | `nl-working-waterfront` | Stages, wharves, fish stores, workshops and warehouses oriented to water. [John Quinton Ltd.](https://www.heritage.nf.ca/articles/society/john-quinton-limited.php) | Net lofts and salt stores are art props; the simulation models wharves/fisheries, not each trade. |
| Factory/warehouse/mill/resource site | `nl-working-industry` | Utilitarian brick/timber workshops and loading yards. [FPU Factory, Advocate](https://www.heritage.nf.ca/articles/society/fpu-factory-advocate-building.php) | Mass/yard placement follows actual business kind and road/resource links. |
| Farm | `nl-farmstead` | Farmhouse, barn/stable, sheds, garden and active fields. [Crowley Property](https://www.heritage.nf.ca/articles/society/aubrey-elizabeth-crowley-property.php) | Mixed fishing/farming livelihoods are not inferred because household occupations do not yet model them. |

## Explicit gaps

There is no church or community-hall kind in the building inventory (`src/00-foundation.js`), so the API reserves a `nl-community-church` cue only for future use; no church entity or activity is claimed. Existing banks have real books and the finance engine can open a new standalone bank after its population/confidence/capital gates. That is not a privately built branch: deposit and loan markets are townwide, banks have no modeled branch staff or local service catchment, and a player-placed duplicate bank tile would add no financial access. The planner reports founding bank nodes and active balances without promising branch expansion. A future branch project needs branch-specific access, staffing and client/account routing tied to the existing `G.banks` ledger before it can be a truthful investment action.

Natural six-year evidence: seed 42 has 11 middle-income and four no-resident-income profiles; seed 101 has 11 middle-income, one lower-income, one higher-income and four no-resident-income profiles. Both have observed downtown and market-centre blocks; neither has a financial district because all three banks were founding institutions. Market centres now share mixed-use employment blocks when active retail and reachable customers support both patterns. The generated report preserves the measured profiles and actual bank building handoff.

## Verification

`tests/test_urban_district_profiles.py` runs two natural six-year towns, checks the classifications against their source indicators, checks that descriptors leave save/RNG/money/goods untouched, approves an ordinary $600 neighbourhood-plan review through the real UI, and verifies exact 30-day save/replay. Existing urban evolution, active-play, trajectory checkpoint and art tests also pass. The original historical kernel attempt failed before product assertions because its referenced generated archive was absent from commit `833afee35aa714919a38e420e74cee1f719315db`. The current integrated `tests/test_urban_kernel.py` uses the committed ordinary-resource day-721 checkpoint, retains an independent spatial reference, and passes mutation/array checks plus 180-day complete-state continuation with zero exclusions. Historical failure evidence remains in the district review checkpoint.
