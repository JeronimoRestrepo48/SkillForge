"""
Comando para crear datos iniciales de desarrollo.
Uso: python manage.py crear_datos_iniciales
"""
from django.core.management.base import BaseCommand
from catalog.models import Categoria, Curso, EstadoCurso, NivelDificultad
from users.models import User, TipoUsuario


class Command(BaseCommand):
    help = 'Crea categorías de ejemplo y un usuario admin/instructor de prueba'

    def handle(self, *args, **options):
        categorias_data = [
            {'nombre': 'Programación', 'descripcion': 'Lenguajes y frameworks de desarrollo'},
            {'nombre': 'Diseño', 'descripcion': 'UI/UX, diseño gráfico y herramientas'},
            {'nombre': 'Marketing Digital', 'descripcion': 'SEO, redes sociales, publicidad'},
            {'nombre': 'Finanzas', 'descripcion': 'Inversiones, contabilidad, finanzas personales'},
            {'nombre': 'Idiomas', 'descripcion': 'Inglés, español y otros idiomas'},
        ]
        created = 0
        for data in categorias_data:
            _, was_created = Categoria.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'descripcion': data['descripcion']}
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Categorías: {created} creadas'))

        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@skillforge.local',
                password='admin123',
                tipo=TipoUsuario.ADMINISTRADOR
            )
            self.stdout.write(self.style.SUCCESS('Usuario admin creado (admin / admin123)'))

        if not User.objects.filter(username='instructor1').exists():
            from users.services import crear_usuario
            instructor = crear_usuario(
                username='instructor1',
                email='instructor@skillforge.local',
                password='instructor123',
                first_name='María',
                last_name='García',
                tipo=TipoUsuario.INSTRUCTOR
            )
            cat = Categoria.objects.first()
            if cat:
                Curso.objects.create(
                    titulo='Introducción a Python',
                    descripcion='Aprende los fundamentos de Python desde cero.',
                    precio=99_000,
                    categoria=cat,
                    nivel_dificultad=NivelDificultad.PRINCIPIANTE,
                    duracion_horas=20,
                    instructor=instructor,
                    estado=EstadoCurso.PUBLICADO,
                    cupos_totales=30,
                    cupos_disponibles=30
                )
            self.stdout.write(self.style.SUCCESS('Usuario instructor creado (instructor1 / instructor123)'))

        self.stdout.write(self.style.SUCCESS('Datos iniciales creados correctamente.'))
