from django import forms
from root.forms import BaseForm

from .models import Organization, StaticPage


class OrganizationForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"
        exclude = [
            "is_deleted",
            "status",
            "is_featured",
            "sorting_order",
        ]


class StaticPageForm(BaseForm, forms.ModelForm):
    class Meta:
        model = StaticPage
        fields = "__all__"
        exclude = [
            "is_deleted",
            "status",
            "slug",
            "sorting_order",
            "is_featured",
        ]


from .models import Branch


class BranchForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Branch
        fields = "__all__"
        exclude = [
            "is_deleted",
            "status",
            "deleted_at",
            "sorting_order",
            "is_featured",
            "organization",
        ]

from .models import MailRecipient

class MailRecipientForm(BaseForm, forms.ModelForm):
    class Meta:
        model = MailRecipient
        fields = '__all__'
        
from .models import Terminal

class TerminalForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Terminal
        fields = '__all__'
        exclude = ['is_deleted', 'status', 'deleted_at','sorting_order', 'is_featured']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add a placeholder for the table_number field
        self.fields['terminal_no'].widget.attrs['placeholder'] = 'Enter terminal number'