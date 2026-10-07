from build_notebooks import code, exercise, md
from notebooks_src.common import setup, wrapup

META = dict(
    file="05_integration_conditions_r_vs_python.ipynb",
    title=("05 · Integration, comparing conditions, and R vs. Python",
           "05 · Integración, comparación de condiciones y R vs. Python"),
    time="12:05–12:25 (20 min, live demo) + self-study",
    goals=(
        ["Recognize batch/condition effects in a multi-sample dataset",
         "Integrate samples with **Harmony** and **BBKNN** and evaluate mixing vs. biology",
         "Compare cell type proportions between conditions",
         "Run **pseudobulk differential expression** with PyDESeq2 and interpret it with pathway enrichment",
         "Map every step to its R/Seurat equivalent and move data between ecosystems"],
        ["Reconocer efectos de lote/condición en un conjunto con varias muestras",
         "Integrar muestras con **Harmony** y **BBKNN** y evaluar mezcla vs. biología",
         "Comparar proporciones de tipos celulares entre condiciones",
         "Hacer **expresión diferencial pseudobulk** con PyDESeq2 e interpretarla con enriquecimiento de vías",
         "Relacionar cada paso con su equivalente en R/Seurat y mover datos entre ecosistemas"],
    ),
)

CELLS = [
    setup("integration", extra_imports="import decoupler as dc\nimport seaborn as sns"),
    md(
        """## 1. The dataset: IFN-β stimulation of PBMCs 🟢
**Kang *et al.*, *Nature Biotechnology* 2018.** PBMCs from **8 lupus patients** were split in two: one half was left
untreated (**ctrl**) and the other was stimulated with **interferon-β for 6 h** (**stim**). Cells from the 8 donors
were pooled and each condition was run in its own 10x lane, so donors were later identified by their SNPs (*demuxlet*).
It is the same dataset used in Seurat's integration vignette (`ifnb`), so you can compare both tools directly.

Design: 8 donors × 2 conditions = 16 samples, ~25,000 cells, cell types already annotated.""",
        """## 1. El conjunto de datos: estimulación de PBMCs con IFN-β 🟢
**Kang *et al.*, *Nature Biotechnology* 2018.** Las PBMCs de **8 pacientes con lupus** se dividieron en dos: una mitad
quedó sin tratar (**ctrl**) y la otra se estimuló con **interferón-β por 6 h** (**stim**). Las células de los 8 donantes
se mezclaron y cada condición se corrió en su propio carril de 10x; luego los donantes se identificaron por sus SNPs
(*demuxlet*). Es el mismo conjunto que usa la viñeta de integración de Seurat (`ifnb`), así que puedes comparar ambas
herramientas directamente.

Diseño: 8 donantes × 2 condiciones = 16 muestras, ~25.000 células, tipos celulares ya anotados.""",
    ),
    code(
        """kang = tut.load_kang(WORKDIR)
print(kang)
pd.crosstab(kang.obs["replicate"], kang.obs["label"])"""
    ),
    md("""## 2. Standard processing, no integration 🟢""", """## 2. Procesamiento estándar, sin integración 🟢"""),
    code(
        """kang.layers["counts"] = kang.X.copy()
sc.pp.filter_genes(kang, min_cells=10)
sc.pp.normalize_total(kang, target_sum=1e4)
sc.pp.log1p(kang)
sc.pp.highly_variable_genes(kang, n_top_genes=2000, batch_key="label")
sc.tl.pca(kang, n_comps=30, mask_var="highly_variable", random_state=0)
sc.pp.neighbors(kang, n_pcs=30, random_state=0)
sc.tl.umap(kang, random_state=0)
kang.obsm["X_umap_uncorrected"] = kang.obsm["X_umap"].copy()
sc.pl.embedding(kang, basis="X_umap_uncorrected", color=["label", "cell_type"], ncols=2, wspace=0.5)"""
    ),
    md(
        """Every cell type is split in two islands, **ctrl** and **stim**. Part of that is real biology (interferon
response), part is technical (different lanes). Either way, it makes it hard to say "these are the same cell type
in both conditions". **Integration** aligns shared cell types across samples **in the embedding only**:
the counts are not changed, so we can still test for differences later.""",
        """Cada tipo celular aparece dividido en dos islas, **ctrl** y **stim**. Una parte es biología real (respuesta a
interferón) y otra es técnica (carriles distintos). En cualquier caso, dificulta decir "estos son el mismo tipo celular
en ambas condiciones". La **integración** alinea los tipos celulares compartidos entre muestras **solo en el embedding**:
los conteos no cambian, así que después aún podemos probar diferencias.""",
    ),
    md(
        """## 3. Integration with Harmony 🟢
**Harmony** iteratively clusters cells in PCA space and moves each sample's cells towards the cluster centers, removing
sample-specific shifts. It is fast, works on the PCA, and exists in both R and Python.""",
        """## 3. Integración con Harmony 🟢
**Harmony** agrupa iterativamente las células en el espacio de PCA y desplaza las células de cada muestra hacia los
centros de los grupos, eliminando los desplazamientos propios de cada muestra. Es rápido, trabaja sobre el PCA y existe en R y Python.""",
    ),
    code(
        """import harmonypy
ho = harmonypy.run_harmony(kang.obsm["X_pca"], kang.obs, "label", random_state=0, verbose=False)
Z = np.asarray(ho.Z_corr)
kang.obsm["X_pca_harmony"] = Z if Z.shape[0] == kang.n_obs else Z.T   # orientation differs between versions || la orientación cambia entre versiones

sc.pp.neighbors(kang, use_rep="X_pca_harmony", random_state=0)
sc.tl.umap(kang, random_state=0)
kang.obsm["X_umap_harmony"] = kang.obsm["X_umap"].copy()
sc.pl.embedding(kang, basis="X_umap_harmony", color=["label", "cell_type"], ncols=2, wspace=0.5)"""
    ),
    md(
        """## 4. Integration with BBKNN 🟢
**BBKNN** (batch-balanced kNN) does not change the PCA. Instead, when building the neighbor graph, it takes the same
number of neighbors **from each batch**. Very fast; the output is a graph, so it only affects clustering and UMAP.""",
        """## 4. Integración con BBKNN 🟢
**BBKNN** (kNN balanceado por lote) no modifica el PCA. En cambio, al construir el grafo de vecinos toma el mismo número
de vecinos **de cada lote**. Muy rápido; el resultado es un grafo, así que solo afecta el clustering y el UMAP.""",
    ),
    code(
        """import bbknn
bbknn.bbknn(kang, batch_key="label", n_pcs=30)
sc.tl.umap(kang, random_state=0)
kang.obsm["X_umap_bbknn"] = kang.obsm["X_umap"].copy()
sc.pl.embedding(kang, basis="X_umap_bbknn", color=["label", "cell_type"], ncols=2, wspace=0.5)"""
    ),
    md(
        """## 5. Did it work? Mixing vs. biological conservation 🟢
A good integration **mixes the batches** but **keeps cell types apart**. Two simple metrics on each UMAP:
- **Batch mixing**: among each cell's 30 nearest neighbors, the fraction from the other condition, relative to chance
  (1 = perfectly mixed, 0 = separated).
- **Cell type silhouette**: how well cell types stay separated (higher = better, range −1 to 1).

For real benchmarks use the **scIB** package (Luecken *et al.*, *Nature Methods* 2022), which computes ~14 metrics.""",
        """## 5. ¿Funcionó? Mezcla vs. conservación biológica 🟢
Una buena integración **mezcla los lotes** pero **mantiene separados los tipos celulares**. Dos métricas simples en cada UMAP:
- **Mezcla de lotes**: entre los 30 vecinos más cercanos de cada célula, la fracción de la otra condición, relativa al azar
  (1 = mezcla perfecta, 0 = separados).
- **Silueta de tipo celular**: qué tan separados siguen los tipos celulares (más alto = mejor, rango −1 a 1).

Para evaluaciones reales usa el paquete **scIB** (Luecken *et al.*, *Nature Methods* 2022), que calcula ~14 métricas.""",
    ),
    code(
        """from sklearn.metrics import silhouette_score
rows = []
for method in ["uncorrected", "harmony", "bbknn"]:
    rep = f"X_umap_{method}"
    rows.append({
        "method": method,
        "batch mixing (1 = best)": tut.neighbor_mixing(kang, "label", rep),
        "cell type silhouette": silhouette_score(kang.obsm[rep], kang.obs["cell_type"],
                                                 sample_size=min(5000, kang.n_obs), random_state=0),
    })
metrics = pd.DataFrame(rows).set_index("method").round(3)
metrics"""
    ),
    code(
        """fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, method in zip(axes, ["uncorrected", "harmony", "bbknn"]):
    sc.pl.embedding(kang, basis=f"X_umap_{method}", color="label", ax=ax, show=False,
                    title=f"{method}  (mixing {metrics.loc[method].iloc[0]:.2f})")
plt.tight_layout()"""
    ),
    md(
        """🔎 **Extra: scVI.** A deep generative model (variational autoencoder) that learns a batch-corrected latent space
from the raw counts. It handles complex batch structures and large atlases well, and its extension **scANVI** also
transfers labels. It is much faster on a GPU (*Runtime → Change runtime type → T4 GPU*). Set `RUN_SCVI = True` to try it.""",
        """🔎 **Extra: scVI.** Un modelo generativo profundo (autoencoder variacional) que aprende un espacio latente corregido
por lote a partir de los conteos crudos. Maneja bien estructuras de lote complejas y atlas grandes, y su extensión
**scANVI** también transfiere etiquetas. Es mucho más rápido en GPU (*Entorno de ejecución → Cambiar tipo → GPU T4*).
Cambia `RUN_SCVI = True` para probarlo.""",
    ),
    code(
        """RUN_SCVI = False
if RUN_SCVI:
    !pip install -q scvi-tools
    import scvi
    hvg = kang[:, kang.var["highly_variable"]].copy()
    scvi.model.SCVI.setup_anndata(hvg, layer="counts", batch_key="label")
    model = scvi.model.SCVI(hvg, n_latent=20)
    model.train(max_epochs=100)
    kang.obsm["X_scVI"] = model.get_latent_representation()
    sc.pp.neighbors(kang, use_rep="X_scVI")
    sc.tl.umap(kang)
    sc.pl.umap(kang, color=["label", "cell_type"])"""
    ),
    md(
        """## 6. Comparing cell type proportions between conditions 🟢
Now each sample (donor × condition) is a replicate. Plotting per-sample proportions shows both the effect and the
donor-to-donor variability.""",
        """## 6. Comparar proporciones de tipos celulares entre condiciones 🟢
Ahora cada muestra (donante × condición) es una réplica. Graficar las proporciones por muestra muestra tanto el efecto
como la variabilidad entre donantes.""",
    ),
    code(
        """comp = pd.crosstab(kang.obs["sample"], kang.obs["cell_type"], normalize="index")
meta = kang.obs[["sample", "replicate", "label"]].drop_duplicates().set_index("sample")
comp = comp.loc[meta.sort_values(["label", "replicate"]).index]

fig, axes = plt.subplots(1, 2, figsize=(16, 4.5), gridspec_kw={"width_ratios": [1.2, 1]})
comp.mul(100).plot.bar(stacked=True, ax=axes[0], width=0.85, colormap="tab20", legend=False)
axes[0].set(ylabel="% of cells", xlabel="")
axes[0].legend(bbox_to_anchor=(1, 1), frameon=False, fontsize=7)
long = comp.mul(100).join(meta).melt(id_vars=["replicate", "label"], var_name="cell_type", value_name="pct")
sns.boxplot(long, x="cell_type", y="pct", hue="label", ax=axes[1], fliersize=0)
sns.stripplot(long, x="cell_type", y="pct", hue="label", dodge=True, ax=axes[1], color="k", size=3, legend=False)
axes[1].tick_params(axis="x", rotation=60)
axes[1].set(ylabel="% of cells", xlabel="")
plt.tight_layout()"""
    ),
    md(
        """Proportions are **compositional**: if one cell type expands, all others shrink in percentage. Dedicated methods
account for this: **scCODA** and **Milo** (Python, available in `pertpy`), **propeller** (`speckle`, R), **sccomp** (R).""",
        """Las proporciones son **composicionales**: si un tipo celular se expande, todos los demás disminuyen en porcentaje.
Hay métodos específicos que lo consideran: **scCODA** y **Milo** (Python, disponibles en `pertpy`), **propeller**
(`speckle`, R), **sccomp** (R).""",
    ),
    md(
        """## 7. Pseudobulk differential expression: stim vs. ctrl 🟢
1. **Sum the raw counts** of all cells of the same cell type in the same sample → one "bulk" profile per sample × cell type.
2. Drop pseudobulk samples with too few cells or counts.
3. Test with **DESeq2** (here its Python port **PyDESeq2**). Because each donor appears in both conditions, we use a
   **paired design**: `~ replicate + label`.

This respects the real unit of replication (the donor), which keeps false positives under control
(Squair *et al.*, *Nature Communications* 2021).""",
        """## 7. Expresión diferencial pseudobulk: stim vs. ctrl 🟢
1. **Sumar los conteos crudos** de todas las células del mismo tipo en la misma muestra → un perfil "bulk" por muestra × tipo celular.
2. Eliminar las muestras pseudobulk con muy pocas células o conteos.
3. Probar con **DESeq2** (aquí su versión en Python, **PyDESeq2**). Como cada donante aparece en ambas condiciones, usamos un
   **diseño pareado**: `~ replicate + label`.

Esto respeta la verdadera unidad de replicación (el donante) y mantiene bajo control los falsos positivos
(Squair *et al.*, *Nature Communications* 2021).""",
    ),
    code(
        """pdata = dc.pp.pseudobulk(kang, sample_col="sample", groups_col="cell_type", layer="counts", mode="sum")
dc.pp.filter_samples(pdata, min_cells=10, min_counts=1000)
print(pdata)
pd.crosstab(pdata.obs["cell_type"], pdata.obs["label"])"""
    ),
    code(
        """import scipy.sparse as sp
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

def pseudobulk_deseq2(pdata, cell_type):
    sub = pdata[pdata.obs["cell_type"] == cell_type].copy()
    dc.pp.filter_by_expr(sub, group="label", min_count=10, min_total_count=15)
    X = sub.X.toarray() if sp.issparse(sub.X) else np.asarray(sub.X)
    sub.X = np.round(X).astype(int)
    sub.obs = sub.obs[["replicate", "label"]].astype(str)
    dds = DeseqDataSet(adata=sub, design="~replicate + label", quiet=True)
    dds.deseq2()
    stats = DeseqStats(dds, contrast=["label", "stim", "ctrl"], quiet=True)
    stats.summary()
    return stats.results_df.sort_values("padj")

res_mono = pseudobulk_deseq2(pdata, "CD14+ Monocytes")
print((res_mono["padj"] < 0.05).sum(), "genes with padj < 0.05")
res_mono.head(15)"""
    ),
    code(
        """d = res_mono.dropna(subset=["padj"]).copy()
d["nlp"] = -np.log10(d["padj"].clip(lower=1e-300))
sig = (d["padj"] < 0.05) & (d["log2FoldChange"].abs() > 1)
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(d.loc[~sig, "log2FoldChange"], d.loc[~sig, "nlp"], s=4, c="lightgray")
ax.scatter(d.loc[sig, "log2FoldChange"], d.loc[sig, "nlp"], s=6,
           c=np.where(d.loc[sig, "log2FoldChange"] > 0, "#d62728", "#1f77b4"))
for gene, r in d[sig].head(15).iterrows():
    ax.annotate(gene, (r["log2FoldChange"], r["nlp"]), fontsize=8)
ax.set(xlabel="log2 fold change (stim / ctrl)", ylabel="-log10 adjusted p-value",
       title="CD14+ monocytes: IFN-β vs control (pseudobulk, paired)")
plt.show()"""
    ),
    md(
        """Interferon-stimulated genes (*ISG15*, *IFIT1*, *IFI6*, *MX1*, *CXCL10*...) should dominate the top of the list.

### Pathway enrichment on the DE statistics
We use the DESeq2 **Wald statistic** of every gene (no arbitrary cut-off) and score the Hallmark and PROGENy gene sets
with a ULM.""",
        """Los genes estimulados por interferón (*ISG15*, *IFIT1*, *IFI6*, *MX1*, *CXCL10*...) deberían dominar el inicio de la lista.

### Enriquecimiento de vías sobre los estadísticos de DE
Usamos el **estadístico de Wald** de DESeq2 para todos los genes (sin un corte arbitrario) y puntuamos los conjuntos
Hallmark y PROGENy con un ULM.""",
    ),
    code(
        """hallmark = tut.cached_table("hallmark_human", lambda: dc.op.hallmark(organism="human"), WORKDIR)
progeny = tut.cached_table("progeny_human", lambda: dc.op.progeny(organism="human", top=500), WORKDIR)
stat = res_mono[["stat"]].dropna().T.rename(index={"stat": "CD14 Mono"})

hm_es, hm_p = dc.mt.ulm(stat, net=hallmark, tmin=5)
pg_es, pg_p = dc.mt.ulm(stat, net=progeny, tmin=5)
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
hm = hm_es.T["CD14 Mono"].sort_values()
hm = pd.concat([hm.head(5), hm.tail(10)])
axes[0].barh(hm.index.str.replace("HALLMARK_", ""), hm.values, color=np.where(hm > 0, "#d62728", "#1f77b4"))
axes[0].set(title="Hallmark (ULM score)", xlabel="score")
pg = pg_es.T["CD14 Mono"].sort_values()
axes[1].barh(pg.index, pg.values, color=np.where(pg > 0, "#d62728", "#1f77b4"))
axes[1].set(title="PROGENy pathways", xlabel="score")
plt.tight_layout()"""
    ),
    md(
        """🔎 **Extra: which cell types respond the most?** Run the same test for every cell type and count DEGs.""",
        """🔎 **Extra: ¿qué tipos celulares responden más?** Ejecuta la misma prueba para cada tipo celular y cuenta los DEGs.""",
    ),
    code(
        """n_deg = {}
for ct in pdata.obs["cell_type"].unique():
    if (pdata.obs["cell_type"] == ct).sum() >= 6:   # need enough pseudobulk samples || se necesitan suficientes muestras pseudobulk
        r = pseudobulk_deseq2(pdata, ct)
        n_deg[ct] = ((r["padj"] < 0.05) & (r["log2FoldChange"].abs() > 1)).sum()
pd.Series(n_deg).sort_values().plot.barh(figsize=(5, 3.5), color="#2a9d8f", title="DEGs (padj<0.05, |log2FC|>1)")
plt.show()"""
    ),
    md(
        """## 8. R vs. Python: the same analysis in both ecosystems 🟢

| Step | Python (scverse) | R |
|---|---|---|
| Data object | `AnnData` (`.h5ad`), `MuData` for multimodal | `Seurat` (`.rds`), `SingleCellExperiment` (Bioconductor) |
| Read Cell Ranger | `sc.read_10x_h5`, `sc.read_10x_mtx` | `Read10X_h5`, `Read10X` |
| QC metrics | `sc.pp.calculate_qc_metrics` | `PercentageFeatureSet`, `scater::addPerCellQC` |
| Doublets | `sc.pp.scrublet` | `scDblFinder`, `DoubletFinder` |
| Ambient RNA | CellBender, scAR | SoupX, DecontX |
| Normalization | `normalize_total` + `log1p`, Pearson residuals | `NormalizeData`, `SCTransform`, `scran` |
| HVGs | `sc.pp.highly_variable_genes` | `FindVariableFeatures`, `scran::modelGeneVar` |
| PCA / graph / UMAP | `sc.tl.pca`, `sc.pp.neighbors`, `sc.tl.umap` | `RunPCA`, `FindNeighbors`, `RunUMAP` |
| Clustering | `sc.tl.leiden` | `FindClusters` (Louvain/Leiden) |
| Markers | `sc.tl.rank_genes_groups` | `FindAllMarkers` (presto for speed) |
| Integration | Harmony, BBKNN, Scanorama, scVI/scANVI | Harmony, CCA/RPCA (`IntegrateLayers`), fastMNN |
| Automated annotation | CellTypist, `ingest`, scANVI, popV | SingleR, Azimuth, scType |
| Pseudobulk DE | decoupler + PyDESeq2 | muscat, DESeq2, edgeR, limma-voom |
| Enrichment / pathways | decoupler, GSEApy | fgsea, clusterProfiler, decoupleR |
| Cell–cell communication | LIANA+, CellPhoneDB | CellChat, NicheNet, LIANA |
| Trajectories | PAGA, scVelo, CellRank, Palantir | Monocle 3, Slingshot, tradeSeq |
| Spatial | Squidpy, SpatialData | Seurat, Giotto, Voyager |

**Which one should I use?** Both are excellent and widely published.
- **Python** shines with very large datasets (millions of cells, GPU via `rapids-singlecell`), deep-learning models
  (scvi-tools) and integration into machine-learning pipelines.
- **R** has Bioconductor's mature statistics (DESeq2, edgeR, limma), many specialized methods, and very polished
  Seurat vignettes.
- Results are similar but **not identical**: defaults differ (e.g. Seurat scales data before PCA, uses Louvain by default
  and a different HVG method). Always report software versions and parameters.

**Moving data between them:**
```python
adata.write_h5ad("pbmc.h5ad")          # Python -> file
```
```r
sce <- zellkonverter::readH5AD("pbmc.h5ad")            # -> SingleCellExperiment
seu <- Seurat::as.Seurat(sce, counts = "counts", data = "X")   # -> Seurat
# Seurat -> h5ad: zellkonverter::writeH5AD(as.SingleCellExperiment(seu), "pbmc.h5ad")
```
In a notebook you can even mix them with **`rpy2`** and **`anndata2ri`** (`%%R` cells).""",
        """## 8. R vs. Python: el mismo análisis en ambos ecosistemas 🟢

| Paso | Python (scverse) | R |
|---|---|---|
| Objeto de datos | `AnnData` (`.h5ad`), `MuData` para multimodal | `Seurat` (`.rds`), `SingleCellExperiment` (Bioconductor) |
| Leer Cell Ranger | `sc.read_10x_h5`, `sc.read_10x_mtx` | `Read10X_h5`, `Read10X` |
| Métricas de calidad | `sc.pp.calculate_qc_metrics` | `PercentageFeatureSet`, `scater::addPerCellQC` |
| Dobletes | `sc.pp.scrublet` | `scDblFinder`, `DoubletFinder` |
| RNA ambiental | CellBender, scAR | SoupX, DecontX |
| Normalización | `normalize_total` + `log1p`, residuos de Pearson | `NormalizeData`, `SCTransform`, `scran` |
| HVGs | `sc.pp.highly_variable_genes` | `FindVariableFeatures`, `scran::modelGeneVar` |
| PCA / grafo / UMAP | `sc.tl.pca`, `sc.pp.neighbors`, `sc.tl.umap` | `RunPCA`, `FindNeighbors`, `RunUMAP` |
| Clustering | `sc.tl.leiden` | `FindClusters` (Louvain/Leiden) |
| Marcadores | `sc.tl.rank_genes_groups` | `FindAllMarkers` (presto para mayor velocidad) |
| Integración | Harmony, BBKNN, Scanorama, scVI/scANVI | Harmony, CCA/RPCA (`IntegrateLayers`), fastMNN |
| Anotación automática | CellTypist, `ingest`, scANVI, popV | SingleR, Azimuth, scType |
| DE pseudobulk | decoupler + PyDESeq2 | muscat, DESeq2, edgeR, limma-voom |
| Enriquecimiento / vías | decoupler, GSEApy | fgsea, clusterProfiler, decoupleR |
| Comunicación célula–célula | LIANA+, CellPhoneDB | CellChat, NicheNet, LIANA |
| Trayectorias | PAGA, scVelo, CellRank, Palantir | Monocle 3, Slingshot, tradeSeq |
| Espacial | Squidpy, SpatialData | Seurat, Giotto, Voyager |

**¿Cuál debo usar?** Ambos son excelentes y muy publicados.
- **Python** destaca con conjuntos muy grandes (millones de células, GPU con `rapids-singlecell`), modelos de aprendizaje
  profundo (scvi-tools) e integración con pipelines de machine learning.
- **R** tiene la estadística madura de Bioconductor (DESeq2, edgeR, limma), muchos métodos especializados y viñetas de
  Seurat muy pulidas.
- Los resultados son parecidos pero **no idénticos**: los valores por defecto cambian (p. ej. Seurat escala los datos
  antes del PCA, usa Louvain por defecto y otro método de HVG). Reporta siempre versiones y parámetros.

**Mover datos entre ambos:**
```python
adata.write_h5ad("pbmc.h5ad")          # Python -> archivo
```
```r
sce <- zellkonverter::readH5AD("pbmc.h5ad")            # -> SingleCellExperiment
seu <- Seurat::as.Seurat(sce, counts = "counts", data = "X")   # -> Seurat
# Seurat -> h5ad: zellkonverter::writeH5AD(as.SingleCellExperiment(seu), "pbmc.h5ad")
```
En un notebook incluso puedes mezclarlos con **`rpy2`** y **`anndata2ri`** (celdas `%%R`).""",
    ),
    md(
        """### The same integration in Seurat v5 (for reference)
```r
library(Seurat); library(SeuratData)
InstallData("ifnb"); ifnb <- LoadData("ifnb")
ifnb[["RNA"]] <- split(ifnb[["RNA"]], f = ifnb$stim)
ifnb <- NormalizeData(ifnb) |> FindVariableFeatures() |> ScaleData() |> RunPCA()
ifnb <- IntegrateLayers(ifnb, method = HarmonyIntegration, orig.reduction = "pca", new.reduction = "harmony")
ifnb <- FindNeighbors(ifnb, reduction = "harmony", dims = 1:30) |> FindClusters(resolution = 0.8) |>
        RunUMAP(reduction = "harmony", dims = 1:30)
ifnb <- JoinLayers(ifnb)
# Pseudobulk DE
pb <- AggregateExpression(ifnb, assays = "RNA", return.seurat = TRUE, group.by = c("stim", "orig.ident", "seurat_annotations"))
```""",
        """### La misma integración en Seurat v5 (como referencia)
```r
library(Seurat); library(SeuratData)
InstallData("ifnb"); ifnb <- LoadData("ifnb")
ifnb[["RNA"]] <- split(ifnb[["RNA"]], f = ifnb$stim)
ifnb <- NormalizeData(ifnb) |> FindVariableFeatures() |> ScaleData() |> RunPCA()
ifnb <- IntegrateLayers(ifnb, method = HarmonyIntegration, orig.reduction = "pca", new.reduction = "harmony")
ifnb <- FindNeighbors(ifnb, reduction = "harmony", dims = 1:30) |> FindClusters(resolution = 0.8) |>
        RunUMAP(reduction = "harmony", dims = 1:30)
ifnb <- JoinLayers(ifnb)
# DE pseudobulk
pb <- AggregateExpression(ifnb, assays = "RNA", return.seurat = TRUE, group.by = c("stim", "orig.ident", "seurat_annotations"))
```""",
    ),
    exercise(
        """Run the pseudobulk analysis for **B cells** and list the 10 most significant genes. Are they the same
interferon genes as in monocytes?""",
        """Ejecuta el análisis pseudobulk para las **B cells** y lista los 10 genes más significativos. ¿Son los mismos
genes de interferón que en los monocitos?""",
        """res_b = pseudobulk_deseq2(pdata, "B cells")
print(res_b.head(10).index.tolist())
print("shared with monocytes:", set(res_b.head(20).index) & set(res_mono.head(20).index))""",
    ),
    md(
        """## 9. Where to go next
- **Single-cell best practices** (scverse book): <https://www.sc-best-practices.org>
- **Scanpy tutorials**: <https://scanpy.readthedocs.io/en/stable/tutorials/>
- **decoupler** (enrichment, pseudobulk): <https://decoupler.readthedocs.io>
- **scvi-tools** (deep generative models): <https://docs.scvi-tools.org>
- **Orchestrating Single-Cell Analysis with Bioconductor** (R): <https://bioconductor.org/books/release/OSCA/>
- **Seurat vignettes** (R): <https://satijalab.org/seurat/>
- **Galaxy Training Network**, single-cell track (no code): <https://training.galaxyproject.org/training-material/topics/single-cell/>
- Communities in the region: the **ISCB Regional Student Groups** (RSG-Brasil, RSG-Peru, RSG-Argentina, ...) and **ISCB-LATAM**.""",
        """## 9. Para seguir aprendiendo
- **Single-cell best practices** (libro de scverse): <https://www.sc-best-practices.org>
- **Tutoriales de Scanpy**: <https://scanpy.readthedocs.io/en/stable/tutorials/>
- **decoupler** (enriquecimiento, pseudobulk): <https://decoupler.readthedocs.io>
- **scvi-tools** (modelos generativos profundos): <https://docs.scvi-tools.org>
- **Orchestrating Single-Cell Analysis with Bioconductor** (R): <https://bioconductor.org/books/release/OSCA/>
- **Viñetas de Seurat** (R): <https://satijalab.org/seurat/>
- **Galaxy Training Network**, sección single-cell (sin código): <https://training.galaxyproject.org/training-material/topics/single-cell/>
- Comunidades en la región: los **Regional Student Groups de ISCB** (RSG-Brasil, RSG-Peru, RSG-Argentina, ...) e **ISCB-LATAM**.""",
    ),
    wrapup(
        "You went from a Cell Ranger matrix to clusters, cell types, DEGs, integrated conditions and pathways. "
        "Thank you for joining! Feedback and questions: open an issue at <https://github.com/Kur1sutaru/ISMB-LATAM/issues>.",
        "Fuiste de una matriz de Cell Ranger a clústeres, tipos celulares, DEGs, condiciones integradas y vías. "
        "¡Gracias por participar! Comentarios y preguntas: abre un issue en <https://github.com/Kur1sutaru/ISMB-LATAM/issues>.",
    ),
]
