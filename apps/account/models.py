from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseAbstractDate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class User(AbstractUser):
    role = models.CharField(max_length=100, default='organization')

    def __str__(self):
        return self.username


class Admin(BaseAbstractDate):
    phone = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.FileField(upload_to='Avatar', null=True, blank=True)
    is_organizations = models.BooleanField(default=True)
    is_courier = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_statistic = models.BooleanField(default=False)
    is_incomes = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    is_add_admin = models.BooleanField(default=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin',
        null=True, blank=True
    )

    def __str__(self):
        return self.full_name


class Contact(models.Model):
    email = models.EmailField(null=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.email
