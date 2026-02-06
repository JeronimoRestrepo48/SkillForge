from django.contrib import admin
from .models import Categoria, Curso


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'instructor', 'estado', 'precio', 'fecha_creacion']
    list_filter = ['estado', 'categoria', 'nivel_dificultad']
    search_fields = ['titulo', 'descripcion']
