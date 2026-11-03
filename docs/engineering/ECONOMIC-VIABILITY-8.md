# Contracts and independent service viability

This phase follows integration checkpoint `ce8695c`. It addresses operating causes found in the actual-control play audit, rather than guaranteeing commercial success.

## Confirmed causes and changes

The current staged-logistics replay already fulfilled the old audit's 600-unit manufactures agreement. The older failure is therefore not presented as an unchanged universal defect. A separate reproducible food-supplier case exposed the structural problem: every supplier retained an entire town food buffer, and contracts could request only yesterday's leftovers before production. Contracts now retain the supplier's normal working stock (`max(10, 0.8 × observed sales)`) and receive current output above it before ordinary spot exports and local wholesale buyers. This is an explicit allocation choice: shops may require more imports. Goods on retail shelves are unaffected.

`regionalContractForecast(f, market, good, ceiling)` reports working reserve, free stock, observed production trend, existing unshipped promises, dispatch window and estimated/suggested quantities. The buyer's 200/600-unit district ceiling remains. A smaller forecast-sized commitment and a disclosed risky full window are separate choices. Queues, cash, input availability and staffing can invalidate forecasts. No fresh contract cargo dispatches when its current route estimate is already too late. Paid cargo continues travelling; missed promises remain missed. Forecast capacity is conservative when today's shared market allocation is exhausted; it is not a delivery guarantee or an optimization solver.

Private schools' forecasts counted customers already purchasing from incumbent providers. Their job plans also reduced advertised positions without releasing excess workers, preserving excessive payroll. Actual per-household purchases are now recorded by provider, and entrants forecast only remaining customers. Family fees share one affordability budget across providers; targeted vouchers share their real authorized budget. A one-dollar voucher authorization no longer represents a blanket demand multiplier.

Staffing follows smoothed purchased-client demand and actually releases excess positions. One teacher can operate a 16-place school; brigades retain a two-worker minimum. Site proposals include connected qualified workers and the wage needed to attract them, actual family affordability, public/private competition, operating costs and capital return. Closed sites require two viable demand reviews at least 30 days apart before recapitalization. Persistent unfunded private operations also have an independent 90-day distress clock, so zero-payroll providers cannot remain indefinitely active because generic loss counters cancel each other.

A brigade invitation before the founding town has earned income is correctly rejected in the controlled entry case: 58.18 affordable memberships cannot cover $78.10/day costs. After a normal daily payroll settlement, real control-driven school and brigade entry both pass. No customer cash, staffing or subsidy is granted by these entry tests.

## Interfaces for integration and player feedback

- `privateServiceDemand(kind, site, excludeFirmId)` is residual potential demand; exclude an incumbent to forecast its own existing market.
- `privateServiceForecast(kind, site, fee, staff, excludeFirmId, wageOffer)` returns clients, capacity, fee, staff, wage, revenue, payroll, overhead, profit and net. Forecasts do not transfer money.
- Runtime `G.privateServiceProvision.allocations[firmId][householdId]` records actual served/paid/subsidy; it is derived daily and cleared on archive load.
- Optional persisted firm fields: `serviceClientTrend`, `serviceWeakDays`, `serviceRecoverySince`, and producer `productionTrend`. Old saves need no invented history.
- Private construction preserves `serviceStaff` and `serviceWage` alongside its real escrow; completion must use these values. Preserve this hook when reconciling urban construction changes.
- `dispatchRegionalContracts()` runs during logistics settlement and immediately after actual production, before spot sales. Preserve this ordering when adding passenger payroll/transit hooks. It does not change freight road connectivity.
- Provider inspection shows forecast customers, payroll, costs, net result and recapitalization requirements. Trade review discloses priority, smaller commitments, margin limitations and late-delivery risk.

## Evidence and limits

`reports/integration/8-economic-viability.json` identifies exact source and results. Compressed full before/after actual-control traces are retained beside it. Two fresh-town strategies each cover about six game years (60 minutes at 1×), not 60 minutes of human playtesting. They use normal controls and clock acceleration, with no resource grants. The post-change routes contain 45 major decisions and 210 button clicks collectively.

Before: two trade-route schools close five times each; community schools close twice and once. After: one school closes once in each route, without a repeating recapitalization cycle. Commercial failure remains possible. Three additional seeds over three years record at most one closure per provider. The whole strategies diverge in later external random events; their outcomes are not isolated causal estimates or a claim that every civic metric improves. In particular community learning coverage is lower in the new trajectory and remains a real service-management pressure.

Controlled tests additionally cover incumbent competition, unaffordable demand, small voucher budgets, released positions, genuine paid learning, zero-fee failure, two-review recapitalization, live school/brigade controls, supplier working stock, fresh-output allocation, impossible promises, cash/goods conservation and atomic malformed-save rejection. Core replay/migration/pause and existing freight accounting remain required. Host browser timing does not establish Android performance or human enjoyment. Urban/transit integration and final acceptance remain pending.
