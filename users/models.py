"""
Modelos del dominio de Usuarios.
Alineados al diagrama de clases de SkillForge.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class TipoUsuario(models.TextChoices):
    """Roles del sistema."""
    ESTUDIANTE = 'ESTUDIANTE', 'Estudiante'
    INSTRUCTOR = 'INSTRUCTOR', 'Instructor'
    ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'


class EstadoUsuario(models.TextChoices):
    """Estado de la cuenta del usuario."""
    ACTIVO = 'ACTIVO', 'Activo'
    INACTIVO = 'INACTIVO', 'Inactivo'
    SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'


class NivelExperiencia(models.TextChoices):
    """Nivel de experiencia del estudiante."""
    PRINCIPIANTE = 'PRINCIPIANTE', 'Principiante'
    INTERMEDIO = 'INTERMEDIO', 'Intermedio'
    AVANZADO = 'AVANZADO', 'Avanzado'
    EXPERTO = 'EXPERTO', 'Experto'


class User(AbstractUser):
    """
    Usuario base - mapeo del diagrama Usuario.
    Extiende AbstractUser con tipo de rol y estado.
    """
    tipo = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.ESTUDIANTE
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoUsuario.choices,
        default=EstadoUsuario.ACTIVO
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def es_instructor(self):
        return self.tipo == TipoUsuario.INSTRUCTOR

    @property
    def es_estudiante(self):
        return self.tipo == TipoUsuario.ESTUDIANTE

    @property
    def es_administrador(self):
        return self.tipo == TipoUsuario.ADMINISTRADOR


class Estudiante(models.Model):
    """
    Perfil Estudiante - herencia por composición.
    Datos adicionales para usuarios con rol Estudiante.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='estudiante_profile',
        primary_key=True
    )
    nivel_experiencia = models.CharField(
        max_length=20,
        choices=NivelExperiencia.choices,
        default=NivelExperiencia.PRINCIPIANTE
    )
    puntos_acumulados = models.PositiveIntegerField(default=0)
    fecha_ultimo_acceso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return str(self.user)


class Instructor(models.Model):
    """
    Perfil Instructor - datos adicionales para instructores.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        primary_key=True
    )
    especialidad = models.CharField(max_length=100, blank=True)
    calificacion_promedio = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )
    cursos_publicados = models.PositiveIntegerField(default=0)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructores'

    def __str__(self):
        return str(self.user)
