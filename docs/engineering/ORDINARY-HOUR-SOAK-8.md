# One-hour ordinary-play performance soak

The latest synchronous build completed a 3,601.9-second host Chromium session. The browser loaded the generated terminal-town QA fixture (embedded day41,681, 778 residents, 797 buildings, 81 firms, 48 total routes and21 owned districts). Its production bundle stayed byte-for-byte at SHA-256 `4a9c9e17032a91c84b8639bced0029670e7cb0a1c31dcdf62884bdc99f02f250` from commit `d61bc20d6d3fe8f4c6e1e6a5f9af2e64db23a1ee`.

During the run the game kept automatic development, private-service entry, freight, transit and audio enabled. The player used Public Works to place one public green and extend one road without adding funds; later road extensions were also attempted through the UI. The session panned the map60 times, opened60 report panels, completed30 explicit saves, and made six 8-second pauses during the64× bursts. It repeated six 10-minute cycles: six minutes at16× followed by one minute each at1×,8×,32× and64×. There were117 approximately30-second samples and no JavaScript/console errors.

| Requested speed | Typical measured delivery | Observed RAF P99 | Input-to-next-RAF tail |
| ---: | ---: | ---: | ---: |
| 1× | ~1× after transition windows | 16.8 ms | up to79 ms in settled samples |
| 8× | ~8× after transition windows | 16.8–33.4 ms | up to26 ms in settled samples |
| 16× | 15.3–16.1× in steady windows | 16.8–116.7 ms in the early dense city; mostly16.8–50 ms later | occasional windows reached323 ms |
| 32× | 31.2–32.0× in settled windows | 149.9–266.6 ms | up to65 ms in settled windows |
| 64× | 33.8–59.0× | 150–349.9 ms | 357–433 ms in settled windows |

RAF and input figures are host Chromium samples from emulated trusted browser input; they are not Android display latency or device certification. Several measurement windows straddled speed changes, so their delivered-rate values blend both settings. The repeated steady windows are listed separately in the full receipt. At64× the queued work peaked at6.94 simulation days. Each pause took effect immediately: the day remained unchanged for the eight-second pause and the queue remained visible until a speed change reset it.

Accounting audits every five minutes and at shutdown passed. Final money-ledger drift was about`0.000017`, commodity-balance error stayed below`4.5e-8`, and the final town archive validated. No test reset, wallet injection, periodic economic replenishment or hidden simulation skipping occurred. V8 heap was12.8MiB after the initial boundary GC, reached161.8MiB during play, and measured21.2MiB after final GC. This omits native canvas, audio and GPU memory. Thirty explicit save-button operations completed; median completion was253ms and the slowest was528ms.

The economy changed substantially during the accelerated century of simulation: population fell from778 to17 and operating transit routes from9 to0, while buildings rose to810. This is a significant gameplay/economic balance finding and also means late samples came from a much smaller population workload. The soak preserves the natural evolution rather than adding money or residents to keep the performance load artificially high.

The full timestamped samples and actions are in `reports/session-performance/ordinary-hour-0086590/session.json`; the rerunnable harness is `tools/ordinary_hour_session_8.py`. Source fixture SHA-256 is `ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786` (generated QA data, not a user save).
