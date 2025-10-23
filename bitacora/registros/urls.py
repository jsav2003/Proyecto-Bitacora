from django.urls import path
from . import views

urlpatterns = [
    # URLs de Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    
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
    
    # URLs de Análisis
    path('analisis/', views.analisis_dashboard, name='analisis_dashboard'),
    path('analisis/<int:estudiante_id>/', views.analisis_regresion, name='analisis_regresion'),
    path('exportar-csv/<int:estudiante_id>/', views.exportar_csv, name='exportar_csv'),
]

