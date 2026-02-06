"""
Servicio de usuarios - encapsula la lógica de negocio del dominio Usuarios.
Principio de Responsabilidad Única (SRP): una única razón de cambio.
"""
from django.db import transaction

from users.models import User, Estudiante, Instructor, TipoUsuario, NivelExperiencia


def crear_usuario(
    username: str,
    email: str,
    password: str,
    first_name: str = '',
    last_name: str = '',
    tipo: str = TipoUsuario.ESTUDIANTE,
) -> User:
    """
    Crea un usuario con su perfil asociado según el tipo.
    Usa transacción atómica para garantizar consistencia.
    """
    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            tipo=tipo,
        )
        if tipo == TipoUsuario.ESTUDIANTE:
            crear_estudiante(user)
        elif tipo == TipoUsuario.INSTRUCTOR:
            crear_instructor(user)
        return user


def crear_estudiante(user: User) -> Estudiante:
    """Crea el perfil de Estudiante para un usuario."""
    return Estudiante.objects.create(
        user=user,
        nivel_experiencia=NivelExperiencia.PRINCIPIANTE,
    )


def crear_instructor(user: User) -> Instructor:
    """Crea el perfil de Instructor para un usuario."""
    return Instructor.objects.create(
        user=user,
        especialidad='',
    )
