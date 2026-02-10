"""Template tags/filters for course placeholder images and other helpers."""
import re
from urllib.parse import quote_plus

from django import template
from django.utils.text import Truncator

register = template.Library()


def _sin_certificacion_str(value):
    """Quita referencias a 'Certificación' en un string (uso interno y en filtro)."""
    if value is None or not isinstance(value, str):
        return value
    s = value.strip()
    s = re.sub(r'^Certificación\s+', '', s)
    s = re.sub(r'Certificación de industria reconocida:\s*', 'Avalada por la industria: ', s, flags=re.IGNORECASE)
    s = re.sub(r'Certificación profesional (avalada |)por la industria[:\s]*', 'Avalada por la industria: ', s, flags=re.IGNORECASE)
    return s


@register.filter
def sin_certificacion(value):
    """
    Quita referencias a 'Certificación' en títulos y descripciones de cursos,
    para que en la vista de cursos no se muestre esa etiqueta.
    """
    return _sin_certificacion_str(value)

# Imágenes temáticas por curso: cada curso muestra una imagen alusiva (logos o Unsplash)
# Orden: más específico primero (ej. "git" antes de "programación")
IMAGENES_TEMATICAS = {
    # Logos / imágenes muy específicas
    'git': 'https://git-scm.com/images/logo@2x.png',
    'control de versiones': 'https://git-scm.com/images/logo@2x.png',
    'python': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&q=80',
    'django': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&q=80',
    'javascript': 'https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?w=800&q=80',
    'react': 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80',
    'sql': 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&q=80',
    'base de datos': 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&q=80',
    'bases de datos': 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&q=80',
    'figma': 'https://images.unsplash.com/photo-1561070791-2526d31fe5b6?w=800&q=80',
    'diseño': 'https://images.unsplash.com/photo-1561070791-2526d31fe5b6?w=800&q=80',
    'illustrator': 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=800&q=80',
    'photoshop': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&q=80',
    'ui': 'https://images.unsplash.com/photo-1561070791-2526d31fe5b6?w=800&q=80',
    'ux': 'https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800&q=80',
    'seo': 'https://estudiarvirtual.unipiloto.edu.co/blog/tipos-de-marketing-que-existen',
    'marketing': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80',
    'redes sociales': 'https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=800&q=80',
    'google ads': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&q=80',
    'remarketing': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&q=80',
    'finanzas': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80',
    'excel': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
    'inversión': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
    'bolsa': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
    'inglés': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80',
    'español': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=800&q=80',
    'negocios': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&q=80',
    'idiomas': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80',
    'programación': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80',
    'introducción': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80',
    'backend': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&q=80',
    'moderno': 'https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?w=800&q=80',
    'desde cero': 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80',
    'principiantes': 'https://images.unsplash.com/photo-1432888622747-4eb9a8f2b6c3?w=800&q=80',
    'personal': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80',
    'nivel': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80',
    'gramática': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80',
    'conversación': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80',
    'comunicación': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&q=80',
    'presentaciones': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&q=80',
    'consultas': 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&q=80',
    'joins': 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&q=80',
    'relacional': 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&q=80',
    'ramas': 'https://git-scm.com/images/logo@2x.png',
    'merge': 'https://git-scm.com/images/logo@2x.png',
    'vectorización': 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=800&q=80',
    'edición': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&q=80',
    'posicionamiento': 'https://images.unsplash.com/photo-1432888622747-4eb9a8f2b6c3?w=800&q=80',
    'keywords': 'https://images.unsplash.com/photo-1432888622747-4eb9a8f2b6c3?w=800&q=80',
    'ahorro': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80',
    'presupuesto': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80',
    'fórmulas': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
    'tablas dinámicas': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
    'mercados': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
    'portafolios': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
    'vocabulario': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80',
    'comprensión': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80',
    'prototipos': 'https://images.unsplash.com/photo-1561070791-2526d31fe5b6?w=800&q=80',
}


def _get_theme_image_for_course(titulo, categoria_nombre, size='800x380'):
    """Return a theme-specific image URL for a course (title + category)."""
    if not titulo:
        titulo = ''
    else:
        titulo = _sin_certificacion_str(titulo)
    if not categoria_nombre:
        categoria_nombre = ''
    combined = f'{titulo} {categoria_nombre}'.lower()
    for keyword, url in IMAGENES_TEMATICAS.items():
        if keyword in combined:
            # Ajustar tamaño en URL Unsplash si aplica
            if 'w=800' in url and size:
                w, h = size.split('x') if 'x' in size else (800, 380)
                url = url.replace('w=800', f'w={w}')
            return url
    # Fallback: placeholder con texto del curso (sin prefijo "Certificación")
    text = Truncator(titulo or 'Course').chars(28)
    encoded = quote_plus(text)
    return f'https://placehold.co/{size}/1a1a2e/eee?text={encoded}'


@register.filter
def placeholder_course_image(titulo, size='400x225'):
    """
    Build a placeholder image URL with the course title as text (alusiva al curso).
    size: e.g. '400x225' for cards, '800x380' for detail.
    """
    if not titulo:
        titulo = 'Course'
    text = Truncator(titulo).chars(28)
    encoded = quote_plus(text)
    return f'https://placehold.co/{size}/1a1a2e/eee?text={encoded}'


@register.filter
def course_theme_image(curso, size='800x380'):
    """
    Return a theme-specific image URL for the course (e.g. business for "Español para negocios").
    Use: {{ curso|course_theme_image:'800x380' }}
    If curso.imagen is set, the template should use that instead; this is for when no image is uploaded.
    """
    if not curso:
        return f'https://placehold.co/{size}/1a1a2e/eee?text=Course'
    titulo = getattr(curso, 'titulo', '') or ''
    categoria_nombre = ''
    if hasattr(curso, 'categoria') and curso.categoria:
        categoria_nombre = getattr(curso.categoria, 'nombre', '') or ''
    return _get_theme_image_for_course(titulo, categoria_nombre, size)
