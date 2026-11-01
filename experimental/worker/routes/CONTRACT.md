# Worker route modules — version 1 team contract

Common base: `0a14b9e88bb5b133fec78336b7742ce9879e3bd3`. This freezes the API for parallel module authors. Central owner implements registration, validation, dispatch, UI bindings and composition. Registration/validation/shared-root dispatch and the working example are included with this contract checkpoint; declarative UI bindings and typed presentation effects are now implemented and tested. Full family actual-UI acceptance still belongs to its author. They are not present in0a14b9e. No module or partial composition enables production. Keep the complete synchronous game available.

## File ownership

* Paid reviewer: `routes/land-district.js`, `route-ui/land-district.json`, tests with `land_district` prefix. Own land/district/renewal and bridge/removal operations.
* Macro owner: `routes/transit-freight.js`, `route-ui/transit-freight.json`, tests with `transit_freight` prefix.
* Central owner: route registry/dispatcher, builder, bridge, owner registration; `routes/civic.js` and matching UI/test files for custom reviews, public projects and gatherings; native/composition/realtime.

Do not edit adapter.js, paid-worker.js, root-runtime.js, real-view-bridge.js, build.cjs or either shared paid-owner/layer file in family branches. Publish module/test commits and identify any missing central hook. Existing model functions may be called directly from trusted module source; functions never cross postMessage. Do not install another root, saver or DOM shim. Prefer actual model functions; if they mix DOM and economics, adapt only the DOM boundary, preserve the original economic body and prove equivalence against the untouched current-source UI. Report required production-source extractions to central rather than silently duplicating altered economics.

## Static registration

Each trusted JS module is appended to the generated worker after the central registry. It registers exactly once during bootstrap, before owner enable. Duplicate module/operation names fail startup. Module/operation names use lowercase ASCII letters, digits and hyphens, maximum64 characters; `$choice` is reserved. Module source is repository code, never fetched or supplied by a message.

```js
registerWorkerRouteModule({
  version: 1,
  id: 'land-district',
  operations: {
    'district-review': {
      mode: 'preview',
      fields: {parcel: {type:'string', maxLength:64}},
      execute(payload, ctx) {
        // Resolve against current worker G, refuse stale/unavailable targets.
        ctx.review(() => originalDistrictReview(payload.parcel));
      },
      // Required if execute creates choices. No automatic generic callback grant.
      settle(review, ctx) {
        // review = frozen {event, choice, index}; actual event/choice stay worker-local.
        // Validate current target/quote/ownership BEFORE payment. After creator work,
        // assert actual creation/settlement; refusal must roll back the whole root.
        ctx.applyChoice(review, {
          validate: () => true, // replace with domain checks, never a placeholder in delivery
          verify: () => true   // replace with concrete outcome checks where work can refuse
        });
      }
    }
  },
  // Optional ONLY for module-owned mutable runtime, registered disabled/idle.
  runtime: {capture: () => moduleRuntime, restore: value => {moduleRuntime=value;}}
});
```

The example names `originalDistrictReview` and checks are illustrative, not an implementation or permission to accept unverified settlement. A delivered module must call real source functions and implement its checks.

Operation `mode` is `preview` or `command`. Both execute synchronously **inside the existing command-only paid root** with graph/runtime rollback, current validators, creator preflights, cash conservation and committed-effect/save drain. Preview is not permission to silently charge: it may establish authoritative review state/RNG/bookkeeping only, and tests must prove no unintended payment or economic action. No ordinary-day root or snapshot is added. `allowPendingReview:true` is an explicit optional flag only for a tested operation which safely replaces/settles a current review; default false. An execute/settle returning a Promise fails closed. No operation is installed or invoked from a packet.

## DTO and validation

New transport packet:

```js
{type:'route', module:'land-district', operation:'district-review',
 payload:{parcel:'east-meadow'}}
```

The bridge adds its existing causal command ID and epoch; the worker binds those actual values to dispatch. User payload must not contain identity, epoch, callbacks, source, selectors or arbitrary property paths. Unknown module, operation, extra field, stale epoch/ID or malformed field refuses before model work. Unknown commands never reach a generic work callback. Payload is copied and deeply frozen before execution.

`fields` is an exact object schema. Field specs:

* `{type:'integer', min:0, max:9007199254740991}` or `{type:'number', min:0, max:50000}`: finite numbers, no string coercion; integer means safe integer. Explicit `min`/`max` are required.
* `{type:'string', maxLength:64}`: string only; maxLength required, at most512.
* `{type:'boolean'}`; `{type:'enum', values:['bus','elevated']}`: exact listed scalar values.
* `{type:'array', maxLength:256, items:fieldSpec}`: bounded array, items validated recursively.
* `{type:'object', fields:{...}}`: exact nested object, no unknown keys.
* `optional:true` and `nullable:true` must be explicitly declared. No implicit defaults or permissive coercion. Max nesting6, fields32 per object; dangerous prototype keys are rejected.

