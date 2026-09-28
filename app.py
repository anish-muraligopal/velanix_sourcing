"""Velanix Sourcing — EU–India B2B sourcing website.

Run locally:  python app.py   (http://127.0.0.1:5000)
"""
import csv
import io
import json
import logging
import os
import re
import secrets
import sqlite3
import threading
import urllib.request
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import (Flask, Response, abort, g, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)
from werkzeug.utils import secure_filename

from content.categories import (CATEGORIES, CATEGORY_BY_SLUG, COMPLIANCE, ORDER_TYPES,
                                SOURCING_SITUATIONS, UNITS)
from content.site import COUNTRIES, CURRENCIES, INCOTERMS, SITE, TEAM

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = Path(os.environ.get("VELANIX_INSTANCE_DIR", BASE_DIR / "instance"))
DB_PATH = INSTANCE_DIR / "leads.db"
UPLOAD_DIR = INSTANCE_DIR / "uploads"
LANGS = ("en", "de")
ALLOWED_EXT = {"pdf", "step", "stp", "igs", "iges", "dwg", "dxf", "stl", "x_t", "sldprt",
               "png", "jpg", "jpeg", "xlsx", "xls", "csv", "docx", "zip"}
MAX_FILES = 10
LEAD_STATUSES = ["new", "qualified", "quoting", "sampling", "won", "lost", "on_hold"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Static export (GitHub Pages): forms submit from the browser to FORM_ENDPOINT (e.g. Formspree),
# or fall back to a pre-filled email when no endpoint is configured. See freeze.py.
STATIC_MODE = os.environ.get("VELANIX_STATIC") == "1"
FORM_ENDPOINT = os.environ.get("VELANIX_FORM_ENDPOINT", "")
if os.environ.get("SITE_URL"):
    SITE["domain"] = os.environ["SITE_URL"].rstrip("/")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024
app.secret_key = os.environ.get("VELANIX_SECRET_KEY") or secrets.token_hex(32)
app.jinja_env.filters["zip_self"] = lambda items: [(i, i) for i in items]
log = logging.getLogger("velanix")

STRINGS = {lang: json.loads((BASE_DIR / "translations" / f"{lang}.json").read_text(encoding="utf-8"))
           for lang in LANGS}


# ---------------------------------------------------------------- database
def get_db():
    if "db" not in g:
        INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


LEAD_COLUMNS = [
    "ref", "created_at", "lead_type", "status", "locale", "category", "hs_code",
    "company", "contact_name", "role", "email", "phone", "company_country", "website",
    "delivery_country", "quantity", "quantity_unit", "order_type", "annual_volume",
    "target_price", "currency", "incoterm", "required_by", "sourcing_situation",
    "compliance", "spec_json", "message", "attachments", "nda_requested",
    "source_page", "utm", "notes",
]


def init_db():
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    cols = ",\n".join(f"{c} TEXT" for c in LEAD_COLUMNS if c != "ref")
    with sqlite3.connect(DB_PATH) as db:
        db.execute(f"CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT, ref TEXT UNIQUE, {cols})")


init_db()


# ---------------------------------------------------------------- i18n / routing
@app.url_value_preprocessor
def pull_lang(_endpoint, values):
    g.lang = values.pop("lang", None) if values else None


@app.url_defaults
def add_lang(endpoint, values):
    if "lang" in values or not g.get("lang"):
        return
    if app.url_map.is_endpoint_expecting(endpoint, "lang"):
        values["lang"] = g.lang


@app.before_request
def validate_lang():
    if g.get("lang") and g.lang not in LANGS:
        abort(404)


def current_lang():
    return g.get("lang") or "en"


def loc(value):
    """Pick the current language from a {"en":..., "de":...} dict."""
    if isinstance(value, dict) and "en" in value:
        return value.get(current_lang()) or value["en"]
    return value


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(24)
    return session["csrf"]


@app.context_processor
def inject_globals():
    lang = current_lang()

    def alt_url(target_lang):
        if request.endpoint and request.view_args is not None and app.url_map.is_endpoint_expecting(request.endpoint, "lang"):
            return url_for(request.endpoint, lang=target_lang, **request.view_args)
        return url_for("home", lang=target_lang)

    return {
        "lang": lang,
        "T": STRINGS[lang],
        "loc": loc,
        "site": SITE,
        "categories": CATEGORIES,
        "alt_url": alt_url,
        "langs": LANGS,
        "csrf_token": csrf_token,
        "countries": [(c, en if lang == "en" else de) for c, en, de in COUNTRIES],
        "year": datetime.now().year,
        "static_mode": STATIC_MODE,
        "form_endpoint": FORM_ENDPOINT,
    }


# ---------------------------------------------------------------- lead capture
def check_csrf():
    token = request.form.get("csrf_token", "")
    if not token or not secrets.compare_digest(token, session.get("csrf", "")):
        abort(400, "Form expired. Please reload the page and try again.")


def is_spam():
    return bool(request.form.get("_gotcha"))


def clean(name, max_len=2000):
    return (request.form.get(name) or "").strip()[:max_len]


def validate_contact(errors, E):
    for name in ("company", "contact_name", "email"):
        if not clean(name):
            errors[name] = E["required"]
    if clean("email") and not EMAIL_RE.match(clean("email")):
        errors["email"] = E["email"]
    if not request.form.get("consent"):
        errors["consent"] = E["consent"]


def save_files(ref):
    saved = []
    files = [f for f in request.files.getlist("attachments") if f and f.filename][:MAX_FILES]
    if not files:
        return saved
    target = UPLOAD_DIR / ref
    target.mkdir(parents=True, exist_ok=True)
    for f in files:
        name = secure_filename(f.filename)
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if not name or ext not in ALLOWED_EXT:
            continue
        f.save(target / name)
        saved.append(name)
    return saved


def insert_lead(data):
    data = {k: v for k, v in data.items() if k in LEAD_COLUMNS}
    data.setdefault("status", "new")
    data["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    data["locale"] = current_lang()
    data["source_page"] = request.path
    utm = {k: v for k, v in request.args.items() if k.startswith("utm_")}
    data["utm"] = json.dumps(utm) if utm else ""
    db = get_db()
    cols = ", ".join(data)
    cur = db.execute(f"INSERT INTO leads ({cols}) VALUES ({', '.join('?' * len(data))})", list(data.values()))
    lead_id = cur.lastrowid
    ref = f"VX-{datetime.now().year}-{lead_id:05d}"
    attachments = save_files(ref)
    db.execute("UPDATE leads SET ref = ?, attachments = ? WHERE id = ?", (ref, ", ".join(attachments), lead_id))
    db.commit()
    data.update(ref=ref, attachments=", ".join(attachments))
    push_to_crm(data)
    return ref


def push_to_crm(lead):
    """POST the lead as JSON to VELANIX_CRM_WEBHOOK (e.g. Zapier/Make -> HubSpot/Pipedrive)."""
    url = os.environ.get("VELANIX_CRM_WEBHOOK")
    if not url:
        return
    payload = json.dumps(lead).encode("utf-8")

    def send():
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=8)
        except Exception as exc:  # the lead is already in SQLite; never fail the request
            log.warning("CRM webhook failed for %s: %s", lead.get("ref"), exc)

    threading.Thread(target=send, daemon=True).start()


def spec_value(f):
    key = f"spec_{f['name']}"
    if f["kind"] == "multi":
        return request.form.getlist(key)
    return clean(key, 500)


# ---------------------------------------------------------------- pages
@app.route("/")
def root():
    return redirect(url_for("home", lang=request.accept_languages.best_match(LANGS) or "en"))


@app.route("/<lang>/")
def home():
    return render_template("home.html")


@app.route("/<lang>/rfq")
def rfq_start():
    """Homepage quick-quote widget: forward to the category form, keeping quantity/country."""
    slug = request.args.get("category")
    if slug not in CATEGORY_BY_SLUG:
        return redirect(url_for("home", _anchor="categories"))
    prefill = {k: request.args[k] for k in ("quantity", "delivery_country") if request.args.get(k)}
    return redirect(url_for("category", slug=slug, _anchor="rfq", **prefill))


@app.route("/<lang>/categories/<slug>", methods=["GET", "POST"])
def category(slug):
    cat = CATEGORY_BY_SLUG.get(slug)
    if not cat:
        abort(404)
    errors, values = {}, {}
    if request.method == "POST":
        check_csrf()
        values = request.form.to_dict(flat=False)
        if is_spam():
            return redirect(url_for("thanks", ref="VX-0"))
        E = STRINGS[current_lang()]["form"]["errors"]
        spec = {}
        for f in cat["fields"]:
            spec[f["name"]] = spec_value(f)
            if f["required"] and not spec[f["name"]]:
                errors[f"spec_{f['name']}"] = E["required"]
        for name in ("quantity", "delivery_country"):
            if not clean(name):
                errors[name] = E["required"]
        validate_contact(errors, E)
        if not errors:
            ref = insert_lead({
                "lead_type": "rfq", "category": cat["slug"], "hs_code": cat["hs"],
                "company": clean("company", 200), "contact_name": clean("contact_name", 200), "role": clean("role", 200),
                "email": clean("email", 200), "phone": clean("phone", 60), "company_country": clean("company_country", 10),
                "website": clean("website", 200), "delivery_country": clean("delivery_country", 10),
                "quantity": clean("quantity", 40), "quantity_unit": clean("quantity_unit", 10),
                "order_type": clean("order_type", 40), "annual_volume": clean("annual_volume", 60),
                "target_price": clean("target_price", 40), "currency": clean("currency", 5),
                "incoterm": clean("incoterm", 5), "required_by": clean("required_by", 20),
                "sourcing_situation": clean("sourcing_situation", 40),
                "compliance": ", ".join(request.form.getlist("compliance")),
                "spec_json": json.dumps({"part_name": clean("part_name", 200), **spec}, ensure_ascii=False),
                "message": clean("message", 5000), "nda_requested": "yes" if request.form.get("nda") else "no",
            })
            return redirect(url_for("thanks", ref=ref))
    else:
        # Pre-fill from the homepage quick-quote widget.
        for k in ("quantity", "delivery_country"):
            if request.args.get(k):
                values[k] = [request.args[k]]
    return render_template(
        "category.html", cat=cat, errors=errors, values=values, compliance=COMPLIANCE, units=UNITS,
        order_types=ORDER_TYPES, situations=SOURCING_SITUATIONS, currencies=CURRENCIES,
        incoterms=INCOTERMS), (400 if errors else 200)


@app.route("/<lang>/eu-buyers")
def buyers():
    return render_template("buyers.html")


@app.route("/<lang>/indian-suppliers", methods=["GET", "POST"])
def suppliers():
    errors, values = {}, {}
    if request.method == "POST":
        check_csrf()
        values = request.form.to_dict(flat=False)
        if is_spam():
            return redirect(url_for("thanks", ref="VX-0"))
        E = STRINGS[current_lang()]["form"]["errors"]
        if not request.form.getlist("categories"):
            errors["categories"] = E["required"]
        if not clean("city"):
            errors["city"] = E["required"]
        validate_contact(errors, E)
        if not errors:
            spec = {k: clean(k, 500) for k in ("city", "state", "employees", "turnover", "export_share",
                                                 "export_markets", "eu_customers", "capacity")}
            spec["certifications"] = request.form.getlist("certifications")
            ref = insert_lead({
                "lead_type": "supplier", "category": ", ".join(request.form.getlist("categories")),
                "company": clean("company", 200), "contact_name": clean("contact_name", 200), "role": clean("role", 200),
                "email": clean("email", 200), "phone": clean("phone", 60), "company_country": "IN",
                "website": clean("website", 200), "spec_json": json.dumps(spec, ensure_ascii=False),
                "message": clean("message", 5000),
            })
            return redirect(url_for("thanks", ref=ref, kind="supplier"))
    return render_template("suppliers.html", errors=errors, values=values), (400 if errors else 200)


@app.route("/<lang>/about")
def about():
    return render_template("about.html", team=TEAM)


@app.route("/<lang>/contact", methods=["GET", "POST"])
def contact():
    errors, values = {}, {}
    if request.method == "POST":
        check_csrf()
        values = request.form.to_dict(flat=False)
        if is_spam():
            return redirect(url_for("thanks", ref="VX-0"))
        E = STRINGS[current_lang()]["form"]["errors"]
        if not clean("category"):
            errors["category"] = E["required"]
        validate_contact(errors, E)
        if not errors:
            cat = CATEGORY_BY_SLUG.get(clean("category"))
            ref = insert_lead({
                "lead_type": "inquiry", "category": clean("category", 80), "hs_code": cat["hs"] if cat else "",
                "company": clean("company", 200), "contact_name": clean("contact_name", 200), "role": clean("role", 200),
                "email": clean("email", 200), "phone": clean("phone", 60), "company_country": clean("company_country", 10),
                "delivery_country": clean("delivery_country", 10), "quantity": clean("quantity", 40),
                "quantity_unit": clean("quantity_unit", 10), "target_price": clean("target_price", 40),
                "currency": "EUR" if clean("target_price") else "",
                "spec_json": json.dumps({"product": clean("product", 300)}, ensure_ascii=False),
                "message": clean("message", 5000),
            })
            return redirect(url_for("thanks", ref=ref))
    return render_template("contact.html", errors=errors, values=values, units=UNITS), (400 if errors else 200)


@app.route("/<lang>/thank-you/<ref>")
def thanks(ref):
    if not re.fullmatch(r"VX-\d{1,4}(-\d{5})?", ref):
        abort(404)
    return render_template("thanks.html", ref=ref, kind=request.args.get("kind", "buyer"))


@app.route("/<lang>/thank-you/")
def thanks_static():
    """Static-site thank-you page; reference and buyer/supplier text are filled in by JS from the query string."""
    return render_template("thanks.html", ref=None, kind="buyer")


@app.route("/<lang>/legal")
def legal():
    return render_template("legal.html")


@app.route("/robots.txt")
def robots():
    return Response(f"User-agent: *\nDisallow: /admin/\nSitemap: {SITE['domain']}/sitemap.xml\n", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    paths = ["home", "buyers", "suppliers", "about", "contact", "legal"]
    urls = []
    for lang in LANGS:
        urls += [SITE["domain"] + url_for(p, lang=lang) for p in paths]
        urls += [SITE["domain"] + url_for("category", lang=lang, slug=c["slug"]) for c in CATEGORIES]
    body = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>',
                    mimetype="application/xml")


@app.errorhandler(404)
def not_found(_e):
    if g.get("lang") not in LANGS:
        g.lang = "en"
    return render_template("404.html"), 404


# ---------------------------------------------------------------- admin (CRM intake)
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        password = os.environ.get("VELANIX_ADMIN_PASSWORD")
        if not password:
            return Response("Admin disabled. Set VELANIX_ADMIN_PASSWORD to enable.", 503)
        auth = request.authorization
        if not auth or auth.username != os.environ.get("VELANIX_ADMIN_USER", "admin") \
                or not secrets.compare_digest(auth.password or "", password):
            return Response("Authentication required", 401, {"WWW-Authenticate": 'Basic realm="Velanix admin"'})
        return view(*args, **kwargs)
    return wrapped


def query_leads():
    sql, params = "SELECT * FROM leads WHERE 1=1", []
    for key in ("lead_type", "status", "category"):
        if request.args.get(key):
            sql += f" AND {key} LIKE ?"
            params.append(f"%{request.args[key]}%")
    if request.args.get("q"):
        sql += " AND (company LIKE ? OR email LIKE ? OR contact_name LIKE ? OR ref LIKE ?)"
        params += [f"%{request.args['q']}%"] * 4
    return get_db().execute(sql + " ORDER BY id DESC", params).fetchall()


@app.route("/admin/")
@admin_required
def admin_leads():
    return render_template("admin/leads.html", leads=query_leads(), statuses=LEAD_STATUSES,
                           cat_names={c["slug"]: c["name"]["en"] for c in CATEGORIES})


@app.route("/admin/leads/<ref>", methods=["GET", "POST"])
@admin_required
def admin_lead(ref):
    db = get_db()
    if request.method == "POST":
        check_csrf()
        status = request.form.get("status")
        if status in LEAD_STATUSES:
            db.execute("UPDATE leads SET status = ?, notes = ? WHERE ref = ?", (status, request.form.get("notes", ""), ref))
            db.commit()
        return redirect(url_for("admin_lead", ref=ref))
    lead = db.execute("SELECT * FROM leads WHERE ref = ?", (ref,)).fetchone()
    if not lead:
        abort(404)
    spec = json.loads(lead["spec_json"] or "{}")
    files = [f for f in (lead["attachments"] or "").split(", ") if f]
    return render_template("admin/lead.html", lead=lead, spec=spec, files=files, statuses=LEAD_STATUSES)


@app.route("/admin/files/<ref>/<name>")
@admin_required
def admin_file(ref, name):
    return send_from_directory(UPLOAD_DIR / secure_filename(ref), secure_filename(name), as_attachment=True)


@app.route("/admin/leads.csv")
@admin_required
def admin_csv():
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id"] + LEAD_COLUMNS)
    for row in query_leads():
        writer.writerow([row["id"]] + [row[c] for c in LEAD_COLUMNS])
    # BOM so Excel opens UTF-8 (German umlauts) correctly
    return Response("﻿" + buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=velanix-leads.csv"})


@app.route("/admin/leads.json")
@admin_required
def admin_json():
    leads = []
    for row in query_leads():
        item = dict(row)
        item["spec"] = json.loads(item.pop("spec_json") or "{}")
        leads.append(item)
    return jsonify(leads)


if __name__ == "__main__":
    if not os.environ.get("VELANIX_ADMIN_PASSWORD"):
        os.environ["VELANIX_ADMIN_PASSWORD"] = "change-me"
        print(" * Dev admin at /admin/  (user: admin, password: change-me)")
    app.run(debug=True)
