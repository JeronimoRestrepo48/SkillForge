"""
Serializers para la API del catálogo (entrada y salida).
"""
from rest_framework import serializers
from .models import Curso, Modulo, Leccion, Categoria, Calificacion


class CalificacionCreateSerializer(serializers.Serializer):
    """Entrada para crear o actualizar una calificación (POST /api/courses/<id>/rate/)."""
    puntuacion = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField(required=False, allow_blank=True, default='')


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'icono']


class LeccionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Leccion
        fields = ['id', 'titulo', 'tipo', 'tipo_display', 'orden', 'duracion_minutos']


class ModuloSerializer(serializers.ModelSerializer):
    lecciones = LeccionSerializer(many=True, read_only=True)
    total_lecciones = serializers.IntegerField(source='lecciones.count', read_only=True)

    class Meta:
        model = Modulo
        fields = ['id', 'titulo', 'orden', 'duracion_minutos', 'total_lecciones', 'lecciones']


class CalificacionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Calificacion
        fields = ['id', 'user_name', 'puntuacion', 'comentario', 'es_verificada', 'fecha_creacion']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class CursoListSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    instructor_name = serializers.SerializerMethodField()
    precio_final = serializers.DecimalField(source='calcular_precio_final', max_digits=10, decimal_places=2, read_only=True)
    nivel_display = serializers.CharField(source='get_nivel_dificultad_display', read_only=True)
    disponible = serializers.BooleanField(source='esta_disponible', read_only=True)

    class Meta:
        model = Curso
        fields = [
            'id', 'titulo', 'descripcion', 'precio', 'precio_descuento', 'precio_final',
            'categoria', 'nivel_dificultad', 'nivel_display', 'duracion_horas',
            'instructor_name', 'estado', 'cupos_disponibles', 'disponible',
            'fecha_creacion', 'fecha_publicacion',
        ]

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.username


class CursoDetailSerializer(CursoListSerializer):
    modulos = ModuloSerializer(many=True, read_only=True)
    calificaciones = CalificacionSerializer(many=True, read_only=True)
    info_evaluacion = serializers.CharField()

    class Meta(CursoListSerializer.Meta):
        fields = CursoListSerializer.Meta.fields + ['modulos', 'calificaciones', 'info_evaluacion']
