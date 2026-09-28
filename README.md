# Velanix Sourcing — website

EU–India B2B sourcing site: Flask + Jinja, server-rendered, English/German, with structured lead capture.

## Run locally

```bash
pip install -r requirements.txt
python app.py            # http://127.0.0.1:5000  (admin: /admin/  user admin / change-me)
python tests/test_site.py
```

## Structure

| Path | What |
|---|---|
| `app.py` | Routes, i18n, form validation, SQLite lead store, admin, CSV/JSON export, CRM webhook |
| `content/categories.py` | The 7 categories: copy, standards, clusters, lead times and **category-specific RFQ fields** |
| `content/site.py` | Company details, team, Magna toggle (`show_magna`), countries — replace `[placeholders]` |
| `translations/en.json`, `de.json` | All page copy. Keep keys identical (a test checks this). Add a language by adding a JSON file and its code to `LANGS` |
| `templates/` | Pages; `_forms.html` = form macros, `_icons.html` = inline SVG icons |
| `static/` | CSS, JS (multi-step form, live RFQ summary, validation), favicon |
| `instance/` | Created at runtime: `leads.db` (SQLite) and `uploads/<ref>/` drawings — not for version control |

URLs: `/en/…` and `/de/…`; `/` redirects by browser language. Category pages: `/en/categories/<slug>`.

## Lead capture (CRM intake)

Every form (category RFQ, quick enquiry, supplier application) writes one row to `leads` with structured columns
(`lead_type`, `category`, `hs_code`, `company`, `delivery_country`, `quantity`, `quantity_unit`, `target_price`,
`currency`, `incoterm`, `compliance`, …) plus `spec_json` with the category-specific fields, and gets a reference such as `VX-2026-00012`.

- `/admin/` — filterable lead list, detail view, pipeline status + internal notes, attachment downloads (HTTP basic auth)
- `/admin/leads.csv` and `/admin/leads.json` — exports (respect the current filters)
- `VELANIX_CRM_WEBHOOK=https://…` — each new lead is also POSTed as JSON (e.g. to Zapier/Make → HubSpot, Pipedrive, email)

## GitHub Pages (static hosting)

`.github/workflows/pages.yml` runs the tests, exports the site with `freeze.py` and deploys it on every push to `main`.
One-time setup: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

GitHub Pages cannot run Python, so on the static site the admin, SQLite lead store and server-side validation are not available.
Forms are submitted from the browser instead:

- **Recommended:** create a free form at [formspree.io](https://formspree.io), then add a repository variable
  `VELANIX_FORM_ENDPOINT` = `https://formspree.io/f/xxxxxxx` (**Settings → Secrets and variables → Actions → Variables**) and re-run the workflow.
  Submissions (all structured fields + reference number) land in Formspree, which emails you and exports CSV.
  Drawing uploads need a paid Formspree plan; on the free plan the form resubmits without the files.
- **Without an endpoint:** the form opens the visitor's email program with the structured request pre-filled, addressed to `SITE["email"]`.

Preview the export locally: `python freeze.py` → `_site/`.

## Production environment variables (full Flask hosting)

| Variable | Purpose |
|---|---|
| `VELANIX_SECRET_KEY` | **Required** — stable random string (sessions/CSRF across restarts and workers) |
| `VELANIX_ADMIN_PASSWORD` / `VELANIX_ADMIN_USER` | Admin login (admin is disabled if the password is unset) |
| `VELANIX_CRM_WEBHOOK` | Optional CRM webhook URL |
| `VELANIX_INSTANCE_DIR` | Optional location of DB + uploads (use a persistent volume) |

Run with e.g. `gunicorn -w 3 app:app` behind HTTPS, on EU hosting (the privacy notice says data stays in the EU).

## Before launch

- Replace every `[bracketed]` placeholder in `content/site.py` (legal entity, address, register no., VAT ID, phone, team names).
- Review the "Representative engagements" on the homepage — they're labelled *Illustrative*; swap in real, approved case studies when available.
- Have the privacy notice/imprint checked by your Austrian advisor; confirm lead times and response-time commitments.
