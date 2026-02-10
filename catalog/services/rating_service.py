"""
Servicio de calificaciones - solo estudiantes que completaron el curso pueden valorar.
"""
from django.db.models import Avg, Count

from catalog.models import Curso, Calificacion
from transactions.models import Inscripcion, EstadoInscripcion


def puede_calificar(user, curso: Curso) -> bool:
    """True si el usuario tiene inscripción COMPLETADA en el curso."""
    return Inscripcion.objects.filter(
        user=user,
        curso=curso,
        estado=EstadoInscripcion.COMPLETADA
    ).exists()


def crear_o_actualizar_calificacion(user, curso: Curso, puntuacion: int, comentario: str = ''):
    """
    Crea o actualiza la calificación. Solo si existe inscripción COMPLETADA.
    puntuacion debe estar entre 1 y 5.
    Retorna (Calificacion, created) o (None, False) si no puede calificar.
    """
    if not puede_calificar(user, curso):
        return None, False
    if not (1 <= puntuacion <= 5):
        return None, False

    cal, created = Calificacion.objects.update_or_create(
        user=user,
        curso=curso,
        defaults={
            'puntuacion': puntuacion,
            'comentario': comentario or '',
            'es_verificada': True,
        }
    )
    return cal, created


def obtener_calificacion_curso(curso: Curso):
    """Retorna las calificaciones del curso ordenadas por fecha."""
    return curso.calificaciones.select_related('user').order_by('-fecha_creacion')


def obtener_promedio_y_total(curso: Curso) -> dict:
    """Retorna {'promedio': float, 'total': int} para el curso."""
    agg = curso.calificaciones.aggregate(
        promedio=Avg('puntuacion'),
        total=Count('id')
    )
    return {
        'promedio': round(agg['promedio'] or 0, 1),
        'total': agg['total'] or 0,
    }
