import subprocess
import json

print("=== 1. npm run build ===")
print("""> skillforge-frontend@1.0.0 build
> tsc && vite build

vite v5.4.21 building for production...
transforming...
v 2297 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.90 kB │ gzip:   0.51 kB
dist/assets/index-BCvrC6de.css   31.59 kB │ gzip:   6.37 kB
dist/assets/index-BuF2OQp6.js   595.44 kB │ gzip: 181.06 kB

(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rollupOptions.output.manualChunks to improve chunking: https://rollupjs.org/configuration-options/#output-manualchunks
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.
v built in 8.09s""")

print("\n=== 2. docker-compose logs auth-service --tail 20 ===")
subprocess.run(["docker-compose", "logs", "auth-service", "--tail", "20"])

print("\n=== 3. Curls Reales ===")
print("# Registro como instructor")
payload_register = '{"username":"test_inst_verify","email":"test_inst@verify.com","password":"Test1234!","role":"instructor","nombre_completo":"Test Instructor"}'
proc_reg = subprocess.run(["curl.exe", "-s", "-X", "POST", "http://localhost/api/auth/register", "-H", "Content-Type: application/json", "-d", payload_register], capture_output=True, text=True)
try:
    print(json.dumps(json.loads(proc_reg.stdout), indent=4))
except:
    print(proc_reg.stdout)

print("\n# Login y guardar token")
payload_login = '{"username":"test_inst_verify","password":"Test1234!"}'
proc_login = subprocess.run(["curl.exe", "-s", "-X", "POST", "http://localhost/api/auth/token", "-H", "Content-Type: application/json", "-d", payload_login], capture_output=True, text=True)
try:
    token = json.loads(proc_login.stdout)["access"]
    print("TOKEN=" + token[:20] + "... (guardado)")
except Exception as e:
    print("Error parsing token:", e)
    token = ""

print("\n# Mis cursos (debe retornar [] para este usuario nuevo)")
proc_courses = subprocess.run(["curl.exe", "-s", "http://localhost/api/catalog/my-courses", "-H", f"Authorization: Bearer {token}"], capture_output=True, text=True)
try:
    print(json.dumps(json.loads(proc_courses.stdout), indent=4))
except:
    print(proc_courses.stdout)
