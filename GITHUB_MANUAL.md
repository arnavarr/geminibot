# Instrucciones para subir a GitHub Manualmente

El cliente de GitHub (`gh`) no está instalado en este entorno o falló su ejecución. Sigue estos pasos para subir tu código:

1.  Ve a [GitHub.com/new](https://github.com/new) y crea un nuevo repositorio (por ejemplo, llámalo `geminibot`). **No lo inicialices con README, .gitignore ni License** (ya los tenemos localmente).
2.  Copia la URL del repositorio creado (ej. `https://github.com/TU_USUARIO/geminibot.git`).
3.  Abre tu terminal en la carpeta del proyecto y ejecuta:

```bash
# 1. Enlazar tu repositorio local con el remoto
git remote add origin https://github.com/arnavarr/geminibot.git

# 2. Renombrar la rama principal a main (estándar actual)
git branch -M main

# 3. Subir tus cambios
git push -u origin main
```

> **Nota**: Si ya habías añadido un 'origin' antes y te da error, usa `git remote set-url origin LA_NUEVA_URL`.
