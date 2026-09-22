"""Download the Marketplace key art and screenshots listed in data/products.json.

Writes, per product, under assets/img/<slug>/:
  keyart.jpg / keyart.webp   original 800x450 key art
  thumb.jpg                  500x500 center crop (Bucket of Crabs thumbnail)
  shot-1..3.webp             screenshots for the website
"""
import io
import json
import pathlib
import urllib.request

from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) portfolio-image-fetch"}


def fetch(url: str) -> Image.Image:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    img = Image.open(io.BytesIO(data))
    img.load()
    return img.convert("RGB")


def square(img: Image.Image, size: int) -> Image.Image:
    """Whole key art centered on a blurred fill, so the title stays readable."""
    w, h = img.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    bg = img.crop((left, top, left + s, top + s)).resize((size, size), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.55))
    fg = img.resize((size, round(size * h / w)), Image.LANCZOS)
    bg.paste(fg, (0, (size - fg.size[1]) // 2))
    return bg


def main() -> None:
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    for p in products:
        d = OUT / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        key = fetch(p["keyart"])
        key.save(d / "keyart.jpg", quality=90)
        key.save(d / "keyart.webp", quality=82)
        square(key, 500).save(d / "thumb.jpg", quality=90)
        for i, url in enumerate(p["shots"], 1):
            fetch(url).save(d / f"shot-{i}.webp", quality=80)
        print(f"ok  {p['slug']:<22} keyart {key.size[0]}x{key.size[1]}, {len(p['shots'])} shots")


if __name__ == "__main__":
    main()
