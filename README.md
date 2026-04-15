# Bot Convocatorias — Fondos de Cultura

Scraper automático que monitorea las convocatorias abiertas en [fondosdecultura.cl](https://www.fondosdecultura.cl/convocatorias-abiertas/), filtra por palabras clave relevantes, guarda los resultados en Excel y envía un resumen por Telegram.

---

## Características

- Scraping con Selenium (modo headless)
- Filtrado por palabras clave configurables
- Exportación automática a `.xlsx` con fecha
- Notificación vía bot de Telegram

---

## Requisitos

- Python 3.8+
- Google Chrome instalado
- Una cuenta de Telegram con un bot creado ([instrucciones](https://core.telegram.org/bots#botfather))

---

## Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/bot-convocatorias.git
cd bot-convocatorias

# 2. Crea y activa un entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Configura las variables de entorno
cp .env.example .env
# Edita .env con tu TELEGRAM_TOKEN y TELEGRAM_CHAT_ID
```

---

## Configuración

Edita el archivo `.env`:

```
TELEGRAM_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

Las palabras clave de filtrado se pueden editar directamente en `scraper.py`, en la variable `PALABRAS_CLAVE`.

---

## Uso

```bash
python scraper.py
```

Los resultados se guardan en la carpeta `resultados/` con el nombre `convocatorias_relevantes_YYYY-MM-DD.xlsx`.

---

## Automatización (opcional)

Para ejecutar el bot de forma periódica, programarlo con el **Programador de tareas de Windows** o con `cron` en Linux/macOS.

Ejemplo de cron (todos los días a las 9:00 AM):
```
0 9 * * * /ruta/al/proyecto/.venv/bin/python /ruta/al/proyecto/scraper.py
```

---

## Estructura del proyecto

```
bot-convocatorias/
├── scraper.py          # Script principal
├── requirements.txt    # Dependencias
├── .env.example        # Plantilla de configuración
├── .gitignore
└── README.md
```
