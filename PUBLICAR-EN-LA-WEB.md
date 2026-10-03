# Publicar el manual en la web y editarlo desde el navegador

El manual queda en internet y las personas autorizadas pueden editarlo desde el navegador, sin instalar nada.
Para entrar al editor (`/editar/`, o el enlace **Iniciar sesión** del manual) se necesitan dos cosas:

1. **El correo corporativo.** Debe terminar en `@nextepinnovation.com`.
2. **La clave de edición.** Es una clave compartida que Diego les da a los editores.

El servidor revisa las dos en cada llamada, nunca el navegador. Si algo falla, responde
"Usa tu correo corporativo" o "Clave incorrecta" después de esperar 1 segundo, para frenar intentos al azar.
El correo y la clave se guardan solo en la pestaña (`sessionStorage`). Al cerrarla o tocar **Salir**, se borran.

## Cómo funciona

| Pieza | Qué hace |
|---|---|
| GitHub (`dnanez01/ziclo-manual-usuario`) | Guarda el manual. Cada guardado es un commit con el mensaje "Edición de <correo> desde la web". |
| Cloudflare Pages | Construye el sitio con `mkdocs build` después de cada commit. Tarda 1 o 2 minutos. |
| Pages Functions (`functions/api/[[ruta]].js`) | Es el backend del editor. Revisa el correo y la clave, y lee y guarda en GitHub con el token. El token nunca llega al navegador. |
| Editor web (`docs/editar/index.html`) | Es una copia del editor de siempre que habla con `/api/...` en vez de con `editor.py`. |

**Por qué el editor está en `docs/editar/`:** MkDocs solo convierte en páginas los archivos `.md`. Un `.html`
dentro de `docs/` lo copia tal cual a `site/editar/`, sin meterlo en el menú ni en el buscador. Si estuviera fuera
de `docs/`, no llegaría a la carpeta `site` que publica Cloudflare. Por eso no se usa `exclude_docs`: con esa
opción el archivo no se publicaría.

`herramientas/editor.html` y `editor.py` no cambiaron. El editor local sigue funcionando igual.

---

## 1. Repositorio (ya hecho)

Para referencia, estos son los comandos con los que se creó el repositorio desde esta carpeta:

```powershell
cd "C:\Users\diego\OneDrive\Desktop\Nextep\santa teresa\documentacion\manual-usuario\sistema"
git init -b main
git add .
git commit -m "Manual de usuario"
git remote add origin https://github.com/dnanez01/ziclo-manual-usuario.git
git push -u origin main
```

El archivo `.gitignore` deja fuera estas carpetas:

- `site/`
- `__pycache__/`
- `herramientas/respaldos/`
- `herramientas/raw/`: capturas originales, unos 20 MB.

La carpeta `herramientas/papelera/` sí se sube.

## 2. Token de GitHub de grano fino

1. En GitHub, ve a **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Llena estos datos:
   - **Token name:** `editor-manual-web`
   - **Expiration:** 1 año. Anota la fecha para renovarlo.
   - **Resource owner:** `dnanez01`
   - **Repository access:** *Only select repositories* → `ziclo-manual-usuario`
   - **Repository permissions → Contents:** **Read and write**. *Metadata: Read* se marca solo.
3. Toca **Generate token** y copia el token. No lo guardes en ningún archivo: se pega solo en Cloudflare, en el paso 4.

## 3. Proyecto en Cloudflare Pages

1. Ve a **Workers & Pages → Create → Pages → Connect to Git** y elige `ziclo-manual-usuario`.
2. Completa la configuración:
   - **Production branch:** `main`
   - **Framework preset:** None
   - **Build command:** `pip install -r requirements.txt && mkdocs build`
   - **Build output directory:** `site`
   - **Root directory:** déjalo vacío.
   - En **Environment variables**, agrega `PYTHON_VERSION` = `3.12`.
3. Toca **Save and Deploy**.

`requirements.txt` trae todo con versiones fijas: `mkdocs`, `mkdocs-material` y `mkdocs-print-site-plugin`.
No depende de nada del computador: la letra Montserrat va dentro de `docs/estilos/fuentes`.

## 4. Variables y secretos

En el proyecto, ve a **Settings → Variables and Secrets** y agrega estas variables en **Production**:

| Nombre | Tipo | Valor |
|---|---|---|
| `GITHUB_TOKEN` | **Secret** | el token del paso 2 |
| `CLAVE_EDITOR` | **Secret** | la clave de edición. Que sea larga, por ejemplo tres palabras y un número. |
| `GITHUB_REPO` | Text | `dnanez01/ziclo-manual-usuario` |
| `GITHUB_BRANCH` | Text | `main` |

Después ve a **Deployments**, abre el último despliegue y toca **Retry deployment** para que tome los valores.

