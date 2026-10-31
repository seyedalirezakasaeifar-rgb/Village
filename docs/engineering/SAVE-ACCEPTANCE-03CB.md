# Combined checkpoint save acceptance: early negative result

Checkpoint `03cb54675880a9b60c0c8d8de5dd0b671d0abff3`, assembled SHA-256
`27ca5f1e1e5df352d38daf042d2de63b63024b8deed596c79e2f4679cc50947e`.
Random operation seed `8142026`; actual loopback HTTP origin, isolated detached
worktree `/workspace/save-acceptance-03cb`. Production source is unchanged.

The strict randomized gate stopped after approximately 40 seconds / 31 completed
operations. Saving at day 102 and comparing nine uninterrupted days against
restore-plus-nine-days changes bank cash, household/firm accounts, goods histories,
regional shipments, treasury and waterfront state. Pending council event is false.
The failure repeats at the same day/operation with the same seed. This is a
canonical continuation failure; it does not demonstrate destroyed money. Total
money, goods, IDs and archive bounds passed before the failing replay.

The combined controlled city contains 1,375 original-plus-fixture people, all 21
annexations, bus/elevated routes and fare accounts, actual paid cargo, provider and
mall escrow, a municipal rehousing project and three active civic projects. The
first fixture's attempted enterprise clearance was correctly blocked by existing
cargo/contracts; it is not claimed as successful demolition.

`docs/previews/save8/03cb-negative/failure.json` records the source, timing, changed
fields and representative financial divergence. `operations.jsonl` records the
operation trace. Full generated archive/expected/actual snapshots remain private
under `/workspace/scratch/save-acceptance-03cb-diagnostic/` for diagnosis and are
excluded from Git. A separate diagnostic preserving both saved public/private
service provision caches still fails at day 102, ruling out that simple fix.

`tools/accept_save_randomized.py` is the reproducible acceptance harness. It uses
existing fixture APIs, pauses simulation except requested steps, performs actual
cold Continue, quota/denied-store/corrupt-store/stale-callback faults, rapid and
same-day saves, malformed and failed-adoption imports, and exact replay. Outputs
include seed, source hash, due time, bounded samples and every operation.

To reproduce the original exact sequence, use `SAVE_QA_REPRO_03CB=1` with
`SAVE_QA_ROOT` pointing at the immutable checkout and `SAVE_QA_OUTPUT` at a fresh
scratch directory. This preserves the initial blocked enterprise-clearance fixture
and original operation weights/sequence; it stops near day 102 in about 40 seconds.

Default mode stops on a canonical mismatch. `SAVE_QA_CONTINUE_REPLAY=1` explicitly
records the mismatch, restores the known checkpoint and continues independent
fault/invariant checks; its result is `completed_with_replay_failures`, never a
passing canonical gate. It retains at most three private diagnostic snapshots.

An extended one-hour independent fault run was launched in this continuation mode
with output `/workspace/scratch/save-acceptance-03cb-extended`. Consult its
`status.json` for the exact due time, PID, completed operations and pending status.
It includes real paid crop-title clearance and later attempts actual compensated
home redevelopment against available replacement housing. This is not rendering,
audio, native-device or subjective-play endurance, and no such claims are made.

The first extended attempt stopped at 40 seconds because a newly constructed park
had no `baseValue` before cold restore, and hydration added `baseValue: 80000`
(equal to its existing value). The physical comparator now applies that documented
default on both sides; this is classified as harmless normalization, with no
production change. All other physical fields remain compared. The restarted run
uses output `/workspace/scratch/save-acceptance-03cb-extended-final`.
