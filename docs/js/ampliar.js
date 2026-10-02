/* Ampliar capturas: al tocar una imagen se abre en grande sobre un fondo oscuro.
   Se cierra con la X, tocando fuera de la imagen o con la tecla Escape. */
(function () {
  var visor, imagen;

  function crearVisor() {
    visor = document.createElement("div");
    visor.className = "visor-captura";
    visor.setAttribute("role", "dialog");
    visor.setAttribute("aria-modal", "true");
    visor.setAttribute("aria-label", "Imagen ampliada");
    visor.innerHTML =
      '<button type="button" class="visor-cerrar" aria-label="Cerrar">&times;</button>' +
      '<img class="visor-imagen" alt="">';
    imagen = visor.querySelector(".visor-imagen");

    visor.addEventListener("click", function (e) {
      if (e.target !== imagen) cerrar();   // fondo o botón X
    });
    document.body.appendChild(visor);
  }

  function abrir(img) {
    if (!visor) crearVisor();
    imagen.src = img.currentSrc || img.src;
    imagen.alt = img.alt;
    visor.classList.add("abierto");
    document.documentElement.classList.add("visor-activo");
    visor.querySelector(".visor-cerrar").focus();
  }

  function cerrar() {
    if (!visor) return;
    visor.classList.remove("abierto");
    document.documentElement.classList.remove("visor-activo");
  }

  document.addEventListener("click", function (e) {
    var img = e.target.closest && e.target.closest(".md-typeset img.captura");
    if (img) { e.preventDefault(); abrir(img); }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") cerrar();
  });
})();
