# Archive record integrity — scoped QA handoff

Base: `525e47dd3967741fb59d2fd06921c1647a29a24a` from `codex/townledger-7.0.1`.
Branch: `codex/8-save-qa`. This checkpoint actually declares **schema 8** in
`release.json`; no schema/version change is introduced here.

## Reproduced defects and fix

The base accepted an archive with a living resident removed from their household,
negative commodity stock, negative deposits, a loan referencing bank -1, a reused
building ID counter, orphan employment, duplicate home IDs, and missing property
or enterprise references. These were accepted by the import API even when the
result immediately failed town validation. Malformed bank/loan records could also
be silently discarded by filtering. Original negative evidence is retained in
`docs/previews/save8/before-negative-evidence.json`.

`validateArchiveRecords` now checks the candidate's financial/identity graph before
adoption. Property references use a Map of stable building IDs; tile indexes and
array offsets cannot stand in for titles or home addresses. Closed demolished
firms retain their permitted historical reference to a removed building. Empty
estates retain their historical household record. Loan bank indexes must be
nonnegative. No balances, goods or people are repaired or invented by these checks.

Object imports are cloned before normalization/validation. A valid import cannot
alias caller-owned arrays and wallets, and candidate defaults or normalization
cannot change the caller's object on a rejected import. Existing string archives
retain one JSON parse. The clone adds bounded work to object import only, outside
the running simulation/render loop.

Production scope is `src/90-archive-panels.js` plus its assembled bundle. No
simulation, renderer, transit economy or native host implementation is changed.

## Evidence

All final JSON reports in `docs/previews/save8/` bind to assembled source SHA-256
`17297afbea134d5259b60ba6db500af1444328b1a0f0c91e71b5b6c1460f8e54`.

- New `tests/test_save_adversarial.py`: 25 malformed record graphs plus four
  truncated/raw cases at founding, after 360 regional days and after 720 hard-times
  days; byte-identical running archive, RNG and persistence timeline on rejection;
  caller independence on success and failure; 90-day exact canonical continuation
  from each checkpoint; both committed historical JSON fixtures accepted.
- New `tests/test_save_composite.py`: controlled 1,375-person 128 atlas, two actual
  transit routes, a paid settled passenger receipt, 18 live cargo consignments,
  $6,000 provider escrow and $28,000 mall escrow. Restore preserves receipts,
  authoritative cargo/routes/projects and total cash. The same 29 rejection cases
  preserve the complete running state. Catchment growth is a controlled fixture,
  and its extra passenger uses the real reserve/settle APIs.
- Existing save chronology gate: all 12 fault checks pass, including quota,
  interrupted IDB transactions, disagreement, same-day changes, wall-clock rollback,
  stale callbacks, restored/new timelines, late heads, ambiguous legacy copies and
  both-store denial. Use the existing opt-in HTTP adapter in this environment.
- Existing queue gate: 8,000 historical people / 1,144,025-byte archive, 41 Save
  attempts and 40 direct requests produce two indexed writes.
- Existing urban/transit joint gate: pure 56/80-to-128 migration and injected
  post-validation failure; 21 adjoining acquisitions with live freight and fares;
  60 days of conserved cash/goods. Building/depot/station IDs stay IDs while paths,
  bus stops and tracks remap as tile indexes.
- Existing urban evolution gate: real compensated home/farm clearance, preserved
  occupants/enterprise goods, mall funding/commissioning, district lifecycle,
  80-grid migration and two 1,080-day runs. Existing private-entry gate preserves
  provider capital through restore and commissions a staffed fee-charging school.
- Existing core release gate passes with exact replay, authentic 56-grid migration,
  pause, traffic and structural checks. `TOWNLEDGER_CORE_ONLY=1` explicitly skips
  its long endurance matrix; it is not a new 115-year endurance claim.

Commands for existing file-origin fixtures:

```
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_save_chronology.py
TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_save_queue.py
TOWNLEDGER_CORE_ONLY=1 TOWNLEDGER_USE_HTTP=1 PYTHONPATH=tools/browser_http_adapter python tests/test_release.py
```

The first raw file-origin chronology attempt was blocked by Chromium's managed
`ERR_BLOCKED_BY_ADMINISTRATOR` policy. The already-supported loopback HTTP adapter
resolved this without changing browser policy. An earlier chronology run was
invalidated by rebuilding the bundle mid-run and correctly failed its source hash
assertion; the final immutable run passed. No Android/signing work was attempted.

## Limits and follow-up

These checks protect structural save integrity, not anti-cheat; offline positive
balance edits are not cryptographically authenticated. Existing system-specific
validators continue to own contracts, provider rules and transit receipt semantics.
A cross-system cold restart on a physical phone, native/browser disagreement and a
full new long-session endurance pass remain integration acceptance work. The
bounded host simulations and IDB fault injection do not certify native durability
or physical Android performance. No publishing, merge or deployment is included.
