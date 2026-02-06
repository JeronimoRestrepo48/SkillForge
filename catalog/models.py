"""
Modelos del dominio Catálogo.
Alineados al diagrama de clases de SkillForge.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings


class Categoria(models.Model):
    """Categoría de cursos."""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class EstadoCurso(models.TextChoices):
    """Estados posibles de un curso."""
    BORRADOR = 'BORRADOR', 'Borrador'
    EN_REVISION = 'EN_REVISION', 'En revisión'
    PUBLICADO = 'PUBLICADO', 'Publicado'
    PAUSADO = 'PAUSADO', 'Pausado'
    ARCHIVADO = 'ARCHIVADO', 'Archivado'


class NivelDificultad(models.TextChoices):
    """Nivel de dificultad del curso."""
    PRINCIPIANTE = 'PRINCIPIANTE', 'Principiante'
    INTERMEDIO = 'INTERMEDIO', 'Intermedio'
    AVANZADO = 'AVANZADO', 'Avanzado'
    EXPERTO = 'EXPERTO', 'Experto'


class Curso(models.Model):
    """
    Curso del catálogo.
    Encapsula lógica de precios y disponibilidad (diagrama de clases).
    """
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='cursos'
    )
    nivel_dificultad = models.CharField(
        max_length=20,
        choices=NivelDificultad.choices,
        default=NivelDificultad.PRINCIPIANTE
    )
    duracion_horas = models.PositiveIntegerField(default=0)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cursos_impartidos'
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoCurso.choices,
        default=EstadoCurso.BORRADOR
    )
    cupos_disponibles = models.PositiveIntegerField(default=0)
    cupos_totales = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    imagen = models.ImageField(
        upload_to='cursos/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo

    def calcular_precio_final(self) -> Decimal:
        """Retorna el precio final (con descuento si aplica)."""
        return self.precio_descuento if self.precio_descuento else self.precio

    def esta_disponible(self) -> bool:
        """Verifica si el curso está publicado y tiene cupos."""
        return (
            self.estado == EstadoCurso.PUBLICADO
            and self.cupos_disponibles > 0
        )

    def validar_disponibilidad(self) -> bool:
        """Alias para esta_disponible (alineado al diagrama)."""
        return self.esta_disponible()
