# Audio and accessibility release notes

TownLedger 8 adds ten original soundtrack pieces totaling about 47 minutes. Music selection responds to town context and your chosen character, remembers recent pieces to reduce repetition, and crossfades between tracks. Music volume and effects/ambience controls are separate. Music begins after your first interaction. If playback is interrupted, use Retry music.

Settings also include reduced motion, larger menu text, graphics quality, frame-rate limit, visible traffic, atmospheric effects, and landscape detail. In verified Chromium checks at 360×640, mute and display choices persisted after reload; muted audio stayed paused through background return and native host suspend/resume. Reduced motion held the presentation clock while simulation continued. Keyboard focus moved from the music toggle to Next piece, and the checked controls fit horizontally.

The soundtrack passed a three-hour host-browser playback run on integrated checkpoint `03cb546`, with all ten pieces selected, no recorded playback failures, and two native host suspend/resume callbacks. Its report records 18 resource samples. Focused lifecycle and race checks also passed on the audio checkpoint; the documented final host turnover run completed 300 handoffs and 12 rapid Next actions.

These results cover Chromium host execution and simulated host lifecycle callbacks. They do not certify physical Android audio routing, audio focus, decoder memory, assistive technology behavior, or subjective listening quality.
