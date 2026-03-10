"""
Servicio de insignias - evalúa logros del usuario y otorga badges automáticamente.
"""
from catalog.models import (
    Insignia,
    TipoInsignia,
    INSIGNIA_META,
    Certificado,
    Calificacion,
    DiplomaCertificacionIndustria,
)


def _award(user, tipo):
    """Creates the badge if it doesn't already exist."""
    Insignia.objects.get_or_create(user=user, tipo=tipo)


def evaluar_y_otorgar(user):
    """
    Checks all badge conditions for the user and awards any that are missing.
    Call after course completion, review submission, or exam pass.
    """
    certs_count = Certificado.objects.filter(user=user).count()
    reviews_count = Calificacion.objects.filter(user=user).count()
    diplomas = DiplomaCertificacionIndustria.objects.filter(user=user, aprobado=True)
    diplomas_count = diplomas.count()
    perfect = diplomas.filter(puntaje=100).exists()

    if certs_count >= 1:
        _award(user, TipoInsignia.FIRST_COURSE)
    if certs_count >= 3:
        _award(user, TipoInsignia.THREE_COURSES)
    if certs_count >= 5:
        _award(user, TipoInsignia.FIVE_COURSES)
    if certs_count >= 10:
        _award(user, TipoInsignia.TEN_COURSES)

    if reviews_count >= 1:
        _award(user, TipoInsignia.FIRST_REVIEW)
    if reviews_count >= 5:
        _award(user, TipoInsignia.FIVE_REVIEWS)

    if diplomas_count >= 1:
        _award(user, TipoInsignia.INDUSTRY_CERT)
    if perfect:
        _award(user, TipoInsignia.PERFECT_SCORE)


def obtener_insignias(user):
    """Returns the user's badges with metadata attached."""
    badges = list(Insignia.objects.filter(user=user).order_by('fecha_obtencion'))
    for b in badges:
        meta = INSIGNIA_META.get(b.tipo, {})
        b.icon = meta.get('icon', 'bi-patch-check')
        b.color = meta.get('color', '#6c757d')
        b.description = meta.get('description', '')
    return badges


def obtener_todas_insignias_con_estado(user):
    """Returns ALL badge types with earned/locked status for display."""
    earned_tipos = set(
        Insignia.objects.filter(user=user).values_list('tipo', flat=True)
    )
    result = []
    for tipo_value, tipo_label in TipoInsignia.choices:
        meta = INSIGNIA_META.get(tipo_value, {})
        result.append({
            'tipo': tipo_value,
            'label': tipo_label,
            'icon': meta.get('icon', 'bi-patch-check'),
            'color': meta.get('color', '#6c757d'),
            'description': meta.get('description', ''),
            'earned': tipo_value in earned_tipos,
        })
    return result
