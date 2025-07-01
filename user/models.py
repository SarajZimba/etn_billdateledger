import datetime
import random
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from organization.models import Branch, Organization
from root.utils import BaseModel


class User(AbstractUser, BaseModel):
    full_name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    image = models.ImageField(upload_to="user/images/", null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.full_name} - ({self.email})"

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = f"{self.username}@periwin.com"

        super().save(*args, **kwargs)


class Customer(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Customer Name")
    tax_number = models.CharField(
        max_length=255, verbose_name="PAN/VAT Number", null=True, blank=True
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, blank=True
    )
    email = models.EmailField(null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    loyalty_points =models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.contact_number})"


class ForgetPassword(BaseModel):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    email = models.EmailField(max_length=255)
    token = models.CharField(max_length=255, blank=True)
    is_used = models.BooleanField(default=False)
    key = models.UUIDField(editable=False, blank=True)
    expiry_date = models.DateTimeField(blank=True)
    mail_sent = models.BooleanField(default=False)
    mail_sent_date = models.DateTimeField(blank=True, null=True)
    expired = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
            self.key = self.generate_key()
            self.expiry_date = datetime.datetime.now() + datetime.timedelta(hours=24)
        super().save(*args, **kwargs)

    def generate_token(self):
        return random.randint(100000, 999999)

    def generate_key(self):
        return uuid.uuid1(self.token)


@receiver(post_save, sender=ForgetPassword)
def send_mail_to_user(sender, instance, created, **kwargs):
    if created:
        ForgetPassword.objects.filter(email=instance.email, expired=False).exclude(
            id=instance.id
        ).update(expired=True)
        send_mail(
            "Reset Password",
            "Your token is {}".format(instance.token),
            settings.EMAIL_HOST_USER,
            [
                instance.email,
            ],
            fail_silently=True,
        )
        instance.mail_sent = True
        instance.mail_sent_date = datetime.datetime.now()
        instance.save()
