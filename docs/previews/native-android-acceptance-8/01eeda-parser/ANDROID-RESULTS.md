# Native acceptance notes — 01eeda3

Source: `01eeda3d2ff09822b9422721f75e97fabbc9958a` (based on `3bea58b0b8d21cced9611049ee5e5038e57383c7`).

API 30, WebView 83.0.4103.120, x86_64 software emulator. Isolated package: `org.townledger.vale.qanative01eeda`. Scratch APK SHA-256: `8f065849a2942abb1f02a97f91cbbe0c41830a0cf00462dcddc30beec7c1204f`. Canonical game bundle SHA-256: `84ecbaef6b0ae999a9c5adcd49b9ba1678840cabfc36cf02b617c74a93d208a4`; MainActivity SHA-256: `7283d9365de4efdf0633205c520c6c7b660f369420b3d4cb9e1612f9bcd2345d`. Worker endpoint remained disabled.

Actual Java bridge parser probe sent a completion with duplicate `persisted` fields. The app logged `Rejected malformed async archive completion: IllegalArgumentException`; the synthetic town state remained unchanged (excluding live `trafficState`).

Actual DocumentsUI export created a 370 KB synthetic archive named `TownLedger-QA-01eeda-北港 (2).json`. Open Document picker cancellation by Android Back returned to the app with the exact 102-field state hash unchanged: `30a4f865fb05ba1d470510a420335da28c3ac53e7849d05a15dd70c66221a43e` (day 14, 169 residents). The exported file was selected through the real picker in a separate run.

An actual `am kill` process-death followed by Android Continue restored a town, but exact pre/post equality was not demonstrated: Continue resumes simulation, and the observed day advanced from 14 to 15. This is explicitly not recorded as an exact-equality pass.

The commit's canonical report is `docs/engineering/NATIVE-COMPLETION-FIELDS-8.md`; it documents host parser fixtures and explicitly says Android execution was not yet recorded. This supplemental runtime note captures the later API30 probe. Screenshots here are synthetic town UI only. They exclude APKs, signing material, saves and personal data.

Selected device captures: [synthetic town](native01eeda-town2.png), [paused town](native01eeda-paused.png), [Unicode picker](native01eeda-unicode-picker2.png), [selected archive](native01eeda-import-selected.png), [cold restart](native01eeda-coldwelcome.png), and [restored town](native01eeda-cold-continued.png).
