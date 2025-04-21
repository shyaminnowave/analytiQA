from django import forms
from apps.core.widgets import JsonTableWidget
from apps.core.models import TestCaseModel
from django.utils.translation import gettext_lazy as _


class TestCaseForm(forms.ModelForm):

    class Meta:
        model = TestCaseModel
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['steps'].widget = JsonTableWidget(testcase_id=self.instance.id)


class StepAddForm(forms.Form):

    step_number = forms.IntegerField(max_value=100, 
                                     help_text=(_("Step Number")))
    step_action = forms.CharField(max_length=200, help_text=(_("Step Action")))
    step_data = forms.CharField(max_length=200, required=False, help_text=(_("Step Data")))
    expected_result = forms.CharField(max_length=200, help_text=(_("Expected Result")))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for key, field in self.fields.items():
            field.widget.attrs.update({
                "class": 'form-control',
                "placeholder": field.help_text
            })
            
