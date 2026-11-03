# Longer original score and streaming handoff

## Composition

The score now contains ten original pieces, 2,846.37 seconds (47.44 minutes): the existing three chamber themes plus Orchard Footpaths, Rails to Greyhaven, Work at the Waterline, The Long Market Day, Rooms after the Rain, A Borough Grows and The Quiet River. Seven longer arrangements have contrasting opening/response/return/bridge/chorus/coda sections, different diatonic modes and meters, authored motifs, register/orchestration changes and restrained percussion. No samples or borrowed recordings were used; the compositions, recordings and generators carry CC0 dedication in `assets/music/LICENSE.txt`.

Canonical committed assets and duration/RMS/peak/SHA metadata are in `assets/music/score.json`. Runtime playback streams compressed Vorbis assets; it does not decode an entire playlist into AudioBuffers. Recompose with a Python interpreter containing NumPy plus FFmpeg: `python tools/compose_music.py` renders all ten; `python tools/compose_extended_score.py` refreshes the seven longer pieces while retaining the three legacy records. NumPy is available in this executor's system Python, rather than its browser-test venv. Arrangements/PCM are deterministic; container hashes identify the committed encoded outputs. Build packaging consumes these checked assets without synthesizing them again.

## Runtime interfaces and ownership

`src/95-music.js` owns the score controller and its Options panel. The audio specialist can take ownership after this checkpoint; other workers should preserve its interfaces.

- `MUSIC_TRACKS`: ten file/title/duration/tag/mix records. The original quieter tracks receive bounded per-track compensation; user volume remains independently persisted.
- `chooseMusicTrack()`: weighted context/character selection, excluding the six most recently started pieces and the current pending piece. It uses its own presentation PRNG, never the economic random stream. Water/trade/growth/evening context is read only at piece boundaries; events do not interrupt a phrase.
- `recordMusicPlayback(index)`: records a successfully started piece once. History, character, volume, enabled state and presentation PRNG persist outside the town save.
- `playMusicTrack(index)`, `refreshMusic(retry=false)`, `stopMusic()`, `setMusicVolumes()` retain their integration roles. `refreshAmbience` in the effects controller continues to call refreshMusic; effects and music have separate controls.
- `musicEpoch` guards delayed play success/rejection. A stale rejected promise must not stop a later successful selection. Fade time starts when play resolves, rather than while a decoder is buffering.
- At most two referenced streaming decks and one fade timer. Retiring a deck pauses it, removes its listeners and src, clears predecessor ownership and calls load() to release the old media resource. Fade completion/suspension also breaks predecessor chains. Suspension cancels the fade, retires the stale tail and keeps one paused current deck for resumption.
- Eight-second equal-power handoffs overlap the legacy themes' longer release tails. Natural endings and manual Next use the same selector. User gesture, hidden document and native host suspension remain authoritative. Playback errors wait for an explicit Retry/toggle/Next rather than periodic retry storms.
- Music character is adaptive/quiet/lively; changing it affects the next selection. Muting/volume zero and persisted preferences remain distinct. No music starts on page reload before a gesture.

## Verification and honest limits

`tests/test_music.py` runs the real HTTP-origin application and real HTML media. It verifies gesture playback, independent effects mute/music volume, native suspend/resume, manual Next, a forced end-of-piece timeupdate handoff, preference persistence and no pre-gesture media on reload. All ten assets are genuinely decoded through the browser AudioContext, with stereo/nonzero RMS, bounded peak and matching duration. Large decoded test buffers are released between browser jobs; this decoding loop is test instrumentation, not the runtime architecture.

A 100-selection controlled policy fixture visits all ten pieces without repeating the recent-six window and leaves the complete economic archive/random stream unchanged. Identically seeded character tests select quiet/evening pieces 340/400 times in quiet mode versus70/400 in lively mode. These are selection checks, not claims that everyone prefers the score.

`tests/test_music_races.py` exercises delayed/rejected play promises: an older rejection cannot silence a newer successful stream; suspension ends the fade and retired sources are unloaded. Effects lifecycle controls also pass. Receipts carry the exact assembled source SHA.

There is no hearing-capable tool in this environment. No subjective listening, speaker quality, seamless acoustic-mix certification or Android decoder-memory claim is made. Long-session real playback, process/native decoder memory, interruption/route/audio-focus behavior and subjective audition remain with the audio/native specialists. The early integration APK below predates this soundtrack; do not label it as the new audio build.

## Early native build readiness

`artifacts/development/8.0.0-integration-525e47d/` contains a development-only APK from the prior immutable integrated game commit525e47d, assembled JS SHA293fe306631099dfaacdd37e724d4c6e3b89991f56a1e15c50f872606f662c90. Real javac/DEX, complete packaged asset hashes, manifest/version/package, icon resources, no permissions, signature and alignment pass. The private persistent signer matches7.1.1. Native archive transport JVM checks, Back coordinator/generated-JS persistence handshake and browser host lifecycle pass.

That5,474,087-byte APK has SHA1ecb9c23ea7b1ad533ff8937acd03615a2ba7999e03481326ce5fcf9f4a4d071. It contains the earlier three-piece score, has not been launched on a device/emulator, and is not the final8.0 release. The native specialist owns further acceptance; the production signing key remains private with the integration lead. Original7.0 used a different signer, so its save must be exported before an uninstall.

Checkpoint assembled JS SHA-256: `23bd4570b62219ddc9f58a68007cb7c696569def326004fd4d1a198fcccd0fe1`. Exact evidence: `reports/integration/8-soundtrack.json`.
