import requests
import json
import uuid
import time

BASE_URL = "http://localhost:80/api"

# Wait a few seconds for services to become completely healthy behind nginx
time.sleep(3)

# 1. Register a new instructor
username = f"instructor_{uuid.uuid4().hex[:6]}"
payload = {
    "username": username,
    "email": f"{username}@test.com",
    "password": "Password123!",
    "role": "instructor",
    "nombre_completo": "Test Instructor",
    "ciudad": "Bogotá"
}

print("=== CHECK 1: Register Instructor ===")
r_reg = requests.post(f"{BASE_URL}/auth/register", json=payload)
print("Status:", r_reg.status_code)
try:
    print("Response:", json.dumps(r_reg.json(), indent=2))
except:
    print("Response text:", r_reg.text)

# 2. Get Users as Admin (using default admin credentials from seed)
print("\n=== CHECK 2: List Users as Admin ===")
r_admin_login = requests.post(f"{BASE_URL}/auth/token", json={"username": "admin", "password": "admin"})
if r_admin_login.status_code == 200:
    admin_token = r_admin_login.json()["access"]
    r_users = requests.get(f"{BASE_URL}/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
    print("Status:", r_users.status_code)
    try:
        users_data = r_users.json()
        print(f"Users count: {len(users_data)}")
        # Print the newly registered user and the admin to verify output
        print("First 2 users returned:", json.dumps(users_data[:2], indent=2))
    except:
        print("Response text:", r_users.text)
else:
    print("Failed to login as admin:", r_admin_login.text)

# 3. Get my-courses as the instructor
print("\n=== CHECK 3: Get My Courses as Instructor ===")
r_inst_login = requests.post(f"{BASE_URL}/auth/token", json={"username": username, "password": "Password123!"})
if r_inst_login.status_code == 200:
    inst_token = r_inst_login.json()["access"]
    # Testing the /my-courses endpoint that we created
    r_courses = requests.get(f"{BASE_URL}/catalog/my-courses", headers={"Authorization": f"Bearer {inst_token}"})
    print("Status:", r_courses.status_code)
    try:
        print("Response:", json.dumps(r_courses.json(), indent=2))
    except:
        print("Response text:", r_courses.text)
else:
    print("Failed to login as instructor:", r_inst_login.text)
