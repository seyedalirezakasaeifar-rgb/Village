# Install and keep your town

## Android

Download the standalone **TownLedger 7.1.1 Android APK**. You do not need to unpack the source ZIP. Open the APK and follow Android's normal installation prompts. Package: `org.townledger.vale`; version7.1.1/code21; minimum Android7/API24 with a current Android System WebView/Chrome.

The APK uses the same persistent development signer as this project's recent signed checkpoints. Its signer differs from the original baseline APK. If Android refuses an update because the signatures differ, preserve a verified backup before uninstalling the older app. Uninstalling can erase local game storage. No private signing key is included in any deliverable.

## Export before changing installations

1. In the existing game, open **Options → Export backup**.
2. Android opens its document chooser. Choose a destination and wait for the saved confirmation. Keep a separate copy and check the file exists and is not empty; restore/validate it in another compatible build when possible.
3. In7.1.1, choose **Options → Restore backup**, select the JSON archive, and inspect the restored town, treasury and properties.

Desktop browser builds provide a text-copy/paste archive fallback. Archives are validated before replacing the running town. Native exports/imports are bounded to 8MiB of UTF-8; an error does not count as a completed backup. Keep the older export if you may return to an older build: older engines do not understand expanded schema 6 towns.

## Recovery and controls

Continue reads available on-device copies before selecting the newest intact save. Conflicting older copies without chronology offer an explicit choice. Back/Escape closes the topmost dialog/drawer/tool. At the map root, native Back saves before leaving; a failed save offers Keep playing/export or explicit unsaved exit. If Android reclaims the game view, reopen and use Continue when a completed save is available; unsaved changes are not promised to survive renderer loss.

Drag to pan, pinch to zoom and tap properties to inspect. Public Works contains **Expand the borough** and **Waterfront**. Services explains access/staffing/funding; Policies stages changes until enacted. Seasons/weather remain optional. Options includes reduced motion, larger text, sound, quality and frame-rate controls.

The native host recovery flows were exercised on an emulator. Physical-device FPS, thermals, full-game touch and real system document-provider behavior remain unverified; see the accompanying QA report.
