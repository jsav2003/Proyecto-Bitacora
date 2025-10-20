from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Estudiante(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre completo")
    correo_institucional = models.EmailField(unique=True, verbose_name="Correo institucional")
    grupo = models.IntegerField(verbose_name="Grupo/Curso")
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ['grupo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - Grupo {self.grupo}"


class MedicionPlantas(models.Model):
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE, 
        related_name='mediciones',
        verbose_name="Estudiante"
    )
    dia = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Día de medición"
    )
    altura = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Altura de la planta (cm)"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    
    class Meta:
        verbose_name = "Medición de Plantas"
        verbose_name_plural = "Mediciones de Plantas"
        ordering = ['-fecha_registro']
        unique_together = ['estudiante', 'dia']  # Un estudiante solo puede tener una medición por día
    
    def __str__(self):
        return f"Día {self.dia} - {self.estudiante.nombre} - {self.altura} cm"


class RegistroFotografico(models.Model):
    medicion = models.OneToOneField(
        MedicionPlantas,
        on_delete=models.CASCADE,
        related_name='foto',
        verbose_name="Medición asociada",
        null=True,
        blank=True
    )
    # Mantener estudiante por compatibilidad con datos existentes
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE, 
        related_name='registros_fotograficos',
        verbose_name="Estudiante"
    )
    imagen = models.ImageField(upload_to='registro_fotografico/', verbose_name="Fotografía")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentario")
    
    class Meta:
        verbose_name = "Registro Fotográfico"
        verbose_name_plural = "Registros Fotográficos"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Foto - {self.estudiante.nombre} - {self.fecha.strftime('%d/%m/%Y')}"
