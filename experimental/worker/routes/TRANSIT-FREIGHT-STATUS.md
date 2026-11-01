# Transit/freight first family increment

Base ee15d61. Disabled experiment only. Registers routing, priority, stop-relief, retire, remove-guideway and remove-site using unchanged source model functions and shared paid root. Static UI bindings are supplied but actual UI acceptance is pending central declarative binding implementation.

Direct test: four routing/priority changes, duplicate/invalid/extra-field refusals after each, four absent/no-op targets, exact export archive unchanged on refusals. This is not full economic settlement, actual UI, save failure/retry or transit build acceptance. Calendar registration regression also passes.

Remaining transit controls: authoritative draft/new/edit/map/undo/quote/build, levels and presentation reports. Remaining freight controls: reviewed relief, transfers, cancellation, supplier contracts, staged procurement and port dispatch. Their worker-local review/settlement and trusted UI parity must be tested before claiming completion. No production activation.

Run WORKER_PAID_COMMAND_OWNER=1 node experimental/worker/build.cjs then python experimental/worker/transit_freight_test.py.
