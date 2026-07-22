from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a default superadmin user if no superuser exists.'

    def handle(self, *args, **kwargs):
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Superadmin user already exists. Skipping creation.")
            return

        super_admin_role = Role.objects.filter(code='SUPER_ADMIN').first()

        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@kolak.com',
            password='adminpassword123',
            first_name='System',
            last_name='Admin',
            role=super_admin_role,
        )
        self.stdout.write(self.style.SUCCESS(
            "Default superadmin created successfully!\n"
            "  Username: admin\n"
            "  Email:    admin@kolak.com\n"
            "  Password: adminpassword123"
        ))
