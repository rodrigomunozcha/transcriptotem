# -*- coding: utf-8 -*-
"""
Módulo de transcripción con Whisper.
Prioriza mlx-whisper en Apple Silicon (M3) para mejor rendimiento.
Si no está disponible, usa openai-whisper (CPU).
"""
import os
import re
from typing import Optional, Tuple

from backend.models import PROMPTS_POR_IDIOMA, LANGUAGE_CODE

_engine: Optional[str] = None
_model_loaded: Optional[str] = None
_whisper_model = None

MLX_MODELS_LEGACY = {
    "base":     "mlx-community/whisper-base-mlx",
    "small":    "mlx-community/whisper-small-mlx",
    "medium":   "mlx-community/whisper-medium-mlx",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
}

OPENAI_FALLBACK_MODELS = {
    "mlx-community/whisper-tiny-mlx":       "tiny",
    "mlx-community/whisper-base-mlx":       "base",
    "mlx-community/whisper-small-mlx":      "small",
    "mlx-community/whisper-medium-mlx":     "medium",
    "mlx-community/whisper-large-v3-turbo": "large-v3",
    "mlx-community/whisper-large-v3-mlx":   "large-v3",
}

DEFAULT_CONTEXT_FALLBACK = (
    "Transcripción de clase universitaria en Chile. "
    "Transcribir únicamente al expositor principal, "
    "ignorar ruido de fondo y conversaciones secundarias."
)


def _build_initial_prompt(language_profile: str, context_text: str) -> str:
    user_ctx = (context_text or "").strip()
    base_ctx = user_ctx if user_ctx else DEFAULT_CONTEXT_FALLBACK
    profile_prompt = (PROMPTS_POR_IDIOMA.get(language_profile) or "").strip()
    if not profile_prompt:
        return base_ctx
    if profile_prompt.lower() in base_ctx.lower():
        return base_ctx
    return f"{base_ctx}\n{profile_prompt}"


def _clean_transcript(text: str) -> str:
    """Filtro de alucinaciones post-procesamiento."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\b(\w+)(?:\s+\1){4,}\b", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"\b((?:\w+\s+){1,4}\w+)(?:\s+\1){4,}\b", r"\1", text, flags=re.IGNORECASE)
    cleaned_lines = []
    for line in text.split("\n"):
        raw = line.strip()
        if not raw:
            cleaned_lines.append("")
            continue
        if re.fullmatch(r"[.\s\u2026]+", raw):
            continue
        if re.fullmatch(r"[^\w\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\u00c1\u00c9\u00cd\u00d3\u00da\u00d1]+", raw):
            continue
        tokens = re.findall(r"[a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+", raw.lower())
        if len(tokens) >= 2 and len(set(tokens)) == 1:
            continue
        if re.search(r"(.)\1{4,}", raw):
            continue
        raw_stripped = re.sub(r"\s+", " ", raw.strip())
        if re.search(r"\b(\w{1,3})(?:\s+\1){4,}\b", raw_stripped, re.IGNORECASE):
            continue
        letters = re.findall(r"[a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]", raw.lower())
        if letters and (len(letters) / max(len(raw), 1)) < 0.25:
            continue
        cleaned_lines.append(line)
    out = "\n".join(cleaned_lines)
    out = re.sub(r"\n{4,}", "\n\n\n", out)
    return out.strip()


def _get_whisper_model(model_name: str):
    global _whisper_model, _model_loaded
    if _whisper_model is None or _model_loaded != model_name:
        try:
            import whisper
            _whisper_model = whisper.load_model(model_name, device="cpu")
            _model_loaded = model_name
        except Exception as e:
            raise RuntimeError(f"No se pudo cargar Whisper: {e}")
    return _whisper_model


def _detect_engine() -> str:
    global _engine
    if _engine is not None:
        return _engine
    try:
        import mlx_whisper  # noqa: F401
        _engine = "mlx"
    except ImportError:
        _engine = "whisper"
    return _engine


def transcribe(
    audio_path: str,
    language_profile: str = "es-chile",
    model_name: str = "mlx-community/whisper-large-v3-turbo",
    context_text: str = "",
) -> Tuple[str, str, int]:
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Archivo no encontrado: {audio_path}")
    lang_code = LANGUAGE_CODE.get(language_profile, "es")
    initial_prompt = _build_initial_prompt(language_profile, context_text)
    engine = _detect_engine()
    if engine == "mlx":
        text, lang_used, segs = _transcribe_mlx(audio_path, lang_code, initial_prompt, model_name)
    else:
        fallback = OPENAI_FALLBACK_MODELS.get(model_name, model_name)
        text, lang_used, segs = _transcribe_openai(audio_path, lang_code, initial_prompt, fallback, language_profile)
    return _clean_transcript(text), lang_used, segs


def _transcribe_mlx(audio_path, lang_code, initial_prompt, model_name):
    import mlx_whisper
    hf_name = model_name if "/" in model_name else MLX_MODELS_LEGACY.get(model_name, "mlx-community/whisper-large-v3-turbo")
    kwargs = {"path_or_hf_repo": hf_name, "language": lang_code, "no_speech_threshold": 0.6, "compression_ratio_threshold": 2.4}
    if initial_prompt:
        kwargs["initial_prompt"] = initial_prompt
    try:
        result = mlx_whisper.transcribe(audio_path, **kwargs)
    except TypeError:
        result = None
        for key in ["initial_prompt", "compression_ratio_threshold", "no_speech_threshold"]:
            kwargs.pop(key, None)
            try:
                result = mlx_whisper.transcribe(audio_path, **kwargs)
                break
            except TypeError:
                pass
        if result is None:
            result = mlx_whisper.transcribe(audio_path, path_or_hf_repo=hf_name, language=lang_code)
    return result.get("text", "").strip(), lang_code, len(result.get("segments", []))


def _transcribe_openai(audio_path, lang_code, initial_prompt, model_name, language_profile="es-chile"):
    model = _get_whisper_model(model_name)
    temperature = 0.2 if language_profile == "accento-mixto" else 0.0
    result = model.transcribe(
        audio_path, language=lang_code, initial_prompt=initial_prompt,
        no_speech_threshold=0.6, compression_ratio_threshold=2.4,
        condition_on_previous_text=True, temperature=temperature, fp16=False,
    )
    return (result.get("text") or "").strip(), lang_code, len(result.get("segments", []))
