from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
import sqlite3
import os
import random

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE GMAIL ---
# Reemplaza con tus datos y las 16 letras que generaste
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'proyectoarcade1.0@gmail.com' 
app.config['MAIL_PASSWORD'] = 'bdanphhdurheyocs' 
mail = Mail(app)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, 'arcadelocal', 'usuarios_arcade.db')

# Diccionario temporal para códigos OTP (Email: Código)
codigos_activos = {}

def init_db():
    if not os.path.exists(os.path.join(BASE_PATH, 'arcadelocal')):
        os.makedirs(os.path.join(BASE_PATH, 'arcadelocal'))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- RUTAS DE NAVEGACIÓN ---
@app.route('/')
@app.route('/index.html')
def home():
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/login.html')
def login_page():
    return send_from_directory(BASE_PATH, 'login.html')

@app.route('/datos.js')
def datos_js():
    return send_from_directory(BASE_PATH, 'datos.js')

@app.route('/imagenes/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(BASE_PATH, 'imagenes'), filename)

# --- RUTA DE DESCARGAS ---
@app.route('/arcadelocal/archivos_locales/<path:filename>')
def descargar_juego(filename):
    return send_from_directory(
        os.path.join(BASE_PATH, 'arcadelocal', 'archivos_locales'), 
        filename, 
        as_attachment=True
    )

# --- SISTEMA DE VALIDACIÓN GMAIL (OTP) ---
@app.route('/enviar-otp', methods=['POST'])
def enviar_otp():
    email = request.json.get('email')
    codigo = str(random.randint(100000, 999999))
    codigos_activos[email] = codigo
    
    try:
        msg = Message('Código de Acceso - Arcade UTN',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"Tu código de acceso para el sistema es: {codigo}"
        mail.send(msg)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- REGISTRO Y LOGIN ---
@app.route('/auth', methods=['POST'])
def auth():
    datos = request.json
    email = datos.get('email')
    password = datos.get('password')
    nombre = datos.get('nombre')
    codigo_otp = datos.get('codigo') # El código que llegó al correo

    # Validar el código primero
    if email not in codigos_activos or codigos_activos[email] != codigo_otp:
        return jsonify({"status": "error", "message": "Código incorrecto"}), 401

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if nombre: # Registro
        try:
            cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', 
                           (nombre, email, password))
            conn.commit()
            del codigos_activos[email]
            return jsonify({"status": "ok", "nombre": nombre}), 201
        except:
            return jsonify({"status": "error", "message": "Email ya existe"}), 400
    else: # Login
        cursor.execute('SELECT nombre FROM usuarios WHERE email=? AND password=?', (email, password))
        user = cursor.fetchone()
        if user:
            del codigos_activos[email]
            return jsonify({"status": "ok", "nombre": user[0]}), 200
        return jsonify({"status": "error", "message": "Clave incorrecta"}), 401

# --- RECUPERACIÓN DE CONTRASEÑA ---
@app.route('/cambiar-password', methods=['POST'])
def cambiar_password():
    datos = request.json
    email = datos.get('email')
    codigo = datos.get('codigo')
    nueva_password = datos.get('nueva_password')

    if email in codigos_activos and codigos_activos[email] == codigo:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET password=? WHERE email=?', (nueva_password, email))
        conn.commit()
        conn.close()
        del codigos_activos[email]
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)