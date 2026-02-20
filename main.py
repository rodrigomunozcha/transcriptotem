"""
Punto de entrada para ejecutar el servidor de Transcriptotem.

Uso:
    python main.py

O con uvicorn directamente:
    uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
"""
import os
import uvicorn

# ── Optimización térmica para Apple Silicon M3 ──────────────────────────────
# Limita los threads de operaciones matemáticas para reducir calor.
# Whisper seguirá usando la GPU del M3 (vía MLX) pero con menos presión
# en los cores de CPU. Efecto: ~20% menos calor, ~10% más lento.
# Cambiar "4" a "6" si prefieres más velocidad y aceptas más calor.
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "4"

# Evita que MLX acapare toda la memoria unificada del M3.
# Limita el uso de memoria de la GPU al 70% (ajusta si tienes errores de RAM).
os.environ["MLX_GPU_MEMORY_LIMIT"] = "0.70"
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # host 0.0.0.0 permite conexiones desde otras máquinas en la red (ej: Android)
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Recarga automática al cambiar código
    )
