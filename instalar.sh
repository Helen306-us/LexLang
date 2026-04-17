#!/bin/bash
echo "============================================="
echo " LexLang v2.0 - Instalador de dependencias"
echo "============================================="
echo ""

# Verificar Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 no está instalado."
    echo "Instálalo con: sudo apt install python3  (Linux)"
    echo "              o desde: https://www.python.org/ (Mac/Win)"
    exit 1
fi

echo "[OK] Python detectado: $(python3 --version)"
echo ""

# Actualizar pip
echo "[1/2] Actualizando pip..."
python3 -m pip install --upgrade pip
echo ""

# Instalar dependencias
echo "[2/2] Instalando dependencias desde requirements.txt..."
pip3 install -r requirements.txt
echo ""

if [ $? -eq 0 ]; then
    echo "============================================="
    echo " Instalación completada exitosamente!"
    echo " Inicia el servidor con: python3 app.py"
    echo "============================================="
else
    echo "[ERROR] Hubo un problema durante la instalación."
    exit 1
fi
