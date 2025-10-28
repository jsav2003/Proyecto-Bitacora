from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from registros.models import Estudiante
from django.db import transaction


class Command(BaseCommand):
    help = 'Lista y ayuda a corregir estudiantes sin usuario asociado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--crear-usuarios',
            action='store_true',
            help='Crea automáticamente usuarios para estudiantes sin usuario asociado'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='temporal123',
            help='Contraseña para los usuarios creados automáticamente (default: temporal123)'
        )

    def handle(self, *args, **kwargs):
        crear_usuarios = kwargs.get('crear_usuarios', False)
        password_default = kwargs.get('password', 'temporal123')
        
        # Buscar estudiantes sin usuario
        estudiantes_sin_usuario = Estudiante.objects.filter(usuario__isnull=True)
        
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.WARNING('ESTUDIANTES SIN USUARIO ASOCIADO'))
        self.stdout.write('=' * 80)
        
        if not estudiantes_sin_usuario.exists():
            self.stdout.write(
                self.style.SUCCESS('\n✓ Todos los estudiantes tienen un usuario asociado\n')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'\n⚠ Encontrados {estudiantes_sin_usuario.count()} estudiantes sin usuario:\n')
        )
        
        for estudiante in estudiantes_sin_usuario:
            self.stdout.write(f'  • ID: {estudiante.id:3} | {estudiante.nombre:40} | Grupo: {estudiante.grupo}')
            self.stdout.write(f'    Email: {estudiante.correo_institucional}')
            self.stdout.write('')
        
        if not crear_usuarios:
            self.stdout.write('=' * 80)
            self.stdout.write(self.style.WARNING('\nPARA SOLUCIONAR:'))
            self.stdout.write('=' * 80)
            self.stdout.write('\nOpción 1: Crear usuarios automáticamente')
            self.stdout.write('  python manage.py verificar_estudiantes_sin_usuario --crear-usuarios')
            self.stdout.write('\nOpción 2: Asociar con usuarios existentes manualmente')
            self.stdout.write('  - Ir al panel de administración')
            self.stdout.write('  - Editar cada estudiante')
            self.stdout.write('  - Seleccionar un usuario existente')
            self.stdout.write('\nOpción 3: Usar el comando de asociación por email')
            self.stdout.write('  python manage.py asociar_usuarios_estudiantes')
            self.stdout.write('')
            return
        
        # Crear usuarios automáticamente
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.WARNING('CREANDO USUARIOS AUTOMÁTICAMENTE'))
        self.stdout.write('=' * 80)
        self.stdout.write(f'Contraseña para todos: {password_default}\n')
        
        creados = 0
        errores = 0
        
        for estudiante in estudiantes_sin_usuario:
            try:
                with transaction.atomic():
                    # Generar nombre de usuario desde el nombre
                    nombre_base = estudiante.nombre.lower().replace(' ', '_')
                    username = nombre_base
                    
                    # Si el username ya existe, agregar número
                    contador = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{nombre_base}{contador}"
                        contador += 1
                    
                    # Crear el usuario
                    user = User.objects.create_user(
                        username=username,
                        email=estudiante.correo_institucional,
                        password=password_default,
                        first_name=estudiante.nombre.split()[0] if estudiante.nombre.split() else estudiante.nombre,
                        last_name=' '.join(estudiante.nombre.split()[1:]) if len(estudiante.nombre.split()) > 1 else ''
                    )
                    
                    # Asociar con el estudiante
                    estudiante.usuario = user
                    estudiante.save()
                    
                    creados += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Usuario creado: {username:30} → {estudiante.nombre}')
                    )
                    
            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creando usuario para {estudiante.nombre}: {e}')
                )
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS(f'✓ {creados} usuarios creados exitosamente'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'✗ {errores} errores'))
        self.stdout.write('=' * 80)
        
        if creados > 0:
            self.stdout.write(self.style.WARNING('\n⚠ IMPORTANTE: Todos los usuarios tienen la contraseña: ' + password_default))
            self.stdout.write(self.style.WARNING('Los estudiantes deben cambiarla al iniciar sesión.\n'))
