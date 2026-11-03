# Staged-order stress and capacity correction

Parent production checkpoint: c11196f1900a4d4e261956b5df8fdc09a2200adc. Source hashes for both experiments are retained with the raw results in docs/evidence/procurement-stress8.

Confirmed defect: after normal daily trade, the regional seed42 town rejected staged orders because the review multiplied today's *remaining* market/loading allowance across every future dispatch day. The town had functioning daily capacity, but an exhausted current-day allowance advertised zero future capacity. Corrected only the planning envelope: use the named market's minimum cyclical daily capacity and currently staffed quoted-depot capacity, capped by the existing 120-unit consignment limit. Outstanding commitments remain deducted conservatively. Actual loading, market limits, dispatch and settlement are unchanged.

Eight bounded histories compare normal supply, cancellation between stages, controlled supplier liquidation, and temporary adjoining-road removal with paid reconstruction, in actual 169- and 657-resident towns. All have one competing ordinary agreement on the same grain producer. Initial 50/100 milestones are tried first; a 10/10 fallback is explicitly recorded if needed. After correction both towns admit the full 50/100 order. Separate food-order eligibility is recorded, with local food stocks and hardship sampled; that quote does not itself authorize another food order.

Both normal orders fulfill both milestones. Controlled liquidation produces two missed milestones with zero delivered. A real 5000 bank loan is approved before liquidation in each closure case; asset proceeds repay it fully. These cases therefore test solvent estate repayment, **not** a reproduced default or creditor loss. Prior focused estate/default accounting evidence remains separate.

Cancellation at day16 preserves a fulfilled first stage and marks the second cancelled. All100 second-stage units had already been dispatched, so they still arrive. Cancelled status is preserved rather than rewritten into fulfillment. Travelling cargo and liabilities are not erased. This is an important player-facing distinction: cancelling an agreement stops new dispatch, not an existing shipment.

Temporary road removal does not cause missed milestones in these layouts; already-dispatched cargo, alternative reachability and the available delivery windows permit fulfillment. Do not present this as proof of recovery from complete isolation. Every daily cash/goods/town check passes; maximum endpoint cash drift is below 0.000004. Exact ten-day save continuation/replay passes for every admitted outcome. No extra cash is granted for recovery.

A separate labelled synthetic history fixture fills the 24-record ledger with completed ordinary records while a real cancelled group's cargo travels. Another grouped authorization prunes other history and preserves both original linked records and their actual cargo. No reliability reward or persistent score exists to be lost on pruning. Malformed orphan rejection remains covered by the focused procurement suite.

Reproduction: python tests/test_procurement_stress.py. Existing procurement and supplier-selection suites also pass on the corrected assembled source. Scope is two seed42 city sizes, eight short scenarios, not a general economic or performance certification.

Player explanation: A staged order is two arrival deadlines sharing one supply chain. A forecast is not reserved production. Keep working food stocks and freight cash, consider competing promises, and leave time for queues and travel. Cancellation stops future loads; paid cargo already travelling still arrives or follows its return/recovery rules. The supplier receives actual sales receipts; town hall receives no completion reward.
