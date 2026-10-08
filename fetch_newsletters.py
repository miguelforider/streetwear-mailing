#!/usr/bin/env python3
"""
Streetwear Newsletter Fetcher & Archiver (Mail.tm API)
Descarga newsletters de Mail.tm, detecta la marca y su categoría
('Directos moto', 'Streetwear', 'Técnica') y las guarda con HTML íntegro.
"""

import json
import os
import random
import re
import shutil
import string
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = BASE_DIR / "archive"
INDEX_FILE = ARCHIVE_DIR / "index.json"
PROCESSED_FILE = ARCHIVE_DIR / "processed_ids.json"
ENV_FILE = BASE_DIR / ".env"
API_BASE = "https://api.mail.tm"

BRAND_MAP = {
    # Directos moto
    "alpinestars": ("Alpinestars", "Directos moto"),
    "bull-it": ("Bull-it", "Directos moto"),
    "bullit": ("Bull-it", "Directos moto"),
    "bull it": ("Bull-it", "Directos moto"),
    "dainese": ("Dainese", "Directos moto"),
    "deus": ("Deus Ex Machina", "Directos moto"),
    "deuscustoms": ("Deus Ex Machina", "Directos moto"),
    "deus ex machina": ("Deus Ex Machina", "Directos moto"),
    "fuel": ("Fuel Motorcycles", "Directos moto"),
    "fuelmotorcycles": ("Fuel Motorcycles", "Directos moto"),
    "fuel motorcycles": ("Fuel Motorcycles", "Directos moto"),
    "icon": ("Icon", "Directos moto"),
    "rideicon": ("Icon", "Directos moto"),
    "johndoe": ("John Doe", "Directos moto"),
    "john doe": ("John Doe", "Directos moto"),
    "john-doe": ("John Doe", "Directos moto"),
    "ridejohndoe": ("John Doe", "Directos moto"),
    "knox": ("Knox", "Directos moto"),
    "planet-knox": ("Knox", "Directos moto"),
    "planet knox": ("Knox", "Directos moto"),
    "leftlane": ("Leftlane", "Directos moto"),
    "left lane": ("Leftlane", "Directos moto"),
    "pando": ("Pando Moto", "Directos moto"),
    "pandomoto": ("Pando Moto", "Directos moto"),
    "pando moto": ("Pando Moto", "Directos moto"),
    "pmj": ("PMJ", "Directos moto"),
    "pmj jeans": ("PMJ", "Directos moto"),
    "resurgence": ("Resurgence Gear", "Directos moto"),
    "resurgencegear": ("Resurgence Gear", "Directos moto"),
    "resurgence gear": ("Resurgence Gear", "Directos moto"),
    "revit": ("REV'IT!", "Directos moto"),
    "revitsport": ("REV'IT!", "Directos moto"),
    "rev'it": ("REV'IT!", "Directos moto"),
    "ridingculture": ("Riding Culture", "Directos moto"),
    "riding culture": ("Riding Culture", "Directos moto"),
    "saint": ("SA1NT", "Directos moto"),
    "sa1nt": ("SA1NT", "Directos moto"),
    "spidi": ("Spidi", "Directos moto"),
    "tobacco": ("Tobacco Motorwear", "Directos moto"),
    "tobaccomotorwear": ("Tobacco Motorwear", "Directos moto"),
    "tobacco motorwear": ("Tobacco Motorwear", "Directos moto"),
    "tucano": ("Tucano Urbano", "Directos moto"),
    "tucanourbano": ("Tucano Urbano", "Directos moto"),
    "tucano urbano": ("Tucano Urbano", "Directos moto"),
    "wildust": ("Wildust", "Directos moto"),
    "wildust sisters": ("Wildust", "Directos moto"),

    # Streetwear
    "aime": ("Aimé Leon Dore", "Streetwear"),
    "aimeleondore": ("Aimé Leon Dore", "Streetwear"),
    "aime leon dore": ("Aimé Leon Dore", "Streetwear"),
    "ald": ("Aimé Leon Dore", "Streetwear"),
    "arte": ("Arte Antwerp", "Streetwear"),
    "arte-antwerp": ("Arte Antwerp", "Streetwear"),
    "arte antwerp": ("Arte Antwerp", "Streetwear"),
    "carhartt": ("Carhartt WIP", "Streetwear"),
    "carhartt-wip": ("Carhartt WIP", "Streetwear"),
    "carhartt wip": ("Carhartt WIP", "Streetwear"),
    "coldculture": ("Cold Culture", "Streetwear"),
    "cold culture": ("Cold Culture", "Streetwear"),
    "coldcultureworldwide": ("Cold Culture", "Streetwear"),
    "colebuxton": ("Cole Buxton", "Streetwear"),
    "cole buxton": ("Cole Buxton", "Streetwear"),
    "dailypaper": ("Daily Paper", "Streetwear"),
    "daily paper": ("Daily Paper", "Streetwear"),
    "dailypaperclothing": ("Daily Paper", "Streetwear"),
    "eme": ("Eme Studios", "Streetwear"),
    "eme studios": ("Eme Studios", "Streetwear"),
    "emestudios": ("Eme Studios", "Streetwear"),
    "fearofgod": ("Fear of God Essentials", "Streetwear"),
    "fear of god": ("Fear of God Essentials", "Streetwear"),
    "essentials": ("Fear of God Essentials", "Streetwear"),
    "gods": ("GODS", "Streetwear"),
    "fakegods": ("GODS", "Streetwear"),
    "fake gods": ("GODS", "Streetwear"),
    "fakegodsbrand": ("GODS", "Streetwear"),
    "kith": ("Kith", "Streetwear"),
    "laagam": ("Laagam", "Streetwear"),
    "orggeil": ("Orggeïl", "Streetwear"),
    "orggeïl": ("Orggeïl", "Streetwear"),
    "nude-project": ("Nude Project", "Streetwear"),
    "nudeproject": ("Nude Project", "Streetwear"),
    "nude project": ("Nude Project", "Streetwear"),
    "loveobsessed": ("LOVEOBSESSED", "Streetwear"),
    "love obsessed": ("LOVEOBSESSED", "Streetwear"),
    "ourlegacy": ("Our Legacy", "Streetwear"),
    "our legacy": ("Our Legacy", "Streetwear"),
    "palace": ("Palace", "Streetwear"),
    "palaceskateboards": ("Palace", "Streetwear"),
    "palace skateboards": ("Palace", "Streetwear"),
    "pangaia": ("Pangaia", "Streetwear"),
    "represent": ("Represent", "Streetwear"),
    "representclo": ("Represent", "Streetwear"),
    "represent clo": ("Represent", "Streetwear"),
    "scrapworld": ("Scrap World", "Streetwear"),
    "scrap world": ("Scrap World", "Streetwear"),
    "scuffers": ("Scuffers", "Streetwear"),
    "sportyandrich": ("Sporty & Rich", "Streetwear"),
    "sporty & rich": ("Sporty & Rich", "Streetwear"),
    "sporty and rich": ("Sporty & Rich", "Streetwear"),
    "stussy": ("Stüssy", "Streetwear"),
    "uniqlo": ("Uniqlo", "Streetwear"),
    "yuxus": ("Yuxus", "Streetwear"),

    # Técnica
    "alo": ("Alo", "Técnica"),
    "aloyoga": ("Alo", "Técnica"),
    "alo yoga": ("Alo", "Técnica"),
    "arcteryx": ("Arc'teryx", "Técnica"),
    "arc'teryx": ("Arc'teryx", "Técnica"),
    "ciele": ("Ciele", "Técnica"),
    "cieleathletics": ("Ciele", "Técnica"),
    "ciele athletics": ("Ciele", "Técnica"),
    "districtvision": ("District Vision", "Técnica"),
    "district vision": ("District Vision", "Técnica"),
    "ecoalf": ("Ecoalf", "Técnica"),
    "gymshark": ("Gymshark", "Técnica"),
    "houdini": ("Houdini", "Técnica"),
    "houdinisportswear": ("Houdini", "Técnica"),
    "houdini sportswear": ("Houdini", "Técnica"),
    "janji": ("Janji", "Técnica"),
    "nike": ("Nike ACG", "Técnica"),
    "nikeacg": ("Nike ACG", "Técnica"),
    "nike acg": ("Nike ACG", "Técnica"),
    "acg": ("Nike ACG", "Técnica"),
    "norrona": ("Norrøna", "Técnica"),
    "norrøna": ("Norrøna", "Técnica"),
    "on": ("On", "Técnica"),
    "on-running": ("On", "Técnica"),
    "on running": ("On", "Técnica"),
    "pasnormalstudios": ("Pas Normal Studios", "Técnica"),
    "pas normal studios": ("Pas Normal Studios", "Técnica"),
    "patagonia": ("Patagonia", "Técnica"),
    "patagonia-europe": ("Patagonia", "Técnica"),
    "patagonia europe": ("Patagonia", "Técnica"),
    "rapha": ("Rapha", "Técnica"),
    "satisfy": ("Satisfy", "Técnica"),
    "satisfyrunning": ("Satisfy", "Técnica"),
    "satisfy running": ("Satisfy", "Técnica"),
    "soar": ("SOAR", "Técnica"),
    "soarrunning": ("SOAR", "Técnica"),
    "soar running": ("SOAR", "Técnica"),
    "vuori": ("Vuori", "Técnica"),
    "vuoriclothing": ("Vuori", "Técnica"),
    "vuori clothing": ("Vuori", "Técnica"),
}


