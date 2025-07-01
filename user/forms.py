from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from root.forms import BaseForm  # optional


User = get_user_model()

user_fields = ["full_name", "username"]


class UserCreateForm(BaseForm, UserCreationForm):
    class Meta:
        model = User
        fields = ["username"] + user_fields


class AdminForm(BaseForm, UserCreationForm):
    # password1 = None  # Standard django password input

    class Meta:
        model = User
        fields = ["full_name", "username"]

    def clean_password(self):
        return self.clean_password


class UserForm(BaseForm, UserCreationForm):
    # password1 = None  # Standard django password input
    password2 = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget = forms.HiddenInput()
        self.fields["password1"].required = False
        self.fields["username"].label = "Usercode"

    class Meta:
        model = User
        fields = ["full_name", "username"]

    def clean_password(self):
        return self.clean_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["username"])
        if commit:
            user.save()
        return user


from .models import Customer


class CustomerForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured",
            "created_by",
            "email",
        ]
