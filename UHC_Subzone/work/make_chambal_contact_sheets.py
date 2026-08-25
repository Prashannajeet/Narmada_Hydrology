import math
import pathlib

from PIL import Image, ImageDraw, ImageFont


SRC = pathlib.Path("work/chambal_page_images")
OUT = pathlib.Path("work/chambal_contact_sheets")


def make_sheet(files, sheet_index):
    thumb_w, thumb_h = 210, 300
    cols = 5
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 24)), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, file in enumerate(files):
        page_num = int(file.name.split("-")[1])
        img = Image.open(file).convert("RGB")
        img.thumbnail((thumb_w, thumb_h))
        x = (idx % cols) * thumb_w + (thumb_w - img.width) // 2
        y = (idx // cols) * (thumb_h + 24) + 20
        sheet.paste(img, (x, y))
        draw.text(((idx % cols) * thumb_w + 8, (idx // cols) * (thumb_h + 24) + 4), f"Page {page_num}", fill=(0, 0, 0))
    target = OUT / f"sheet-{sheet_index:02d}.jpg"
    sheet.save(target, quality=88)
    return target


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("page-*.jpg"))
    targets = []
    for i in range(0, len(files), 20):
        targets.append(make_sheet(files[i:i + 20], i // 20 + 1))
    print([str(t) for t in targets])


if __name__ == "__main__":
    main()