Entity existence, current money/quote, ownership, topology, outstanding order and project phase are stateful checks **inside** the root, through `ctx.refuse(reason)` or thrown errors. A schema check is not evidence that work succeeded. `execute` may return a small plain result DTO, not model object references/functions. Existing committed reply/snapshot/outbox format remains; do not acknowledge persistence in a route result.

## Context and opaque reviews

`ctx.refuse(text)` refuses the shared root. `ctx.notify(text)` emits the existing notification outbox. `ctx.openPanel(name)` calls the authoritative worker panel preparation. `ctx.present(dto)` stages an explicitly validated presentation effect, never a main-thread model mutation. `ctx.save()` stages the existing save intent; only original writer readback plus token ACK is durable.

`ctx.review(work)` runs a trusted synchronous original preview function inside the root. If it establishes pendingEvent, central binds its exact worker-local event identity, workerId, epoch, module and operation. Choice callbacks remain authoritative in that realm. Source review state must not be recreated on main.

The existing `{type:'choice',eventId,index}` packet remains. For a bound module review, central validates the opaque ID/epoch/index against the actual current event and calls that operation's registered `settle(review,ctx)` inside the same paid root. Missing settler, stale/repeated review, changed event identity or unsupported callback refuses. It never falls through to the old unprotected generic choice path. Existing authored council choices keep their current dispatcher.

`ctx.applyChoice(review,{validate,verify})` validates before any debit; uses the exact original choice close/payment/apply/recompute/header/save order; then verifies the concrete outcome. Both callbacks are trusted module functions, never message fields. A false check refuses/rolls back model/RNG, pending review, UI effects and saves. Domain-specific choices whose original ordering differs must implement that ordering explicitly in `settle` using actual model functions and tests, rather than forcing this helper. Validate affordability and creator success; a callback returning after a toast is not success. Cancellation/zero-cost previews must preserve their original semantics.

Central supplies identity/epoch/context; no module may synthesize review IDs, change workerEpoch/workerCommand, acknowledge tokens, clear faults, advance days or publish partial models. Additional module runtime must be registered before enable; automatic G and shared runtime already participate in rollback.

## Declarative real UI bindings

Each family provides an array in its owned `route-ui/*.json`:

```json
[{
  "event":"click",
  "selector":"[data-district-review]",
  "operation":"district-review",
  "fields":{"parcel":{"source":"attribute","name":"data-district-review","as":"string"}}
}]
```

The filename supplies the module id. No dynamic selector or function comes from a user payload. Bindings precede generic unsupported guards. Supported field sources are `attribute` (explicit name), `constant` (plain value), `input` (static selector, reads value/checked), `context` (`selected`, `draftPolicy`, `transitDraft` only), and map-only `tile-x`/`tile-y`. Conversion `as` is `string`, `integer`, `number` or `boolean`; invalid conversion refuses visibly. The worker independently validates its exact schema. Attribute values are not executed or used as property paths.

Map binding example: `{event:'map', tool:'road_bridge', operation:'bridge-review', fields:{x:{source:'tile-x',as:'integer'},y:{source:'tile-y',as:'integer'}}}`. Tools are explicit static names. A transit draft map binding uses `tool:'transit-draft'`; main carries only the published presentation draft and sends taps back to the authoritative worker. It cannot run the original mutating host transitMapTap. Native/worker admission and main command FIFO remain central.

During staged integration pass the combined parsed binding list through trusted `enable(...,{routeBindings:[{module:'land-district',...binding},...]})`. Central builder will emit `route-bindings.generated.json`; missing bindings do not imply support. Retained options are reused by fresh-realm recovery. Existing controls take precedence only when the new family does not own their selector. Duplicate selector ownership fails startup.

Allowed `ctx.present` DTOs (version is supplied centrally):

* `{kind:'camera-grid', x,y,zoom}`: finite in-grid coordinates, zoom .025–1.7.
* `{kind:'build-tool', tool, x?,y?, projectKind?,projectId?}`: explicit source construction/review tool; never constructs on main.
* `{kind:'overlay', value}`: existing overlay enum only.
* `{kind:'policy-draft', values}`: validated policy proposal only; never enacts on main.
* `{kind:'focus-policy', key}`: finite existing policy key; no arbitrary selector.
* `{kind:'transit-draft', draft}` / `{kind:'clear-transit-draft'}`: serializable **presentation** draft; no G references; authoritative draft stays in worker. Supply draft field schema and actual source mapping with the transit module before central enables it.

