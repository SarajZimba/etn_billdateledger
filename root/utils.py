import six

import shortuuid
from django.db import models
from django.http import JsonResponse
from django.utils.text import slugify
from root.constants import COUNTRIES


class Manger(models.Manager):
    def is_not_deleted(self):
        return self.filter(is_deleted=False)

    def active(self):
        return self.filter(is_deleted=False, status=True)


class BaseModel(models.Model):
    """
    This is the base model for all the models.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    sorting_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    objects = Manger()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def catch_exception(self, slug_item, *args, **kwargs):
        self.slug = slugify(slug_item) + "-" + str(six.text_type(shortuuid.uuid()))
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):

        if hasattr(self, "slug"):
            if hasattr(self, "name"):
                if self.name:
                    try:
                        self.slug = slugify(self.name)
                        super().save(*args, **kwargs)
                    except Exception:
                        self.catch_exception(self, self.name, *args, **kwargs)

            elif hasattr(self, "title"):
                if self.title:
                    try:
                        self.slug = slugify(self.title)
                        # super().save(*args, **kwargs)
                    except Exception:
                        self.catch_exception(self, self.title, *args, **kwargs)

        super().save(*args, **kwargs)


class CountryField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 2)
        kwargs.setdefault("choices", COUNTRIES)
        kwargs.setdefault("default", "NP")

        super(CountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"


class UserMixin(BaseModel):
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Others"),
    )
    user = models.OneToOneField(
        "user.User",
        on_delete=models.CASCADE,
    )
    phone_number = models.CharField(max_length=255, null=False, blank=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True)

    country = CountryField()
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    user_image = models.ImageField(upload_to="user/images/", null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user.full_name} - {self.phone_number}"


class DeleteMixin:
    def remove_from_DB(self, request):
        try:
            object_id = request.GET.get("pk", None)
            object = self.model.objects.get(id=object_id)
            object.is_deleted = True
            object.save()

            return True
        except Exception as e:
            print(e)
            return str(e)

    def get(self, request):
        status = self.remove_from_DB(request)
        return JsonResponse({"deleted": status})


class SingletonModel:
    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        return super().save(**kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


def remove_from_DB(self, request):
    try:
        object_id = request.GET.get("pk", None)
        self.model.objects.get(id=object_id).delete()
        return True
    except:
        return False
