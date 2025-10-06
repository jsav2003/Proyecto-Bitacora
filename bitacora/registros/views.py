from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Estudiante, MedicionPlantas, RegistroFotografico
from .forms import EstudianteForm, MedicionPlantasForm, RegistroFotograficoForm


# Vista principal
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


def estudiante_eliminar(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    
    if request.method == 'POST':
        estudiante.delete()
        messages.success(request, 'Estudiante eliminado exitosamente.')
        return redirect('estudiante_listar')
    
    return render(request, 'registros/estudiante_eliminar.html', {'estudiante': estudiante})


# ===== VISTAS DE MEDICIONES =====

def medicion_crear(request):
    if request.method == 'POST':
        form = MedicionPlantasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medición registrada exitosamente.')
            return redirect('medicion_listar')
    else:
        form = MedicionPlantasForm()
    
    return render(request, 'registros/medicion_form.html', {'form': form, 'accion': 'Registrar'})


def medicion_listar(request):
    estudiante_id = request.GET.get('estudiante', '')
    mediciones = MedicionPlantas.objects.select_related('estudiante').all()
    
    if estudiante_id:
        mediciones = mediciones.filter(estudiante_id=estudiante_id)
    
    estudiantes = Estudiante.objects.all()
    
    context = {
        'mediciones': mediciones,
        'estudiantes': estudiantes,
        'estudiante_seleccionado': estudiante_id
    }
    return render(request, 'registros/medicion_lista.html', context)


def medicion_editar(request, pk):
    medicion = get_object_or_404(MedicionPlantas, pk=pk)
    
    if request.method == 'POST':
        form = MedicionPlantasForm(request.POST, instance=medicion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medición actualizada exitosamente.')
            return redirect('medicion_listar')
    else:
        form = MedicionPlantasForm(instance=medicion)
    
    return render(request, 'registros/medicion_form.html', {'form': form, 'accion': 'Editar'})


def medicion_eliminar(request, pk):
    medicion = get_object_or_404(MedicionPlantas, pk=pk)
    
    if request.method == 'POST':
        medicion.delete()
        messages.success(request, 'Medición eliminada exitosamente.')
        return redirect('medicion_listar')
    
    return render(request, 'registros/medicion_eliminar.html', {'medicion': medicion})


# ===== VISTAS DE REGISTROS FOTOGRÁFICOS =====

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


def registro_fotografico_eliminar(request, pk):
    registro = get_object_or_404(RegistroFotografico, pk=pk)
    
    if request.method == 'POST':
        registro.delete()
        messages.success(request, 'Registro fotográfico eliminado exitosamente.')
        return redirect('registro_fotografico_listar')
    
    return render(request, 'registros/registro_fotografico_eliminar.html', {'registro': registro})
