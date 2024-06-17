from django import forms
from .models import *

class DashboardForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date
    )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['fecha', 'solicitante', 'cuenta', 'importe', 'comentarios']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'solicitante' in self.data:
            try:
                solicitante_id = int(self.data.get('solicitante'))
                self.fields['cuenta'].queryset = Cuenta.objects.filter(cliente_id=solicitante_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['cuenta'].queryset = self.instance.solicitante.cuentas
        else:
            self.fields['cuenta'].queryset = Cuenta.objects.none()
