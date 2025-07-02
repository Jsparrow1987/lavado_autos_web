from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_muy_dificil_de_adivinar'
DATABASE = 'carwash.db'

# --- Conexión a la Base de Datos ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Decoradores de Autenticación ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'dueño':
            flash('Acceso denegado. Se requiere rol de "dueño".', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas Principales ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    conn = get_db_connection()
    total_clientes = conn.execute('SELECT COUNT(id) FROM clientes').fetchone()[0]
    total_ventas_hoy = conn.execute("SELECT COUNT(id) FROM ventas WHERE DATE(fecha) = CURRENT_DATE").fetchone()[0]
    ingresos_hoy = conn.execute("SELECT SUM(precio_final) FROM ventas WHERE DATE(fecha) = CURRENT_DATE").fetchone()[0] or 0
    conn.close()
    return render_template('dashboard.html', total_clientes=total_clientes, total_ventas_hoy=total_ventas_hoy, ingresos_hoy=ingresos_hoy)

# --- CLIENTES ---
@app.route('/clientes')
@login_required
def lista_clientes():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM clientes ORDER BY fecha_registro DESC').fetchall()
    conn.close()
    return render_template('lista_clientes.html', clientes=clientes)

@app.route('/clientes/registrar', methods=['GET', 'POST'])
@login_required
def registrar_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        telefono = request.form['telefono']
        placa = request.form['placa'].upper()
        marca_modelo = request.form['marca_modelo']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO clientes (nombre, dni, telefono, placa, marca_modelo) VALUES (?, ?, ?, ?, ?)',
                         (nombre, dni, telefono, placa, marca_modelo))
            conn.commit()
            flash('¡Cliente registrado exitosamente!', 'success')
            return redirect(url_for('lista_clientes'))
        except sqlite3.IntegrityError:
            flash('Error: La placa o el DNI ya existen en la base de datos.', 'danger')
        finally:
            conn.close()
    return render_template('registrar_cliente.html')

@app.route('/cliente/<int:id>')
@login_required
def perfil_cliente(id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()
    historial = conn.execute('''
        SELECT v.fecha, s.nombre, v.precio_final, u.username 
        FROM ventas v
        JOIN servicios s ON v.servicio_id = s.id
        JOIN usuarios u ON v.usuario_id = u.id
        WHERE v.cliente_id = ? ORDER BY v.fecha DESC
    ''', (id,)).fetchall()
    conn.close()
    if cliente is None:
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('lista_clientes'))
    return render_template('perfil_cliente.html', cliente=cliente, historial=historial)

# --- SERVICIOS ---
@app.route('/servicios')
@login_required
def lista_servicios():
    conn = get_db_connection()
    servicios = conn.execute('SELECT * FROM servicios ORDER BY precio').fetchall()
    conn.close()
    return render_template('lista_servicios.html', servicios=servicios)

# --- USUARIOS (Solo para el dueño) ---
@app.route('/usuarios')
@login_required
@owner_required
def lista_usuarios():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT id, username, role FROM usuarios').fetchall()
    conn.close()
    return render_template('lista_usuarios.html', usuarios=usuarios)

@app.route('/usuarios/registrar', methods=['GET', 'POST'])
@login_required
@owner_required
def registrar_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        if not password:
            flash('La contraseña no puede estar vacía.', 'danger')
            return redirect(url_for('registrar_usuario'))

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)',
                         (username, generate_password_hash(password), role))
            conn.commit()
            flash('Usuario registrado exitosamente.', 'success')
            return redirect(url_for('lista_usuarios'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe.', 'danger')
        finally:
            conn.close()
            
    return render_template('registrar_usuario.html')

# --- VENTAS ---
@app.route('/ventas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    conn = get_db_connection()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        servicio_id = request.form['servicio_id']
        precio_final = request.form['precio_final']
        metodo_pago = request.form['metodo_pago']
        observaciones = request.form['observaciones']
        usuario_id = session['user_id']
        
        # Insertar la venta
        conn.execute('''
            INSERT INTO ventas (cliente_id, servicio_id, usuario_id, precio_final, metodo_pago, observaciones) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cliente_id, servicio_id, usuario_id, precio_final, metodo_pago, observaciones))
        
        # Añadir un punto de lealtad al cliente
        conn.execute('UPDATE clientes SET puntos = puntos + 1 WHERE id = ?', (cliente_id,))
        
        conn.commit()
        conn.close()
        
        flash('Venta registrada y punto de lealtad añadido exitosamente!', 'success')
        return redirect(url_for('perfil_cliente', id=cliente_id))

    # Lógica para el GET
    clientes = conn.execute('SELECT id, nombre, placa FROM clientes ORDER BY nombre').fetchall()
    servicios = conn.execute('SELECT id, nombre, precio FROM servicios ORDER BY nombre').fetchall()
    conn.close()
    return render_template('nueva_venta.html', clientes=clientes, servicios=servicios)

# Pega este nuevo bloque de código en tu archivo app.py
@app.route('/ventas')
@login_required
def lista_ventas():
    conn = get_db_connection()
    ventas = conn.execute('''
        SELECT 
            v.id,
            v.fecha,
            c.id AS cliente_id,
            c.nombre AS cliente_nombre,
            s.nombre AS servicio_nombre,
            u.username AS usuario_nombre,
            v.precio_final
        FROM ventas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN servicios s ON v.servicio_id = s.id
        JOIN usuarios u ON v.usuario_id = u.id
        ORDER BY v.fecha DESC
    ''').fetchall()
    conn.close()
    return render_template('lista_ventas.html', ventas=ventas)

if __name__ == '__main__':
    app.run(debug=True)