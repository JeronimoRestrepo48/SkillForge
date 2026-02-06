"""Mixins reutilizables para vistas."""
from django.contrib.auth.mixins import UserPassesTestMixin


class InstructorRequiredMixin(UserPassesTestMixin):
    """Mixin que restringe el acceso a usuarios con rol de Instructor."""

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.tipo == 'INSTRUCTOR'
        )


class EstudianteRequiredMixin(UserPassesTestMixin):
    """Mixin que restringe el acceso a usuarios con rol de Estudiante."""

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.tipo == 'ESTUDIANTE'
        )
