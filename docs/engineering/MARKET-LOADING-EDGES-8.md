# Market loading choice edge checks

Five requested cases were run against a real paid peak-arrival queue fixture. Result JSON records treasury, total cash, priority, relief expiry and individual waiting shipments before and after every action. Source SHA-256 is stored alongside it.

- Empty queue: review denied with explanation; state unchanged.
- Insufficient treasury ($0.35, less than one $0.36 handling unit): review denied; no payment/state change.
- Repeated confirmation: first authorization succeeds; second stale authorization is rejected; policy/expiry and money are unchanged after the rejection.
- Queue changes after quote: advance one actual simulation day, then authorize old review. It is rejected; post-advance state remains unchanged by that rejected action.
- Gathering cancellation: prepare a real public square gathering, quote loading choice, cancel the gathering, then authorize the old loading quote. It is rejected; cancellation and municipal cash remain unchanged by rejected authorization.

All five pass. Empty/poor/repeat/stale/cancel checks preserve total cash. The queue-change case records ordinary one-day simulation purchases and cash changes separately, then verifies old-quote rejection changes neither. No production fix was indicated.

Reproduce: `python tests/test_market_loading_edges.py`. The existing focused loading-choice and civic-calendar suites also passed in the preceding integration turn. This test checks game state and spending outcomes; it does not certify Android UI performance.
