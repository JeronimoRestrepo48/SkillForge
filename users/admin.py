from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Estudiante, Instructor, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'tipo', 'estado', 'fecha_registro']
    list_filter = ['tipo', 'estado']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SkillForge', {'fields': ('tipo', 'estado', 'fecha_registro')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SkillForge', {'fields': ('tipo', 'estado')}),
    )


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ['user', 'nivel_experiencia', 'puntos_acumulados']


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'especialidad', 'calificacion_promedio', 'cursos_publicados']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio_short']
    search_fields = ['user__username', 'bio']

    def bio_short(self, obj):
        return (obj.bio[:50] + '...') if obj.bio and len(obj.bio) > 50 else (obj.bio or '')
    bio_short.short_description = 'Bio'
