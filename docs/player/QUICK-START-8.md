# TownLedger 8 quick start

## Start a town

Choose a Newfoundland scenario from the founding screen, then start or continue. Pause before inspecting options or making a large change. The speed control selects simulation rates; its label is requested speed. At high rates the game may deliver fewer simulation days per real second, so do not treat 64× as guaranteed actual speed.

Start with essentials: check the food market and household hardship, keep enough treasury for wages and operations, and connect useful sites by road. Review the Works & Planning panel before placing buildings. A selected building tool only arms placement; tap a valid map location to attempt construction. Use the town reports to check whether goods, jobs, access and cash actually changed.

## Trade, districts and services

In Trade, compare regional offers and costs before authorizing a shipment or contract. Freight moves through the road network and can take simulation time. Public Works previews adjoining district deeds; purchase and connect parcels as funds allow. Expansion is constrained by adjacency, available land and treasury.

Private schools and fire providers are licensed through policy and require real construction funding, staffing and operating revenue. Their fees can limit access; check coverage and affordability before relying on them.

## City view and performance

Open **Options → Display & accessibility → City view** and choose **Newfoundland · 3D**. Choose **Classic · reliable** to return to the classic view. The renderer choice is saved on this device. The **Graphics quality** choices are **Performance**, **Balanced (adaptive)** and **Rich detail**; the **Frame-rate limit** choices are 20, 30 or 60 FPS. Balanced can fall back to Classic on unsupported or slow renderers without changing your saved preference. Performance reduces rendering detail; Rich detail is more demanding. At 64×, Balanced and Performance simplify the ground and lower map resolution, and high simulation speed caps map refresh at up to 20 FPS so the economy gets more CPU time. The speed indicator reports days actually completed, which can be below the selected rate. Physical-device smoothness has not been verified.

## Music, saves and installing

Settings → Music & atmosphere provides separate music and effects/ambience controls, volume, three music characters and Next piece. Playback begins after your first interaction. Backgrounding or suspending the app pauses audio; return resumes subject to mute settings.

Use **SAVE NOW** for the local save and **EXPORT BACKUP** to copy archive text somewhere safe before reinstalling or changing app identities. **RESTORE BACKUP** validates pasted archive text before replacing the current town. Keep an export until the restored town is open and checked.

The checked Android manifest uses package `org.townledger.vale`, version 8.0.0, code 22, schema 8. The native development build has been verified under package `org.townledger.vale.v8sidecar`, installed alongside the older app with a development signer different from the old release signer. It is a separate app and does not inherit the old app’s private save: export from the old app and restore in the sidecar. This verifies sidecar packaging and coexistence, not delivery of the final APK. Keep the old app and a backup until the final binary is delivered and the restored town is checked.

## Known limits

The WebGL direction remains an experimental paused-town view. It is not the complete live simulation renderer, and it has no physical-device performance certification. Requested simulation speed is not guaranteed achieved speed. Save backups are user-managed text; keep them private and retain an extra copy before migration.


**QA source:** checked against source commit `87811c52cdb9aecd13cd23beebd52f6475c6dd9c` (especially `src/93-preferences.js` and `assets/webgl-entry.js`). This revision corrects the earlier guide: City view is available in Options and its selection persists; sidecar package/coexistence were verified in the native development build. Physical-device smoothness and final APK delivery remain unverified. The normal default renderer is Classic; Newfoundland 3D is selected explicitly.
