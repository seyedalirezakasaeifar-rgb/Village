# Transit/freight first family increment

Base ee15d61. Disabled experiment only. Registers routing, priority, stop-relief, retire, remove-guideway and remove-site using unchanged source model functions and shared paid root. Static UI bindings are supplied but actual UI acceptance is pending central declarative binding implementation.

Direct test: four routing/priority changes, duplicate/invalid/extra-field refusals after each, four absent/no-op targets, exact export archive unchanged on refusals. This is not full economic settlement, actual UI, save failure/retry or transit build acceptance. Calendar registration regression also passes.

Remaining transit controls: authoritative draft/new/edit/map/undo/quote/build, levels and presentation reports. Remaining freight controls: reviewed relief, transfers, cancellation, supplier contracts, staged procurement and port dispatch. Their worker-local review/settlement and trusted UI parity must be tested before claiming completion. No production activation.

Run WORKER_PAID_COMMAND_OWNER=1 node experimental/worker/build.cjs then python experimental/worker/transit_freight_test.py.

Second implementation increment adds worker-owned transit drafts and opaque relief/procurement reviews; exact UI acceptance remains pending central presentation support. Draft presentation contains no G/town reference. Central must validate it and map a presentation-only `town:G` for the existing office panel. Quote is the unchanged `transitReviewedQuote` DTO; builds pass that exact retained quote to `buildTransitRoute`, preserving source freshness checks. These new transit draft paths are not acceptance-tested yet and must remain disabled until combined UI tests pass. Relief opaque settlement and repeated-choice rollback are exercised by the family harness.

Current local implementation additionally includes exact source offer preview, port-load preview, cargo recall/transfer reviews, draft configuration/map and service-level routing. All use authoritative model functions or original trusted source preview bodies. Choice verification refuses callback no-ops and restores the shared root. Added source-body previews are not yet matched full-model/UI acceptance: do not enable them based on DTO tests. Founding-town staged procurement correctly refuses all three excessive combined orders without changing the archive; this is retained negative evidence, not a successful trade playthrough.

Pending central hooks block actual UI acceptance at ee15d61: declarative click/change/map registration, transit-draft presentation/quote validation and town mapping, build-tool transit_route mapping. Additional report/focus/overlay presentation-only transit controls remain unimplemented. Exact operation count in this module must not be confused with coverage of original handlers. Original writer failure/retry, funded cargo transfer/port settlement and transit build parity remain required.
