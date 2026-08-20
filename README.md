# Asalith Fields — Modpack oficial

Modpack del servidor **Asalith**, gestionado con [packwiz](https://packwiz.infra.link/).

| | |
|---|---|
| **Minecraft** | 1.20.1 |
| **Modloader** | Forge 47.4.22 |
| **Web** | https://perlanddev.github.io/asalith-modpack/ |
| **Descargas** | [Última release](https://github.com/PerlandDev/asalith-modpack/releases/latest) |

---

## Para jugadores

Toda la instalación parte del archivo **`.mrpack`** que se publica en cada release.
Las instrucciones detalladas, paso a paso y por lanzador, están en la web:

**https://perlanddev.github.io/asalith-modpack/**

En resumen:

- **Modrinth App** (recomendado) — importa el `.mrpack` desde el botón `+` → *Import from file*.
- **Prism Launcher** — *Añadir instancia* → pestaña *Importar* → selecciona el `.mrpack`.
- **TLauncher** — no admite `.mrpack`. Usa `Asalith-manual.zip`, que trae las carpetas
  `mods` y `config` ya preparadas para copiarlas dentro de `.minecraft`.

Descarga siempre desde la **última release**: los `.mrpack` de releases antiguas
siguen accesibles en GitHub y tienen las versiones de mods de aquel momento.

Para **actualizar** a una versión nueva no basta con volver a importar el `.mrpack`
encima: borra la instancia (o la carpeta `mods` completa, si instalaste a mano) y
vuelve a instalar. Si se mezclan mods de dos versiones el cliente no arranca o el
servidor lo rechaza con *«Incompatible FML modded server»*.

---

## Para el equipo (mantenimiento)

Necesitas [packwiz](https://packwiz.infra.link/installing/) en el `PATH`.

### Añadir mods

```bash
# Desde Modrinth (preferido: es lo que permite exportar el .mrpack)
packwiz modrinth add sodium
packwiz mr add https://modrinth.com/mod/lithium

# Desde CurseForge
packwiz curseforge add jei
packwiz cf add https://www.curseforge.com/minecraft/mc-mods/journeymap
```

packwiz pregunta qué versión usar y resuelve las dependencias automáticamente.
Si un mod no aparece, casi siempre es que no tiene versión para Forge 1.20.1.

### Otras operaciones habituales

```bash
packwiz update --all          # actualizar todos los mods
packwiz update sodium         # actualizar uno concreto
packwiz remove sodium         # quitar un mod
packwiz refresh               # regenerar index.toml (¡obligatorio antes de commitear!)
packwiz modrinth export       # generar un .mrpack en local para probar
```

### Lados cliente/servidor

Los mods que solo van en un lado se marcan editando su `.pw.toml`:

```toml
side = "client"   # o "server", o "both" (por defecto)
```

Así el servidor no descarga shaders ni mods de interfaz.

### Publicar una versión

Las descargas se generan solas al crear una etiqueta:

```bash
git tag v1.0.0 && git push --tags
```

Eso publica una release con `Asalith.mrpack` y `Asalith-manual.zip`.

### Recursos de marca

La insignia, el favicon y la imagen de previsualización se generan desde un único
script, para que el SVG y los PNG no se desincronicen:

```bash
python scripts/build_brand_assets.py --preview
```

`--preview` añade `assets/preview-badge.png`, que sirve solo para revisar el
dibujo a ojo y no se publica.

### Flujo de trabajo

1. Añade o actualiza mods con los comandos de arriba.
2. Ejecuta `packwiz refresh`.
3. Commitea y haz push a `main`. La web se actualiza sola.
4. Cuando quieras publicar para los jugadores, crea una etiqueta `v*`.

---

## Estructura del repositorio

```
pack.toml            Metadatos del pack (versiones, opciones)
index.toml           Índice generado por packwiz — no editar a mano
mods/                Un .pw.toml por mod
config/              Ficheros de configuración que se distribuyen a los clientes
datapacks/           Datapacks del pack
resourcepacks/       Packs de recursos
shaderpacks/         Shaders
index.html           Web pública con instrucciones y lista de mods
assets/              Insignia, favicon e imagen de previsualización
scripts/             Generación de mods.json y de los recursos de marca
.github/workflows/   Despliegue, publicación de descargas y validación
.packwizignore       Ficheros del repo que NO forman parte del modpack
```

## Automatizaciones

| Workflow | Cuándo | Qué hace |
|---|---|---|
| `deploy-pages.yml` | push a `main` | Publica la web y el pack en GitHub Pages |
| `release-mrpack.yml` | etiquetas `v*` | Publica `Asalith.mrpack` y `Asalith-manual.zip` |
| `validate.yml` | pull requests | Falla si el `index.toml` está desactualizado |
