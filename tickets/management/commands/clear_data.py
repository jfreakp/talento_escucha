from django.core.management.base import BaseCommand
from django.db import transaction
from tickets.models import Ticket, TicketAuditoria, Agencia
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Elimina todos los datos excepto los usuarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma que quieres eliminar todos los datos (excepto usuarios)',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'Este comando eliminará TODOS los datos excepto usuarios.\n'
                    'Para confirmar, usa: python manage.py clear_data --confirm'
                )
            )
            return

        # Contar registros antes de eliminar
        ticket_count = Ticket.objects.count()
        auditoria_count = TicketAuditoria.objects.count()
        agencia_count = Agencia.objects.count()
        user_count = User.objects.count()

        self.stdout.write(f'Datos actuales en la base de datos:')
        self.stdout.write(f'- Usuarios: {user_count} (se mantendrán)')
        self.stdout.write(f'- Tickets: {ticket_count}')
        self.stdout.write(f'- Auditorías: {auditoria_count}')
        self.stdout.write(f'- Agencias: {agencia_count}')
        self.stdout.write('')

        try:
            # No usar transaction.atomic() para permitir eliminaciones parciales
            # Eliminar en orden para evitar problemas de claves foráneas
            self.stdout.write('Eliminando auditorías de tickets...')
            deleted_auditoria = TicketAuditoria.objects.all().delete()
            
            self.stdout.write('Eliminando tickets...')
            deleted_tickets = Ticket.objects.all().delete()
            
            self.stdout.write('Eliminando agencias (manteniendo referencias a usuarios)...')
            # Las agencias tienen FK a usuarios, así que no podemos eliminarlas
            # a menos que eliminemos esas referencias primero
            
            # Opción 1: Eliminar solo si no hay referencias críticas
            try:
                deleted_agencias = Agencia.objects.all().delete()
                agencia_deleted_count = deleted_agencias[0] if deleted_agencias else 0
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  No se pudieron eliminar las agencias (tienen referencias a usuarios): {str(e)}\n'
                        f'   Las agencias se mantendrán en la base de datos.'
                    )
                )
                agencia_deleted_count = 0

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Limpieza completada exitosamente:\n'
                    f'- {auditoria_count} auditorías eliminadas\n'
                    f'- {ticket_count} tickets eliminados\n'
                    f'- {agencia_deleted_count} de {agencia_count} agencias eliminadas\n'
                    f'- {user_count} usuarios mantenidos\n'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la limpieza: {str(e)}')
            )
            raise

        # Verificar que los usuarios siguen ahí
        remaining_users = User.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'✅ Verificación: {remaining_users} usuarios mantenidos')
        )