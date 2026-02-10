"""
Comando para crear datos iniciales de desarrollo.
Uso: python manage.py crear_datos_iniciales
"""
from django.core.management.base import BaseCommand
from catalog.models import Categoria, Curso, EstadoCurso, NivelDificultad, Modulo, Leccion
from users.models import User, TipoUsuario


def get_or_create_categorias():
    data = [
        ('Programación', 'Lenguajes y frameworks de desarrollo'),
        ('Diseño', 'UI/UX, diseño gráfico y herramientas'),
        ('Marketing Digital', 'SEO, redes sociales, publicidad'),
        ('Finanzas', 'Inversiones, contabilidad, finanzas personales'),
        ('Idiomas', 'Inglés, español y otros idiomas'),
        ('Ciberseguridad', 'Seguridad ofensiva y defensiva, Purple Team, Blue Team, Red Team'),
    ]
    cats = []
    for nombre, desc in data:
        c, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
        cats.append(c)
    return cats


def get_or_create_instructors():
    users = []
    for username, email, first_name, tipo in [
        ('instructor1', 'instructor1@skillforge.local', 'María García', TipoUsuario.INSTRUCTOR),
        ('instructor2', 'instructor2@skillforge.local', 'Carlos López', TipoUsuario.INSTRUCTOR),
        ('instructor3', 'instructor3@skillforge.local', 'Ana Martínez', TipoUsuario.INSTRUCTOR),
    ]:
        u, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name.split()[0],
                'last_name': first_name.split()[1] if len(first_name.split()) > 1 else '',
                'tipo': tipo,
            }
        )
        if created:
            u.set_password(username + '123')
            u.save()
        users.append(u)
    return users


CURSOS_DATA = [
    ('Introducción a Python', 'Aprende los fundamentos de Python desde cero.', 0, 'PRINCIPIANTE', 20, 99_000, 0),
    ('Django: Backend profesional', 'Construye APIs y sitios web con Django.', 0, 'INTERMEDIO', 30, 149_000, 0),
    ('JavaScript moderno', 'ES6+, async, frameworks frontend.', 0, 'PRINCIPIANTE', 25, 119_000, 1),
    ('React desde cero', 'Componentes, hooks y estado con React.', 0, 'INTERMEDIO', 28, 139_000, 1),
    ('Diseño UI/UX con Figma', 'Prototipos y sistemas de diseño.', 1, 'PRINCIPIANTE', 18, 89_000, 1),
    ('Illustrator para diseñadores', 'Vectorización e ilustración digital.', 1, 'INTERMEDIO', 22, 109_000, 2),
    ('Photoshop esencial', 'Edición de imágenes y composición.', 1, 'PRINCIPIANTE', 16, 79_000, 2),
    ('SEO para principiantes', 'Posicionamiento en buscadores y keywords.', 2, 'PRINCIPIANTE', 12, 69_000, 2),
    ('Marketing en redes sociales', 'Facebook, Instagram, LinkedIn y métricas.', 2, 'INTERMEDIO', 20, 99_000, 0),
    ('Google Ads y remarketing', 'Campañas de pago y conversión.', 2, 'INTERMEDIO', 15, 129_000, 1),
    ('Finanzas personales', 'Ahorro, presupuesto e inversión básica.', 3, 'PRINCIPIANTE', 10, 59_000, 0),
    ('Excel para finanzas', 'Fórmulas, tablas dinámicas y análisis.', 3, 'INTERMEDIO', 14, 79_000, 2),
    ('Inversión en bolsa', 'Conceptos de mercados y portafolios.', 3, 'AVANZADO', 24, 179_000, 1),
    ('Inglés nivel A1-A2', 'Gramática y vocabulario básico.', 4, 'PRINCIPIANTE', 40, 199_000, 0),
    ('Inglés nivel B1', 'Conversación y comprensión intermedia.', 4, 'INTERMEDIO', 50, 249_000, 1),
    ('Español para negocios', 'Comunicación formal y presentaciones.', 4, 'INTERMEDIO', 20, 99_000, 2),
    ('SQL y bases de datos', 'Consultas, joins y diseño relacional.', 0, 'PRINCIPIANTE', 16, 89_000, 2),
    ('Git y control de versiones', 'Ramas, merge y flujo de trabajo.', 0, 'PRINCIPIANTE', 8, 49_000, 0),
]


