from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app) # Crucial para evitar errores de bloqueo en el navegador

# Configuración de carpetas para Render
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

# --- RUTAS DE NAVEGACIÓN ---
@app.route('/')
def home():
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(BASE_PATH, path)

# --- RUTA DE AUTENTICACIÓN ---
@app.route('/auth', methods=['POST'])
def auth():
    datos = request.json
    email = datos.get('email')
    password = datos.get('password')
    nombre = datos.get('nombre')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if nombre:  # REGISTRO
        try:
            cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', 
                           (nombre, email, password))
            conn.commit()
            return jsonify({"status": "ok", "nombre": nombre}), 201
        except:
            return jsonify({"status": "error", "message": "El correo ya existe"}), 400
        finally:
            conn.close()
    else:  # LOGIN
        cursor.execute('SELECT nombre FROM usuarios WHERE email=? AND password=?', (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({"status": "ok", "nombre": user[0]}), 200
        return jsonify({"status": "error", "message": "Usuario o clave incorrectos"}), 401

# --- NUEVA RUTA: INSTALAR ---
@app.route('/instalar', methods=['POST'])
def instalar():
    datos = request.json
    juego = datos.get('juego')
    consola = datos.get('consola')
    # Aquí puedes agregar tu lógica de descarga
    return jsonify({"status": "ok", "message": f"Iniciando descarga de {juego} ({consola})"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)