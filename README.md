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
| `data/supplied.json` | 8 motifs from the original artwork; 6 traced to a source chart, 2 held back as untraced. |
| `data/supplied_charts.json` | Owner artwork charts fitted by the pipeline (Asset 29, held back as untraced). |
| `PROVENANCE.md` | Generated register: every pattern in use, its source chart and how it was adapted. |
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

## Sources (sources of truth)

No pattern is invented. Every motif and border band is traced from a real historical chart in one of two sources, and may only be approximated (cropped, fitted, recoloured, simplified) from it:

1. **Tatreez.app**, the Tirazain archive of charted Palestinian motifs: https://tatreez.app/motifs
2. **Widad Kamel Kawar & Tania Tamari Nasir, *Palestinian Embroidery: Traditional "Fallahi" Cross-Stitch* (2021)**, charts on pp.18–19.

`pipeline/build.py` leaves out any motif that has no source from these two and fails on an untraced border band. See [PROVENANCE.md](PROVENANCE.md) for the source and adaptation of each pattern.
