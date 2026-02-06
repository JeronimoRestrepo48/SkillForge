from django import forms
from .models import Curso


class CursoForm(forms.ModelForm):
    """Formulario de creación/edición de curso."""

    class Meta:
        model = Curso
        fields = [
            'titulo',
            'descripcion',
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
            'descripcion': forms.Textarea(attrs={'rows': 5}),
        }
