"""
API REST del catálogo (DRF). Endpoints con Serializers y códigos HTTP 201, 400, 404, 409.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Curso
from .serializers import CalificacionCreateSerializer
from .services.rating_service import puede_calificar, crear_o_actualizar_calificacion


class CourseRateView(APIView):
    """
    POST /api/courses/<id>/rate/
    Crea o actualiza la calificación del usuario para el curso.
    Requiere haber completado el curso (inscripción COMPLETADA).
    - 201: calificación creada
    - 200: calificación actualizada
    - 400: datos inválidos (puntuación fuera de rango, etc.)
    - 404: curso no encontrado
    - 409: conflicto (el usuario no puede calificar: no ha completado el curso)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            curso = Curso.objects.get(pk=pk)
        except Curso.DoesNotExist:
            return Response(
                {'detail': 'Course not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not puede_calificar(request.user, curso):
            return Response(
                {'detail': 'You can only rate a course after completing it.'},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = CalificacionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        puntuacion = serializer.validated_data['puntuacion']
        comentario = serializer.validated_data.get('comentario', '')
        cal, created = crear_o_actualizar_calificacion(
            request.user, curso, puntuacion, comentario
        )
        if cal is None:
            return Response(
                {'detail': 'Invalid rating data.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                'id': cal.pk,
                'curso_id': curso.pk,
                'puntuacion': cal.puntuacion,
                'comentario': cal.comentario,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
