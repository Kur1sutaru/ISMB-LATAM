from build_notebooks import code, exercise, md
from notebooks_src.common import setup, wrapup

META = dict(
    file="02_dimensionality_reduction_clustering.ipynb",
    title=("02 · Dimensionality reduction and clustering", "02 · Reducción de dimensionalidad y clustering"),
    time="10:15–10:45 (30 min)",
    goals=(
        ["Run PCA and choose how many principal components to keep",
         "Build a k-nearest-neighbor graph and a UMAP embedding (and know what UMAP does *not* tell you)",
         "Cluster cells with the Leiden algorithm and explore the effect of resolution",
         "Check clusters for technical artifacts"],
        ["Ejecutar PCA y decidir cuántos componentes principales conservar",
         "Construir un grafo de k vecinos más cercanos y un embedding UMAP (y saber lo que UMAP *no* te dice)",
         "Agrupar células con el algoritmo de Leiden y explorar el efecto de la resolución",
         "Revisar los clústeres en busca de artefactos técnicos"],
    ),
)

CELLS = [
    setup("base"),
    md(
        """## 1. Load the QC'd data 🟢
`tut.get_checkpoint("qc")` loads the file saved at the end of notebook 01. If it is not there (new Colab session),
it rebuilds it from the raw data with the same parameters.""",
        """## 1. Cargar los datos con QC 🟢
`tut.get_checkpoint("qc")` carga el archivo guardado al final del notebook 01. Si no existe (nueva sesión de Colab),
lo reconstruye desde los datos crudos con los mismos parámetros.""",
    ),
    code("""adata = tut.get_checkpoint("qc", WORKDIR)
adata"""),
    md(
        """## 2. PCA: from 2,000 genes to ~30 axes 🟢
Genes are correlated (a T cell expresses *CD3D*, *CD3E*, *IL7R* together), so a few **principal components**
capture most of the biological signal. Downstream steps use the PCs instead of genes: faster and less noisy.

> 🔎 Many tutorials scale each gene to unit variance (`sc.pp.scale`) before PCA. Current best practice
> (sc-best-practices.org) often skips it; both work for PBMCs.""",
        """## 2. PCA: de 2.000 genes a ~30 ejes 🟢
Los genes están correlacionados (una célula T expresa *CD3D*, *CD3E*, *IL7R* juntos), así que unos pocos
**componentes principales** capturan la mayor parte de la señal biológica. Los pasos siguientes usan los PCs en vez
de los genes: más rápido y con menos ruido.

> 🔎 Muchos tutoriales escalan cada gen a varianza unitaria (`sc.pp.scale`) antes del PCA. Las buenas prácticas
> actuales (sc-best-practices.org) a menudo lo omiten; ambas opciones funcionan para PBMCs.""",
    ),
    code(
        """sc.tl.pca(adata, n_comps=50, mask_var="highly_variable", random_state=0)
sc.pl.pca_variance_ratio(adata, n_pcs=50, log=True)"""
    ),
    md(
        """**Elbow plot:** after the "elbow" each extra PC adds little. For PBMC 3k it is around PC 10–15; keeping
a few more (we use **30**) is safe, while keeping too few can merge rare populations.""",
        """**Gráfico de codo:** después del "codo" cada PC extra aporta poco. Para PBMC 3k está alrededor del PC 10–15;
conservar algunos más (usamos **30**) es seguro, mientras que conservar muy pocos puede fusionar poblaciones raras.""",
    ),
    code("""sc.pl.pca(adata, color=["CST3", "NKG7", "MS4A1", "pct_counts_mt"], ncols=4, use_raw=True)"""),
    md(
        """PC1 already separates myeloid cells (*CST3*) from lymphocytes, and % MT is not driving the main axes: good sign.

## 3. Neighbor graph and UMAP 🟢
1. **kNN graph:** each cell is connected to its 15 most similar cells in PCA space. Clustering and UMAP both use this graph.
2. **UMAP** draws that graph in 2D for visualization.

⚠️ UMAP preserves **local** neighborhoods. Distances **between** clusters and cluster **sizes** in a UMAP are not
reliable: never draw biological conclusions from them alone.""",
        """PC1 ya separa las células mieloides (*CST3*) de los linfocitos, y el % MT no domina los ejes principales: buena señal.

## 3. Grafo de vecinos y UMAP 🟢
1. **Grafo kNN:** cada célula se conecta con sus 15 células más parecidas en el espacio de PCA. El clustering y el UMAP usan este grafo.
2. **UMAP** dibuja ese grafo en 2D para visualizarlo.

⚠️ UMAP conserva los vecindarios **locales**. Las distancias **entre** clústeres y los **tamaños** de los clústeres en un UMAP
no son confiables: nunca saques conclusiones biológicas solo de ellos.""",
    ),
    code(
        """sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30, random_state=0)
sc.tl.umap(adata, random_state=0)
sc.pl.umap(adata, color=["total_counts", "n_genes_by_counts", "pct_counts_mt"], ncols=3)"""
    ),
    code(
        """sc.pl.umap(adata, color=["CD3E", "CD8A", "GNLY", "MS4A1", "CD14", "FCGR3A", "FCER1A", "PPBP"],
           ncols=4, use_raw=True, cmap="viridis")"""
    ),
    md(
        """## 4. Leiden clustering 🟢
Leiden finds groups of cells that are more connected to each other than to the rest of the graph.
The **resolution** controls how many clusters you get: higher = more, smaller clusters.
There is no single correct value; it depends on the biological question.""",
        """## 4. Clustering con Leiden 🟢
Leiden encuentra grupos de células más conectadas entre sí que con el resto del grafo.
La **resolución** controla cuántos clústeres obtienes: más alta = más clústeres, más pequeños.
No existe un único valor correcto; depende de la pregunta biológica.""",
    ),
    code(
        """for res in [0.3, 0.8, 1.5]:
    sc.tl.leiden(adata, resolution=res, key_added=f"leiden_{res}",
                 flavor="igraph", n_iterations=2, directed=False, random_state=0)
    print(f"resolution {res}: {adata.obs[f'leiden_{res}'].nunique()} clusters")

sc.pl.umap(adata, color=["leiden_0.3", "leiden_0.8", "leiden_1.5"], legend_loc="on data", ncols=3)"""
    ),
    md(
        """How do clusters split as resolution increases? A cross-table shows it (the R package **clustree** draws the same idea as a tree).""",
        """¿Cómo se dividen los clústeres al aumentar la resolución? Una tabla cruzada lo muestra (el paquete de R **clustree** dibuja la misma idea como un árbol).""",
    ),
    code("""pd.crosstab(adata.obs["leiden_0.3"], adata.obs["leiden_0.8"])"""),
    md(
        """We keep **resolution 0.8** as our main clustering (`adata.obs["leiden"]`).

## 5. Are any clusters technical artifacts? 🟢
A cluster defined only by low UMIs or high % MT is usually low-quality cells, not a cell type.""",
        """Nos quedamos con la **resolución 0,8** como clustering principal (`adata.obs["leiden"]`).

## 5. ¿Hay clústeres que sean artefactos técnicos? 🟢
Un clúster definido solo por pocos UMIs o alto % MT suele ser de células de baja calidad, no un tipo celular.""",
    ),
    code(
        """adata.obs["leiden"] = adata.obs["leiden_0.8"]
sc.pl.violin(adata, ["n_genes_by_counts", "pct_counts_mt", "doublet_score"], groupby="leiden",
             stripplot=False, multi_panel=True)
adata.obs["leiden"].value_counts().sort_index().to_frame("cells").T"""
    ),
    md(
        """## 6. 🔎 Extra: t-SNE and PAGA
t-SNE is an older alternative to UMAP. PAGA summarizes how clusters connect, useful for continuous processes
(differentiation) and as a better initialization for UMAP.""",
        """## 6. 🔎 Extra: t-SNE y PAGA
t-SNE es una alternativa más antigua a UMAP. PAGA resume cómo se conectan los clústeres, útil para procesos continuos
(diferenciación) y como mejor inicialización para UMAP.""",
    ),
    code(
        """sc.tl.tsne(adata, n_pcs=30, random_state=0)
sc.tl.paga(adata, groups="leiden")
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
sc.pl.tsne(adata, color="leiden", ax=axes[0], show=False, legend_loc="on data")
sc.pl.paga(adata, ax=axes[1], show=False, fontsize=9)
plt.tight_layout()"""
    ),
    md("""## 7. Save the checkpoint 🟢""", """## 7. Guardar el checkpoint 🟢"""),
    code("""adata.write_h5ad(f"{WORKDIR}/results/pbmc3k_clustered.h5ad")"""),
    exercise(
        """Recompute the neighbor graph with `n_neighbors=5` and with `n_neighbors=50`, run UMAP each time and compare
with the plot above (color by `leiden`). What changes? Do the clusters change?""",
        """Recalcula el grafo de vecinos con `n_neighbors=5` y con `n_neighbors=50`, ejecuta UMAP cada vez y compara con el
gráfico de arriba (colorea por `leiden`). ¿Qué cambia? ¿Cambian los clústeres?""",
        """for k in (5, 50):
    tmp = adata.copy()
    sc.pp.neighbors(tmp, n_neighbors=k, n_pcs=30, random_state=0)
    sc.tl.umap(tmp, random_state=0)
    sc.pl.umap(tmp, color="leiden", title=f"n_neighbors = {k}", legend_loc="on data")
# Small k: fragmented, local structure. Large k: smoother, more global structure. || k pequeño: estructura local, fragmentada. k grande: más suave, más global.
# Same colors = same clusters (computed before): UMAP is only a picture of the graph. || Mismos colores = mismos clústeres (calculados antes): UMAP es solo un dibujo del grafo.""",
    ),
    wrapup(
        "You have clusters. But what cell types are they? Next: **03 · Cell type annotation**.",
        "Ya tienes clústeres. Pero, ¿qué tipos celulares son? Siguiente: **03 · Anotación de tipos celulares**.",
    ),
]
