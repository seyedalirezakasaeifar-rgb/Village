# Upgrade and user-recovery matrix

Base f4e0315. `tests/test_upgrade_matrix.py` executes the supplied 5.6/6.0 engines
and pinned historical 7.0.0, 7.1.1, schema-7 and schema-8 engines to obtain actual
exports in memory. It imports those, both committed authentic financial/history
fixtures, a fresh current town and an 8,000-person historical-record town into the
candidate. All ten imports pass with conserved cash and unchanged person identity,
household references and property ID/kind/owner/coordinates. Reports publish only
hashes, sizes and counts, never generated archive payloads.

Unsupported future/negative schemas, orphan membership, truncated input and an
injected adoption interruption reject without changing the previous archive/RNG.
A small user-facing fix explains a newer schema and asks for a compatible update;
invalid/truncated/incompatible errors explicitly retain the current town. Both
native restore and desktop restore use the same pure error formatter. Validation
policy, archive schema and Android wrapper are unchanged.

Current exports identify release 8.0.0, schema 8 and gridSize 128. `version: 3` is
an archive-format compatibility field, NOT the app release. The native default
filename is currently the safe constant `TownLedger-town.json`; it contains no
untrusted pathname components but does not distinguish versions. Native owner may
choose a version/schema suffix; readers must continue checking payload metadata,
not trusting the name. Do not rename an older backup to imply compatibility.

The mixed 128-atlas/1,375-person archive preserves paid freight, settled fare,
provider/mall escrow and routes. All 29 malformed/truncated import cases remain
atomic. Twelve existing storage fault cases pass, including aborted IDB commit,
quota divergence, same-day/new-town chronology, held stale callbacks and legacy
copy cancellation/recovery. Host JVM archive transport passes Unicode/BOM, exact
8 MiB UTF-8 bounds, malformed Unicode/provider errors and pending filename safety.
No extra one-hour run was performed.

User recovery: preserve the older export before upgrading; wait for completed
export confirmation and retain a separate copy; verify a backup by restoring it in
a compatible installation. An import error leaves the previous town available.
A failed/cancelled export is not a verified backup; a provider failure can leave a
partial destination, so keep the original file. Unsupported future schemas must
be opened in a compatible newer build rather than altered manually.

Needs relaying to native owner: actual DocumentsUI cancellation/recreation, denied
or failing provider writes, duplicate-name/overwrite choice and confirmation that
failed export leaves the prior independent backup available. These host checks do
not substitute for that actual picker/provider behavior or physical upgrade/signing
continuity. No wrapper/signing change is authored here. Integrator should reassemble
the current source and rerun the native restore message after cherry-picking.
