# Architecture and living-city art pass

Apply this commit **after `eae3e914824f580cb896000543d26a34de6e9c9e`** on `codex/8-visual-world`, then reassemble the integrated bundle. The new `src/98zz-diorama.js` sorts after the freight kit and before instrumentation. It replaces architecture and landscaping functions at initialization, retaining the original kit for farms, forestry, quarries, shoreline structures and worksites. No economic/schema, service ownership, menus, music or Android changes.

This is a dedicated model/art pass, not another set of frontage decorations:

- Twenty re-authored sectors: homes; apartments, towers and offices; factories, warehouses and sawmills; grocers, bakeries and taverns; eight civic sectors; parks and squares.
- Six detached-home silhouettes with cross-gables, hip roofs, mansards, porch cottages, town houses and timber bungalows. Atlas-stable hashed variants avoid synchronizing with regular founding household IDs and repeating one roof along entire streets.
- North-light factory roofs, glazed warehouse clerestories and open sawmill sheds; industrial investment equipment and shuttered/closed detail remain grounded in existing state.
- Columned civic porticoes, school belfries, apparatus bays and hose towers, a police flag, recognizable clinics, and distinct upper-storey shopfronts.
- Stepped tower crowns, roof machinery, balconies, layered glazing and stronger material-specific plaster/brick/timber shading.
- Four original seasonal tree families, orchard fruit, branching, darker undersides and sunward crowns; redesigned crossed-path parks, seating and fountain squares.
- Cast shadows follow the new roof/mass heights and stack silhouettes. Production emissions originate at the actual new vents rather than the old arbitrary roof point.

`tests/test_diorama_art.py` checks all20 models, six distinct house forms, condition/night/detail differences, unclipped raster envelopes and no economic mutations. Existing sprite-envelope, atlas-byte, mobile-layout, transport, workday, older-WebView API, LOD and live2,000-resident gates were also exercised. The final source-bound2,000-resident result and exact paused/LOD checks are copied into `reports/art-direction`. Mobile-layout/API/workday gates passed before the final house-variant hash adjustment, which only changes static model choice.

`tools/capture_world_art.py eae3e91 reports/art-direction` produces same-seed same-camera before/after frames. Inspect the actual844×390 mobile capture, neighbourhood, industry, civic and night images; roughly33.5% of mobile pixels change beyond5RGB levels, but the pictures—not that metric—are the art review. `tools/capture_living_world.py` records an unedited40-frame host-browser session after20 economic days. The GIF follows actual screenshot cadence and contains no soundtrack; it is not a device FPS claim. Comparison and session JSON bind captures to the source hash.

Owned source: new `src/98zz-diorama.js`, one vent-origin hook in `src/65-landscape.js`, generated `assets/game.js`; new art test and living capture script, capture-tool extension, this note and paired evidence. The terrain/transport ledger itself is unchanged. Integration should regenerate the bundle, preserving any newer renderer changes made by the lead. No package/signing or publication performed. Physical Android review remains outstanding.
