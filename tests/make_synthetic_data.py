"""Build small synthetic stand-ins for every dataset/resource the notebooks download.

Used only by the offline test suite (tests/run_notebooks.py) so the notebooks can be
executed end to end without internet access. Gene names are real human symbols for
the marker programs; the counts are simulated. Participants never need this file:
on Google Colab the notebooks download the real public data.

Usage:  python tests/make_synthetic_data.py <output_data_dir> <celltypist_model_dir>
"""
import gzip
import io
import os
import sys
import tarfile

import anndata as ad
import numpy as np
import pandas as pd
import scipy.io
import scipy.sparse as sp

rng = np.random.default_rng(42)

PROGRAMS = {
    "CD4 T": ["IL7R", "CD3D", "CD3E", "LDHB", "CCR7", "LEF1", "TCF7", "MAL", "CD4", "CD2"],
    "CD8 T": ["CD8A", "CD8B", "CD3D", "CD3E", "CCL5", "GZMK", "CD2", "LAG3"],
    "NK": ["GNLY", "NKG7", "GZMB", "PRF1", "KLRD1", "FCGR3A", "NCAM1", "GZMA", "KLRF1"],
    "B": ["MS4A1", "CD79A", "CD79B", "CD19", "BANK1", "HLA-DRA", "HLA-DQA1", "TCL1A"],
    "CD14 Mono": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1", "VCAN", "CST3", "CD68"],
    "FCGR3A Mono": ["FCGR3A", "MS4A7", "LST1", "AIF1", "IFITM3", "CST3", "CD68", "FCER1G"],
    "DC": ["FCER1A", "CST3", "CLEC10A", "CD1C", "HLA-DQA1", "HLA-DRA", "CLEC4C"],
    "Platelet": ["PPBP", "PF4", "GP9", "ITGA2B", "TUBB1"],
}
PROPS = {"CD4 T": .42, "CD8 T": .12, "NK": .06, "B": .13, "CD14 Mono": .17,
         "FCGR3A Mono": .05, "DC": .03, "Platelet": .02}
ISGS = ["ISG15", "IFI6", "IFIT1", "IFIT3", "MX1", "OAS1", "LY6E", "ISG20", "CXCL10",
        "IRF7", "STAT1", "IFI44L", "RSAD2", "IFITM1", "IFI27", "MX2", "OAS2", "HERC5"]
MITO = ["MT-ND1", "MT-ND2", "MT-CO1", "MT-CO2", "MT-ATP8", "MT-ATP6", "MT-CO3",
        "MT-ND3", "MT-ND4L", "MT-ND4", "MT-ND5", "MT-ND6", "MT-CYB"]
RIBO = [f"RPS{i}" for i in range(2, 30)] + [f"RPL{i}" for i in range(3, 40)]
HOUSE = ["ACTB", "GAPDH", "B2M", "MALAT1", "TMSB4X", "FTL", "FTH1", "EEF1A1", "TPT1", "HBA1", "HBB"]


def gene_universe(n_background):
    named = sorted({g for v in PROGRAMS.values() for g in v} | set(ISGS) | set(MITO) | set(RIBO) | set(HOUSE))
    background = [f"GENE{i:05d}" for i in range(n_background)]
    return named + background


