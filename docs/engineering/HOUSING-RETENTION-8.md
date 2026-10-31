# A household at the council door

Once a month, the council may receive a non-interrupting letter when one of the eight lowest-cash occupied households has a real emigration assessment: a persistent local budget deficit, under ninety days of spendable essentials, financial distress, and a better outside reference. The case names the household and reports its live budget and outside comparison. It is not generated from town-wide hardship alone.

The mayor can transfer exactly fourteen days of the assessed local shortfall (capped at $3,000) from municipal reserves to the household, or adopt the existing `Learning within reach` civic project for that family. The first choice offers short-term runway without promising retention or a job. The second makes no immediate transfer, but requires actual funded school access and a completed adult training term. Existing skills work is not overwritten; if one is active, the alternate option preserves the reserve. Defer keeps the letter available.

The assessment and quoted amount are recomputed immediately before either choice. An improved or otherwise changed case is rejected without charge. Household transfer uses the normal council paid-choice settlement path, so reserves fall by the displayed amount, the named household receives it, and total money is conserved. Council inbox and civic-project state use existing save fields and save hooks.

`tests/test_housing_retention_dilemma.py` exercises actual Agenda and decision controls, save/load and defer, the training-project path, an exact cash transfer and total-money conservation, then changes the target household before authorization and confirms the stale offer cannot debit reserves. `node --check assets/game.js` passes.
