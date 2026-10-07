"""Build the English and Spanish Colab notebooks from a single source.

Each notebook lives in tools/notebooks_src/nbXX_*.py and defines:
    META  = dict(file=..., title=(en, es), time=..., goals=([en...], [es...]))
    CELLS = [md(en, es), code("..."), exercise(...), ...]

Code is shared between languages. Inside code, a comment written as
    # English text || Texto en español
is rendered in the language of the notebook, so code is identical in both versions.

Usage:  python tools/build_notebooks.py        -> writes notebooks/en/*.ipynb and notebooks/es/*.ipynb
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "notebooks_src"
REPO = "Kur1sutaru/ISMB-LATAM"
BRANCH = "main"

LANGS = ("en", "es")
_COMMENT = re.compile(r"^(?P<pre>.*?#\s*)(?P<en>.+?)\s*\|\|\s*(?P<es>.+?)\s*$")


class Cell:
    def __init__(self, kind, en, es=None, hidden_title=None):
        self.kind, self.en, self.es, self.hidden_title = kind, en, es, hidden_title

    def text(self, lang):
        if self.kind == "md":
            return (self.en if lang == "en" else self.es).strip("\n")
        src = self.en.strip("\n")
        out = []
        for line in src.split("\n"):
            m = _COMMENT.match(line)
            if m and "://" not in line.split("#", 1)[1]:
                line = m["pre"] + (m["en"] if lang == "en" else m["es"])
            out.append(line)
        return "\n".join(out)


def md(en, es):
    return Cell("md", en, es)


def code(src):
    return Cell("code", src)


def exercise(q_en, q_es, solution, starter="# Your code here || Tu código aquí\n"):
    """A question, an empty code cell and a collapsed solution."""
    sol = Cell("code", solution)
    return [
        md(f"### 💡 Your turn\n{q_en}", f"### 💡 Te toca a ti\n{q_es}"),
        code(starter),
        md(
            "<details><summary><b>Show solution</b></summary>\n\n```python\n" + sol.text("en") + "\n```\n</details>",
            "<details><summary><b>Ver solución</b></summary>\n\n```python\n" + sol.text("es") + "\n```\n</details>",
        ),
    ]


def header(meta, lang):
    file = meta["file"]
    badge = f"https://colab.research.google.com/github/{REPO}/blob/{BRANCH}/notebooks/{lang}/{file}"
    title = meta["title"][0 if lang == "en" else 1]
    goals = meta["goals"][0 if lang == "en" else 1]
    if lang == "en":
        lines = [
            f"# {title}",
            f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({badge})",
            "",
            "**From Cells to Clusters: An Introduction to Single-Cell RNA-seq Analysis in Python**  ",
            "ISCB-LATAM SolBio SPBBC 2026 · Lima, Peru · November 9, 2026  ",
            "Instructor: Dr. Cristal Villalba Silva (UT Health San Antonio) · "
            "[github.com/Kur1sutaru](https://github.com/Kur1sutaru)",
            "",
            f"⏱ **Time in the tutorial:** {meta['time']}",
            "",
            "**By the end of this notebook you will be able to:**",
        ]
        tail = ["", "> 🟢 **Core** sections are covered live. 🔎 **Extra** sections are for self-study after the tutorial."]
    else:
        lines = [
            f"# {title}",
            f"[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({badge})",
            "",
            "**De Células a Clústeres: Introducción al Análisis de Single-Cell RNA-seq en Python**  ",
            "ISCB-LATAM SolBio SPBBC 2026 · Lima, Perú · 9 de noviembre de 2026  ",
            "Instructora: Dra. Cristal Villalba Silva (UT Health San Antonio) · "
            "[github.com/Kur1sutaru](https://github.com/Kur1sutaru)",
            "",
            f"⏱ **Tiempo en el tutorial:** {meta['time']}",
            "",
            "**Al final de este notebook podrás:**",
        ]
        tail = ["", "> 🟢 Las secciones **Core** se ven en vivo. 🔎 Las secciones **Extra** son para estudiar después del tutorial."]
    lines += [f"- {g}" for g in goals] + tail
    return "\n".join(lines)


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SRC.parent))
    spec.loader.exec_module(mod)
    return mod


def flatten(cells):
    for c in cells:
        if isinstance(c, list):
            yield from flatten(c)
        else:
            yield c


def build(lang, mod):
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": [], "toc_visible": True},
    }
    nb.cells.append(nbf.v4.new_markdown_cell(header(mod.META, lang)))
    for cell in flatten(mod.CELLS):
        txt = cell.text(lang)
        nb.cells.append(nbf.v4.new_markdown_cell(txt) if cell.kind == "md" else nbf.v4.new_code_cell(txt))
    return nb


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    for path in sorted(SRC.glob("nb*.py")):
        mod = load(path)
        for lang in LANGS:
            out = ROOT / "notebooks" / lang / mod.META["file"]
            out.parent.mkdir(parents=True, exist_ok=True)
            nbf.write(build(lang, mod), out)
            print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
