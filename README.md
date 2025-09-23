# Talento Escucha - Django + Tailwind CSS

## 🎯 Configuración Completada

Este proyecto Django está configurado con **Tailwind CSS v4.1.13** y listo para desarrollar con estilos modernos.

## 🚀 Comandos Importantes

### Desarrollo Normal
```bash
# Regenerar CSS (ejecutar después de agregar nuevas clases)
npm run build-css

# Observar cambios automáticamente
npm run build-css-watch

# Ejecutar servidor Django
python manage.py runserver
```

## � Solución de Problemas

### ❌ Los estilos no se muestran

**Problema:** Los botones y elementos no tienen los estilos de Tailwind aplicados.

**Solución:**
1. **Regenerar el CSS después de agregar nuevas clases:**
   ```bash
   npm run build-css
   ```

2. **Verificar que el CSS se está cargando:**
   - Ir a `http://127.0.0.1:8000/`
   - Abrir DevTools (F12)
   - Verificar en Network que `static/css/output.css` se carga con código 200

3. **Limpiar caché del navegador:**
   - Ctrl+F5 (recarga forzada)
   - O borrar caché del navegador

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <tu-repositorio>
   cd talento_escucha
   ```

2. **Configurar el entorno virtual de Python**
   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias de Python**
   ```bash
   pip install django
   ```

4. **Instalar dependencias de Node.js**
   ```bash
   npm install
   ```

5. **Aplicar migraciones de Django**
   ```bash
   python manage.py migrate
   ```

## 🔧 Desarrollo

### Opción 1: Scripts Automatizados

#### Para Windows (PowerShell)
```powershell
.\dev.ps1
```

#### Para Linux/Mac
```bash
chmod +x dev.sh
./dev.sh
```

### Opción 2: Comandos Manuales

#### Terminal 1 - Tailwind CSS (Modo Watch)
```bash
npm run build-css-watch
```

#### Terminal 2 - Django Server
```bash
python manage.py runserver
```

### Comandos Disponibles

- `npm run build-css` - Construir CSS una sola vez
- `npm run build-css-watch` - Construir CSS en modo watch
- `python manage.py runserver` - Iniciar servidor Django

## 📁 Estructura del Proyecto

```
talento_escucha/
├── static/
│   ├── css/
│   │   ├── input.css       # Archivo fuente Tailwind
│   │   └── output.css      # CSS compilado
│   └── js/
├── templates/
│   └── base.html           # Plantilla base con Tailwind
├── talento_escucha/
│   ├── settings.py         # Configuración Django
│   ├── urls.py            # URLs del proyecto
│   ├── views.py           # Vistas del proyecto
│   └── ...
├── package.json           # Dependencias Node.js
├── dev.ps1               # Script desarrollo Windows
├── dev.sh                # Script desarrollo Linux/Mac
└── README.md             # Este archivo
```

## 🎨 Uso de Tailwind CSS

### Ejemplo básico en plantillas
```html
<!-- templates/mi_template.html -->
{% extends 'base.html' %}

{% block content %}
<div class="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
    <h1 class="text-3xl font-bold text-gray-800 mb-4">Mi Página</h1>
    <p class="text-gray-600 leading-relaxed">
        Contenido de la página con estilos de Tailwind CSS.
    </p>
    
    <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4 transition duration-200">
        Botón de Ejemplo
    </button>
</div>
{% endblock %}
```

### Agregando estilos personalizados
Si necesitas estilos personalizados, edita `static/css/input.css`:

```css
@import "tailwindcss";

/* Estilos personalizados aquí */
.mi-clase-personalizada {
    @apply bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-lg;
}
```

## 🔥 Desarrollo en Tiempo Real

Con los scripts de desarrollo, tanto Tailwind CSS como Django se recargarán automáticamente:

- **Tailwind**: Recompila automáticamente cuando cambias clases CSS
- **Django**: Recarga automáticamente cuando cambias archivos Python

## 📝 Notas

- Los archivos estáticos se sirven desde la carpeta `static/`
- Las plantillas están en la carpeta `templates/`
- El archivo `output.css` se regenera automáticamente, no lo edites manualmente
- Para producción, recuerda ejecutar `npm run build-css` para optimizar el CSS

## 🚀 Próximos Pasos

1. Crear apps Django específicas para tu proyecto
2. Configurar formularios con `@tailwindcss/forms`
3. Agregar componentes JavaScript si es necesario
4. Configurar para producción

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.