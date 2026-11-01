# TownLedger 8 quick start

## Start a town

Choose a Newfoundland scenario from the founding screen, then start or continue. Pause before inspecting options or making a large change. The speed control selects simulation rates; its label is requested speed. At high rates the game may deliver fewer simulation days per real second, so do not treat 64× as guaranteed actual speed.

Start with essentials: check the food market and household hardship, keep enough treasury for wages and operations, and connect useful sites by road. Review the Works & Planning panel before placing buildings. A selected building tool only arms placement; tap a valid map location to attempt construction. Use the town reports to check whether goods, jobs, access and cash actually changed.

## Trade, districts and services

In Trade, compare regional offers and costs before authorizing a shipment or contract. Freight moves through the road network and can take simulation time. Public Works previews adjoining district deeds; purchase and connect parcels as funds allow. Expansion is constrained by adjacency, available land and treasury.

Private schools and fire providers are licensed through policy and require real construction funding, staffing and operating revenue. Their fees can limit access; check coverage and affordability before relying on them.

## City view and performance

The checked WebGL build can be opened with `?cityArt=webgl` in a local browser preview. It draws a paused town snapshot and provides camera/picking interactions in the experimental build. It is not currently exposed as **Options → Cityview** in the checked source. If that option appears in a later package, use it to choose between Canvas and Newfoundland 3D. Richer graphics cost more GPU time; the Graphics quality and Frame-rate limit controls affect the existing presentation settings, but they do not promise a particular device frame rate. Canvas remains the fallback. The WebGL preview is not certified on physical Android devices.

## Music, saves and installing

Settings → Music & atmosphere provides separate music and effects/ambience controls, volume, three music characters and Next piece. Playback begins after your first interaction. Backgrounding or suspending the app pauses audio; return resumes subject to mute settings.

Use **SAVE NOW** for the local save and **EXPORT BACKUP** to copy archive text somewhere safe before reinstalling or changing app identities. **RESTORE BACKUP** validates pasted archive text before replacing the current town. Keep an export until the restored town is open and checked.

The checked Android manifest uses package `org.townledger.vale`, version 8.0.0, code 22, schema 8. A sidecar package such as `org.townledger.vale.v8sidecar` installs as a separate app and does not automatically inherit the old app's private save. Export from the old app and restore in the sidecar. Confirm the final APK's package name and signing certificate before installing: an in-place update requires Android to accept the signing identity. The final sidecar APK/package/signature have not been verified by this guide; do not uninstall the old app or treat it as migrated until backup restore is confirmed.

## Known limits

The WebGL direction remains an experimental paused-town view. It is not the complete live simulation renderer, and it has no physical-device performance certification. Requested simulation speed is not guaranteed achieved speed. Save backups are user-managed text; keep them private and retain an extra copy before migration.
