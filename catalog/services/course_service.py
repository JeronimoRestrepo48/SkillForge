"""
Servicio de cursos - encapsula la lógica de negocio del dominio Catálogo.
"""
from datetime import datetime
from django.utils import timezone

from catalog.models import Curso, Categoria, EstadoCurso
from users.models import User


def obtener_cursos_publicados(categoria_id=None):
    """
    Retorna queryset de cursos publicados.
    Opcionalmente filtra por categoría (id).
    """
    qs = Curso.objects.filter(estado=EstadoCurso.PUBLICADO).select_related(
        'categoria', 'instructor'
    )
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    return qs.order_by('-fecha_creacion')


def crear_curso(instructor: User, **kwargs) -> Curso:
    """Crea un nuevo curso asignado al instructor."""
    kwargs.setdefault('estado', EstadoCurso.BORRADOR)
    return Curso.objects.create(instructor=instructor, **kwargs)


def publicar_curso(curso: Curso) -> bool:
    """
    Publica un curso si está en borrador.
    Retorna True si se publicó correctamente.
    """
    if curso.estado != EstadoCurso.BORRADOR:
        return False
    curso.estado = EstadoCurso.PUBLICADO
    curso.fecha_publicacion = timezone.now()
    curso.save(update_fields=['estado', 'fecha_publicacion'])
    return True
