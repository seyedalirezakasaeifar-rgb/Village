# Credit, household budgets and physical markets

This is unpackaged development after the signed 7.0.5 checkpoint. The checkpoint APK does not contain this work. A new version freeze and complete immutable release gate are still required before delivery.

## Player-visible changes

Household inspection now explains the latest credit decision, stressed payment capacity, scheduled debt service, work and shopping travel, service receipts, and daily versus cumulative burglary losses. Firm inspection distinguishes contracted and attending workers, installed capacity, and paid equipment awaiting a dated commissioning. Economy reports missed payments, the investment pipeline, disrupted commutes and residents without a reachable grocer. The tutorial explains service geography, recruitment, adult training, credit and commissioning delays; the starting briefing links directly to Services.

The trade switch is labeled **Regional inventory imports**. It controls imported goods and regional construction inputs, rather than claiming to close every external service or financial relationship.

## Mechanisms and corrected errors

- Household borrowing uses observed net income, income variability, essential costs and liquid reserves. A higher quoted rate is tested with an additional two percentage points of rate stress and a coverage margin. Firms must support debt from observed earnings and working-capital reserves. Declines distinguish standing, liquidity, bank reserves and repayment capacity. These are transparent game rules, not real underwriting advice.
- Household debt is paid after essential purchases and commuting, before optional consumption. Existing deposits can be withdrawn subject to actual bank liquidity. A once-per-day loan guard prevents duplicate collection. Public care/teaching wages and rental receipts are settled before household purchase decisions; optional spending also reserves the later property-tax bill.
- Firm interest is recognized when due, including unpaid interest capitalized into the loan. Lenders receive only actual paid cash. Bank quotes respond to impaired active portfolios and recent defaults. New bank charters do not inherit retired institutions' loss history.
- Equipment requires useful demand, workers, inputs, retained cash and an investment-return test. Its purchase transfers cash to the regional supplier immediately. Capacity arrives after 30 days; pending orders cannot stack. Idle output capacity does not justify an equipment order merely because the owner has accumulated cash.
- Grocers compete on the taxed basket price plus a road/metro shopping journey. A disconnected shop cannot supply a household by teleporting goods. Retail demand and ordering consider the reachable population; retail staff and inventory still bind. The deterministic daily shopping order rotates so a permanently low household ID does not always receive scarce stock first.
- Disconnected employees cannot supply paid work or production. A temporary interruption retains the contract, permitting recovery after a road repair. After 30 blocked days the employee searches for a reachable job. The household and Economy reports distinguish interrupted access from an ordinary vacancy. No fare is collected for a commute that did not happen.
- Daily business books close after interest, road charges, incidents and repairs. Grants and recovered losses are separated from sales; one-off recoveries do not inflate the sales forecast. Household daily flow no longer repeatedly subtracts the cumulative burglary total. These fixes change reported margins and subsequent decisions as well as labels.

Goods and cash retain explicit counterparties. Credit creates matching claims and obligations; capitalized unpaid interest does not create cash. Inventory cost is recognized on sale or use, with purchases shown separately from operating costs.

## Development evidence

Frozen assembled source SHA256: `cd95b60f6cb9566cdf633342011dc17cbea3fc7c7960eb4cb7ce4b4f1b1296f4`.

Targeted browser probes cover rate/income-volatility affordability, invalid negative requests, payment priority, same-day public income, once-per-day payments, capitalized interest, portfolio-risk pricing, funded and delayed equipment, idle-capacity restraint, disrupted shopping/work, delivered prices, road repair recovery, cash conservation and atomic rejection of malformed financial metadata. Existing operating-statement tests now include non-sales income explicitly in their reconciliation.

Thirty matched two-year histories start from identical 60-day snapshots: three scenarios × two seeds × baseline, higher policy interest, higher minimum wage, inventory-import suspension, and suspension followed by reopening. Every monthly operating statement, goods balance and town structure passed validation. Maximum currency drift was 0.00002536. Monthly baseline employment never fell below 76%. No loan defaults occurred in these healthy histories, so they do not certify severe credit-crisis recovery.

The matched choices produce path-dependent tradeoffs rather than predetermined rankings. In settlement seed 42, capital spending was $107,320 at baseline, $92,460 under the higher rate and $68,090 under the higher wage, while the higher-wage households received more payroll and health/education outcomes fell as operating wages rose. In regional seed 42, stopping inventory imports left 100 firms and about $734,211 public cash after two years versus 102 firms and $912,707 at baseline; reopening after six months followed a distinct recovery path. Some self-sufficient towns barely changed when inventory imports stopped. None of these comparisons establishes a universally best policy or calibrated real-world prediction.

The core release gate checks deterministic replay/continuation, malformed-save atomicity, legacy migration, zoning comparisons, cargo ownership, unchanged paused pixels and valid traffic. The Council/import-draft and repeated all-panel/save workflows also pass. These development checks do not replace the final full candidate gate or physical Android playtesting.

The isolated 2,000-resident 64× host-browser run retained the new mechanisms: draw p95 27.5ms, tick p95 13.0ms, reported speed 63.3× and panel response to the next frame 17.9–33.5ms. The test now embeds and checks its source hash. These are host measurements, not Android FPS; occasional longer scenery work remains a profiling target.

Screenshots at 844×390 and density 2 are in [previews/credit-markets](previews/credit-markets), with exact source provenance. Reports and synthetic histories remain local under `reports/development-credit-markets`; no private saves, keys or diagnostic logs are committed.

## Limits and next work

This remains an original stylized model with explicit gameplay parameters. It does not model every household preference, every credit product, depreciation, a calibrated national price system or real credentials. Regional service demand and external finance remain abstract counterparties. Commute connectivity is physical, but daily travel charges still use the existing distance abstraction rather than a complete travel-time model.

Healthy default towns often reach full employment. That is evidence of stability, not proof that the game always offers an interesting decision. Scenario ambitions, delayed consequences and accessible feedback need a dedicated player-loop pass. Native device performance/lifecycle/file-picker checks, long-session memory tests, final balance review and immutable source-to-APK verification remain outstanding.
