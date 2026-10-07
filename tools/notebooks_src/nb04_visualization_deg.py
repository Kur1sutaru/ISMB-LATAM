from build_notebooks import code, exercise, md
from notebooks_src.common import setup, wrapup

META = dict(
    file="04_visualization_deg_downstream.ipynb",
    title=("04 · Visualization, differential expression and downstream analysis",
           "04 · Visualización, expresión diferencial y análisis posteriores"),
    time="11:35–12:05 (30 min)",
    goals=(
        ["Make publication-quality UMAPs, violin plots, dot plots, matrix plots and heatmaps",
         "Plot cell type proportions",
         "Find differentially expressed genes (DEGs) between cell types and draw a volcano plot",
         "Run over-representation analysis (MSigDB Hallmark) and pathway activity inference (PROGENy)",
         "Know why cell-level tests are **not** appropriate for comparing conditions"],
        ["Hacer UMAPs, violin plots, dot plots, matrix plots y heatmaps con calidad de publicación",
         "Graficar proporciones de tipos celulares",
         "Encontrar genes diferencialmente expresados (DEGs) entre tipos celulares y hacer un volcano plot",
         "Hacer análisis de sobrerrepresentación (MSigDB Hallmark) e inferencia de actividad de vías (PROGENy)",
         "Entender por qué las pruebas a nivel de célula **no** son apropiadas para comparar condiciones"],
    ),
)