def load_env():
    """Carga variables desde el archivo .env sin dependencias externas."""
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def api_request(endpoint, method="GET", data=None, token=None):
    """Realiza peticiones HTTP a la API de Mail.tm."""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "User-Agent": "Mozilla/5.0 (StreetwearNewsletterArchiver/1.0)",
        "Accept": "application/json",
    }
    encoded_data = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        encoded_data = json.dumps(data).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            if content:
                return json.loads(content)
            return {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} en {endpoint}: {error_body}")
    except Exception as e:
        raise RuntimeError(f"Error de conexión en {endpoint}: {e}")


def slugify(text, max_length=50):
    """Convierte texto en un slug limpio para nombres de carpetas y archivos."""
    text = re.sub(r"[^\w\s-]", "", str(text or ""), flags=re.UNICODE).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text[:max_length] or "newsletter"


def detect_brand_and_category(from_name, from_email, subject):
    """
    Detecta la marca y su categoría (Directos moto, Streetwear, Técnica).
    Devuelve (brand_slug, brand_name, category).
    """
    from_email_lower = (from_email or "").lower()
    from_name_lower = (from_name or "").lower()
    subject_lower = (subject or "").lower()

    # Extraer dominio limpio (sin 'emea.', 'mail.', etc.)
    domain = from_email_lower.split("@")[-1] if "@" in from_email_lower else ""

    # 1. Comprobar dominios directos
    for key, (canonical_name, category) in BRAND_MAP.items():
        clean_key = key.replace(" ", "").replace("-", "")
        if f".{clean_key}." in f".{domain}." or domain.startswith(f"{clean_key}.") or domain == f"{clean_key}.com":
            return slugify(canonical_name), canonical_name, category

    # 2. Búsqueda por palabra o frase en el remitente o asunto (longitud descendente para mayor precisión)
    sorted_keys = sorted(BRAND_MAP.keys(), key=len, reverse=True)
    for key in sorted_keys:
        canonical_name, category = BRAND_MAP[key]
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(key) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, from_name_lower) or re.search(pattern, subject_lower):
            return slugify(canonical_name), canonical_name, category

    # 3. Búsqueda por caracteres alfanuméricos comprimidos (ej: johndoe vs john doe)
    condensed_from = re.sub(r"[^a-z0-9]", "", from_name_lower)
    for key in sorted_keys:
        clean_key = re.sub(r"[^a-z0-9]", "", key)
        if clean_key and len(clean_key) >= 4 and clean_key in condensed_from:
            canonical_name, category = BRAND_MAP[key]
            return slugify(canonical_name), canonical_name, category

    # 4. Heurística si no está en el mapa
    brand_slug = "general"
    brand_name = "General"
    category = "Streetwear"

    if from_name:
        clean = re.sub(r"[^\w\s-]", "", from_name).strip()
        if clean and len(clean) > 2:
            brand_name = clean
            brand_slug = slugify(clean)
    elif domain:
        parts = domain.split(".")
        if len(parts) >= 2:
            main_part = parts[-2]
            if main_part in ("com", "es", "co", "org", "net", "io") and len(parts) >= 3:
                main_part = parts[-3]
            brand_name = main_part.capitalize()
            brand_slug = slugify(main_part)

    return brand_slug, brand_name, category


