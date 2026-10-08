#!/usr/bin/env python3
"""
Generador de Exportación Estática (Swipe File)
Empaqueta todo el repositorio en una carpeta 'dist/' lista para:
1. Abrir con doble clic en cualquier ordenador (funciona offline).
2. Subir a Vercel, Netlify o GitHub Pages gratis con 1 clic.
3. Enviar comprimido en un archivo .zip a cualquier compañero.
"""

import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = BASE_DIR / "archive"
INDEX_FILE = ARCHIVE_DIR / "index.json"
DIST_DIR = BASE_DIR / "dist"
SERVER_FILE = BASE_DIR / "server.py"


def generate_static():
    print("=" * 60)
    print("  Generando versión estática del Swipe File...")
    print("=" * 60)

    if not ARCHIVE_DIR.exists() or not INDEX_FILE.exists():
        print("[!] No se encontró la carpeta 'archive' o 'index.json'. Ejecuta primero 'python3 fetch_newsletters.py'.")
        return

    # 1. Crear carpeta dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Copiar archivos de archivo
    target_archive = DIST_DIR / "archive"
    shutil.copytree(ARCHIVE_DIR, target_archive)
    print(f"[✓] Copiados archivos de newsletters a 'dist/archive/'.")

    # 3. Leer index.json
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        emails_data = json.load(f)

    # 4. Leer plantilla HTML de server.py
    with open(SERVER_FILE, "r", encoding="utf-8") as f:
        server_code = f.read()

    # Extraer el HTML de server.py
    start_tag = 'HTML_PAGE = """'
    end_tag = '"""'
    start_idx = server_code.find(start_tag) + len(start_tag)
    end_idx = server_code.find(end_tag, start_idx)
    html_template = server_code[start_idx:end_idx]

    # Reemplazar la llamada a fetch('/api/emails') para que use los datos embebidos
    # y así funcione con doble clic directo (file://) o en cualquier hosting estático
    embedded_json = json.dumps(emails_data, ensure_ascii=False)
    modified_html = html_template.replace(
        "async function loadData() {\n      try {\n        const res = await fetch('/api/emails');\n        emails = await res.json();\n        renderBrandChips();\n        filterEmails();\n      } catch (err) {\n        console.error(\"Error cargando emails:\", err);\n      }\n    }",
        f"""function loadData() {{
      emails = {embedded_json};
      renderBrandChips();
      filterEmails();
    }}"""
    )

    # Ocultar el botón Sync en la versión estática exportada
    modified_html = modified_html.replace(
        '<button class="sync-btn" onclick="syncEmails()">↻ Sync</button>',
        '<span style="font-size:0.75rem; color:var(--text-muted); background:var(--border); padding:4px 8px; border-radius:4px;">Archivo Estático</span>'
    )

    # Guardar dist/index.html y también en la raíz del repositorio
    out_index = DIST_DIR / "index.html"
    root_index = BASE_DIR / "index.html"
    with open(out_index, "w", encoding="utf-8") as f:
        f.write(modified_html)
    with open(root_index, "w", encoding="utf-8") as f:
        f.write(modified_html)

    print(f"[✓] Generado 'index.html' en la raíz y en 'dist/' con {len(emails_data)} correos embebidos.")

    # 5. Generar también un archivo ZIP listo para enviar
    zip_path = BASE_DIR / "streetwear_swipe_file"
    shutil.make_archive(str(zip_path), "zip", DIST_DIR)
    print(f"[✓] Archivo comprimido generado: 'streetwear_swipe_file.zip'")

    print("=" * 60)
    print("¡Listo! Opciones para compartir:")
    print("1. Envía el archivo 'streetwear_swipe_file.zip' por Slack / Drive / WeTransfer.")
    print("   -> Tu compañero sólo tiene que descomprimirlo y hacer doble clic en 'index.html'.")
    print("2. O sube la carpeta 'dist/' directamente a Vercel, Netlify o GitHub Pages.")
    print("=" * 60)


if __name__ == "__main__":
    generate_static()
