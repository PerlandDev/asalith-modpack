# Asalith — Modpack oficial

Modpack del servidor **Asalith**, gestionado con [packwiz](https://packwiz.infra.link/).

| | |
|---|---|
| **Minecraft** | 1.20.1 |
| **Modloader** | Forge 47.4.22 |
| **URL del pack** | `https://perlanddev.github.io/asalith-modpack/pack.toml` |
| **Web** | https://perlanddev.github.io/asalith-modpack/ |

---

## Para jugadores

La instalación recomendada usa **packwiz-installer**, que actualiza el modpack solo
cada vez que abres el juego. No hay que reinstalar nada cuando añadimos mods.

1. Instala [Prism Launcher](https://prismlauncher.org/).
2. Crea una instancia de **Minecraft 1.20.1** con **Forge**.
3. Descarga [`packwiz-installer-bootstrap.jar`](https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest)
   y ponlo dentro de la carpeta `.minecraft` de la instancia.
4. En *Editar instancia → Configuración → Ajustes de Java*, marca los argumentos
   personalizados y añade al final:

   ```
   -jar packwiz-installer-bootstrap.jar https://perlanddev.github.io/asalith-modpack/pack.toml
   ```

5. Inicia el juego.

### Alternativa sin auto-actualización

Descarga el `.mrpack` de la [última release](https://github.com/PerlandDev/asalith-modpack/releases/latest)
e impórtalo en Prism Launcher o en la app de Modrinth.

---

## Para el equipo (mantenimiento)

Necesitas [packwiz](https://packwiz.infra.link/installing/) en el `PATH`.

### Añadir mods

```bash
# Desde Modrinth (preferido: no requiere API key y permite exportar .mrpack)
packwiz modrinth add sodium
packwiz mr add https://modrinth.com/mod/lithium

# Desde CurseForge
packwiz curseforge add jei
packwiz cf add https://www.curseforge.com/minecraft/mc-mods/journeymap
```

packwiz pregunta qué versión usar y resuelve las dependencias automáticamente.

### Otras operaciones habituales

```bash
packwiz update --all          # actualizar todos los mods
packwiz update sodium         # actualizar uno concreto
packwiz remove sodium         # quitar un mod
packwiz refresh               # regenerar index.toml (¡obligatorio antes de commitear!)
packwiz modrinth export       # generar un .mrpack en local
```

### Lados cliente/servidor

Los mods que solo van en un lado se marcan editando su `.pw.toml`:

```toml
side = "client"   # o "server", o "both" (por defecto)
```

Así el servidor no descarga shaders ni mods de interfaz.

### Flujo de trabajo

1. Añade o actualiza mods con los comandos de arriba.
2. Ejecuta `packwiz refresh`.
3. Commitea y haz push a `main`.
4. GitHub Actions despliega el pack en GitHub Pages. Los jugadores lo reciben al
   reiniciar el launcher.

Para publicar un `.mrpack` en releases, crea una etiqueta:

```bash
git tag v1.0.0 && git push --tags
```

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
scripts/             Utilidades de build (generación de mods.json)
.github/workflows/   Despliegue en Pages, export de .mrpack y validación en PRs
.packwizignore       Ficheros del repo que NO forman parte del modpack
```

## Automatizaciones

| Workflow | Cuándo | Qué hace |
|---|---|---|
| `deploy-pages.yml` | push a `main` | Publica el pack y la web en GitHub Pages |
| `release-mrpack.yml` | etiquetas `v*` | Exporta `Asalith.mrpack` y lo adjunta a la release |
| `validate.yml` | pull requests | Falla si el `index.toml` está desactualizado |