CELLS = [
    setup("downstream", extra_imports="import decoupler as dc\nimport seaborn as sns"),
    code("""adata = tut.get_checkpoint("annotated", WORKDIR)
order = ["CD4 T", "CD8 T", "NK", "B", "CD14 Mono", "FCGR3A Mono", "DC", "Platelet"]
adata.obs["cell_type"] = adata.obs["cell_type"].cat.reorder_categories(
    [c for c in order if c in adata.obs["cell_type"].cat.categories])
markers = {k: v for k, v in tut.PBMC_MARKERS.items() if k in adata.obs["cell_type"].cat.categories}
adata"""),
    md(
        """## 1. UMAP, the many ways 🟢
Tips: put labels on the data instead of a legend, use a perceptually uniform colormap (`viridis`, `magma`) for
expression, and order the points so that expressing cells are drawn on top (`sort_order=True`, the default).""",
        """## 1. UMAP, de muchas formas 🟢
Consejos: pon las etiquetas sobre los datos en vez de una leyenda, usa un mapa de color perceptualmente uniforme
(`viridis`, `magma`) para la expresión y dibuja encima las células que expresan el gen (`sort_order=True`, por defecto).""",
    ),
    code(
        """sc.pl.umap(adata, color="cell_type", legend_loc="on data", legend_fontsize=9,
           legend_fontoutline=2, title="PBMC 3k cell types")"""
    ),
    code(
        """sc.pl.umap(adata, color=["MS4A1", "CD14", "GNLY", "FCGR3A"], cmap="magma", vmax="p99",
           ncols=4, use_raw=True)"""
    ),
    code(
        """# Highlight one population || Resaltar una población
sc.pl.umap(adata, color="cell_type", groups=["CD14 Mono", "FCGR3A Mono"], title="Monocytes")
# Where do cells concentrate? || ¿Dónde se concentran las células?
sc.tl.embedding_density(adata, basis="umap", groupby="cell_type")
sc.pl.embedding_density(adata, basis="umap", key="umap_density_cell_type",
                        group=["CD4 T", "B", "CD14 Mono"], ncols=3)"""
    ),
    md(
        """## 2. Expression across groups 🟢
| Plot | Best for |
|---|---|
| **Violin / stacked violin** | Full distribution of a few genes |
| **Dot plot** | Many genes × groups: % expressing + mean |
| **Matrix plot** | Mean expression only, compact |
| **Heatmap / tracks plot** | Individual cells, shows heterogeneity within a group |""",
        """## 2. Expresión entre grupos 🟢
| Gráfico | Ideal para |
|---|---|
| **Violin / stacked violin** | Distribución completa de pocos genes |
| **Dot plot** | Muchos genes × grupos: % que expresa + media |
| **Matrix plot** | Solo expresión media, compacto |
| **Heatmap / tracks plot** | Células individuales, muestra heterogeneidad dentro de un grupo |""",
    ),
    code("""sc.pl.violin(adata, ["LYZ", "CD79A", "NKG7"], groupby="cell_type", rotation=60, use_raw=True)"""),
    code("""sc.pl.stacked_violin(adata, markers, groupby="cell_type", swap_axes=False, dendrogram=False, use_raw=True)"""),
    code(
        """sc.pl.dotplot(adata, markers, groupby="cell_type", standard_scale="var", use_raw=True,
              save="_pbmc_markers.pdf")   # saved in WORKDIR/figures/ || guardado en WORKDIR/figures/"""
    ),
    code("""sc.pl.matrixplot(adata, markers, groupby="cell_type", standard_scale="var", cmap="Blues", use_raw=True)"""),
    code("""sc.pl.heatmap(adata, markers, groupby="cell_type", standard_scale="var", cmap="viridis",
              use_raw=True, swap_axes=True, figsize=(10, 6))"""),
    code("""sc.pl.tracksplot(adata, markers, groupby="cell_type", use_raw=True)"""),
    md(
        """## 3. Cell type proportions 🟢
With one sample we can only describe composition. To **compare** proportions between conditions you need several
biological replicates per condition (notebook 05).""",
        """## 3. Proporciones de tipos celulares 🟢
Con una sola muestra solo podemos describir la composición. Para **comparar** proporciones entre condiciones se
necesitan varias réplicas biológicas por condición (notebook 05).""",
    ),
    code(
        """props = adata.obs["cell_type"].value_counts(normalize=True).reindex(adata.obs["cell_type"].cat.categories)
colors = dict(zip(adata.obs["cell_type"].cat.categories, adata.uns["cell_type_colors"])) \\
    if "cell_type_colors" in adata.uns else None
fig, axes = plt.subplots(1, 2, figsize=(11, 3.5), gridspec_kw={"width_ratios": [3, 1]})
props.mul(100).plot.bar(ax=axes[0], color=[colors[c] for c in props.index] if colors else None)
axes[0].set(ylabel="% of cells", xlabel="")
bottom = 0
for ct, p in props.items():
    axes[1].bar(0, p * 100, bottom=bottom, color=colors[ct] if colors else None, label=ct)
    bottom += p * 100
axes[1].set(xticks=[], ylabel="% of cells", title="PBMC 3k")
axes[1].legend(bbox_to_anchor=(1, 1), frameon=False, fontsize=8)
plt.tight_layout()"""
    ),
    md(
        """## 4. Differentially expressed genes between cell types 🟢
We test each cell type against all other cells. `pts=True` also reports the fraction of cells expressing each gene,
which helps you pick **specific** markers (high in the group, low elsewhere).""",
        """## 4. Genes diferencialmente expresados entre tipos celulares 🟢
Probamos cada tipo celular contra todas las demás células. `pts=True` también reporta la fracción de células que
expresan cada gen, lo que ayuda a elegir marcadores **específicos** (alto en el grupo, bajo en el resto).""",
    ),
    code(
        """sc.tl.rank_genes_groups(adata, groupby="cell_type", method="wilcoxon", pts=True)
sc.pl.rank_genes_groups(adata, n_genes=15, ncols=4, sharey=False, fontsize=8)"""
    ),
    code(
        """deg = sc.get.rank_genes_groups_df(adata, group="CD14 Mono")
deg_sig = deg.query("pvals_adj < 0.05 and abs(logfoldchanges) > 1")
print(f"{len(deg_sig)} significant genes ({(deg_sig.logfoldchanges > 0).sum()} up, {(deg_sig.logfoldchanges < 0).sum()} down)")
deg_sig.head(10)"""
    ),
    code(
        """def volcano(df, title, lfc=1, padj=0.05, n_label=10):
    d = df.copy()
    d["nlp"] = -np.log10(d["pvals_adj"].clip(lower=1e-300))
    sig = (d["pvals_adj"] < padj) & (d["logfoldchanges"].abs() > lfc)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.scatter(d.loc[~sig, "logfoldchanges"], d.loc[~sig, "nlp"], s=4, c="lightgray")
    ax.scatter(d.loc[sig, "logfoldchanges"], d.loc[sig, "nlp"], s=6,
               c=np.where(d.loc[sig, "logfoldchanges"] > 0, "#d62728", "#1f77b4"))
    for _, r in d[sig].sort_values("nlp", ascending=False).head(n_label).iterrows():
        ax.annotate(r["names"], (r["logfoldchanges"], r["nlp"]), fontsize=8)
    ax.axvline(lfc, ls="--", c="k", lw=0.5); ax.axvline(-lfc, ls="--", c="k", lw=0.5)
    ax.axhline(-np.log10(padj), ls="--", c="k", lw=0.5)
    ax.set(xlabel="log2 fold change", ylabel="-log10 adjusted p-value", title=title)

volcano(deg, "CD14 monocytes vs. all other cells")"""
    ),
    code(
        """# Keep only specific markers: expressed in >50% of the group and <20% of the rest || Solo marcadores específicos: >50% del grupo y <20% del resto
sc.tl.filter_rank_genes_groups(adata, min_in_group_fraction=0.5, max_out_group_fraction=0.2,
                               min_fold_change=1, key_added="rank_genes_filtered")
sc.pl.rank_genes_groups_dotplot(adata, key="rank_genes_filtered", n_genes=4, standard_scale="var")"""
    ),
    md(
        """⚠️ **Cluster markers ≠ differential expression between conditions.** The Wilcoxon test treats every cell as an
independent replicate. Cells from the same person are not independent, so p-values become tiny and false positives
explode when you compare, e.g., patients vs. controls. For conditions, sum the counts per sample and cell type
(**pseudobulk**) and use bulk RNA-seq tools (DESeq2, edgeR). We do exactly that in notebook 05.""",
        """⚠️ **Marcadores de clúster ≠ expresión diferencial entre condiciones.** La prueba de Wilcoxon trata cada célula
como una réplica independiente. Las células de una misma persona no son independientes, así que los p-valores se
vuelven diminutos y los falsos positivos se disparan al comparar, por ejemplo, pacientes vs. controles. Para condiciones,
suma los conteos por muestra y tipo celular (**pseudobulk**) y usa herramientas de RNA-seq bulk (DESeq2, edgeR). Eso
hacemos en el notebook 05.""",
    ),
    md(
        """## 5. Downstream: what do the DEGs mean? 🟢
### 5.1 Over-representation analysis (ORA) with MSigDB Hallmark
Are the top markers of each cell type enriched in known biological processes? ORA is a Fisher's exact test between
your gene list and each gene set. We use the 50 **Hallmark** gene sets from MSigDB (via OmniPath).""",
        """## 5. Análisis posteriores: ¿qué significan los DEGs? 🟢
### 5.1 Análisis de sobrerrepresentación (ORA) con MSigDB Hallmark
¿Los principales marcadores de cada tipo celular están enriquecidos en procesos biológicos conocidos? ORA es una prueba
exacta de Fisher entre tu lista de genes y cada conjunto de genes. Usamos los 50 conjuntos **Hallmark** de MSigDB (vía OmniPath).""",
    ),
    code(
        """hallmark = tut.cached_table("hallmark_human", lambda: dc.op.hallmark(organism="human"), WORKDIR)
print(hallmark["source"].nunique(), "gene sets")

all_deg = sc.get.rank_genes_groups_df(adata, group=None)
# cell types x genes matrix of positive log fold changes || matriz tipos celulares x genes con log fold changes positivos
lfc = (all_deg.query("pvals_adj < 0.05").pivot_table(index="group", columns="names",
       values="logfoldchanges", observed=True).fillna(0).clip(lower=0))
ora_es, ora_p = dc.mt.ora(lfc, net=hallmark, n_up=100, tmin=5)
top_sets = (-np.log10(ora_p.clip(lower=1e-30))).max().sort_values(ascending=False).head(12).index
fig, ax = plt.subplots(figsize=(7, 0.35 * len(top_sets) + 1.5))
sns.heatmap((-np.log10(ora_p[top_sets].clip(lower=1e-30))).T.rename(index=lambda x: x.replace("HALLMARK_", "")),
            cmap="Reds", ax=ax, cbar_kws={"label": "-log10 adj. p"})
ax.set(xlabel="", ylabel="", title="Hallmark ORA on cell type markers")
plt.show()"""
    ),
    md(
        """### 5.2 Pathway activity per cell with PROGENy
**PROGENy** provides "footprints": genes that change when a signaling pathway (JAK-STAT, NF-κB, TNF-α, TGF-β...) is
activated. With a ULM we estimate an activity score for every cell. Unlike ORA, it uses the **direction and weight**
of each target gene.""",
        """### 5.2 Actividad de vías por célula con PROGENy
**PROGENy** proporciona "huellas": genes que cambian cuando se activa una vía de señalización (JAK-STAT, NF-κB, TNF-α,
TGF-β...). Con un ULM estimamos un puntaje de actividad para cada célula. A diferencia de ORA, usa la **dirección y el
peso** de cada gen blanco.""",
    ),
    code(
        """progeny = tut.cached_table("progeny_human", lambda: dc.op.progeny(organism="human", top=500), WORKDIR)
dc.mt.ulm(adata, net=progeny, raw=True)
pathway_acts = dc.pp.get_obsm(adata, "score_ulm")
sc.pl.matrixplot(pathway_acts, var_names=pathway_acts.var_names, groupby="cell_type",
                 cmap="RdBu_r", vcenter=0, colorbar_title="mean activity")"""
    ),
    code("""sc.pl.umap(pathway_acts, color=[p for p in ["JAK-STAT", "NFkB", "TNFa"] if p in pathway_acts.var_names],
           cmap="RdBu_r", vcenter=0, ncols=3)"""),
    md(
        """### 5.3 🔎 Extra: scoring your own gene signature
Any gene list (e.g. from a paper) can be scored with `sc.tl.score_genes`: the mean expression of the list minus the
mean of a random set of genes with similar expression. Here, an interferon-stimulated gene signature, which will be
much higher in the IFN-β-treated cells of notebook 05.""",
        """### 5.3 🔎 Extra: puntuar tu propia firma génica
Cualquier lista de genes (por ejemplo, de un artículo) se puede puntuar con `sc.tl.score_genes`: la expresión media de
la lista menos la media de un conjunto aleatorio de genes con expresión similar. Aquí, una firma de genes estimulados
por interferón, que será mucho más alta en las células tratadas con IFN-β del notebook 05.""",
    ),
    code(
        """isg = ["ISG15", "IFI6", "IFIT1", "IFIT3", "MX1", "OAS1", "LY6E", "IFITM1", "IRF7", "STAT1"]
sc.tl.score_genes(adata, [g for g in isg if g in adata.raw.var_names], score_name="ISG_score", use_raw=True)
sc.pl.violin(adata, "ISG_score", groupby="cell_type", rotation=60, stripplot=False)"""
    ),
    exercise(
        """Repeat the DEG analysis comparing **CD14 Mono** directly against **FCGR3A Mono** (instead of against all cells)
and draw the volcano plot. *Hint:* `sc.tl.rank_genes_groups(..., groups=["CD14 Mono"], reference="FCGR3A Mono", key_added="mono")`
and `sc.get.rank_genes_groups_df(adata, group="CD14 Mono", key="mono")`.""",
        """Repite el análisis de DEGs comparando **CD14 Mono** directamente contra **FCGR3A Mono** (en vez de contra todas
las células) y dibuja el volcano plot. *Pista:* `sc.tl.rank_genes_groups(..., groups=["CD14 Mono"], reference="FCGR3A Mono", key_added="mono")`
y `sc.get.rank_genes_groups_df(adata, group="CD14 Mono", key="mono")`.""",
        """sc.tl.rank_genes_groups(adata, groupby="cell_type", groups=["CD14 Mono"], reference="FCGR3A Mono",
                        method="wilcoxon", key_added="mono")
volcano(sc.get.rank_genes_groups_df(adata, group="CD14 Mono", key="mono"), "CD14 vs FCGR3A monocytes")""",
    ),
    md("""## 6. Save""", """## 6. Guardar"""),
    code("""for key in ["rank_genes_filtered", "mono"]:   # tables with empty values can't be saved to .h5ad || tablas con valores vacíos no se guardan en .h5ad
    adata.uns.pop(key, None)
adata.write_h5ad(f"{WORKDIR}/results/pbmc3k_final.h5ad")
print(os.listdir(f"{WORKDIR}/figures"))"""),
    wrapup(
        "Last step: several samples, two conditions, and how Python compares with R. Next: **05 · Integration, conditions and R vs Python**.",
        "Último paso: varias muestras, dos condiciones y cómo se compara Python con R. Siguiente: **05 · Integración, condiciones y R vs Python**.",
    ),
]
