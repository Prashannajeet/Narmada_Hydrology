from pathlib import Path
import re

html_path = Path("outputs/hms-narmada-model-tool.html")
data_path = Path("outputs/hms-narmada-model-data.js")

html = html_path.read_text(encoding="utf-8")
data = data_path.read_text(encoding="utf-8").strip()
replacement = "    " + data

pattern = re.compile(r"    window\.HMS_NARMADA_DATA = .*?;\n", re.S)
html, count = pattern.subn(replacement + "\n", html, count=1)
if count != 1:
    raise SystemExit(f"embedded data block replacements: {count}")

html_path.write_text(html, encoding="utf-8")
print(html_path.stat().st_size)
