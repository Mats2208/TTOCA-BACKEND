import json
import os
import bcrypt
import uuid

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def add_user(username, email, password):
    users = load_users()
    if email in users:
        return False  # Usuario ya existe

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users[email] = {
        'email': email,
        'password': hashed_password.decode('utf-8')
    }
    save_users(users)
    return True

def validate_user(email, password):
    users = load_users()
    if email not in users:
        return False

    hashed_password = users[email]['password']
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user_projects(email):
    users = load_users()
    user = users.get(email)
    if not user:
        return None
    return user.get("empresas", [])

def get_user_project_by_id(email, proyecto_id):
    users = load_users()
    user = users.get(email)
    if not user or "empresas" not in user:
        return None
    for proyecto in user["empresas"]:
        if proyecto["id"] == proyecto_id:
            return proyecto
    return None

def add_user_project(email, proyecto_data):
    users = load_users()
    if email not in users:
        return False, "Usuario no existe en la base de datos"

    nueva_empresa = {
        "id": str(uuid.uuid4())[:8],
        "nombre": proyecto_data.get("nombre"),
        "logo": proyecto_data.get("logo", ""),
        "titular": proyecto_data.get("titular", ""),
        "config": proyecto_data.get("config", {})
    }

    if "empresas" not in users[email]:
        users[email]["empresas"] = []

    users[email]["empresas"].append(nueva_empresa)
    save_users(users)
    return True, nueva_empresa
