"""Execute every notebook offline against synthetic stand-in data.

    python tests/run_notebooks.py [--lang en|es|all] [pattern]

The synthetic data (tests/make_synthetic_data.py) mimics the exact file formats of the
real downloads, so this checks that the code runs end to end with the pinned package
versions. It does NOT check biology: run the notebooks on Colab with the real data for that.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en")
    ap.add_argument("pattern", nargs="?", default="*")
    ap.add_argument("--keep", default=None, help="folder to save executed notebooks")
    args = ap.parse_args()

    cache = Path(tempfile.gettempdir()) / "sc_tutorial_testdata"
    model_dir = Path.home() / ".celltypist" / "data" / "models"
    if not (cache / "kang_counts_25k.h5ad").exists() or not (model_dir / "Immune_All_Low.pkl").exists():
        subprocess.run([sys.executable, str(ROOT / "tests" / "make_synthetic_data.py"), str(cache), str(model_dir)],
                       check=True)

    langs = ["en", "es"] if args.lang == "all" else [args.lang]
    failures = []
    for lang in langs:
        for nb_path in sorted((ROOT / "notebooks" / lang).glob(f"{args.pattern}.ipynb")):
            work = Path(tempfile.mkdtemp(prefix="nbtest_"))
            shutil.copy(ROOT / "scripts" / "sc_tutorial.py", work)
            shutil.copytree(cache, work / "sc_tutorial" / "data")
            nb = nbformat.read(nb_path, as_version=4)
            t0 = time.time()
            try:
                NotebookClient(nb, timeout=900, kernel_name="python3",
                               resources={"metadata": {"path": str(work)}}).execute()
                status = "OK"
            except Exception as exc:  # noqa: BLE001
                status = "FAIL"
                failures.append((nb_path, str(exc)[-3000:]))
            if args.keep:
                out = Path(args.keep) / lang
                out.mkdir(parents=True, exist_ok=True)
                nbformat.write(nb, out / nb_path.name)
            print(f"[{status}] {lang}/{nb_path.name}  ({time.time() - t0:.0f}s)", flush=True)
            shutil.rmtree(work, ignore_errors=True)
    for path, err in failures:
        print("\n=====", path.name, "=====\n", err)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
