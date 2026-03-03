"""API views para autenticación JWT y perfil."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import UserMeSerializer


class MeView(APIView):
    """GET /api/me/ - Devuelve el usuario actual (requiere JWT o sesión). Usa Serializer para salida."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(instance=request.user)
        return Response(serializer.data)
