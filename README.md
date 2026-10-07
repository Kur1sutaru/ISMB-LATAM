# From Cells to Clusters: An Introduction to Single-Cell RNA-seq Analysis in Python

**ISCB-LATAM SolBio SPBBC 2026 · Tutorial · Lima, Peru · Monday, November 9, 2026 · 9:00–12:30**

🇪🇸 [Versión en español](README.es.md)

**Instructor:** Dr. Cristal Villalba Silva, Postdoctoral Fellow, Center for Pain Therapeutics and Addiction Research,
UT Health San Antonio, USA · [GitHub](https://github.com/Kur1sutaru) · [ORCID 0000-0003-0283-7982](https://orcid.org/0000-0003-0283-7982)

A beginner-friendly, hands-on half-day tutorial that takes you from a **Cell Ranger count matrix** to **clusters,
annotated cell types, differentially expressed genes, pathways and integrated conditions**, entirely in
**Google Colab** (nothing to install, a browser and a Google account are enough). All materials are available in
**English and Spanish**.

---

## Quick start

1. Open the first notebook in Colab: **[English](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/00_setup_and_cellranger.ipynb)** · **[Español](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/00_setup_and_cellranger.ipynb)**
2. Sign in with your Google account and click *Copy to Drive* (so you can save your changes).
3. Run the cells in order with `Shift + Enter`.

Detailed instructions, including running locally: **[SETUP.md](SETUP.md)**.

## Schedule and materials

★ = hands-on block (~65 % of the time)

| Time | Session | English | Español |
|---|---|---|---|
| 9:00–9:20 | Welcome and introduction: single-cell technologies, 10x Genomics, Cell Ranger, analysis workflow | [slides](slides/en/) | [diapositivas](slides/es/) |
| 9:20–9:40 ★ | **00** · Setup, Cell Ranger outputs and the AnnData object | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/00_setup_and_cellranger.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/00_setup_and_cellranger.ipynb) |
| 9:40–10:15 ★ | **01** · Quality control, doublets, normalization, highly variable genes | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/01_quality_control_preprocessing.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/01_quality_control_preprocessing.ipynb) |
| 10:15–10:45 ★ | **02** · PCA, neighbor graph, UMAP, Leiden clustering | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/02_dimensionality_reduction_clustering.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/02_dimensionality_reduction_clustering.ipynb) |
| 10:45–11:00 | ☕ Coffee break | | |
| 11:00–11:35 ★ | **03** · Cell type annotation: markers, PanglaoDB, CellTypist, reference mapping; CELLxGENE, Single Cell Portal, CAP | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/03_cell_type_annotation.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/03_cell_type_annotation.ipynb) |
| 11:35–12:05 ★ | **04** · Visualization (UMAP, violin, dot plot, heatmap, proportions), DEGs, enrichment and pathway activity | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/04_visualization_deg_downstream.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/04_visualization_deg_downstream.ipynb) |
| 12:05–12:25 ★ | **05** · Integration (Harmony, BBKNN), proportions and pseudobulk DE between conditions, R vs. Python *(live demo + self-study)* | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/05_integration_conditions_r_vs_python.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/05_integration_conditions_r_vs_python.ipynb) |
| 12:25–12:30 | Wrap-up, resources, Q&A | | |

Each notebook marks 🟢 **Core** sections (covered live) and 🔎 **Extra** sections (for self-study), and includes
exercises with hidden solutions.

## Learning objectives

By the end of the tutorial, participants will be able to:

1. Explain how 10x Genomics droplet data become a count matrix with Cell Ranger, and which output files to use.
2. Load and navigate single-cell data with `AnnData` and Scanpy.
3. Perform and justify quality control: filtering low-quality cells and doublets.
4. Normalize data, select highly variable genes, and reduce dimensionality (PCA, UMAP).
5. Cluster cells with the Leiden algorithm and evaluate the effect of resolution.
6. Annotate cell types combining marker genes, marker databases (PanglaoDB), classifiers (CellTypist) and reference
   atlases (CZ CELLxGENE, Single Cell Portal, Cell Annotation Platform).
7. Visualize results and find differentially expressed genes, then interpret them with enrichment and pathway analysis.
8. Integrate samples, compare conditions with pseudobulk differential expression, and map the workflow to R/Seurat.

