"""
Script para verificar las rutas de imports compartidos
"""

import os
import sys

def test_shared_path_from_babies():
    """Simula la ruta desde el directorio babies"""
    # Simular __file__ como si estuviéramos en babies/create.py
    current_file = r"d:\proyectos\AWSLambdaHackathon\upnest\aws\lambdas\babies\create.py"
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE RUTAS DE IMPORT")
    print("=" * 60)
    
    print(f"📁 Archivo actual simulado: {current_file}")
    
    # Calcular shared_path
    shared_path = os.path.join(os.path.dirname(current_file), '..', 'shared')
    print(f"📂 shared_path calculado: {shared_path}")
    
    # Normalizar la ruta
    shared_path_normalized = os.path.normpath(shared_path)
    print(f"✅ shared_path normalizado: {shared_path_normalized}")
    
    # Verificar si existe
    exists = os.path.exists(shared_path_normalized)
    print(f"🔍 ¿Existe la ruta? {exists}")
    
    if exists:
        print(f"📋 Contenido del directorio shared:")
        try:
            files = os.listdir(shared_path_normalized)
            for file in files:
                print(f"   - {file}")
        except Exception as e:
            print(f"   ❌ Error listando archivos: {e}")
    
    # Verificar archivos específicos
    shared_files = [
        'dynamodb_client.py',
        'jwt_utils.py', 
        'response_utils.py',
        'validation_utils.py',
        'exceptions.py',
        '__init__.py'
    ]
    
    print(f"\n🔍 Verificando archivos compartidos:")
    for file in shared_files:
        file_path = os.path.join(shared_path_normalized, file)
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"   {status} {file}")

def test_shared_path_from_growth_data():
    """Simula la ruta desde el directorio growth-data"""
    current_file = r"d:\proyectos\AWSLambdaHackathon\upnest\aws\lambdas\growth-data\create.py"
    
    print("\n" + "=" * 60)
    print("🔍 VERIFICACIÓN DESDE GROWTH-DATA")
    print("=" * 60)
    
    print(f"📁 Archivo actual simulado: {current_file}")
    
    shared_path = os.path.join(os.path.dirname(current_file), '..', 'shared')
    shared_path_normalized = os.path.normpath(shared_path)
    
    print(f"📂 shared_path calculado: {shared_path}")
    print(f"✅ shared_path normalizado: {shared_path_normalized}")
    
    exists = os.path.exists(shared_path_normalized)
    print(f"🔍 ¿Existe la ruta? {exists}")

def test_current_working_directory():
    """Mostrar información del directorio actual"""
    print("\n" + "=" * 60)
    print("🔍 INFORMACIÓN DEL ENTORNO")
    print("=" * 60)
    
    print(f"💻 Directorio de trabajo actual: {os.getcwd()}")
    print(f"🐍 Python path:")
    for i, path in enumerate(sys.path):
        print(f"   {i}: {path}")

if __name__ == "__main__":
    test_shared_path_from_babies()
    test_shared_path_from_growth_data()
    test_current_working_directory()
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 60)
