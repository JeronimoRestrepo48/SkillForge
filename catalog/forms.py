from django import forms
from .models import Curso, Modulo, Leccion, Calificacion


class CursoForm(forms.ModelForm):
    """Formulario de creación/edición de curso."""

    class Meta:
        model = Curso
        fields = [
            'titulo',
            'descripcion',
            'info_evaluacion',
            'precio',
            'precio_descuento',
            'categoria',
            'nivel_dificultad',
            'duracion_horas',
            'estado',
            'cupos_totales',
            'cupos_disponibles',
            'imagen',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 8}),
            'info_evaluacion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Exámenes, trabajos, criterios de calificación.'}),
        }


class ModuloForm(forms.ModelForm):
    """Formulario de creación/edición de módulo."""

    class Meta:
        model = Modulo
        fields = ['titulo', 'orden', 'duracion_minutos']
        widgets = {
            'orden': forms.NumberInput(attrs={'min': 0}),
            'duracion_minutos': forms.NumberInput(attrs={'min': 0}),
        }


class LeccionForm(forms.ModelForm):
    """Formulario de creación/edición de lección."""

    class Meta:
        model = Leccion
        fields = ['titulo', 'tipo', 'contenido', 'orden', 'duracion_minutos']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 6}),
            'orden': forms.NumberInput(attrs={'min': 0}),
            'duracion_minutos': forms.NumberInput(attrs={'min': 0}),
        }


class CalificacionForm(forms.ModelForm):
    """Formulario para valorar un curso (1-5 estrellas y comentario)."""

    class Meta:
        model = Calificacion
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Opcional. Cuéntanos tu experiencia.'}),
        }
