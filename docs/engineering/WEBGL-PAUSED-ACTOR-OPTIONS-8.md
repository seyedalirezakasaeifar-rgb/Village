# Confirmed paused actor-option invalidation defect

Frozen29dd12a running soak reproduced actual road/cargo sprites remaining after the real Visible traffic control was switched OFF while paused: the projection expected0, while six actual IDs remained cached in Economy and14 in Rich. Evidence is retained separately in the running-soak report; acceptance29dd12a is unchanged.

The motion contract now includes traffic/effects flags, and the renderer's actor-mode key observes them. This invalidates only the live actor layer; no economic/route/settlement code or static-world rebuild is added. The same-clock paused case now clears/recreates actual trip actors immediately. Canvas behavior is unchanged.

Actual browser test waited for real trips under the normal clock (no inserted actors), paused, used real OFF/ON controls, and verified disappearance/reappearance, strict full-archive/RNG equality after the legitimate Settings visit, save and no JS errors. Node negative oracle executes the actual prior mode expression and demonstrates why it missed the flag change. Effects uses the same invalidation path; browser trip coverage specifically exercised traffic.
