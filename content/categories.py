"""Product categories and their category-specific specification fields.

Every user-facing string is a {"en": ..., "de": ...} dict (or a list per language).
Field kinds: text, number, select, radio (single chip), multi (multiple chips), textarea.
Submitted values are stored under spec_json in the leads table using the field `name`.
"""


def L(en, de):
    return {"en": en, "de": de}


def opts(*triples):
    return [{"value": v, "label": L(en, de)} for v, en, de in triples]


def field(name, kind, label, required=False, options=None, ph=None, half=False, hint=None):
    return {
        "name": name,
        "kind": kind,
        "label": label,
        "required": required,
        "options": options or [],
        "ph": ph,
        "half": half,
        "hint": hint,
    }


CATEGORIES = [
    # ------------------------------------------------------------------ valves
    {
        "slug": "industrial-valves",
        "hs": "HS 8481",
        "icon": "valve",
        "name": L("Industrial valves", "Industriearmaturen"),
        "short": L("Ball, gate, globe, butterfly and check valves to EN and API standards.",
                   "Kugelhähne, Schieber, Ventile, Klappen und Rückschlagarmaturen nach EN- und API-Normen."),
        "intro": L(
            "Coimbatore and Gujarat host some of India's most established valve foundries and machining shops, "
            "many already exporting to European distributors and EPC contractors. We source complete valves and "
            "valve components — bodies, bonnets, balls, stems — with pressure testing and material traceability "
            "built into the order.",
            "Coimbatore und Gujarat beherbergen einige der etabliertesten Armaturengießereien und "
            "Bearbeitungsbetriebe Indiens, viele davon mit Exporterfahrung für europäische Händler und "
            "EPC-Kontraktoren. Wir beschaffen komplette Armaturen und Komponenten — Gehäuse, Oberteile, Kugeln, "
            "Spindeln — mit Druckprüfung und Materialrückverfolgbarkeit als fester Bestandteil des Auftrags."),
        "processes": L(["Investment & sand casting", "Forged bodies", "CNC machining", "Hydrostatic & pneumatic testing", "Assembly & painting"],
                       ["Fein- & Sandguss", "Geschmiedete Gehäuse", "CNC-Bearbeitung", "Hydrostatische & pneumatische Prüfung", "Montage & Lackierung"]),
        "materials": L(["Carbon steel (WCB, A105)", "Stainless (CF8, CF8M, 316)", "Duplex / super duplex", "Ductile iron", "Bronze"],
                       ["C-Stahl (WCB, A105)", "Edelstahl (CF8, CF8M, 316)", "Duplex / Super-Duplex", "Sphäroguss", "Bronze"]),
        "standards": ["PED 2014/68/EU", "EN 12266", "API 598", "API 6D", "ATEX", "EN 10204 3.1"],
        "clusters": ["Coimbatore", "Ahmedabad", "Vadodara"],
        "lead_sample": L("4–8 weeks", "4–8 Wochen"),
        "lead_series": L("8–14 weeks", "8–14 Wochen"),
        "unit": "pcs",
        "fields": [
            field("valve_type", "radio", L("Valve type", "Armaturentyp"), True, opts(
                ("ball", "Ball", "Kugelhahn"), ("gate", "Gate", "Schieber"), ("globe", "Globe", "Ventil"),
                ("butterfly", "Butterfly", "Klappe"), ("check", "Check", "Rückschlag"), ("plug", "Plug", "Küken"),
                ("needle", "Needle / instrument", "Nadel / Instrument"), ("control", "Control", "Regelarmatur"),
                ("component", "Components only", "Nur Komponenten"))),
            field("size", "text", L("Nominal size(s)", "Nennweite(n)"), True, ph=L("e.g. DN50–DN200 or 2\"–8\"", "z. B. DN50–DN200 oder 2\"–8\""), half=True),
            field("pressure_class", "select", L("Pressure rating", "Druckstufe"), True, opts(
                ("PN10", "PN10", "PN10"), ("PN16", "PN16", "PN16"), ("PN25", "PN25", "PN25"), ("PN40", "PN40", "PN40"),
                ("PN63+", "PN63 and above", "PN63 und höher"), ("150", "ASME Class 150", "ASME Class 150"),
                ("300", "ASME Class 300", "ASME Class 300"), ("600+", "ASME Class 600+", "ASME Class 600+")), half=True),
            field("body_material", "select", L("Body material", "Gehäusewerkstoff"), True, opts(
                ("wcb", "Carbon steel (WCB / A105)", "C-Stahl (WCB / A105)"), ("lcc", "Low-temp carbon steel (LCC / LF2)", "Kaltzäher Stahl (LCC / LF2)"),
                ("cf8m", "Stainless CF8M / 316", "Edelstahl CF8M / 316"), ("cf8", "Stainless CF8 / 304", "Edelstahl CF8 / 304"),
                ("duplex", "Duplex / super duplex", "Duplex / Super-Duplex"), ("ductile", "Ductile / cast iron", "Sphäro- / Grauguss"),
                ("bronze", "Bronze / brass", "Bronze / Messing"), ("other", "Other (specify in notes)", "Andere (in Notizen angeben)")), half=True),
            field("end_connection", "select", L("End connection", "Anschlussart"), False, opts(
                ("flanged_en", "Flanged EN 1092-1", "Flansch EN 1092-1"), ("flanged_asme", "Flanged ASME B16.5", "Flansch ASME B16.5"),
                ("threaded", "Threaded (BSP / NPT)", "Gewinde (BSP / NPT)"), ("bw", "Butt-weld", "Schweißende (BW)"),
                ("sw", "Socket-weld", "Schweißmuffe (SW)"), ("wafer", "Wafer / lug", "Zwischenflansch / Lug")), half=True),
            field("actuation", "radio", L("Actuation", "Betätigung"), False, opts(
                ("manual", "Lever / handwheel", "Hebel / Handrad"), ("gear", "Gearbox", "Getriebe"),
                ("pneumatic", "Pneumatic", "Pneumatisch"), ("electric", "Electric", "Elektrisch"), ("bare", "Bare shaft", "Freies Wellenende"))),
            field("medium", "text", L("Medium & temperature range", "Medium & Temperaturbereich"), False, ph=L("e.g. water / steam, -20 to +180 °C", "z. B. Wasser / Dampf, -20 bis +180 °C")),
            field("testing", "multi", L("Testing & certification", "Prüfung & Zertifizierung"), False, opts(
                ("en12266", "EN 12266-1 pressure test", "Druckprüfung EN 12266-1"), ("api598", "API 598", "API 598"),
                ("ped", "PED CE marking", "PED CE-Kennzeichnung"), ("atex", "ATEX", "ATEX"), ("fire_safe", "Fire-safe (API 607)", "Fire-safe (API 607)"),
                ("ta_luft", "TA-Luft / ISO 15848 fugitive emissions", "TA-Luft / ISO 15848 Emissionen"), ("witness", "Witnessed testing", "Abnahme mit Zeugenprüfung"))),
        ],
    },
    # --------------------------------------------------------- castings/forgings
    {
        "slug": "castings-forgings-machining",
        "hs": "HS 7326",
        "icon": "casting",
        "name": L("Castings, forgings & machined parts", "Guss-, Schmiede- & Drehteile"),
        "short": L("Ferrous and non-ferrous castings, forgings and CNC-machined components to print.",
                   "Eisen- und NE-Guss, Schmiedeteile und CNC-bearbeitete Komponenten nach Zeichnung."),
        "intro": L(
            "Coimbatore's foundry belt is one of the densest in Asia, supplying pump, valve, textile-machinery and "
            "automotive OEMs for decades. We source build-to-print parts from raw casting or forging through "
            "machining, heat treatment and surface finishing — with the inspection documentation European "
            "goods-in teams expect.",
            "Der Gießerei-Gürtel um Coimbatore ist einer der dichtesten Asiens und beliefert seit Jahrzehnten "
            "Pumpen-, Armaturen-, Textilmaschinen- und Automobilhersteller. Wir beschaffen Teile nach Zeichnung — "
            "vom Rohguss oder Schmiedeteil über Bearbeitung, Wärmebehandlung bis zur Oberflächenveredelung — mit "
            "der Prüfdokumentation, die europäische Wareneingangsprüfungen erwarten."),
        "processes": L(["Green-sand & no-bake casting", "Investment casting", "Pressure die casting (Al)", "Closed & open-die forging", "3/4/5-axis CNC machining", "Heat treatment & coating"],
                       ["Grünsand- & No-Bake-Guss", "Feinguss", "Aluminium-Druckguss", "Gesenk- & Freiformschmieden", "3/4/5-Achs-CNC-Bearbeitung", "Wärmebehandlung & Beschichtung"]),
        "materials": L(["Grey & ductile iron (EN-GJL / EN-GJS)", "Carbon & alloy steel", "Stainless steel", "Aluminium alloys", "Bronze & brass"],
                       ["Grau- & Sphäroguss (EN-GJL / EN-GJS)", "C- & legierter Stahl", "Edelstahl", "Aluminiumlegierungen", "Bronze & Messing"]),
        "standards": ["ISO 9001", "IATF 16949", "EN 10204 3.1", "ISO 2768", "PPAP / FAI", "CMM reports"],
        "clusters": ["Coimbatore", "Rajkot", "Kolhapur", "Belagavi"],
        "lead_sample": L("5–10 weeks (incl. pattern / die)", "5–10 Wochen (inkl. Modell / Gesenk)"),
        "lead_series": L("6–12 weeks", "6–12 Wochen"),
        "unit": "pcs",
        "fields": [
            field("process", "multi", L("Manufacturing process", "Fertigungsverfahren"), True, opts(
                ("sand", "Sand casting", "Sandguss"), ("investment", "Investment casting", "Feinguss"),
                ("die", "Die casting", "Druckguss"), ("closed_forging", "Closed-die forging", "Gesenkschmieden"),
                ("open_forging", "Open-die forging", "Freiformschmieden"), ("cnc", "CNC machining", "CNC-Bearbeitung"),
                ("fabrication", "Fabrication / welding", "Schweißkonstruktion"))),
            field("material_grade", "text", L("Material grade", "Werkstoffsorte"), True, ph=L("e.g. EN-GJS-400-15, 42CrMo4, 1.4408", "z. B. EN-GJS-400-15, 42CrMo4, 1.4408"), half=True),
            field("part_weight", "text", L("Finished weight per part (kg)", "Fertiggewicht je Teil (kg)"), False, ph=L("e.g. 3.2", "z. B. 3,2"), half=True),
            field("envelope", "text", L("Approx. dimensions (mm)", "Ca. Abmessungen (mm)"), False, ph=L("L × W × H", "L × B × H"), half=True),
            field("tolerances", "text", L("Critical tolerances", "Kritische Toleranzen"), False, ph=L("e.g. ISO 2768-mK, bores H7, Ra 1.6", "z. B. ISO 2768-mK, Bohrungen H7, Ra 1,6"), half=True),
            field("heat_treatment", "select", L("Heat treatment", "Wärmebehandlung"), False, opts(
                ("none", "None", "Keine"), ("normalising", "Normalising / annealing", "Normalglühen / Weichglühen"),
                ("qt", "Quench & temper", "Vergüten"), ("case", "Case hardening / induction", "Einsatz- / Induktionshärten"),
                ("solution", "Solution annealing", "Lösungsglühen"), ("per_drawing", "As per drawing", "Laut Zeichnung")), half=True),
            field("surface", "text", L("Surface treatment / coating", "Oberflächenbehandlung / Beschichtung"), False, ph=L("e.g. shot blast + primer, zinc-nickel, black oxide", "z. B. Strahlen + Grundierung, Zink-Nickel, brüniert"), half=True),
            field("inspection_docs", "multi", L("Inspection documentation", "Prüfdokumentation"), False, opts(
                ("3.1", "EN 10204 3.1", "EN 10204 3.1"), ("3.2", "EN 10204 3.2", "EN 10204 3.2"), ("fai", "First article (FAI)", "Erstmusterprüfbericht (EMPB)"),
                ("ppap", "PPAP", "PPAP"), ("cmm", "CMM report", "KMG-Protokoll"), ("ndt", "NDT (UT / MPI / X-ray)", "ZfP (UT / MT / RT)"))),
        ],
    },
    # ----------------------------------------------------------------- pumps
    {
        "slug": "pumps-compressors-machinery",
        "hs": "HS 8414",
        "icon": "pump",
        "name": L("Pumps, compressors & machinery parts", "Pumpen, Kompressoren & Maschinenteile"),
        "short": L("Complete pump and compressor units, spares and machinery components.",
                   "Komplette Pumpen- und Kompressoreinheiten, Ersatzteile und Maschinenkomponenten."),
        "intro": L(
            "Coimbatore is widely known as India's pump city — a large share of the country's pumps and motors "
            "are built within a few hours of it. We source complete units for OEM and private-label programmes as "
            "well as impellers, casings, shafts and machined machinery parts to your drawings.",
            "Coimbatore gilt als Indiens „Pump City“ — ein großer Teil der Pumpen und Motoren des Landes wird "
            "im Umkreis weniger Fahrstunden gebaut. Wir beschaffen komplette Einheiten für OEM- und "
            "Private-Label-Programme sowie Laufräder, Gehäuse, Wellen und bearbeitete Maschinenteile nach Ihrer Zeichnung."),
        "processes": L(["Casting & machining of casings and impellers", "Dynamic balancing", "Motor winding & assembly", "Performance testing", "Painting & packing"],
                       ["Guss & Bearbeitung von Gehäusen und Laufrädern", "Dynamisches Wuchten", "Motorwicklung & Montage", "Leistungsprüfung", "Lackierung & Verpackung"]),
        "materials": L(["Cast iron & ductile iron", "Stainless steel (304 / 316 / duplex)", "Bronze impellers", "Engineering plastics"],
                       ["Grau- & Sphäroguss", "Edelstahl (304 / 316 / Duplex)", "Bronze-Laufräder", "Technische Kunststoffe"]),
        "standards": ["CE Machinery Directive", "ISO 9906", "ISO 5199", "IE3 / IE4 (IEC 60034-30-1)", "ATEX", "ISO 9001"],
        "clusters": ["Coimbatore", "Ahmedabad", "Pune"],
        "lead_sample": L("4–8 weeks", "4–8 Wochen"),
        "lead_series": L("6–12 weeks", "6–12 Wochen"),
        "unit": "pcs",
        "fields": [
            field("product_type", "radio", L("Product type", "Produkttyp"), True, opts(
                ("centrifugal", "Centrifugal pump", "Kreiselpumpe"), ("submersible", "Submersible / borehole pump", "Tauch- / Brunnenpumpe"),
                ("pd", "Positive-displacement pump", "Verdrängerpumpe"), ("compressor", "Air compressor / blower", "Kompressor / Gebläse"),
                ("spares", "Spares: impellers, casings, shafts", "Ersatzteile: Laufräder, Gehäuse, Wellen"), ("machinery", "Other machinery parts", "Sonstige Maschinenteile"))),
            field("scope", "radio", L("Supply scope", "Lieferumfang"), True, opts(
                ("complete", "Complete unit", "Komplette Einheit"), ("bare_shaft", "Bare-shaft / without motor", "Ohne Motor"),
                ("component", "Component to print", "Komponente nach Zeichnung"), ("private_label", "Private label", "Private Label"))),
            field("duty", "text", L("Duty point", "Betriebspunkt"), False, ph=L("e.g. Q = 60 m³/h, H = 45 m / 8 bar, 200 m³/min", "z. B. Q = 60 m³/h, H = 45 m / 8 bar"), half=True),
            field("power", "text", L("Motor power (kW) / voltage", "Motorleistung (kW) / Spannung"), False, ph=L("e.g. 7.5 kW, 400 V / 50 Hz", "z. B. 7,5 kW, 400 V / 50 Hz"), half=True),
            field("efficiency", "select", L("Motor efficiency class", "Motor-Effizienzklasse"), False, opts(
                ("ie3", "IE3", "IE3"), ("ie4", "IE4", "IE4"), ("na", "Not applicable", "Nicht zutreffend")), half=True),
            field("moc", "text", L("Material of construction", "Werkstoffe"), False, ph=L("e.g. casing GJL-250, impeller CF8M", "z. B. Gehäuse GJL-250, Laufrad CF8M"), half=True),
            field("standards", "multi", L("Standards & approvals", "Normen & Zulassungen"), False, opts(
                ("ce", "CE — Machinery Directive / Regulation", "CE — Maschinenrichtlinie / -verordnung"), ("iso9906", "ISO 9906 performance test", "Leistungsprüfung ISO 9906"),
                ("iso5199", "ISO 5199", "ISO 5199"), ("atex", "ATEX", "ATEX"), ("wras", "Drinking-water approval (e.g. KTW / WRAS)", "Trinkwasserzulassung (z. B. KTW / WRAS)"))),
        ],
    },
    # ------------------------------------------------------------- automotive
    {
        "slug": "automotive-tractor-components",
        "hs": "HS 8708",
        "icon": "auto",
        "name": L("Automotive & tractor components", "Automobil- & Traktorkomponenten"),
        "short": L("Metallic and plastic components for passenger, commercial, agricultural and off-highway vehicles.",
                   "Metall- und Kunststoffkomponenten für Pkw, Nutzfahrzeuge, Landtechnik und Off-Highway."),
        "intro": L(
            "Tamil Nadu is one of India's largest automotive hubs, and Madurai and Hosur are home to long-established "
            "tier-1 and tier-2 component makers. Indian suppliers already build for global tractor and "
            "commercial-vehicle platforms. We run sourcing the way an OEM purchasing team would: IATF-grade "
            "suppliers, APQP milestones and PPAP submission before start of production.",
            "Tamil Nadu ist einer der größten Automobilstandorte Indiens; in Madurai und Hosur sitzen etablierte "
            "Tier-1- und Tier-2-Zulieferer. Indische Lieferanten fertigen bereits für globale Traktor- und "
            "Nutzfahrzeugplattformen. Wir steuern die Beschaffung so, wie es ein OEM-Einkauf tun würde: "
            "IATF-zertifizierte Lieferanten, APQP-Meilensteine und PPAP-Freigabe vor Serienstart."),
        "processes": L(["Hot & cold forging", "Ferrous & aluminium casting", "Precision machining", "Sheet-metal stamping", "Plastic injection moulding", "Rubber moulding & sub-assembly"],
                       ["Warm- & Kaltumformung", "Eisen- & Aluminiumguss", "Präzisionsbearbeitung", "Blechumformung / Stanzen", "Kunststoffspritzguss", "Gummiformteile & Baugruppen"]),
        "materials": L(["Forging & case-hardening steels", "Ductile iron", "Aluminium alloys", "PA6 / PA66-GF, PP, POM", "EPDM / NBR"],
                       ["Vergütungs- & Einsatzstähle", "Sphäroguss", "Aluminiumlegierungen", "PA6 / PA66-GF, PP, POM", "EPDM / NBR"]),
        "standards": ["IATF 16949", "PPAP (AIAG / VDA 2)", "APQP", "IMDS", "REACH", "ISO 14001"],
        "clusters": ["Madurai", "Chennai", "Hosur", "Coimbatore", "Pune"],
        "lead_sample": L("6–12 weeks (incl. tooling)", "6–12 Wochen (inkl. Werkzeug)"),
        "lead_series": L("8–14 weeks", "8–14 Wochen"),
        "unit": "pcs",
        "fields": [
            field("application", "radio", L("Vehicle application", "Fahrzeuganwendung"), True, opts(
                ("tractor", "Tractor / agricultural", "Traktor / Landtechnik"), ("cv", "Commercial vehicle", "Nutzfahrzeug"),
                ("pc", "Passenger car", "Pkw"), ("offhighway", "Off-highway / construction", "Off-Highway / Bau"),
                ("2w", "Two-wheeler", "Zweirad"), ("aftermarket", "Aftermarket / spare parts", "Aftermarket / Ersatzteile"))),
            field("material_family", "radio", L("Material family", "Werkstoffgruppe"), True, opts(
                ("metal", "Metallic", "Metallisch"), ("plastic", "Plastic", "Kunststoff"), ("rubber", "Rubber / elastomer", "Gummi / Elastomer"),
                ("assembly", "Assembly / mixed", "Baugruppe / gemischt"))),
            field("process", "multi", L("Process", "Verfahren"), False, opts(
                ("forging", "Forging", "Schmieden"), ("casting", "Casting", "Gießen"), ("machining", "Machining", "Zerspanung"),
                ("stamping", "Stamping", "Stanzen"), ("injection", "Injection moulding", "Spritzguss"), ("rubber", "Rubber moulding", "Gummiformen"))),
            field("part_number", "text", L("Part number / OE reference", "Teilenummer / OE-Referenz"), False, ph=L("Optional", "Optional"), half=True),
            field("drawing_rev", "text", L("Drawing revision", "Zeichnungsindex"), False, ph=L("e.g. Rev. C", "z. B. Index C"), half=True),
            field("ppap_level", "select", L("PPAP submission level", "PPAP-Vorlagestufe"), False, opts(
                ("1", "Level 1", "Stufe 1"), ("2", "Level 2", "Stufe 2"), ("3", "Level 3 (default)", "Stufe 3 (Standard)"),
                ("4", "Level 4", "Stufe 4"), ("5", "Level 5", "Stufe 5"), ("vda", "VDA 2 PPA", "VDA 2 PPF"), ("none", "Not required", "Nicht erforderlich")), half=True),
            field("iatf", "select", L("IATF 16949 supplier required?", "IATF-16949-Lieferant erforderlich?"), False, opts(
                ("yes", "Yes, mandatory", "Ja, zwingend"), ("preferred", "Preferred", "Bevorzugt"), ("no", "No", "Nein")), half=True),
        ],
    },
    # ------------------------------------------------------------------ cable
    {
        "slug": "electrical-cable-wiring",
        "hs": "HS 8544 / 8536",
        "icon": "cable",
        "name": L("Electrical cable & wiring", "Elektrokabel & Verdrahtung"),
        "short": L("Power, control and flexible cables, wiring harnesses and low-voltage switching parts.",
                   "Energie-, Steuer- und flexible Leitungen, Kabelbäume und Niederspannungs-Schaltkomponenten."),
        "intro": L(
            "India's cable industry supplies utilities, OEMs and distributors worldwide from large integrated plants "
            "in western India and specialised harness makers in the south. We focus on constructions that meet "
            "harmonised European standards and CPR classification, with type-test reports you can hand to your "
            "certification body.",
            "Die indische Kabelindustrie beliefert Energieversorger, OEMs und Händler weltweit — aus großen "
            "integrierten Werken in Westindien und spezialisierten Kabelbaumherstellern im Süden. Unser Fokus "
            "liegt auf Aufbauten nach harmonisierten europäischen Normen und CPR-Klassifizierung, mit "
            "Typprüfberichten, die Sie Ihrer Zertifizierungsstelle vorlegen können."),
        "processes": L(["Wire drawing & stranding", "Extrusion (PVC, XLPE, LSZH)", "Armouring & sheathing", "Harness cutting, crimping & assembly", "Routine & type testing"],
                       ["Drahtziehen & Verseilen", "Extrusion (PVC, VPE, halogenfrei)", "Bewehrung & Mantel", "Kabelbaum: Ablängen, Crimpen, Montage", "Stück- & Typprüfung"]),
        "materials": L(["Copper & aluminium conductors", "PVC, XLPE, LSZH, rubber", "Tinned copper", "Connectors & terminals"],
                       ["Kupfer- & Aluminiumleiter", "PVC, VPE, halogenfrei, Gummi", "Verzinntes Kupfer", "Steckverbinder & Kontakte"]),
        "standards": ["IEC 60502", "HD 603 / HD 604", "EN 50525", "CPR EN 50575", "VDE / HAR", "RoHS / REACH"],
        "clusters": ["Vadodara", "Daman & Silvassa", "Chennai", "Coimbatore"],
        "lead_sample": L("3–6 weeks", "3–6 Wochen"),
        "lead_series": L("6–10 weeks", "6–10 Wochen"),
        "unit": "m",
        "fields": [
            field("product_type", "radio", L("Product type", "Produkttyp"), True, opts(
                ("lv_power", "LV power cable", "NS-Energiekabel"), ("mv_power", "MV power cable", "MS-Energiekabel"),
                ("control", "Control / instrumentation", "Steuer- / Instrumentenkabel"), ("flexible", "Flexible cords", "Flexible Leitungen"),
                ("building", "Building wire", "Installationsleitung"), ("harness", "Wiring harness", "Kabelbaum"),
                ("switching", "Switching / connection parts (8536)", "Schalt- / Verbindungsteile (8536)"))),
            field("conductor", "radio", L("Conductor", "Leiter"), False, opts(
                ("cu", "Copper", "Kupfer"), ("cu_tinned", "Tinned copper", "Verzinntes Kupfer"), ("al", "Aluminium", "Aluminium"))),
            field("construction", "text", L("Cores × cross-section", "Adern × Querschnitt"), False, ph=L("e.g. 4G2.5 mm², 3×240+120 mm²", "z. B. 4G2,5 mm², 3×240+120 mm²"), half=True),
            field("voltage", "text", L("Rated voltage", "Nennspannung"), False, ph=L("e.g. 0.6/1 kV, 300/500 V", "z. B. 0,6/1 kV, 300/500 V"), half=True),
            field("insulation", "select", L("Insulation / sheath", "Isolierung / Mantel"), False, opts(
                ("pvc", "PVC", "PVC"), ("xlpe", "XLPE", "VPE (XLPE)"), ("lszh", "LSZH / halogen-free", "Halogenfrei (LSZH)"),
                ("rubber", "Rubber (EPR / CR)", "Gummi (EPR / CR)"), ("pur", "PUR", "PUR"), ("other", "Other", "Andere")), half=True),
            field("cpr_class", "select", L("CPR fire class (EN 50575)", "CPR-Brandklasse (EN 50575)"), False, opts(
                ("na", "Not applicable", "Nicht zutreffend"), ("eca", "Eca", "Eca"), ("dca", "Dca", "Dca"),
                ("cca", "Cca", "Cca"), ("b2ca", "B2ca", "B2ca")), half=True),
            field("standards", "multi", L("Standards & marks", "Normen & Zeichen"), False, opts(
                ("iec60502", "IEC 60502", "IEC 60502"), ("hd603", "HD 603 / HD 604", "HD 603 / HD 604"), ("en50525", "EN 50525", "EN 50525"),
                ("vde", "VDE / HAR mark", "VDE- / HAR-Zeichen"), ("rohs", "RoHS / REACH", "RoHS / REACH"), ("ul", "UL (export)", "UL (Export)"))),
        ],
    },
    # --------------------------------------------------------------- textiles
    {
        "slug": "home-textiles-carpets",
        "hs": "HS 5703 / 6302",
        "icon": "textile",
        "name": L("Home textiles & carpets", "Heimtextilien & Teppiche"),
        "short": L("Bed, bath and table linen, hand-made and machine-made rugs for retail and hospitality.",
                   "Bett-, Bad- und Tischwäsche, handgefertigte und maschinelle Teppiche für Handel und Hotellerie."),
        "intro": L(
            "Tamil Nadu's Karur and Madurai clusters are major exporters of cotton home textiles to Europe, while "
            "Panipat and Bhadohi–Mirzapur lead in rugs and carpets. We match your range to mills and weaving "
            "units with the social-compliance and chemical-safety certifications European retailers require.",
            "Die Cluster Karur und Madurai in Tamil Nadu sind bedeutende Exporteure von Baumwoll-Heimtextilien "
            "nach Europa; Panipat und Bhadohi–Mirzapur führen bei Teppichen. Wir bringen Ihr Sortiment mit "
            "Webereien und Konfektionären zusammen, die über die von europäischen Händlern geforderten "
            "Sozial- und Chemikaliensicherheits-Zertifizierungen verfügen."),
        "processes": L(["Weaving (air-jet, rapier, handloom)", "Dyeing, printing & finishing", "Cut & sew", "Hand-knotting & hand-tufting", "Flat-weave & machine-made rugs"],
                       ["Weben (Luftdüse, Greifer, Handwebstuhl)", "Färben, Drucken & Ausrüsten", "Zuschnitt & Konfektion", "Handknüpfen & Handtuften", "Flachgewebe & maschinelle Teppiche"]),
        "materials": L(["Cotton & organic cotton", "Linen", "Wool & jute", "Viscose / bamboo", "Recycled polyester"],
                       ["Baumwolle & Bio-Baumwolle", "Leinen", "Wolle & Jute", "Viskose / Bambus", "Recycling-Polyester"]),
        "standards": ["OEKO-TEX Standard 100", "GOTS", "GRS", "amfori BSCI", "GoodWeave", "REACH"],
        "clusters": ["Karur", "Madurai", "Panipat", "Bhadohi"],
        "lead_sample": L("2–5 weeks", "2–5 Wochen"),
        "lead_series": L("8–12 weeks", "8–12 Wochen"),
        "unit": "pcs",
        "fields": [
            field("product", "radio", L("Product", "Produkt"), True, opts(
                ("bed", "Bed linen", "Bettwäsche"), ("bath", "Towels / bath", "Frottier / Bad"), ("table", "Table & kitchen linen", "Tisch- & Küchenwäsche"),
                ("curtains", "Curtains & cushions", "Vorhänge & Kissen"), ("hand_knotted", "Hand-knotted rugs", "Handgeknüpfte Teppiche"),
                ("tufted", "Hand-tufted rugs", "Handgetuftete Teppiche"), ("flatweave", "Flat-weave / dhurries", "Flachgewebe / Dhurries"),
                ("machine_rug", "Machine-made rugs", "Maschinelle Teppiche"))),
            field("fibre", "multi", L("Fibre", "Faser"), True, opts(
                ("cotton", "Cotton", "Baumwolle"), ("organic", "Organic cotton", "Bio-Baumwolle"), ("linen", "Linen", "Leinen"),
                ("wool", "Wool", "Wolle"), ("jute", "Jute", "Jute"), ("viscose", "Viscose", "Viskose"), ("polyester", "Polyester / recycled", "Polyester / recycelt"))),
            field("spec", "text", L("Size / GSM / thread count", "Größe / Grammatur / Fadendichte"), False, ph=L("e.g. 135×200 cm, 200 TC percale; 500 GSM", "z. B. 135×200 cm, 200 TC Perkal; 500 g/m²"), half=True),
            field("construction", "text", L("Construction / pile", "Aufbau / Flor"), False, ph=L("e.g. 100 knots/in², 12 mm pile", "z. B. 100 Knoten/in², 12 mm Flor"), half=True),
            field("design", "radio", L("Design", "Design"), False, opts(
                ("own", "Our own designs", "Eigene Designs"), ("collection", "From supplier collection", "Aus Lieferantenkollektion"), ("develop", "Develop together", "Gemeinsame Entwicklung"))),
            field("packaging", "text", L("Packaging & labelling", "Verpackung & Etikettierung"), False, ph=L("e.g. retail-ready, EAN, care labels in DE/FR/IT", "z. B. verkaufsfertig, EAN, Pflegeetiketten DE/FR/IT")),
            field("certifications", "multi", L("Required certifications", "Erforderliche Zertifizierungen"), False, opts(
                ("oekotex", "OEKO-TEX Standard 100", "OEKO-TEX Standard 100"), ("gots", "GOTS", "GOTS"), ("grs", "GRS", "GRS"),
                ("bsci", "amfori BSCI", "amfori BSCI"), ("goodweave", "GoodWeave / child-labour free", "GoodWeave / ohne Kinderarbeit"), ("sedex", "SMETA / Sedex", "SMETA / Sedex"))),
        ],
    },
    # ---------------------------------------------------------------- medical
    {
        "slug": "medical-instruments-components",
        "hs": "HS 9018 / 9021",
        "icon": "medical",
        "name": L("Medical instruments & components", "Medizinische Instrumente & Komponenten"),
        "short": L("Reusable surgical instruments, precision components and OEM parts for medical devices.",
                   "Wiederverwendbare chirurgische Instrumente, Präzisionskomponenten und OEM-Teile für Medizinprodukte."),
        "intro": L(
            "India has a growing base of ISO 13485-certified manufacturers, from surgical-instrument makers to "
            "precision machining shops producing implant and device components. We work within your EU MDR "
            "framework: you remain the legal manufacturer, we qualify the supplier and manage the documentation "
            "your technical file needs.",
            "Indien verfügt über eine wachsende Basis ISO-13485-zertifizierter Hersteller — von "
            "Chirurgieinstrumenten bis zu Präzisionsbearbeitern für Implantat- und Gerätekomponenten. Wir arbeiten "
            "innerhalb Ihres EU-MDR-Rahmens: Sie bleiben rechtlicher Hersteller, wir qualifizieren den Lieferanten "
            "und steuern die Dokumentation, die Ihre technische Dokumentation benötigt."),
        "processes": L(["Precision forging & machining", "Swiss-type turning", "Electropolishing & passivation", "Laser marking (UDI)", "Cleanroom packaging (partner sites)"],
                       ["Präzisionsschmieden & -bearbeitung", "Langdrehen", "Elektropolieren & Passivieren", "Laserbeschriftung (UDI)", "Reinraumverpackung (Partnerstandorte)"]),
        "materials": L(["Surgical stainless (1.4021, 1.4034, 316L)", "Titanium Gr 2 / Gr 5 / Gr 23", "Cobalt-chrome", "PEEK & medical polymers"],
                       ["Chirurgischer Edelstahl (1.4021, 1.4034, 316L)", "Titan Gr 2 / Gr 5 / Gr 23", "Kobalt-Chrom", "PEEK & Medizinkunststoffe"]),
        "standards": ["ISO 13485", "EU MDR 2017/745", "ISO 10993", "ISO 7153-1", "ASTM F136", "UDI"],
        "clusters": ["Chennai", "Coimbatore", "Ahmedabad", "Vadodara"],
        "lead_sample": L("6–10 weeks", "6–10 Wochen"),
        "lead_series": L("8–16 weeks", "8–16 Wochen"),
        "unit": "pcs",
        "fields": [
            field("product_type", "radio", L("Product type", "Produkttyp"), True, opts(
                ("surgical", "Reusable surgical instruments", "Wiederverwendbare Chirurgieinstrumente"), ("ortho", "Orthopaedic / implant components", "Orthopädie- / Implantatkomponenten"),
                ("dental", "Dental instruments", "Dentalinstrumente"), ("oem", "Machined OEM components", "Bearbeitete OEM-Komponenten"),
                ("disposable", "Single-use devices", "Einmalprodukte"))),
            field("device_class", "select", L("EU MDR class of finished device", "MDR-Klasse des Endprodukts"), True, opts(
                ("component", "Component (not a device itself)", "Komponente (kein eigenes Produkt)"), ("I", "Class I", "Klasse I"),
                ("Ir", "Class Ir (reusable surgical)", "Klasse Ir (wiederverwendbar chirurgisch)"), ("Is", "Class Is / Im", "Klasse Is / Im"),
                ("IIa", "Class IIa", "Klasse IIa"), ("IIb", "Class IIb", "Klasse IIb"), ("III", "Class III", "Klasse III")), half=True),
            field("sterile", "select", L("Delivery condition", "Lieferzustand"), False, opts(
                ("non_sterile", "Non-sterile", "Unsteril"), ("sterile", "Sterile", "Steril"), ("cleaned", "Cleaned & packed, sterilised by us", "Gereinigt & verpackt, Sterilisation durch uns")), half=True),
            field("material", "text", L("Material", "Werkstoff"), False, ph=L("e.g. 1.4021, Ti-6Al-4V ELI (ASTM F136)", "z. B. 1.4021, Ti-6Al-4V ELI (ASTM F136)"), half=True),
            field("legal_manufacturer", "select", L("Legal manufacturer", "Rechtlicher Hersteller"), False, opts(
                ("buyer", "We are the legal manufacturer", "Wir sind rechtlicher Hersteller"), ("tbd", "To be discussed", "Zu klären")), half=True),
            field("docs", "multi", L("Documentation required", "Erforderliche Dokumentation"), False, opts(
                ("iso13485", "ISO 13485 certified supplier", "ISO-13485-zertifizierter Lieferant"), ("biocomp", "Biocompatibility (ISO 10993)", "Biokompatibilität (ISO 10993)"),
                ("material_certs", "Material certificates 3.1", "Materialzeugnisse 3.1"), ("udi", "UDI marking", "UDI-Kennzeichnung"),
                ("validation", "Process validation (IQ/OQ/PQ)", "Prozessvalidierung (IQ/OQ/PQ)"), ("tech_file", "Technical file support", "Unterstützung technische Dokumentation"))),
        ],
    },
]

