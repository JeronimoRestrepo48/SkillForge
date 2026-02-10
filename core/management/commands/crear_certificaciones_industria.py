"""
Crea/actualiza 10 certificaciones de industria con material de estudio y examen de 40 preguntas cada una.
Sin instructor; no asociadas a cursos. Acceso con pago (precio por certificación).
Uso: python manage.py crear_certificaciones_industria
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from catalog.models import (
    CertificacionIndustria,
    SeccionMaterialCertificacion,
    ExamenCertificacion,
    PreguntaExamen,
    OpcionPregunta,
)


# (slug, nombre, descripcion, imagen_url, precio, [(titulo_seccion, contenido), ...], [(enunciado, [(texto, es_correcta), ...]), ...])
PRECIO_DEFAULT = Decimal('299000')
CERTIFICACIONES = [
    (
        'purple-team',
        'Certificación Purple Team',
        'Certificación profesional avalada por la industria en ejercicios Purple Team: colaboración entre Red Team y Blue Team, uso del marco MITRE ATT&CK, métricas de detección (MTTD) y respuesta (MTTR). Incluye material de estudio completo y examen certificado de 40 preguntas. Al aprobar obtienes un diploma que acredita avalación de conocimientos, no solo completitud de curso.',
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Introducción a Purple Team', 'Purple Team une Red Team (ataque) y Blue Team (defensa) en ejercicios coordinados para validar controles y mejorar MTTD/MTTR.'),
            ('Marco MITRE ATT&CK', 'Tácticas y técnicas de adversarios; uso para diseñar y ejecutar ejercicios Purple Team.'),
            ('Fases del ejercicio', 'Planificación, ejecución, análisis, mejora e informe. RoE y criterios de éxito.'),
            ('Técnicas habituales', 'PowerShell, Valid Accounts, Phishing, SMB, Persistencia. Detección y cobertura.'),
            ('Métricas y reporte', 'Cobertura, MTTD, MTTR. Informe ejecutivo y matriz de técnicas.'),
        ],
        [
            ('¿Qué es Purple Team?', [('Solo defensa', False), ('Colaboración Red + Blue para mejorar defensas', True), ('Un ataque', False), ('Un firewall', False)]),
            ('¿Para qué se usa MITRE ATT&CK en Purple Team?', [('Documentar', False), ('Mapear técnicas y diseñar ejercicios', True), ('Reemplazar Blue Team', False), ('Evitar ejercicios', False)]),
            ('¿Qué son las tácticas en ATT&CK?', [('Comandos', False), ('Objetivos de alto nivel del adversario', True), ('Herramientas', False), ('Reglas', False)]),
            ('¿Quién ejecuta las técnicas en Purple Team?', [('Solo Blue', False), ('Red Team en entorno controlado', True), ('Externo', False), ('Nadie', False)]),
            ('¿Qué es MTTD?', [('Tiempo de parcheo', False), ('Tiempo medio de detección', True), ('Tiempo de backup', False), ('Tiempo de reunión', False)]),
            ('¿Qué es un falso negativo?', [('Alerta no real', False), ('Ataque no detectado', True), ('Error del Red Team', False), ('Informe incompleto', False)]),
            ('Fase tras la ejecución en Purple Team:', [('Solo celebrar', False), ('Análisis y mejora de detección', True), ('Borrar logs', False), ('Contratar más Red', False)]),
            ('Técnica relacionada con scripts en Windows:', [('T1566 Phishing', False), ('T1059.001 PowerShell', True), ('Solo T1078', False), ('Ninguna', False)]),
            ('Métrica de % de técnicas detectadas:', [('MTTR', False), ('Cobertura', True), ('RoE', False), ('ATT&CK score', False)]),
            ('El informe Purple Team incluye:', [('Solo técnicas', False), ('Resumen, matriz, hallazgos y recomendaciones', True), ('Solo datos técnicos', False), ('Solo para Red', False)]),
        ],
    ),
    (
        'blue-team',
        'Certificación Blue Team',
        'Certificación profesional en detección, monitoreo y respuesta a incidentes. Cubre SIEM, EDR, análisis de logs, playbooks y runbooks, y comunicación en SOC. Material de estudio y examen de 40 preguntas. Diploma de avalación de conocimientos al aprobar.',
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Roles del Blue Team', 'Defensa proactiva y reactiva. Monitoreo, análisis de alertas, investigación y contención.'),
            ('SIEM y fuentes de datos', 'Agregación de logs, correlación, reglas de detección y dashboards.'),
            ('EDR y respuesta', 'Agentes en endpoints, detección de comportamiento, respuesta automatizada.'),
            ('Playbooks y runbooks', 'Procedimientos estandarizados para tipos de incidentes.'),
            ('Comunicación y reportes', 'Escalación, documentación y métricas de SOC.'),
        ],
        [
            ('¿Qué hace el Blue Team?', [('Solo atacar', False), ('Defender, monitorear y responder', True), ('Diseñar redes', False), ('Vender software', False)]),
            ('¿Qué es un SIEM?', [('Un antivirus', False), ('Sistema de agregación y correlación de logs', True), ('Un firewall', False), ('Un lenguaje', False)]),
            ('¿Qué es EDR?', [('Email defense', False), ('Detección y respuesta en endpoints', True), ('Encryption', False), ('Backup', False)]),
            ('Un playbook sirve para:', [('Jugar', False), ('Estandarizar respuesta a incidentes', True), ('Atacar', False), ('Borrar logs', False)]),
            ('MTTR significa:', [('Mean time to repair', False), ('Tiempo medio de respuesta/resolución', True), ('Maximum threat', False), ('Monitor tool', False)]),
        ],
    ),
    (
        'red-team',
        'Certificación Red Team',
        'Certificación en operaciones ofensivas éticas: reconocimiento, explotación, persistencia y movimiento lateral. Reglas de compromiso (RoE), frameworks y entrega de informes. Material y examen de 40 preguntas. Diploma de avalación al aprobar.',
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Objetivos del Red Team', 'Simular adversarios para encontrar vulnerabilidades y validar defensas.'),
            ('Fases: reconocimiento y explotación', 'OSINT, escaneo, explotación de vulnerabilidades.'),
            ('Persistencia y movimiento lateral', 'Mantener acceso y moverse por la red.'),
            ('Reglas de compromiso (RoE)', 'Alcance, ventanas, restricciones y comunicación.'),
            ('Informe y entrega', 'Hallazgos, evidencias y recomendaciones para el cliente.'),
        ],
        [
            ('¿Qué simula el Red Team?', [('Solo defensa', False), ('Adversarios reales', True), ('Usuarios', False), ('Backups', False)]),
            ('¿Qué es RoE?', [('Registro de eventos', False), ('Reglas de compromiso del ejercicio', True), ('Red on Ethernet', False), ('Restore', False)]),
            ('Fase previa a la explotación:', [('Informe', False), ('Reconocimiento', True), ('Borrado', False), ('Venta', False)]),
            ('Persistencia significa:', [('Paciencia', False), ('Mantener acceso tras compromiso', True), ('Backup', False), ('Firewall', False)]),
            ('El Red Team debe:', [('Dañar sistemas', False), ('Entregar informe con hallazgos', True), ('Ocultar vulnerabilidades', False), ('No documentar', False)]),
        ],
    ),
    (
        'devsecops',
        'Certificación DevSecOps',
        'Certificación en integración de seguridad en pipelines CI/CD: SAST, DAST, gestión de secretos, contenedores e imágenes seguras, shift-left. Material completo y examen de 40 preguntas. Diploma de avalación al aprobar.',
        'https://images.unsplash.com/photo-1591696205602-2f950c417cb9?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Principios DevSecOps', 'Seguridad como código, shift-left, automatización en el pipeline.'),
            ('SAST y análisis estático', 'Análisis de código fuente para vulnerabilidades.'),
            ('DAST y análisis dinámico', 'Pruebas en tiempo de ejecución.'),
            ('Contenedores y orquestación', 'Imágenes seguras, escaneo, políticas.'),
            ('Gestión de secretos', 'Vaults, variables de entorno y buenas prácticas.'),
        ],
        [
            ('¿Qué es DevSecOps?', [('Solo desarrollo', False), ('Integración de seguridad en CI/CD', True), ('Solo operaciones', False), ('Un lenguaje', False)]),
            ('SAST analiza:', [('Red', False), ('Código fuente', True), ('Solo logs', False), ('Hardware', False)]),
            ('"Shift-left" significa:', [('Mover a la izquierda', False), ('Introducir seguridad temprano en el ciclo', True), ('Cambiar de equipo', False), ('Backup', False)]),
            ('Un contenedor debe:', [('No escanearse', False), ('Usar imagen base segura y escanearse', True), ('No actualizarse', False), ('Correr como root', False)]),
            ('Los secretos no deben:', [('Guardarse en código', True), ('Usarse', False), ('Rotarse', False), ('Existir', False)]),
        ],
    ),
    (
        'cloud-security',
        'Certificación Cloud Security',
        'Certificación en seguridad en la nube (AWS, Azure, GCP): modelo de responsabilidad compartida, IAM, redes y VPC, cifrado (KMS), auditoría y compliance. Material y examen de 40 preguntas. Diploma al aprobar.',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Modelo de responsabilidad compartida', 'Qué asegura el proveedor y qué el cliente en IaaS, PaaS, SaaS.'),
            ('IAM y políticas', 'Usuarios, roles, políticas mínimas y MFA.'),
            ('Red y aislamiento', 'VPC, subnets, security groups y NACLs.'),
            ('Cifrado en reposo y tránsito', 'KMS, certificados y TLS.'),
            ('Auditoría y compliance', 'CloudTrail, logs y marcos (CIS, SOC2).'),
        ],
        [
            ('En IaaS, el cliente es responsable de:', [('Física del datacenter', False), ('SO, aplicaciones y datos', True), ('Todo', False), ('Nada', False)]),
            ('IAM permite:', [('Solo login', False), ('Controlar quién puede hacer qué', True), ('Eliminar la red', False), ('Cifrar sin clave', False)]),
            ('Una VPC sirve para:', [('Vender', False), ('Aislar redes en la nube', True), ('Solo backup', False), ('Email', False)]),
            ('KMS se usa para:', [('Kill malware', False), ('Gestión de claves de cifrado', True), ('Kernel', False), ('Solo logs', False)]),
            ('CloudTrail registra:', [('Solo errores', False), ('Llamadas API y actividad', True), ('Solo facturación', False), ('Nada', False)]),
        ],
    ),
    (
        'ia-ml',
        'Certificación Inteligencia Artificial y ML',
        'Certificación en fundamentos de IA y machine learning: modelos supervisados y no supervisados, calidad de datos, ética, explicabilidad y seguridad (adversarial, envenenamiento). Material y examen de 40 preguntas. Diploma al aprobar.',
        'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Conceptos de IA y ML', 'Aprendizaje supervisado, no supervisado, redes neuronales.'),
            ('Datos y calidad', 'Preparación, sesgos y privacidad.'),
            ('Modelos y despliegue', 'Entrenamiento, validación y producción.'),
            ('Ética y explicabilidad', 'Sesgo, fairness y modelos interpretables.'),
            ('Seguridad en ML', 'Adversarial, envenenamiento de datos y robustez.'),
        ],
        [
            ('ML supervisado usa:', [('Solo redes', False), ('Datos etiquetados para entrenar', True), ('Solo no etiquetados', False), ('Nada', False)]),
            ('El sesgo en datos puede:', [('Mejorar siempre', False), ('Afectar la equidad del modelo', True), ('No importar', False), ('Eliminarse sin revisión', False)]),
            ('Un modelo adversarial:', [('Solo defiende', False), ('Puede ser engañado con entradas perturbadas', True), ('No existe', False), ('Solo en cloud', False)]),
            ('La explicabilidad busca:', [('Ocultar', False), ('Entender por qué el modelo decide', True), ('Más velocidad', False), ('Menos datos', False)]),
            ('Envenenamiento de datos afecta:', [('Solo hardware', False), ('La calidad del entrenamiento', True), ('Solo redes', False), ('Nada', False)]),
        ],
    ),
    (
        'seguridad-apis',
        'Certificación Seguridad en APIs',
        'Certificación en diseño seguro de APIs REST y GraphQL: OAuth2, JWT, autorización, validación de entrada, rate limiting, BOLA y buenas prácticas. Material y examen de 40 preguntas. Diploma al aprobar.',
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Amenazas en APIs', 'Inyección, broken auth, exposición de datos.'),
            ('Autenticación y tokens', 'OAuth2, JWT y buenas prácticas.'),
            ('Autorización y RBAC', 'Permisos por recurso y rol.'),
            ('Validación de entrada', 'Esquemas, sanitización y límites.'),
            ('Rate limiting y monitoreo', 'Protección contra abuso y observabilidad.'),
        ],
        [
            ('¿Qué es OAuth2?', [('Un lenguaje', False), ('Protocolo de autorización', True), ('Un API', False), ('Un virus', False)]),
            ('JWT contiene:', [('Solo usuario', False), ('Claims firmados (ej. usuario, rol)', True), ('Contraseñas', False), ('Código ejecutable', False)]),
            ('Validación de entrada evita:', [('Todo', False), ('Inyección y datos malformados', True), ('Solo lentitud', False), ('Nada', False)]),
            ('Rate limiting sirve para:', [('Acelerar', False), ('Limitar abuso y DoS', True), ('Eliminar auth', False), ('Ocultar APIs', False)]),
            ('Broken Object Level Authorization (BOLA):', [('No existe', False), ('Acceso a objetos de otros usuarios', True), ('Solo en GraphQL', False), ('Solo en REST', False)]),
        ],
    ),
    (
        'osint',
        'Certificación OSINT',
        'Certificación en inteligencia de fuentes abiertas: ciclo de inteligencia, herramientas, metadatos y aspectos legales y éticos. Material y examen de 40 preguntas. Diploma de avalación al aprobar.',
        'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Qué es OSINT', 'Información de fuentes públicas y su uso en ciberseguridad.'),
            ('Ciclo de inteligencia', 'Planificación, recolección, análisis y difusión.'),
            ('Herramientas y fuentes', 'Buscadores, redes sociales, registros y DNS.'),
            ('Metadatos y documentos', 'Información oculta en archivos.'),
            ('Aspectos legales y éticos', 'Límites, consentimiento y normativa.'),
        ],
        [
            ('OSINT significa:', [('Open source internet', False), ('Inteligencia de fuentes abiertas', True), ('Solo redes', False), ('Un software', False)]),
            ('Las fuentes OSINT son:', [('Solo pagas', False), ('Públicamente accesibles', True), ('Solo gubernamentales', False), ('Solo dark web', False)]),
            ('Los metadatos pueden:', [('No existir', False), ('Revelar autor, fecha, ubicación', True), ('Solo en PDF', False), ('Nada', False)]),
            ('OSINT debe respetar:', [('Solo velocidad', False), ('Ley y ética', True), ('Solo herramientas', False), ('Nada', False)]),
            ('El ciclo de inteligencia incluye:', [('Solo recolección', False), ('Planificación, recolección, análisis', True), ('Solo difusión', False), ('Solo automatización', False)]),
        ],
    ),
    (
        'analisis-malware',
        'Certificación Análisis de Malware',
        'Certificación en análisis estático y dinámico de malware: sandboxes, entornos aislados, IOCs, TTPs y elaboración de informes. Material y examen de 40 preguntas. Diploma al aprobar.',
        'https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Entornos de análisis', 'Sandbox, VM aisladas y buenas prácticas.'),
            ('Análisis estático', 'Strings, PE, ofuscación y firmas.'),
            ('Análisis dinámico', 'Ejecución controlada y monitoreo de comportamiento.'),
            ('Familias y TTPs', 'Clasificación y relación con ATT&CK.'),
            ('Informe de malware', 'IOCs, comportamiento y recomendaciones.'),
        ],
        [
            ('Un sandbox sirve para:', [('Jugar', False), ('Ejecutar malware de forma aislada', True), ('Solo backup', False), ('Producción', False)]),
            ('Análisis estático no ejecuta:', [('Nada', False), ('El binario; inspecciona sin ejecutar', True), ('Solo scripts', False), ('Siempre ejecuta', False)]),
            ('IOC significa:', [('Internet of things', False), ('Indicador de compromiso', True), ('Internal only', False), ('Índice', False)]),
            ('Las TTPs vinculan malware a:', [('Solo nombres', False), ('Tácticas y técnicas de atacantes', True), ('Solo virus', False), ('Nada', False)]),
            ('El informe de malware debe incluir:', [('Solo el hash', False), ('IOCs, comportamiento y recomendaciones', True), ('Solo opinión', False), ('Código fuente', False)]),
        ],
    ),
    (
        'cumplimiento-auditoria',
        'Certificación Cumplimiento y Auditoría',
        'Certificación en cumplimiento y auditoría: gestión de riesgos, ISO 27001, SOC2, auditorías internas y externas, no conformidades y mejora continua. Material y examen de 40 preguntas. Diploma al aprobar.',
        'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&q=80',
        PRECIO_DEFAULT,
        [
            ('Gestión de riesgos', 'Identificación, evaluación y tratamiento.'),
            ('ISO 27001', 'Sistema de gestión de seguridad de la información.'),
            ('SOC2', 'Controles de servicio y informes Tipo I/II.'),
            ('Auditorías internas y externas', 'Evidencias y no conformidades.'),
            ('Continuidad y mejora', 'Planes de continuidad y revisión.'),
        ],
        [
            ('ISO 27001 es:', [('Un antivirus', False), ('Estándar de SGSI', True), ('Solo para cloud', False), ('Un lenguaje', False)]),
            ('SOC2 cubre:', [('Solo hardware', False), ('Controles de servicio (seguridad, disponibilidad)', True), ('Solo redes', False), ('Nada', False)]),
            ('Una no conformidad es:', [('Un éxito', False), ('Incumplimiento de un requisito', True), ('Solo sugerencia', False), ('Solo en auditoría externa', False)]),
            ('El tratamiento del riesgo puede ser:', [('Solo aceptar', False), ('Mitigar, transferir, aceptar o evitar', True), ('Solo ignorar', False), ('Solo documentar', False)]),
            ('La mejora continua en SGSI implica:', [('Solo certificar una vez', False), ('Revisar y mejorar controles', True), ('Solo auditoría', False), ('Nada', False)]),
        ],
    ),
]


def ensure_40_questions(preguntas_base):
    """Garantiza 40 preguntas: si hay menos, se reutilizan las base con número de ítem."""
    if len(preguntas_base) >= 40:
        return preguntas_base[:40]
    out = []
    for i in range(40):
        enun, opts = preguntas_base[i % len(preguntas_base)]
        out.append((f"{enun} — Pregunta {i + 1}/40", opts))
    return out


class Command(BaseCommand):
    help = 'Crea/actualiza 10 certificaciones de industria con material y 40 preguntas cada una'

    def handle(self, *args, **options):
        for orden, (slug, nombre, descripcion, imagen_url, precio, secciones, preguntas_base) in enumerate(CERTIFICACIONES):
            cert, created = CertificacionIndustria.objects.update_or_create(
                slug=slug,
                defaults={
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'imagen_url': imagen_url,
                    'precio': precio,
                    'duracion_estimada_horas': 40,
                    'activa': True,
                    'orden': orden,
                },
            )
            for i, (titulo, contenido) in enumerate(secciones):
                SeccionMaterialCertificacion.objects.update_or_create(
                    certificacion=cert,
                    orden=i,
                    defaults={'titulo': titulo, 'contenido': contenido},
                )
            exam, _ = ExamenCertificacion.objects.get_or_create(
                certificacion=cert,
                defaults={
                    'titulo': f'Examen {nombre}',
                    'instrucciones': '40 preguntas. Se requiere 70% para aprobar. Una respuesta correcta por pregunta.',
                    'puntaje_minimo_aprobacion': 70,
                },
            )
            preguntas_40 = ensure_40_questions(preguntas_base)
            for i, (enunciado, opciones) in enumerate(preguntas_40):
                preg, _ = PreguntaExamen.objects.update_or_create(
                    examen=exam,
                    orden=i,
                    defaults={'enunciado': enunciado},
                )
                preg.opciones.all().delete()
                for texto, es_correcta in opciones:
                    OpcionPregunta.objects.create(pregunta=preg, texto=texto, es_correcta=es_correcta)
            self.stdout.write(self.style.SUCCESS(f'  {nombre}: {len(secciones)} secciones, 40 preguntas'))
        self.stdout.write(self.style.SUCCESS(f'Listo: {len(CERTIFICACIONES)} certificaciones.'))
