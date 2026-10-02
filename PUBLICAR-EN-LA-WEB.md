# Publicar el manual en la web y editarlo desde el navegador

Con esto el manual queda en internet y las personas autorizadas lo pueden editar desde el navegador,
sin instalar nada. Para entrar al editor se necesitan dos cosas:

1. **El correo corporativo.** Cloudflare le manda un código de un solo uso a ese correo.
2. **La clave de edición.** Es una clave compartida que tú les das a los editores. La revisa el servidor, nunca el navegador.

## Cómo funciona

| Pieza | Qué hace |
|---|---|
| GitHub (`dnanez01/ziclo-manual-usuario`) | Guarda el manual. Cada vez que alguien guarda en el editor, se crea un commit con el mensaje "Edición de <correo> desde la web". |
| Cloudflare Pages | Construye el sitio con `mkdocs build` después de cada commit y lo publica. Tarda 1 o 2 minutos. |
| Cloudflare Access | Protege `/editar` y `/api`: pide el correo y manda un código de un solo uso. |
| Pages Functions (`functions/api/[[ruta]].js`) | Es el backend del editor. Lee y guarda en GitHub con el token, que nunca llega al navegador. Revisa que la solicitud traiga el correo de Access y la clave de edición. |
| Editor web (`docs/editar/index.html`) | Es una copia del editor de siempre que habla con `/api/...` en vez de con `editor.py`. |

**Por qué el editor está en `docs/editar/`:** MkDocs solo convierte en páginas los archivos `.md`. Un `.html`
dentro de `docs/` lo copia tal cual al sitio, así que queda en `/editar/` sin tocar su diseño ni salir en el menú
ni en el buscador. Si estuviera fuera de `docs/`, no llegaría a la carpeta `site` que publica Cloudflare.
Por eso no se usa `exclude_docs`: con esa opción el archivo no se publicaría.

`herramientas/editor.html` y `editor.py` no cambiaron. El editor local sigue funcionando igual en el computador.

---

## 1. Crear el repositorio y subir la carpeta

1. Entra a <https://github.com/new> con la cuenta `dnanez01`.
2. Llena estos datos:
   - **Repository name:** `ziclo-manual-usuario`
   - **Private**
   - No marques README, .gitignore ni licencia.
3. Toca **Create repository**.
4. En el computador, abre PowerShell y pega lo siguiente:

```powershell
cd "C:\Users\diego\OneDrive\Desktop\Nextep\santa teresa\documentacion\manual-usuario\sistema"
git init -b main
git add .
git commit -m "Manual de usuario"
git remote add origin https://github.com/dnanez01/ziclo-manual-usuario.git
git push -u origin main
```

El archivo `.gitignore` deja fuera estas carpetas:

- `site/`: se genera sola.
- `herramientas/respaldos/`: respaldos locales.
- `herramientas/raw/`: capturas originales sin recortar, unos 20 MB.
- `__pycache__/`

Sí se sube `herramientas/papelera/`, porque el editor web manda ahí las páginas eliminadas.

## 2. Crear el token de GitHub de grano fino

1. En GitHub, ve a tu foto y luego a **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Llena estos datos:
   - **Token name:** `editor-manual-web`
   - **Expiration:** 1 año. Anota la fecha para renovarlo.
   - **Resource owner:** `dnanez01`
   - **Repository access:** *Only select repositories* → `ziclo-manual-usuario`
   - **Permissions → Repository permissions → Contents:** **Read and write**. *Metadata: Read* se marca solo.
3. Toca **Generate token** y copia el token. No lo guardes en ningún archivo. Lo pegarás solo en Cloudflare, en el paso 4.

## 3. Crear el proyecto en Cloudflare Pages

1. Entra a <https://dash.cloudflare.com> y ve a **Workers & Pages → Create → Pages → Connect to Git**.
2. Conecta GitHub y elige `ziclo-manual-usuario`.
3. Completa la configuración del build:
   - **Production branch:** `main`
   - **Framework preset:** None
   - **Build command:** `pip install -r requirements.txt && mkdocs build`
   - **Build output directory:** `site`
   - **Root directory:** déjalo vacío.
   - En **Environment variables**, agrega `PYTHON_VERSION` = `3.12`.
4. Toca **Save and Deploy**. La dirección queda como `https://ziclo-manual-usuario.pages.dev`, aunque puede variar si ese nombre ya está tomado.

`requirements.txt` ya trae todo lo necesario con versiones fijas: `mkdocs`, `mkdocs-material` y `mkdocs-print-site-plugin`.
No depende de nada del computador: la letra Montserrat está dentro de `docs/estilos/fuentes`.

## 4. Cargar las variables y los secretos

En el proyecto, ve a **Settings → Variables and Secrets** y agrega estas variables en **Production**:

| Nombre | Tipo | Valor |
|---|---|---|
| `GITHUB_TOKEN` | **Secret** | el token del paso 2 |
| `CLAVE_EDITOR` | **Secret** | la clave de edición que elijas. Que sea larga, por ejemplo tres palabras y un número. |
| `GITHUB_REPO` | Text | `dnanez01/ziclo-manual-usuario` |
| `GITHUB_BRANCH` | Text | `main` |

