# Isolated visual redesign milestone

Enable `?cityArt=prototype`. The default renderer is unchanged. Original Canvas geometry replaces eight architectural categories using existing legal footprints, actor composition, camera and picking.

The paired captures use the same seeded town and camera. This first milestone is deliberately not a quality acceptance: homes currently read as overly narrow repetitive townhouses; terrain retains the existing tile noise; civic structures still use the old kit. These need resolving before a representative scene is shown as the intended final direction.

Canvas is the first prototype because it preserves tested picking, actor layers, offline loading and old WebView support with no dependency migration. There is no bundled WebGL framework in this tree. A WebGL replacement would require a separate geometry/picking/depth and fallback implementation; it has not been rejected, but adding that dependency before validating art direction would obscure the visual comparison.

Next: broaden house massing into several coherent forms, replace terrain noise with continuous terrain treatment, improve roads/contact shadows and vegetation, then compare actual moving bridge/traffic scenes and HTTP save/reload. Only after these checks should this style propagate. Production replacement is not authorized by this milestone.

Host warm draw sample: baseline 1.16ms, prototype .96ms (60 draws, one town; noisy host results). Both validate the same 169 residents and total funds, with no browser errors. Captures use the existing opaque-origin harness; no persistence claim is made. Measurements are in measurements.json.
