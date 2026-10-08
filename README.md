# Streetwear Mailing Swipe File (Mail.tm)

Sistema automatizado para recopilar, archivar y analizar newsletters de marcas de streetwear usando la API de **Mail.tm**.

---

## 🚀 Inicio Rápido

### 1. Configurar credenciales (o auto-generar)
Abre el archivo `.env`:
- Si tu compañero ya tiene un correo y contraseña de `mail.tm`, ponlos ahí:
  ```env
  MAILTM_EMAIL=tu_correo@dominio.com
  MAILTM_PASSWORD=tu_contraseña
  ```
- **O déjalos vacíos**: Si ejecutas el script con el archivo `.env` vacío, el script creará automáticamente una cuenta en Mail.tm y te mostrará el usuario y contraseña para que también puedas abrirlo en la web.

---

### 2. Descargar Newsletters
Ejecuta:
```bash
python3 fetch_newsletters.py
```
El script:
- Se conecta a la API de Mail.tm.
- Revisa los mensajes recibidos.
- Detecta automáticamente la marca streetwear (remitente o asunto).
- Guarda el HTML original, textos e imágenes en `archive/<marca>/<fecha>_<asunto>/`.
- Actualiza el índice `archive/index.json`.

---

### 3. Abrir el Visor Visual Swipe File
```bash
python3 server.py
```
Abre en tu navegador: **[http://localhost:8000](http://localhost:8000)**

- Vista móvil (iPhone 390px) y de escritorio.
- Filtro por marcas y buscador por asunto.
- Copiar copy del asunto con un clic.
- Botón **Sync** para descargar nuevos correos directamente desde la web.

---

### 4. Compartir el Visor con Compañeros

Tienes 3 formas muy sencillas de pasárselo a quien quieras:

#### A) Enviar un archivo ZIP (Funciona offline en cualquier ordenador)
Ejecuta:
```bash
python3 build_static.py
```
Te creará un archivo **`streetwear_swipe_file.zip`** listo para enviar por Slack, Drive o WeTransfer. Tu compañero solo tiene que descomprimirlo y hacer doble clic en `index.html`. No necesita instalar Python ni nada.

#### B) En la misma red local / WiFi (Oficina o casa)
Si tu servidor está encendido (`python3 server.py`), cualquier persona en tu misma red WiFi puede entrar desde su navegador o móvil introduciendo tu IP local:
- `http://172.31.48.183:8000`

#### C) Crear un enlace público instantáneo en vivo (Túnel)
Si quieres pasarle un enlace web temporal a alguien que esté fuera mientras tienes el servidor abierto:
```bash
npx localtunnel --port 8000
```
Te generará una URL pública segura `https://xxxx.loca.lt` accesible desde cualquier parte del mundo.

