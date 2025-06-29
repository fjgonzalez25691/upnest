"""
Script para probar que los imports funcionan correctamente
"""

import os
import sys

def test_import_from_babies():
    """Simular imports desde babies"""
    print("🧪 PROBANDO IMPORTS DESDE BABIES")
    print("=" * 50)
    
    # Simular la lógica de import de babies/create.py
    current_dir = os.path.dirname(__file__)
    babies_dir = os.path.join(current_dir, 'babies')
    shared_path = os.path.join(current_dir, 'shared')
    
    print(f"📁 Directorio actual: {current_dir}")
    print(f"📁 Directorio shared: {shared_path}")
    
    # Añadir shared al path
    if shared_path not in sys.path:
        sys.path.insert(0, shared_path)
    
    try:
        # Intentar importar los módulos
        from dynamodb_client import dynamodb_client
        print("✅ dynamodb_client importado correctamente")
        
        from jwt_utils import jwt_validator, extract_token_from_event
        print("✅ jwt_utils importado correctamente")
        
        from response_utils import created_response, bad_request_response
        print("✅ response_utils importado correctamente")
        
        from validation_utils import BabyValidator, generate_id
        print("✅ validation_utils importado correctamente")
        
        print("\n🎉 TODOS LOS IMPORTS FUNCIONAN CORRECTAMENTE!")
        
        # Probar que las funciones están disponibles
        print(f"🔍 dynamodb_client type: {type(dynamodb_client)}")
        print(f"🔍 jwt_validator type: {type(jwt_validator)}")
        
    except ImportError as e:
        print(f"❌ Error de import: {e}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_import_from_babies()
