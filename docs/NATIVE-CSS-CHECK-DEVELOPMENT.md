# Native older-WebView rendering check

A bounded software-only API30 AOSP emulator installed the exact `ff7be45` game assets in a private debug-only APK (code900003, not a user deliverable). Chrome83 reported a640×215 canvas, and raster sampling found5,415 colors. The [actual native capture](previews/native-css-check/api30-chrome83-town.png) shows the scene and Town Hall drawer. The `100vh` fallback therefore fixed the previously collapsed map in the actual older WebView, as well as the CSS compatibility fixture.

SystemUI ANR overlays and ADB input timeouts prevented reliable touch certification. Town founding ultimately used a programmatic DOM click. The Back test did not establish correct drawer dismissal: the WebView target disappeared, and Chromium logged a renderer crash (code-1). The cause is uncertain under software emulation. Native lifecycle, document-picker behavior, physical-device performance and FPS remain uncertified. The screenshot is evidence of rendering, not native responsiveness.

Review the host's automatic three-second Back exit fallback and renderer-loss recovery before final delivery. The capture predates the later bounded-save queue and founding crop-title corrections; those JavaScript changes require their own final acceptance.
