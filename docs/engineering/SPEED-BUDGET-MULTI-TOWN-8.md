# Multi-town speed and pause check

This host Chromium run extends the terminal-city speed sweep with two independently evolved late cities and checks the high-speed pause/backlog and requested-versus-actual display. It uses trusted emulated touch taps on the same map-status control. Each speed ran for about7 seconds; completed simulation days divided by elapsed time gives delivered simulation speed. RAF and touch-to-next-RAF values are sample distributions, not Android display/input certification.

The two retained checkpoints are generated QA cities from `generated-late-31987fc`: terminal day41681 (778 residents, 797 buildings, 81 firms) and mid-session day15561 (1,848 residents, 750 buildings, 37 firms). The third city was seeded independently and advanced 420 days (day421, 701 residents, 255 buildings, 99 firms). Its exact town composition differs; it had no transit routes.

| City | Requested | Delivered | RAF p95 / p99 | Touch to next RAF p95 |
| --- | ---: | ---: | ---: | ---: |
| Terminal | 1× | 0.9× | 17 / 17 ms | 36 ms |
| Terminal | 16× | 15.9× | 33 / 67 ms | 70 ms |
| Terminal | 32× | 31.9× | 33 / 217 ms | 348 ms |
| Terminal | 64× | 52.1× | 33 / 250 ms | 112 ms |
| Mid-session | 1× | 0.9× | 17 / 17 ms | 38 ms |
| Mid-session | 16× | 16.1× | 17 / 67 ms | 65 ms |
| Mid-session | 32× | 32.0× | 33 / 200 ms | 55 ms |
| Mid-session | 64× | 56.6× | 67 / 217 ms | 305 ms |
| Independently grown | 1× | 0.9× | 17 / 17 ms | 36 ms |
| Independently grown | 16× | 16.0× | 17 / 33 ms | 68 ms |
| Independently grown | 32× | 32.0× | 33 / 83 ms | 205 ms |
| Independently grown | 64× | 49.1× | 67 / 133 ms | 230 ms |

At64×, queued time reached3.5–7.0 simulation days and delivery fell to49–57×. At32×, delivery stayed near the requested rate, while the tail varied sharply by city: RAF p99 was83–217ms and touch p95 was55–348ms. At16×, delivery stayed near16× and touch p95 was65–70ms. These results support16× as a conservative upper recommendation for this host workload; they do not establish a universal response-time threshold.

Pausing after each64× sample immediately changed the control to “Resume simulation” and showed the pause banner. Across all three cities, the day did not advance during the next~850ms and the accumulated backlog remained unchanged (about5.0–7.0 days). Changing the speed slider while paused clears the backlog, as the existing interaction handler does.

The original high-to-lower-speed check reproduced a stale label: after changing from64× to16×, the header continued to show `Actual 43×` for about one second. The fix clears the sampled rate on every speed change, leaves the actual-rate label blank until a fresh sample completes, then shows the newly measured rate. A focused rerun confirmed this behavior and that pause retains the backlog without advancing days.

Sources and receipts:

- Main measurement source: `bd4c718d1e8d393fec94581590394267c7e13da711a99f683d2f5350b2c1ab78`.
- Corrected source after the label fix: see the current commit containing this note.
- Fixture SHA256: `ad6256fd85d4146fda9eeac0b16d5b182ed352c23bbd96af3b320553c29ce786`.
- Full speed rows: `reports/session-performance/speed-budget-multi-town.json`.
- Pause and label sampling: `reports/session-performance/speed-display-pause.json`.
- Rerunnable harnesses: `tools/speed_budget_multi_town_8.py` and `tools/speed_display_pause_check_8.py`.
