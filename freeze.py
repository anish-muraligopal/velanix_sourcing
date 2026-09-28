"""Export the site as static HTML for GitHub Pages.

    python freeze.py                       # -> _site/
    BASE_PATH=/repo-name python freeze.py  # project pages live under https://<user>.github.io/<repo-name>/

Env: BASE_PATH (URL prefix, default ""), SITE_URL (for sitemap/hreflang),
VELANIX_FORM_ENDPOINT (e.g. https://formspree.io/f/xxxx; without it forms open a pre-filled email).
"""
import os
import shutil
import sys
from pathlib import Path

os.environ["VELANIX_STATIC"] = "1"

import app as site  # noqa: E402  (reads VELANIX_STATIC at import)

OUT = Path(__file__).resolve().parent / "_site"
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")


def target(path):
    """/en/ -> en/index.html, /en/about -> en/about.html (GitHub Pages serves both without the extension)."""
    rel = path.lstrip("/")
    if not rel or rel.endswith("/"):
        return OUT / rel / "index.html"
    return OUT / (rel if "." in rel.rsplit("/", 1)[-1] else rel + ".html")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    client = site.app.test_client()
    base_url = f"http://localhost{BASE_PATH}/"

    paths = []
    for lang in site.LANGS:
        paths += [f"/{lang}/", f"/{lang}/eu-buyers", f"/{lang}/indian-suppliers", f"/{lang}/about",
                  f"/{lang}/contact", f"/{lang}/legal", f"/{lang}/thank-you/"]
        paths += [f"/{lang}/categories/{c['slug']}" for c in site.CATEGORIES]
    paths += ["/sitemap.xml", "/robots.txt"]

    for path in paths:
        resp = client.get(path, base_url=base_url)
        if resp.status_code != 200:
            sys.exit(f"{path} -> {resp.status_code}")
        dest = target(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.data)

    # 404 page (GitHub Pages serves /404.html for unknown paths)
    (OUT / "404.html").write_bytes(client.get("/en/does-not-exist", base_url=base_url).data)

    # Root: send visitors to their browser language.
    en, de = f"{BASE_PATH}/en/", f"{BASE_PATH}/de/"
    (OUT / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Velanix Sourcing</title>'
        f'<meta http-equiv="refresh" content="0; url={en}"><link rel="canonical" href="{en}">'
        f'<script>location.replace((navigator.language || "").toLowerCase().indexOf("de") === 0 ? "{de}" : "{en}")</script>'
        f'<a href="{en}">English</a> · <a href="{de}">Deutsch</a>', encoding="utf-8")

    shutil.copytree(Path(site.app.static_folder), OUT / "static")
    (OUT / ".nojekyll").write_text("")
    print(f"Exported {len(paths) + 2} pages to {OUT} (base path '{BASE_PATH or '/'}', "
          f"forms -> {site.FORM_ENDPOINT or 'email fallback'})")


if __name__ == "__main__":
    main()