If another effect is needed, report its exact schema and source use to central. Do not silently drop meaningful notifications, dialogs, reports, tool state or command outcomes. Main adopts one complete committed snapshot before applying effects. Pending feedback is immediate, confirmation follows commit, saved status follows original writer ACK. Unsupported controls still refuse; a partially routed worker is not a release candidate.

## Required family evidence

Use the exact current-source synchronous UI as oracle; old669 evidence is not current-model acceptance. Provide operation inventory mapping all owned controls, schema negatives, stale/repeated IDs, pending review/command interleaving, refusal after payment/creator refusal with exact rollback, full model/RNG and outbox equivalence, reload, original writer failure/retry and at least one trusted actual UI journey per family. Test absent/unfunded/expired targets honestly. No synthetic wallet injection in ordinary play; controlled conserved test-fixture funding must be labelled. Return exact source/fixture/module hashes and remaining unsupported operations. Native durability and overall realtime acceptance remain separate central/native gates.


## Working example and immediate test entrypoints

`routes/example-calendar.js` registers `example-calendar/summary`, performs the actual `civicCalendarView()` and preserves a real notification. Build with `WORKER_PAID_COMMAND_OWNER=1 NODE_PATH=/path/to/node_modules node experimental/worker/build.cjs` (or install experimental/worker dependencies locally). All `routes/*.js` files are appended in filename order; no central builder edit is required for a new family file. Call `real.command({type:'route',module:'example-calendar',operation:'summary',payload:{}})` after the normal trusted owner initializer. The result is `reply.paid.value`; the reply also contains the complete committed snapshot/effects. `python experimental/worker/test_route_registry.py` proves actual calendar/full-model/RNG equivalence and unknown module/operation/extra-field/null/choice refusals unchanged. Registry source: `experimental/worker/route-registry.js`.

Optional operation `choiceFields` uses the same exact field schema. A bound choice may carry `choicePayload` on the existing `type:'choice'` request; the registry validates/freezes it and supplies `review.payload` to `settle`. Never read DOM from a worker choice. If a custom source choice needs a typed name or form value, provide a static `event:'choice'` binding scoped to that module/operation; central forwards its validated form fields. No choice binding may intercept another module's review. This finite form-binding path is implemented; the protocol test exercises a real opaque choice with typed form input. It is not acceptance of every family form.


## Central UI hook checkpoint

`workerRoutePresent(moduleId,dto)` is now included in the generated worker. Pass parsed `route-bindings.generated.json` as enable option `routeBindings`; build.cjs generates it from family JSON files. Click, input, change, map and choice bindings are supported. A successful click/input/change binding refreshes the active authoritative panel when the module did not already publish panel markup; set `refresh:false` when the original source action deliberately does not rerender it. This affects the real UI path, not raw DTO semantics. Main remains an immutable completed view.

Presentation transit drafts accept source fields mode/depot/stops/level/editing/quote and optional cancelOperation. If omitted, cancelOperation is inferred as `draft-cancel` ONLY when that exact operation is registered in the same module; otherwise the effect refuses. Worker and main map a presentation `town:G` for the original office/overlay view; the module's retained quote/draft stays authoritative. Both mirrors participate in rollback or epoch reset. Main map taps route through the module; the stale host transitMapTap is never called. Back/tool cancellation sends the registered cancel operation.

Module initial runtime must be JSON transient state (normally null review/draft values), or provide a trusted synchronous module `reset()` for epoch changes. Every load resets module runtime; a reset that changes G/RNG refuses. Module runtime and the central transit mirror participate in paid-command graph rollback. No daily root is added.

`ctx.closePanel()` and `{kind:'panel-close'}` are supported. Policy-draft/overlay/tool effects synchronize the worker logical widget state and the main presentation, without enacting policy or constructing on main. Unknown effects/fields fail inside the root. Missing DOM controls cannot silently perform another action.

`python experimental/worker/test_route_ui_hooks.py` passes trusted click/map dispatch, camera/tool/overlay/policy effects, frozen host view and opaque choice with typed form input using a labelled test-only module. It is a shared-interface proof, not transit/land gameplay acceptance. `test_route_registry.py` remains the actual-model calendar/example gate. Current economic source remains669c908 at this hook checkpoint; the01eeda port is central's next isolated composition step.


Transit compatibility smoke: `test_transit_hook_smoke.py` loads published c84371d family code without changing it, uses actual New Bus and Cancel controls, confirms office draft markup, presentation town mapping and frozen host view. It constructs a real depot with labelled conserved regional fixture funding. This proves the shared missing hook is usable; it does not certify a funded route build/cargo journey. Land named-place forms/footprint effects and district-admission visits still need explicit schemas; unsupported effects continue to refuse.
