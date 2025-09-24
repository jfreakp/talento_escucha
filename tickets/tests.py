from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from tickets.models import Agencia, Ticket
from tickets.forms import TicketForm


class TicketFormTest(TestCase):
    """
    Tests para el formulario de tickets
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Crear agencia de prueba
        self.agencia = Agencia.objects.create(
            codigo_faces='TEST001',
            nombre='Agencia de Prueba',
            usuario_creacion=self.user,
            usuario_actualizacion=self.user
        )
    
    def test_ticket_form_fields(self):
        """Prueba que el formulario tenga todos los campos requeridos"""
        form = TicketForm()
        expected_fields = [
            'nombre', 'apellido', 'correo', 'telefono', 
            'agencia', 'tipo_solicitud', 'descripcion'
        ]
        
        for field in expected_fields:
            self.assertIn(field, form.fields)
    
    def test_ticket_form_valid_data(self):
        """Prueba que el formulario sea válido con datos correctos"""
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'correo': 'juan@example.com',
            'telefono': '+1234567890',
            'agencia': self.agencia.id,
            'tipo_solicitud': 'P',
            'descripcion': 'Necesito hacer una petición'
        }
        
        form = TicketForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_ticket_form_missing_required_fields(self):
        """Prueba que el formulario sea inválido sin campos requeridos"""
        form_data = {
            # Solo algunos campos opcionales
        }
        
        form = TicketForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        
        # Verificar que los campos requeridos generen errores
        required_fields = ['nombre', 'apellido', 'correo', 'telefono', 'agencia', 'tipo_solicitud', 'descripcion']
        for field in required_fields:
            self.assertIn(field, form.errors)
    
    def test_ticket_form_email_validation(self):
        """Prueba la validación de email"""
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'correo': 'email_invalido',
            'telefono': '+1234567890',
            'agencia': self.agencia.id,
            'tipo_solicitud': 'Q',
            'descripcion': 'Descripción de prueba'
        }
        
        form = TicketForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)
    
    def test_ticket_form_save_with_user(self):
        """Prueba que el formulario guarde correctamente con usuario"""
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'correo': 'juan@example.com',
            'telefono': '+1234567890',
            'agencia': self.agencia.id,
            'tipo_solicitud': 'R',
            'descripcion': 'Test description'
        }
        
        form = TicketForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        
        ticket = form.save()
        
        # Verificar que el ticket se guardó correctamente
        self.assertEqual(ticket.nombre, 'Juan')
        self.assertEqual(ticket.apellido, 'Pérez')
        self.assertEqual(ticket.correo, 'juan@example.com')
        self.assertEqual(ticket.agencia, self.agencia)
        self.assertEqual(ticket.usuario_crea, self.user)
        self.assertEqual(ticket.estado, 'pendiente')
    
    def test_ticket_form_pre_fill_user_data(self):
        """Prueba que el formulario pre-llene datos del usuario autenticado"""
        form = TicketForm(user=self.user)
        
        # Verificar que los campos se pre-llenen con datos del usuario
        self.assertEqual(form.fields['nombre'].initial, self.user.first_name)
        self.assertEqual(form.fields['apellido'].initial, self.user.last_name)
        self.assertEqual(form.fields['correo'].initial, self.user.email)
    
    def test_ticket_codigo_autogeneration(self):
        """Prueba que el código se genere automáticamente al crear un ticket"""
        form_data = {
            'nombre': 'Carlos',
            'apellido': 'López',
            'correo': 'carlos@example.com',
            'telefono': '+1234567890',
            'agencia': self.agencia.id,
            'tipo_solicitud': 'P',
            'descripcion': 'Prueba de generación automática de código'
        }
        
        form = TicketForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        
        ticket = form.save()
        
        # Verificar que el código se generó automáticamente
        self.assertIsNotNone(ticket.codigo)
        self.assertTrue(ticket.codigo.startswith('FAC'))
        self.assertEqual(ticket.codigo, f'FAC{ticket.id}')
        
        # Verificar que el código no está en el formulario
        self.assertNotIn('codigo', form.fields)


class SolicitudUsuarioViewTest(TestCase):
    """
    Tests para la vista de solicitud de usuario
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear agencia de prueba
        self.agencia = Agencia.objects.create(
            codigo_faces='TEST001',
            nombre='Agencia de Prueba',
            usuario_creacion=self.user,
            usuario_actualizacion=self.user
        )
        
        self.url = reverse('homepage:solicitud_usuario')
    
    def test_solicitud_usuario_allows_anonymous(self):
        """Prueba que la vista permita usuarios anónimos"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # No redirect, permite acceso
    
    def test_solicitud_usuario_get_with_login(self):
        """Prueba GET con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crear Nueva Solicitud')
        self.assertIn('form', response.context)
    
    def test_solicitud_usuario_post_valid_data(self):
        """Prueba POST con datos válidos"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'correo': 'juan@example.com',
            'telefono': '+1234567890',
            'agencia': self.agencia.id,
            'tipo_solicitud': 'S',
            'descripcion': 'Test solicitud completa'
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # Verificar redirección después de éxito
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el ticket se creó
        ticket = Ticket.objects.first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.nombre, 'Juan')
        self.assertEqual(ticket.usuario_crea, self.user)
    
    def test_solicitud_usuario_post_invalid_data(self):
        """Prueba POST con datos inválidos"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'nombre': '',  # Campo requerido vacío
            'correo': 'email_invalido'
            # Faltan campos requeridos
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # Verificar que no se redirija (se mantiene en la página)
        self.assertEqual(response.status_code, 200)
        
        # Verificar que no se creó ningún ticket
        self.assertEqual(Ticket.objects.count(), 0)
        
        # Verificar que hay errores en el formulario
        self.assertTrue(response.context['form'].errors)
    
    def test_solicitud_usuario_post_anonymous_valid_data(self):
        """Prueba POST con datos válidos para usuario anónimo"""
        form_data = {
            'nombre': 'Ana',
            'apellido': 'García',
            'correo': 'ana@example.com',
            'telefono': '+0987654321',
            'agencia': self.agencia.id,
            'tipo_solicitud': 'P',
            'descripcion': 'Petición desde usuario anónimo'
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # Verificar redirección después de éxito
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el ticket se creó
        ticket = Ticket.objects.first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.nombre, 'Ana')
        self.assertIsNone(ticket.usuario_crea)  # Usuario anónimo
        self.assertEqual(ticket.estado, 'pendiente')
    
    def test_solicitud_usuario_get_anonymous(self):
        """Prueba GET para usuario anónimo"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crear Nueva Solicitud')
        self.assertContains(response, 'Solicitud sin registro')
        self.assertIn('form', response.context)