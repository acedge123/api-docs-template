from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user with predefined credentials'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'alan@thegig.agency'
        password = '123456@@@'
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING("User '{}' already exists. Updating password...".format(username))
            )
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS("Updated user '{}' with new password and email.".format(username))
            )
        else:
            # Create new superuser
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS("Created superuser '{}' with email '{}'.".format(username, email))
            )
        
        self.stdout.write("Username: {}".format(username))
        self.stdout.write("Email: {}".format(email))
        self.stdout.write("Password: {}".format(password))
        self.stdout.write(self.style.SUCCESS("You can now login at /admin/"))
