from django.db import models
from django.utils import timezone
import uuid

class Product(models.Model):
    class Meta:
        db_table = 'products'

    DISCOUNT_TYPES = (
        ("Fixed", "Fixed",),
        ("Percentage", "Percentage",),
    )

    CURRENCY_DISPLAY_CHOICES = (
        ("Symbol", "Symbol",),
        ("Code", "Code",),
    )

    uid = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    owner = models.ForeignKey('appauth.User', on_delete=models.CASCADE)
    images = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    desc = models.TextField()
    price = models.PositiveIntegerField()
    discount = models.PositiveIntegerField(default=0)
    enable_discount = models.BooleanField(default=False)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='Fixed')
    currency = models.CharField(max_length=3, default='USD')
    currency_display = models.CharField(max_length=10, default='Code', choices=CURRENCY_DISPLAY_CHOICES)

    def get_owner(self):
        return self.owner.uid
        
    def get_first_image(self):
        images: str = self.images
        if images:
            img_arr = images.split(',')
            return img_arr[0]

        return None