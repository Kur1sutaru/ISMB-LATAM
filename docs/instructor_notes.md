# Instructor notes

## Before November 9

- [ ] **Run every notebook on Google Colab with the real data** (EN and ES), top to bottom, on a fresh free CPU runtime.
      The offline test suite (`tests/run_notebooks.py`) uses synthetic data because the build machine had no access to
      10x/figshare/OmniPath/CellTypist servers: it proves the code runs with the pinned versions, not that the
      biology looks right. Things to eyeball on real data:
  - 01: ~2,600 cells after QC + Scrublet (classic PBMC 3k: 2,638 before doublet removal).
  - 02: ~8–10 Leiden clusters at resolution 0.8.
  - 03: marker-based labels per cluster look right; CellTypist majority-voting labels are sensible; `ingest`
        transfers labels from `pbmc68k_reduced` (≈ 700 shared genes).
  - 05: Kang obs columns are `label`, `replicate`, `cell_type` (the code expects these); Harmony/BBKNN improve the
        mixing score; ISGs at the top of the CD14+ monocyte pseudobulk results.
- [ ] Time each notebook on Colab, including the `pip install` in the setup cell (~1 min per notebook).
- [ ] Download an **offline backup** to a USB stick / shared Drive folder in case the conference Wi-Fi fails:
      `pbmc3k_filtered_gene_bc_matrices.tar.gz`, `kang_counts_25k.h5ad`, the `data/*.csv` tables cached by the
      notebooks (PanglaoDB, Hallmark, PROGENy) and `~/.celltypist/data/models/Immune_All_Low.pkl`.
      Participants copy them into `sc_tutorial/data/` and the notebooks will skip the downloads.
- [ ] Export executed versions of the notebooks (with outputs) as HTML/PDF as a fallback for people who cannot run Colab.
- [ ] Email participants the link to `SETUP.md` one week before (ask them to run the Setup cell of notebook 00).
- [ ] Optional: archive a release on Zenodo (GitHub → Zenodo integration) to get a DOI, as promised in the proposal.

## Timing (9:00–12:30)

| Time | Block | Notes |
|---|---|---|
| 9:00–9:20 | Slides: intro | Ask attendees to open notebook 00 and run Setup while you talk |
| 9:20–9:40 | NB 00 | Mostly reading the Cell Ranger section + AnnData; skip exercise if late |
| 9:40–10:15 | NB 01 | Spend time on the QC plots and the fixed vs. MAD discussion |
| 10:15–10:45 | NB 02 | Run the resolution comparison live; leave t-SNE/PAGA as extra |
| 10:45–11:00 | Coffee | Helpers fix broken sessions |
| 11:00–11:35 | NB 03 | CellTypist download takes ~30 s; show the CELLxGENE/CAP websites in the browser |
| 11:35–12:05 | NB 04 | Do the plots live; ORA/PROGENy can be shown, not typed |
| 12:05–12:25 | NB 05 | Live demo (Kang download ~1 min: start it at the coffee break); R vs Python table |
| 12:25–12:30 | Wrap-up | Feedback form, link to repo, resources |

**If you fall behind:** skip the exercises (solutions are in the notebooks), turn NB 04 section 5 into a demo,
and present NB 05 only from the slides.

## Common issues

- *Colab "not authored by Google" warning* → Run anyway.
- *`ModuleNotFoundError` after a restart* → re-run the Setup cell.
- *A notebook cannot find the previous result* → expected: `tut.get_checkpoint()` rebuilds it (~1 min).
- *CellTypist and scikit-learn*: CellTypist 1.7 **training** (`celltypist.train`) breaks with scikit-learn ≥ 1.8
  (removed `multi_class`); **annotation** with pre-trained models works. The tutorial only annotates.
- *Harmony*: `sc.external.pp.harmony_integrate` breaks with harmonypy ≥ 2.0 (output orientation changed), so
  notebook 05 calls `harmonypy.run_harmony` directly and handles both orientations. A good teaching moment about
  pinning versions.
- *Pandas 3* returns Arrow-backed string columns; the helper converts them to NumPy before indexing.

## Updating the materials

Edit `tools/notebooks_src/nbXX_*.py` (never the `.ipynb` directly), then:
```bash
python tools/build_notebooks.py
python tests/run_notebooks.py --lang all
```
