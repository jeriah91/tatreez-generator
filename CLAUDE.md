# CLAUDE.md — Tatreez Module Generator

Single-page generator for modular Palestinian tatreez (cross-stitch) compositions. Build: `python3 pipeline/build.py` → `dist/index.html`. Deployed on Netlify from `main`.

## Established design rules (set by the owner — do not relax)

### Grid and modules
- Square module = 13×13 stitches + 1-stitch margin on every side (15×15 cells, CELL=24px).
- Tall module = exactly double: 13 + 2 + 13 stitches high (28 inner). Wide is the same rotated.
- Compositions are fully filled, Lego-like: no gaps, any mix of 1×1, 1×2, 2×1.

### Fill rule
- Every motif fills its whole field, leaving **exactly a 1-stitch margin** on all four sides — never 2.
- Checked on the **rendered** grid (after dense/negative rendering), not just the source data.
- Dense motifs (>60% filled) render in one thread: accent cells enclosed by the field become gaps, but outline/edge accents are stitched in the main thread so the motif still reaches the margin.

### Symmetry
- Patterns are symmetrical vertically, horizontally, or both — matching the source. No lopsided output.
- Symmetry is checked per stitch and per colour. A C4 pinwheel colouring does **not** count as mirror-balanced.
- Taller/wider modules must be symmetric.
- Square modules only use motifs with at least one exact axis. Asymmetric motifs (e.g. birds) appear only as wide facing pairs, tagged with `faces: left|right` (set in `pipeline/run_fit.py` `FACES`).

### Orientation and spacing
- Directional motifs (cypress, trees, palms, birds) are **always upright**. Never flip them upside down.
- Tall stacked = top + 2 empty rows + the same top. Wide facing = left + 2 empty cols + mirrored left.
- Stacked/repeated stars are separated by equal spacing (2 empty stitches).
- Star side ornaments must connect to the star; on the Najma star they run vertically (cols 0 and 12, rows 4–8).
- **Connector rule:** repeats in a tall/wide module are joined through the gap by a stem on the centre line (`connectRepeats`), drawn in the accent thread (main thread on dense motifs). (Owner's reference example: Asset_28.svg — black stem joining the two repeats.)

### Colour
- Palette: green, off-white, black, red. Solid background, contrasting stitches.
- Accessible contrast (WCAG 1.4.11, ≥3:1). **Never** red on green, red on black, or green on black. In practice, stitches are off-white on a colour or a colour on off-white.
- Colours are balanced across all four by module area. Adjacent modules never share a background.

### Borders
- Toggle on/off. Choose all four sides or specific sides.
- One module deep. Runs are segmented symmetrically from each run's own centre. Corners use C4-symmetric motifs.
- Border strips use equal spacing; pictorial units stay upright.

### Sources
- Motifs come from Tatreez.app / Tirazain charts and the Kawar & Nasir PDF (source of truth), catalogued by region, historical city and type.
- Don't commit the source PDF.

### Output
- One SVG download. Groups: `#composition > #field, #border`; each module is its own `<g>` with an id like `NN-[border-side-]kind-motifid` and `data-*` metadata.

## Workflow
- Edit the UI/logic in `src/app.html`. Edit the motif list in `pipeline/spec.py`, then `npm run fit`.
- After changes, run `npm run shot` (no console errors) and `npm run balance`. Stress-test new rules across many seeds and sizes; report violations of fill, symmetry, clash and contrast.
