import sqlite3

DATABASE = 'carwash.db'

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Crear tabla usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('empleado', 'dueño'))
)
''')

# Crear tabla clientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dni TEXT UNIQUE NOT NULL,
    telefono TEXT,
    placa TEXT UNIQUE NOT NULL,
    marca_modelo TEXT,
    puntos INTEGER DEFAULT 0,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Crear tabla servicios
cursor.execute('''
CREATE TABLE IF NOT EXISTS servicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL
)
''')

# Crear tabla ventas
cursor.execute('''
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    servicio_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    precio_final REAL NOT NULL,
    metodo_pago TEXT,
    observaciones TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (servicio_id) REFERENCES servicios(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
''')

conn.commit()
conn.close()
print("Base de datos inicializada con éxito ✅")
print("Tablas creadas: usuarios, clientes, servicios, ventas")
print("Recuerda agregar usuarios y servicios antes de iniciar la aplicación.")
print("Para agregar usuarios, usa el script 'add_users.py'.")
print("Para agregar servicios, usa el script 'add_services.py'.")   

print("¡Listo para usar la aplicación de lavado de autos! 🚗💦")
print("Inicia la aplicación con 'python app.py' y disfruta de la gestión de tu negocio.")
print("Si tienes alguna duda, revisa la documentación o contacta al soporte técnico.")  
print("¡Gracias por usar nuestra aplicación! Tu negocio de lavado de autos está a un paso de ser más eficiente y organizado. 🚀"            )
