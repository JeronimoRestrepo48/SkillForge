from django.contrib import admin
from .models import (
    Categoria,
    Curso,
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


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'instructor', 'estado', 'precio', 'fecha_creacion']
    list_filter = ['estado', 'categoria', 'nivel_dificultad']
    search_fields = ['titulo', 'descripcion']


class SeccionMaterialCertificacionInline(admin.TabularInline):
    model = SeccionMaterialCertificacion
    extra = 0
    ordering = ['orden']


@admin.register(CertificacionIndustria)
class CertificacionIndustriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activa', 'orden']
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
