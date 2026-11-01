# TownLedger game previews

These are local Chromium captures of the current-public game candidate `133d2801d621fb63970eb05565a0ee3061d0aa5d` (`assets/game.js` SHA-256 `2bc6ed1cdec4259c1a5f51dcaf40f3aa4562349592a4353ccf50c3c2c6243c81`). Each image is 1280×720 and contains only the game. No game source or art was changed for these captures.

- [Open causeway with paid freight crossing](bridge-open-with-freight.png): both banks are visible; the actual 60-unit import truck is on the five-cell deck after save, reload, and a second save/reload.
- [Closed causeway after underfunding](bridge-closed-after-underfunding.png): the real maintenance routine lowered bridge condition to 24.75, below the 25 closure threshold; water remains present. For this controlled preview fixture, municipal cash was transferred to the regional account before applying the routine 215 times, preserving total funds.
- [Night neighbourhood](night-neighbourhood.png): evening lighting was switched through Game Options; warm occupied windows and street lamps are visible.
- [Road-access planning view](road-access-planning-overlay.png): Road Access was selected through Game Options; the legend and access symbols remain visible.

The old `road-bridge-art-phone.png` / `road-bridge-art-closed-phone.png` diagnostics are preserved in `docs/previews/urban8/`. Their save warning came from the previous `page.set_content()` harness, whose document origin is `null`: localStorage raises a `SecurityError`, autosave is false, and the app correctly displays its warning. Repeating the app over local HTTP (`http://127.0.0.1:8766`) allowed a successful local save and reload; the bridge, five water-backed deck cells, valid archive, and active crossing shipment were preserved. The showcase screenshots were taken on that working HTTP origin after closing the overview panel with its Close control.

All four captures were inspected at pixel size. Browser page errors: none. This verifies host Chromium and browser storage only; no Android-device claim is made.
