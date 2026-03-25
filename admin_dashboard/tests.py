from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse

from tickets.models import Agencia, Ticket, TicketAuditoria


class RechazarTicketViewTest(TestCase):
	def setUp(self):
		self.admin_group, _ = Group.objects.get_or_create(name='ADMIN')
		self.revisor_group, _ = Group.objects.get_or_create(name='REVISOR')

		self.admin = User.objects.create_user(username='admin_role', password='testpass123')
		self.admin.groups.add(self.admin_group)

		self.revisor = User.objects.create_user(username='revisor_role', password='testpass123')
		self.revisor.groups.add(self.revisor_group)

		self.otro_revisor = User.objects.create_user(username='otro_revisor_role', password='testpass123')
		self.otro_revisor.groups.add(self.revisor_group)

		self.agencia = Agencia.objects.create(
			codigo_faces='RECH001',
			nombre='Agencia Rechazo',
			usuario_creacion=self.admin,
			usuario_actualizacion=self.admin,
		)

	def test_admin_puede_rechazar_ticket_y_guardar_historial(self):
		ticket = Ticket.objects.create(
			nombre='Juan',
			apellido='Caso',
			correo='juan@example.com',
			telefono='3000000000',
			agencia=self.agencia,
			tipo_solicitud='P',
			descripcion='Ticket para rechazo por admin',
			usuario_asignado=self.revisor,
			usuario_actualiza=self.revisor,
			estado='en_proceso',
		)

		self.client.login(username='admin_role', password='testpass123')
		response = self.client.post(
			reverse('admin_dashboard:rechazar_ticket', args=[ticket.id]),
			{'motivo_rechazo': 'Informacion incompleta'},
			follow=True,
		)

		ticket.refresh_from_db()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(ticket.estado, 'cancelado')
		self.assertEqual(ticket.motivo_rechazo, 'Informacion incompleta')

		auditoria = TicketAuditoria.objects.filter(ticket=ticket).order_by('-fecha_cambio').first()
		self.assertEqual(auditoria.operacion, 'REJECT')
		self.assertEqual(auditoria.usuario, self.admin)
		self.assertIn('rechazado', auditoria.comentario.lower())
		self.assertIn('informacion incompleta', auditoria.comentario.lower())

	def test_revisor_asignado_puede_rechazar_ticket(self):
		ticket = Ticket.objects.create(
			nombre='Ana',
			apellido='Caso',
			correo='ana@example.com',
			telefono='3000000001',
			agencia=self.agencia,
			tipo_solicitud='Q',
			descripcion='Ticket para rechazo por revisor',
			usuario_asignado=self.revisor,
			usuario_actualiza=self.revisor,
			estado='en_proceso',
		)

		self.client.login(username='revisor_role', password='testpass123')
		response = self.client.post(
			reverse('admin_dashboard:rechazar_ticket', args=[ticket.id]),
			{'motivo_rechazo': 'No corresponde al proceso actual'},
			follow=True,
		)

		ticket.refresh_from_db()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(ticket.estado, 'cancelado')
		self.assertEqual(ticket.motivo_rechazo, 'No corresponde al proceso actual')

	def test_revisor_no_asignado_no_puede_rechazar_ticket(self):
		ticket = Ticket.objects.create(
			nombre='Pedro',
			apellido='Caso',
			correo='pedro@example.com',
			telefono='3000000002',
			agencia=self.agencia,
			tipo_solicitud='R',
			descripcion='Ticket protegido ante rechazo por otro revisor',
			usuario_asignado=self.revisor,
			usuario_actualiza=self.revisor,
			estado='en_proceso',
		)

		self.client.login(username='otro_revisor_role', password='testpass123')
		response = self.client.post(
			reverse('admin_dashboard:rechazar_ticket', args=[ticket.id]),
			{'motivo_rechazo': 'Intento invalido'},
			follow=True,
		)

		ticket.refresh_from_db()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(ticket.estado, 'en_proceso')
