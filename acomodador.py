from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE RUTAS ---
# Obtenemos la ruta de la carpeta donde está este archivo
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Ruta a la base de datos dentro de arcadelocal
# Asegúrate de que el nombre del archivo sea exactamente 'usuarios_arcade.db' 
# o cámbialo aquí abajo si tiene otro nombre.
DB_PATH = os.path.join(BASE_PATH, 'arcadelocal', 'usuarios_arcade.db')

def init_db():
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

# Inicializar base de datos al arrancar
init_db()

# --- RUTAS DE LA PÁGINA ---

# Esta ruta es VITAL para que no te salga el error "Not Found" al entrar al link
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Por si tus archivos CSS/JS necesitan cargarse manualmente
@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

# --- RUTA DE AUTENTICACIÓN / REGISTRO ---
@app.route('/auth', methods=['POST'])
def auth():
    datos = request.json
    email = datos.get('email')
    password = datos.get('password')
    nombre = datos.get('nombre')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if nombre:  # Lógica de Registro
        try:
            cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', 
                           (nombre, email, password))
            conn.commit()
            return jsonify({"status": "registro", "nombre": nombre}), 201
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "El correo ya está registrado"}), 400
        finally:
            conn.close()
    else:  # Lógica de Login
        cursor.execute('SELECT nombre FROM usuarios WHERE email = ? AND password = ?', 
                       (email, password))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            return jsonify({"status": "login", "nombre": usuario[0]}), 200
        else:
            return jsonify({"status": "error", "message": "Credenciales incorrectas"}), 401

if __name__ == '__main__':
    # Usar el puerto que asigne Render o el 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)