## Audience and prerequisites

**Level: beginner.** Graduate students, postdocs and researchers in biology, medicine and bioinformatics who have
(or soon will have) single-cell data.
- **Required:** basic Python (variables, lists, functions, importing libraries) or equivalent R experience;
  basic molecular biology (genes, mRNA, cell types).
- **Not required:** prior single-cell or machine-learning experience.
- **Bring:** a laptop with a modern web browser, internet access and a (free) Google account.

## Software

| Package | Used for |
|---|---|
| [Scanpy](https://scanpy.readthedocs.io) / [AnnData](https://anndata.readthedocs.io) | Core analysis and data structure |
| [leidenalg](https://github.com/vtraag/leidenalg) / [igraph](https://python.igraph.org) | Leiden clustering |
| Scrublet (in Scanpy) | Doublet detection |
| [decoupler](https://decoupler.readthedocs.io) | PanglaoDB / Hallmark / PROGENy (via OmniPath), enrichment, pseudobulk |
| [CellTypist](https://www.celltypist.org) | Automated cell type annotation |
| [harmonypy](https://github.com/slowkow/harmonypy), [BBKNN](https://github.com/Teichlab/bbknn) | Integration |
| [PyDESeq2](https://pydeseq2.readthedocs.io) | Pseudobulk differential expression |

Tested versions are pinned in [`requirements.txt`](requirements.txt).

## Datasets

All datasets are public and downloaded automatically by the notebooks; nothing needs to be downloaded by hand.

| Dataset | Used in | Source · License |
|---|---|---|
| **PBMC 3k**: 2,700 PBMCs from a healthy donor, Cell Ranger 1.1.0 output | 00–04 | [10x Genomics](https://www.10xgenomics.com/datasets) · CC BY 4.0 |
| **pbmc68k_reduced**: annotated PBMC reference (ships with Scanpy) | 03 | Zheng *et al.*, *Nat Commun* 2017 |
| **Kang 2018**: PBMCs from 8 lupus patients, control vs. IFN-β | 05 | Kang *et al.*, *Nat Biotechnol* 2018 · GEO [GSE96583](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE96583) |
| PanglaoDB markers, MSigDB Hallmark, PROGENy | 03–05 | via [OmniPath](https://omnipathdb.org) |
| CellTypist `Immune_All_Low` model | 03 | Domínguez Conde *et al.*, *Science* 2022 |

## Repository structure

```
notebooks/en/   Colab notebooks in English (00–05)
notebooks/es/   The same notebooks in Spanish
slides/en/      Lecture slides (PowerPoint + PDF), English
slides/es/      Lecture slides (PowerPoint + PDF), Spanish
scripts/        sc_tutorial.py: download helpers + checkpoints used by every notebook
docs/           Annotation resources, R ↔ Python cheat sheet, instructor notes
tools/          Source for the bilingual notebooks (build_notebooks.py)
tests/          Offline test suite (synthetic data that mimics every download)
```

## For developers / instructors

The notebooks are generated from one bilingual source so code stays identical in both languages:
```bash
pip install -r requirements.txt nbclient nbformat ipykernel
python tools/build_notebooks.py          # writes notebooks/en and notebooks/es
python tests/run_notebooks.py --lang all # executes all 12 notebooks offline on synthetic data
```

## License

- Code (notebooks, scripts): [MIT](LICENSE)
- Text, slides and figures: [CC BY 4.0](LICENSE-CC-BY-4.0.md)
- Datasets keep their original licenses (see table above).

## How to cite

If you use or adapt these materials, please cite them (see [`CITATION.cff`](CITATION.cff)):

> Villalba Silva, G. C. (2026). *From Cells to Clusters: An Introduction to Single-Cell RNA-seq Analysis in Python*.
> Tutorial, ISCB-LATAM SolBio SPBBC 2026, Lima, Peru. https://github.com/Kur1sutaru/ISMB-LATAM

## Acknowledgments

Built on the open-source work of the [scverse](https://scverse.org) community, the Scanpy and Seurat PBMC 3k tutorials,
the [Single-cell best practices](https://www.sc-best-practices.org) book, and the developers of decoupler, CellTypist,
Harmony, BBKNN and PyDESeq2. Thanks to the ISCB-LATAM SolBio SPBBC 2026 Tutorial Committee.
