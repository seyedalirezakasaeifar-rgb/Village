# Loan retention and regional creditor correction

Integrated loan-only change 8be6a94. Only complete repaid zero-balance receipts compact into borrower/lender totals. Active obligations, defaults and incomplete legacy receipts remain. Full protected capacity refuses new disbursement; next IDs remain monotonic.

Independent review reproduced an existing boundary inconsistency: bank resolution transfers active loan rights to regional creditor `bankId=-1`, but archive hydration rejected all negative bank IDs. The new summaries also rejected their legitimate `banks['-1']` regional bucket. Fixed both validators to accept exactly the engine's -1 sentinel while retaining real local-bank references and rejecting -2. Updated the malformed-bank regression to use the unsupported -2 instead of misclassifying the legitimate sentinel.

The new test resolves an actual bank, repays the transferred real loan, then uses explicitly synthetic repeated historical receipts to cross the retention boundary. Before fix the historical archive is rejected. After fix self-export/import and thirty-day canonical replay pass, with cash preserved. Summary validation now also checks monotonic-ID metadata, canonical owner keys and borrower/lender count/principal/payment totals. Four malformed-summary imports reject atomically.

Three source-matched gates pass in `reports/integration/loan-regional-retention-8/receipt.json`: regional resolution/compaction/replay, ordinary/protected loan-retention boundary and composite cross-system save faults. Broad core and final native/endurance gates are still required after queued integrations.

Separate performance experiment 3362827 on `codex/8-retail-proposal-reuse` is rejected and not merged. Six warmed 180-day pairs match full model/RNG, but baseline/candidate medians 4785.70/4771.95 ms and only three favorable pairs establish no consistent model-level gain. Production retains the original retail scans.
