#!/usr/bin/env python3
"""
Script de pruebas automatizadas para el Sistema de Gestión de Tareas
Ejecutar con: python test_api.py
"""

import requests
import time
import sys

# Configuración
BASE_URL = "http://localhost:5000"
TEST_USER = "testuser_" + str(int(time.time()))  # Usuario único
TEST_PASSWORD = "test1234"

class Colors:
    """Códigos ANSI para colores en terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}")
    print(f"🧪 {message}")
    print(f"{'='*50}{Colors.END}")

def test_server_running():
    """Verifica que el servidor esté ejecutándose"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_success("Servidor Flask está ejecutándose")
            return True
        else:
            print_error(f"Servidor responde con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("No se puede conectar al servidor. ¿Está ejecutándose?")
        print_info("Ejecutar: python servidor.py")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return False

def test_registration():
    """Prueba el registro de usuario"""
    print_header("PRUEBA: Registro de Usuario")
    
    # Datos de prueba
    user_data = {
        "usuario": TEST_USER,
        "contraseña": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/registro",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print_info(f"POST /registro - Código: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Usuario registrado exitosamente")
            print_info(f"Usuario: {data.get('usuario')}")
            print_info(f"Fecha registro: {data.get('fecha_registro')}")
            return True
        else:
            print_error("Error en registro")
            print_error(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error en registro: {e}")
        return False

def test_duplicate_registration():
    """Prueba registro duplicado (debe fallar)"""
    print_header("PRUEBA: Registro Duplicado (debe fallar)")
    
    user_data = {
        "usuario": TEST_USER,
        "contraseña": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/registro",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print_info(f"POST /registro - Código: {response.status_code}")
        
        if response.status_code == 409:
            print_success("Error 409 correcto - Usuario ya existe")
            return True
        else:
            print_warning(f"Se esperaba código 409, se obtuvo {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba de duplicado: {e}")
        return False

def test_login():
    """Prueba el inicio de sesión"""
    print_header("PRUEBA: Inicio de Sesión")
    
    user_data = {
        "usuario": TEST_USER,
        "contraseña": TEST_PASSWORD
    }
    
    try:
        # Crear sesión para mantener cookies
        session = requests.Session()
        
        response = session.post(
            f"{BASE_URL}/login",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print_info(f"POST /login - Código: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Inicio de sesión exitoso")
            print_info(f"Usuario: {data.get('usuario')}")
            print_info(f"Fecha login: {data.get('fecha_login')}")
            return session  # Retorna la sesión para pruebas posteriores
        else:
            print_error("Error en login")
            print_error(f"Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error en login: {e}")
        return None

def test_invalid_login():
    """Prueba login con credenciales incorrectas"""
    print_header("PRUEBA: Login Inválido (debe fallar)")
    
    user_data = {
        "usuario": TEST_USER,
        "contraseña": "contraseña_incorrecta"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print_info(f"POST /login - Código: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Error 401 correcto - Credenciales inválidas")
            return True
        else:
            print_warning(f"Se esperaba código 401, se obtuvo {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba de login inválido: {e}")
        return False

def test_tasks_without_auth():
    """Prueba acceso a tareas sin autenticación"""
    print_header("PRUEBA: Acceso sin Autenticación (debe fallar)")
    
    try:
        response = requests.get(f"{BASE_URL}/tareas")
        
        print_info(f"GET /tareas - Código: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Error 401 correcto - No autorizado")
            return True
        else:
            print_warning(f"Se esperaba código 401, se obtuvo {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba sin auth: {e}")
        return False

def test_tasks_with_auth(session):
    """Prueba acceso a tareas con autenticación"""
    print_header("PRUEBA: Acceso a Tareas con Autenticación")
    
    try:
        response = session.get(f"{BASE_URL}/tareas")
        
        print_info(f"GET /tareas - Código: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Acceso autorizado a página de tareas")
            print_info("Página HTML de bienvenida cargada correctamente")
            return True
        else:
            print_error(f"Error en acceso a tareas: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error en acceso a tareas: {e}")
        return False

def test_logout(session):
    """Prueba cerrar sesión"""
    print_header("PRUEBA: Cerrar Sesión")
    
    try:
        response = session.post(f"{BASE_URL}/logout")
        
        print_info(f"POST /logout - Código: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Sesión cerrada exitosamente")
            print_info(f"Mensaje: {data.get('mensaje')}")
            return True
        else:
            print_error(f"Error en logout: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en logout: {e}")
        return False

def test_access_after_logout(session):
    """Prueba acceso después de cerrar sesión"""
    print_header("PRUEBA: Acceso Después de Logout (debe fallar)")
    
    try:
        response = session.get(f"{BASE_URL}/tareas")
        
        print_info(f"GET /tareas - Código: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Error 401 correcto - Sesión cerrada")
            return True
        else:
            print_warning(f"Se esperaba código 401, se obtuvo {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba post-logout: {e}")
        return False

def test_list_users():
    """Prueba endpoint de listar usuarios"""
    print_header("PRUEBA: Listar Usuarios (Debugging)")
    
    try:
        response = requests.get(f"{BASE_URL}/usuarios")
        
        print_info(f"GET /usuarios - Código: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Lista de usuarios obtenida")
            print_info(f"Total usuarios: {data.get('total', 0)}")
            
            # Buscar nuestro usuario de prueba
            usuarios = data.get('usuarios', [])
            test_user_found = any(u['usuario'] == TEST_USER for u in usuarios)
            
            if test_user_found:
                print_success(f"Usuario de prueba '{TEST_USER}' encontrado en la lista")
            else:
                print_warning(f"Usuario de prueba '{TEST_USER}' no encontrado")
            
            return True
        else:
            print_error(f"Error en listar usuarios: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en listar usuarios: {e}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🧪 INICIANDO PRUEBAS AUTOMATIZADAS")
    print("Sistema de Gestión de Tareas - API Flask")
    print(f"{'='*50}{Colors.END}")
    
    results = []
    
    # Verificar servidor
    if not test_server_running():
        print_error("El servidor no está ejecutándose. Terminando pruebas.")
        return False
    
    # Registro
    results.append(("Registro de usuario", test_registration()))
    
    # Registro duplicado
    results.append(("Registro duplicado", test_duplicate_registration()))
    
    # Login inválido
    results.append(("Login inválido", test_invalid_login()))
    
    # Login válido
    session = test_login()
    results.append(("Login válido", session is not None))
    
    if session:
        # Acceso sin auth
        results.append(("Acceso sin auth", test_tasks_without_auth()))
        
        # Acceso con auth
        results.append(("Acceso con auth", test_tasks_with_auth(session)))
        
        # Logout
        results.append(("Logout", test_logout(session)))
        
        # Acceso después de logout
        results.append(("Acceso post-logout", test_access_after_logout(session)))
    
    # Listar usuarios
    results.append(("Listar usuarios", test_list_users()))
    
    # Mostrar resumen
    print_header("RESUMEN DE PRUEBAS")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
            passed += 1
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}")
    if passed == total:
        print(f"{Colors.GREEN}🎉 TODAS LAS PRUEBAS PASARON ({passed}/{total})")
        print("✅ El sistema está funcionando correctamente")
    else:
        print(f"{Colors.YELLOW}⚠️  ALGUNAS PRUEBAS FALLARON ({passed}/{total})")
        print("❗ Revisar errores arriba")
    
    print(f"{Colors.END}")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Pruebas interrumpidas por el usuario{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)