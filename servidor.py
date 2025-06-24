from flask import Flask, request, jsonify, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Clave secreta para las sesiones

# Configuración de la base de datos
DATABASE = 'tareas.db'


def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla de tareas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            completada BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

    conn.commit()
    conn.close()


def get_db_connection():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def verificar_usuario_existe(usuario):
    """Verifica si un usuario ya existe en la base de datos"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT id FROM usuarios WHERE usuario = ?', (usuario,)).fetchone()
    conn.close()
    return user is not None


def obtener_usuario_por_credenciales(usuario, password):
    """Obtiene usuario si las credenciales son correctas"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM usuarios WHERE usuario = ?', (usuario,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None


@app.route('/')
def home():
    """Página de inicio"""
    html_template = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Gestión de Tareas</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .endpoint { background: #e8f4fd; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2196F3; }
            .method { font-weight: bold; color: #2196F3; }
            code { background: #f1f1f1; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1> Sistema de Gestión de Tareas</h1>
            <p>API REST para gestión de usuarios y tareas con autenticación segura.</p>
            
            <h2> Endpoints Disponibles:</h2>
            
            <div class="endpoint">
                <div class="method">POST /registro</div>
                <p><strong>Descripción:</strong> Registra un nuevo usuario en el sistema</p>
                <p><strong>Cuerpo:</strong> <code>{"usuario": "nombre", "contraseña": "1234"}</code></p>
                <p><strong>Respuesta exitosa:</strong> <code>{"mensaje": "Usuario registrado exitosamente", "usuario": "nombre"}</code></p>
            </div>
            
            <div class="endpoint">
                <div class="method">POST /login</div>
                <p><strong>Descripción:</strong> Inicia sesión con credenciales de usuario</p>
                <p><strong>Cuerpo:</strong> <code>{"usuario": "nombre", "contraseña": "1234"}</code></p>
                <p><strong>Respuesta exitosa:</strong> <code>{"mensaje": "Inicio de sesión exitoso", "usuario": "nombre"}</code></p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET /tareas</div>
                <p><strong>Descripción:</strong> Muestra página de bienvenida para usuarios autenticados</p>
                <p><strong>Requiere:</strong> Sesión activa (haber hecho login previamente)</p>
            </div>
            
            <div class="endpoint">
                <div class="method">POST /logout</div>
                <p><strong>Descripción:</strong> Cierra la sesión del usuario actual</p>
            </div>
            
            <h2> Cómo probar la API:</h2>
            
            <h3>Colección de Postman Incluida:</h3>
            <p>El proyecto incluye una <strong>colección completa de Postman</strong> con todos los endpoints preconfigurados:</p>
            <ul>
                <li> <strong>Archivo:</strong> <code>coleccion-postman.json</code></li>
                <li> <strong>Tests automatizados</strong> para cada endpoint</li>
                <li> <strong>Variables automáticas</strong> (usuario único, gestión de cookies)</li>
                <li> <strong>Ejemplos de respuesta</strong> para éxito y errores</li>
            </ul>
            
            <p><strong>Para usar:</strong></p>
            <ol>
                <li>Importar el archivo JSON en Postman</li>
                <li>Ejecutar las peticiones en orden secuencial</li>
                <li>Las cookies y variables se manejan automáticamente</li>
            </ol>
            
            <h3>Herramientas Alternativas:</h3>
            <p>También se puede usar <strong>curl</strong>, <strong>Thunder Client</strong> o <strong>Insomnia</strong>:</p>
            
            <h3>Ejemplo con curl:</h3>
            <code>curl -X POST http://localhost:5000/registro -H "Content-Type: application/json" -d '{"usuario":"test", "contraseña":"1234"}'</code>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_template)


@app.route('/registro', methods=['POST'])
def registro():
    """Endpoint para registrar nuevos usuarios"""
    try:
        data = request.get_json()

        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({
                'error': 'Datos incompletos',
                'mensaje': 'Se requieren los campos: usuario y contraseña'
            }), 400

        usuario = data['usuario'].strip()
        password = data['contraseña']

        # Validaciones básicas
        if len(usuario) < 3:
            return jsonify({
                'error': 'Usuario inválido',
                'mensaje': 'El nombre de usuario debe tener al menos 3 caracteres'
            }), 400

        if len(password) < 4:
            return jsonify({
                'error': 'Contraseña inválida',
                'mensaje': 'La contraseña debe tener al menos 4 caracteres'
            }), 400

        # Verificar si el usuario ya existe
        if verificar_usuario_existe(usuario):
            return jsonify({
                'error': 'Usuario existente',
                'mensaje': f'El usuario "{usuario}" ya está registrado'
            }), 409

        # Hashear la contraseña
        password_hash = generate_password_hash(password)

        # Insertar en la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)',
            (usuario, password_hash)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'mensaje': 'Usuario registrado exitosamente',
            'usuario': usuario,
            'fecha_registro': datetime.now().isoformat()
        }), 201

    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'mensaje': str(e)
        }), 500


