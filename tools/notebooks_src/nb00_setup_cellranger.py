from build_notebooks import code, exercise, md
from notebooks_src.common import setup, wrapup

META = dict(
    file="00_setup_and_cellranger.ipynb",
    title=("00 · Setup, Cell Ranger outputs and the AnnData object",
           "00 · Configuración, salidas de Cell Ranger y el objeto AnnData"),
    time="9:20–9:40 (20 min)",
    goals=(
        ["Run code in Google Colab",
         "Explain what Cell Ranger does, from FASTQ files to a count matrix",
         "Recognize the files in a Cell Ranger `outs/` folder and which ones you need",
         "Load a count matrix into Python and navigate an `AnnData` object"],
        ["Ejecutar código en Google Colab",
         "Explicar qué hace Cell Ranger, desde los archivos FASTQ hasta la matriz de conteos",
         "Reconocer los archivos de la carpeta `outs/` de Cell Ranger y cuáles necesitas",
         "Cargar una matriz de conteos en Python y navegar un objeto `AnnData`"],
    ),
)

CELLS = [
    md(
        """## How to use Google Colab
- Each grey box is a **code cell**. Click it and press `Shift + Enter` to run it.
- Cells run **in order**. If something breaks, use *Runtime → Restart session and run all*.
- Free Colab gives you a CPU machine with ~12 GB RAM. That is enough for this tutorial; no GPU needed.
- Colab machines are temporary: files disappear when the session ends (unless you use Google Drive).""",
        """## Cómo usar Google Colab
- Cada caja gris es una **celda de código**. Haz clic en ella y presiona `Shift + Enter` para ejecutarla.
- Las celdas se ejecutan **en orden**. Si algo falla, usa *Entorno de ejecución → Reiniciar sesión y ejecutar todo*.
- Colab gratuito te da una máquina con CPU y ~12 GB de RAM. Es suficiente para este tutorial; no se necesita GPU.
- Las máquinas de Colab son temporales: los archivos desaparecen al terminar la sesión (salvo que uses Google Drive).""",
    ),
    setup("base"),
    md(
        """## 1. From the sequencer to a count matrix: Cell Ranger 🟢

A 10x Genomics experiment gives you **FASTQ files**. Each read pair carries:
- **Read 1**: the **cell barcode** (which droplet/cell, 16 bp) + the **UMI** (which original molecule, 10–12 bp);
- **Read 2**: the cDNA sequence (which gene).

**Cell Ranger** (`cellranger count`) turns those reads into a **cells × genes count matrix**:

1. **Align** Read 2 to the reference genome/transcriptome (STAR inside Cell Ranger).
2. **Correct barcodes** against the whitelist of valid 10x barcodes.
3. **Count UMIs**: reads with the same barcode + UMI + gene are PCR copies of one molecule → counted once.
4. **Call cells**: separate droplets that contain a cell from empty droplets (only ambient RNA).

You do not run Cell Ranger in Colab (it needs a Linux server with ~64 GB RAM). A typical command is:

```bash
cellranger count --id=sample1 \\
    --transcriptome=refdata-gex-GRCh38-2024-A \\
    --fastqs=/path/to/fastqs --sample=sample1 \\
    --create-bam=true --localcores=16 --localmem=64
```

Open-source alternatives that produce the same kind of matrix: **STARsolo**, **alevin-fry / simpleaf**,
**kallisto | bustools**. They are often faster and are free to run anywhere.""",
        """## 1. Del secuenciador a la matriz de conteos: Cell Ranger 🟢

Un experimento de 10x Genomics te entrega **archivos FASTQ**. Cada par de lecturas contiene:
- **Read 1**: el **código de barras celular** (qué gota/célula, 16 pb) + el **UMI** (qué molécula original, 10–12 pb);
- **Read 2**: la secuencia de cDNA (qué gen).

**Cell Ranger** (`cellranger count`) convierte esas lecturas en una **matriz de conteos células × genes**:

1. **Alinea** el Read 2 al genoma/transcriptoma de referencia (usa STAR internamente).
2. **Corrige los códigos de barras** con la lista de códigos válidos de 10x.
3. **Cuenta UMIs**: lecturas con el mismo código + UMI + gen son copias de PCR de una molécula → se cuentan una vez.
4. **Identifica células**: separa las gotas que contienen una célula de las gotas vacías (solo RNA ambiental).

Cell Ranger no se ejecuta en Colab (necesita un servidor Linux con ~64 GB de RAM). Un comando típico es:

```bash
cellranger count --id=sample1 \\
    --transcriptome=refdata-gex-GRCh38-2024-A \\
    --fastqs=/ruta/a/fastqs --sample=sample1 \\
    --create-bam=true --localcores=16 --localmem=64
```

Alternativas de código abierto que producen el mismo tipo de matriz: **STARsolo**, **alevin-fry / simpleaf**,
**kallisto | bustools**. Suelen ser más rápidas y se pueden ejecutar en cualquier lugar.""",
    ),
    md(
        """### What is inside `outs/`?

| File | What it is | Do you need it? |
|---|---|---|
| `web_summary.html` | Interactive QC report | **Always open it first** |
| `metrics_summary.csv` | The same metrics as a table | Yes, to compare samples |
| `filtered_feature_bc_matrix/` (`barcodes.tsv.gz`, `features.tsv.gz`, `matrix.mtx.gz`) | Counts for **called cells** only | **Yes: this is what we analyze** |
| `filtered_feature_bc_matrix.h5` | Same matrix in a single HDF5 file | Yes (easiest to load) |
| `raw_feature_bc_matrix/` | Counts for **all** barcodes, including empty droplets | For ambient RNA removal (SoupX, CellBender) |
| `possorted_genome_bam.bam` | Aligned reads | Rarely (RNA velocity, genotyping) |
| `molecule_info.h5` | Per-molecule info | To aggregate/downsample samples |
| `cloupe.cloupe` | File for the Loupe Browser app | Quick visual exploration |

**Metrics to check in `web_summary.html`:** estimated number of cells, median genes per cell,
fraction of reads in cells (> 70 %), reads mapped confidently to the transcriptome (> 60 %),
sequencing saturation, and the shape of the **barcode rank ("knee") plot**.""",
        """### ¿Qué hay dentro de `outs/`?

| Archivo | Qué es | ¿Lo necesitas? |
|---|---|---|
| `web_summary.html` | Reporte interactivo de control de calidad | **Ábrelo siempre primero** |
| `metrics_summary.csv` | Las mismas métricas en una tabla | Sí, para comparar muestras |
| `filtered_feature_bc_matrix/` (`barcodes.tsv.gz`, `features.tsv.gz`, `matrix.mtx.gz`) | Conteos solo de las **células identificadas** | **Sí: es lo que analizamos** |
| `filtered_feature_bc_matrix.h5` | La misma matriz en un solo archivo HDF5 | Sí (lo más fácil de cargar) |
| `raw_feature_bc_matrix/` | Conteos de **todos** los códigos, incluidas las gotas vacías | Para eliminar RNA ambiental (SoupX, CellBender) |
| `possorted_genome_bam.bam` | Lecturas alineadas | Rara vez (velocidad de RNA, genotipado) |
| `molecule_info.h5` | Información por molécula | Para agregar/submuestrear muestras |
| `cloupe.cloupe` | Archivo para la aplicación Loupe Browser | Exploración visual rápida |

**Métricas a revisar en `web_summary.html`:** número estimado de células, mediana de genes por célula,
fracción de lecturas en células (> 70 %), lecturas mapeadas con confianza al transcriptoma (> 60 %),
saturación de secuenciación y la forma del **gráfico de rango de códigos de barras ("rodilla")**.""",
    ),
    md(
        """## 2. Download a real Cell Ranger output 🟢
We use **PBMC 3k**: ~2,700 peripheral blood mononuclear cells from a healthy donor, sequenced by 10x Genomics
(public, CC BY 4.0). It is the "hello world" of single-cell analysis, so you can compare your results
with the Scanpy and Seurat tutorials. This dataset was made with an old Cell Ranger version, so the files
are called `genes.tsv` instead of `features.tsv.gz`, but the structure is the same.""",
        """## 2. Descargar una salida real de Cell Ranger 🟢
Usamos **PBMC 3k**: ~2.700 células mononucleares de sangre periférica de un donante sano, secuenciadas por 10x
Genomics (públicas, CC BY 4.0). Es el "hola mundo" del análisis de single-cell, así que puedes comparar tus
resultados con los tutoriales de Scanpy y Seurat. Este conjunto se generó con una versión antigua de Cell
Ranger, por eso los archivos se llaman `genes.tsv` en vez de `features.tsv.gz`, pero la estructura es la misma.""",
    ),
    code(
        """import tarfile
from pathlib import Path

data_dir = Path(WORKDIR) / "data"
tar_path = tut.download(tut.URLS["pbmc3k"], data_dir / "pbmc3k_filtered_gene_bc_matrices.tar.gz")
with tarfile.open(tar_path) as fh:
    fh.extractall(data_dir)

mtx_dir = data_dir / "filtered_gene_bc_matrices" / "hg19"
for f in sorted(mtx_dir.iterdir()):
    print(f"{f.name:15s} {f.stat().st_size / 1e6:6.1f} MB")"""
    ),
    md(
        """Let's peek at the three files. `barcodes.tsv` = one cell per line; `genes.tsv` = Ensembl ID + gene symbol;
`matrix.mtx` = a **sparse** matrix stored as *(gene, cell, count)* triplets, because >90 % of the values are zero.""",
        """Veamos los tres archivos. `barcodes.tsv` = una célula por línea; `genes.tsv` = ID de Ensembl + símbolo del gen;
`matrix.mtx` = una matriz **dispersa** guardada como tripletes *(gen, célula, conteo)*, porque >90 % de los valores son cero.""",
    ),
    code(
        """for name in ["barcodes.tsv", "genes.tsv", "matrix.mtx"]:
    print(f"--- {name} ---")
    with open(mtx_dir / name) as fh:
        for _ in range(4):
            print(fh.readline().rstrip())"""
    ),
    md(
        """## 3. Load the matrix into an `AnnData` object 🟢
`sc.read_10x_mtx()` reads the folder. For newer Cell Ranger outputs you can also use
`sc.read_10x_h5("filtered_feature_bc_matrix.h5")`.""",
        """## 3. Cargar la matriz en un objeto `AnnData` 🟢
`sc.read_10x_mtx()` lee la carpeta. Para salidas recientes de Cell Ranger también puedes usar
`sc.read_10x_h5("filtered_feature_bc_matrix.h5")`.""",
    ),
    code(
        """adata = sc.read_10x_mtx(mtx_dir, var_names="gene_symbols", cache=False)
adata.var_names_make_unique()  # a few gene symbols are duplicated || algunos símbolos de genes están duplicados
adata"""
    ),
    md(
        """### The anatomy of `AnnData`

```
                 var  (genes: gene_ids, highly_variable, ...)
              ┌───────────────────────────┐
  obs         │                           │   obsm: X_pca, X_umap (one row per cell)
 (cells:      │   X  (cells × genes)      │   layers: counts, ... (same shape as X)
  n_genes,    │                           │   uns: anything else (colors, parameters)
  cluster...) │                           │   obsp: cell–cell graphs (neighbors)
              └───────────────────────────┘
```
- `adata.X` → the matrix (here raw UMI counts, sparse)
- `adata.obs` → a pandas DataFrame with one row **per cell** (QC metrics, clusters, cell types...)
- `adata.var` → a pandas DataFrame with one row **per gene**
- `adata.obsm`, `adata.layers`, `adata.uns`, `adata.obsp` → embeddings, alternative matrices, metadata, graphs

The R equivalent is a **Seurat** or **SingleCellExperiment** object. We compare them in notebook 05.""",
        """### La anatomía de `AnnData`

```
                 var  (genes: gene_ids, highly_variable, ...)
              ┌───────────────────────────┐
  obs         │                           │   obsm: X_pca, X_umap (una fila por célula)
 (células:    │   X  (células × genes)    │   layers: counts, ... (misma forma que X)
  n_genes,    │                           │   uns: todo lo demás (colores, parámetros)
  cluster...) │                           │   obsp: grafos célula–célula (vecinos)
              └───────────────────────────┘
```
- `adata.X` → la matriz (aquí conteos crudos de UMIs, dispersa)
- `adata.obs` → un DataFrame de pandas con una fila **por célula** (métricas de calidad, clústeres, tipos celulares...)
- `adata.var` → un DataFrame de pandas con una fila **por gen**
- `adata.obsm`, `adata.layers`, `adata.uns`, `adata.obsp` → embeddings, matrices alternativas, metadatos, grafos

El equivalente en R es un objeto **Seurat** o **SingleCellExperiment**. Los comparamos en el notebook 05.""",
    ),
    code(
        """print("cells x genes:", adata.shape)
print("first barcodes:", adata.obs_names[:3].tolist())
print("first genes:   ", adata.var_names[:3].tolist())
print("matrix type:   ", type(adata.X).__name__)
sparsity = 1 - adata.X.nnz / (adata.n_obs * adata.n_vars)
print(f"zeros in the matrix: {sparsity:.1%}")
adata.var.head()"""
    ),
    md(
        """### Basic numbers per cell
Total UMIs per cell (**library size**) and number of detected genes are the first things to look at.""",
        """### Números básicos por célula
El total de UMIs por célula (**tamaño de biblioteca**) y el número de genes detectados son lo primero que miramos.""",
    ),
    code(
        """adata.obs["total_counts"] = np.asarray(adata.X.sum(axis=1)).ravel()
adata.obs["n_genes"] = np.asarray((adata.X > 0).sum(axis=1)).ravel()
adata.obs.describe().round(1)"""
    ),
    code(
        """fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
axes[0].hist(adata.obs["total_counts"], bins=60, color="#2a9d8f")
axes[0].set(xlabel="UMIs per cell", ylabel="cells")
axes[1].hist(adata.obs["n_genes"], bins=60, color="#e76f51")
axes[1].set(xlabel="genes per cell")
# Barcode rank ("knee") plot, like in web_summary.html || Gráfico de rango ("rodilla"), como en web_summary.html
ranked = np.sort(adata.obs["total_counts"].values)[::-1]
axes[2].loglog(np.arange(1, len(ranked) + 1), ranked, color="#264653")
axes[2].set(xlabel="barcode rank", ylabel="UMIs")
plt.tight_layout()"""
    ),
    md(
        """> The knee plot here only shows **called cells** (filtered matrix). In the `raw_feature_bc_matrix` you would
> also see the long tail of empty droplets after the knee.

### Which genes take most of the reads?""",
        """> Aquí el gráfico de rodilla solo muestra las **células identificadas** (matriz filtrada). En `raw_feature_bc_matrix`
> también verías la larga cola de gotas vacías después de la rodilla.

### ¿Qué genes se llevan la mayoría de las lecturas?""",
    ),
    code("""sc.pl.highest_expr_genes(adata, n_top=20)"""),
    md(
        """Mitochondrial (`MT-`), ribosomal (`RPS`/`RPL`) and very abundant genes like `MALAT1` dominate.
This is normal, and it is why we need quality control and normalization (next notebook).""",
        """Dominan los genes mitocondriales (`MT-`), ribosomales (`RPS`/`RPL`) y genes muy abundantes como `MALAT1`.
Es normal, y por eso necesitamos control de calidad y normalización (siguiente notebook).""",
    ),
    exercise(
        """1. How many UMIs does the **first** cell have? 2. Which gene has the highest **total** count across all cells?
*Hint:* `adata.X.sum(axis=0)` sums over cells.""",
        """1. ¿Cuántos UMIs tiene la **primera** célula? 2. ¿Qué gen tiene el mayor conteo **total** sumando todas las células?
*Pista:* `adata.X.sum(axis=0)` suma sobre las células.""",
        """print(adata.obs["total_counts"].iloc[0])
gene_totals = np.asarray(adata.X.sum(axis=0)).ravel()
print(adata.var_names[gene_totals.argmax()])""",
    ),
    md(
        """## 4. 🔎 Extra: the same in R (Seurat)
```r
library(Seurat)
counts <- Read10X("filtered_gene_bc_matrices/hg19/")   # or Read10X_h5("filtered_feature_bc_matrix.h5")
pbmc <- CreateSeuratObject(counts, project = "pbmc3k", min.cells = 3, min.features = 200)
pbmc
```
Converting between ecosystems: save `adata.write_h5ad("pbmc.h5ad")` and read it in R with
`zellkonverter::readH5AD()` (SingleCellExperiment) or `schard::h5ad2seurat()`.""",
        """## 4. 🔎 Extra: lo mismo en R (Seurat)
```r
library(Seurat)
counts <- Read10X("filtered_gene_bc_matrices/hg19/")   # o Read10X_h5("filtered_feature_bc_matrix.h5")
pbmc <- CreateSeuratObject(counts, project = "pbmc3k", min.cells = 3, min.features = 200)
pbmc
```
Para convertir entre ecosistemas: guarda `adata.write_h5ad("pbmc.h5ad")` y léelo en R con
`zellkonverter::readH5AD()` (SingleCellExperiment) o `schard::h5ad2seurat()`.""",
    ),
    md(
        """## 5. 🔎 Extra: analyzing your own data
Upload your `filtered_feature_bc_matrix.h5` (folder icon on the left → upload) or copy it to Google Drive, then:
```python
adata = sc.read_10x_h5("filtered_feature_bc_matrix.h5")
adata.var_names_make_unique()
```
For several samples, read each one, add `adata.obs["sample"] = "name"` and join them with
`anndata.concat([...], label="sample")`.""",
        """## 5. 🔎 Extra: analizar tus propios datos
Sube tu `filtered_feature_bc_matrix.h5` (ícono de carpeta a la izquierda → subir) o cópialo a Google Drive, y luego:
```python
adata = sc.read_10x_h5("filtered_feature_bc_matrix.h5")
adata.var_names_make_unique()
```
Para varias muestras, lee cada una, agrega `adata.obs["sample"] = "nombre"` y únelas con
`anndata.concat([...], label="sample")`.""",
    ),
    wrapup(
        "You know where the count matrix comes from and how it lives in Python. Next: **01 · Quality control and preprocessing**.",
        "Ya sabes de dónde viene la matriz de conteos y cómo vive en Python. Siguiente: **01 · Control de calidad y preprocesamiento**.",
    ),
]
