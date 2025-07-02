import sqlite3

DATABASE = 'carwash.db'

servicios = [
    ("Lavado rápido", "Lavado exterior rápido", 15.0),
    ("Lavado completo", "Lavado exterior e interior", 25.0),
    ("Lavado premium", "Lavado completo + encerado", 35.0),
    ("Lavado de motor", "Limpieza detallada del motor", 40.0),
    ("Aspirado interior", "Aspirado de alfombras y asientos", 10.0),
    ("Encerado", "Encerado con cera de alta calidad", 20.0),
    ("Desinfección", "Desinfección interior con ozono", 30.0)
]

def agregar_servicios():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    insertados = 0

    for nombre, descripcion, precio in servicios:
        try:
            cursor.execute('''
                INSERT INTO servicios (nombre, descripcion, precio)
                VALUES (?, ?, ?)
            ''', (nombre, descripcion, precio))
            insertados += 1
        except sqlite3.IntegrityError:
            print(f"⚠️  El servicio '{nombre}' ya existe. Saltando.")
            continue

    conn.commit()
    conn.close()
    print(f"✅ Servicios cargados: {insertados}/{len(servicios)}")

if __name__ == '__main__':
    agregar_servicios()
