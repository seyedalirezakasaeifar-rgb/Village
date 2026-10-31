# Independent cooperative persistence boundary attacks

Tests-only branch based on prototype `e68ff5fe2d4ced7396e4fa204930cf92dbe193a0`.
The requested abbreviated ecd02e3 was not a fetchable ref; the published prototype
branch was resolved explicitly and the parent confirmed this latest checkpoint.
No scheduler, economic, native or presentation production code is changed.

`tests/test_cooperative_save_faults.py` reuses the owner's hold/pump instrumentation
and independently attacks all 115 actual yielded boundaries of a small seeded
month-end day over a real HTTP origin: 1,035 cases, zero failures, terminal exit 0.
Cases include save acknowledgements deferred until commit, synchronous export,
native bridge suspend and Back, invalid/valid imports, founding, queued exactly-once
cash transfer and injected iterator failure with deferred save rejection/rollback.
Each case compares every archived field except the existing traffic/visual state
exclusion to the synchronous tick oracle, verifies valid structure and explicitly
sends the old task token after completion to confirm it is inert. Import/founding
compare to the replacement town; failures compare to the prior completed town.

The named migration filter/assessment yields are individually tested, rather than
merely probing the dailyEconomy boundary. Full per-boundary results bind the exact
assembled source SHA in `docs/evidence/cooperative-save8/boundaries.json`. The
prototype remains disabled by default. These are browser function/bridge attacks,
not physical native UI acknowledgement or touch/multitouch certification. The
owner's separate post-fault continuation and trusted-input tests remain relevant;
this suite does not claim a late-city pause bound or performance result.

The frozen 662ec6f hour is unchanged and no duplicate hour was started.
