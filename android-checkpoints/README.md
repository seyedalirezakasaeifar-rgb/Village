# Development checkpoint APK

7.0.3/code17 is an intermediate overnight checkpoint, not a final release. Source checkpoint: `0b052aa0a43a0f9f625f5db6946da2e293a1d276`. Build uses the private development signer retained outside this repository; the original baseline signer is unavailable.

APK SHA256: `8311757b92070f0ca7139a29b7184db98aa4f3efebc31737e1c9b0877469f3cd`.

All thirteen browser/economy/archive gates passed against immutable shipped assets, then DEX/manifest/asset/signature/alignment verification passed. Exact 7.0.3 native installation and launch have not been run. The earlier 7.0.2 installed on a software-only API30 emulator, whose system process subsequently became unresponsive; successful game launch is not established. See `docs/QA-7.0.3.md` and `docs/OVERNIGHT-ROADMAP.md`.

Export and verify existing town saves before uninstalling an older build if Android rejects the changed signer. Signing keys and local save data are excluded.
