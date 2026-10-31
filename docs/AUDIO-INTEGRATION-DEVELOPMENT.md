# Audio integration checkpoint

Mute, native suspension and browser backgrounding now stop both short effects and ambience. Click feedback cannot start while hidden or suspended. Returning to the game restarts ambience, without replaying old effects. The sound toggle exposes its state with `aria-pressed`.

Free council/archive choices use the ordinary click; choices with a displayed positive treasury cost use the coin cue. Disabled buttons do not play an effect. This avoids a payment sound when keeping an existing boundary or cancelling a free choice.

`tests/test_audio_lifecycle.py` exercises actual button event paths with a mocked Audio class, including paid/free choices, native suspend/resume, mute, hidden clicks and foreground return. This proves scheduling/state behavior, not speaker loudness or subjective sound quality. Host lifecycle and council/archive workflow regressions also pass on this assembly. The prior 36-gate, waterfront and 45-minute soak evidence belongs to the preceding immutable 129be0f assembly; final release gates must be rerun after this change.