@app.route('/login', methods=['POST'])
def login():
    """Endpoint para iniciar sesión"""
    try:
        data = request.get_json()

        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({
                'error': 'Datos incompletos',
                'mensaje': 'Se requieren los campos: usuario y contraseña'
            }), 400

        usuario = data['usuario'].strip()
        password = data['contraseña']

        # Verificar credenciales
        user_data = obtener_usuario_por_credenciales(usuario, password)

        if not user_data:
            return jsonify({
                'error': 'Credenciales inválidas',
                'mensaje': 'Usuario o contraseña incorrectos'
            }), 401

        # Crear sesión
        session['user_id'] = user_data['id']
        session['usuario'] = user_data['usuario']

        return jsonify({
            'mensaje': 'Inicio de sesión exitoso',
            'usuario': user_data['usuario'],
            'fecha_login': datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'mensaje': str(e)
        }), 500


@app.route('/tareas', methods=['GET'])
def tareas():
    """Endpoint para mostrar tareas (requiere autenticación)"""
    if 'user_id' not in session:
        return jsonify({
            'error': 'No autorizado',
            'mensaje': 'Debe iniciar sesión para acceder a las tareas'
        }), 401

    html_bienvenida = '''
<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mis Tareas</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .welcome {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .user-info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 25px;
        }

        .feature {
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            border-left: 5px solid #007bff;
        }

        .btn {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }

        .btn:hover {
            background: #0056b3;
        }

        .logout-btn {
            background: #dc3545;
        }

        .logout-btn:hover {
            background: #c82333;
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <h1 class="welcome">🎉 ¡Bienvenido!</h1>
            <div class="user-info">
                <h3>👤 Usuario: testuser_1750732468</h3>
                <p>Iniciaste sesión exitosamente en el Sistema de Gestión de Tareas</p>
            </div>
        </div>

        <div class="feature">
            <h3>Gestión de Tareas</h3>
            <p>Desde acá podrás administrar todas tus tareas de manera eficiente. El sistema te permite crear, editar,
                completar y eliminar tareas.</p>
        </div>

        <div class="feature">
            <h3> Sesión Segura</h3>
            <p>Tu sesión está protegida con autenticación segura. Todas las contraseñas están hasheadas y tus datos
                están almacenados de forma segura en SQLite.</p>
        </div>

        <div class="feature">
            <h3>Probar con Postman</h3>
            <p><strong>Colección incluida:</strong> <code>Sistema-Gestion-Tareas.postman_collection.json</code></p>
            <ol>
                <li> Importar la colección en Postman</li>
                <li> Asegurar que el servidor esté ejecutándose</li>
                <li> Ejecutar peticiones en orden secuencial</li>
                <li> Las cookies se manejan automáticamente</li>
            </ol>
            <p><strong>Orden recomendado:</strong> Registro → Login → Tareas → Logout</p>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <button class="btn logout-btn" onclick="cerrarSesion()">🚪 Cerrar Sesión</button>
        </div>
    </div>

    <script>
        function cerrarSesion() {
                fetch('/logout', { method: 'POST' })
                .then(() => {
                    alert('Sesión cerrada exitosamente');
                    window.location.href = '/';
                })
                .catch(err => {
                    console.error('Error al cerrar sesión:', err);
                });
            }
    </script>
</body>

</html>
    '''

    return render_template_string(html_bienvenida, usuario=session['usuario'])


@app.route('/logout', methods=['POST'])
def logout():
    """Endpoint para cerrar sesión"""
    session.clear()
    return jsonify({
        'mensaje': 'Sesión cerrada exitosamente'
    }), 200


@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Endpoint para listar usuarios registrados (para debugging)"""
    try:
        conn = get_db_connection()
        usuarios = conn.execute(
            'SELECT id, usuario, fecha_registro FROM usuarios ORDER BY fecha_registro DESC').fetchall()
        conn.close()

        usuarios_list = []
        for user in usuarios:
            usuarios_list.append({
                'id': user['id'],
                'usuario': user['usuario'],
                'fecha_registro': user['fecha_registro']
            })

        return jsonify({
            'usuarios': usuarios_list,
            'total': len(usuarios_list)
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'mensaje': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint no encontrado',
        'mensaje': 'La ruta solicitada no existe'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Método no permitido',
        'mensaje': 'El método HTTP no está permitido para esta ruta'
    }), 405


if __name__ == '__main__':
    # Inicializar base de datos
    init_db()
    print("🚀 Iniciando servidor Flask...")
    print("📍 Servidor disponible en: http://localhost:5000")
    print("📋 Base de datos SQLite inicializada")

    # Ejecutar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)
