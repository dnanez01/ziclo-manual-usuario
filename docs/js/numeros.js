/* Tablas "Las partes de la pantalla": el número de la primera columna se muestra dentro de un
   círculo rojo, igual al de la captura. Aplica solo a las tablas cuyo primer título es "#". */
(function () {
  function marcar() {
    document.querySelectorAll(".md-typeset table").forEach(function (tabla) {
      var titulo = tabla.querySelector("thead th");
      if (!titulo || titulo.textContent.trim() !== "#") return;
      tabla.setAttribute("data-partes", "");   // sin clase: MkDocs solo da estilo a tablas sin clase
      tabla.querySelectorAll("tbody tr").forEach(function (fila) {
        var celda = fila.cells[0], n = celda ? celda.textContent.trim() : "";
        if (/^\d{1,2}$/.test(n) && !celda.querySelector(".numero-captura")) {
          celda.innerHTML = '<span class="numero-captura">' + n + "</span>";
        }
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", marcar);
  else marcar();
})();
