# Native graphics and archive smoke — API 30

This is a bounded Android emulator smoke of public integration `87811c52cdb9aecd13cd23beebd52f6475c6dd9c`, captured 2026-11-01. The canonical assembled `assets/game.js` hash is `037c92b56d4b736f2c9c2bb96a950ae194bc815d1a393d36b3634f4272521d94`.

The emulator ran Android API 30 with WebView `83.0.4103.120` and the emulated OpenGL ES translator backed by Google SwiftShader. It is a software emulator, not a physical-device performance test.

## Results

- The app opened with the no-query Classic renderer default. I opened Options and selected **Newfoundland · 3D** through the actual Android WebView select control. The choice persisted as `townledger-renderer=webgl`.
- With **Performance** selected, the WebGL canvas initialized. The runtime reported SwiftShader, a `320 × 107` backing buffer, 21 draw calls, and 18,142 triangles. [Performance mode screenshot](performance-webgl.png)
- I changed quality to **Balanced (adaptive)** through the actual Android select control. The renderer returned to the ordinary Canvas (`__webglTaste` was absent), and the UI displayed “Canvas view selected for this renderer. Performance and Rich detail remain available in Settings.” The saved renderer choice stayed `webgl`, and quality stayed `balanced`. [Canvas fallback screenshot](balanced-canvas-fallback.png)
- At paused Day 17, the canonical archive SHA-256 was `4c40e9eb285b9b9ffd3f717d5d23a9c6a3fe5cac527367706bde883036e8d323` both before and after changing Performance to Balanced. No model-state change was observed from that graphics preference change.
- After force-stop and relaunch, `townledger-renderer=webgl`, `quality=balanced`, and the saved town archive were present before Continue. Continue reopened the 169-resident town at Day 17. Later it advanced while active; no strict post-Continue equality claim is made.
- I opened the real Android DocumentsUI Create Document picker, then pressed Android Back. It returned to the app and its Options screen with the town present and paused. No file was written. [Picker-cancel return screenshot](documentsui-cancel-return.png)

## Package identity

The graphics interaction run used the isolated QA package `org.townledger.vale.v8graphics3ba`, built from this source with only the package ID and QA label changed. Its APK SHA-256 was `7130942c3cf7eea53668dae243d033ba0fb15a014cfa6b84b5e30cdd1cf55714`; the pulled installed APK matched exactly. Replacing the QA package ID with the public production ID reproduces the canonical bundle hash above.

I also built and installed the intended side-by-side package `org.townledger.vale.v8sidecar`, labeled “TownLedger 8 Side-by-side QA”, from this exact source and the existing private development signer. APK SHA-256: `76ce91c7d0ad22788e18d92d29a3dfa09fba85ff2d93c85187f1919696873582`; the pulled installed APK matched exactly. Version is 8.0.0/code 22. The original `org.townledger.vale` remained installed. This signer is not the original app’s signer, so the package ID stays distinct.

Neither APK nor save files are included here. The screenshots show only a synthetic TownLedger test town. The software-emulator interactions were slow and sometimes took tens of seconds to return; these results do not establish smooth performance on user devices. Full-scene appearance and physical-device performance remain open.
