from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import shutil

app = Flask(__name__)
CORS(app)

# Configuración de rutas relativas al archivo
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, 'usuarios_arcade.db')

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

@app.route('/auth', methods=['POST'])
def auth():
    datos = request.json
    email = datos.get('email')
    password = datos.get('password')
    nombre = datos.get('nombre')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if nombre: # Lógica de Registro
        try:
            cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', 
                           (nombre, email, password))
            conn.commit()
            return jsonify({"status": "registro", "nombre": nombre}), 201
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "El correo ya está registrado"}), 400
        finally:
            conn.close()

    # Lógica de Login
    cursor.execute('SELECT nombre FROM usuarios WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"status": "login", "nombre": user[0]}), 200
    return jsonify({"status": "error", "message": "Datos incorrectos"}), 404

@app.route('/instalar', methods=['POST'])
def instalar():
    datos = request.json
    juego_url = datos.get('juego')
    consola = datos.get('consola')

    # Mapeo de carpetas personalizadas
    if consola == 'gamecube':
        folder = 'cube'
    elif consola == 'n64':
        folder = '64'
    else:
        folder = consola

    nombre_archivo = juego_url.split('/')[-1]
    
    # Rutas de carpetas
    bodega = os.path.join(BASE_PATH, 'archivos_locales')
    destino_dir = os.path.join(BASE_PATH, 'roms', folder)
    
    if not os.path.exists(destino_dir):
        os.makedirs(destino_dir)
    
    origen = os.path.join(bodega, nombre_archivo)
    destino_final = os.path.join(destino_dir, nombre_archivo)

    if os.path.exists(origen):
        try:
            shutil.copy(origen, destino_final)
            return jsonify({"status": "success", "message": f"Instalado en roms/{folder}"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "error", "message": f"No se encontró {nombre_archivo} en archivos_locales"}), 404

if __name__ == '__main__':
    # Puerto 5000 para Flask
    app.run(port=5000, debug=True)