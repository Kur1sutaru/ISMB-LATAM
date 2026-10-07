from build_notebooks import code, exercise, md
from notebooks_src.common import setup, wrapup

META = dict(
    file="03_cell_type_annotation.ipynb",
    title=("03 · Cell type annotation", "03 · Anotación de tipos celulares"),
    time="11:00–11:35 (35 min)",
    goals=(
        ["Find marker genes for each cluster and annotate them manually with known markers",
         "Use a marker database (**PanglaoDB**) to score cell types",
         "Annotate automatically with a pre-trained classifier (**CellTypist**) and with a reference (`sc.tl.ingest`)",
         "Know where to find references and record annotations: **CZ CELLxGENE**, **Single Cell Portal**, "
         "**Cell Annotation Platform (CAP)**, Human Cell Atlas, Cell Ontology",
         "Compare annotation methods and decide on final labels"],
        ["Encontrar genes marcadores de cada clúster y anotarlos manualmente con marcadores conocidos",
         "Usar una base de datos de marcadores (**PanglaoDB**) para puntuar tipos celulares",
         "Anotar automáticamente con un clasificador preentrenado (**CellTypist**) y con una referencia (`sc.tl.ingest`)",
         "Saber dónde encontrar referencias y registrar anotaciones: **CZ CELLxGENE**, **Single Cell Portal**, "
         "**Cell Annotation Platform (CAP)**, Human Cell Atlas, Cell Ontology",
         "Comparar métodos de anotación y decidir las etiquetas finales"],
    ),
)

