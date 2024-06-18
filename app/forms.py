# forms.py

from django import forms
from .models import charge_sheet

class ChargeSheetForm(forms.ModelForm):
    class Meta:
        model = charge_sheet
        fields = ['law', 'officer', 'investigation']  # Exclude main_user and other fields you don't want to show
