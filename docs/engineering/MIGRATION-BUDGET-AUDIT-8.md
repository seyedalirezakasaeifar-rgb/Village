# Migration, physical housing and the source of passive reserves

Read-only audit of `dc0ddab26532fc62342e5a614ea262ec6117cac1`, game SHA-256 `23bd4570b62219ddc9f58a68007cb7c696569def326004fd4d1a198fcccd0fe1`. Fetch confirmed that this checkpoint differs from `525e47d` only in soundtrack assets/code, packaging and related evidence. The economic rules are unchanged. This branch changes tools and evidence only; proposed production fixes require the integration/economics lead's decision.

Evidence: [compact results](../evidence/migration8/summary.json) and [complete compressed fixtures/flows](../evidence/migration8/full-evidence.json.gz). There are 36 final controlled fixture cases, six natural matched histories totaling 80 intervention years, and a final one-year observer check. The failed setup pilot is retained separately. There are no arbitrary coefficient changes or injected money, goods, people or skills. Controlled fixtures deliberately edit vacancies, candidate stress, cash placement and disconnected roads to isolate admission/departure rules; they are not unassisted mayor play.

## Priority: a departed household can cause duplicate occupation

**Confirmed in all three seeds, and observed later in an ordinary town.** The real monthly refill and annual estate-refill paths do not share an authoritative vacancy check:

1. `outwardMigration()` empties a household but leaves its `home` reference for its external financial/estate record.
2. `occupyVacantHousing()` correctly fills the vacant cottage and changes `building.hh`. It does not clear the departed household's stale `home` reference.
3. `yearlyDemographics()` sees that old empty household and existing building, then calls `addHouseholdAt()` again. It does not check whether another household now occupies the building.
4. `addHouseholdAt()` checks aggregate job vacancies and funding, but not actual unit vacancy. A second two-person family is admitted into the same one-household cottage. It is not registered in `building.hh`.

The controlled normal-function sequence produces resident households 67 and 68 in one cottage in seeds 42/101/909. Cash stays conserved. **Both `validateTown()` and save reload accept the duplicate occupation.** This is a physical-capacity/population defect that the conservation gates miss.

The unassisted seed-42 passive run first records the problem on day 5760. Over the 30-year intervention it accumulates 16,208 unregistered-household-days and 15,308 over-capacity-building-days. These are cumulative occupancy diagnostics, not counts of distinct families. The other five ten-year histories do not reach this failure in their recorded horizons.

Proposed minimal fix: centralize successful tenancy registration, clear only the replaced *empty* household's stale tenancy reference, and require genuine available unit capacity before every household arrival. Add a defensive vacancy check to `addHouseholdAt()`. Keep departed owners' titles, deposits, loans and estate records intact. Extend validators to check live household registration and physical unit capacity. Existing over-occupied archives need an explicit rehousing/migration policy; do not silently delete residents or their assets. No shared production code was edited here.

## Migration currently follows headcounts more than offers or budgets

The new-household gate requires at least two net private vacancies after current jobseekers, town employment of at least 88%, available regional startup cash and the population ceiling. Those are real constraints. However it does not assess a funded, reachable job offer, expected wage-minus-living-cost budget, local service access or an outside alternative.

With the same seeded candidate and controlled sufficient vacancies, all three seeds:

| Candidate change | Admission |
|---|---|
| Normal funded connected case | Accepted |
| No vacancies | Refused |
| Sole vacancy employer has zero cash | Accepted |
| School, health and fire authorizations zero | Accepted |
| Rent index at its ordinary 1.5 target ceiling | Accepted |
| Legal minimum and offered wage reduced to $10 | Accepted |
| Candidate home disconnected from workplaces | Accepted; both new adults remain unemployed |

In seed 42 the low-wage entrants have estimated net earnings of $17.60/day against the existing credit model's $33.71/day essentials estimate. The disconnected entrants have zero prospective earnings. Each accepted household still receives exactly $2,500 transferred from `G.region`; there is no currency creation. Initial savings can legitimately finance a transition, so a temporary deficit is not proof that every such move should be prohibited. The confirmed gap is that neither financial runway nor access influences the admission decision at all.

The separate 45-day individual-arrival path uses high aggregate employment/low hardship, any open firm vacancy, a random existing household and its size. It has no destination/origin, offer, financial transfer or outside-living-cost comparison. No extra wallet money is created when someone joins a family. The current outside region is a conserved aggregate counterparty, not a simulated population with competing local job/housing offers.

Proposed next interface: one shared migration assessment with a reachable job candidate, credible paid wage, actual available home/unit, after-tax essentials and moving runway, plus a small explicit outside-option record. Record origin/destination, reason, age/skill and funds brought/taken. A compact explanation such as “two vacancies exist, but neither reaches this home” is preferable to an unexplained population roll. Do not invent complete foreign-city simulations or force a uniformly affluent entrant population.

## Emigration can depend on wallet placement rather than spendable wealth

**Matched equal-wealth defect in all three seeds.** Under identical severe town stress and the same random draw, a household leaves if its fully withdrawable savings are banked, but stays if the exact same funds are withdrawn into its wallet:

| Seed | Identical household liquidity | Banked: people leave | Wallet: people leave |
|---:|---:|---:|---:|
| 42 | $1,954 | 3 | 0 |
| 101 | $1,768 | 2 | 0 |
| 909 | $1,968 | 3 | 0 |

`outwardMigration()` filters on `h.cash`, whereas hardship and other affordability rules use `householdLiquidity(h)`. The banks can actually pay the tested withdrawals. This is not a legitimate difference in economic resources. Use redeemable savings/essential-cost runway, not wallet cash alone, while retaining genuine safety/service/stress reasons to leave.

