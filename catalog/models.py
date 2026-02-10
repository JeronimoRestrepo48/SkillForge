"""
Modelos del dominio Catálogo.
Alineados al diagrama de clases de SkillForge.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.text import Truncator


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
    """Course difficulty level."""
    PRINCIPIANTE = 'PRINCIPIANTE', 'Beginner'
    INTERMEDIO = 'INTERMEDIO', 'Intermediate'
    AVANZADO = 'AVANZADO', 'Advanced'
    EXPERTO = 'EXPERTO', 'Expert'


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
    # Información sobre evaluación (exámenes, trabajos, calificaciones) — visible en detalle del curso
    info_evaluacion = models.TextField(
        blank=True,
        help_text='Criterios de exámenes, trabajos prácticos y sistema de calificaciones.'
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


class Modulo(models.Model):
    """Módulo de un curso. Agrupa lecciones."""
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='modulos'
    )
    titulo = models.CharField(max_length=200)
    orden = models.PositiveIntegerField(default=0)
    duracion_minutos = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['curso', 'orden']
        unique_together = [['curso', 'orden']]

    def __str__(self):
        return f'{self.curso.titulo} - {self.titulo}'


class TipoLeccion(models.TextChoices):
    """Lesson content type."""
    VIDEO = 'VIDEO', 'Video'
    TEXTO = 'TEXTO', 'Text'
    QUIZ = 'QUIZ', 'Quiz'
    PRACTICA = 'PRACTICA', 'Practice'


class Leccion(models.Model):
    """Lección dentro de un módulo."""
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name='lecciones'
    )
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(
        max_length=20,
        choices=TipoLeccion.choices,
        default=TipoLeccion.TEXTO
    )
    contenido = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    duracion_minutos = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
        ordering = ['modulo', 'orden']
        unique_together = [['modulo', 'orden']]

    def __str__(self):
        return f'{self.modulo.titulo} - {self.titulo}'


class ProgresoLeccion(models.Model):
    """Progreso de un usuario en una lección (completada o no)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progreso_lecciones'
    )
    leccion = models.ForeignKey(
        Leccion,
        on_delete=models.CASCADE,
        related_name='progresos'
    )
    completada = models.BooleanField(default=False)
    fecha_completada = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Progreso de lección'
        verbose_name_plural = 'Progresos de lecciones'
        unique_together = [['user', 'leccion']]

    def __str__(self):
        return f'{self.user} - {self.leccion.titulo}'


class Calificacion(models.Model):
    """Calificación/reseña de un curso. Solo estudiantes que completaron pueden valorar."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calificaciones'
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='calificaciones'
    )
    puntuacion = models.PositiveSmallIntegerField()  # 1-5
    comentario = models.TextField(blank=True)
    es_verificada = models.BooleanField(default=False)  # True si completó el curso
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = [['user', 'curso']]
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.user} - {self.curso.titulo}: {self.puntuacion}'


class Certificado(models.Model):
    """Certificado de finalización de curso. Se genera al completar 100%."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificados'
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='certificados'
    )
    inscripcion = models.ForeignKey(
        'transactions.Inscripcion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificados'
    )
    numero_certificado = models.CharField(max_length=50, unique=True)
    codigo_verificacion = models.CharField(max_length=20, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='certificados/', null=True, blank=True)
    plantilla = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
        unique_together = [['user', 'curso']]
        ordering = ['-fecha_emision']

    def __str__(self):
        return f'{self.numero_certificado} - {self.user} - {self.curso.titulo}'


# --- Certificaciones de industria (ej. Purple Team, IA, Ciberseguridad) ---
# Independientes de cursos. Material de estudio + examen certificado; acceso solo tras pago.
# Al aprobar el examen se emite un diploma que avala conocimientos (no solo completitud).


