import json
import os
import bcrypt

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

def add_user(username, email, password):
    users = load_users()
    if email in users:
        return False  # Usuario ya existe

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users[email] = {
        'email': email,
        'password': hashed_password.decode('utf-8')
    }
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def validate_user(username, password):
    users = load_users()
    if username not in users:
        return False

    hashed_password = users[username]['password']
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
