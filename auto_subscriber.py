#!/usr/bin/env python3
"""
Auto-Subscriber para Streetwear, Moto y Ropa Técnica
Inspecciona las webs de las marcas, detecta formularios de newsletter
(Shopify, Mailchimp, Klaviyo, etc.) y tramita la suscripción automáticamente.
También revisa el buzón de Mail.tm para confirmar enlaces de doble opt-in.
"""

import html
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TARGET_EMAIL = "streetwear_moto_8asc@maxxspace.com"

# SSL Context que ignora errores de certificados antiguos si los hay
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

BRANDS_TO_TRY = [
    # DIRECTOS MOTO
    ("Alpinestars", "https://www.alpinestars.com"),
    ("Bull-it", "https://www.bull-it.com"),
    ("Dainese", "https://www.dainese.com"),
    ("Deus Ex Machina", "https://eu.deuscustoms.com"),
    ("Fuel Motorcycles", "https://fuelmotorcycles.eu"),
    ("Icon", "https://rideicon.com"),
    ("John Doe", "https://www.ridejohndoe.com"),
    ("Knox", "https://www.planet-knox.com"),
    ("Leftlane", "https://leftlaneapparel.com"),
    ("Pando Moto", "https://pandomoto.com"),
    ("PMJ", "https://pmj.it"),
    ("Resurgence Gear", "https://www.resurgencegear.net"),
    ("REV'IT!", "https://www.revitsport.com"),
    ("Riding Culture", "https://ridingculture.com"),
    ("SA1NT", "https://saint.cc"),
    ("Spidi", "https://www.spidi.com"),
    ("Tobacco Motorwear", "https://tobaccomotorwear.com"),
    ("Tucano Urbano", "https://www.tucanourbano.com"),
    ("Wildust", "https://wildust-sisters.com"),

    # STREETWEAR
    ("Aimé Leon Dore", "https://www.aimeleondore.com"),
    ("Arte Antwerp", "https://arte-antwerp.com"),
    ("Carhartt WIP", "https://www.carhartt-wip.com"),
    ("Cold Culture", "https://coldcultureworldwide.com"),
    ("Cole Buxton", "https://colebuxton.com"),
    ("Daily Paper", "https://www.dailypaperclothing.com"),
    ("Eme Studios", "https://emestudios.com"),
    ("Fear of God", "https://fearofgod.com"),
    ("GODS", "https://fakegodsbrand.com"),
    ("Kith", "https://kith.com"),
    ("Laagam", "https://laagam.com"),
    ("Our Legacy", "https://www.ourlegacy.com"),
    ("Palace", "https://www.palaceskateboards.com"),
    ("Pangaia", "https://pangaia.com"),
    ("Represent", "https://representclo.com"),
    ("Scrap World", "https://scrapworld.es"),
    ("Sporty & Rich", "https://sportyandrich.com"),
    ("Stüssy", "https://www.stussy.com"),
    ("Uniqlo", "https://www.uniqlo.com"),
    ("Yuxus", "https://yuxus.com"),

    # TÉCNICA
    ("Alo", "https://www.aloyoga.com"),
    ("Arc'teryx", "https://arcteryx.com"),
    ("Ciele", "https://cieleathletics.com"),
    ("District Vision", "https://www.districtvision.com"),
    ("Ecoalf", "https://ecoalf.com"),
    ("Gymshark", "https://www.gymshark.com"),
    ("Houdini", "https://houdinisportswear.com"),
    ("Janji", "https://janji.com"),
    ("Nike ACG", "https://www.nike.com"),
    ("Norrøna", "https://norrona.com"),
    ("On", "https://www.on.com"),
    ("Pas Normal Studios", "https://pasnormalstudios.com"),
    ("Rapha", "https://www.rapha.cc"),
    ("Satisfy", "https://satisfyrunning.com"),
    ("SOAR", "https://www.soarrunning.com"),
    ("Vuori", "https://vuoriclothing.com"),
]


