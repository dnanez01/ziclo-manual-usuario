# Importante: lo que hay que cuidar del manual web

Manual publicado: https://ziclo-manual-usuario.pages.dev
Editor: https://ziclo-manual-usuario.pages.dev/editar/, o el enlace **Iniciar sesión** del manual.
La guía completa de instalación y mantenimiento está en [PUBLICAR-EN-LA-WEB.md](PUBLICAR-EN-LA-WEB.md).

## Fechas

- **1 de octubre de 2027: vence el token de GitHub** llamado "clave edicion", de la cuenta dnanez01. Si no se renueva, el manual se sigue viendo, pero **el editor no puede guardar**. Renuévalo antes de esa fecha siguiendo la sección "Mantenimiento" de la guía.

## Quién puede editar

- Puede entrar cualquier correo que termine en **@nextepinnovation.com** y conozca la **clave de edición**.
- La clave se revisa en el servidor de Cloudflare y no aparece en el código del sitio.
- Si la clave se filtra o se va alguien del equipo, **cambia la clave**: en Cloudflare entra a **Workers & Pages → ziclo-manual-usuario → Settings → Variables and Secrets**, edita `CLAVE_EDITOR` y haz **Deployments → ⋯ → Retry deployment**.
- Usa una clave larga, de 12 caracteres o más, y no la mandes por grupos abiertos.

## Cuentas

| Servicio | Cuenta | Para qué |
|---|---|---|
| GitHub | dnanez01, cuenta de la empresa | Guarda el contenido del manual y su historial |
| Cloudflare | Correo de la empresa | Publica el sitio y revisa la clave de edición |

- Si la persona que administra la cuenta de Cloudflare se va, primero invita a otra persona de la empresa como administradora, en **Manage Account → Members**.
- No borres el proyecto de Pages ni el repositorio: el manual dejaría de verse.

## Cosas que se rompen fácil

- **No edites los mismos archivos al mismo tiempo desde el editor web y desde el editor de escritorio.** Lo recomendado es editar solo por la web. Si alguien usa el editor de escritorio, antes de empezar tiene que bajar los cambios con `git pull`, y al terminar subirlos con `git push`.
- **Error "GitHub 403" al guardar:** el token perdió el permiso de escritura o venció. Revisa la sección "Mantenimiento" de la guía.
- **Error "Clave incorrecta" o "Usa tu correo corporativo":** revisa el correo y la clave.
- **Cloudflare tiene un límite de 500 publicaciones al mes en el plan gratis.** Cada guardado es una publicación. Para un manual es más que suficiente, pero no hay que guardar a cada letra.
- **Los scripts `.sh` y `.command` tienen que quedar con saltos de línea de Mac.** El archivo `.gitattributes` ya lo controla, así que no lo borres.
- Las copias de respaldo del editor de escritorio y las capturas originales sin recortar no se suben a GitHub; quedan solo en el computador donde se crearon.