class CertificacionIndustria(models.Model):
    """
    Certificación profesional avalada por la industria: material de estudio y examen (40 preguntas).
    No asociada a cursos. El acceso al material y al examen requiere pago (AccesoCertificacion).
    Al aprobar se emite un diploma PDF que certifica avalación de conocimientos.
    """
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True)
    descripcion = models.TextField(help_text='Descripción extensa: qué avala, a quién va dirigida, qué incluye.')
    imagen = models.ImageField(upload_to='certificaciones_industria/', null=True, blank=True)
    imagen_url = models.URLField(blank=True, help_text='URL de imagen alusiva (si no se sube archivo).')
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        help_text='Precio para acceder al material y al examen (pago simulado).'
    )
    duracion_estimada_horas = models.PositiveIntegerField(default=40)
    activa = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Certificación de industria'
        verbose_name_plural = 'Certificaciones de industria'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class SeccionMaterialCertificacion(models.Model):
    """Sección del material de estudio de una certificación de industria."""
    certificacion = models.ForeignKey(
        CertificacionIndustria,
        on_delete=models.CASCADE,
        related_name='secciones_material'
    )
    titulo = models.CharField(max_length=300)
    orden = models.PositiveIntegerField(default=0)
    contenido = models.TextField(help_text='Contenido en texto o HTML.')

    class Meta:
        ordering = ['certificacion', 'orden']
        unique_together = [['certificacion', 'orden']]

    def __str__(self):
        return f'{self.certificacion.nombre} - {self.titulo}'


class ExamenCertificacion(models.Model):
    """Examen tipo cuestionario de una certificación de industria."""
    certificacion = models.OneToOneField(
        CertificacionIndustria,
        on_delete=models.CASCADE,
        related_name='examen'
    )
    titulo = models.CharField(max_length=200)
    instrucciones = models.TextField(blank=True)
    puntaje_minimo_aprobacion = models.PositiveSmallIntegerField(
        default=70,
        help_text='Porcentaje mínimo para aprobar (0-100).'
    )

    class Meta:
        verbose_name = 'Examen de certificación'
        verbose_name_plural = 'Exámenes de certificación'

    def __str__(self):
        return f'{self.certificacion.nombre} - Examen'


class PreguntaExamen(models.Model):
    """Pregunta del examen (tipo cuestionario)."""
    examen = models.ForeignKey(
        ExamenCertificacion,
        on_delete=models.CASCADE,
        related_name='preguntas'
    )
    enunciado = models.TextField()
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['examen', 'orden']

    def __str__(self):
        return Truncator(self.enunciado).chars(60)


class OpcionPregunta(models.Model):
    """Opción de respuesta de una pregunta (una es la correcta)."""
    pregunta = models.ForeignKey(
        PreguntaExamen,
        on_delete=models.CASCADE,
        related_name='opciones'
    )
    texto = models.CharField(max_length=500)
    es_correcta = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Opción de pregunta'
        verbose_name_plural = 'Opciones de pregunta'

    def __str__(self):
        return self.texto[:50]


class AccesoCertificacion(models.Model):
    """Acceso comprado a una certificación de industria (material + examen)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accesos_certificaciones'
    )
    certificacion = models.ForeignKey(
        CertificacionIndustria,
        on_delete=models.CASCADE,
        related_name='accesos'
    )
    fecha_compra = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'certificacion']]
        ordering = ['-fecha_compra']

    def __str__(self):
        return f'{self.user} — {self.certificacion.nombre}'


class DiplomaCertificacionIndustria(models.Model):
    """
    Diploma emitido al aprobar el examen de una certificación de industria.
    Certifica avalación de conocimientos (no solo completitud de curso).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diplomas_certificaciones'
    )
    certificacion = models.ForeignKey(
        CertificacionIndustria,
        on_delete=models.CASCADE,
        related_name='diplomas'
    )
    fecha_examen = models.DateTimeField(auto_now_add=True)
    puntaje = models.PositiveSmallIntegerField(help_text='Porcentaje obtenido (0-100).')
    aprobado = models.BooleanField(default=True)
    codigo_verificacion = models.CharField(max_length=24, unique=True)

    class Meta:
        unique_together = [['user', 'certificacion']]
        ordering = ['-fecha_examen']

    def __str__(self):
        return f'{self.user} — {self.certificacion.nombre} ({self.puntaje}%)'
