# Portfolio — Santiago Montes de Oca

Sitio estático publicado en **https://santiaagod.github.io** (GitHub Pages, rama `main`).

## Cómo actualizarlo

1. Editá los datos:
   - `data/profile.json` — nombre, mail, Discord, tarifa, link de Bucket of Crabs.
   - `data/products.json` — los proyectos (texto, fecha de lanzamiento, links, imágenes).
2. Si agregaste un producto nuevo, bajá sus imágenes: `python tools/fetch_images.py`
3. Regenerá la página: `python tools/build.py` (reescribe `index.html`, `assets/og.jpg` y `assets/favicon.svg`).
4. Subilo: `git add -A && git commit -m "..." && git push` — GitHub Pages lo publica solo en un par de minutos.

El diseño vive en `tools/template.html`; no edites `index.html` a mano porque se pisa en cada build.
