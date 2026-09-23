# -*- coding: utf-8 -*-
"""
Comprueba la configuracion de carpetas del modo carpeta.

Existe por un error real: la interfaz llamaba a /api/config desde tres
lugares y ese endpoint nunca se habia escrito, asi que guardar las rutas
fallaba siempre y el backend usaba una ruta fija dentro de la carpeta de una
persona. En otro equipo el modo carpeta no funcionaba.

Se corre solo:  python3 tests/test_config.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from backend import app as modulo  # noqa: E402

fallos = 0


def check(descripcion, condicion, detalle=""):
    global fallos
    if condicion:
        print(f"  ok     {descripcion}")
    else:
        fallos += 1
        print(f"  FALLA  {descripcion}  {detalle}")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "Entrada").mkdir()
        (base / "Salida").mkdir()
        # El config.json de prueba vive en el temporal: no se toca el real.
        modulo.CONFIG_PATH = base / "config.json"
        cliente = TestClient(modulo.app)

        print("\n== las carpetas por defecto no son las de nadie ==")
        porDefecto = cliente.get("/api/config").json()
        check("responde 200 sin config.json", "pendientes" in porDefecto)
        check("no apunta a la carpeta de una persona",
              "OneDrive-Personal" not in json.dumps(porDefecto), porDefecto)
        check("no quedan rutas fijas en el modulo",
              not hasattr(modulo, "ONEDRIVE"))

        print("\n== guardar y releer ==")
        guardado = cliente.post("/api/config", json={
            "pendientes": str(base / "Entrada"),
            "transcritas": str(base / "Salida"),
            "archivados": str(base / "NoExiste"),
        }).json()
        check("devuelve la ruta guardada",
              guardado["pendientes"] == str(base / "Entrada"), guardado)
        check("marca en verde la carpeta que existe", guardado["pendientes_ok"] is True)
        check("marca en amarillo la que no existe", guardado["archivados_ok"] is False)
        check("persiste entre llamadas",
              cliente.get("/api/config").json()["transcritas"] == str(base / "Salida"))

        print("\n== un campo vacio no borra lo ya guardado ==")
        # La interfaz reenvia las tres rutas al arrancar. Si una llega vacia,
        # perder la anterior dejaria el modo carpeta apuntando a otro lado.
        vacio = cliente.post("/api/config", json={
            "pendientes": "", "transcritas": "", "archivados": ""}).json()
        check("conserva la ruta anterior",
              vacio["pendientes"] == str(base / "Entrada"), vacio)

        print("\n== se acepta el atajo del home ==")
        conTilde = cliente.post("/api/config", json={"pendientes": "~/Audios"}).json()
        check("~ se expande a una ruta absoluta",
              conTilde["pendientes"] == str(Path.home() / "Audios"), conTilde)

    print()
    if fallos:
        print(f"FALLARON {fallos}")
        sys.exit(1)
    print("Todas las pruebas pasaron.")


main()
