from .models import DiscountTable
from django import forms
from root.forms import BaseForm


class DiscountTableForm(BaseForm, forms.ModelForm):
    class Meta:
        model = DiscountTable
        fields = '__all__'
        exclude = ['is_deleted', 'status', 'deleted_at', 'sorting_order', 'is_featured']
                        