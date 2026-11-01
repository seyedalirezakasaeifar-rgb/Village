# TownLedger 8 quick start

## Start a town

Choose a Newfoundland scenario from the founding screen, then start or continue. Pause before inspecting options or making a large change. The speed control selects a requested simulation rate from 1× to 64×. At 8× and above, the header can also show **Actual N×**, a rolling estimate based on completed simulation days; it may be lower than the selected rate when the device cannot keep up.

Start with essentials: check the food market and household hardship, keep enough treasury for wages and operations, and connect useful sites by road. Review the Works & Planning panel before placing buildings. A selected building tool only arms placement; tap a valid map location to attempt construction. Use the town reports to check whether goods, jobs, access and cash actually changed.

## Trade, districts and services

In Trade, compare regional offers and costs before authorizing a shipment or contract. Freight moves through the road network and can take simulation time. Public Works previews adjoining district deeds; purchase and connect parcels as funds allow. Expansion is constrained by adjacency, available land and treasury.

Private schools and fire providers are licensed through policy and require real construction funding, staffing and operating revenue. Their fees can limit access; check coverage and affordability before relying on them.

## City view and performance

Open **Options → Display & accessibility → City view** and choose **Newfoundland · 3D**. Choose **Classic · reliable** to return to the classic view. The renderer choice is saved on this device. The **Graphics quality** choices are **Performance**, **Balanced (adaptive)** and **Rich detail**; the **Frame-rate limit** choices are 20, 30 or 60 FPS. Balanced can fall back to Classic on unsupported or slow renderers without changing your saved preference. Performance reduces rendering detail; Rich detail is more demanding. At 64×, Balanced and Performance simplify the ground and lower map resolution, and high simulation speed caps map refresh at up to 20 FPS so the economy gets more CPU time. The speed indicator reports days actually completed, which can be below the selected rate. Physical-device smoothness has not been verified.

## Music, saves and installing

Settings → Music & atmosphere provides separate music and effects/ambience controls, volume, three music characters and Next piece. Playback begins after your first interaction. Backgrounding or suspending the app pauses audio; return resumes subject to mute settings.

Use **SAVE NOW** for the local save. In the Android APK, **EXPORT BACKUP** opens Android’s document picker so you can save the archive file; **RESTORE BACKUP** lets you choose an archive file to import. In a browser, export shows archive text to copy into a file, and restore accepts pasted TownLedger text. Keep a separate export before restoring because restore replaces the current town, then check that the restored town opens correctly.

The checked Android manifest uses package `org.townledger.vale`, version 8.0.0, code 22, schema 8. The native development build has been verified under package `org.townledger.vale.v8sidecar`, installed alongside the older app with a development signer different from the old release signer. It is a separate app and does not inherit the old app’s private save: export from the old app and restore in the sidecar. This verifies sidecar packaging and coexistence, not delivery of the final APK. Keep the old app and a backup until the final binary is delivered and the restored town is checked.

## Known limits

Newfoundland 3D is an optional live city view. It streams the world and can show moving traffic, transit and boats; the experimental Worker background simulation is not shipped; the displayed renderer is WebGL or Canvas. Rendering quality and achieved frame rate depend on the device and selected workload settings. Physical-device smoothness has not been verified. Save backups are user-managed files or text; keep them private and retain an extra copy before migration.


**QA source:** checked against source commit `87811c52cdb9aecd13cd23beebd52f6475c6dd9c` (especially `src/93-preferences.js` and `assets/webgl-entry.js`). This revision corrects the earlier guide: City view is available in Options and its selection persists; the optional 3D view is live rather than a paused snapshot; the native development sidecar was verified alongside the old app. The Android APK uses the native document picker for archive files, while browser backup uses copied/pasted text; the header’s Actual N× is a rolling achieved-rate estimate distinct from the selected speed. The experimental Worker refers to background simulation, not graphics rendering. Physical-device smoothness and final APK delivery remain unverified. The normal default renderer is Classic; Newfoundland 3D is selected explicitly.
