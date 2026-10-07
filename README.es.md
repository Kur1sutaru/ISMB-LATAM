# De Células a Clústeres: Introducción al Análisis de Single-Cell RNA-seq en Python

**ISCB-LATAM SolBio SPBBC 2026 · Tutorial · Lima, Perú · Lunes 9 de noviembre de 2026 · 9:00–12:30**

🇬🇧 [English version](README.md)

**Instructora:** Dra. Cristal Villalba Silva, Investigadora Postdoctoral, Center for Pain Therapeutics and Addiction
Research, UT Health San Antonio, EE. UU. · [GitHub](https://github.com/Kur1sutaru) · [ORCID 0000-0003-0283-7982](https://orcid.org/0000-0003-0283-7982)

Un tutorial práctico de medio día, para principiantes, que te lleva desde una **matriz de conteos de Cell Ranger** hasta
**clústeres, tipos celulares anotados, genes diferencialmente expresados, vías e integración de condiciones**, todo en
**Google Colab** (no hay que instalar nada: basta un navegador y una cuenta de Google). Todo el material está disponible
en **inglés y español**.

---

## Inicio rápido

1. Abre el primer notebook en Colab: **[Español](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/00_setup_and_cellranger.ipynb)** · **[English](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/00_setup_and_cellranger.ipynb)**
2. Inicia sesión con tu cuenta de Google y haz clic en *Copiar en Drive* (para guardar tus cambios).
3. Ejecuta las celdas en orden con `Shift + Enter`.

Instrucciones detalladas, incluida la instalación local: **[SETUP.md](SETUP.md#español)**.

## Programa y materiales

★ = bloque práctico (~65 % del tiempo)

| Hora | Sesión | Español | English |
|---|---|---|---|
| 9:00–9:20 | Bienvenida e introducción: tecnologías single-cell, 10x Genomics, Cell Ranger, flujo de análisis | [diapositivas](slides/es/) | [slides](slides/en/) |
| 9:20–9:40 ★ | **00** · Configuración, salidas de Cell Ranger y el objeto AnnData | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/00_setup_and_cellranger.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/00_setup_and_cellranger.ipynb) |
| 9:40–10:15 ★ | **01** · Control de calidad, dobletes, normalización, genes altamente variables | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/01_quality_control_preprocessing.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/01_quality_control_preprocessing.ipynb) |
| 10:15–10:45 ★ | **02** · PCA, grafo de vecinos, UMAP, clustering con Leiden | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/02_dimensionality_reduction_clustering.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/02_dimensionality_reduction_clustering.ipynb) |
| 10:45–11:00 | ☕ Pausa para café | | |
| 11:00–11:35 ★ | **03** · Anotación de tipos celulares: marcadores, PanglaoDB, CellTypist, mapeo a referencia; CELLxGENE, Single Cell Portal, CAP | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/03_cell_type_annotation.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/03_cell_type_annotation.ipynb) |
| 11:35–12:05 ★ | **04** · Visualización (UMAP, violin, dot plot, heatmap, proporciones), DEGs, enriquecimiento y actividad de vías | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/04_visualization_deg_downstream.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/04_visualization_deg_downstream.ipynb) |
| 12:05–12:25 ★ | **05** · Integración (Harmony, BBKNN), proporciones y DE pseudobulk entre condiciones, R vs. Python *(demostración en vivo + estudio individual)* | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/05_integration_conditions_r_vs_python.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/05_integration_conditions_r_vs_python.ipynb) |
| 12:25–12:30 | Cierre, recursos, preguntas | | |

Cada notebook marca las secciones 🟢 **Core** (se ven en vivo) y 🔎 **Extra** (para estudiar después), e incluye
ejercicios con soluciones ocultas.

## Objetivos de aprendizaje

Al final del tutorial, los participantes podrán:

1. Explicar cómo los datos de gotas de 10x Genomics se convierten en una matriz de conteos con Cell Ranger, y qué archivos usar.
2. Cargar y navegar datos de single-cell con `AnnData` y Scanpy.
3. Realizar y justificar el control de calidad: filtrar células de baja calidad y dobletes.
4. Normalizar datos, seleccionar genes altamente variables y reducir la dimensionalidad (PCA, UMAP).
5. Agrupar células con el algoritmo de Leiden y evaluar el efecto de la resolución.
6. Anotar tipos celulares combinando genes marcadores, bases de datos (PanglaoDB), clasificadores (CellTypist) y atlas de
   referencia (CZ CELLxGENE, Single Cell Portal, Cell Annotation Platform).
7. Visualizar resultados y encontrar genes diferencialmente expresados, e interpretarlos con análisis de enriquecimiento y vías.
8. Integrar muestras, comparar condiciones con expresión diferencial pseudobulk y relacionar el flujo con R/Seurat.

## Público y requisitos

**Nivel: principiante.** Estudiantes de posgrado, posdoctorandos e investigadores de biología, medicina y bioinformática
que tienen (o pronto tendrán) datos de single-cell.
- **Necesario:** Python básico (variables, listas, funciones, importar librerías) o experiencia equivalente en R;
  biología molecular básica (genes, mRNA, tipos celulares).
- **No necesario:** experiencia previa en single-cell o aprendizaje automático.
- **Trae:** una laptop con un navegador moderno, acceso a internet y una cuenta (gratuita) de Google.

## Conjuntos de datos

Todos son públicos y los notebooks los descargan automáticamente.

| Conjunto | Notebooks | Fuente · Licencia |
|---|---|---|
| **PBMC 3k**: 2.700 PBMCs de un donante sano, salida de Cell Ranger 1.1.0 | 00–04 | [10x Genomics](https://www.10xgenomics.com/datasets) · CC BY 4.0 |
| **pbmc68k_reduced**: referencia anotada de PBMC (incluida en Scanpy) | 03 | Zheng *et al.*, *Nat Commun* 2017 |
| **Kang 2018**: PBMCs de 8 pacientes con lupus, control vs. IFN-β | 05 | Kang *et al.*, *Nat Biotechnol* 2018 · GEO [GSE96583](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE96583) |
| Marcadores de PanglaoDB, MSigDB Hallmark, PROGENy | 03–05 | vía [OmniPath](https://omnipathdb.org) |
| Modelo `Immune_All_Low` de CellTypist | 03 | Domínguez Conde *et al.*, *Science* 2022 |

## Licencia

- Código (notebooks, scripts): [MIT](LICENSE)
- Textos, diapositivas y figuras: [CC BY 4.0](LICENSE-CC-BY-4.0.md)
- Los conjuntos de datos conservan sus licencias originales.

## Cómo citar

> Villalba Silva, G. C. (2026). *From Cells to Clusters: An Introduction to Single-Cell RNA-seq Analysis in Python*.
> Tutorial, ISCB-LATAM SolBio SPBBC 2026, Lima, Perú. https://github.com/Kur1sutaru/ISMB-LATAM
