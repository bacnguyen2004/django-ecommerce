from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Nhân viên'),
        ('customer', 'Khách hàng'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )

    name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name if self.name else self.user.username

