# Mayor’s desk and earned town directions

Branch: `codex/8-player-experience`, based on `1de69303010f31375677c193bb3318822dc4c7b4`. This is a UI/progression slice for integration, not an Android release.

The mayor now opens a short, actionable desk instead of a stack of overlapping reports. It ranks at most three observed pressures: food supply, cash runway, broken commuting, hardship, usable services, late cargo and missed commitments. Each has a concrete report link and a collapsible causal explanation. Day one explicitly awaits the first settlement rather than claiming a zero-food or zero-service crisis from uninitialized daily accounts. Existing reports, council programme and ambitions remain available in the full-report disclosure and Agenda.

The existing first paid food order stays directly below the desk. It leads to the real regional exchange, then an export agreement, then a district commitment. An optional four-report council session teaches that loop, tracks explored reports and can be hidden permanently. This is guidance, not a claim that visiting a report achieves an economic outcome.

Three optional town directions provide distinct long-term plans:

- Regional crossroads: delivered cargo → fulfilled agreement → established trade park → sustained food, employment and reserves.
- Working river: staffed fishery → staffed outlet wharf → established waterfront district → sustained household essentials and reserves.
- Complete neighbourhood: food and hardship → usable care and teaching → established mixed neighbourhood → sustained work, services and reserves.

Progress is earned from real shared metrics, one stage at most per daily settlement. The final stage requires 30 consecutive qualifying days, resets its current run after a failure, and recovers normally. Completed stages remain recorded. Directions create no cash, goods, policy changes, bonuses or buildings. Changing direction has a cancellable review and starts a fresh record without changing the economy.

Agenda also has an explicit before/after comparison with units and dates, a replacement confirmation, and field notes drawn from an actual delivery, the household with the thinnest cash/deposit cushion, and acquired district population, staffing, connections and coverage. These do not invent resident quotations or attribute causality to a single policy.

Regional quotes and unit freight now display cents: a $0.21/unit cost must not appear free. The agreement review states units, local reserve, arrival lag, deadline, upfront enterprise freight, estimated inventory margin, gross delayed receipts and disruption risk. It continues to use the existing contract dispatcher and settlement code.

## Integration contract

New independent files: `src/98-player-experience.js`, `assets/mayor8.css`, `tests/test_mayor_journey.py`, `tests/test_mayor_rules.py`.

Minimal shared hooks:

1. `src/50-clock.js`: call `mayorJourneyDay()` after `districtProgrammeDay()` and `updateScenarioProgramme()` in the canonical end-of-day snapshot.
2. `src/90-archive-panels.js`: reject `!validateMayorJourney(data)` before adopting the parsed town.
3. `src/80-civic.js`: add `TOWN DIRECTION` and `OBSERVED OUTCOMES` to `directTransactionDialog()` so these reviews use Cancel and bypass generic council grant settlement.
4. `assets/index.html`: load `mayor8.css` after `civic7.css`.
5. `src/98-onboarding-trade.js`: text spacing only. Its existing controls/handlers remain the authoritative paid-order path.
6. `src/98-trade-ui.js`: display-only precision, spacing and expanded review; no dispatch, price or accounting algorithm changes. `mayorUnitMoney()` is declared in the new module, which sorts before `98-trade-ui.js`.
7. `tests/test_mobile_rendering.py`: include the new stylesheet in originless test fixtures. `tests/test_council_programme.py`: explicitly expand the full-report disclosure and scroll to the original programme shortcut before asserting its visibility.

The new overview wraps `tradingOverviewBase`, avoiding duplicate display of the existing trade-next-decision wrapper; it renders `tradingTownNextDecision()` directly outside the full-report disclosure. If the integration lead replaces that wrapper, retain this structure or update the base reference. Renderer and economic-service settlement modules are untouched.

`G.mayorJourney` is optional additive save data, version 1:

```
{version:1, direction:''|'exchange'|'river'|'community', started:day,
 stage:0..4, held:0..29, lastDay:day,
 completed:[{stage,day}], guide:boolean, visited:[panelName],
 review:null|{day,metrics:{employment,food,hardship,medical,school,reserve}}}
```

Old saves without the field are accepted. State is initialized by the next daily settlement or an explicit UI action; rendering uses a temporary default and does not initialize or advance progression. Validation rejects unknown directions, invalid dates/stages, duplicate/unknown visited panels, corrupt completed stages and invalid baseline values before changing the active town. No save schema bump is required by this additive UI data alone; the integration lead owns the combined release schema.

Coverage comes from `programmeMetrics()`, and district observations come from `districtMetrics()`. **When private school/care/provider logic is integrated, the lead must make these shared coverage functions report effective combined access consistently.** This branch does not implement a competing service model or promise an available private operator where the integration has not supplied one. Private-provider commissioning controls remain the lead’s UI.

## Evidence and limits

Exact assembled source SHA-256: `2e97e23dc2946ed500bf3b855673d13fe8755d38996b2e681513a9641fae0255`.

Passed:

- `python tools/assemble.py` (includes `node --check`).
- `python tests/test_mayor_journey.py`: real landscape/portrait controls; cancelled direction and food order; actual paid food import and arrival; actual fulfilled 30-day export agreement; two earned stages; unchanged municipal cash at commitments; conserved cash; exact five-day save/load replay; lazy legacy migration; five atomic corrupt-archive rejections; guide persistence and direction cancellation.
- `python tests/test_mayor_rules.py`: controlled metrics for all three paths; no duplicate day; sequential stages; final 30-day reset/recovery; no repeated completion story or money award; valid completed archives. This is explicitly a rule fixture, not a real economic playthrough.
- Existing `test_regional_trade.py`, `test_council_programme.py`, `test_district_trade_choices.py`, `test_regional_tradeoffs.py` and `test_mobile_rendering.py`.
- Seven mobile layouts, 568×320 through 844×390 landscape and 360×640/390×844 portrait; no overflow or page errors, reachable tabs and time controls. Density mean pixel difference 4.72.
- `git diff --check`.

Screenshots and machine-readable receipts: `reports/player-experience/`. New journey tests serve the project on localhost because this managed Chromium blocks direct `file:` navigation; they use the actual shipped assets and controls. Existing originless test fixtures inline all shipped stylesheets.

Limits: this verifies a playable browser decision chain and simulated economic time, not a multi-hour human play session, physical-phone frame rate, Android file pickers or subjective studio quality. It does not prove that every late-game district placement and every private-provider mix is balanced. The existing economic experiments still reach very high employment/low hardship over a year; more long-run difficulty tuning remains with the integration lead. No APK, signer, merge or release was produced here.
