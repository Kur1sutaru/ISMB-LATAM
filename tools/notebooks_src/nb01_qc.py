from build_notebooks import code, exercise, md
from notebooks_src.common import setup, wrapup

META = dict(
    file="01_quality_control_preprocessing.ipynb",
    title=("01 · Quality control and preprocessing", "01 · Control de calidad y preprocesamiento"),
    time="9:40–10:15 (35 min)",
    goals=(
        ["Compute and plot per-cell QC metrics (UMIs, genes, % mitochondrial, % ribosomal)",
         "Choose filtering thresholds: fixed cut-offs vs. data-driven (MAD) cut-offs",
         "Detect and remove doublets with Scrublet",
         "Normalize, log-transform and select highly variable genes"],
        ["Calcular y graficar métricas de calidad por célula (UMIs, genes, % mitocondrial, % ribosomal)",
         "Elegir umbrales de filtrado: cortes fijos vs. cortes basados en los datos (MAD)",
         "Detectar y eliminar dobletes con Scrublet",
         "Normalizar, transformar a log y seleccionar genes altamente variables"],
    ),
)

CELLS = [
    setup("base"),
    md(
        """## 1. Load the Cell Ranger matrix 🟢
`tut.load_pbmc3k_raw()` does what we did step by step in notebook 00 (download + `sc.read_10x_mtx`).""",
        """## 1. Cargar la matriz de Cell Ranger 🟢
`tut.load_pbmc3k_raw()` hace lo que hicimos paso a paso en el notebook 00 (descarga + `sc.read_10x_mtx`).""",
    ),
    code("""adata = tut.load_pbmc3k_raw(WORKDIR)
adata"""),
    md(
        """## 2. Why quality control? 🟢
Not every barcode is a healthy single cell:

| Problem | Signature | Why it happens |
|---|---|---|
| **Dying / broken cell** | few genes, high **% mitochondrial** reads | cytoplasmic mRNA leaks out, mitochondrial transcripts stay |
| **Empty droplet** with ambient RNA | very few UMIs and genes | Cell Ranger kept it as a cell |
| **Doublet** (two cells in one droplet) | unusually many UMIs/genes, mixed markers | ~0.8 % per 1,000 cells loaded |
| Red blood cell contamination | high **hemoglobin** (`HBA1`, `HBB`) | common in blood/tissue samples |

We flag them with a few numbers per cell.""",
        """## 2. ¿Por qué control de calidad? 🟢
No todos los códigos de barras son una célula individual sana:

| Problema | Señal | Por qué ocurre |
|---|---|---|
| **Célula muriendo / rota** | pocos genes, alto **% de lecturas mitocondriales** | el mRNA citoplasmático se escapa, los transcritos mitocondriales quedan |
| **Gota vacía** con RNA ambiental | muy pocos UMIs y genes | Cell Ranger la conservó como célula |
| **Doblete** (dos células en una gota) | demasiados UMIs/genes, marcadores mezclados | ~0,8 % por cada 1.000 células cargadas |
| Contaminación con glóbulos rojos | alta **hemoglobina** (`HBA1`, `HBB`) | común en sangre y tejidos |

Las detectamos con algunos números por célula.""",
    ),
    code(
        """# Flag gene groups (human symbols; for mouse use "mt-", ("Rps", "Rpl"), "^Hb[^(p)]") || Marcar grupos de genes (símbolos humanos; en ratón usa "mt-", ("Rps", "Rpl"), "^Hb[^(p)]")
adata.var["mt"] = adata.var_names.str.startswith("MT-")
adata.var["ribo"] = adata.var_names.str.startswith(("RPS", "RPL"))
adata.var["hb"] = adata.var_names.str.contains(r"^HB[^(P)]")
print(adata.var[["mt", "ribo", "hb"]].sum())

sc.pp.calculate_qc_metrics(adata, qc_vars=["mt", "ribo", "hb"], inplace=True, log1p=True)
adata.obs[["total_counts", "n_genes_by_counts", "pct_counts_mt", "pct_counts_ribo", "pct_counts_hb"]].describe().round(2)"""
    ),
    md("""### Look at the distributions 🟢""", """### Mirar las distribuciones 🟢"""),
    code(
        """sc.pl.violin(adata, ["n_genes_by_counts", "total_counts", "pct_counts_mt", "pct_counts_ribo"],
             jitter=0.4, multi_panel=True)"""
    ),
    code(
        """sc.pl.scatter(adata, x="total_counts", y="n_genes_by_counts", color="pct_counts_mt")"""
    ),
    md(
        """**How to read it:** healthy cells lie on the diagonal (more UMIs → more genes). Cells in the **bottom-left** with
**high % MT** (yellow) are low quality. Cells far to the **top-right** may be doublets.""",
        """**Cómo leerlo:** las células sanas están en la diagonal (más UMIs → más genes). Las células **abajo a la izquierda**
con **alto % MT** (amarillo) son de baja calidad. Las que están muy **arriba a la derecha** pueden ser dobletes.""",
    ),
    md(
        """## 3. Choosing thresholds 🟢
**Option A: fixed cut-offs.** Simple and common for well-known samples. For PBMC 3k the classic choice
(Seurat and Scanpy tutorials) is: ≥ 200 genes, < 2,500 genes, < 5 % mitochondrial.

**Option B: data-driven cut-offs (MAD).** Flag cells more than *k* **median absolute deviations** away from the
median. It adapts to each sample, which is useful when you have many samples or tissues with different
baselines (e.g. neurons or cardiomyocytes have naturally higher % MT).""",
        """## 3. Elegir umbrales 🟢
**Opción A: cortes fijos.** Simple y común para muestras conocidas. Para PBMC 3k la elección clásica (tutoriales
de Seurat y Scanpy) es: ≥ 200 genes, < 2.500 genes, < 5 % mitocondrial.

**Opción B: cortes basados en los datos (MAD).** Marca las células a más de *k* **desviaciones absolutas medianas**
de la mediana. Se adapta a cada muestra, útil cuando tienes muchas muestras o tejidos con valores basales
distintos (p. ej. neuronas o cardiomiocitos tienen naturalmente más % MT).""",
    ),
    code(
        """def is_outlier(adata, metric, nmads):
    x = adata.obs[metric]
    mad = np.median(np.abs(x - np.median(x)))
    return (x < np.median(x) - nmads * mad) | (x > np.median(x) + nmads * mad)

adata.obs["outlier_mad"] = (
    is_outlier(adata, "log1p_total_counts", 5)
    | is_outlier(adata, "log1p_n_genes_by_counts", 5)
    | is_outlier(adata, "pct_counts_mt", 3)
)
adata.obs["outlier_fixed"] = (
    (adata.obs.n_genes_by_counts < 200) | (adata.obs.n_genes_by_counts >= 2500) | (adata.obs.pct_counts_mt >= 5)
)
pd.crosstab(adata.obs["outlier_fixed"], adata.obs["outlier_mad"],
            rownames=["fixed cut-offs"], colnames=["MAD cut-offs"])"""
    ),
    md(
        """Both strategies mostly agree. We continue with the **fixed** cut-offs so your numbers match the classic
tutorials. Always report which thresholds you used in your methods section!""",
        """Ambas estrategias coinciden casi siempre. Seguimos con los cortes **fijos** para que tus números coincidan con
los tutoriales clásicos. ¡Siempre reporta los umbrales que usaste en la sección de métodos!""",
    ),
    code(
        """n0 = adata.n_obs
sc.pp.filter_cells(adata, min_genes=200)   # cells with < 200 genes || células con < 200 genes
sc.pp.filter_genes(adata, min_cells=3)     # genes seen in < 3 cells || genes vistos en < 3 células
adata = adata[(adata.obs.n_genes_by_counts < 2500) & (adata.obs.pct_counts_mt < 5)].copy()
print(f"cells: {n0} -> {adata.n_obs}   genes: {adata.n_vars}")"""
    ),
    code(
        """sc.pl.violin(adata, ["n_genes_by_counts", "total_counts", "pct_counts_mt"], jitter=0.4, multi_panel=True)"""
    ),
    md(
        """## 4. Doublets with Scrublet 🟢
Scrublet simulates artificial doublets by adding random pairs of cells, then scores every real cell by how similar
it is to the simulated doublets. It works **per sample** (use `batch_key="sample"` when you have several).""",
        """## 4. Dobletes con Scrublet 🟢
Scrublet simula dobletes artificiales sumando pares aleatorios de células y luego puntúa cada célula real según
cuánto se parece a los dobletes simulados. Funciona **por muestra** (usa `batch_key="sample"` si tienes varias).""",
    ),
    code(
        """sc.pp.scrublet(adata, random_state=0)
print(adata.obs["predicted_doublet"].value_counts())
sc.pl.scrublet_score_distribution(adata)"""
    ),
    code(
        """adata = adata[~adata.obs["predicted_doublet"]].copy()
print("cells after doublet removal:", adata.n_obs)"""
    ),
    md(
        """> 🔎 **Extra: ambient RNA.** Free-floating mRNA from lysed cells ends up in every droplet. Tools such as
> **SoupX** (R), **CellBender** (Python, GPU) or **scAR** estimate this "soup" from the `raw_feature_bc_matrix`
> and subtract it. It matters most for tissues with very abundant transcripts (e.g. epithelia, hemoglobin in blood).""",
        """> 🔎 **Extra: RNA ambiental.** El mRNA libre de células lisadas termina en todas las gotas. Herramientas como
> **SoupX** (R), **CellBender** (Python, GPU) o **scAR** estiman esa "sopa" a partir de `raw_feature_bc_matrix`
> y la restan. Importa sobre todo en tejidos con transcritos muy abundantes (p. ej. epitelios, hemoglobina en sangre).""",
    ),
    md(
        """## 5. Normalization 🟢
Cells were sequenced to different depths, so raw counts are not comparable. The standard approach:
1. **Keep the raw counts** in a layer (we need them later for pseudobulk differential expression).
2. **Scale** each cell to the same total (10,000 counts = "counts per 10k").
3. **Log-transform**, `log(x + 1)`, to reduce the effect of very highly expressed genes.

Alternatives: scran pooling, analytic Pearson residuals (`sc.experimental.pp.normalize_pearson_residuals`),
or `SCTransform` in Seurat.""",
        """## 5. Normalización 🟢
Las células se secuenciaron a distintas profundidades, así que los conteos crudos no son comparables. El enfoque estándar:
1. **Guardar los conteos crudos** en una capa (los necesitamos luego para la expresión diferencial pseudobulk).
2. **Escalar** cada célula al mismo total (10.000 conteos = "conteos por 10k").
3. **Transformar a log**, `log(x + 1)`, para reducir el efecto de los genes muy expresados.

Alternativas: agrupamiento de scran, residuos de Pearson analíticos (`sc.experimental.pp.normalize_pearson_residuals`)
o `SCTransform` en Seurat.""",
    ),
    code(
        """adata.layers["counts"] = adata.X.copy()   # raw counts, never modified || conteos crudos, nunca se modifican
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata  # snapshot of the log-normalized values of ALL genes || copia de los valores log-normalizados de TODOS los genes

fig, axes = plt.subplots(1, 2, figsize=(9, 3))
axes[0].hist(np.asarray(adata.layers["counts"].sum(1)).ravel(), bins=50, color="#264653")
axes[0].set(title="raw counts per cell", xlabel="total")
axes[1].hist(np.asarray(adata.X.sum(1)).ravel(), bins=50, color="#2a9d8f")
axes[1].set(title="after normalize + log1p", xlabel="total")
plt.tight_layout()"""
    ),
    md(
        """## 6. Highly variable genes (HVGs) 🟢
Most genes are either not expressed or constant across cells: they add noise but no information.
We keep the ~2,000 genes whose variance is higher than expected for their mean expression.
They are only **flagged** (`adata.var["highly_variable"]`); all genes stay in the object.""",
        """## 6. Genes altamente variables (HVGs) 🟢
La mayoría de los genes no se expresan o son constantes entre células: agregan ruido pero no información.
Nos quedamos con los ~2.000 genes cuya varianza es mayor de lo esperado para su expresión media.
Solo se **marcan** (`adata.var["highly_variable"]`); todos los genes siguen en el objeto.""",
    ),
    code(
        """sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pl.highly_variable_genes(adata)
print(adata.var.query("highly_variable").sort_values("dispersions_norm", ascending=False).head(15).index.tolist())"""
    ),
    md("""## 7. Save the checkpoint 🟢""", """## 7. Guardar el checkpoint 🟢"""),
    code(
        """os.makedirs(f"{WORKDIR}/results", exist_ok=True)
adata.write_h5ad(f"{WORKDIR}/results/pbmc3k_qc.h5ad")
adata"""
    ),
    exercise(
        """Reload the raw data (`tut.load_pbmc3k_raw(WORKDIR)`) and count how many cells would pass if you allowed
up to **10 %** mitochondrial reads instead of 5 %. Is that a big difference for PBMCs?""",
        """Vuelve a cargar los datos crudos (`tut.load_pbmc3k_raw(WORKDIR)`) y cuenta cuántas células pasarían si permitieras
hasta **10 %** de lecturas mitocondriales en vez de 5 %. ¿Es una gran diferencia para PBMCs?""",
        """raw = tut.load_pbmc3k_raw(WORKDIR)
raw.var["mt"] = raw.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(raw, qc_vars=["mt"], inplace=True)
for thr in (5, 10):
    keep = (raw.obs.n_genes_by_counts >= 200) & (raw.obs.n_genes_by_counts < 2500) & (raw.obs.pct_counts_mt < thr)
    print(thr, "% MT ->", keep.sum(), "cells")""",
    ),
    wrapup(
        "Your data is clean and normalized. Next: **02 · Dimensionality reduction and clustering**.",
        "Tus datos están limpios y normalizados. Siguiente: **02 · Reducción de dimensionalidad y clustering**.",
    ),
]