CONFIRMATION_PATTERNS = [
    r"confirm.*(subscription|email|newsletter|address|registration)",
    r"confirma.*(suscripci[oó]n|correo|email|cuenta|registro)",
    r"verify.*(email|subscription|address|account)",
    r"verifi.*(email|courriel|adresse|inscription)",
    r"bitte.*bestätigen",
    r"bestätigen sie.*(anmeldung|newsletter|e-mail)",
    r"opt-?in",
    r"activate.*(subscription|account|newsletter)",
    r"action required.*(confirm|verify)",
    r"one more step",
    r"please confirm",
    r"por favor confirma",
]


def is_confirmation_email(subject, from_name=""):
    """Comprueba si un correo es de confirmación / doble opt-in transaccional."""
    text_to_check = f"{subject or ''} {from_name or ''}".lower()
    for pat in CONFIRMATION_PATTERNS:
        if re.search(pat, text_to_check, re.IGNORECASE):
            return True
    return False


def extract_and_click_confirmation_link(html_body, text_body=""):
    """
    Busca enlaces de confirmación o activación y los visita mediante HTTP GET
    para asegurar que la suscripción queda confirmada en la marca.
    """
    urls_found = []

    # 1. Buscar enlaces <a href="..."> en HTML
    a_tags = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html_body or "", re.IGNORECASE | re.DOTALL)
    for href, link_text in a_tags:
        clean_text = re.sub(r'<[^>]+>', '', link_text).strip().lower()
        href_lower = href.lower()

        # Descartar enlaces irrelevantes o de baja
        if any(bad in href_lower for bad in ["unsubscribe", "opt-out", "mailto:", "javascript:", "instagram.com", "facebook.com", "twitter.com", "tiktok.com", "youtube.com", "pinterest.com"]):
            continue

        # Comprobar si el texto o el link indica confirmación
        is_confirm_text = any(word in clean_text for word in ["confirm", "confirma", "verify", "verificar", "bestätigen", "activate", "activar", "yes, subscribe", "sí, suscribirme", "yes, sign me up", "click here to confirm"])
        is_confirm_url = any(word in href_lower for word in ["confirm", "verification", "optin", "double_opt_in", "/r/ldb/", "token=", "activate"])

        if is_confirm_text or is_confirm_url:
            urls_found.append(href)

    # 2. Si no se encontró en <a>, buscar URLs directas en texto plano
    if not urls_found and text_body:
        raw_urls = re.findall(r'https?://[^\s<>"\']+', text_body)
        for u in raw_urls:
            u_lower = u.lower()
            if any(word in u_lower for word in ["confirm", "verify", "optin", "activate", "token="]):
                if not any(bad in u_lower for bad in ["unsubscribe", "privacy", "terms"]):
                    urls_found.append(u)

    # Visitar los enlaces de confirmación encontrados
    visited = set()
    clicked = False
    for u in urls_found:
        u_clean = u.replace("&amp;", "&").strip()
        if u_clean in visited:
            continue
        visited.add(u_clean)
        try:
            req = urllib.request.Request(
                u_clean,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                }
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                print(f"      [✓] Suscripción confirmada automáticamente: {resp.geturl()} (HTTP {resp.status})")
                clicked = True
                break
        except Exception as e:
            print(f"      [i] Enlace de confirmación visitado ({u_clean[:60]}...): {e}")

    return clicked