CELLS = [
    setup("annotation", extra_imports="import decoupler as dc"),
    code("""adata = tut.get_checkpoint("clustered", WORKDIR)
sc.pl.umap(adata, color="leiden", legend_loc="on data", title="Leiden clusters")"""),
    md(
        """## 1. Three ways to annotate 🟢

| Strategy | How | Pros | Cons |
|---|---|---|---|
| **Manual (markers)** | Find genes enriched in each cluster, compare with known markers | Transparent, uses your expertise | Slow, subjective, needs good markers |
| **Marker databases** | Score each cell with curated marker lists (PanglaoDB, CellMarker) | Fast, no reference data needed | Lists are generic, tissue context matters |
| **Reference-based / classifiers** | Transfer labels from an annotated atlas (CellTypist, ingest, scANVI, Azimuth, SingleR) | Fast, reproducible, fine-grained | Only as good as the reference; cannot find new types |

In practice you **combine** them and use the agreement between methods as evidence.""",
        """## 1. Tres formas de anotar 🟢

| Estrategia | Cómo | Ventajas | Desventajas |
|---|---|---|---|
| **Manual (marcadores)** | Buscar genes enriquecidos en cada clúster y compararlos con marcadores conocidos | Transparente, usa tu experiencia | Lenta, subjetiva, necesita buenos marcadores |
| **Bases de datos de marcadores** | Puntuar cada célula con listas curadas (PanglaoDB, CellMarker) | Rápida, no necesita datos de referencia | Listas genéricas, el contexto del tejido importa |
| **Por referencia / clasificadores** | Transferir etiquetas desde un atlas anotado (CellTypist, ingest, scANVI, Azimuth, SingleR) | Rápida, reproducible, detallada | Tan buena como la referencia; no encuentra tipos nuevos |

En la práctica se **combinan** y la concordancia entre métodos se usa como evidencia.""",
    ),
    md(
        """## 2. Data-driven marker genes 🟢
`sc.tl.rank_genes_groups` compares each cluster against all other cells (Wilcoxon rank-sum test on the
log-normalized values stored in `adata.raw`).""",
        """## 2. Genes marcadores a partir de los datos 🟢
`sc.tl.rank_genes_groups` compara cada clúster contra todas las demás células (prueba de Wilcoxon sobre los
valores log-normalizados guardados en `adata.raw`).""",
    ),
    code(
        """sc.tl.rank_genes_groups(adata, groupby="leiden", method="wilcoxon")
sc.tl.dendrogram(adata, groupby="leiden")
sc.pl.rank_genes_groups_dotplot(adata, n_genes=4, standard_scale="var")"""
    ),
    code(
        """markers_df = sc.get.rank_genes_groups_df(adata, group=None)
top = (markers_df.query("logfoldchanges > 1 and pvals_adj < 0.05")
       .groupby("group", observed=True).head(5)
       .groupby("group", observed=True)["names"].apply(", ".join))
top.to_frame("top 5 markers")"""
    ),
    md(
        """## 3. Manual annotation with known markers 🟢
Classic PBMC markers (from the Seurat/Scanpy tutorials and the literature):""",
        """## 3. Anotación manual con marcadores conocidos 🟢
Marcadores clásicos de PBMC (de los tutoriales de Seurat/Scanpy y la literatura):""",
    ),
    code(
        """pbmc_markers = tut.PBMC_MARKERS
pd.Series({k: ", ".join(v) for k, v in pbmc_markers.items()}).to_frame("markers")"""
    ),
    code(
        """sc.pl.dotplot(adata, pbmc_markers, groupby="leiden", standard_scale="var")"""
    ),
    md(
        """**Reading a dot plot:** dot **size** = % of cells in the cluster expressing the gene; **color** = mean expression
(scaled per gene). A good marker is big and dark in one group and small elsewhere.

To make this reproducible, we **score** each marker set per cell (`sc.tl.score_genes`) and give each cluster the
label with the highest average score.""",
        """**Cómo leer un dot plot:** el **tamaño** del punto = % de células del clúster que expresan el gen; el **color** =
expresión media (escalada por gen). Un buen marcador es grande y oscuro en un grupo y pequeño en los demás.

Para que sea reproducible, **puntuamos** cada conjunto de marcadores por célula (`sc.tl.score_genes`) y asignamos a
cada clúster la etiqueta con el puntaje promedio más alto.""",
    ),
    code(
        """adata = tut.annotate_by_markers(adata, pbmc_markers, cluster_key="leiden", key_added="cell_type")
score_cols = [c for c in adata.obs.columns if c.startswith("score_")]
display(adata.obs.groupby("leiden", observed=True)[score_cols].mean().round(2))
pd.crosstab(adata.obs["leiden"], adata.obs["cell_type"])"""
    ),
    md(
        """If you disagree with a label (that is your expertise!), override it with a dictionary:
```python
manual = {"0": "CD4 T", "1": "CD14 Mono", ...}      # cluster -> cell type
adata.obs["cell_type"] = adata.obs["leiden"].map(manual).astype("category")
```""",
        """Si no estás de acuerdo con una etiqueta (¡esa es tu experiencia!), corrígela con un diccionario:
```python
manual = {"0": "CD4 T", "1": "CD14 Mono", ...}      # clúster -> tipo celular
adata.obs["cell_type"] = adata.obs["leiden"].map(manual).astype("category")
```""",
    ),
    code("""sc.pl.umap(adata, color=["leiden", "cell_type"], legend_loc="on data", ncols=2)"""),
    md(
        """## 4. Marker database: PanglaoDB 🟢
[**PanglaoDB**](https://panglaodb.se) curates >8,000 marker–cell type associations from >1,000 single-cell
datasets (human and mouse). We download it through **OmniPath** with `decoupler` and score every cell with a
**univariate linear model (ULM)**: for each cell type, how strongly do its markers explain the cell's expression?""",
        """## 4. Base de datos de marcadores: PanglaoDB 🟢
[**PanglaoDB**](https://panglaodb.se) reúne >8.000 asociaciones marcador–tipo celular de >1.000 conjuntos de
single-cell (humano y ratón). La descargamos a través de **OmniPath** con `decoupler` y puntuamos cada célula con un
**modelo lineal univariado (ULM)**: para cada tipo celular, ¿qué tanto explican sus marcadores la expresión de la célula?""",
    ),
    code(
        """panglao = tut.cached_table("panglaodb_human", lambda: dc.op.resource("PanglaoDB", organism="human"), WORKDIR)
is_true = lambda s: s.astype(str).str.lower().isin(["true", "1", "1.0"])
markers_db = panglao[is_true(panglao["human"]) & is_true(panglao["canonical_marker"])
                     & (pd.to_numeric(panglao["human_sensitivity"], errors="coerce") > 0.5)]
markers_db = (markers_db.rename(columns={"cell_type": "source", "genesymbol": "target"})
              [["source", "target"]].drop_duplicates())
print(f"{markers_db['source'].nunique()} cell types, {len(markers_db)} markers")
markers_db.head()"""
    ),
    code(
        """dc.mt.ulm(adata, net=markers_db, tmin=3, raw=True)
panglao_scores = dc.pp.get_obsm(adata, "score_ulm")
ranked = dc.tl.rankby_group(panglao_scores, groupby="leiden")
top_panglao = (ranked[ranked["stat"] > 0].sort_values("stat", ascending=False)
               .groupby("group", observed=True).head(3)
               .groupby("group", observed=True)["name"].apply(" | ".join))
top_panglao.to_frame("top 3 PanglaoDB cell types")"""
    ),
    code(
        """best = ranked.sort_values("stat", ascending=False).groupby("group", observed=True).head(1).set_index("group")["name"]
adata.obs["panglaodb"] = adata.obs["leiden"].map(best).astype("category")
show = [c for c in ["T cells", "NK cells", "B cells", "Monocytes", "Dendritic cells", "Platelets"]
        if c in panglao_scores.var_names]
sc.pl.umap(panglao_scores, color=show, cmap="RdBu_r", vcenter=0, ncols=3)"""
    ),
    md(
        """## 5. Automated classifier: CellTypist 🟢
[**CellTypist**](https://www.celltypist.org) is a logistic-regression classifier trained on large immune atlases
(Domínguez Conde *et al.*, *Science* 2022). `Immune_All_Low` predicts ~98 fine-grained immune cell types;
`Immune_All_High` gives ~32 broader ones. Many other models exist (lung, gut, brain, developing tissues, mouse...).

CellTypist expects **log1p(counts per 10k)**, which is exactly what we stored in `adata.raw`.
`majority_voting=True` smooths the per-cell predictions within each cluster.""",
        """## 5. Clasificador automático: CellTypist 🟢
[**CellTypist**](https://www.celltypist.org) es un clasificador de regresión logística entrenado con grandes atlas
inmunes (Domínguez Conde *et al.*, *Science* 2022). `Immune_All_Low` predice ~98 tipos inmunes detallados;
`Immune_All_High` da ~32 más generales. Existen muchos otros modelos (pulmón, intestino, cerebro, tejidos en desarrollo, ratón...).

CellTypist espera **log1p(conteos por 10k)**, que es justo lo que guardamos en `adata.raw`.
`majority_voting=True` suaviza las predicciones por célula dentro de cada clúster.""",
    ),
    code(
        """import celltypist
from celltypist import models

model_name = "Immune_All_Low.pkl"
if not os.path.exists(models.get_model_path(model_name)):
    models.download_models(model=[model_name])

adata_ct = adata.raw.to_adata()     # all genes, log1p(CP10k) || todos los genes, log1p(CP10k)
pred = celltypist.annotate(adata_ct, model=model_name, majority_voting=True,
                           over_clustering="leiden")
adata.obs["celltypist"] = pred.predicted_labels["majority_voting"].astype("category").values
adata.obs["celltypist_conf"] = pred.probability_matrix.max(axis=1).values
sc.pl.umap(adata, color=["celltypist", "celltypist_conf"], ncols=2, wspace=0.6)"""
    ),
    md(
        """## 6. Reference mapping with `sc.tl.ingest` 🟢
`ingest` projects your cells onto the PCA/UMAP of an **annotated reference** and transfers the labels of the nearest
reference cells. Here the reference is `pbmc68k_reduced`, a small annotated subset of 68k PBMCs that ships with Scanpy.
The same idea scales to large atlases with **scANVI**, **scArches** or **Azimuth** (R).""",
        """## 6. Mapeo a una referencia con `sc.tl.ingest` 🟢
`ingest` proyecta tus células sobre el PCA/UMAP de una **referencia anotada** y transfiere las etiquetas de las células
de referencia más cercanas. Aquí la referencia es `pbmc68k_reduced`, un pequeño subconjunto anotado de 68k PBMCs que
viene con Scanpy. La misma idea escala a grandes atlas con **scANVI**, **scArches** o **Azimuth** (R).""",
    ),
    code(
        """ref = sc.datasets.pbmc68k_reduced()
shared = ref.var_names.intersection(adata.var_names)
ref = ref[:, shared].copy()
query = adata[:, shared].copy()
n_pcs = min(30, len(shared) - 1)
sc.pp.pca(ref, n_comps=n_pcs)
sc.pp.neighbors(ref, n_pcs=n_pcs)
sc.tl.umap(ref)
sc.tl.ingest(query, ref, obs="bulk_labels")
adata.obs["ingest"] = query.obs["bulk_labels"].values
print(len(shared), "shared genes")
sc.pl.umap(adata, color="ingest")"""
    ),
    md(
        """## 7. Where to find references and record annotations 🟢

| Resource | What it offers | How to use it from Python |
|---|---|---|
| [**PanglaoDB**](https://panglaodb.se) | Curated marker genes (human, mouse) | `decoupler.op.resource("PanglaoDB")` (above) |
| [**CellMarker 2.0**](http://bio-bigdata.hrbmu.edu.cn/CellMarker/) | Manually curated markers from >100k publications | Download table → same ULM approach |
| [**CZ CELLxGENE Discover**](https://cellxgene.cziscience.com) | >1,000 standardized datasets, >100 million cells, all with Cell Ontology labels; *Explorer* for interactive browsing; *Gene Expression* tool to check a marker across tissues | `cellxgene_census` package to download annotated references as AnnData |
| [**Single Cell Portal**](https://singlecell.broadinstitute.org) (Broad Institute) | Hundreds of studies with interactive plots and downloadable matrices/metadata | Download `.h5ad`/matrices → reference for ingest/CellTypist training |
| [**Cell Annotation Platform (CAP)**](https://celltype.info) | Upload your `.h5ad`, record **each** cell type with marker evidence, synonyms and Cell Ontology terms; share/publish annotations | Export `adata.write_h5ad(...)` with labels + marker genes |
| [**Human Cell Atlas Data Portal**](https://data.humancellatlas.org) | Raw and processed data from HCA projects | Download data/references |
| [**CellTypist models**](https://www.celltypist.org/models) | Pre-trained classifiers for many tissues | `celltypist.models.download_models()` |
| [**Cell Ontology (CL)**](https://www.ebi.ac.uk/ols4/ontologies/cl) | Standard IDs for cell types (`CL:0000236` = B cell) | Store IDs in `adata.obs` so others can reuse your labels |

**Good practice:** store a Cell Ontology ID next to each label. CELLxGENE and CAP use these IDs, and they make
your annotations comparable across studies.""",
        """## 7. Dónde encontrar referencias y registrar anotaciones 🟢

| Recurso | Qué ofrece | Cómo usarlo desde Python |
|---|---|---|
| [**PanglaoDB**](https://panglaodb.se) | Genes marcadores curados (humano, ratón) | `decoupler.op.resource("PanglaoDB")` (arriba) |
| [**CellMarker 2.0**](http://bio-bigdata.hrbmu.edu.cn/CellMarker/) | Marcadores curados manualmente de >100k publicaciones | Descargar la tabla → mismo enfoque ULM |
| [**CZ CELLxGENE Discover**](https://cellxgene.cziscience.com) | >1.000 conjuntos estandarizados, >100 millones de células, todos con etiquetas de Cell Ontology; *Explorer* para navegar; herramienta *Gene Expression* para ver un marcador en todos los tejidos | Paquete `cellxgene_census` para descargar referencias anotadas como AnnData |
| [**Single Cell Portal**](https://singlecell.broadinstitute.org) (Broad Institute) | Cientos de estudios con gráficos interactivos y matrices/metadatos descargables | Descargar `.h5ad`/matrices → referencia para ingest/entrenar CellTypist |
| [**Cell Annotation Platform (CAP)**](https://celltype.info) | Sube tu `.h5ad`, registra **cada** tipo celular con evidencia de marcadores, sinónimos y términos de Cell Ontology; comparte/publica anotaciones | Exportar `adata.write_h5ad(...)` con etiquetas + genes marcadores |
| [**Human Cell Atlas Data Portal**](https://data.humancellatlas.org) | Datos crudos y procesados de proyectos del HCA | Descargar datos/referencias |
| [**Modelos de CellTypist**](https://www.celltypist.org/models) | Clasificadores preentrenados para muchos tejidos | `celltypist.models.download_models()` |
| [**Cell Ontology (CL)**](https://www.ebi.ac.uk/ols4/ontologies/cl) | IDs estándar para tipos celulares (`CL:0000236` = célula B) | Guarda los IDs en `adata.obs` para que otros reutilicen tus etiquetas |

**Buena práctica:** guarda un ID de Cell Ontology junto a cada etiqueta. CELLxGENE y CAP usan estos IDs, y hacen que
tus anotaciones sean comparables entre estudios.""",
    ),
    code(
        """cell_ontology = {
    "CD4 T": ("CD4-positive, alpha-beta T cell", "CL:0000624"),
    "CD8 T": ("CD8-positive, alpha-beta T cell", "CL:0000625"),
    "NK": ("natural killer cell", "CL:0000623"),
    "B": ("B cell", "CL:0000236"),
    "CD14 Mono": ("CD14-positive monocyte", "CL:0001054"),
    "FCGR3A Mono": ("CD14-low, CD16-positive monocyte", "CL:0002396"),
    "DC": ("dendritic cell", "CL:0000451"),
    "Platelet": ("platelet", "CL:0000233"),
}
adata.obs["cell_type_ontology_term"] = adata.obs["cell_type"].map({k: v[0] for k, v in cell_ontology.items()})
adata.obs["cell_type_ontology_term_id"] = adata.obs["cell_type"].map({k: v[1] for k, v in cell_ontology.items()})
adata.obs[["cell_type", "cell_type_ontology_term", "cell_type_ontology_term_id"]].drop_duplicates().reset_index(drop=True)"""
    ),
    md(
        """🔎 **Extra: downloading a reference from CZ CELLxGENE** (not run in class):
1. Browse <https://cellxgene.cziscience.com/datasets>, filter by tissue/disease, open a dataset and copy its **dataset ID**.
2. Download it as AnnData:
```python
!pip install -q cellxgene-census
import cellxgene_census
cellxgene_census.download_source_h5ad("<dataset_id>", to_path="reference.h5ad")
ref = sc.read_h5ad("reference.h5ad")      # labels in ref.obs["cell_type"]
```
Then use it with `sc.tl.ingest`, or train your own CellTypist model: `celltypist.train(ref, labels="cell_type")`.""",
        """🔎 **Extra: descargar una referencia de CZ CELLxGENE** (no se ejecuta en clase):
1. Navega <https://cellxgene.cziscience.com/datasets>, filtra por tejido/enfermedad, abre un conjunto de datos y copia su **dataset ID**.
2. Descárgalo como AnnData:
```python
!pip install -q cellxgene-census
import cellxgene_census
cellxgene_census.download_source_h5ad("<dataset_id>", to_path="reference.h5ad")
ref = sc.read_h5ad("reference.h5ad")      # etiquetas en ref.obs["cell_type"]
```
Luego úsala con `sc.tl.ingest`, o entrena tu propio modelo de CellTypist: `celltypist.train(ref, labels="cell_type")`.""",
    ),
    md(
        """## 8. Do the methods agree? 🟢
Agreement between independent methods is your evidence. Disagreement points to clusters that need a closer look
(mixed clusters, doublets, rare or activated states).""",
        """## 8. ¿Coinciden los métodos? 🟢
La concordancia entre métodos independientes es tu evidencia. Las discrepancias señalan clústeres que requieren una
mirada más cercana (clústeres mixtos, dobletes, estados raros o activados).""",
    ),
    code(
        """sc.pl.umap(adata, color=["cell_type", "panglaodb", "celltypist", "ingest"], ncols=2, wspace=0.7)"""
    ),
    code(
        """import seaborn as sns
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, other in zip(axes, ["panglaodb", "celltypist", "ingest"]):
    tab = pd.crosstab(adata.obs["cell_type"], adata.obs[other], normalize="index")
    sns.heatmap(tab, cmap="Blues", ax=ax, cbar=False, vmin=0, vmax=1)
    ax.set(title=f"markers vs {other}", xlabel=other, ylabel="cell_type (markers)")
plt.tight_layout()"""
    ),
    md("""## 9. Save the annotated object 🟢""", """## 9. Guardar el objeto anotado 🟢"""),
    code(
        """adata.uns.pop("rank_genes_groups", None)   # recomputed by cell type in notebook 04 || se recalcula por tipo celular en el notebook 04
adata.write_h5ad(f"{WORKDIR}/results/pbmc3k_annotated.h5ad")
adata.obs["cell_type"].value_counts()"""
    ),
    exercise(
        """Run CellTypist again with the coarser model `Immune_All_High.pkl` and compare it with `cell_type`
using `pd.crosstab`. Which labels become broader?""",
        """Ejecuta CellTypist otra vez con el modelo más general `Immune_All_High.pkl` y compáralo con `cell_type`
usando `pd.crosstab`. ¿Qué etiquetas se vuelven más generales?""",
        """models.download_models(model=["Immune_All_High.pkl"])
pred_high = celltypist.annotate(adata_ct, model="Immune_All_High.pkl", majority_voting=True,
                                over_clustering="leiden")
pd.crosstab(adata.obs["cell_type"], pred_high.predicted_labels["majority_voting"].values)""",
    ),
    wrapup(
        "Every cell has a name. Next: **04 · Visualization, differential expression and downstream analysis**.",
        "Cada célula tiene nombre. Siguiente: **04 · Visualización, expresión diferencial y análisis posteriores**.",
    ),
]
