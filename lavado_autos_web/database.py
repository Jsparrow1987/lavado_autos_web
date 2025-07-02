import os
# Eliminar la base de datos anterior si existe
if os.path.exists('carwash.db'):
    os.remove('carwash.db')
    print("🗑️ Base de datos anterior eliminada.")
print("🆕 Creando nueva base de datos...")

import sqlite3
from werkzeug.security import generate_password_hash

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect('carwash.db')
cursor = conn.cursor()

print("Inicializando base de datos...")
print("Creando tablas...")

# --- Crear Tablas ---

# Tabla de Usuarios (para dueños y empleados)
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('dueño', 'empleado'))
)
''')

# Tabla de Clientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dni TEXT UNIQUE,
    telefono TEXT,
    placa TEXT UNIQUE NOT NULL,
    marca_modelo TEXT,
    categoria TEXT DEFAULT 'Nuevo', -- Nuevo, Frecuente, Inactivo
    puntos INTEGER DEFAULT 0,
    fecha_nacimiento DATE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Tabla de Servicios (con los datos que proporcionaste)
cursor.execute('''
CREATE TABLE IF NOT EXISTS servicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL
)
''')

# Tabla de Ventas (registra cada servicio hecho a un cliente)
cursor.execute('''
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    servicio_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    precio_final REAL NOT NULL,
    metodo_pago TEXT, -- Efectivo, Transferencia, etc.
    hora_entrada TIMESTAMP,
    hora_salida TIMESTAMP,
    foto_path TEXT,
    observaciones TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (servicio_id) REFERENCES servicios(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
''')


print("Tablas creadas exitosamente.")

# --- Insertar Datos Iniciales ---

print("Insertando datos iniciales...")

# Insertar un usuario "dueño" por defecto
try:
    cursor.execute("INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                   ('dueño', generate_password_hash('admin123'), 'dueño'))
    print("- Usuario 'dueño' creado. Contraseña: 'admin123'")
except sqlite3.IntegrityError:
    print("- El usuario 'dueño' ya existe.")

# Insertar los servicios que definiste
servicios_iniciales = [
    ('Lavado Exterior', 'Elimina suciedad, polvo y residuos del exterior. Se utiliza agua a presión, champú especial y productos de limpieza.', 25.00),
    ('Lavado Interior', 'Limpieza de asientos, alfombras, paneles y tablero. Se utilizan aspiradoras y productos específicos.', 30.00),
    ('Pulido y Encerado', 'Mejora el brillo y protege la pintura. Elimina pequeños arañazos y añade una capa protectora.', 80.00),
    ('Limpieza de Llantas y Neumáticos', 'Elimina suciedad, barro y residuos de la carretera de llantas y neumáticos.', 15.00),
    ('Limpieza de Motor', 'Limpia el motor y sus componentes de grasa, aceite y suciedad acumulada.', 50.00),
    ('Detallado Completo', 'Limpieza minuciosa y profunda tanto del interior como del exterior del auto.', 150.00)
]

try:
    cursor.executemany("INSERT INTO servicios (nombre, descripcion, precio) VALUES (?, ?, ?)", servicios_iniciales)
    print("- Servicios iniciales insertados.")
except sqlite3.IntegrityError:
    print("- Los servicios ya han sido insertados previamente.")


# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("\n¡Base de datos inicializada correctamente!")