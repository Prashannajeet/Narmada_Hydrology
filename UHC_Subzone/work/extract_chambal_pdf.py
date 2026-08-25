import json
import pathlib

import pdfplumber


PDF = pathlib.Path(r"F:\05 Knowledge\CWC\Flood Estimation Reports-CWC\2-Chambal subzone 1(b).pdf")
OUT = pathlib.Path("work/chambal_report_text.txt")


def main():
    texts = []
    with pdfplumber.open(PDF) as pdf:
        for page_number, page in enumerate(pdf.pages, 1):
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            texts.append(f"\n\n--- PAGE {page_number} ---\n{text}")

    OUT.write_text("\n".join(texts), encoding="utf-8")
    print(json.dumps({"pages": page_number, "chars": OUT.stat().st_size, "out": str(OUT)}))


if __name__ == "__main__":
    main()
