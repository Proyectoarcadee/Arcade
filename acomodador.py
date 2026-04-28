from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app) # Esto es vital para que el frontend pueda conectarse

# Configuramos las rutas para que funcionen en la nube
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
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

init_db()

# --- RUTAS PARA MOSTRAR TU PÁGINA ---
@app.route('/')
def index():
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(BASE_PATH, path)

# --- RUTA DE LOGIN/REGISTRO ---
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
            return jsonify({"status": "registro", "nombre": nombre}), 201
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "Email ya registrado"}), 400
        finally:
            conn.close()
    else:  # LOGIN
        cursor.execute('SELECT nombre FROM usuarios WHERE email = ? AND password = ?', 
                       (email, password))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            return jsonify({"status": "login", "nombre": usuario[0]}), 200
        else:
            return jsonify({"status": "error", "message": "Datos incorrectos"}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)