"""
Serializers para la API de usuarios (entrada y salida).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserMeSerializer(serializers.ModelSerializer):
    """Serializer de salida para GET /api/me/ (perfil del usuario autenticado)."""
    bio = serializers.SerializerMethodField()
    preferencias = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'tipo',
            'is_staff',
            'bio',
            'preferencias',
        ]
        read_only_fields = fields

    def get_bio(self, obj):
        return getattr(obj.profile, 'bio', '') if hasattr(obj, 'profile') else ''

    def get_preferencias(self, obj):
        return getattr(obj.profile, 'preferencias', {}) or {} if hasattr(obj, 'profile') else {}
