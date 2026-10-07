"""Cells shared by every notebook."""
from build_notebooks import code, md

PKGS = {
    "base": ['"scanpy[leiden,scrublet]>=1.10"'],
    "annotation": ['"scanpy[leiden,scrublet]>=1.10"', '"decoupler>=2.1,<3"', '"celltypist>=1.7"'],
    "downstream": ['"scanpy[leiden,scrublet]>=1.10"', '"decoupler>=2.1,<3"'],
    "integration": ['"scanpy[leiden,scrublet]>=1.10"', '"decoupler>=2.1,<3"', '"harmonypy>=0.0.10"',
                    '"bbknn>=1.6"', '"pydeseq2>=0.5"'],
}


def setup(pkgs="base", extra_imports=""):
    install = " ".join(PKGS[pkgs])
    return [
        md(
            """## 0. Setup 🟢
Run the cell below first (▶ or `Shift + Enter`). On Google Colab it installs the packages (~1 min);
on your own computer it assumes you already ran `pip install -r requirements.txt`.

**Optional:** set `USE_DRIVE = True` to save your results in Google Drive, so the next notebooks
can reuse them. If you leave it `False`, each notebook rebuilds what it needs automatically.""",
            """## 0. Configuración 🟢
Ejecuta primero la celda de abajo (▶ o `Shift + Enter`). En Google Colab instala los paquetes (~1 min);
en tu computadora asume que ya ejecutaste `pip install -r requirements.txt`.

**Opcional:** cambia `USE_DRIVE = True` para guardar tus resultados en Google Drive y reutilizarlos en
los siguientes notebooks. Si lo dejas en `False`, cada notebook reconstruye lo que necesita automáticamente.""",
        ),
        code(
            f"""import os, sys, urllib.request
IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    !pip install -q {install}

USE_DRIVE = False  # True = keep results in Google Drive || True = guardar resultados en Google Drive
WORKDIR = "sc_tutorial"
if IN_COLAB and USE_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")
    WORKDIR = "/content/drive/MyDrive/sc_tutorial"
os.makedirs(WORKDIR, exist_ok=True)

# Tutorial helper functions (download + checkpoints) || Funciones auxiliares del tutorial (descarga + checkpoints)
if os.path.exists("../../scripts/sc_tutorial.py"):          # running from a local clone || ejecutando desde un clon local
    sys.path.insert(0, os.path.abspath("../../scripts"))
elif not os.path.exists("sc_tutorial.py"):
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/Kur1sutaru/ISMB-LATAM/main/scripts/sc_tutorial.py", "sc_tutorial.py")
import sc_tutorial as tut

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scanpy as sc
{extra_imports}
sc.settings.verbosity = 1
sc.settings.set_figure_params(dpi=80, facecolor="white", frameon=False)
sc.settings.figdir = os.path.join(WORKDIR, "figures")
print("scanpy", sc.__version__, "| working directory:", os.path.abspath(WORKDIR))"""
        ),
    ]


def wrapup(next_en, next_es):
    return md(
        f"---\n## ✅ Done!\n{next_en}",
        f"---\n## ✅ ¡Listo!\n{next_es}",
    )
