"""Site-wide settings and editable business details.

Everything in [square brackets] is a placeholder to replace before launch.
"""

SITE = {
    "name": "Velanix Sourcing",
    "legal_name": "[Velanix Sourcing GmbH]",
    "email": "rfq@velanix-sourcing.com",
    "phone": "+43 [000 000 000]",
    "address_eu": "[Street 1], [1010 Vienna], Austria",
    "address_in": "[Office address], Coimbatore, Tamil Nadu, India",
    "company_register": "[FN 000000x]",
    "vat_id": "[ATU00000000]",
    "domain": "https://www.velanix-sourcing.com",
    # Set to False to remove the Magna reference from the About page.
    "show_magna": True,
}

# Team shown on the About page. Replace names/bios before launch.
TEAM = [
    {
        "name": "[Founder Name]",
        "initials": "FN",
        "role": {"en": "Founder & Managing Director", "de": "Gründer & Geschäftsführer"},
        "bio": {
            "en": "Procurement and supplier-development background at Magna, one of the world's largest "
                  "automotive suppliers. Has qualified and managed component suppliers for series production "
                  "under IATF 16949 and PPAP requirements.",
            "de": "Einkaufs- und Lieferantenentwicklungs-Hintergrund bei Magna, einem der weltweit größten "
                  "Automobilzulieferer. Erfahrung in der Qualifizierung und Steuerung von Komponentenlieferanten "
                  "für die Serienfertigung nach IATF 16949 und PPAP.",
        },
        # Used instead of `bio` when SITE["show_magna"] is False.
        "bio_alt": {
            "en": "Procurement and supplier-development background at a global tier-1 automotive supplier. Has "
                  "qualified and managed component suppliers for series production under IATF 16949 and PPAP.",
            "de": "Einkaufs- und Lieferantenentwicklungs-Hintergrund bei einem globalen Tier-1-Automobilzulieferer. "
                  "Erfahrung in der Qualifizierung und Steuerung von Serienlieferanten nach IATF 16949 und PPAP.",
        },
        "magna": True,
        "location": {"en": "Austria", "de": "Österreich"},
    },
    {
        "name": "[Name]",
        "initials": "IN",
        "role": {"en": "Head of Supplier Network, India", "de": "Leitung Lieferantennetzwerk, Indien"},
        "bio": {
            "en": "Based in Coimbatore. Runs supplier audits, sample inspections and production follow-up "
                  "across the Tamil Nadu clusters and partner regions.",
            "de": "Sitz in Coimbatore. Verantwortlich für Lieferantenaudits, Musterprüfungen und "
                  "Produktionsverfolgung in den Clustern in Tamil Nadu und Partnerregionen.",
        },
        "magna": False,
        "location": {"en": "Coimbatore, India", "de": "Coimbatore, Indien"},
    },
    {
        "name": "[Name]",
        "initials": "QA",
        "role": {"en": "Quality & Compliance Lead", "de": "Leitung Qualität & Compliance"},
        "bio": {
            "en": "Owns inspection plans, first-article reviews and compliance documentation "
                  "(CE, REACH/RoHS, EN 10204, PPAP) for every programme.",
            "de": "Verantwortet Prüfpläne, Erstmusterprüfungen und Compliance-Dokumentation "
                  "(CE, REACH/RoHS, EN 10204, PPAP) für jedes Projekt.",
        },
        "magna": False,
        "location": {"en": "Austria / India", "de": "Österreich / Indien"},
    },
]

# Delivery / company countries: code -> (English, German)
COUNTRIES = [
    ("AT", "Austria", "Österreich"), ("DE", "Germany", "Deutschland"), ("CH", "Switzerland", "Schweiz"),
    ("IT", "Italy", "Italien"), ("FR", "France", "Frankreich"), ("NL", "Netherlands", "Niederlande"),
    ("BE", "Belgium", "Belgien"), ("LU", "Luxembourg", "Luxemburg"), ("PL", "Poland", "Polen"),
    ("CZ", "Czechia", "Tschechien"), ("SK", "Slovakia", "Slowakei"), ("HU", "Hungary", "Ungarn"),
    ("SI", "Slovenia", "Slowenien"), ("HR", "Croatia", "Kroatien"), ("RO", "Romania", "Rumänien"),
    ("BG", "Bulgaria", "Bulgarien"), ("GR", "Greece", "Griechenland"), ("ES", "Spain", "Spanien"),
    ("PT", "Portugal", "Portugal"), ("IE", "Ireland", "Irland"), ("DK", "Denmark", "Dänemark"),
    ("SE", "Sweden", "Schweden"), ("FI", "Finland", "Finnland"), ("EE", "Estonia", "Estland"),
    ("LV", "Latvia", "Lettland"), ("LT", "Lithuania", "Litauen"), ("CY", "Cyprus", "Zypern"),
    ("MT", "Malta", "Malta"), ("NO", "Norway", "Norwegen"), ("GB", "United Kingdom", "Vereinigtes Königreich"),
    ("IN", "India", "Indien"), ("OTHER", "Other", "Andere"),
]

CURRENCIES = ["EUR", "USD", "CHF", "GBP", "INR"]
INCOTERMS = ["EXW", "FCA", "FOB", "CIF", "CPT", "DAP", "DDP"]
