#!/usr/bin/env python3
"""Render the project's Markdown files to styled, standalone HTML.

Solves the "ask Claude to regenerate the HTML every time" problem: run this
yourself whenever you want fresh HTML views. Output goes to docs_html/ (which is
git-ignored — these are local view files, not part of the repo).

Usage:
    pip install markdown            # one-time
    python render_docs.py           # render every *.md in this folder
    python render_docs.py ARCHITECTURE.md INDEX.md   # render specific files

Then open the file, e.g.:  open docs_html/ARCHITECTURE.html   (macOS)
"""
import pathlib
import sys

try:
    import markdown
except ImportError:
    sys.exit("Missing dependency. Run:  pip install markdown")

CSS = """
:root{--bg:#f7f7f5;--panel:#fff;--ink:#1a1a1a;--muted:#5c5c5c;--line:#e2e2dd;
  --accent:#b4491f;--code:#eef2f7}
@media (prefers-color-scheme:dark){:root{--bg:#16181c;--panel:#20242b;--ink:#eceef1;
  --muted:#a3abb6;--line:#333a44;--accent:#e0794f;--code:#1c2530}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);padding:2rem 1rem;
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:900px;margin:0 auto}
h1,h2,h3{line-height:1.25}h1{font-size:1.8rem;border-bottom:2px solid var(--line);padding-bottom:.4rem}
h2{font-size:1.3rem;margin-top:2rem}h3{font-size:1.05rem;color:var(--muted)}
a{color:var(--accent)}
table{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.93rem;overflow-x:auto;display:block}
th,td{text-align:left;padding:.55rem .7rem;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.03em}
code{background:var(--code);padding:.12rem .35rem;border-radius:4px;font-size:.88em}
pre{background:var(--code);padding:1rem;border-radius:8px;overflow-x:auto}
pre code{background:none;padding:0}
blockquote{border-left:4px solid var(--accent);margin:1rem 0;padding:.4rem 1rem;color:var(--muted)}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>{css}</style></head>
<body><div class="wrap">{body}</div></body></html>"""


def render(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists", "toc"]
    )
    return TEMPLATE.format(title=path.stem, css=CSS, body=body)


def main(argv):
    root = pathlib.Path(__file__).parent
    out = root / "docs_html"
    out.mkdir(exist_ok=True)
    files = [pathlib.Path(a) for a in argv] or sorted(root.glob("*.md"))
    for f in files:
        (out / f"{f.stem}.html").write_text(render(f), encoding="utf-8")
        print(f"rendered {f.name} -> docs_html/{f.stem}.html")


if __name__ == "__main__":
    main(sys.argv[1:])