def simulate(n_cells, genes, types, condition=None, donor=None, low_quality_frac=0.0, doublet_frac=0.0):
    g_idx = {g: i for i, g in enumerate(genes)}
    n_genes = len(genes)
    base = rng.gamma(0.3, 1.0, n_genes)
    for g in RIBO:
        base[g_idx[g]] = rng.uniform(8, 20)
    for g in MITO:
        base[g_idx[g]] = rng.uniform(2, 5)
    for g in HOUSE[:-2]:
        base[g_idx[g]] = rng.uniform(10, 30)
    type_profiles = {}
    for t, markers in PROGRAMS.items():
        prof = base.copy() * rng.lognormal(0, 0.15, n_genes)
        for m in markers:
            prof[g_idx[m]] += rng.uniform(15, 40)
        type_profiles[t] = prof
    # a few hundred background genes vary by type so HVG/PCA have structure
    for t in type_profiles:
        idx = rng.choice(np.arange(len(genes) - 3000, n_genes), 60, replace=False)
        type_profiles[t][idx] += rng.uniform(1, 4, 60)

    rows = []
    lib = rng.lognormal(np.log(2200), 0.45, n_cells)
    for c in range(n_cells):
        prof = type_profiles[types[c]].copy()
        if condition is not None and condition[c] == "stim":
            for g in ISGS:
                prof[g_idx[g]] += rng.uniform(10, 30)
            prof[g_idx["CXCL10"]] += 40 if "Mono" in types[c] else 0
            shift = np.arange(len(genes) - 400, len(genes) - 250)
            prof[shift] *= 3.0  # global condition shift -> needs integration
        if donor is not None:
            prof *= np.exp(donor_effects[donor[c]])
        rows.append(prof)
    rates = np.vstack(rows)
    if doublet_frac:
        nd = int(doublet_frac * n_cells)
        a = rng.choice(n_cells, nd, replace=False)
        b = rng.choice(n_cells, nd, replace=False)
        rates[a] = (rates[a] + rates[b])
        lib[a] *= 1.8
    rates = rates / rates.sum(1, keepdims=True) * lib[:, None]
    if low_quality_frac:
        nl = int(low_quality_frac * n_cells)
        lq = rng.choice(n_cells, nl, replace=False)
        mito_cols = [g_idx[g] for g in MITO]
        rates[lq] *= 0.25
        rates[np.ix_(lq, mito_cols)] *= 40
    counts = rng.poisson(rates).astype(np.float32)
    return sp.csr_matrix(counts)


