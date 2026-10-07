# Setup instructions / Instrucciones de configuración

- [English](#english)
- [Español](#español)

---

## English

### Option A — Google Colab (recommended, nothing to install)

**What you need:** a laptop with a recent Chrome, Firefox, Edge or Safari, a stable internet connection, and a free
Google account. A tablet or phone is not enough for the hands-on parts.

**Before the tutorial (5 minutes, please do it at home or at the hotel):**
1. Make sure you can sign in to <https://colab.research.google.com> with your Google account.
2. Open notebook 00 ([English](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/00_setup_and_cellranger.ipynb) ·
   [Español](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/00_setup_and_cellranger.ipynb)).
3. Click **File → Save a copy in Drive** so your edits are kept.
4. Run the first code cell (**Setup**). If it ends with a line like `scanpy 1.x.x | working directory: ...`, you are ready.

**During the tutorial:**
- Open each notebook from the links in the [README](README.md#schedule-and-materials).
- Each Colab notebook runs on its own temporary machine. Notebooks 02–04 automatically rebuild the results of the
  previous notebook if they cannot find them (about 1 minute). To skip that, set `USE_DRIVE = True` in the setup cell:
  results are then saved in `My Drive/sc_tutorial/` and reused.
- If something goes wrong: **Runtime → Restart session and run all**.
- The free CPU runtime (~12 GB RAM) is enough. A GPU is only useful for the optional scVI section in notebook 05.

**Troubleshooting**
| Problem | Fix |
|---|---|
| "Warning: This notebook was not authored by Google" | Click **Run anyway** (it is this repository). |
| `ModuleNotFoundError` | Run the **Setup** cell first; if you restarted the session, run it again. |
| A download fails (10x, figshare, OmniPath, CellTypist) | Run the cell again; conference Wi-Fi can be slow. If it keeps failing, ask the instructor for the offline copy. |
| Session disconnected / out of memory | **Runtime → Restart session and run all**. Close other Colab tabs. |

### Option B — Your own computer

Requirements: Python 3.11–3.12, ~4 GB free disk, 8 GB RAM.

```bash
git clone https://github.com/Kur1sutaru/ISMB-LATAM.git
cd ISMB-LATAM
python -m venv sc-env
source sc-env/bin/activate          # Windows: sc-env\Scripts\activate
pip install -r requirements.txt
jupyter lab                          # open notebooks/en or notebooks/es
```
With conda/mamba: `mamba env create -f environment.yml && mamba activate sc-tutorial && jupyter lab`.

The notebooks detect that they are not on Colab and skip the installation step. Data are downloaded to
`notebooks/<lang>/sc_tutorial/data/` the first time.

---

## Español

### Opción A — Google Colab (recomendada, no hay que instalar nada)

**Qué necesitas:** una laptop con Chrome, Firefox, Edge o Safari actualizado, una conexión a internet estable y una
cuenta gratuita de Google. Una tableta o un celular no son suficientes para las partes prácticas.

**Antes del tutorial (5 minutos, por favor hazlo en casa o en el hotel):**
1. Verifica que puedes iniciar sesión en <https://colab.research.google.com> con tu cuenta de Google.
2. Abre el notebook 00 ([Español](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/es/00_setup_and_cellranger.ipynb) ·
   [English](https://colab.research.google.com/github/Kur1sutaru/ISMB-LATAM/blob/main/notebooks/en/00_setup_and_cellranger.ipynb)).
3. Haz clic en **Archivo → Guardar una copia en Drive** para conservar tus cambios.
4. Ejecuta la primera celda de código (**Configuración**). Si termina con una línea como
   `scanpy 1.x.x | working directory: ...`, ya estás listo.

**Durante el tutorial:**
- Abre cada notebook desde los enlaces del [README](README.es.md#programa-y-materiales).
- Cada notebook de Colab corre en su propia máquina temporal. Los notebooks 02–04 reconstruyen automáticamente los
  resultados del notebook anterior si no los encuentran (cerca de 1 minuto). Para evitarlo, cambia `USE_DRIVE = True`
  en la celda de configuración: los resultados se guardan en `Mi unidad/sc_tutorial/` y se reutilizan.
- Si algo falla: **Entorno de ejecución → Reiniciar sesión y ejecutar todo**.
- El entorno gratuito con CPU (~12 GB de RAM) es suficiente. Una GPU solo sirve para la sección opcional de scVI del notebook 05.

**Solución de problemas**
| Problema | Solución |
|---|---|
| "Advertencia: Google no creó este notebook" | Haz clic en **Ejecutar de todos modos** (es este repositorio). |
| `ModuleNotFoundError` | Ejecuta primero la celda de **Configuración**; si reiniciaste la sesión, vuelve a ejecutarla. |
| Falla una descarga (10x, figshare, OmniPath, CellTypist) | Vuelve a ejecutar la celda; el Wi-Fi del congreso puede ser lento. Si sigue fallando, pide a la instructora la copia sin conexión. |
| Sesión desconectada / sin memoria | **Entorno de ejecución → Reiniciar sesión y ejecutar todo**. Cierra otras pestañas de Colab. |

### Opción B — En tu computadora

Requisitos: Python 3.11–3.12, ~4 GB libres en disco, 8 GB de RAM.

```bash
git clone https://github.com/Kur1sutaru/ISMB-LATAM.git
cd ISMB-LATAM
python -m venv sc-env
source sc-env/bin/activate          # Windows: sc-env\Scripts\activate
pip install -r requirements.txt
jupyter lab                          # abre notebooks/es o notebooks/en
```
Con conda/mamba: `mamba env create -f environment.yml && mamba activate sc-tutorial && jupyter lab`.

Los notebooks detectan que no están en Colab y omiten la instalación. Los datos se descargan en
`notebooks/<idioma>/sc_tutorial/data/` la primera vez.
