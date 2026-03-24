from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings
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
            'severidad': 'M',
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
            'severidad': 'M',
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
            'severidad': 'M',
            'descripcion': 'Test description'
        }
        
        form = TicketForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        
        ticket = form.save()
        
        # Verificar que el ticket se guardó correctamente
        self.assertEqual(ticket.nombre, self.user.first_name)
        self.assertEqual(ticket.apellido, self.user.last_name)
        self.assertEqual(ticket.correo, self.user.email)
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
        self.assertTrue(form.fields['nombre'].disabled)
        self.assertTrue(form.fields['apellido'].disabled)
        self.assertTrue(form.fields['correo'].disabled)
    
    def test_ticket_codigo_autogeneration(self):
        """Prueba que el código se genere automáticamente al crear un ticket"""
        form_data = {
            'nombre': 'Carlos',
            'apellido': 'López',
            'correo': 'carlos@example.com',
            'telefono': '+1234567890',
            'agencia': self.agencia.id,
            'tipo_solicitud': 'P',
            'severidad': 'M',
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
            'severidad': 'M',
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
            'severidad': 'M',
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
        self.assertContains(response, 'sin necesidad de registrarte')
        self.assertIn('form', response.context)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TicketAsignacionEmailTest(TestCase):
    """Tests para validar el envío de correo al asignar tickets."""

    def setUp(self):
        self.creador = User.objects.create_user(
            username='creador',
            email='creador@example.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Creador',
        )
        self.revisor = User.objects.create_user(
            username='revisor',
            email='revisor@example.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Revisor',
        )
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@example.com',
            password='testpass123',
        )

        self.agencia = Agencia.objects.create(
            codigo_faces='EMAIL001',
            nombre='Agencia Email',
            usuario_creacion=self.admin,
            usuario_actualizacion=self.admin,
        )

    def test_envia_correo_cuando_ticket_registrado_es_asignado(self):
        ticket = Ticket.objects.create(
            nombre='Juan',
            apellido='Prueba',
            correo='juan@example.com',
            telefono='+1234567890',
            agencia=self.agencia,
            tipo_solicitud='P',
            descripcion='Ticket para validar notificacion por asignacion',
            usuario_crea=self.creador,
            usuario_actualiza=self.creador,
        )

        mail.outbox = []

        ticket.usuario_asignado = self.revisor
        ticket.estado = 'en_proceso'
        ticket.usuario_actualiza = self.revisor
        ticket.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(ticket.codigo, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [self.creador.email, ticket.correo, self.revisor.email])

    def test_envia_correo_cuando_ticket_anonimo_es_asignado(self):
        ticket = Ticket.objects.create(
            nombre='Ana',
            apellido='Anonima',
            correo='ana@example.com',
            telefono='+0987654321',
            agencia=self.agencia,
            tipo_solicitud='Q',
            descripcion='Ticket anonimo para validar que no se envia correo de asignacion',
            usuario_actualiza=self.admin,
        )

        mail.outbox = []

        ticket.usuario_asignado = self.revisor
        ticket.estado = 'en_proceso'
        ticket.usuario_actualiza = self.revisor
        ticket.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(ticket.codigo, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [ticket.correo, self.revisor.email])


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TicketResolucionEmailTest(TestCase):
    """Tests para validar el envío de correo al resolver tickets."""

    def setUp(self):
        self.creador = User.objects.create_user(
            username='creador_res',
            email='creador_res@example.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Creador',
        )
        self.revisor = User.objects.create_user(
            username='revisor_res',
            email='revisor_res@example.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Revisor',
        )
        self.admin = User.objects.create_user(
            username='admin_res',
            email='admin_res@example.com',
            password='testpass123',
        )

        self.agencia = Agencia.objects.create(
            codigo_faces='EMAILRES001',
            nombre='Agencia Email Resolucion',
            usuario_creacion=self.admin,
            usuario_actualizacion=self.admin,
        )

    def test_envia_correo_cuando_ticket_registrado_se_resuelve(self):
        ticket = Ticket.objects.create(
            nombre='Carlos',
            apellido='Registrado',
            correo='carlos@example.com',
            telefono='+1111111111',
            agencia=self.agencia,
            tipo_solicitud='P',
            descripcion='Ticket registrado para validar correo de resolucion',
            usuario_crea=self.creador,
            usuario_asignado=self.revisor,
            usuario_actualiza=self.revisor,
            estado='en_proceso',
        )

        mail.outbox = []

        ticket.solucion = 'Se aplico la solucion de prueba'
        ticket.estado = 'resuelto'
        ticket.usuario_actualiza = self.revisor
        ticket.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(ticket.codigo, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [self.creador.email, ticket.correo, self.revisor.email])

    def test_envia_correo_cuando_ticket_anonimo_se_resuelve(self):
        ticket = Ticket.objects.create(
            nombre='Lucia',
            apellido='Anonima',
            correo='lucia@example.com',
            telefono='+2222222222',
            agencia=self.agencia,
            tipo_solicitud='R',
            descripcion='Ticket anonimo para validar correo de resolucion',
            usuario_asignado=self.revisor,
            usuario_actualiza=self.revisor,
            estado='en_proceso',
        )

        mail.outbox = []

        ticket.solucion = 'Se envio una respuesta al caso'
        ticket.estado = 'resuelto'
        ticket.usuario_actualiza = self.revisor
        ticket.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(ticket.codigo, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [ticket.correo, self.revisor.email])


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TicketCreacionEmailTest(TestCase):
    """Tests para validar correo al crear tickets."""

    def setUp(self):
        self.creador = User.objects.create_user(
            username='creador_new',
            email='creador_new@example.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Creador',
        )
        self.revisor = User.objects.create_user(
            username='revisor_new',
            email='revisor_new@example.com',
            password='testpass123',
        )
        self.admin = User.objects.create_user(
            username='admin_new',
            email='admin_new@example.com',
            password='testpass123',
        )

        self.agencia = Agencia.objects.create(
            codigo_faces='EMAILNEW001',
            nombre='Agencia Email Creacion',
            usuario_creacion=self.admin,
            usuario_actualizacion=self.admin,
        )

        revisor_group, _ = Group.objects.get_or_create(name='REVISOR')
        self.revisor.groups.add(revisor_group)

    def test_creacion_envia_confirmacion_a_usuario_y_correo_solicitud(self):
        mail.outbox = []

        ticket = Ticket.objects.create(
            nombre='Laura',
            apellido='Registrada',
            correo='laura.solicitud@example.com',
            telefono='+3000000000',
            agencia=self.agencia,
            tipo_solicitud='P',
            descripcion='Solicitud creada para validar correo de confirmacion',
            usuario_crea=self.creador,
            usuario_actualiza=self.creador,
        )

        self.assertIsNotNone(ticket.codigo)
        self.assertGreaterEqual(len(mail.outbox), 2)
        confirmaciones = [m for m in mail.outbox if ticket.codigo in m.subject and 'Hemos recibido tu solicitud' in m.subject]
        self.assertEqual(len(confirmaciones), 1)
        self.assertEqual(confirmaciones[0].to, [self.creador.email, ticket.correo])

    def test_creacion_envia_confirmacion_a_correo_solicitud_para_anonimo(self):
        mail.outbox = []

        ticket = Ticket.objects.create(
            nombre='Pedro',
            apellido='Anonimo',
            correo='pedro.anonimo@example.com',
            telefono='+3111111111',
            agencia=self.agencia,
            tipo_solicitud='Q',
            descripcion='Solicitud anonima para validar correo de confirmacion',
            usuario_actualiza=self.admin,
        )

        self.assertIsNotNone(ticket.codigo)
        self.assertGreaterEqual(len(mail.outbox), 2)
        confirmaciones = [m for m in mail.outbox if ticket.codigo in m.subject and 'Hemos recibido tu solicitud' in m.subject]
        self.assertEqual(len(confirmaciones), 1)
        self.assertEqual(confirmaciones[0].to, [ticket.correo])