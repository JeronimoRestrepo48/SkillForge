"""API views para autenticación JWT y perfil."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class MeView(APIView):
    """GET /api/me/ - Devuelve el usuario actual (requiere JWT o sesión)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tipo': user.tipo,
            'is_staff': user.is_staff,
        }
        if hasattr(user, 'profile'):
            data['bio'] = user.profile.bio
            data['preferencias'] = user.profile.preferencias
        else:
            data['bio'] = ''
            data['preferencias'] = {}
        return Response(data)