def ensure_default_role_users():
    """Crea los 3 usuarios por defecto para acceder a cada panel (Estudiante, Instructor, Administrador)."""
    defaults = [
        ('estudiante', 'estudiante123', TipoUsuario.ESTUDIANTE, 'estudiante@skillforge.local', 'Estudiante', 'Demo'),
        ('instructor', 'instructor123', TipoUsuario.INSTRUCTOR, 'instructor@skillforge.local', 'Instructor', 'Demo'),
        ('admin', 'admin123', TipoUsuario.ADMINISTRADOR, 'admin@skillforge.local', 'Admin', 'SkillForge'),
    ]
    created = []
    for username, password, tipo, email, first_name, last_name in defaults:
        if not User.objects.filter(username=username).exists():
            if tipo == TipoUsuario.ADMINISTRADOR:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    tipo=tipo,
                )
            else:
                u = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    tipo=tipo,
                )
            created.append(username)
    return created


class Command(BaseCommand):
    help = 'Crea categorías, instructores, cursos de ejemplo y usuarios por defecto para los 3 roles'

    def handle(self, *args, **options):
        # Usuarios por defecto para los 3 paneles (Estudiante, Instructor, Administrador)
        created_users = ensure_default_role_users()
        if created_users:
            self.stdout.write(self.style.SUCCESS(f'Usuarios por defecto creados: {", ".join(created_users)}'))

        categorias = get_or_create_categorias()
        self.stdout.write(self.style.SUCCESS(f'Categorías: {len(categorias)} listas'))

        instructores = get_or_create_instructors()
        self.stdout.write(self.style.SUCCESS(f'Instructores: {len(instructores)} listos'))

        created_cursos = 0
        for titulo, desc, cat_idx, nivel, horas, precio, inst_idx in CURSOS_DATA:
            cat = categorias[cat_idx]
            inst = instructores[inst_idx]
            _, was_created = Curso.objects.get_or_create(
                titulo=titulo,
                instructor=inst,
                defaults={
                    'descripcion': desc + ' Ideal para avanzar en tu carrera.',
                    'precio': precio,
                    'categoria': cat,
                    'nivel_dificultad': nivel,
                    'duracion_horas': horas,
                    'estado': EstadoCurso.PUBLICADO,
                    'cupos_totales': 50,
                    'cupos_disponibles': 50,
                }
            )
            if was_created:
                created_cursos += 1

        total = Curso.objects.filter(estado=EstadoCurso.PUBLICADO).count()
        self.stdout.write(self.style.SUCCESS(f'Cursos: {created_cursos} creados (total publicados: {total})'))

        for curso in Curso.objects.filter(estado=EstadoCurso.PUBLICADO).prefetch_related('modulos'):
            if curso.modulos.count() == 0:
                m = Modulo.objects.create(curso=curso, titulo='Módulo 1: Introducción', orden=0)
                Leccion.objects.create(modulo=m, titulo='Bienvenida', tipo='TEXTO', contenido='Contenido de bienvenida.', orden=0)
                Leccion.objects.create(modulo=m, titulo='Conceptos clave', tipo='TEXTO', contenido='Repaso de conceptos.', orden=1)

        self.stdout.write(self.style.SUCCESS('Datos iniciales creados correctamente.'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('--- Credenciales por defecto (3 roles) ---'))
        self.stdout.write('  Estudiante:    estudiante / estudiante123  (Home, Cursos, Mis cursos, Certificaciones, Carrito)')
        self.stdout.write('  Instructor:    instructor / instructor123   (Home, Gestionar cursos, Crear curso)')
        self.stdout.write('  Administrador: admin / admin123            (Home, Panel admin en /panel/)')
        self.stdout.write('')
