# Development checkpoint: save recovery and older WebView layout

Download **TownLedger-Android.apk** directly to Android; extracting the source ZIP is not required. This is 7.1.0/code20, an intermediate development checkpoint rather than the final overnight handoff or a store release.

This build includes mayor-purchased districts, productive fisheries and wharves, continuous working boats, original town artwork and activity, staged policy/service/credit systems, the Chrome83 map-height correction, audio suspension, and chronology-based recovery across local storage and IndexedDB.

Forty browser/model/host-JVM checks passed against frozen shipped assets. APK source assets, real Java DEX, manifest, v2/v3 signature and alignment were independently verified. See manifest.json for the immutable source commit and file hashes. The earlier compensated-ledger assembly also passed a separate 45-minute expanded-town real-RAF soak; that result does not certify the later save implementation.

Physical-device performance and native document-picker/lifecycle checks remain incomplete. The software emulator suffered SystemUI ANRs; the corrected map layout is undergoing a bounded, separate native rerun. Do not interpret compilation or browser timing as Android FPS.

The APK uses the persistent development signer, which differs from the original baseline signer. Export and verify an existing town backup before any uninstall required by Android. Private keys, private logs and personal saves are excluded. The matching source ZIP includes required assets, build scripts, tests, text documentation and historical source references; documentation screenshots remain in the repository galleries.
