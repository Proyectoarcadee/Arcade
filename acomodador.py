from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE RUTAS ---
# BASE_PATH detecta la carpeta raíz donde está este archivo
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Ruta a la base de datos dentro de arcadelocal
# Importante: Asegúrate de que el nombre del archivo coincida con el tuyo
DB_PATH = os.path.join(BASE_PATH, 'arcadelocal', 'usuarios_arcade.db')

def init_db():
    # Creamos la carpeta si no existe, aunque ya la tengas
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
        
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

# Inicializar la base de datos al arrancar el servidor
init_db()

# --- RUTAS PARA SERVIR EL FRONTEND (Solución al "Not Found") ---

@app.route('/')
def index():
    # Esto envía el archivo index.html que está en tu raíz
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    # Esto permite que se carguen datos.js, imágenes y el login.html
    return send_from_directory(BASE_PATH, path)

# --- RUTA DE AUTENTICACIÓN (LOGIN Y REGISTRO) ---

@app.route('/auth', methods=['POST'])
def auth():
    datos = request.json
    email = datos.get('email')
    password = datos.get('password')
    nombre = datos.get('nombre') # Solo viene en el registro

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if nombre:  # Lógica de REGISTRO
        try:
            cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', 
                           (nombre, email, password))
            conn.commit()
            return jsonify({"status": "registro", "nombre": nombre}), 201
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "El correo ya está registrado"}), 400
        finally:
            conn.close()
    else:  # Lógica de LOGIN
        cursor.execute('SELECT nombre FROM usuarios WHERE email = ? AND password = ?', 
                       (email, password))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            return jsonify({"status": "login", "nombre": usuario[0]}), 200
        else:
            return jsonify({"status": "error", "message": "Credenciales incorrectas"}), 401

if __name__ == '__main__':
    # Render asigna dinámicamente un puerto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)