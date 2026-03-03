"""
Servicio de inscripciones - encapsula la lógica de negocio de inscripción a cursos.
"""
from transactions.models import Inscripcion


def esta_inscrito(user, curso) -> bool:
    """
    True si el usuario tiene una inscripción activa o completada en el curso
    (excluye canceladas).
    """
    return Inscripcion.objects.filter(
        user=user,
        curso=curso,
    ).exclude(estado='CANCELADA').exists()


def tiene_acceso_aprender(user, curso) -> bool:
    """
    True si el usuario puede acceder a la vista de aprender (inscripción ACTIVA o COMPLETADA).
    """
    return Inscripcion.objects.filter(
        user=user,
        curso=curso,
        estado__in=('ACTIVA', 'COMPLETADA'),
    ).exists()


def inscripciones_activas(user):
    """
    Retorna queryset de inscripciones del usuario no canceladas,
    con curso y categoría para presentación.
    """
    return (
        Inscripcion.objects.filter(user=user)
        .exclude(estado='CANCELADA')
        .select_related('curso', 'curso__categoria')
        .order_by('-fecha_inscripcion')
    )
