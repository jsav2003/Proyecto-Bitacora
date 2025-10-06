from django import forms
from .models import Estudiante, MedicionPlantas, RegistroFotografico


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
                'placeholder': 'Altura de la planta en cm',
                'step': '0.01',
                'min': '0.01'
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
