from django.shortcuts import render, redirect
from django.contrib import messages
from tickets.forms import TicketForm

def home(request):
    """Vista principal del sitio web"""
    # Si el usuario ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    return render(request, 'homepage/home.html')

def servicios(request):
    """Página de servicios - vacía por ahora"""
    return render(request, 'homepage/servicios.html')

def sobre_nosotros(request):
    """Página sobre nosotros - vacía por ahora"""
    return render(request, 'homepage/sobre_nosotros.html')

def solicitud_usuario(request):
    """Página de solicitud para usuarios (autenticados o anónimos)"""
    # Determinar el usuario (puede ser None si es anónimo)
    user = request.user if request.user.is_authenticated else None
    
    if request.method == 'POST':
        form = TicketForm(request.POST, user=user)
        if form.is_valid():
            ticket = form.save()
            messages.success(
                request, 
                f'¡Solicitud creada exitosamente! Tu número de ticket es: {ticket.id}. '
                f'Te contactaremos pronto al correo: {ticket.correo}'
            )
            return redirect('homepage:solicitud_usuario')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = TicketForm(user=user)
    
    context = {
        'form': form
    }
    return render(request, 'homepage/solicitud_usuario.html', context)

def solicitud_anonimo(request):
    """Página de solicitud para usuarios anónimos"""
    return render(request, 'homepage/solicitud_anonimo.html')

def buscar_ticket(request):
    """Página para buscar tickets"""
    return render(request, 'homepage/buscar_ticket.html')

def test_styles(request):
    """Página de prueba de estilos"""
    return render(request, 'test_styles.html')
