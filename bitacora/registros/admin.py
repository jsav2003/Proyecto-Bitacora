from django.contrib import admin
from django.utils.html import format_html
from .models import Estudiante, MedicionPlantas, RegistroFotografico


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo_institucional', 'grupo', 'usuario_asociado', 'estado_usuario')
    list_filter = ('grupo', 'usuario')
    search_fields = ('nombre', 'correo_institucional', 'usuario__username')
    readonly_fields = ('estado_asociacion',)
    
    fieldsets = (
        ('Información del Estudiante', {
            'fields': ('nombre', 'correo_institucional', 'grupo')
        }),
        ('Asociación con Usuario', {
            'fields': ('usuario', 'estado_asociacion'),
            'description': 'Asocia este estudiante con una cuenta de usuario existente. '
                          'Si el estudiante no tiene usuario, NO podrá iniciar sesión en el sistema.'
        }),
    )
    
    def usuario_asociado(self, obj):
        """Muestra el nombre de usuario asociado"""
        if obj.usuario:
            return obj.usuario.username
        return '-'
    usuario_asociado.short_description = 'Usuario'
    
    def estado_usuario(self, obj):
        """Muestra el estado de la asociación con íconos"""
        if obj.usuario:
            return format_html(
                '<span style="color: green;">✓ Asociado</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">⚠ Sin usuario</span>'
        )
    estado_usuario.short_description = 'Estado'
    
    def estado_asociacion(self, obj):
        """Muestra información detallada sobre la asociación"""
        if obj.usuario:
            return format_html(
                '<div style="padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;">'
                '<strong style="color: #155724;">✓ Usuario asociado correctamente</strong><br>'
                'Usuario: <strong>{}</strong><br>'
                'Email: {}<br>'
                'Estado: {}'
                '</div>',
                obj.usuario.username,
                obj.usuario.email,
                'Activo' if obj.usuario.is_active else 'Inactivo'
            )
        return format_html(
            '<div style="padding: 10px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px;">'
            '<strong style="color: #721c24;">⚠ ADVERTENCIA: Este estudiante NO tiene usuario asociado</strong><br>'
            '<ul style="margin-top: 10px; margin-bottom: 0;">'
            '<li>No podrá iniciar sesión en el sistema</li>'
            '<li>No aparecerá en las opciones de estudiantes para mediciones</li>'
            '<li>Selecciona un usuario existente arriba o crea uno nuevo desde el panel de Usuarios</li>'
            '</ul>'
            '</div>'
        )
    estado_asociacion.short_description = 'Estado de Asociación'


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
