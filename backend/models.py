"""
Modelos Pydantic para las peticiones y respuestas de la API.
Cada modelo describe la estructura de datos que recibe o devuelve el backend.
"""
from pydantic import BaseModel, Field
from typing import Optional


# --- Perfiles de idioma (coinciden con los valores del select en index.html) ---
# es-chile, es-spain, es-neutro, en, acento-mixto

# Prompts iniciales para orientar a Whisper hacia voz de profesor en clase
PROMPTS_POR_IDIOMA = {
    "es-chile": (
        "Transcripción de clase universitaria en Chile. "
        "Transcribir únicamente la voz del profesor. "
        "Ignorar conversaciones de alumnos en el fondo. "
        "Contexto académico formal."
    ),
    "es-spain": (
        "Transcripción de clase universitaria en España. "
        "Voz del profesor, contexto académico y formal."
    ),
    "es-neutro": (
        "Transcripción de clase universitaria en español. "
        "Voz del profesor, contexto académico."
    ),
    "en": (
        "University lecture transcription. Professor's voice, academic context."
    ),
    "acento-mixto": (
        "Transcripción de clase universitaria en español. "
        "El profesor habla con acento mixto de varias regiones: "
        "pronuncia las vocales de forma más cerrada de lo habitual, "
        "alterna 'vosotros' y 'ustedes', y mezcla expresiones de España "
        "y de Hispanoamérica. "
        "Habla en primera persona dirigiéndose a alumnos. "
        "Transcribir únicamente la voz del profesor, ignorar respuestas "
        "breves de alumnos. "
        "Contexto académico formal."
    ),
}

# Mapeo idioma UI -> código Whisper (language="es" o "en")
LANGUAGE_CODE = {
    "es-chile": "es",
    "es-spain": "es",
    "es-neutro": "es",
    "en": "en",
    "acento-mixto": "es",
}


class TranscribeRequest(BaseModel):
    """
    Parámetros opcionales que el frontend puede enviar junto al archivo.
    Si no se envían, se usan los valores por defecto.
    """
    language: str = Field(
        default="es-chile",
        description="Perfil de idioma: es-chile, es-spain, es-neutro, en, acento-mixto"
    )
    model: str = Field(
        default="mlx-community/whisper-large-v3-turbo",
        description="Modelo MLX (HuggingFace) o compat: base/small/medium/large-v3"
    )


class TranscribeResponse(BaseModel):
    """
    Respuesta de la API de transcripción.
    """
    text: str = Field(description="Texto transcrito completo")
    language: str = Field(description="Idioma usado en la transcripción")
    model: str = Field(description="Modelo Whisper utilizado")
    segments_count: int = Field(default=0, description="Número de segmentos (si aplica)")
    error: Optional[str] = Field(default=None, description="Mensaje de error si falló")
