"""
Asigna la imagen de portada (marketing digital) a los 3 cursos de Marketing Digital.
Uso: python manage.py asignar_imagen_cursos_marketing
"""
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.conf import settings

from catalog.models import Curso


TITULOS_CURSOS_MARKETING = [
    'SEO para principiantes',
    'Marketing en redes sociales',
    'Google Ads y remarketing',
]

NOMBRE_ARCHIVO = 'portada_marketing_digital.png'


class Command(BaseCommand):
    help = 'Asigna la imagen de portada a los 3 cursos de Marketing Digital'

    def handle(self, *args, **options):
        imagen_path = Path(settings.MEDIA_ROOT) / 'cursos' / NOMBRE_ARCHIVO
        if not imagen_path.exists():
            self.stdout.write(self.style.ERROR(f'No se encontró la imagen en {imagen_path}'))
            return

        content = imagen_path.read_bytes()
        actualizados = 0
        for titulo in TITULOS_CURSOS_MARKETING:
            curso = Curso.objects.filter(titulo=titulo).first()
            if not curso:
                self.stdout.write(self.style.WARNING(f'Curso no encontrado: {titulo}'))
                continue
            curso.imagen.save(NOMBRE_ARCHIVO, ContentFile(content), save=True)
            actualizados += 1
            self.stdout.write(self.style.SUCCESS(f'Imagen asignada a: {titulo}'))

        self.stdout.write(self.style.SUCCESS(f'Listo: {actualizados} cursos actualizados.'))
