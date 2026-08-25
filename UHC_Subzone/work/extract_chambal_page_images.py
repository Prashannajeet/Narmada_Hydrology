import pathlib

from pypdf import PdfReader


PDF = pathlib.Path(r"F:\05 Knowledge\CWC\Flood Estimation Reports-CWC\2-Chambal subzone 1(b).pdf")
OUT = pathlib.Path("work/chambal_page_images")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(PDF))
    saved = []
    for page_index, page in enumerate(reader.pages, 1):
        for image_index, image in enumerate(page.images, 1):
            suffix = pathlib.Path(image.name).suffix or ".png"
            target = OUT / f"page-{page_index:03d}-image-{image_index:02d}{suffix}"
            target.write_bytes(image.data)
            saved.append(str(target))
    print({"pages": len(reader.pages), "images": len(saved), "sample": saved[:10]})


if __name__ == "__main__":
    main()
