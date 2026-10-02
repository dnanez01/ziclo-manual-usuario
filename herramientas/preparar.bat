@echo off
rem Deja listo Python y MkDocs. Lo usan los archivos de la carpeta "USAR EL MANUAL".
where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo  Falta instalar Python en este computador.
  echo  Abre "0. Preparar este computador", en esta misma carpeta.
  echo.
  pause
  exit /b 1
)
python -c "import mkdocs, material, mkdocs_print_site_plugin" >nul 2>nul
if errorlevel 1 (
  echo  Preparando el manual por primera vez. Espera un momento...
  python -m pip install -q -r "%~dp0..\requirements.txt"
  if errorlevel 1 (
    echo.
    echo  No se pudo preparar. Revisa que tengas internet e inténtalo de nuevo.
    echo.
    pause
    exit /b 1
  )
)
exit /b 0