Después ve a **Deployments**, abre el último despliegue y toca **Retry deployment** para que tome las variables.

Dos detalles:

- No cargues estas variables en **Preview**. Así, las versiones de prueba no pueden editar el manual.
- Opcional, pero recomendado: cuando termines el paso 5, agrega dos variables más para que el servidor verifique también la firma de Access:
  - `ACCESS_TEAM_DOMAIN`, por ejemplo `tuequipo.cloudflareaccess.com`.
  - `ACCESS_AUD`: es el *Application Audience (AUD) Tag* que aparece en la aplicación de Access.

## 5. Configurar Cloudflare Access

1. En el panel de Cloudflare, entra a **Zero Trust**. La primera vez:
   - Elige un nombre de equipo.
   - Elige el plan **Free**, que sirve hasta 50 personas. Puede que te pida una tarjeta aunque sea gratis.
2. Activa el código por correo: ve a **Settings → Authentication → Login methods → Add new → One-time PIN**.
3. Crea la aplicación: ve a **Access → Applications → Add an application → Self-hosted** y llena estos datos:
   - **Application name:** `Editor del manual`
   - **Session duration:** 24 hours
   - **Public hostname**, agrega dos entradas con el mismo dominio, `ziclo-manual-usuario.pages.dev`:
     - Path `editar*`
     - Path `api/*`
   - **Identity providers:** solo *One-time PIN*. Activa **Instant Auth** para que vaya directo al correo.
4. Crea la política, con **Action: Allow**:
   - **Opción recomendada:** en **Include**, elige *Emails ending in* y escribe `@nextepinnovation.com`. Así cualquiera con correo de la empresa recibe el código, y para editar necesita además la clave.
   - **Alternativa:** en **Include**, elige *Everyone*. Cualquier correo recibe el código, y la clave de edición es la que realmente decide quién edita.
5. Protege también las versiones de prueba: en Pages, ve a **Settings → General → Access policy (Preview deployments) → Enable**.

### Personalizar la pantalla del correo

Ve a **Zero Trust → Settings → Custom Pages → Login page** (en algunas versiones del panel se llama *Reusable components → Custom pages*). Ahí puedes cambiar:

- el nombre de la organización;
- el logo, con una URL a la imagen;
- el color de fondo;
- el texto de encabezado: pon **"Ingrese su correo corporativo"**;
- el texto del pie.

Hasta donde sé, esto se puede hacer en el plan gratis. Lo que no se puede cambiar:

- La etiqueta del campo del correo y el correo con el código. Los pone Cloudflare y salen en el idioma del navegador.
- Las páginas completamente propias en HTML. Son de planes de pago.

Si al entrar ves que algo de esto está bloqueado, es un límite del plan.

### Probar

1. Abre el manual y toca **Iniciar sesión**, arriba a la derecha.
2. Escribe tu correo y el código que te llega.
3. Aparece el editor y pide **"Ingresa la clave de edición"**.
4. Edita algo y toca **Guardar**.
5. En GitHub debe aparecer el commit "Edición de tu-correo desde la web". En 1 o 2 minutos el cambio se ve en el manual.

## 6. Agregar o quitar personas

- **Agregar a alguien con correo corporativo:** dale la clave de edición. Con la política de dominios no hay que tocar nada más.
- **Agregar a alguien con un correo de otro dominio:** en la política de Access, agrega en **Include** una regla *Emails* con su correo. Luego dale la clave.
- **Quitar a alguien:**
  1. Cambia `CLAVE_EDITOR` en **Settings → Variables and Secrets**.
  2. Toca **Retry deployment**.
  3. Dale la clave nueva al resto.
  4. Si quieres cerrarle la sesión de inmediato, ve a **Zero Trust → My Team → Users**, elige a la persona y toca **Revoke sessions**.
  5. Para bloquear a una persona aunque tenga correo corporativo, agrega en la política una regla **Exclude → Emails** con su correo.

## Bueno saber

- **Historial:** cada guardado es un commit. En el editor, **Versiones** muestra quién guardó y cuándo, y permite volver a una versión anterior.
- **Papelera:** las páginas eliminadas van a `herramientas/papelera/` y se pueden recuperar desde el editor.
- **Conflictos:** si dos personas editan la misma página, la segunda que guarda ve un aviso y no pisa el cambio de la otra.
- **Editor local y editor web a la vez:** el editor local de `herramientas/` escribe en esta carpeta, no en GitHub. Si se usa el local:
  - antes de editar, corre `git pull`;
  - después, corre `git add . && git commit -m "Edición local" && git push`.

  Lo más simple es usar solo el editor web.
- **Límite de builds:** el plan gratis de Pages permite 500 builds al mes. Cada guardado es un build.
- **Salir:** el botón **Salir** del editor lleva a `/cdn-cgi/access/logout`.
