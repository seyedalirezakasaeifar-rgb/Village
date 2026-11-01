# Android 30 low-quality full-scene WebGL probe

Frozen source `664b44c0549a65784381191fd505e80bc4a8d84e` starts and renders the normal 128×128 town on an isolated API30 Android emulator with the explicit low-quality WebGL URL. The in-page renderer was `Android Emulator OpenGL ES Translator (Google SwiftShader)` under WebView 83.0.4103.120. The normal scene used mid LOD, a 640×215 landscape map viewport, and a 480×161 backing buffer; the sampled scene reported 19 draw calls and 93,640 triangles. It is the full town model in the ordinary renderer path, not the 13×13 diagnostic window.

The QA APK package is `org.townledger.vale.qagfx664`, version code 900020, built with `?cityArt=webgl&cityQuality=low`. APK SHA-256 `6f3421260b663d87f51b9472f747cf170af21eb9dc322acec68af2f7632d1e93` matches the APK pulled from the device. Source commit is `664b44c0549a65784381191fd505e80bc4a8d84e`; canonical assembled game bundle SHA-256 is `451bfa6f9686c9ad6c29e2ce19b8614908339596ddd02aa94f8a5e2b70374b03`. The QA metadata and Java URL are the only scratch packaging overrides; embedded WebGL modules match the frozen source.

On the paused Day-3 town, the actual Android tap on the projected Town Hall point `(320, 160.5)` opened Property Inspector for tile `(26,26)`, building ID3354. The saved-state hash stayed `a9a6cf046d7d818ac6e00e513d8c143aded9efb11ffb6359ab47ac6ea741d6f2`. A real drag moved the camera target from `(26,26)` to `(18.242,25.750)` while leaving that hash unchanged. After the pause settled, frame ID18 remained stable for 10 seconds with zero extra draws and unchanged saved state.

The real 1× resume tap changed the motion state to running; a real pause tap then returned the town to paused at Day4. CDP closed during the second tap, but reconnecting to the new page target showed WebGL still active, Day4 paused, and the normal app screen intact. A real landscape zoom tap changed camera zoom from1.00 to1.22 and frame ID34→35; it did not change the saved state.

With QA orientation unlocked, resizing to portrait changed the viewport to360×640 and WebGL buffer to270×316. The actual projected Hall point `(292.01,392.53)` still picked ID3354; a real tap opened Property Inspector with unchanged saved state. Returning the system to its original landscape/auto-rotate settings restored the640×360 viewport and480×161 buffer.

A deliberate `WEBGL_lose_context` test removed the WebGL canvas and showed the ordinary visible `#view` Canvas renderer. The paused Day4 town and saved-state SHA-256 `7ed4f98c6cacaaf8d53280a1c443c5e077ab6ca6ffb3e8a49c1b808834348ac0` were unchanged. This confirms the fallback path; the loss was intentionally triggered, not spontaneous.

Screenshots captured from the Android OS:

- [Paused normal low-quality town](paused-full-scene-landscape.png)
- [After real camera pan](panned-full-scene.png)
- [Portrait Property Inspector after a real Hall pick](portrait-property-inspector.png)
- [Day4 after 1× resume/pause](paused-day4-after-1x.png)
- [Canvas fallback after controlled context loss](canvas-fallback-after-context-loss.png)

The scene did render and accept actions, but the software emulator was slow: observed input-to-postcondition was roughly7–11seconds. Startup initially saturated the renderer and the first UI actions queued until it settled. This is compatibility evidence and a maximum successful configuration for this AVD, not a claim of smooth performance on user hardware. Production still launches Canvas by default.
