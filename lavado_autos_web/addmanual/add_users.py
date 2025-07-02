import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'carwash.db'

def agregar_usuario(username, password, role):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO usuarios (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', (username, generate_password_hash(password), role))
        conn.commit()
        print(f"✅ Usuario '{username}' con rol '{role}' creado correctamente.")
    except sqlite3.IntegrityError:
        print(f"❌ El nombre de usuario '{username}' ya existe.")
    finally:
        conn.close()

if __name__ == '__main__':
    print("📋 Crear nuevo usuario")
    username = input("👤 Nombre de usuario: ").strip()
    password = input("🔒 Contraseña: ").strip()
    role = input("🧑‍💼 Rol ('dueño' o 'empleado'): ").strip().lower()

    if role not in ['dueño', 'empleado']:
        print("❌ Rol inválido. Usa 'dueño' o 'empleado'.")
    elif not username or not password:
        print("❌ Usuario o contraseña no pueden estar vacíos.")
    else:
        agregar_usuario(username, password, role)
# This script allows you to add users to the car wash database.
# It prompts for a username, password, and role, then inserts the user into the database.
# Make sure to run this script after initializing the database with init_db.py.     
# You can run this script multiple times to add more users.
# Ensure you have the necessary permissions to create users in the database.                
# Remember to use strong passwords and unique usernames for security.

    
