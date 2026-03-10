"""
API REST del catálogo (DRF). Endpoints con Serializers y códigos HTTP correctos.
"""
import logging

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Curso, EstadoCurso, Modulo
from .serializers import (
    CalificacionCreateSerializer,
    CursoListSerializer,
    CursoDetailSerializer,
    ModuloSerializer,
    CategoriaSerializer,
)
from .services.rating_service import puede_calificar, crear_o_actualizar_calificacion
from .services import course_service

logger = logging.getLogger('catalog')


class CourseListAPIView(ListAPIView):
    """
    GET /api/courses/
    Lists published courses. Supports ?q= search and ?categoria= filter.
    """
    serializer_class = CursoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        q = self.request.query_params.get('q', '').strip()
        cat = self.request.query_params.get('categoria')
        cat_id = int(cat) if cat and str(cat).isdigit() else None
        return course_service.obtener_cursos_publicados(
            categoria_id=cat_id,
            search_query=q or None,
        )


class CourseDetailAPIView(RetrieveAPIView):
    """
    GET /api/courses/<id>/
    Returns full course detail with modules, lessons, and reviews.
    """
    serializer_class = CursoDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Curso.objects.filter(
            estado=EstadoCurso.PUBLICADO
        ).select_related('categoria', 'instructor').prefetch_related(
            'modulos__lecciones', 'calificaciones__user'
        )


class CourseModulesAPIView(ListAPIView):
    """
    GET /api/courses/<id>/modules/
    Returns modules and lessons for a course.
    """
    serializer_class = ModuloSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Modulo.objects.filter(
            curso_id=self.kwargs['pk'],
            curso__estado=EstadoCurso.PUBLICADO,
        ).prefetch_related('lecciones').order_by('orden')


class CategoryListAPIView(ListAPIView):
    """
    GET /api/categories/
    Lists all categories.
    """
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from .models import Categoria
        return Categoria.objects.all()


class CourseRateView(APIView):
    """
    POST /api/courses/<id>/rate/
    201 Created | 200 OK | 400 Bad Request | 404 Not Found | 409 Conflict
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cal, created = crear_o_actualizar_calificacion(
            request.user, curso,
            serializer.validated_data['puntuacion'],
            serializer.validated_data.get('comentario', ''),
        )
        if cal is None:
            return Response({'detail': 'Invalid rating data.'}, status=status.HTTP_400_BAD_REQUEST)

        logger.info('User %s rated course %s: %d/5', request.user.username, curso.titulo, cal.puntuacion)
        return Response(
            {'id': cal.pk, 'curso_id': curso.pk, 'puntuacion': cal.puntuacion, 'comentario': cal.comentario},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
