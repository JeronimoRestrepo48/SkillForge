from django.contrib import admin
from .models import (
    Categoria,
    Curso,
    Modulo,
    Leccion,
    ProgresoLeccion,
    Calificacion,
    Certificado,
    Insignia,
    WishlistItem,
    CertificacionIndustria,
    SeccionMaterialCertificacion,
    ExamenCertificacion,
    PreguntaExamen,
    OpcionPregunta,
    AccesoCertificacion,
    DiplomaCertificacionIndustria,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']


class ModuloInline(admin.TabularInline):
    model = Modulo
    extra = 0
    ordering = ['orden']
    show_change_link = True


class LeccionInline(admin.TabularInline):
    model = Leccion
    extra = 0
    ordering = ['orden']
    fields = ['titulo', 'tipo', 'orden', 'duracion_minutos']


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'instructor', 'estado', 'precio', 'cupos_disponibles', 'fecha_creacion']
    list_filter = ['estado', 'categoria', 'nivel_dificultad']
    search_fields = ['titulo', 'descripcion']
    inlines = [ModuloInline]


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'curso', 'orden', 'duracion_minutos']
    list_filter = ['curso']
    search_fields = ['titulo']
    inlines = [LeccionInline]


@admin.register(Leccion)
class LeccionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'modulo', 'tipo', 'orden', 'duracion_minutos']
    list_filter = ['tipo', 'modulo__curso']
    search_fields = ['titulo']


@admin.register(ProgresoLeccion)
class ProgresoLeccionAdmin(admin.ModelAdmin):
    list_display = ['user', 'leccion', 'completada', 'fecha_completada']
    list_filter = ['completada']
    search_fields = ['user__username', 'leccion__titulo']


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ['user', 'curso', 'puntuacion', 'es_verificada', 'fecha_creacion']
    list_filter = ['puntuacion', 'es_verificada']
    search_fields = ['user__username', 'curso__titulo']


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ['numero_certificado', 'user', 'curso', 'codigo_verificacion', 'fecha_emision']
    list_filter = ['curso__categoria']
    search_fields = ['numero_certificado', 'codigo_verificacion', 'user__username']


@admin.register(Insignia)
class InsigniaAdmin(admin.ModelAdmin):
    list_display = ['user', 'tipo', 'fecha_obtencion']
    list_filter = ['tipo']
    search_fields = ['user__username']


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'curso', 'fecha_agregado']
    search_fields = ['user__username', 'curso__titulo']


class SeccionMaterialCertificacionInline(admin.TabularInline):
    model = SeccionMaterialCertificacion
    extra = 0
    ordering = ['orden']


@admin.register(CertificacionIndustria)
class CertificacionIndustriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activa', 'precio', 'orden']
    list_filter = ['activa']
    search_fields = ['nombre', 'slug']
    prepopulated_fields = {'slug': ['nombre']}
    inlines = [SeccionMaterialCertificacionInline]


class OpcionPreguntaInline(admin.TabularInline):
    model = OpcionPregunta
    extra = 2


class PreguntaExamenInline(admin.TabularInline):
    model = PreguntaExamen
    extra = 0


@admin.register(ExamenCertificacion)
class ExamenCertificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'certificacion', 'puntaje_minimo_aprobacion']
    inlines = [PreguntaExamenInline]


@admin.register(PreguntaExamen)
class PreguntaExamenAdmin(admin.ModelAdmin):
    list_display = ['enunciado_short', 'examen', 'orden']
    list_filter = ['examen']
    inlines = [OpcionPreguntaInline]

    def enunciado_short(self, obj):
        return (obj.enunciado or '')[:60]
    enunciado_short.short_description = 'Enunciado'


@admin.register(OpcionPregunta)
class OpcionPreguntaAdmin(admin.ModelAdmin):
    list_display = ['texto_short', 'pregunta', 'es_correcta']
    list_filter = ['es_correcta']

    def texto_short(self, obj):
        return (obj.texto or '')[:50]
    texto_short.short_description = 'Texto'


@admin.register(AccesoCertificacion)
class AccesoCertificacionAdmin(admin.ModelAdmin):
    list_display = ['user', 'certificacion', 'fecha_compra']
    list_filter = ['certificacion']


@admin.register(DiplomaCertificacionIndustria)
class DiplomaCertificacionIndustriaAdmin(admin.ModelAdmin):
    list_display = ['user', 'certificacion', 'puntaje', 'aprobado', 'fecha_examen', 'codigo_verificacion']
    list_filter = ['certificacion', 'aprobado']
