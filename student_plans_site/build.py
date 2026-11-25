"""Build index.html from template.html + plans.json.

Edit plans.json (prices, and the "checked" date), then run:  python3 build.py
index.html carries a seed copy of the prices; the live page also re-reads
plans.json every 30 minutes, so republishing both files updates open pages.
"""
import json
from pathlib import Path

here = Path(__file__).parent
data = json.loads((here / "plans.json").read_text())
seed = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
page = (here / "template.html").read_text().replace("/*__PLANS__*/null", seed)
(here / "index.html").write_text(page)
# Local preview with the same wrapper the published page gets.
(here / "preview.html").write_text(
    '<!doctype html><html><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1"></head>'
    f'<body style="margin:0">{page}</body></html>'
)
print(f"Built index.html with {len(data['plans'])} plans, checked {data['checked']}")
