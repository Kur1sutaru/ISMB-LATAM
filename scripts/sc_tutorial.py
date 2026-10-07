"""Helper functions for the tutorial "From Cells to Clusters" (ISCB-LATAM SolBio SPBBC 2026).

Every notebook downloads this file at the start. It does two jobs:

1. ``download`` / ``load_pbmc3k_raw`` / ``load_kang``: fetch the public datasets once and
   reuse the local copy afterwards.
2. ``get_checkpoint``: each Colab notebook runs in its own virtual machine, so a notebook
   cannot see the files saved by the previous one. ``get_checkpoint`` loads the saved
   result if it exists (e.g. on Google Drive) and otherwise rebuilds it from the raw data
   with exactly the same parameters used in the notebooks. Rebuilding takes ~1 minute.

Everything here is plain Scanpy; read it if you are curious, it is the whole pipeline
in ~100 lines.
"""
from __future__ import annotations

import os
import tarfile
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc

URLS = {
    # Cell Ranger output for 2,700 PBMCs from a healthy donor (10x Genomics, CC BY 4.0)
    "pbmc3k": "https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz",
    # Kang et al. 2018 (Nat Biotechnol): PBMCs from 8 lupus patients, control vs IFN-beta
    "kang": "https://figshare.com/ndownloader/files/34464122",
}

# Canonical PBMC markers (Seurat/Scanpy PBMC 3k tutorials, PanglaoDB, CellMarker)
PBMC_MARKERS = {
    "CD4 T": ["IL7R", "CCR7", "CD3E", "LDHB"],
    "CD8 T": ["CD8A", "CD8B", "CCL5"],
    "NK": ["GNLY", "NKG7", "KLRD1"],
    "B": ["MS4A1", "CD79A", "CD79B"],
    "CD14 Mono": ["CD14", "LYZ", "S100A8"],
    "FCGR3A Mono": ["FCGR3A", "MS4A7"],
    "DC": ["FCER1A", "CLEC10A"],
    "Platelet": ["PPBP", "PF4"],
}

SEED = 0


def download(url: str, dest: str | Path) -> Path:
    """Download ``url`` to ``dest`` unless the file already exists."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        print(f"Downloading {url.split('/')[-1]} ...")
        urllib.request.urlretrieve(url, dest)
    return dest


def load_pbmc3k_raw(workdir: str | Path = "sc_tutorial"):
    """Download and read the Cell Ranger 'filtered_feature_bc_matrix' for PBMC 3k."""
    data = Path(workdir) / "data"
    tar = download(URLS["pbmc3k"], data / "pbmc3k_filtered_gene_bc_matrices.tar.gz")
    mtx_dir = data / "filtered_gene_bc_matrices" / "hg19"
    if not mtx_dir.exists():
        with tarfile.open(tar) as fh:
            fh.extractall(data)
    adata = sc.read_10x_mtx(mtx_dir, var_names="gene_symbols", cache=False)
    adata.var_names_make_unique()
    return adata


def load_kang(workdir: str | Path = "sc_tutorial"):
    """Kang et al. 2018 IFN-beta stimulation dataset (raw counts in .X)."""
    path = download(URLS["kang"], Path(workdir) / "data" / "kang_counts_25k.h5ad")
    adata = sc.read_h5ad(path)
    adata.obs["sample"] = adata.obs["replicate"].astype(str) + "_" + adata.obs["label"].astype(str)
    return adata


# --------------------------------------------------------------------------------------
# The pipeline, one function per notebook (same parameters as in the notebooks)
# --------------------------------------------------------------------------------------
def run_qc(adata):
    """Notebook 01: QC metrics, filtering, doublets, normalization, HVGs."""
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    adata.var["ribo"] = adata.var_names.str.startswith(("RPS", "RPL"))
    adata.var["hb"] = adata.var_names.str.contains(r"^HB[^(P)]")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt", "ribo", "hb"], inplace=True, log1p=True)
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=3)
    adata = adata[(adata.obs.n_genes_by_counts < 2500) & (adata.obs.pct_counts_mt < 5)].copy()
    sc.pp.scrublet(adata, random_state=SEED)
    adata = adata[~adata.obs["predicted_doublet"]].copy()
    adata.layers["counts"] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    adata.raw = adata
    sc.pp.highly_variable_genes(adata, n_top_genes=2000)
    return adata


def run_clustering(adata, resolution: float = 0.8):
    """Notebook 02: PCA, neighbors, UMAP, Leiden."""
    sc.tl.pca(adata, n_comps=50, mask_var="highly_variable", random_state=SEED)
    sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30, random_state=SEED)
    sc.tl.umap(adata, random_state=SEED)
    sc.tl.leiden(adata, resolution=resolution, key_added="leiden",
                 flavor="igraph", n_iterations=2, directed=False, random_state=SEED)
    return adata


def annotate_by_markers(adata, markers: dict | None = None, cluster_key: str = "leiden",
                        key_added: str = "cell_type"):
    """Notebook 03: score each marker set and give every cluster its best-scoring label."""
    markers = markers or PBMC_MARKERS
    scores = {}
    for ct, genes in markers.items():
        genes = [g for g in genes if g in adata.raw.var_names]
        if genes:
            sc.tl.score_genes(adata, genes, score_name=f"score_{ct}", use_raw=True, random_state=SEED)
            scores[ct] = f"score_{ct}"
    per_cluster = adata.obs.groupby(cluster_key, observed=True)[list(scores.values())].mean()
    best = per_cluster.idxmax(axis=1).str.replace("score_", "", regex=False)
    adata.obs[key_added] = adata.obs[cluster_key].map(best).astype("category")
    return adata


STAGES = ["qc", "clustered", "annotated"]


def get_checkpoint(stage: str, workdir: str | Path = "sc_tutorial"):
    """Load results/pbmc3k_<stage>.h5ad, or rebuild it from the raw data if missing."""
    assert stage in STAGES, f"stage must be one of {STAGES}"
    res = Path(workdir) / "results"
    res.mkdir(parents=True, exist_ok=True)
    path = res / f"pbmc3k_{stage}.h5ad"
    if path.exists():
        print(f"Loading checkpoint {path}")
        return sc.read_h5ad(path)
    print(f"Checkpoint {path.name} not found: rebuilding it from the raw data (about 1 min)...")
    adata = run_qc(load_pbmc3k_raw(workdir))
    if stage in ("clustered", "annotated"):
        adata = run_clustering(adata)
    if stage == "annotated":
        adata = annotate_by_markers(adata)
    adata.write_h5ad(path)
    return adata


def cached_table(name: str, fetch, workdir: str | Path = "sc_tutorial") -> pd.DataFrame:
    """Return data/<name>.csv if present, otherwise call ``fetch()`` and save the result."""
    path = Path(workdir) / "data" / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path)
    df = fetch()
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def neighbor_mixing(adata, batch_key: str, use_rep: str, k: int = 30) -> float:
    """Average fraction of each cell's k nearest neighbours that come from another batch,
    divided by the fraction expected by chance (1 = perfectly mixed, 0 = fully separated)."""
    from sklearn.neighbors import NearestNeighbors

    X = adata.obsm[use_rep]
    labels = np.asarray(adata.obs[batch_key].astype(str).to_numpy(), dtype=object)
    nn = NearestNeighbors(n_neighbors=k + 1).fit(X)
    idx = nn.kneighbors(X, return_distance=False)[:, 1:]
    observed = (labels[idx] != labels[:, None]).mean()
    freqs = pd.Series(labels).value_counts(normalize=True)
    expected = 1 - (freqs ** 2).sum()
    return float(observed / expected)
