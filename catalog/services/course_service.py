"""
Servicio de cursos - encapsula la lógica de negocio del dominio Catálogo.
"""
import logging

from django.db import models
from django.db.models import Avg, Count
from django.utils import timezone

logger = logging.getLogger('catalog')

from catalog.models import Curso, Categoria, EstadoCurso, Modulo, Leccion, ProgresoLeccion
from users.models import User


def obtener_cursos_publicados(categoria_id=None, search_query=None):
    """
    Retorna queryset de cursos publicados con anotaciones de rating.
    Opcionalmente filtra por categoría (id) y/o búsqueda de texto.
    """
    from django.db.models import Q

    qs = Curso.objects.filter(estado=EstadoCurso.PUBLICADO).select_related(
        'categoria', 'instructor'
    ).annotate(
        rating_avg=Avg('calificaciones__puntuacion'),
        rating_count=Count('calificaciones'),
    )
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    if search_query:
        qs = qs.filter(
            Q(titulo__icontains=search_query)
            | Q(descripcion__icontains=search_query)
            | Q(categoria__nombre__icontains=search_query)
            | Q(instructor__first_name__icontains=search_query)
            | Q(instructor__last_name__icontains=search_query)
        )
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


# --- Módulos y lecciones ---


def obtener_modulos_de_curso(curso: Curso):
    """Retorna los módulos de un curso ordenados."""
    return curso.modulos.all().order_by('orden')


def crear_modulo(curso: Curso, titulo: str, orden: int | None = None, duracion_minutos: int = 0) -> Modulo:
    """Crea un módulo en el curso. Si orden es None, se asigna al final."""
    if orden is None:
        agg = curso.modulos.aggregate(max_orden=models.Max('orden'))
        orden = (agg['max_orden'] or 0) + 1
    return Modulo.objects.create(
        curso=curso,
        titulo=titulo,
        orden=orden,
        duracion_minutos=duracion_minutos,
    )


def obtener_lecciones_de_modulo(modulo: Modulo):
    """Retorna las lecciones de un módulo ordenadas."""
    return modulo.lecciones.all().order_by('orden')


def crear_leccion(modulo: Modulo, titulo: str, tipo: str = 'TEXTO', contenido: str = '',
                  orden: int | None = None, duracion_minutos: int = 0) -> Leccion:
    """Crea una lección en el módulo. Si orden es None, se asigna al final."""
    if orden is None:
        max_orden = modulo.lecciones.aggregate(max_orden=models.Max('orden'))['max_orden']
        orden = (max_orden or 0) + 1
    return Leccion.objects.create(
        modulo=modulo,
        titulo=titulo,
        tipo=tipo,
        contenido=contenido,
        orden=orden,
        duracion_minutos=duracion_minutos,
    )


def marcar_leccion_completada(user, leccion: Leccion) -> ProgresoLeccion:
    """Marca una lección como completada para el usuario."""
    logger.info('User %s completing lesson %s (pk=%d)', user.username, leccion.titulo, leccion.pk)
    prog, created = ProgresoLeccion.objects.update_or_create(
        user=user,
        leccion=leccion,
        defaults={
            'completada': True,
            'fecha_completada': timezone.now(),
        }
    )
    return prog


def obtener_progreso_curso(user, curso: Curso) -> dict:
    """
    Retorna dict con total lecciones y lecciones completadas para el usuario en el curso.
    """
    lecciones_ids = Leccion.objects.filter(modulo__curso=curso).values_list('pk', flat=True)
    total = len(list(lecciones_ids))
    completadas = ProgresoLeccion.objects.filter(
        user=user,
        leccion_id__in=lecciones_ids,
        completada=True
    ).count()
    return {'total': total, 'completadas': completadas, 'porcentaje': (completadas / total * 100) if total else 0}


def obtener_lecciones_ordenadas_curso(curso: Curso):
    """
    Retorna lista de lecciones del curso en orden (módulo.orden, leccion.orden).
    Útil para navegación siguiente/anterior.
    """
    return list(
        Leccion.objects.filter(modulo__curso=curso).select_related('modulo').order_by(
            'modulo__orden', 'orden'
        )
    )


def total_lecciones_curso(curso: Curso) -> int:
    """Retorna el número total de lecciones del curso."""
    return Leccion.objects.filter(modulo__curso=curso).count()
