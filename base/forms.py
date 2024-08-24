from django import forms
from .models import Medicine
from django.contrib.auth.models import User

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['medicine_name', 'description', 'quantity', 'expiry_date', 'user']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'medicine_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(MedicineForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all()  # Show all users
