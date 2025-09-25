from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tickets.models import Ticket


class Command(BaseCommand):
    help = 'Crea los roles (grupos) del sistema: ADMIN, REVISOR, USER'

    def handle(self, *args, **options):
        # Crear o obtener los grupos
        admin_group, created = Group.objects.get_or_create(name='ADMIN')
        revisor_group, created = Group.objects.get_or_create(name='REVISOR')
        user_group, created = Group.objects.get_or_create(name='USER')

        # Obtener content types
        ticket_content_type = ContentType.objects.get_for_model(Ticket)
        
        # Obtener permisos básicos de Django
        from django.contrib.auth.models import User
        user_content_type = ContentType.objects.get_for_model(User)

        # Permisos para tickets
        view_ticket = Permission.objects.get(codename='view_ticket', content_type=ticket_content_type)
        add_ticket = Permission.objects.get(codename='add_ticket', content_type=ticket_content_type)
        change_ticket = Permission.objects.get(codename='change_ticket', content_type=ticket_content_type)
        delete_ticket = Permission.objects.get(codename='delete_ticket', content_type=ticket_content_type)

        # Permisos para usuarios
        view_user = Permission.objects.get(codename='view_user', content_type=user_content_type)
        add_user = Permission.objects.get(codename='add_user', content_type=user_content_type)
        change_user = Permission.objects.get(codename='change_user', content_type=user_content_type)
        delete_user = Permission.objects.get(codename='delete_user', content_type=user_content_type)

        # Configurar permisos para ADMIN (Super Usuario)
        # Tiene todos los permisos
        admin_permissions = [
            view_ticket, add_ticket, change_ticket, delete_ticket,
            view_user, add_user, change_user, delete_user
        ]
        admin_group.permissions.set(admin_permissions)

        # Configurar permisos para REVISOR
        # Puede ver y modificar tickets, pero no usuarios
        revisor_permissions = [
            view_ticket, add_ticket, change_ticket, delete_ticket
        ]
        revisor_group.permissions.set(revisor_permissions)

        # Configurar permisos para USER
        # Solo puede ver tickets
        user_permissions = [
            view_ticket
        ]
        user_group.permissions.set(user_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                'Roles creados exitosamente:\n'
                '- ADMIN: Acceso completo al sistema\n'
                '- REVISOR: Gestión completa de tickets\n'
                '- USER: Solo visualización de tickets'
            )
        )