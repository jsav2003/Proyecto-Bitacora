from django.contrib import admin
from .models import Estudiante, MedicionPlantas, RegistroFotografico


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo_institucional', 'grupo')
    list_filter = ('grupo',)
    search_fields = ('nombre', 'correo_institucional')


@admin.register(MedicionPlantas)
class MedicionPlantasAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'dia', 'altura', 'fecha_registro')
    list_filter = ('dia', 'fecha_registro', 'estudiante')
    search_fields = ('estudiante__nombre',)
    date_hierarchy = 'fecha_registro'


@admin.register(RegistroFotografico)
class RegistroFotograficoAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'imagen', 'fecha', 'comentario')
    list_filter = ('fecha', 'estudiante')
    search_fields = ('estudiante__nombre', 'comentario')
    date_hierarchy = 'fecha'
