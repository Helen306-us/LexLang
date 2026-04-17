@echo off
echo =============================================
echo  LexLang v2.0 - Instalador de dependencias
echo =============================================
echo.

REM Verificar que Python este instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Descargalo desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detectado:
python --version
echo.

REM Actualizar pip
echo [1/2] Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias
echo [2/2] Instalando dependencias desde requirements.txt...
pip install -r requirements.txt
echo.

if %errorlevel% equ 0 (
    echo =============================================
    echo  Instalacion completada exitosamente!
    echo  Inicia el servidor con: python app.py
    echo =============================================
) else (
    echo [ERROR] Hubo un problema durante la instalacion.
)

pause
