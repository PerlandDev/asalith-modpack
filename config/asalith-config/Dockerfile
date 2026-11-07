# Imagen oficial de Docker de Minecraft
FROM itzg/minecraft-server:latest

# La configuración de los mods (lado servidor) está contenida en la carpeta
# config. Al añadir mods nuevos al modpack, actualizar aquí lo que haga falta.
# El contenido se sincroniza a /data/config al arrancar el contenedor.
COPY config /config

# Expone el puerto de Minecraft (solo documentación; el contenedor
# siempre se ejecuta vía compose y solo se abre el puerto mapeado).
EXPOSE 25565
