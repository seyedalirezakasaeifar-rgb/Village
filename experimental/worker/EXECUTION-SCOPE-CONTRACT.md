# Worker/paid-owner explicit execution scope v1

Compatible hook for the paid-command-only adapter proposed in public841ade2. No new controller, no ordinary-day whole-state certificate, no production owner installed here.

The owner passed to `workerInstallPaidOwner(owner)` must supply:

```js
owner.workerExecution = {
  version: 1,
  mode: 'paid-command',
  bind(readTrustedContext) { /* retain this function exactly once while disabled */ },
  readyForOrdinaryDay() { /* boolean true only after BOTH integration conditions below */ }
};
```

`readTrustedContext()` returns a frozen `{version:1,mode,epoch,command,stepping}`. The trusted mode is `idle`, `paid-command` or `ordinary-day`; packet fields cannot set it. The worker installs this provider before enabling the owner, and sets/resets scope synchronously with try/finally. The paid layer should read the retained provider through the owner, never infer bypass from `simulationBusy` or missing shared roots. An enabled shared root still owns nested work. Scope does not authorize unsupported DTOs.

`readyForOrdinaryDay()` MUST remain false until:

1. The paid owner's `completeDevelopmentProjects` wrapper recognizes this exact ordinary-day context and takes its safe automatic path WITHOUT shared.run/capture/certificate. Explicit user completion, or completion inside an existing paid root, must retain paid admission. It must reject unknown scope rather than treating it as automatic work.
2. The capacity owner's actual local automatic creator preflight/settlement contract is composed and independently checked for due completion, capacity refusal and creator failure. A constant true declaration or skipping the previous guard is not sufficient evidence.

The worker's paid-command day path refuses BEFORE tick while readiness is false. Once true it invokes original tick directly inside `ordinary-day`; unexpected tick failure fences export/mutation and requires recovery. It creates zero worker day roots/certificates. Paid-owner wrapper behavior still needs its independent zero-capture due/empty-day gates. No implementation here asserts automatic creator safety is already available.

Owner installation with no execution contract is rejected. The only exception is the explicitly marked public `testOnly:true` reference owner; it runs historical `reference-day` whole-root oracles, never production. Status exposes executionMode/referenceTestOwner/productionAdmissionCertified:false. Direct raw build/policy/package commands remain refused in paid-command mode until their finite whitelist/root contract is agreed; choices/providers use the published serializable dispatcher with `paid-command` context. No implicit synchronous-host mutation fallback exists.

All causal model/view packets refuse while `workerStepping` is true, including between completed days. Their admitted IDs remain consumed. This includes council choice/provider, review/defer, policy, preview and load. Save prepare/ACK/abort and effect ACK/read/export may operate on a completed boundary. Future realtime scheduling must submit bounded day batches and wait for the batch acknowledgement before admitting queued commands; never label an interleaved mutation a completed replay-equivalent batch.

The execution context is transport/control state outside financial rollback. Existing paid runtime and outbox graph registration remains required. Save-intent drain, epoch/serial effect ACK, immutable native packet/session and token/write/ACK ownership are unchanged. Paid-owner implementation owns completing its half of this contract; automatic preflight stays with the capacity owner.

## Disabled and halted owner behavior

An installed paid-command owner that is disabled cannot fall through to the unowned ordinary-day path. The worker refuses before tick. Unknown requests and disabled paid dispatch never invoke shared.run's disabled direct-work path.

A halted shared root sets the worker's failed-state fence. Export, snapshot, step, inspect and in-place load refuse with `ROOT_HALTED_RECREATE_WORKER`; this controller cannot be reset safely in its current realm. Recovery requires a new worker realm initialized from a verified archive. Presentation ACK and a prior save-token ACK/abort can still finish: they acknowledge already prepared committed work and do not serialize the potentially failed current model. This is a protocol permission, not a disk-write claim. The real UI/native new-realm recovery flow remains an explicit production acceptance dependency.
