from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Estudiante, MedicionPlantas, RegistroFotografico
from .forms import EstudianteForm, MedicionPlantasForm, RegistroFotograficoForm, RegistroForm, LoginForm


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
