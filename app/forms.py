from django import forms
from .models import charge_sheet,User

class ChargeSheetForm(forms.ModelForm):
    class Meta:
        model = charge_sheet
        fields = ['law', 'officer', 'investigation']  # Exclude main_user and other fields you don't want to show
    
    def __init__(self, *args, **kwargs):
        super(ChargeSheetForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True 

    law = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'required': 'required'}))
    officer = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'required': 'required'}))
    investigation = forms.CharField(max_length=1000, required=True, widget=forms.TextInput(attrs={'required': 'required'}))

class FIRForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['remark'] 

    def __init__(self, *args, **kwargs):
        super(FIRForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True 

    remark = forms.CharField(max_length=1000, required=True, widget=forms.TextInput(attrs={'required': 'required'}))