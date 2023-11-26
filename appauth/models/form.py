from django.db import models
import uuid

class Form(models.Model):
    class Meta:
        db_table = 'forms'

    FORM_CHOICES = (
        ("Normal", "Normal",),
        ("Checkout", "Checkout",),
    )

    uid = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    ftype = models.CharField(max_length=20, default="Normal", choices=FORM_CHOICES)
    owner = models.ForeignKey('appauth.User', on_delete=models.CASCADE)