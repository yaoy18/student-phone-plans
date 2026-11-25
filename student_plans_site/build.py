"""Build the site from template.html + plans.json.

Edit plans.json (prices, and the "checked" date), then run:  python3 build.py

Writes:
  index.html            the page as a Claude Artifact expects it (no <html> wrapper)
  ../docs/index.html    the same page as a complete web page, served by GitHub Pages
  ../docs/plans.json    a copy of the prices; the page re-reads it every 30 minutes
  preview.html          a local preview (not committed)
"""
import json
from pathlib import Path

here = Path(__file__).parent
docs = here.parent / "docs"
data = json.loads((here / "plans.json").read_text())
seed = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
page = (here / "template.html").read_text().replace("/*__PLANS__*/null", seed)
(here / "index.html").write_text(page)

# A complete document: the template's <title>, <meta>, <link> and <style> go in <head>.
cut = page.index("</style>") + len("</style>")
head, body = page[:cut], page[cut:]
full = (
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="color-scheme" content="light dark">\n'
    '<meta name="description" content="Compare US phone plans for international students by real yearly cost.">\n'
    "<style>body{margin:0}img{max-width:100%}</style>\n"
    f"{head}\n</head>\n<body>{body}</body>\n</html>\n"
)
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(full)
(docs / "plans.json").write_text((here / "plans.json").read_text())
(docs / ".nojekyll").write_text("")
(here / "preview.html").write_text(full)
print(f"Built index.html and docs/ with {len(data['plans'])} plans, checked {data['checked']}")
