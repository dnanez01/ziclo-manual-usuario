#!/bin/bash
# Deja listo Python y MkDocs. Lo usan los archivos de la carpeta "USAR EL MANUAL" en Mac.
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo ""
  echo " Falta instalar Python en este computador."
  echo " Abre '0. Preparar este computador.command', en esta misma carpeta."
  echo ""
  exit 1
fi
if ! python3 -c "import mkdocs, material, mkdocs_print_site_plugin" >/dev/null 2>&1; then
  echo " Preparando el manual por primera vez. Espera un momento..."
  python3 -m pip install -q -r "$(dirname "$0")/../requirements.txt"
  if [ $? -ne 0 ]; then
    echo ""
    echo " No se pudo preparar. Revisa que tengas internet e inténtalo de nuevo."
    echo ""
    exit 1
  fi
fi
exit 0
