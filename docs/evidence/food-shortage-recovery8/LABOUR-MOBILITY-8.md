# Labor mobility and grocery staffing, version 8

**Branch/source:** codex/8-balance-lab based on `d40b954f8f4e63f7b4347eadc1595e81bcbe7cb5`; corrected bundle SHA-256 `affae2d0365cc9bffdb6858fda184f9495c5304d2b2900ae152234a6b9e01d6c`. Deterministic matched histories and worker traces are in [grocer-capacity-response.json](grocer-capacity-response.json); the pre-fix 30-day evidence is retained in [grocer-capacity-response-prefx.json](grocer-capacity-response-prefx.json).

## Cause and narrow fix

Workers did not switch employers while employed. `assignJobs()` fills vacancies only from eligible people who are already jobless, can reach the job from home, and are inside the commute limit. Employees become available again when employers cut job slots, firms close, workers age out, or a commute/payroll failure releases them. The scheduler then ranks vacancies to allocate that available pool.

The ranking used each firm's nominal `f.wage`, but payroll and worker-facing pay use `workerIncome(f) = max(policy.minWage, f.wage)`. In the pre-fix regional seed 909 after a 120-day gateway-road interruption and a 120-day reopening, the city had no free workers, 72 vacant jobs, and 12 vacancies across 13 groceries. Grocery offers averaged about $30.8/day against an all-sector median around $32.4/day. Staffed-and-stocked retail capacity was 1,120 against need of 1,137.6; late shoppers missed 17.6 units that day, and the prior 30 days recorded 2,627 unmet units. Many grocers held cash, but had no unassigned workers available. A mayor-built grocer received stock and two job slots yet stayed unstaffed and sold nothing.

The mismatch mattered under a statutory wage floor: vacancies with different nominal wages but identical actual pay were still ordered as if they paid different wages. I changed the comparator to rank by effective pay, with firm ID as a deterministic tie-break. No production, wage, migration, or capacity coefficients changed.

## Matched outcome

The same seed, road-interruption/reopening harness, and 360-day continuation on the corrected bundle started with 710 residents, full employment, 35 vacancies, 11 open groceries, 19 grocery workers, and 1,520 sellable units against 1,136 daily need. With no mayor intervention, the full 360-day history had zero unmet-food days and zero unmet units. Population reached 785; housing units rose from 328 to 350; and grocery capacity ended at 1,360 against 1,256 need. An exact one-year replay matched byte for byte. Cash drift stayed below $0.000007 and goods-account error below 0.000000003 units.

This changes the interpretation of the earlier shortage evidence: in this seed and history, wage-priority allocation was the primary cause of the observed throughput gap. No broad wage hike or invented labor was needed. The new-home-only action also selected actual higher-paying factory openings (about $32.24 and $32.30/day); both residents had reachable commutes, which is the expected outcome when those offers beat grocery pay.

A regression also raises the existing minimum-wage policy from $28 to $34/day, builds one ordinary home, and checks immediate allocation. Both new adults are reachable; one receives a grocery job at the actual $34 floor and the other takes a mill job at the same floor. This verifies the effective-wage tie-break. The no-policy and wage-policy year arms both had zero unmet-food days after the comparator fix, so this test does not claim that $34 is needed or recommend that wage. Raising the floor affects every employer.

## Other observed labor and housing rules

New households require real vacant housing and a job market with at least two more vacancies than active jobseekers; admitted residents receive capital from the regional account, then use the normal vacancy allocator. The post-fix natural history showed zero to one empty housing units at sampled month ends, high housing pressure, and automatic construction. Newly employed household members had reachable commutes. This run did not find transport access or household affordability to be the binding obstacle.

Direct voluntary job-switching or poaching is absent. Movement across employers happens after an old job slot is released and a worker becomes eligible for the shared allocator. That is a simplified labor market, but wages paid and vacancy ranking now agree. The city's development-demand estimate still does not use food shortfall or staffed retail capacity; that separate investor-forecast gap remains outside this fix.

## Verification and limits

`python tests/test_grocer_capacity_response.py` passed the effective-wage placement regression, matched home/grocery actions, town validation, cash and goods conservation, and exact one-year replay. `python -m py_compile tests/test_grocer_capacity_response.py` and JavaScript bundle assembly/check passed. The road closure is a deterministic test-only removal of external gateway tiles, not an in-game closure control. This is one regional seed and one scenario; it establishes the code-path inconsistency and a reproducible correction, not broad balance or real-world labor behavior.