def get_token(email_addr, password):
    """Autentica y devuelve el JWT Token."""
    res = api_request("/token", method="POST", data={"address": email_addr, "password": password})
    token = res.get("token")
    if not token:
        raise RuntimeError("No se recibió token de autenticación de Mail.tm.")
    return token


def fetch_all():
    print("=" * 60)
    print("  Streetwear & Moto Newsletter Archiver")
    print("=" * 60)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    env = load_env()
    email_addr = env.get("MAILTM_EMAIL") or os.environ.get("MAILTM_EMAIL")
    password = env.get("MAILTM_PASSWORD") or os.environ.get("MAILTM_PASSWORD")

    if not email_addr or not password:
        print("[!] Faltan credenciales en .env o variables de entorno (MAILTM_EMAIL, MAILTM_PASSWORD)")
        return

    try:
        token = get_token(email_addr, password)
    except Exception as e:
        print(f"[!] Error de autenticación: {e}")
        return

    processed_ids = set()
    if PROCESSED_FILE.exists():
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                processed_ids = set(json.load(f))
        except Exception:
            processed_ids = set()

    index_data = []
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except Exception:
            index_data = []

    print(f"[*] Conectado como: {email_addr}")
    print("[*] Comprobando bandeja de entrada...")
    messages_res = api_request("/messages?page=1", token=token)
    if isinstance(messages_res, list):
        messages = messages_res
    elif isinstance(messages_res, dict):
        messages = messages_res.get("hydra:member", messages_res.get("data", []))
    else:
        messages = []

    print(f"[*] Mensajes encontrados: {len(messages)}")

    new_count = 0
    for item in messages:
        msg_id = item.get("id")
        if not msg_id or msg_id in processed_ids:
            continue

        try:
            detail = api_request(f"/messages/{msg_id}", token=token)
        except Exception as e:
            print(f"[!] Error al descargar mensaje {msg_id}: {e}")
            continue

        from_obj = detail.get("from", {}) or {}
        from_name = from_obj.get("name", "") or ""
        from_email = from_obj.get("address", "") or ""
        subject = detail.get("subject", "(Sin Asunto)") or "(Sin Asunto)"
        created_at_raw = detail.get("createdAt", "")

        try:
            dt = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            date_prefix = dt.strftime("%Y-%m-%d")
        except Exception:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_prefix = datetime.now().strftime("%Y-%m-%d")

        # Extraer HTML
        html_raw = detail.get("html")
        html_body = ""
        if isinstance(html_raw, list):
            html_body = "".join(html_raw)
        elif isinstance(html_raw, str):
            html_body = html_raw

        if not html_body:
            text_body = detail.get("text", "")
            html_body = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{subject}</title>
