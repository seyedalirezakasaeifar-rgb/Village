# Asset and license inventory

This inventory records repository evidence, not a blanket rights clearance. It covers the current tree at the time of review.

## Explicit project licenses

- **Project source and original game assets:** root [`LICENSE`](../../LICENSE) applies the MIT License, copyright 2026 Townledger contributors, and explicitly says bundled third-party software and fonts retain their own licenses.
- **Original soundtrack:** [`assets/music/LICENSE.txt`](../../assets/music/LICENSE.txt) dedicates the ten compositions, recordings, and score-generation code under CC0-1.0. It says the pieces are original and use no external samples or borrowed recordings. [`assets/music/score.json`](../../assets/music/score.json) records the ten tracks and their asset hashes.
- **Original synthesized sound effects:** [`assets/sound/LICENSE.txt`](../../assets/sound/LICENSE.txt) says the effects were created for this project and are licensed under the project MIT license.
- **Graphics:** the root MIT license covers original project assets. Repository files reviewed here do not provide a separate per-graphic authorship or provenance register. Graphics provenance beyond the project license: **provenance not yet verified**.

## Bundled fonts and libraries

A filename scan of the current asset and Android trees found no bundled `.ttf`, `.otf`, `.woff`, `.woff2`, `.jar`, `.aar`, or `.so` files. The game stylesheets name Georgia and Arial system font families; these are references to fonts supplied by the host operating system, not bundled font files. Their distribution is outside this asset inventory.

The scan found `assets/game.js`, the assembled application script. The repository identifies it as the TownLedger game bundle, and the root MIT license applies. No separate third-party library inventory or software bill of materials was found in the reviewed paths. Whether any code embedded in that assembled file is third-party: **provenance not yet verified**.

The repository includes original-sounding music and effects with explicit project-authored license statements above. No third-party font or library binary appeared in the filename scan. This finding is limited to the checked-in filenames; it does not certify every source dependency or every graphic's history.
