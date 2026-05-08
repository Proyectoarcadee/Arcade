from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
import sqlite3
import os
import random

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DEL "CARTERO" (GMAIL) ---
# Aquí pones el correo desde donde saldrán todos los mensajes
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'proyectoarcade1.0@gmail.com' # TU CORREO EMISOR
app.config['MAIL_PASSWORD'] = 'bdanphhdurheyocs' # LAS 16 LETRAS SIN ESPACIOS
mail = Mail(app)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, 'arcadelocal', 'usuarios_arcade.db')

# Diccionario para guardar datos antes de que confirmen el correo
registros_pendientes = {}

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

@app.route('/arcadelocal/archivos_locales/<path:filename>')
def descargar_juego(filename):
    return send_from_directory(
        os.path.join(BASE_PATH, 'arcadelocal', 'archivos_locales'), 
        filename, 
        as_attachment=True
    )

# --- SISTEMA DE REGISTRO CON VERIFICACIÓN ---

@app.route('/solicitar-registro', methods=['POST'])
def solicitar_registro():
    datos = request.json
    email_usuario = datos.get('email') # El correo que el usuario escribió en la web
    nombre = datos.get('nombre')
    password = datos.get('password')
    
    codigo = str(random.randint(100000, 999999))
    
    # Guardamos los datos temporalmente
    registros_pendientes[email_usuario] = {
        "nombre": nombre,
        "password": password,
        "codigo": codigo
    }
    
    try:
        # El Cartero envía el mensaje al correo del usuario nuevo
        msg = Message('Verifica tu cuenta - Arcade',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email_usuario])
        msg.body = f"Hola {nombre}, tu código de verificación para Arcade es: {codigo}"
        mail.send(msg)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        # Si esto falla, devuelve error 500 (Casi siempre es por la contraseña de 16 letras)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/confirmar-registro', methods=['POST'])
def confirmar_registro():
    datos = request.json
    email = datos.get('email')
    codigo_usuario = datos.get('codigo')

    if email in registros_pendientes and registros_pendientes[email]['codigo'] == codigo_usuario:
        user_data = registros_pendientes[email]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', 
                           (user_data['nombre'], email, user_data['password']))
            conn.commit()
            del registros_pendientes[email]
            return jsonify({"status": "ok"}), 201
        except:
            return jsonify({"status": "error", "message": "Este correo ya está registrado"}), 400
        finally:
            conn.close()
    
    return jsonify({"status": "error", "message": "Código incorrecto"}), 401

# --- LOGIN DIRECTO ---

@app.route('/login-directo', methods=['POST'])
def login_directo():
    datos = request.json
    email = datos.get('email')
    password = datos.get('password')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT nombre FROM usuarios WHERE email=? AND password=?', (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "ok", "nombre": user[0]}), 200
    return jsonify({"status": "error", "message": "Correo o contraseña incorrectos"}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)