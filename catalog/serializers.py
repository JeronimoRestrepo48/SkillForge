"""
Serializers para la API del catálogo (entrada y salida).
"""
from rest_framework import serializers


class CalificacionCreateSerializer(serializers.Serializer):
    """Entrada para crear o actualizar una calificación (POST /api/courses/<id>/rate/)."""
    puntuacion = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField(required=False, allow_blank=True, default='')
