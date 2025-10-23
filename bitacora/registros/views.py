from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from .models import Estudiante, MedicionPlantas, RegistroFotografico
from .forms import EstudianteForm, MedicionPlantasForm, RegistroFotograficoForm, RegistroForm, LoginForm
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend sin interfaz gráfica para servidor
import matplotlib.pyplot as plt
import io
import base64
import csv
from decimal import Decimal


# ===== VISTAS DE AUTENTICACIÓN =====

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('index')
    else:
        form = RegistroForm()
    
    return render(request, 'registros/auth/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'registros/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


# ===== VISTAS EXISTENTES =====


# Vista principal
@login_required
def index(request):
    estudiantes_count = Estudiante.objects.count()
    mediciones_count = MedicionPlantas.objects.count()
    fotos_count = RegistroFotografico.objects.count()
    
    context = {
        'estudiantes_count': estudiantes_count,
        'mediciones_count': mediciones_count,
        'fotos_count': fotos_count,
    }
    return render(request, 'registros/index.html', context)


# ===== VISTAS DE ESTUDIANTES =====

@login_required
def estudiante_crear(request):
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudiante registrado exitosamente.')
            return redirect('estudiante_listar')
    else:
        form = EstudianteForm()
    
    return render(request, 'registros/estudiante_form.html', {'form': form, 'accion': 'Registrar'})


@login_required
def estudiante_listar(request):
    busqueda = request.GET.get('buscar', '')
    estudiantes = Estudiante.objects.all()
    
    if busqueda:
        estudiantes = estudiantes.filter(
            Q(nombre__icontains=busqueda) | 
            Q(correo_institucional__icontains=busqueda) |
            Q(grupo__icontains=busqueda)
        )
    
    context = {
        'estudiantes': estudiantes,
        'busqueda': busqueda
    }
    return render(request, 'registros/estudiante_lista.html', context)


@login_required
def estudiante_editar(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    
    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudiante actualizado exitosamente.')
            return redirect('estudiante_listar')
    else:
        form = EstudianteForm(instance=estudiante)
    
    return render(request, 'registros/estudiante_form.html', {'form': form, 'accion': 'Editar'})


@login_required
def estudiante_eliminar(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    
    if request.method == 'POST':
        estudiante.delete()
        messages.success(request, 'Estudiante eliminado exitosamente.')
        return redirect('estudiante_listar')
    
    return render(request, 'registros/estudiante_eliminar.html', {'estudiante': estudiante})


# ===== VISTAS DE MEDICIONES =====

@login_required
def medicion_crear(request):
    if request.method == 'POST':
        form = MedicionPlantasForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar la medición
            medicion = form.save()
            
            # Si hay imagen, crear el registro fotográfico asociado
            imagen = form.cleaned_data.get('imagen')
            comentario = form.cleaned_data.get('comentario', '')
            
            if imagen:
                RegistroFotografico.objects.create(
                    medicion=medicion,  # ← Relación directa
                    estudiante=medicion.estudiante,
                    imagen=imagen,
                    comentario=comentario
                )
                messages.success(request, 'Medición y fotografía registradas exitosamente.')
            else:
                messages.success(request, 'Medición registrada exitosamente.')
            
            return redirect('medicion_listar')
    else:
        form = MedicionPlantasForm()
    
    return render(request, 'registros/medicion_form.html', {'form': form, 'accion': 'Registrar'})


@login_required
def medicion_listar(request):
    estudiante_id = request.GET.get('estudiante', '')
    mediciones = MedicionPlantas.objects.select_related('estudiante').prefetch_related('foto').all()
    
    if estudiante_id:
        mediciones = mediciones.filter(estudiante_id=estudiante_id)
    
    # Crear lista con mediciones y sus fotos (ahora es simple con OneToOne)
    mediciones_con_fotos = []
    for medicion in mediciones:
        mediciones_con_fotos.append({
            'medicion': medicion,
            'foto': medicion.foto if hasattr(medicion, 'foto') else None
        })
    
    estudiantes = Estudiante.objects.all()
    
    context = {
        'mediciones_con_fotos': mediciones_con_fotos,
        'mediciones': mediciones,
        'estudiantes': estudiantes,
        'estudiante_seleccionado': estudiante_id
    }
    return render(request, 'registros/medicion_lista.html', context)


@login_required
def medicion_editar(request, pk):
    medicion = get_object_or_404(MedicionPlantas, pk=pk)
    # Obtener foto asociada si existe (ahora es simple con OneToOne)
    registro_foto = medicion.foto if hasattr(medicion, 'foto') else None
    
    if request.method == 'POST':
        form = MedicionPlantasForm(request.POST, request.FILES, instance=medicion)
        if form.is_valid():
            # Actualizar la medición
            medicion = form.save()
            
            # Manejar imagen y comentario
            imagen = form.cleaned_data.get('imagen')
            comentario = form.cleaned_data.get('comentario', '')
            
            if registro_foto:
                # Actualizar registro existente
                if imagen:
                    registro_foto.imagen = imagen
                registro_foto.comentario = comentario
                registro_foto.save()
                messages.success(request, 'Medición actualizada exitosamente.')
            elif imagen:
                # Crear nuevo registro solo si hay imagen
                RegistroFotografico.objects.create(
                    medicion=medicion,  # ← Relación directa
                    estudiante=medicion.estudiante,
                    imagen=imagen,
                    comentario=comentario
                )
                messages.success(request, 'Medición y fotografía actualizadas exitosamente.')
            else:
                messages.success(request, 'Medición actualizada exitosamente.')
            
            return redirect('medicion_listar')
    else:
        # Crear el formulario con la instancia de medición
        # y datos iniciales del registro fotográfico
        initial_data = {}
        if registro_foto:
            initial_data['comentario'] = registro_foto.comentario
        
        form = MedicionPlantasForm(instance=medicion, initial=initial_data)
    
    context = {
        'form': form, 
        'accion': 'Editar',
        'registro_foto': registro_foto
    }
    return render(request, 'registros/medicion_form.html', context)


@login_required
def medicion_eliminar(request, pk):
    medicion = get_object_or_404(MedicionPlantas, pk=pk)
    
    if request.method == 'POST':
        medicion.delete()
        messages.success(request, 'Medición eliminada exitosamente.')
        return redirect('medicion_listar')
    
    return render(request, 'registros/medicion_eliminar.html', {'medicion': medicion})


# ===== VISTAS DE REGISTROS FOTOGRÁFICOS =====

@login_required
def registro_fotografico_crear(request):
    if request.method == 'POST':
        form = RegistroFotograficoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro fotográfico guardado exitosamente.')
            return redirect('registro_fotografico_listar')
    else:
        form = RegistroFotograficoForm()
    
    return render(request, 'registros/registro_fotografico_form.html', {'form': form, 'accion': 'Registrar'})


@login_required
def registro_fotografico_listar(request):
    estudiante_id = request.GET.get('estudiante', '')
    registros = RegistroFotografico.objects.select_related('estudiante').all()
    
    if estudiante_id:
        registros = registros.filter(estudiante_id=estudiante_id)
    
    estudiantes = Estudiante.objects.all()
    
    context = {
        'registros': registros,
        'estudiantes': estudiantes,
        'estudiante_seleccionado': estudiante_id
    }
    return render(request, 'registros/registro_fotografico_lista.html', context)


@login_required
def registro_fotografico_eliminar(request, pk):
    registro = get_object_or_404(RegistroFotografico, pk=pk)
    
    if request.method == 'POST':
        registro.delete()
        messages.success(request, 'Registro fotográfico eliminado exitosamente.')
        return redirect('registro_fotografico_listar')
    
    return render(request, 'registros/registro_fotografico_eliminar.html', {'registro': registro})


# ===== FUNCIONES DE ANÁLISIS DE REGRESIÓN =====

def MinCuad(x, y):
    """
    Calcula la regresión lineal por el método de mínimos cuadrados.
    
    Args:
        x: array de valores independientes (días)
        y: array de valores dependientes (alturas)
    
    Returns:
        tuple: (a0, a1) donde y = a0 + a1*x
    """
    sumx = 0
    sumy = 0
    sumxy = 0
    sumxx = 0
    n = len(x)
    
    for i in range(len(x)):
        sumxy += x[i] * y[i]
        sumxx += x[i] ** 2
        sumx += x[i]
        sumy += y[i]
    
    a1 = (n * sumxy - sumx * sumy) / (n * sumxx - sumx ** 2)
    a0 = (sumy - a1 * sumx) / n
    
    return a0, a1


def calcular_coeficiente_correlacion(x, y, a0, a1):
    """
    Calcula el coeficiente de correlación r y r²
    
    Args:
        x: array de valores independientes
        y: array de valores dependientes
        a0, a1: coeficientes de la regresión
    
    Returns:
        tuple: (r, r2)
    """
    media_y = np.mean(y)
    y_est = a0 + a1 * x
    
    # Coeficiente de correlación
    num = np.sum((y_est - media_y) ** 2)
    den = np.sum((y - media_y) ** 2)
    r = np.sqrt(num / den) if den != 0 else 0
    
    # Coeficiente de determinación
    r2 = 1 - np.sum((y - y_est) ** 2) / den if den != 0 else 0
    
    return r, r2


# ===== VISTAS DE ANÁLISIS =====

@login_required
def analisis_dashboard(request):
    """
    Vista dashboard para mostrar todos los estudiantes disponibles para análisis
    con funcionalidad de búsqueda y filtros
    """
    # Obtener parámetros de búsqueda y filtros
    busqueda = request.GET.get('buscar', '').strip()
    grupo_filtro = request.GET.get('grupo', '')
    ajuste_filtro = request.GET.get('ajuste', '')
    ordenar = request.GET.get('ordenar', 'nombre')
    
    # Obtener TODOS los estudiantes
    estudiantes = Estudiante.objects.all()
    
    # Aplicar filtro de búsqueda por nombre
    if busqueda:
        estudiantes = estudiantes.filter(nombre__icontains=busqueda)
    
    # Aplicar filtro por grupo
    if grupo_filtro:
        estudiantes = estudiantes.filter(grupo=grupo_filtro)
    
    # Ordenar inicialmente
    estudiantes = estudiantes.order_by('grupo', 'nombre')
    
    # Preparar datos de cada estudiante
    estudiantes_data = []
    estudiantes_sin_datos = []
    
    for estudiante in estudiantes:
        mediciones = MedicionPlantas.objects.filter(estudiante=estudiante).order_by('dia')
        num_mediciones = mediciones.count()
        
        if num_mediciones >= 2:
            # Calcular estadísticas rápidas
            dias = np.array([float(m.dia) for m in mediciones])
            alturas = np.array([float(m.altura) for m in mediciones])
            
            a0, a1 = MinCuad(dias, alturas)
            r, r2 = calcular_coeficiente_correlacion(dias, alturas, a0, a1)
            
            # Clasificar calidad de ajuste
            if r2 > 0.9:
                calidad_ajuste = 'excelente'
            elif r2 > 0.7:
                calidad_ajuste = 'bueno'
            elif r2 > 0.5:
                calidad_ajuste = 'moderado'
            else:
                calidad_ajuste = 'debil'
            
            estudiantes_data.append({
                'estudiante': estudiante,
                'num_mediciones': num_mediciones,
                'dias_registrados': f"{int(dias.min())} - {int(dias.max())}",
                'altura_inicial': float(alturas[0]),
                'altura_final': float(alturas[-1]),
                'crecimiento_total': float(alturas[-1] - alturas[0]),
                'r2': round(r2, 3),
                'tiene_buen_ajuste': r2 > 0.7,
                'calidad_ajuste': calidad_ajuste,
                'puede_analizar': True
            })
        else:
            # Estudiante sin suficientes datos
            estudiantes_sin_datos.append({
                'estudiante': estudiante,
                'num_mediciones': num_mediciones,
                'puede_analizar': False,
                'motivo': 'Necesita al menos 2 mediciones' if num_mediciones < 2 else 'Sin datos'
            })
    
    # Aplicar filtro por calidad de ajuste
    if ajuste_filtro:
        estudiantes_data = [e for e in estudiantes_data if e['calidad_ajuste'] == ajuste_filtro]
    
    # Aplicar ordenamiento
    if ordenar == 'nombre':
        estudiantes_data.sort(key=lambda x: x['estudiante'].nombre)
    elif ordenar == 'grupo':
        estudiantes_data.sort(key=lambda x: x['estudiante'].grupo)
    elif ordenar == 'r2_desc':
        estudiantes_data.sort(key=lambda x: x['r2'], reverse=True)
    elif ordenar == 'r2_asc':
        estudiantes_data.sort(key=lambda x: x['r2'])
    elif ordenar == 'crecimiento_desc':
        estudiantes_data.sort(key=lambda x: x['crecimiento_total'], reverse=True)
    elif ordenar == 'crecimiento_asc':
        estudiantes_data.sort(key=lambda x: x['crecimiento_total'])
    elif ordenar == 'mediciones_desc':
        estudiantes_data.sort(key=lambda x: x['num_mediciones'], reverse=True)
    
    # Obtener lista de grupos únicos para el filtro
    grupos = Estudiante.objects.values_list('grupo', flat=True).distinct().order_by('grupo')
    
    context = {
        'estudiantes_data': estudiantes_data,
        'estudiantes_sin_datos': estudiantes_sin_datos,
        'total_estudiantes': len(estudiantes_data),
        'total_sin_datos': len(estudiantes_sin_datos),
        'grupos': grupos,
        'busqueda': busqueda,
        'grupo_filtro': grupo_filtro,
        'ajuste_filtro': ajuste_filtro,
        'ordenar': ordenar,
    }
    
    return render(request, 'registros/analisis_dashboard.html', context)


@login_required
def analisis_regresion(request, estudiante_id):
    """
    Vista para mostrar el análisis de regresión lineal del crecimiento de plantas
    """
    estudiante = get_object_or_404(Estudiante, pk=estudiante_id)
    mediciones = MedicionPlantas.objects.filter(estudiante=estudiante).order_by('dia')
    
    # Verificar que haya suficientes datos
    if mediciones.count() < 2:
        messages.warning(request, 'Se necesitan al menos 2 mediciones para realizar el análisis.')
        return redirect('medicion_listar')
    
    # Extraer datos
    dias = np.array([float(m.dia) for m in mediciones])
    alturas = np.array([float(m.altura) for m in mediciones])
    
    # Calcular regresión lineal
    a0, a1 = MinCuad(dias, alturas)
    
    # Calcular coeficientes de correlación
    r, r2 = calcular_coeficiente_correlacion(dias, alturas, a0, a1)
    
    # Generar puntos para la línea de regresión
    dias_linea = np.linspace(dias.min(), dias.max(), 100)
    alturas_linea = a0 + a1 * dias_linea
    
    # Crear gráfica
    plt.figure(figsize=(10, 6))
    plt.scatter(dias, alturas, color='blue', s=100, alpha=0.6, edgecolors='black', label='Datos medidos')
    plt.plot(dias_linea, alturas_linea, color='red', linewidth=2, label=f'Regresión: y = {a0:.2f} + {a1:.2f}x')
    plt.xlabel('Día', fontsize=12)
    plt.ylabel('Altura (cm)', fontsize=12)
    plt.title(f'Análisis de Crecimiento - {estudiante.nombre}', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    # Convertir gráfica a imagen base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    grafica_base64 = base64.b64encode(image_png).decode('utf-8')
    
    # Preparar datos para el template
    context = {
        'estudiante': estudiante,
        'mediciones': mediciones,
        'grafica': grafica_base64,
        'a0': round(a0, 4),
        'a1': round(a1, 4),
        'r': round(r, 4),
        'r2': round(r2, 4),
        'ecuacion': f'y = {a0:.2f} + {a1:.2f}x',
        'num_mediciones': mediciones.count(),
        'altura_inicial': float(alturas[0]),
        'altura_final': float(alturas[-1]),
        'crecimiento_promedio': round(a1, 2),
    }
    
    return render(request, 'registros/analisis_regresion.html', context)


@login_required
def exportar_csv(request, estudiante_id):
    """
    Exporta los datos de mediciones de un estudiante a CSV
    """
    estudiante = get_object_or_404(Estudiante, pk=estudiante_id)
    mediciones = MedicionPlantas.objects.filter(estudiante=estudiante).order_by('dia')
    
    # Crear respuesta HTTP con tipo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="mediciones_{estudiante.nombre.replace(" ", "_")}.csv"'
    
    # Crear escritor CSV
    writer = csv.writer(response)
    writer.writerow(['Día', 'Altura (cm)', 'Fecha de Registro'])
    
    for medicion in mediciones:
        writer.writerow([
            medicion.dia,
            medicion.altura,
            medicion.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

