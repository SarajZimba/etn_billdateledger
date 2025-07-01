from django.forms import Textarea
from django.forms.fields import (
    BooleanField,
    DateField,
    DateTimeField,
)
from django.forms.widgets import DateInput, CheckboxSelectMultiple
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField


class BaseForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if type(self.fields[field]) != BooleanField:
                self.fields[field].widget.attrs[
                    "class"
                ] = "form-control form-control-solid"

            if type(self.fields[field]) == BooleanField:
                self.fields[field].widget.attrs.update(
                    {"class": "form-check-input", "type": "checkbox"}
                )

            if type(self.fields[field]) == DateTimeField:
                self.fields[field].widget = DateInput(
                    attrs={
                        "class": "form-control datetimepicker-input form-control-solid",
                        "type": "datetime-local",
                    }
                )

            if type(self.fields[field]) == DateField:
                self.fields[field].widget = DateInput(
                    attrs={
                        "class": "form-control datetimepicker-input col-2 form-control-solid",
                        "type": "date",
                    }
                )
            if type(self.fields[field]) == Textarea:
                self.fields[field].widget.attrs["id"] = "kt_docs_ckeditor_classic"

            if type(self.fields[field]) == ModelMultipleChoiceField and (
                type(self.fields[field].widget) == CheckboxSelectMultiple
            ):
                self.fields[field].widget.attrs.update(
                    {
                        "class": "form-check-input",
                        "type": "checkbox",
                        "onclick": "handleClick(this)",
                    }
                )