from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from appauth.models import User

class Command(BaseCommand):
    help = "Manually creates user."

    def add_arguments(self, parser) -> None:
        parser.add_argument("email", type=str, help="Email of the user")
        parser.add_argument("password", type=str, help="Password of the user.")
        parser.add_argument("-r", "--role", type=str, help="User's role")
        parser.add_argument("-a", "--active", type=int, help="Whether user is active", default=1)

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        role = options["role"]
        is_active = options['active']
        is_staff = True if role == "admin" else False

        User.objects.create(email=email, password=make_password(password), is_staff=is_staff, is_active=is_active)
        print("User created successfully!")