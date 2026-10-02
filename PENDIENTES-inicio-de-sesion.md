# Pendientes para cerrar la página "Inicio de sesión"

Página: `docs/primeros-pasos/inicio-de-sesion.md`. Las preguntas están en `santa teresa/qa/preguntas-para-dev.md`, enviadas al equipo de desarrollo el 1 de octubre de 2026. Las respuestas de Diego del mismo día están en `santa teresa/qa/respuestas-de-diego.md`.

Este archivo está fuera de `docs/` a propósito: así no sale en el manual ni en el editor visual. Cada punto tiene en la página un comentario `<!-- PENDIENTE P-xx: ... -->` en el lugar donde va el cambio. Cuando llegue la respuesta, haz el cambio, borra el comentario y marca el punto.

## Textos por completar

| Hecho | Pregunta | Sección de la página | Qué falta |
|:-:|---|---|---|
| [ ] | P-01 | Entrar a la aplicación, paso 1 | Nombre definitivo del ícono de la app. Diego: hoy es provisional. |
| [x] | P-02 | Qué necesitas antes de entrar | Respondido: un administrador da el acceso; se entra con el correo corporativo. Texto ajustado. |
| [x] | P-04 | Qué necesitas antes de entrar y No tienes conexión | Respondido: internet solo la primera vez. Texto ajustado. |
| [ ] | P-03 | Las partes de la pantalla, fila 5 | Respondido en parte: la huella se usa después de entrar la primera vez con correo y contraseña. Texto ajustado. Falta saber si activarla será opcional. |
| [x] | P-11 | Aviso tras varios intentos fallidos | Respondido: la cuenta no se bloquea. Aviso ajustado. |
| [x] | P-16 | Olvidaste tu contraseña, paso 3 | Respondido: llega un código al correo corporativo. Texto ajustado. Falta solo la captura `olvido-paso-3.png`, abajo. |
| [x] | P-18 | Olvidaste tu contraseña, final | Respondido: si no tiene acceso a su correo corporativo, se comunica con el equipo de Santa Teresa. Texto ajustado. |
| [ ] | P-22 | No tienes conexión | Texto exacto del aviso sin conexión. |
| [ ] | P-09 | Cerrar sesión, aviso "Antes de cerrar sesión" | Por confirmar en prueba, LOGIN-060. Lo esperado es que lo guardado se envíe apenas haya señal. El aviso queda neutro: recomienda tener señal antes de cerrar sesión. |
| [x] | P-15 | Consejos de seguridad, aviso "Tu contraseña es solo tuya" | Respondido: no se promete que nadie la pedirá. Se deja el consejo de no compartirla. |
| [ ] | P-07 | Consejos de seguridad | Respondido: se cambia desde el perfil, dentro de la app. Consejo agregado. Faltan los pasos exactos y su captura. |
| [x] | P-10 | Para qué sirve | Respondido: la sesión no tiene límite. Texto ajustado: queda abierta hasta que la cierres. |

## Capturas por tomar

Van en `docs/imagenes/inicio-de-sesion/`. Solo con datos inventados, por ejemplo `qa.prueba.inexistente@example.com`, nunca con un correo o una contraseña reales.

| Hecho | Archivo | Pregunta | Qué debe mostrar | Cuándo se puede tomar |
|:-:|---|---|---|---|
| [ ] | `error-credenciales.png` | P-19 | Pantalla de inicio de sesión con un correo inventado y el aviso rojo de correo o contraseña incorrectos. | Cuando el aviso salga en español. Hoy dice "Invalid credentials". |
| [ ] | `error-sin-conexion.png` | P-22 | Pantalla de inicio de sesión con el aviso de falta de conexión y un recuadro rojo sobre el aviso. | Cuando se conozca el texto de P-22 y los mensajes estén en español. |
| [ ] | `olvido-paso-3.png` | P-16 | Pantalla donde se escribe el código que llega al correo, con recuadro rojo sobre el campo del código. | Con la cuenta y el buzón de P-17. |

Después de agregar cada captura, cambia su comentario `PENDIENTE-IMAGEN` por la imagen con `{ .captura }`, como las demás de la página.

## A tener en cuenta, sin comentario en la página

- **P-08, BUG-001.** La sección "Cerrar sesión" dice que para volver a entrar hay que escribir otra vez la contraseña. Hoy no es así: al reabrir la app entra al Home. El texto describe lo correcto; revisarlo cuando dev confirme la corrección, y no publicar el manual a vendedores antes sin hablarlo con Diego.
- **P-19 y BUG-005.** Si cambian los textos de la pantalla, por ejemplo el botón "Inicia Sesión" o "Enviar código", hay que actualizar el texto visible de la página y volver a tomar las capturas que los muestran.

## Para cerrar la página

1. Todos los puntos de arriba marcados.
2. En la página no queda ningún `<!-- PENDIENTE`.
3. `python -m mkdocs build --strict` pasa sin avisos.