CATEGORY_BY_SLUG = {c["slug"]: c for c in CATEGORIES}

# Common compliance checklist shown in the commercial step of every RFQ.
COMPLIANCE = opts(
    ("ce", "CE marking", "CE-Kennzeichnung"),
    ("reach", "REACH", "REACH"),
    ("rohs", "RoHS", "RoHS"),
    ("en10204", "EN 10204 material certificates", "Werkszeugnisse EN 10204"),
    ("iso9001", "ISO 9001 supplier", "ISO-9001-Lieferant"),
    ("ppap", "PPAP / first-article report", "PPAP / Erstmusterprüfbericht"),
    ("cbam", "CBAM emissions data", "CBAM-Emissionsdaten"),
    ("csddd", "Supply-chain due-diligence (LkSG / CSDDD)", "Lieferketten-Sorgfalt (LkSG / CSDDD)"),
    ("nda", "NDA before sharing drawings", "NDA vor Zeichnungsweitergabe"),
)

UNITS = opts(
    ("pcs", "pieces", "Stück"), ("sets", "sets", "Sätze"), ("m", "metres", "Meter"),
    ("kg", "kg", "kg"), ("t", "tonnes", "Tonnen"), ("m2", "m²", "m²"),
)

ORDER_TYPES = opts(
    ("prototype", "Prototype / samples only", "Prototyp / nur Muster"),
    ("pilot", "Pilot batch", "Vorserie"),
    ("series", "Series / annual contract", "Serie / Jahresvertrag"),
    ("spot", "One-off order", "Einmalauftrag"),
)

SOURCING_SITUATIONS = opts(
    ("second_source", "Second source for an existing part", "Zweitlieferant für bestehendes Teil"),
    ("replace", "Replace current supplier", "Aktuellen Lieferanten ersetzen"),
    ("new", "New part / new programme", "Neues Teil / neues Projekt"),
    ("cost", "Cost benchmark", "Kosten-Benchmark"),
)
