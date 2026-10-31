# Audio sample-level measurement summary

Source: per-file ffmpeg `volumedetect` and ffprobe logs in `reports/audio-media-qa-raw/`; scanned media compared with `reports/asset-manifest-8.json`. Values below are FFmpeg sample `max_volume` / `mean_volume` in dBFS, not true peak and not a subjective quality assessment. The scan produced no sample peaks at or above 0 dBFS. Values absent from logs remain unknown.

Music mean-volume endpoints: quietest `assets/music/river-and-road.ogg` at -28.2 dBFS; loudest tie `assets/music/a-borough-grows.ogg` and `assets/music/waterline-work.ogg` at -23.7 dBFS.

The 18 scanned WAV/OGG media files include two effects not referenced by the 16-entry runtime manifest: `assets/sound/build.wav` and `assets/sound/error.wav`. They are present in assets but the current source does not reference them. This count compares the media scan with the generated runtime-reference manifest; it does not imply those files should be deleted.
