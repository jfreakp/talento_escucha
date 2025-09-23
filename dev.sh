#!/bin/bash

echo "Iniciando desarrollo con Tailwind CSS..."

# Función para manejar la terminación del script
cleanup() {
    echo "Terminando procesos..."
    kill $TAILWIND_PID $DJANGO_PID 2>/dev/null
    exit 0
}

# Capturar señales de terminación
trap cleanup SIGINT SIGTERM

# Iniciar Tailwind en modo watch
echo "Iniciando Tailwind CSS en modo watch..."
npm run build-css-watch &
TAILWIND_PID=$!

# Esperar un momento para que Tailwind se inicie
sleep 2

# Iniciar Django
echo "Iniciando servidor Django..."
python manage.py runserver &
DJANGO_PID=$!

echo "Desarrollo iniciado:"
echo "- Tailwind CSS: Observando cambios en archivos CSS"
echo "- Django: http://127.0.0.1:8000/"
echo "Presiona Ctrl+C para terminar ambos procesos"

# Esperar a que termine cualquiera de los procesos
wait