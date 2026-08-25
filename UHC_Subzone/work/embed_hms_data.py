from pathlib import Path

html_path = Path("outputs/hms-narmada-model-tool.html")
data_path = Path("outputs/hms-narmada-model-data.js")

html = html_path.read_text(encoding="utf-8")
data = data_path.read_text(encoding="utf-8").strip()

old = '  <script src="hms-narmada-model-data.js"></script>'
new = "  <script>\n    " + data.replace("\n", "\n    ") + "\n  </script>"

if old not in html:
    raise SystemExit("script tag not found")

html_path.write_text(html.replace(old, new), encoding="utf-8")
print(html_path.stat().st_size)
