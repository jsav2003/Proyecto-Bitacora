from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Estudiante, MedicionPlantas, RegistroFotografico


# ===== FORMULARIOS DE AUTENTICACIÓN =====

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


# ===== FORMULARIOS EXISTENTES =====


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'correo_institucional', 'grupo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del estudiante'
            }),
            'correo_institucional': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@institucion.edu'
            }),
            'grupo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de grupo o curso',
                'min': '1'
            }),
        }


class MedicionPlantasForm(forms.ModelForm):
    # Campos adicionales para el registro fotográfico
    imagen = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Fotografía (opcional)'
    )
    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Observaciones y comentarios sobre la fotografía',
            'rows': 4
        }),
        label='Comentario (opcional)'
    )
    
    class Meta:
        model = MedicionPlantas
        fields = ['estudiante', 'dia', 'altura']
        widgets = {
            'estudiante': forms.Select(attrs={
                'class': 'form-control'
            }),
            'dia': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número del día (1, 2, 3...)',
                'min': '1'
            }),
            'altura': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 15.5',
                'step': '0.01',
                'min': '0'
            }),
        }


class RegistroFotograficoForm(forms.ModelForm):
    class Meta:
        model = RegistroFotografico
        fields = ['estudiante', 'imagen', 'comentario']
        widgets = {
            'estudiante': forms.Select(attrs={
                'class': 'form-control'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones y comentarios sobre la fotografía',
                'rows': 4
            }),
        }
