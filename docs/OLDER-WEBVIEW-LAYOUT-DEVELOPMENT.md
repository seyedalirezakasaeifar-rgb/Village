# Older Android WebView layout checkpoint

A bounded native attempt used the exact 129be0f game in an API30 AOSP emulator with Chrome83 WebView, 4GB, two CPU cores, Swangle and Vulkan disabled. The APK installed and launched. Actual ADB touch founded a town (the welcome screen closed; the simulation advanced), and native Back closed its drawer. System/SystemUI ANRs during boot and focus changes made responsiveness and lifecycle/provider checks unreliable. This is not physical-device or native FPS certification.

The final native screenshot exposed a separate genuine compatibility bug: the header and navigation rendered but the map had no height. `.main` specified only `height:100dvh`, which Chrome83 does not understand. The old browser therefore sized the flex layout to its non-map content. A `height:100vh` fallback now precedes the dynamic viewport value, and the canvas has explicit top/right/bottom/left fallbacks for unsupported `inset`.

`tests/test_older_webview_layout.py` removes `dvh` and `inset` declarations before current Chromium parses styles. It reproduces a zero-height map when the new viewport fallback is removed, then verifies a visible map and usable construction drawer at 640×360, 844×390 and 360×640. This is a targeted CSS compatibility simulation; the corrected APK still needs an exact-source native rerun. The native boot ANR limitation remains separate.
