from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, TipoUsuario


class RegisterForm(UserCreationForm):
    """Formulario de registro con selección de rol."""
    tipo = forms.ChoiceField(
        choices=[
            (TipoUsuario.ESTUDIANTE, 'Estudiante'),
            (TipoUsuario.INSTRUCTOR, 'Instructor'),
        ],
        widget=forms.RadioSelect,
        label='Quiero registrarme como',
    )
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False, label='Nombre')
    last_name = forms.CharField(max_length=150, required=False, label='Apellido')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'tipo', 'password1', 'password2']
