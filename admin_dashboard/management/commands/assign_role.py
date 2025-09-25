from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Asigna un rol a un usuario existente'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario')
        parser.add_argument('role', type=str, choices=['ADMIN', 'REVISOR', 'USER'], help='Rol a asignar')

    def handle(self, *args, **options):
        username = options['username']
        role_name = options['role']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuario "{username}" no encontrado')
            )
            return

        try:
            role_group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Rol "{role_name}" no encontrado. Ejecuta "python manage.py setup_roles" primero.')
            )
            return

        # Remover roles anteriores
        user.groups.clear()
        # Asignar nuevo rol
        user.groups.add(role_group)

        self.stdout.write(
            self.style.SUCCESS(f'Rol "{role_name}" asignado exitosamente al usuario "{username}"')
        )