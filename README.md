# Transcriptotem 🎙

**Transcripción automática de clases universitarias con Whisper + Apple Silicon M3**

Herramienta personal para transcribir grabaciones de clases directamente en el Mac, usando Whisper MLX optimizado para el chip M3. Sin servicios externos, sin costos, sin nada corriendo en background cuando no se usa.

---

## ¿Qué hace?

- Transcribe archivos `.m4a`, `.mp3` y `.wav` localmente con [Whisper MLX](https://github.com/ml-explore/mlx-examples)
- Interfaz web local (no requiere internet para transcribir)
- Modo manual (drag & drop) y modo carpeta (procesa una carpeta entera de una vez)
- Presets por ramo universitario para mejorar la precisión
- Exportación a TXT, PDF y DOCX
- Optimizado para Apple Silicon M3 — sin servicios en background, el Mac queda 100% libre al cerrar

---

## Stack

| Componente | Tecnología |
|---|---|
| Backend | Python · FastAPI · Uvicorn |
| Transcripción | mlx-whisper (Apple Silicon) · openai-whisper (fallback CPU) |
| Frontend | HTML · CSS · JavaScript vanilla |
| Exportación | ReportLab (PDF) · python-docx (DOCX) |

---

## Requisitos

- macOS con Apple Silicon (M1 / M2 / M3) — recomendado
- Python 3.10+
- [Homebrew](https://brew.sh) (para instalar ffprobe)

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/transcriptotem.git
cd transcriptotem

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. (Opcional) Instalar ffprobe para estimación de tiempo
brew install ffmpeg
```

---

## Uso

```bash
# Activar entorno e iniciar servidor
source venv/bin/activate && python3 main.py
```

Luego abre **http://localhost:8000** en tu navegador.

Para detener: `Ctrl + C` en Terminal.

---

## Estructura del proyecto

```
transcriptotem/
├── index.html          # Interfaz web
├── main.py             # Punto de entrada del servidor
├── requirements.txt    # Dependencias Python
└── backend/
    ├── app.py          # API FastAPI
    ├── transcriber.py  # Motor de transcripción Whisper
    └── models.py       # Modelos y configuración de idioma
```

---

## Configuración de carpetas (modo carpeta OneDrive)

Edita las rutas en `backend/app.py` para que apunten a tus carpetas:

```python
ONEDRIVE    = Path.home() / "tu" / "ruta" / "carpeta-base"
PENDIENTES  = ONEDRIVE / "Pendientes"   # audios a transcribir
TRANSCRITAS = ONEDRIVE / "Transcritas"  # .txt generados
ARCHIVADOS  = ONEDRIVE / "Archivados"   # audios ya procesados
```

---

## Modelos disponibles

| Modelo | Velocidad | Precisión | Calor |
|---|---|---|---|
| Tiny | ⚡⚡⚡⚡ | ★★☆☆ | 🟢 |
| Base | ⚡⚡⚡ | ★★★☆ | 🟢 |
| Small | ⚡⚡ | ★★★☆ | 🟡 |
| Medium | ⚡ | ★★★★ | 🟡 |
| **Large Turbo** ⭐ | ⚡⚡ | ★★★★ | 🟠 |
| Large v3 | ⚡ | ★★★★★ | 🔴 |

---

## Licencia

MIT — úsalo, modifícalo, mejóralo.
