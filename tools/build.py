"""Render index.html (plus og.jpg and favicon.svg) from data/*.json and tools/template.html.

Run from anywhere:  python tools/build.py
"""
import datetime
import html
import json
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

# Display order on the page: strongest and most varied first, studios interleaved.
ORDER = [
    "portality", "soul-hunters", "pet-blocks", "one-chunk-survival", "wither-plus",
    "weapons", "pizza-rush", "cartoon-planes", "dungeons-expansion",
    "one-block-space-smp", "puppiez", "space-gadgets", "mobs",
]
MOSAIC = ["soul-hunters", "portality", "pet-blocks", "cartoon-planes", "wither-plus", "one-chunk-survival"]

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8" shape-rendering="crispEdges">
<rect x="2" y="0" width="4" height="1" fill="#1fa35c"/><rect x="1" y="1" width="6" height="1" fill="#3ddc84"/>
<rect x="0" y="2" width="8" height="4" fill="#3ddc84"/><rect x="1" y="2" width="2" height="2" fill="#b6f7d2"/>
<rect x="1" y="6" width="6" height="1" fill="#1fa35c"/><rect x="2" y="7" width="4" height="1" fill="#137a42"/>
<rect x="5" y="4" width="2" height="2" fill="#1fa35c"/></svg>
"""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def month_year(iso: str) -> str:
    return datetime.date.fromisoformat(iso).strftime("%b %Y")


def card(p: dict) -> str:
    chips = "".join(f'<span class="chip">{esc(f)}</span>' for f in p["features"][:3])
    return f"""        <button class="card" type="button" data-slug="{esc(p['slug'])}" data-studio="{esc(p['studio'])}" aria-haspopup="dialog">
          <span class="thumb"><img src="assets/img/{esc(p['slug'])}/keyart.webp" alt="{esc(p['title'])} key art" width="800" height="450" loading="lazy"></span>
          <span class="body">
            <span class="title">{esc(p['title'])}</span>
            <span class="studio">{esc(p['studio'])} · {esc(p['type'])} · {month_year(p['released'])}</span>
            <span class="desc">{esc(p['summary'])}</span>
            <span class="chips">{chips}</span>
          </span>
        </button>"""


def ratings_label(products: list) -> str:
    total = sum(p.get("ratings") or 0 for p in products)
    return f"{total // 100 * 100:,}+"


def og_image(products: dict, profile: dict, out: pathlib.Path) -> None:
    W, H = 1200, 630
    canvas = Image.new("RGB", (W, H), (11, 13, 18))
    tile_w, tile_h = 300, 169
    slugs = ORDER[:8]
    for i, slug in enumerate(slugs):
        im = Image.open(IMG / slug / "keyart.jpg").convert("RGB").resize((tile_w, tile_h), Image.LANCZOS)
        canvas.paste(im, ((i % 4) * tile_w, 292 + (i // 4) * tile_h))
    # darken the art so the text reads, strongest at the top
    shade = Image.new("L", (W, H))
    d = ImageDraw.Draw(shade)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=int(255 - max(0, y - 260) * 0.35) if y > 260 else 255)
    dark = Image.new("RGB", (W, H), (11, 13, 18))
    canvas = Image.composite(dark, canvas, shade.point(lambda v: min(255, v)))
    draw = ImageDraw.Draw(canvas)
    fonts = pathlib.Path("C:/Windows/Fonts")
    bold = ImageFont.truetype(str(fonts / "segoeuib.ttf"), 64)
    semi = ImageFont.truetype(str(fonts / "segoeui.ttf"), 30)
    small = ImageFont.truetype(str(fonts / "segoeuib.ttf"), 22)
    draw.rectangle([64, 70, 84, 90], fill=(61, 220, 132))
    draw.text((100, 62), "MINECRAFT BEDROCK DEVELOPER", font=small, fill=(61, 220, 132))
    draw.text((62, 104), profile["name"], font=bold, fill=(233, 236, 242))
    draw.text((64, 190), "Former CTO at Sapphire Studios  ·  13 Marketplace titles", font=semi, fill=(190, 198, 212))
    draw.text((64, 232), "Script API  ·  custom entities  ·  world generation", font=semi, fill=(154, 163, 180))
    canvas.save(out, quality=88)


def main() -> None:
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    by_slug = {p["slug"]: p for p in products}
    ordered = [by_slug[s] for s in ORDER] + [p for p in products if p["slug"] not in ORDER]

    mosaic = "\n".join(
        f'        <img src="assets/img/{s}/keyart.webp" alt="" width="800" height="450">' for s in MOSAIC
    )
    data = [
        {k: p.get(k) for k in ("slug", "title", "studio", "type", "summary", "features", "url", "trailer")}
        | {"released": month_year(p["released"])}
        | {"shots": [None] * len(p["shots"])}
        for p in ordered
    ]
    discord = profile.get("discord")
    discord_item = (
        f'            <li><span class="k">Discord</span><span class="val">{esc(discord)}</span>'
        f'<button class="copy" type="button" data-copy="{esc(discord)}">Copy</button></li>'
        if discord else ""
    )
    subs = {
        "{{NAME}}": esc(profile["name"]),
        "{{HANDLE}}": esc(profile["handle"]),
        "{{EMAIL}}": esc(profile["email"]),
        "{{SITE}}": esc(profile["site"]),
        "{{BOC}}": esc(profile["boc"]),
        "{{RATE}}": esc(profile["rate"]),
        "{{TZ}}": esc(profile["timezone"]),
        "{{YEAR}}": str(datetime.date.today().year),
        "{{RATINGS}}": ratings_label(products),
        "{{COUNT_ALL}}": str(len(products)),
        "{{COUNT_SAPPHIRE}}": str(sum(p["studio"] == "Sapphire Studios" for p in products)),
        "{{COUNT_FOXY}}": str(sum(p["studio"] == "A Foxy Toast" for p in products)),
        "{{MOSAIC}}": mosaic,
        "{{CARDS}}": "\n".join(card(p) for p in ordered),
        "{{DISCORD_ITEM}}": discord_item,
        "{{PRODUCTS_JSON}}": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
    }
    page = (ROOT / "tools" / "template.html").read_text(encoding="utf-8")
    for k, v in subs.items():
        page = page.replace(k, v)
    leftover = [t for t in subs if t in page]
    assert not leftover, leftover
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    (ROOT / "assets" / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    og_image(by_slug, profile, ROOT / "assets" / "og.jpg")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built index.html ({len(page) // 1024} KB), {len(products)} projects, ratings {subs['{{RATINGS}}']}")


if __name__ == "__main__":
    main()
