from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from registros.models import Estudiante


class Command(BaseCommand):
    help = 'Asocia usuarios existentes con estudiantes por correo electrónico'

    def handle(self, *args, **kwargs):
        """
        Busca estudiantes sin usuario asociado y los vincula con usuarios
        que tengan el mismo correo electrónico
        """
        estudiantes_sin_usuario = Estudiante.objects.filter(usuario__isnull=True)
        
        if not estudiantes_sin_usuario.exists():
            self.stdout.write(
                self.style.SUCCESS('✓ Todos los estudiantes ya tienen un usuario asociado')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Encontrados {estudiantes_sin_usuario.count()} estudiantes sin usuario asociado')
        )
        
        asociados = 0
        no_encontrados = []
        
        for estudiante in estudiantes_sin_usuario:
            try:
                # Buscar usuario por correo
                usuario = User.objects.get(email=estudiante.correo_institucional)
                estudiante.usuario = usuario
                estudiante.save()
                asociados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {estudiante.nombre} asociado con usuario: {usuario.username}')
                )
            except User.DoesNotExist:
                no_encontrados.append(estudiante)
                self.stdout.write(
                    self.style.WARNING(f'⚠ No se encontró usuario con email: {estudiante.correo_institucional}')
                )
            except User.MultipleObjectsReturned:
                self.stdout.write(
                    self.style.ERROR(f'✗ Múltiples usuarios con email: {estudiante.correo_institucional}')
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ {asociados} estudiantes asociados exitosamente'))
        
        if no_encontrados:
            self.stdout.write(
                self.style.WARNING(f'⚠ {len(no_encontrados)} estudiantes sin usuario correspondiente:')
            )
            for est in no_encontrados:
                self.stdout.write(f'  - {est.nombre} ({est.correo_institucional})')
            self.stdout.write('\n' + self.style.NOTICE('Sugerencia: Crea usuarios para estos correos o actualiza los correos de los estudiantes'))
