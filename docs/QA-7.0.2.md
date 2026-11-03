# TownLedger 7.0.2 candidate: changes and evidence

## Changes

- Separate ground and scene caches; retain the cropped background across changes to buildings. Worksites use stable scaffolding with live progress bars, avoiding sprite regeneration at every progress stage.
- Balanced and Performance settings reduce ground detail and backing resolution at 64×. Pausing or lowering speed restores detail; Rich detail retains it throughout. The setting explains this behavior.
- Street names prioritize long major roads, cull offscreen labels, avoid label collisions, maintain readable size with zoom, and remain behind buildings.
- Correct background scaling at high device density and tall-building culling at screen edges. Density checks use all three shipped stylesheets.
- Reject negative archive schema integers atomically while retaining schema-less legacy imports. Existing future-schema rejection remains.
- Use a text play icon and label the control Resume or Pause according to its current action.
- Describe Hard Times as an 18-month export-demand shock, matching the simulation. No artificial unemployment floor or recovery gate was introduced.
- Build with Java 8 bytecode on a current JDK, supply the platform library to d8, retain the full patch version in APK filenames, and verify the version code.

## Browser and mechanics review

Chromium 154, host CPU, Playwright, real requestAnimationFrame sampling; not Android timings. The reproducible synthetic stress town has 2,000 residents, 678 households and 711 buildings at 844×390. At requested 64×, the final run simulated 313 days in 8.03 seconds. RAF p50/p95/p99: 16.7/33.3/66.7 ms. Draw p95: 43.2 ms; tick p95: 8.1 ms. The earlier same-size baseline draw p95 was 56.9 ms. Changes were refined over repeated runs. A few concurrent build/simulation runs exceeded the 50 ms draw target; final timing was measured without those workloads.

There were 7 RAF intervals over 50 ms and draw p99 was 121.5 ms: occasional expensive scene changes still cause visible hitches. Four panels opened without errors; measured next-frame latency ranged 13.3–32.4 ms. Currency conservation drift was 0.00000647. No JavaScript errors were recorded.

Landscape 844×390 at densities 1 and 2 and browser portrait 390×844 were checked for panels, Escape closure and document overflow. Downscaled map mean pixel difference between landscape densities was about 4.4/255, validating consistent composition. Landscape screenshots were visually reviewed. Android declares landscape orientation; portrait browser controls retain the existing compact layout and are not an Android portrait support claim.

Controls, touch placement/cost, pinch without construction, staged policies, speed slider, modal/focus behavior, archive schema checks and core release checks passed. Contrast audit found zero violations in menu, 13 panel views and council modal. Core release evidence includes seeded replay, save continuation, malformed-save atomicity, legacy migration, cash conservation, cargo ownership, true pause and traffic progress.

Fifteen three-year scenario trajectories (five scenarios × seeds 42, 101, 909) remained structurally valid and conserved currency. Hard Times recovered from 75% employment gradually (roughly 75–77% at day 91 and 88–89% at day 181), then approached full employment. Other starts reach high employment rapidly. This remains a relatively forgiving simulation; deeper long-term challenge and balance need player feedback. Earlier policy experiments, liquidity and default-start checks also passed. Rendering changes do not alter economy coefficients.

## Android package

Official SDK platform 36, build-tools 36.0.0; minimum API 24, target 36; package `org.townledger.vale`, version 7.0.2/code 16. Built with javac/d8/aapt/zipalign/apksigner. Independent verification checked DEX checksums, exact bundled asset bytes, package metadata, icon, absence of permissions, v2/v3 signatures and alignment. APK bytes and hash are in the delivery manifest and machine-readable verification report.

A new RSA-3072 development signer was generated and retained outside the repository with private file permissions. It is not the original baseline signer. Export and verify towns before uninstalling if Android refuses an update. The key is excluded from commits and delivery archives.

**Not run:** Android installation, launch, document-picker backup/import on a real device, background/resume and native Back behavior, Android frame rate, battery and thermal measurements. No usable emulator/device is attached and `/dev/kvm` is absent. This is a browser-tested and package-verified candidate, not a claim of completed device certification or studio-level perfection.
