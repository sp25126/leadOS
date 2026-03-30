import csv, io, json, os
from typing import Optional
import openpyxl
import xlrd

REQUIRED_FIELD_ALIASES = {
    "name": ["name", "company_name", "companyname", "business_name",
             "businessname", "company", "business"],
    "phone": ["phone", "mobile", "whatsapp", "contact", "phonenumber",
              "phone_number", "mobile_number", "wa"],
    "email": ["email", "email_address", "emailaddress", "mail"],
    "website": ["website", "url", "domain", "web", "site"],
    "address": ["address", "location", "city", "area", "place"],
}

def normalize_headers(headers: list[str]) -> dict[str, str]:
    """
    Returns mapping: canonical_field -> actual_header_in_file
    """
    mapping = {}
    lower_headers = {h.lower().replace(" ", "").replace("_", ""): h for h in headers}
    for canonical, aliases in REQUIRED_FIELD_ALIASES.items():
        for alias in aliases:
            clean_alias = alias.lower().replace("_", "").replace(" ", "")
            if clean_alias in lower_headers:
                mapping[canonical] = lower_headers[clean_alias]
                break
    return mapping


def parse_row(row: dict, mapping: dict[str, str]) -> dict:
    """Map a raw file row to a normalized lead dict."""
    def get(canonical):
        col = mapping.get(canonical)
        return str(row.get(col, "") or "").strip()

    name = get("name")
    if not name:
        return None  # skip rows with no business name

    phone = get("phone")
    # Normalize Indian phone numbers
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10 and digits[0] in "6789":
        phone = f"+91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        phone = f"+{digits}"
    elif len(digits) >= 7:
        phone = f"+{digits}"
    else:
        phone = ""

    email = get("email").lower()
    if email and "@" not in email:
        email = ""

    website = get("website")
    if website and not website.startswith("http"):
        website = f"https://{website}"

    return {
        "name": name,
        "phone": phone,
        "email": email,
        "website": website,
        "has_website": bool(website),
        "address": get("address"),
        "score": None,   # will be scored if Gemini scoring enabled
        "priority": "medium",
        "source": "user_upload",
        "pain_points": "",
        "reason": "",
        "tech_hints": "",
        "social_media": "",
        "merged_sources": "user_upload",
    }


def import_csv(content: bytes) -> list[dict]:
    text = content.decode("utf-8-sig")  # handles BOM
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    mapping = normalize_headers(list(headers))
    leads = []
    for row in reader:
        parsed = parse_row(dict(row), mapping)
        if parsed:
            leads.append(parsed)
    return leads


def import_xlsx(content: bytes) -> list[dict]:
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h or "").strip() for h in rows[0]]
    mapping = normalize_headers(headers)
    leads = []
    for row in rows[1:]:
        row_dict = {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
        parsed = parse_row(row_dict, mapping)
        if parsed:
            leads.append(parsed)
    return leads


def import_xls(content: bytes) -> list[dict]:
    wb = xlrd.open_workbook(file_contents=content)
    ws = wb.sheet_by_index(0)
    headers = [str(ws.cell_value(0, c)).strip() for c in range(ws.ncols)]
    mapping = normalize_headers(headers)
    leads = []
    for r in range(1, ws.nrows):
        row_dict = {headers[c]: ws.cell_value(r, c) for c in range(ws.ncols)}
        parsed = parse_row(row_dict, mapping)
        if parsed:
            leads.append(parsed)
    return leads


def import_json(content: bytes) -> list[dict]:
    data = json.loads(content.decode("utf-8"))
    if isinstance(data, dict):
        data = data.get("leads") or data.get("data") or list(data.values())
    if not isinstance(data, list):
        raise ValueError("JSON must be an array of lead objects or {leads: [...]}")
    headers = list(data[0].keys()) if data else []
    mapping = normalize_headers(headers)
    leads = []
    for row in data:
        parsed = parse_row(row, mapping)
        if parsed:
            leads.append(parsed)
    return leads


def import_file(filename: str, content: bytes) -> list[dict]:
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".csv":
        return import_csv(content)
    elif ext == ".xlsx":
        return import_xlsx(content)
    elif ext == ".xls":
        return import_xls(content)
    elif ext == ".json":
        return import_json(content)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .csv .xlsx .xls .json")
