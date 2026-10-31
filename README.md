# Tatreez Module Generator

A generator for grid-based, cross-stitch compositions built from Palestinian tatreez motifs. Each module is a 13×13 stitch field with a 1-stitch margin (15×15 overall), a tall/wide variant of 13+2+13, or a large module (2×2 = 28×28, 2×4 = 28×58) for complex charts. Compositions tile with no gaps, colours are auto-balanced across green, off-white, black and red, and the result downloads as one SVG with every module in its own group.

## Run locally

```bash
python3 pipeline/build.py        # writes dist/index.html
open dist/index.html             # it's a single self-contained page
```

No dependencies are needed to build. Python 3.9+ is enough.

## Project layout

| Path | What it is |
|---|---|
| `src/app.html` | The app template: UI, tiling, colour assignment, borders, SVG export. Placeholders (`__MOTIFS__`, `__BORDERS__`…) are filled at build. |
| `data/motifs.json` | 55 motifs (incl. 9 large) fitted to the grid from Tatreez.app charts and the Kawar & Nasir book. |
| `data/supplied.json` | 8 motifs from the original artwork. |
| `data/supplied_charts.json` | Owner artwork charts fitted by the pipeline (Asset 29). |
| `data/borders.json` | 9 border bands with prebuilt strips (`h13`, `h28`, `v13`, `v28`). |
| `data/charts.json` | 53 source charts transcribed from Tatreez.app. |
| `data/kawar/*.json` | Vector charts extracted from the Kawar & Nasir PDF. The PDF itself isn't committed. |
| `pipeline/` | Python: `fit.py` (crop/reduce/symmetry/fill), `spec.py` (the curated motif list), `run_fit.py` (→ motifs.json), `borders.py` (→ borders.json), `inventory_src.py` (source inventory), `build.py` (→ dist). |
| `tools/` | Playwright checks (`shot.js`, `bal.js`) and PDF/SVG extraction helpers. |
| `reference/artwork/` | The original SVG artwork the system is based on. |

## Regenerating motifs

```bash
npm run fit      # refit motifs + borders from source charts, then build
npm run audit    # symmetry report per motif
npm run rules    # full rules check across many seeds (needs Playwright)
npm install && npm run shot   # screenshot + console errors (needs Playwright)
```

## Deploy

Netlify builds with `python3 pipeline/build.py` and publishes `dist/` (see `netlify.toml`). Every push to `main` redeploys.

## Sources

- Tatreez.app and Tirazain motif archives
- Widad Kawar & Tania Tamari Nasir, *Palestinian Embroidery: Traditional "Fallahi" Cross-Stitch*
