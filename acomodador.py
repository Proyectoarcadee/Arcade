from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Configuración de rutas
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, 'arcadelocal', 'usuarios_arcade.db')

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

# --- RUTAS DE NAVEGACIÓN (Se ven en el navegador) ---

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

# --- RUTA DE DESCARGAS (Solo descarga juegos de la subcarpeta) ---

@app.route('/arcadelocal/archivos_locales/<path:filename>')
def descargar_juego(filename):
    # as_attachment=True fuerza la descarga en lugar de abrir el archivo
    return send_from_directory(
        os.path.join(BASE_PATH, 'arcadelocal', 'archivos_locales'), 
        filename, 
        as_attachment=True
    )

# --- AUTENTICACIÓN ---

@app.route('/auth', methods=['POST'])
def auth():
    datos = request.json
    email = datos.get('email')
    password = datos.get('password')
    nombre = datos.get('nombre')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if nombre:  # Proceso de Registro
        try:
            cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', 
                           (nombre, email, password))
            conn.commit()
            return jsonify({"status": "ok", "nombre": nombre}), 201
        except:
            return jsonify({"status": "error", "message": "El correo ya existe"}), 400
        finally:
            conn.close()
    else:  # Proceso de Login
        cursor.execute('SELECT nombre FROM usuarios WHERE email=? AND password=?', (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({"status": "ok", "nombre": user[0]}), 200
        return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)