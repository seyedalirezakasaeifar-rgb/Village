# Combined render and district-admission checkpoint

This checkpoint integrates render audit `e8913c7` and migration-aware district guidance `d944c4f` onto `662ec6f`. It preserves funded migration, legacy tenancy validation, port settlement, transit forecasts and native fixes.

## Confirmed changes

- Ground actors are composed below elevated infrastructure. The funded bus crossing fixture changes from 151 incorrect overlap pixels to zero.
- Foreground actor shadows match an independent full redraw: 464 differing channels become zero. The underlay is viewport-bounded and released at distant zoom.
- Pause uses a font-independent SVG.
- District guidance proposes at most one dwelling per phase and stops while usable vacant units remain. Constructing a municipal home grants no residents.
- Address inspection reports the actual funded-job, household-budget, food, access and service assessment. A rejected illustrative household is explicitly titled “cannot move here yet.” This is an assessment, not an admission guarantee.

## Exact-source evidence

Assembled `assets/game.js` SHA256:
`3570ef6e14dbd08908232955768f355b198c1c869021289204825cd952d038ed`.

[Combined receipt](../../reports/integration/render-migration-8/receipt.json) embeds nine gates, all asserting that source hash: actor compositor, bridge occlusion, ten camera/day/night cases, paid port art, visual LOD, actual district controls, tenancy archive, composite save and core release gates. No economic-state assertion was relaxed.

Fresh captures: [day](../../reports/integration/render-migration-8/mobile-day.png), [night](../../reports/integration/render-migration-8/mobile-night.png), [far](../../reports/integration/render-migration-8/mobile-far.png), [district plan](../../reports/integration/render-migration-8/district-plan.png), [negative admission report](../../reports/integration/render-migration-8/unfunded-address.png).

The camera capture now navigates the actual HTTP asset origin instead of opaque `set_content`; this avoids a test-origin storage warning without suppressing legitimate storage errors. The day and negative-admission images were visually inspected after that correction.

## Remaining acceptance

These finite Chromium and simulation regressions do not establish physical-device smoothness or multi-hour enjoyment. Current-source Android/WebView animation and crossing review remains required. Representative long-session responsiveness findings remain open. The separate cooperative scheduling prototype is not enabled by this checkpoint. No new APK or release publication is included.