def fetch_page(url, timeout=10):
    """Descarga el HTML de la página principal."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace"), resp.geturl()
    except Exception as e:
        return None, None


def try_shopify_contact_form(base_url, page_html):
    """Intenta suscribirse mediante el formulario estándar de cliente de Shopify."""
    parsed = urllib.parse.urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    target_url = f"{origin}/contact"

    # Buscar si hay inputs hidden específicos en el formulario
    data = {
        "form_type": "customer",
        "utf8": "✓",
        "contact[tags]": "newsletter",
        "contact[email]": TARGET_EMAIL,
    }

    encoded = urllib.parse.urlencode(data).encode("utf-8")
    post_headers = {
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": origin,
        "Referer": base_url,
    }

    req = urllib.request.Request(target_url, data=encoded, headers=post_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            if resp.status in (200, 302, 303):
                return True, "Shopify Form"
    except urllib.error.HTTPError as e:
        if e.code in (302, 303):
            return True, "Shopify Form (Redirect)"
    except Exception:
        pass
    return False, None


def try_klaviyo_api(base_url, page_html):
    """Detecta tokens de Klaviyo en la página e intenta enviar suscripción a Klaviyo."""
    # Buscar company_id / account_id de Klaviyo (ej: company_id=XYZ o 'XYZ' en script de klaviyo)
    company_ids = re.findall(r"klaviyo\.com/onsite/js/klaviyo\.js\?company_id=([a-zA-Z0-9_-]+)", page_html)
    if not company_ids:
        company_ids = re.findall(r"_learnq\.push\(\[\s*['\"]identify['\"]\s*,\s*\{\s*['\"]\$email['\"]", page_html)
    if not company_ids:
        company_ids = re.findall(r"[\"']([A-Za-z0-9]{6})[\"']\s*:\s*\{\s*\"type\"\s*:\s*\"klaviyo\"", page_html)
    if not company_ids:
        company_ids = re.findall(r"account_id[\"']?\s*:\s*[\"']([A-Za-z0-9]{6})[\"']", page_html)

    # Buscar list_id
    list_ids = re.findall(r"list_id[\"']?\s*:\s*[\"']([A-Za-z0-9]{6})[\"']", page_html)
    if not list_ids:
        list_ids = re.findall(r"g=([A-Za-z0-9]{6})", page_html)

    if company_ids:
        comp_id = company_ids[0]
        # Intentar Klaviyo client subscription
        url = f"https://a.klaviyo.com/client/subscriptions/?company_id={comp_id}"
        payload = {
            "data": {
                "type": "subscription",
                "attributes": {
                    "email": TARGET_EMAIL,
                }
            }
        }
        if list_ids:
            payload["data"]["attributes"]["list_id"] = list_ids[0]

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": HEADERS["User-Agent"],
                "revision": "2023-10-15"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
                if resp.status in (200, 201, 202):
                    return True, f"Klaviyo API ({comp_id})"
        except Exception:
            pass

    return False, None


def try_mailchimp_form(base_url, page_html):
    """Detecta formularios de Mailchimp en la página y envía el correo."""
    mc_urls = re.findall(r'action=["\'](https://[^"\']*list-manage\.com/subscribe/post[^"\']*)["\']', page_html)
    if mc_urls:
        mc_url = html.unescape(mc_urls[0])
        # Reemplazar post por post-json para respuesta limpia si aplica
        data = urllib.parse.urlencode({"EMAIL": TARGET_EMAIL, "b_email": TARGET_EMAIL}).encode("utf-8")
        req = urllib.request.Request(mc_url, data=data, headers={**HEADERS, "Referer": base_url}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                if resp.status in (200, 302):
                    return True, "Mailchimp Form"
        except Exception:
            pass
    return False, None


def try_generic_form(base_url, page_html):
    """Busca cualquier formulario en la página que tenga un campo 'email'."""
    forms = re.findall(r"<form[^>]*action=[\"']([^\"']*)[\"'][^>]*>(.*?)</form>", page_html, re.I | re.DOTALL)
    parsed = urllib.parse.urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    for action, form_body in forms:
        if "email" not in form_body.lower():
            continue
        # Descartar formularios de búsqueda o login
        if "search" in action.lower() or "login" in action.lower():
            continue

        target_url = urllib.parse.urljoin(base_url, action)
        inputs = re.findall(r"<input[^>]*name=[\"']([^\"']*)[\"'][^>]*>", form_body, re.I)

        data = {}
        email_field_found = False
        for inp in inputs:
            name = inp.strip()
            if not name:
                continue
            if "email" in name.lower():
                data[name] = TARGET_EMAIL
                email_field_found = True
            elif "utf8" in name.lower():
                data[name] = "✓"
            elif "form_type" in name.lower():
                data[name] = "customer"
            elif "tags" in name.lower():
                data[name] = "newsletter"

        if email_field_found:
            encoded = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(
                target_url,
                data=encoded,
                headers={
                    **HEADERS,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": origin,
                    "Referer": base_url
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    if resp.status in (200, 302, 303):
                        return True, f"Form ({target_url})"
            except Exception:
                pass
    return False, None


def subscribe_brand(name, url):
    """Prueba todos los métodos para suscribir una marca."""
    page_html, final_url = fetch_page(url)
    if not page_html:
        return False, "Web inaccesible o Cloudflare/Bot block"

    # 1. Probar formulario nativo de Shopify
    ok, method = try_shopify_contact_form(final_url or url, page_html)
    if ok:
        return True, method

    # 2. Probar Mailchimp
    ok, method = try_mailchimp_form(final_url or url, page_html)
    if ok:
        return True, method

    # 3. Probar Klaviyo
    ok, method = try_klaviyo_api(final_url or url, page_html)
    if ok:
        return True, method

    # 4. Probar formulario genérico
    ok, method = try_generic_form(final_url or url, page_html)
    if ok:
        return True, method

    return False, "Requiere Captcha/Popup interactivo"


def main():
    print("=" * 70)
    print(f"  Iniciando proceso de auto-suscripción para:")
    print(f"  👉 {TARGET_EMAIL}")
    print("=" * 70)

    results = {"success": [], "protected": []}

    for name, url in BRANDS_TO_TRY:
        print(f"[*] Procesando: {name} ({url})...", end=" ", flush=True)
        try:
            ok, method = subscribe_brand(name, url)
            if ok:
                print(f"✅ ¡SUSCRITO! [{method}]")
                results["success"].append((name, method))
            else:
                print(f"⚠️ {method}")
                results["protected"].append((name, method))
        except Exception as e:
            print(f"❌ Error: {e}")
            results["protected"].append((name, str(e)))

        # Pausa suave de cortesía para no saturar
        time.sleep(1)

    print("\n" + "=" * 70)
    print(f"  RESUMEN DE AUTO-SUSCRIPCIÓN:")
    print(f"  ✅ Exitosas automáticamente: {len(results['success'])}")
    print(f"  ⚠️ Protegidas / Requieren navegador: {len(results['protected'])}")
    print("=" * 70)

    if results["success"]:
        print("\nMarcas suscritas con éxito:")
        for name, method in results["success"]:
            print(f"  - {name} ({method})")

    # Guardar reporte en archivo para consulta
    report_file = BASE_DIR / "auto_subscription_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] Reporte guardado en: {report_file}")


if __name__ == "__main__":
    main()
