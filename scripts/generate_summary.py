import os
import glob
import subprocess

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output

out = []

out.append('=== 1. CATALOG-SERVICE ===\n')

# Modelos
out.append('--- Modelos (catalog-service/app/models/*.py) ---')
models = glob.glob('microservices/services/catalog-service/app/models/*.py')
for m in models:
    if '__init__' not in m:
        out.append(f'\n# Archivo: {m}\n')
        with open(m, 'r', encoding='utf-8') as f:
            out.append(f.read())

# Schemas
out.append('\n--- Schemas (catalog-service/app/schemas/*.py) ---')
schemas = glob.glob('microservices/services/catalog-service/app/schemas/*.py')
for s in schemas:
    if '__init__' not in s:
        out.append(f'\n# Archivo: {s}\n')
        with open(s, 'r', encoding='utf-8') as f:
            out.append(f.read())

# Estructura de carpetas
out.append('\n--- Estructura de carpetas (2 niveles) ---')
out.append(run_cmd('powershell -Command "(Get-ChildItem -Path microservices/services/catalog-service -Recurse -Depth 2).FullName"'))

# Rutas
out.append('\n--- Rutas/Endpoints ---')
routers = glob.glob('microservices/services/catalog-service/app/routers/*.py')
for r in routers:
    with open(r, 'r', encoding='utf-8') as f:
        for line in f:
            if '@router.' in line:
                out.append(f'{os.path.basename(r)}: {line.strip()}')

out.append('\n\n=== 2. AUTH-SERVICE ===\n')

# Modelos
out.append('--- Modelos (auth-service/app/models/*.py) ---')
models = glob.glob('microservices/services/auth-service/app/models/*.py')
for m in models:
    if '__init__' not in m:
        out.append(f'\n# Archivo: {m}\n')
        with open(m, 'r', encoding='utf-8') as f:
            out.append(f.read())

# Schemas
out.append('\n--- Schemas (auth-service/app/schemas/*.py) ---')
schemas = glob.glob('microservices/services/auth-service/app/schemas/*.py')
for s in schemas:
    if '__init__' not in s:
        out.append(f'\n# Archivo: {s}\n')
        with open(s, 'r', encoding='utf-8') as f:
            out.append(f.read())

# Rutas
out.append('\n--- Rutas/Endpoints ---')
routers = glob.glob('microservices/services/auth-service/app/routers/*.py')
for r in routers:
    with open(r, 'r', encoding='utf-8') as f:
        for line in f:
            if '@router.' in line:
                out.append(f'{os.path.basename(r)}: {line.strip()}')

out.append('\n\n=== 3. ESTADO DE ALEMBIC ===\n')
out.append('--- Catalog Service ---')
out.append(run_cmd('docker-compose exec -T catalog-service alembic current'))

out.append('\n--- Auth Service ---')
out.append(run_cmd('docker-compose exec -T auth-service alembic current'))

with open('state_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
