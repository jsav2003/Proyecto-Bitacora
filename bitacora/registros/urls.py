from django.urls import path
from . import views

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),
    
    # URLs de Estudiantes
    path('estudiantes/', views.estudiante_listar, name='estudiante_listar'),
    path('estudiantes/crear/', views.estudiante_crear, name='estudiante_crear'),
    path('estudiantes/editar/<int:pk>/', views.estudiante_editar, name='estudiante_editar'),
    path('estudiantes/eliminar/<int:pk>/', views.estudiante_eliminar, name='estudiante_eliminar'),
    
    # URLs de Mediciones
    path('mediciones/', views.medicion_listar, name='medicion_listar'),
    path('mediciones/crear/', views.medicion_crear, name='medicion_crear'),
    path('mediciones/editar/<int:pk>/', views.medicion_editar, name='medicion_editar'),
    path('mediciones/eliminar/<int:pk>/', views.medicion_eliminar, name='medicion_eliminar'),
    
    # URLs de Registros Fotográficos
    path('registros-fotograficos/', views.registro_fotografico_listar, name='registro_fotografico_listar'),
    path('registros-fotograficos/crear/', views.registro_fotografico_crear, name='registro_fotografico_crear'),
    path('registros-fotograficos/eliminar/<int:pk>/', views.registro_fotografico_eliminar, name='registro_fotografico_eliminar'),
]
