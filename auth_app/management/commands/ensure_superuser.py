import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the configured superuser if it does not already exist"

    def handle(self, *args, **options):
        username = os.getenv("SUPERUSER_USERNAME")
        email = os.getenv("SUPERUSER_EMAIL")
        password = os.getenv("SUPERUSER_PASSWORD")
        role_name = os.getenv("SUPERUSER_ROLE", "ADMIN")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser creation: SUPERUSER_USERNAME, SUPERUSER_EMAIL or SUPERUSER_PASSWORD is missing"
                )
            )
            return

        user_model = get_user_model()
        user = user_model.objects.filter(username=username).first()

        if user:
            updated = False
            if user.email != email:
                user.email = email
                updated = True
            if not user.is_staff:
                user.is_staff = True
                updated = True
            if not user.is_superuser:
                user.is_superuser = True
                updated = True
            if not user.has_usable_password() or not user.check_password(password):
                user.set_password(password)
                updated = True

            role_group = Group.objects.filter(name=role_name).first()
            if role_group and not user.groups.filter(name=role_name).exists():
                user.groups.clear()
                user.groups.add(role_group)
                updated = True

            if updated:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Updated existing superuser '{username}'"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists"))
            return

        user_model.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        role_group = Group.objects.filter(name=role_name).first()
        if role_group:
            created_user = user_model.objects.get(username=username)
            created_user.groups.clear()
            created_user.groups.add(role_group)

        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'"))