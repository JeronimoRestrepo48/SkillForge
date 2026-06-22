import subprocess
import time

courses_data = [
    {'title': 'React.js Avanzado: Hooks y Context', 'img': 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=500&fit=crop'},
    {'title': 'Node.js y Express desde Cero', 'img': 'https://images.unsplash.com/photo-1555099962-4199c345e5dd?w=800&h=500&fit=crop'},
    {'title': 'CSS Grid y Flexbox Masterclass', 'img': 'https://images.unsplash.com/photo-1547658719-b28e6f1f15e5?w=800&h=500&fit=crop'},
    {'title': 'Certificación Fullstack MERN', 'img': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&h=500&fit=crop'},
    {'title': 'Python para Análisis de Datos', 'img': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=500&fit=crop'},
    {'title': 'Certificación en Machine Learning con Scikit-Learn', 'img': 'https://images.unsplash.com/photo-1504868584819-eb814187f54c?w=800&h=500&fit=crop'},
    {'title': 'Deep Learning con TensorFlow', 'img': 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&h=500&fit=crop'},
    {'title': 'Diseño de Microservicios', 'img': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=500&fit=crop'},
    {'title': 'Patrones de Arquitectura Cloud', 'img': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=500&fit=crop'},
    {'title': 'Certificación AWS Serverless', 'img': 'https://images.unsplash.com/photo-1614064641913-6b70fea5af2e?w=800&h=500&fit=crop'},
    {'title': 'Fundamentos de Diseño UX', 'img': 'https://images.unsplash.com/photo-1561070791-2526d3098f71?w=800&h=500&fit=crop'},
    {'title': 'Prototipado Avanzado en Figma', 'img': 'https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=800&h=500&fit=crop'},
    {'title': 'Introducción al Ethical Hacking', 'img': 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&h=500&fit=crop'},
    {'title': 'Certificación en Seguridad Web (OWASP)', 'img': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&h=500&fit=crop'},
    {'title': 'Análisis Forense Digital', 'img': 'https://images.unsplash.com/photo-1563206767-5b38d0010d2c?w=800&h=500&fit=crop'}
]
trayectorias_data = [
    {'nombre': 'Ruta de Arquitectura y Backend', 'img': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=500&fit=crop'},
    {'nombre': 'Ruta de Diseño y Frontend', 'img': 'https://images.unsplash.com/photo-1507608158173-1dcec673a2e5?w=800&h=500&fit=crop'}
]

for c in courses_data:
    title = c['title'].replace("'", "''")
    cmd = f'docker exec skillforge2-catalog-db-1 psql -U catalog -d catalogdb -c "UPDATE courses SET imagen_url=\'{c["img"]}\' WHERE title=\'{title}\';"'
    subprocess.run(cmd, shell=True, check=True)

for t in trayectorias_data:
    nombre = t['nombre'].replace("'", "''")
    cmd = f'docker exec skillforge2-catalog-db-1 psql -U catalog -d catalogdb -c "UPDATE trayectorias SET imagen_url=\'{t["img"]}\' WHERE nombre=\'{nombre}\';"'
    subprocess.run(cmd, shell=True, check=True)
