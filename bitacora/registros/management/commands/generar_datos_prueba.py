"""
Management command para generar datos de prueba del experimento de frijol
Uso: python manage.py generar_datos_prueba
"""
from django.core.management.base import BaseCommand
from registros.models import Estudiante, MedicionPlantas
import numpy as np
from decimal import Decimal


class Command(BaseCommand):
    help = 'Genera datos de prueba realistas para el experimento de crecimiento de frijol'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina todos los datos de prueba antes de generar nuevos',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Generador de Datos de Prueba ===\n'))

        # Limpiar datos si se especifica
        if options['limpiar']:
            self.stdout.write('Limpiando datos existentes...')
            MedicionPlantas.objects.all().delete()
            Estudiante.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Datos eliminados\n'))

        # Crear estudiantes de prueba
        self.stdout.write('Creando estudiantes de prueba...')
        
        estudiantes_data = [
            {
                'nombre': 'Juan Sebastian Arevalo Vasquez',
                'correo': 'juan.arevalo@ejemplo.edu.co',
                'grupo': 3,
                'dias': 18,
                'crecimiento_base': 1.8,  # cm por día
                'altura_inicial': 2.5,
                'variacion': 0.5
            },
            {
                'nombre': 'Emerick Rios Villa',
                'correo': 'emerick.rios@ejemplo.edu.co',
                'grupo': 3,
                'dias': 20,
                'crecimiento_base': 1.5,
                'altura_inicial': 3.0,
                'variacion': 0.6
            },
            {
                'nombre': 'Maria Fernanda Giraldo Duque',
                'correo': 'maria.giraldo@ejemplo.edu.co',
                'grupo': 3,
                'dias': 15,
                'crecimiento_base': 2.0,
                'altura_inicial': 2.0,
                'variacion': 0.4
            }
        ]

        np.random.seed(42)  # Para reproducibilidad

        for est_data in estudiantes_data:
            # Crear estudiante
            estudiante, created = Estudiante.objects.get_or_create(
                correo_institucional=est_data['correo'],
                defaults={
                    'nombre': est_data['nombre'],
                    'grupo': est_data['grupo']
                }
            )

            if created:
                self.stdout.write(f'  ✓ Creado: {estudiante.nombre} (Grupo {estudiante.grupo})')
            else:
                self.stdout.write(f'  → Ya existe: {estudiante.nombre}')

            # Generar mediciones realistas
            dias = est_data['dias']
            crecimiento_base = est_data['crecimiento_base']
            altura_inicial = est_data['altura_inicial']
            variacion = est_data['variacion']

            mediciones_creadas = 0
            
            for dia in range(1, dias + 1):
                # Simular crecimiento realista con:
                # - Crecimiento lineal base
                # - Variación aleatoria natural
                # - Ralentización en primeros días (germinación)
                
                factor_germinacion = 0.3 if dia <= 3 else 1.0
                
                altura = (
                    altura_inicial + 
                    (crecimiento_base * dia * factor_germinacion) +
                    np.random.normal(0, variacion)
                )
                
                # Asegurar que la altura sea positiva y realista
                altura = max(altura, altura_inicial)
                
                # Crear medición
                medicion, created = MedicionPlantas.objects.get_or_create(
                    estudiante=estudiante,
                    dia=dia,
                    defaults={'altura': Decimal(str(round(altura, 2)))}
                )
                
                if created:
                    mediciones_creadas += 1

            self.stdout.write(f'    → {mediciones_creadas} mediciones creadas\n')

        # Resumen final
        total_estudiantes = Estudiante.objects.count()
        total_mediciones = MedicionPlantas.objects.count()

        self.stdout.write(self.style.SUCCESS('\n=== Resumen ==='))
        self.stdout.write(self.style.SUCCESS(f'✓ Estudiantes: {total_estudiantes}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Mediciones: {total_mediciones}'))
        self.stdout.write(self.style.SUCCESS('\n¡Datos de prueba generados exitosamente!'))
        self.stdout.write(self.style.WARNING('\nPara limpiar todos los datos, usa: python manage.py generar_datos_prueba --limpiar'))
