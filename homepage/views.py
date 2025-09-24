from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from tickets.forms import TicketForm, TicketAnonimForm
from tickets.models import Ticket
from tickets.pdf_utils import generar_pdf_ticket_anonimo

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
                f'¡Solicitud creada exitosamente! Tu número de ticket es: {ticket.codigo}. '
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
    if request.method == 'POST':
        form = TicketAnonimForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            # Agregar mensaje de éxito
            messages.success(
                request, 
                f'¡Solicitud anónima creada exitosamente! Tu número de ticket es: {ticket.codigo}. '
                f'Tu PDF se descargará automáticamente.'
            )
            # Redirigir directamente al PDF
            return redirect('homepage:descargar_pdf_ticket', ticket_id=ticket.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = TicketAnonimForm()
    
    context = {
        'form': form
    }
    return render(request, 'homepage/solicitud_anonimo.html', context)

def buscar_ticket(request):
    """Página para buscar tickets"""
    return render(request, 'homepage/buscar_ticket.html')

def test_styles(request):
    """Página de prueba de estilos"""
    return render(request, 'test_styles.html')

def descargar_pdf_ticket(request, ticket_id):
    """Genera y descarga el PDF del ticket anónimo"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Generar el PDF
    pdf_content = generar_pdf_ticket_anonimo(ticket)
    
    # Crear la respuesta HTTP con el PDF
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.codigo}.pdf"'
    
    return response
