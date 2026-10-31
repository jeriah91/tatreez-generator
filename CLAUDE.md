# CLAUDE.md — Tatreez Module Generator

Single-page generator for modular Palestinian tatreez (cross-stitch) compositions. Build: `python3 pipeline/build.py` → `dist/index.html`. Deployed on Netlify from `main`.

## Established design rules (set by the owner — do not relax)

### Grid and modules
- Square module = 13×13 stitches + 1-stitch margin on every side (15×15 cells, CELL=24px).
- Tall module = exactly double: 13 + 2 + 13 stitches high (28 inner). Wide is the same rotated.
- Large modules carry complex charts close to full size: **large** = 2×2 modules (28×28 stitches), **large tall** = 2×4 (28×58). An n-module span is 13n + 2(n−1) stitches. Share set by the "Large modules (area)" slider; they never appear in the border.
- Compositions are fully filled, Lego-like: no gaps, any mix of 1×1, 1×2, 2×1, 2×2, 2×4.

### Fill rule
- Every motif fills its whole field, leaving **exactly a 1-stitch margin** on all four sides — never 2.
- Checked on the **rendered** grid (after dense/negative rendering), not just the source data.
- Dense motifs (>60% filled) render in one thread: accent cells enclosed by the field become gaps, but outline/edge accents are stitched in the main thread so the motif still reaches the margin.

### Symmetry
- Patterns are symmetrical vertically, horizontally, or both — matching the source. No lopsided output.
- Symmetry is checked per stitch and per colour. A C4 pinwheel colouring does **not** count as mirror-balanced.
- Taller/wider modules must be symmetric. Large (2×2) motifs need at least one exact axis; large tall (2×4) motifs must be left↔right symmetric.
- Even fields (28, 58) centre a symmetric motif on an even axis: fitting doubles the centre line of odd-width charts (`make_odd` in `fit.py`). Growing a chart to a large field spreads duplicated lines across the motif and avoids the centre stem (`spread` in `expand_width/height`).
- Square modules only use motifs with at least one exact axis. Asymmetric motifs (e.g. birds) appear only as wide facing pairs, tagged with `faces: left|right` (set in `pipeline/run_fit.py` `FACES`).

### Orientation and spacing
- Directional motifs (cypress, trees, palms, birds) are **always upright**. Never flip them upside down.
- Tall stacked = top + 2 empty rows + the same top. Wide facing = left + 2 empty cols + mirrored left.
- Stacked/repeated stars are separated by equal spacing (2 empty stitches).
- Star side ornaments must connect to the star; on the Najma star they run vertically (cols 0 and 12, rows 4–8).
- **Connector rule:** repeats in a tall/wide module are joined through the gap by a stem on the centre line (`connectRepeats`), drawn in the accent thread (main thread on dense motifs). (Owner's reference example: Asset_28.svg — black stem joining the two repeats.)
- **Exception — facing birds:** motifs with `faces` (birds) are never joined; the 2-stitch gap stays empty so the pair reads as two separate birds.

### Colour
- Palette: green, off-white, black, red. Solid background, contrasting stitches.
- Accessible contrast (WCAG 1.4.11, ≥3:1). **Never** red on green, red on black, or green on black. In practice, stitches are off-white on a colour or a colour on off-white.
- Colours are balanced across all four by module area. Adjacent modules never share a background (hard rule).
- Frame modules in mirror-image positions share a colourway. If that makes a background clash unavoidable (e.g. a large module touching both the top and bottom runs), the solver relaxes it: first each side's run is mirrored only about its own centre, and only as a last resort is every frame module coloured on its own.
- Known limit: dense large motifs always carry ≥~30% off-white (off-white is in every colourway), so a high large-module share pushes off-white above 25%.

### Borders
- Toggle on/off. Choose all four sides or specific sides.
- One module deep. Runs are segmented symmetrically from each run's own centre. Corners use C4-symmetric motifs.
- Border strips use equal spacing; pictorial units stay upright.

### Sources
- Motifs come from Tatreez.app / Tirazain charts and the Kawar & Nasir PDF (source of truth), catalogued by region, historical city and type.
- Don't commit the source PDF.
- Owner artwork charts live in `data/supplied_charts.json` (e.g. `asset-29`, from `reference/artwork/Asset 29.svg`, one motif of the pair, made exactly symmetric) and are referenced from `spec.py` with `supplied=`. Tatreez.app charts can be reused for a second size with `chart=`.

### Output
- One SVG download. Groups: `#composition > #field, #border`; each module is its own `<g>` with an id like `NN-[border-side-]kind-motifid` and `data-*` metadata.

## Workflow
- Edit the UI/logic in `src/app.html`. Edit the motif list in `pipeline/spec.py`, then `npm run fit`.
- After changes, run `npm run shot` (no console errors), `npm run balance` and `npm run rules` (full rules check across thousands of seeds/settings, measured on the rendered grid). Stress-test new rules across many seeds and sizes; report violations of fill, symmetry, clash and contrast.
