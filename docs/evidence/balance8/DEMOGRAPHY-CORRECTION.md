# Correction to the original demographic split

The 45-history evidence retains its original measurements. Its birth/immigration split is unreliable: `balance_lab.py` originally inferred a birth from a newly created person's age being zero **after** `tick()`. On an annual day, `birthsAndGenerations()` creates newborns before `yearlyDemographics()` increments their ages. They were therefore wrongly counted as immigrants.

The follow-up source-hook audit detects births immediately inside `birthsAndGenerations()`, before annual ageing, and reconciles the population identity each day. In the matched seed-42 first intervention year, the corrected counts are **11 births and 16 immigrants**, versus the original 7 and 20. Both sum to the same 27-person population increase. The old population, employment, fiscal, distribution, cash and commodity results are unaffected by this classification error. Their source hashes and raw evidence have not been rewritten.

`tools/balance_lab.py` now uses source-identified birth IDs. Re-run it to obtain corrected demographic splits. The new migration audit provides explicit arrival, departure, birth and death events rather than treating the old split as valid. A newborn becoming age one on the same annual day is also a separate engine modelling limitation reported to the economics lead; no engine rules were changed here.
