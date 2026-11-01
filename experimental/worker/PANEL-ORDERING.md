# Authoritative model panel ordering

Follow-up to disabled lifecycle candidate459d750. Model panels now use the original `panelContents` inside the worker. Main-thread model panel generation is replaced by a sequential queue of `prepare-panel` commands; every admitted preview retains its actual source call and RNG effects. Typed context accepts only known panels, validated selection/filter/category fields and bounded policy draft fields. It never assigns arbitrary globals or accepts callbacks/source.

Host snapshots stay frozen. Panel effects install already generated HTML, preserving scroll. Navigation close also sends a causal `close-view` command, including the originally bound close button. Worker-originated navigation publishes active panel/selection before markup. Queued views from an old adoption epoch are discarded before admission. A panel effect for a no-longer-visible tab does not overwrite the current tab. Existing policy-package replies already contain the source render, so the bridge does not request a duplicate render after enactment.

Settings and trip remain explicit local presentation panels: device audio/options and current visual trip inspection remain main-thread owned. The actual settings control is checked to preserve canonical model/RNG. This is not a declaration that all UI interactions are routed.

`panel_ordering_test.py` compares14 ordered panel previews (12 model panel kinds, repeated construction/agenda), including search/filter/draft/inspection context, with exact original host HTML, full model and RNG. It also exercises actual tab, cabinet draft, close and private-provider buttons. Without an owner the provider button and raw construction refuse without changing model/RNG. Status always reports production admission uncertified; normal bundle excludes the reference owner.

Provider UI now invokes the existing serializable shared-root dispatcher, rather than a second paid path. It remains unavailable in the default build until an approved owner is installed. Remaining unsupported paid families are still explicitly refused. Production startup and realtime worker admission remain disabled.

`current-dense-trace-first.json` retains an initial timing diagnostic. Its browser wait delayed the driver's first input until after the synchronous stall; those input values are not a matched responsiveness comparison. The corrected harness uses a driver-side120ms wait and positions the pointer before starting the model batch. The final trace records candidate/source/worker/bridge hashes. Full snapshot cadence is deliberately disclosed as once per31-day batch; this is a bounded model/render diagnostic, not realtime worker gameplay acceptance.

## Actual paid UI proof and dense diagnostic

`paid_real_controls_test.py` uses the actual Agenda tab, Convene button and council choice button under the published reference owner. No test-only logical panel injection is needed: typed preview preparation carries the real context. The resulting full model/RNG exactly matches synchronous actual UI, host snapshots remain frozen and the original persistence writer receives the save. `paid-real-controls-proof.json` is reference-owner composition evidence only.

Three paired31-day runs from the generated778-resident checkpoint cross a monthly boundary and retain exact full model/RNG. Candidate d5905fe7a92b32b2632f8960775db34f0c96abd9, source6ed9d208b0112e4e360f40ef21063b68c519aefd9df3e1b39071c02c78e22a02; full bundle/bridge/fixture hashes and negative samples are in `current-dense-trace.json`.

| Diagnostic | Synchronous | Worker/default owner absent |
|---|---:|---:|
|31-day batch wall time|1,437–1,556ms|1,567–1,639ms|
|Maximum observed frame gap per run|1,417–1,533ms|517–550ms|
|Maximum pointer-handler delay per run|1,419–1,537ms|0.6–1.3ms|
|Maximum input-to-next-RAF per run|1,420–1,538ms|25–35ms|

Input is four trusted actual map pans per run. The batch snapshot arrives once per31days, so this diagnoses simulation isolation with the real renderer, not a playable realtime cadence or actual-speed guarantee. Large worker frame gaps remain despite responsive input during model work; this fails a smooth-rendering gate. Snapshot application/render cache behavior requires further component attribution. Observed worker heap55.8–68.6MiB is a short sample, not a long-session memory bound. No physical-device guarantee or production admission claim follows.

Final paid composition, actual-model lifecycle and delayed/cancelled archive regressions were rerun after the panel changes and passed. Independent paid reviewea04b99 accepted the prior459d750 lifecycle scope; this follow-up still requires independent review and native durability/composed-owner gates.
