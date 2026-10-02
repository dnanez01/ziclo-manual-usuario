/* Enlace discreto "Iniciar sesión" en el encabezado del manual publicado en la web.
   Lleva al editor (/editar/), que está protegido con el correo corporativo (Cloudflare Access).
   No aparece cuando el manual se abre desde el computador (archivo local), porque ahí no hay editor web. */
(function () {
  if (!/^https?:$/.test(location.protocol) || /^(localhost|127\.0\.0\.1)$/.test(location.hostname)) return;
  var cab = document.querySelector(".md-header__inner");
  if (!cab || document.querySelector(".enlace-sesion")) return;
  var estilo = document.createElement("style");
  estilo.textContent =
    ".enlace-sesion{display:inline-flex;align-items:center;gap:.35rem;margin:0 .4rem;padding:.25rem .6rem;" +
    "border:1px solid currentColor;border-radius:.2rem;color:inherit;font-size:.64rem;white-space:nowrap;opacity:.8}" +
    ".enlace-sesion:hover,.enlace-sesion:focus{opacity:1;color:inherit}" +
    ".enlace-sesion svg{width:.9rem;height:.9rem;fill:currentColor}" +
    "@media screen and (max-width:44.9375em){.enlace-sesion span{display:none}.enlace-sesion{border:0;padding:.25rem}}" +
    "@media print{.enlace-sesion{display:none}}";
  document.head.appendChild(estilo);
  var a = document.createElement("a");
  a.className = "enlace-sesion";
  a.href = "/editar/";
  a.title = "Editar el manual (solo personas autorizadas)";
  a.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4a4 4 0 1 1 0 8 4 4 0 0 1 0-8m0 10c4.42 0 8 1.79 8 4v2H4v-2c0-2.21 3.58-4 8-4"/></svg><span>Iniciar sesión</span>';
  var busqueda = cab.querySelector(".md-search");
  cab.insertBefore(a, busqueda || null);
})();
