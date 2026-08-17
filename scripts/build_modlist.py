#!/usr/bin/env python3
"""Genera mods.json a partir de los archivos .pw.toml del modpack.

La web (index.html) lo carga para mostrar la lista de mods siempre al día,
sin necesidad de commitear una lista a mano.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARPETAS = ["mods", "resourcepacks", "shaderpacks", "datapacks"]

SITIOS = {
    "modrinth": ("Modrinth", "https://modrinth.com/project/{id}"),
    "curseforge": ("CurseForge", "https://www.curseforge.com/projects/{id}"),
}


def leer_entrada(archivo: Path) -> dict:
    datos = tomllib.loads(archivo.read_text(encoding="utf-8"))
    update = datos.get("update", {})

    fuente, enlace = None, None
    for clave, (nombre, plantilla) in SITIOS.items():
        if clave in update:
            fuente = nombre
            ident = update[clave].get("mod-id") or update[clave].get("project-id")
            if ident:
                enlace = plantilla.format(id=ident)
            break

    return {
        "nombre": datos.get("name", archivo.stem),
        "archivo": datos.get("filename", ""),
        "carpeta": archivo.parent.name,
        "lado": datos.get("side", "both"),
        "fuente": fuente,
        "enlace": enlace,
    }


def main() -> None:
    entradas = []
    for carpeta in CARPETAS:
        ruta = ROOT / carpeta
        if not ruta.is_dir():
            continue
        for archivo in sorted(ruta.glob("*.pw.toml")):
            entradas.append(leer_entrada(archivo))

    entradas.sort(key=lambda e: e["nombre"].lower())

    pack = tomllib.loads((ROOT / "pack.toml").read_text(encoding="utf-8"))
    salida = {
        "pack": {
            "nombre": pack.get("name"),
            "version": pack.get("version"),
            "minecraft": pack.get("versions", {}).get("minecraft"),
            "forge": pack.get("versions", {}).get("forge"),
        },
        "total": len(entradas),
        "entradas": entradas,
    }

    (ROOT / "mods.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"mods.json generado con {len(entradas)} entradas.")


if __name__ == "__main__":
    main()
