from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import uuid

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = 'users'

    USERNAME_FIELD = 'email'
    objects = UserManager()

    # USER_ROLES = (("Admin", 0), ("Regular", 1), ("Designer", 2))

    uid = models.UUIDField(unique=True, default=uuid.uuid4)
    email = models.EmailField(verbose_name='email address', max_length=191, unique=True)
    name = models.CharField(max_length=160, null=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    dp = models.CharField(max_length=250, null=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    role = models.CharField(default="regular", max_length=12)

    def __str__(self):
        return self.name

    def get_name(self):
        if self.name and self.name != '':
            return self.name

        return 'Anonymous'

    # def send_confirmation(self):
    #     activation_token = TokenGenerator()
    #     subject = 'Activate Your Mailx Account'
    #     uid = urlsafe_base64_encode(force_bytes(self.pk))
    #     token = activation_token.make_token(self)
    #     confirm_url = FRONTEND+'auth/confirm/'+uid+'/'+token

    #     message = render_to_string('email_confirmation.html', {
    #         'user': self,
    #         'confirm_url': confirm_url,
    #     })

    #     email = EmailMessage(
    #         subject,
    #         message,
    #         from_email="support@appclick.com",
    #         to=[self.email]
    #     )

    #     email.content_subtype = "html"
    #     email.send()
