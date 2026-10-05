from django import forms
from .models import Cliente, Cuenta, Transaccion
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'email',
            'telefono'
        ]
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre completo',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'correo@ejemplo.com',
                }
            ),
            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+56 9 1234 5678',
                }
            ),
        }
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control aw-input',
                'placeholder':'Usuario',
                'autofocus': True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class':'form-control aw-input',
                'placeholder': 'Contrasena',
            }
        )
    )

class RegistroForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['cliente', 'numero_cuenta', 'etiquetas']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'numero_cuenta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numero de cuenta'}),
            'etiquetas': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['cuenta', 'tipo', 'monto', 'descripcion']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripcion (opcional)'}),
        }

    def clean_monto(self):
        monto = self.cleaned_data['monto']
        if monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor a 0.')
        return monto