No cargues estas variables en **Preview**. Así, las versiones de prueba no pueden editar el manual.

### Probar

1. Abre el manual y toca **Iniciar sesión**.
2. Escribe tu correo corporativo y la clave, y toca **Entrar**.
3. Edita algo y toca **Guardar**.
4. En GitHub debe aparecer el commit "Edición de tu-correo desde la web". En 1 o 2 minutos el cambio se ve en el manual.

## 5. Cambiar la clave, agregar o quitar personas

- **Cambiar la clave:**
  1. Ve a **Settings → Variables and Secrets**.
  2. Edita `CLAVE_EDITOR` y guarda.
  3. Ve a **Deployments**, abre el último despliegue y toca **Retry deployment**.

  En 1 o 2 minutos la clave anterior deja de servir. Quien tenga el editor abierto vuelve a la pantalla de entrada.
- **Agregar a alguien:** dale la clave. Tiene que tener correo `@nextepinnovation.com`.
- **Quitar a alguien:** cambia la clave y dásela al resto.
- **Permitir otro dominio de correo:** hay que cambiar `RX_CORREO` en `functions/api/[[ruta]].js` y la revisión del correo en `docs/editar/index.html`. Pide ayuda técnica.

## 6. Opcional: Cloudflare Access (requiere tarjeta en Cloudflare)

Cloudflare Access agrega un código de un solo uso que llega al correo, antes del editor. El plan Zero Trust es
gratis hasta 50 personas, pero Cloudflare pide registrar una tarjeta. Por eso hoy no se usa. Si algún día se activa:

1. Ve a **Zero Trust → Settings → Authentication → Login methods** y agrega **One-time PIN**.
2. Ve a **Access → Applications → Self-hosted** y crea la aplicación:
   - Dominio del sitio, con las rutas `editar*` y `api/*`.
   - Política **Allow** con **Include → Emails ending in** `@nextepinnovation.com`.
3. Para personalizar la pantalla, ve a **Settings → Custom Pages → Login page**. Puedes cambiar el nombre, el logo, el color y el texto del encabezado, por ejemplo "Ingrese su correo corporativo".
4. Agrega en Pages las variables `ACCESS_TEAM_DOMAIN`, por ejemplo `tuequipo.cloudflareaccess.com`, y `ACCESS_AUD`, que es el *Application Audience Tag* de la aplicación. Con ellas, el servidor exige además la firma de Access. El correo y la clave se siguen pidiendo igual.

## Bueno saber

- **Historial:** en el editor, **Versiones** muestra quién guardó y cuándo, y permite volver a una versión anterior.
- **Papelera:** las páginas eliminadas van a `herramientas/papelera/` y se recuperan desde el editor.
- **Conflictos:** si dos personas editan la misma página, la segunda que guarda ve un aviso y no pisa el cambio de la otra.
- **Editor local y editor web a la vez:** el editor local escribe en esta carpeta, no en GitHub. Si se usa el local:
  - antes de editar, corre `git pull`;
  - después, corre `git add . && git commit -m "Edición local" && git push`.
- **Límite de builds:** el plan gratis de Pages permite 500 builds al mes. Cada guardado es un build.

## Mantenimiento

### El token de GitHub vence en octubre de 2027

El editor web guarda los cambios en GitHub con un token de la cuenta **dnanez01**. Se creó el 2 de octubre de 2026 con vencimiento de 1 año. Cuando venza, el editor mostrará un error al guardar, aunque el manual se siga viendo. Para renovarlo:

1. Entra a GitHub con la cuenta **dnanez01** y abre https://github.com/settings/personal-access-tokens.
2. Abre el token **Editor web del manual** y toca **Regenerate token**. Si no existe, crea uno nuevo así:
   - **Repository access:** solo `ziclo-manual-usuario`.
   - **Permissions → Contents:** Read and write.
3. Copia el token nuevo.
4. En Cloudflare, entra a **Workers & Pages → ziclo-manual-usuario → Settings → Variables and Secrets**, edita `GITHUB_TOKEN` y pega el nuevo valor.
5. En **Deployments**, toca **⋯ → Retry deployment** en el último despliegue.

### Si al guardar aparece "GitHub 403"

El token no tiene permiso de escritura. En GitHub, edita el token y revisa que **Contents** esté en **Read and write** y que el repositorio `ziclo-manual-usuario` esté incluido. El cambio aplica al instante y no hace falta tocar Cloudflare.

### Cuentas que usa el manual web

- **GitHub:** cuenta de la empresa **dnanez01**, en el repositorio `dnanez01/ziclo-manual-usuario`.
- **Cloudflare:** cuenta con el correo de la empresa, en el proyecto de Pages `ziclo-manual-usuario`.
- **Clave de edición:** el secreto `CLAVE_EDITOR` en Cloudflare. Se cambia editando ese secreto y haciendo **Retry deployment**.