Existing financial exit treatment is mostly explicit: departing people leave employer rosters, their wallets transfer to the region, deposits remain bank liabilities of the external household, and titles remain unchanged. A normally approved $100 loan in seed 101 remains owed after departure; the next payment withdraws deposits and reduces principal to $99.7222. The normal lender declines the other two candidate loan requests; they were not forced through. No disappearing debt or free estate balance was found in these cases. There is no separately modelled destination portfolio or migration-cost invoice.

## Birth/death accounting and correction to the earlier laboratory

The new observer identifies births **inside `birthsAndGenerations()` before annual ageing**, then reconciles population after every simulated day:

`closing residents = opening residents + births + immigration − deaths − emigration`.

Seed 42 starts the intervention with 178 residents and ends with `178 + 292 + 197 − 29 − 2 = 636`. This reconciles all 10,800 days. The other natural histories also reconcile daily.

The earlier balance laboratory inferred births from age zero *after* `tick()`. On an annual day a newborn can already have become age one, so the old audit misclassified those births as immigrants. Its first-year seed-42 split was 7 births/20 immigrants; the correct split is **11/16**. Population and financial totals are unchanged. The old tool and a prominent historical-evidence correction are pushed separately in commit `89730e5` on `codex/8-balance-lab`; do not reuse its original birth/immigration split. Raw old measurements have not been rewritten.

Annual whole-population ageing itself is a model shortcut: the seed-101 fixture shows a newborn turning one on the same annual day. Birthdays/creation dates would improve cohort realism. Deaths are currently age-driven, rather than a full health/mortality model. The retained observer captures birth and funded-household creation ages directly; inline family-join entries have their exact end-of-day ages but a null creation-age field. These limits are explicit, not inferred medical or real-world demographic claims.

## Why passive towns accumulate millions

**The main cause is default service underspending, not missing cash charges or large quest rewards.** The nested flow observer accounts for each exclusive treasury delta, avoiding double-counting payroll taxes returned to government. In seed 42 over ten intervention years:

| Cash source/use | Amount |
|---|---:|
| Income tax | +$2,856,635 |
| Business profit tax | +$1,505,809 |
| Property tax | +$780,154 |
| Other taxes/permits | +$392,948 |
| Regional ambition grant | +$6,500 |
| Public operating purchases | −$2,177,938 |
| Aid, pensions and remaining household programmes | −$1,487,498 |
| Automatic public construction | −$14,900 |
| Net treasury change | **+$1,861,709** |

Opening cash of $109,191 therefore becomes $1,970,900. The $6,500 residual is consistent with the bounded regional ambition-grant transfer, not millions of minted rewards. The final observer separately labels such future grants. The original long-run ledger keeps the residual label and reconciles it honestly.

At that point the default $70 health and $90 education budgets buy only **31.3% health coverage and 15.0% schooling coverage**, with required daily operating funding of $223 and $601 respectively. Public health has fallen to 34.9. At year 30 it reaches the model floor of 25 despite $1.27m cash and $6.20m in paid regional reserve claims. Reserve purchases are financial assets, not service spending; cash plus claims must not be confused with immediately spendable regional cash.

A matched alternative changes only legal operating authorizations monthly, using the existing population/staffing and road-upkeep standards. No extra tax, grant, forced labour, annexation or construction command is supplied:

| Seed | Default cash, year 10 | Service-oriented cash | Default health | Service-oriented health |
|---:|---:|---:|---:|---:|
| 42 | $1,970,900 | $35,122 | 34.9 | 99 |
| 101 | $1,831,938 | $12,409 | 41.0 | 99 |
| 909 | $1,618,147 | $132,675 | 42.9 | 99 |

The alternative's schooling coverage is 83.1–100%, care coverage 99.4–100%, employment 100% and hardship zero at year 10. Populations differ because employment and demographic paths respond to the intervention; these are matched model paths, not isolated real-world policy estimates. Two towns authorize the $500 education ceiling; actual constraints still differ. Seed 101 remains limited by one school and its access/capacity, whereas seed 909 purchases the $500 ceiling against a larger operating requirement.

Actual operating payroll/supplies, pension, aid and road purchases already exist. Public budgets do not automatically rise with population or impose a minimum service obligation: default settings can leave services underprovided while reserves grow. Calling that an informed voluntary choice would overstate the current explanation. There is also no distinct routine municipal building-depreciation/repair account: operating purchases are not a complete physical asset-maintenance model. Explain required versus authorized versus purchased capacity and the resulting health/access first; do not create arbitrary penalties merely to empty the treasury. The earlier “passive prosperity” conclusion must be read as **passive fiscal accumulation**, not a healthy, physically well-housed city.

## Reproduction and limits

```sh
python tools/audit_migration_budget.py
python tools/audit_migration_flows.py
# Short observer check:
python tools/audit_migration_flows.py --seeds 42 --years 1 --passive-years 1 --strategy passive
```

Use separate `--out` paths for independent runs. JSON writes are atomic. Install the repository's `requirements-test.txt` and Chromium. Maximum natural-run cash drift is $0.0001782; treasury reconciliation error is $0.0000542; commodity error is 3.89e-9. Those financial gates pass while the new housing diagnostics deliberately expose structural failures. The final observer reproduces first-year economic/demographic results exactly. These are frozen-source model findings, not human playtesting, physical-device certification or a claim that migration is calibrated to a real country. Shared economics edits, archive repair policy and UI changes remain proposed for the lead.