if __name__ == "__main__":
    data_dir, model_dir = sys.argv[1], sys.argv[2]
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    genes = gene_universe(3000)

    # ---- 1. 10x Cell Ranger output, PBMC 3k layout (filtered_gene_bc_matrices/hg19) ----
    n = 2700
    types = rng.choice(list(PROPS), n, p=list(PROPS.values()))
    donor_effects = {}
    X = simulate(n, genes, types, low_quality_frac=0.05, doublet_frac=0.04)
    barcodes = [f"{''.join(rng.choice(list('ACGT'), 14))}-1" for _ in range(n)]
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        def add(name, payload):
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
        mtx = io.BytesIO()
        scipy.io.mmwrite(mtx, X.T.tocoo().astype(np.int64), field="integer")
        add("filtered_gene_bc_matrices/hg19/matrix.mtx", mtx.getvalue())
        add("filtered_gene_bc_matrices/hg19/genes.tsv",
            "".join(f"ENSG{i:011d}\t{g}\n" for i, g in enumerate(genes)).encode())
        add("filtered_gene_bc_matrices/hg19/barcodes.tsv", "".join(b + "\n" for b in barcodes).encode())
    with open(os.path.join(data_dir, "pbmc3k_filtered_gene_bc_matrices.tar.gz"), "wb") as fh:
        fh.write(buf.getvalue())

    # ---- 2. Kang et al. 2018 IFN-beta PBMC (ctrl vs stim, 8 donors) ----
    kang_types = {"CD4 T": "CD4 T cells", "CD8 T": "CD8 T cells", "NK": "NK cells", "B": "B cells",
                  "CD14 Mono": "CD14+ Monocytes", "FCGR3A Mono": "FCGR3A+ Monocytes",
                  "DC": "Dendritic cells", "Platelet": "Megakaryocytes"}
    donors = ["patient_101", "patient_1015", "patient_1016", "patient_1039",
              "patient_107", "patient_1244", "patient_1256", "patient_1488"]
    donor_effects = {d: rng.normal(0, 0.05, len(genes)) for d in donors}
    nk = 6000
    t2 = rng.choice(list(PROPS), nk, p=list(PROPS.values()))
    cond = rng.choice(["ctrl", "stim"], nk)
    don = rng.choice(donors, nk)
    Xk = simulate(nk, genes, t2, condition=cond, donor=don)
    kang = ad.AnnData(Xk, obs=pd.DataFrame({
        "label": pd.Categorical(cond), "replicate": pd.Categorical(don),
        "cell_type": pd.Categorical([kang_types[t] for t in t2])},
        index=[f"cell{i}" for i in range(nk)]), var=pd.DataFrame(index=genes))
    kang.write_h5ad(os.path.join(data_dir, "kang_counts_25k.h5ad"))

    # ---- 3. Marker / gene-set resources (same columns as the OmniPath downloads) ----
    pang_names = {"CD4 T": "T cells", "CD8 T": "T cells", "NK": "NK cells", "B": "B cells",
                  "CD14 Mono": "Monocytes", "FCGR3A Mono": "Monocytes", "DC": "Dendritic cells",
                  "Platelet": "Platelets"}
    rows = []
    for t, ms in PROGRAMS.items():
        for m in ms:
            rows.append(dict(genesymbol=m, canonical_marker=True, cell_type=pang_names[t],
                             germ_layer="Mesoderm", human=True, human_sensitivity=0.8,
                             human_specificity=0.1, mouse=True, organ="Immune system"))
    for m in ["GENE00001", "GENE00002", "GENE00003", "GENE00004"]:
        rows.append(dict(genesymbol=m, canonical_marker=True, cell_type="Hepatocytes", germ_layer="Endoderm",
                         human=True, human_sensitivity=0.9, human_specificity=0.1, mouse=True, organ="Liver"))
    pd.DataFrame(rows).drop_duplicates(["genesymbol", "cell_type"]).to_csv(
        os.path.join(data_dir, "panglaodb_human.csv"), index=False)

    hall = []
    for g in ISGS:
        hall += [("HALLMARK_INTERFERON_ALPHA_RESPONSE", g), ("HALLMARK_INTERFERON_GAMMA_RESPONSE", g)]
    for g in ["S100A8", "S100A9", "CD14", "LYZ", "FCN1", "VCAN", "CD68"]:
        hall.append(("HALLMARK_INFLAMMATORY_RESPONSE", g))
    for g in ["CD3D", "CD3E", "IL7R", "CCR7", "LEF1", "TCF7", "CD2"]:
        hall.append(("HALLMARK_IL2_STAT5_SIGNALING", g))
    for i in range(30):
        hall.append(("HALLMARK_OXIDATIVE_PHOSPHORYLATION", f"GENE{100 + i:05d}"))
    pd.DataFrame(hall, columns=["source", "target"]).to_csv(os.path.join(data_dir, "hallmark_human.csv"), index=False)

    prog = [("JAK-STAT", g, rng.uniform(1, 4), 1e-5) for g in ISGS]
    prog += [("NFkB", g, rng.uniform(1, 3), 1e-5) for g in ["CXCL10", "S100A8", "CD14", "LYZ", "NFKBIA"] if g in genes]
    prog += [("TNFa", g, rng.uniform(1, 3), 1e-5) for g in ["S100A9", "FCN1", "VCAN", "CD68", "LST1"]]
    prog += [("Hypoxia", f"GENE{200 + i:05d}", rng.uniform(1, 3), 1e-5) for i in range(20)]
    pd.DataFrame(prog, columns=["source", "target", "weight", "padj"]).to_csv(
        os.path.join(data_dir, "progeny_human.csv"), index=False)

    # ---- 4. CellTypist model stand-in named like the real Immune_All_Low.pkl ----
    import scanpy as sc
    from celltypist.models import Model
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    ct_names = {"CD4 T": "Tcm/Naive helper T cells", "CD8 T": "Tem/Trm cytotoxic T cells",
                "NK": "CD16+ NK cells", "B": "Naive B cells", "CD14 Mono": "Classical monocytes",
                "FCGR3A Mono": "Non-classical monocytes", "DC": "DC2", "Platelet": "Megakaryocytes/platelets"}
    tr = ad.AnnData(X.copy())
    tr.var_names = genes
    sc.pp.normalize_total(tr, target_sum=1e4)
    sc.pp.log1p(tr)
    labels = np.array([ct_names[t] for t in types])
    scaler = StandardScaler()
    Xs = scaler.fit_transform(tr.X.toarray())
    clf = LogisticRegression(max_iter=300).fit(Xs, labels)
    clf.features = np.array(genes)
    Model(clf, scaler, {"date": "synthetic", "details": "offline test stand-in", "url": "", "source": "",
                        "version": "test", "number_celltypes": len(set(labels))}).write(
        os.path.join(model_dir, "Immune_All_Low.pkl"))
    print("synthetic data written to", data_dir)
