"""Smoke tests: python -m pytest tests  (or: python tests/test_site.py)"""
import base64
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["VELANIX_INSTANCE_DIR"] = tempfile.mkdtemp()
os.environ["VELANIX_ADMIN_PASSWORD"] = "test"

import app as site  # noqa: E402

AUTH = {"Authorization": "Basic " + base64.b64encode(b"admin:test").decode()}


def keys(d, prefix=""):
    out = set()
    for k, v in d.items():
        out.add(prefix + k)
        if isinstance(v, dict):
            out |= keys(v, prefix + k + ".")
    return out


def csrf(client, url):
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def test_translation_parity():
    assert keys(site.STRINGS["en"]) == keys(site.STRINGS["de"])


def test_pages_render():
    c = site.app.test_client()
    assert c.get("/").status_code == 302
    for lang in site.LANGS:
        urls = [f"/{lang}/", f"/{lang}/eu-buyers", f"/{lang}/indian-suppliers", f"/{lang}/about",
                f"/{lang}/contact", f"/{lang}/legal", f"/{lang}/thank-you/VX-2026-00001"]
        urls += [f"/{lang}/categories/{cat['slug']}" for cat in site.CATEGORIES]
        for url in urls:
            r = c.get(url)
            assert r.status_code == 200, url
            assert "{{" not in r.get_data(as_text=True), url
    assert c.get("/fr/").status_code == 404
    assert c.get("/en/categories/nope").status_code == 404
    assert c.get("/sitemap.xml").status_code == 200
    r = c.get("/en/rfq?category=industrial-valves&quantity=500&delivery_country=AT")
    assert r.status_code == 302 and "quantity=500" in r.headers["Location"]


def test_rfq_submission_and_export():
    c = site.app.test_client()
    url = "/de/categories/industrial-valves"
    token = csrf(c, url)
    # missing required fields -> 400 with errors
    r = c.post(url, data={"csrf_token": token})
    assert r.status_code == 400 and "field-error" in r.get_data(as_text=True)
    data = {
        "csrf_token": token, "part_name": "Kugelhahn DN100", "spec_valve_type": "ball", "spec_size": "DN100",
        "spec_pressure_class": "PN40", "spec_body_material": "cf8m", "spec_testing": ["en12266", "ped"],
        "quantity": "500", "quantity_unit": "pcs", "delivery_country": "AT", "currency": "EUR",
        "compliance": ["ce", "reach"], "company": "Muster GmbH", "contact_name": "Alex Muster",
        "email": "alex@example.at", "consent": "yes",
        "attachments": (io.BytesIO(b"%PDF-1.4 test"), "drawing rev A.pdf"),
    }
    r = c.post(url, data=data, content_type="multipart/form-data")
    assert r.status_code == 302, r.get_data(as_text=True)[:500]
    ref = r.headers["Location"].rsplit("/", 1)[-1]
    assert re.fullmatch(r"VX-\d{4}-\d{5}", ref)

    leads = c.get("/admin/leads.json", headers=AUTH).get_json()
    lead = next(l for l in leads if l["ref"] == ref)
    assert lead["spec"]["testing"] == ["en12266", "ped"]
    assert lead["locale"] == "de" and lead["attachments"] == "drawing_rev_A.pdf"
    assert "Muster GmbH" in c.get("/admin/leads.csv", headers=AUTH).get_data(as_text=True)
    assert c.get(f"/admin/leads/{ref}", headers=AUTH).status_code == 200
    assert c.get("/admin/", headers=AUTH).status_code == 200
    assert c.get("/admin/").status_code == 401


def test_supplier_and_contact_forms():
    c = site.app.test_client()
    token = csrf(c, "/en/indian-suppliers")
    r = c.post("/en/indian-suppliers", data={
        "csrf_token": token, "company": "Kovai Castings", "city": "Coimbatore", "categories": ["castings-forgings-machining"],
        "certifications": ["ISO 9001"], "contact_name": "R. Kumar", "email": "r@kovai.in", "consent": "yes"})
    assert r.status_code == 302 and "kind=supplier" in r.headers["Location"]
    token = csrf(c, "/en/contact")
    r = c.post("/en/contact", data={"csrf_token": token, "category": "pumps-compressors-machinery", "quantity": "200",
                                    "company": "Pumpen AG", "contact_name": "J. Doe", "email": "j@pumpen.de", "consent": "yes"})
    assert r.status_code == 302
    # CSRF enforced
    assert c.post("/en/contact", data={"company": "x"}).status_code == 400


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