<style>body{{font-family:sans-serif;padding:20px;white-space:pre-wrap;}}</style>
</head><body>{text_body}</body></html>"""

        brand_slug, brand_name, category = detect_brand_and_category(from_name, from_email, subject)

        # Detectar si es un correo transaccional de confirmación / doble opt-in
        text_body = detail.get("text", "")
        if is_confirmation_email(subject, from_name):
            print(f"  [⚡] Correo de confirmación detectado ({brand_name}): '{subject}'")
            print("      Haciendo clic automático en el enlace de confirmación para activar la suscripción...")
            extract_and_click_confirmation_link(html_body, text_body)
            processed_ids.add(msg_id)
            print("      [✓] Suscripción activada y correo excluido del Swipe File (no es newsletter de producto).")
            continue

        subj_slug = slugify(subject, max_length=40)
        folder_name = f"{date_prefix}_{subj_slug}"
        target_dir = ARCHIVE_DIR / brand_slug / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        html_file = target_dir / "email.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_body)

        meta = {
            "id": msg_id,
            "brand": brand_slug,
            "brand_name": brand_name,
            "category": category,
            "subject": subject,
            "from_name": from_name,
            "from_email": from_email,
            "to": email_addr,
            "date": date_str,
            "folder": str(target_dir.relative_to(ARCHIVE_DIR)),
            "html_path": str(html_file.relative_to(ARCHIVE_DIR)),
        }

        with open(target_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        index_data.append(meta)
        processed_ids.add(msg_id)
        new_count += 1
        print(f"  [+] [{category} | {brand_name}] {subject} ({date_prefix})")

    # Limpieza proactiva: eliminar cualquier correo de confirmación residual y re-clasificar
    cleaned_index = []
    for item in index_data:
        if is_confirmation_email(item.get("subject", ""), item.get("from_name", "")):
            folder = ARCHIVE_DIR / item.get("folder", "")
            if folder.exists():
                shutil.rmtree(folder, ignore_errors=True)
            print(f"  [-] Eliminado correo de confirmación residual: {item.get('subject')}")
        else:
            b_slug, b_name, cat = detect_brand_and_category(
                item.get("from_name", ""), item.get("from_email", ""), item.get("subject", "")
            )
            item["brand"] = b_slug
            item["brand_name"] = b_name
            item["category"] = cat
            cleaned_index.append(item)
    index_data = cleaned_index

    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f, indent=2)

    index_data.sort(key=lambda x: x.get("date", ""), reverse=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"[✓] Finalizado: {new_count} nuevas newsletters guardadas.")
    print(f"[*] Repositorio total: {len(index_data)} newsletters.")
    print("=" * 60)


if __name__ == "__main__":
    fetch_all()
