# Settled loan retention: boundary repro and scoped fix

Base 1380bd6. This commit owns loan retention only; firms, households and persons
are not deleted, renumbered or frozen. Generated bundle is excluded for integration.

A valid 10,000-record loan archive accepts a real new bankLoan and then rejects its
own 10,001-record export. The fixture first originates and repays an actual $100
loan through loanPayments, clones the completed receipt into synthetic historical
IDs, verifies import at the boundary, then originates the next real advance. It
is not presented as 10,000 naturally simulated loans. Original negative retained.

The existing daily routine already discarded non-active history above 2,500 rows,
including positive default balances still used by bankCompetition's recent-loss
calculation. It also did not run before a new advance. Simply keeping that routine
or blocking all lending at the historical count is not a safe long-play solution.

compactSettledLoans now runs before issuing new credit and at the existing daily
retention point. Only repaid receipts with balance exactly zero and complete finite
original/paid amounts are eligible. It retains recent detailed rows toward 1,800;
older discharged receipts are summarized by borrower identity and bank identity,
with counts, original principal, total paid and highest retired ID. Global summary
counts/sums are not cash transfers. nextLoanId remains monotonic. This preserves
financial totals/parties while compacting per-receipt terms, rather than claiming
full original-document retention. Previously those receipts were simply erased.

All active loans, every default balance/status and incomplete legacy receipts remain
unchanged. If all 10,000 rows are protected obligations, a new advance is explicitly
declined before disbursement; claims are not erased to manufacture capacity.
The ordinary borrower credit-decision UI reports why. This exceptional protected-
claim ceiling is communicated, not a general freeze caused by settled history.

Optional settledLoanHistory version 1 is structurally validated on import. Its
borrower and bank keys reference existing retained identity records. Future
household/firm archival work MUST preserve or explicitly remap these references;
no identity arrays are shortened here. Older archives without the field still load.
The summary is available in exported records; no new financial UI is authored.

Tests: the real next advance succeeds after automatic compaction (1,801 detailed
rows); principal/cash remain conserved; active/default/incomplete-legacy rows stay
byte-identical. A 10,000-default boundary refuses new credit without erasing claims.
Malformed negative summaries reject atomically, thirty-day continuation is exact,
authentic legacy fixtures and core deterministic/conservation gates pass. Source-
bound receipts are under docs/evidence/loan-retention8. No whole synthetic archive
is published. This is not a new one-hour acceptance or an unlimited debt-ledger
claim. Other entity creator/importer boundaries still require separate safe designs.
