# TownLedger 7.0.3 development checkpoint

This is an intermediate overnight checkpoint. The roadmap in OVERNIGHT-ROADMAP.md defines the remaining economic, visual, resilience and native work; it is not a completed studio-quality claim.

## Changes since 7.0.2

- Portrait header has two rows, with visible date, Pause/Resume and speed controls. All twelve destinations occupy a two-row navigation grid. Tests now check every control's bounds and center hit target, activate every tab, and cover 360×640 and 390×844 alongside landscape/density cases.
- Council decisions have modal semantics, focus trapping and Decide later. Back/Escape dismisses the topmost dialog, retains the petition and resumes the prior simulation state. Decisions persist in the inbox until applied, and deferral does not spend or enact anything. Archive confirmation has Cancel.
- Regional imports now belong to draft/enact/discard; draft summaries and policy experiments include boolean changes.
- The full-world ground cache is half resolution at 64× in Balanced/Performance, reducing changed-image upload cost. Buildings/labels remain independent; full ground detail returns on pause/lower speed/Rich detail. Background margins clear before cropping to avoid stale edge pixels.
- Market Cross is correctly named; seasonal greeting is suppressed when seasons are off. Scenario briefings explain opening demand constraints and provide Economy/Policies/Outcomes actions. Hard Times tracks the family-resilience ambition; Market Cross tracks the existing health-and-education ambition. No economy coefficients were changed.
- First-use map hints disappear after interacting with the map; colored tab emoji were replaced by original monochrome SVG glyphs. Tutorial describes observe/change/review and the role of customers/materials.

## Immutable QA evidence

`tools/qa_candidate.py` assembles once and fingerprints every shipped asset. It runs all gates sequentially, rejecting changes during a gate, then builds and verifies the package and checks the generated source hash again. `candidate-gates.json` records every gate, asset and log hash. A development iteration deliberately changed an icon while the first gate run was active; the guard rejected that run. All required gates were rerun after the final asset freeze.

Final game.js SHA256: `747ca3ccf44087b3db48ef9433b6ceb79daee4b807902228cc6157234e764955`. All 13 required gates passed against that source. Scenario trajectories and core release logs now carry the same source hash as the APK, unlike the earlier 7.0.2 intermediate evidence. Package verification additionally checks every bundled asset byte.

The final stressed host-browser run loaded 2,000 residents/678 households/711 buildings at 844×390 and requested 64×. It simulated 311 days in 8.02s. RAF p95 33.3ms; draw p95 37.2ms; 5 RAF intervals exceeded 50ms. Draw p99 remained 156.0ms. The software emulator was running during this acceptance pass, so treat it as a loaded-host result, not a controlled comparative benchmark or Android FPS result. The earlier isolated next-cycle trial measured draw p95 34.1ms and RAF p95 16.8ms, with two intervals above50ms. Scene-change outliers still need further work.

The review-workflow regression includes Council focus/Back/deferral/application, import draft/discard/enact, and six 180-day simulation/save/restore/all-tab cycles. Core release, archive, controls, contrast, model/default starts, 15 scenario trajectories, liquidity, multi-seed policy experiments and matched regional tradeoffs all passed. Full machine-readable evidence is shipped with the checkpoint.

Matched regional runs demonstrate fiscal/service consequences even where employment reaches100%. At day361, seed42 passive policy held about$959k cash, safety79, health84 and education61; cutting key services held about$1.17m but safety63, health68 and education43. A large service proposal consumed most fiscal headroom without proportional quality gains. Inspection identified a priority for the next cycle: health/school ratios use the fraction of their proposed allocation paid, so the quantity of service purchased needs a controlled spending-staircase audit. No balance fix has yet been claimed.

## Android progress and limits

Official SDK36/build-tools36.0.0 package, code17, stable private development signer. Exact asset/DEX/metadata/permission/signature/alignment checks pass. A software-only API30 x86_64 emulator has been started with `-accel off` and SwiftShader; lack of KVM does not prevent startup. The host ADB cannot write its default read-only configuration directory; an official Ubuntu container with a normal writable home provides the same official ADB tool and connects locally to the emulator. No security controls were disabled.

The prior7.0.2 APK installed successfully on that emulator. Its first `am start -W` returned a timeout rather than a confirmed launch; a screenshot subsequently showed Android “Process system isn’t responding” dialogs. The software emulator was stopped after about ten minutes to free resources. Installation succeeded, but game launch and all interactive native stages remain unverified. A smaller emulator configuration is a follow-up option. WebView83 is present, making older-WebView compatibility and the exact7.0.3 install/launch/Back/lifecycle/document-picker checks priorities for the next native smoke pass. Physical-device performance remains untested. Preserve the development signer outside the public repo and archive; it differs from the original baseline key.

A supplemental isolated run after stopping the emulator used the same final game source (747ca3ccf44087b3db48ef9433b6ceb79daee4b807902228cc6157234e764955). Draw p95 was 28.8ms, RAF p95 16.8ms, and 4 intervals exceeded50ms; draw p99 was still 169.2ms. The corresponding JSON is separate from the immutable gate logs. The long-tail hitch remains an overnight profiling priority.
