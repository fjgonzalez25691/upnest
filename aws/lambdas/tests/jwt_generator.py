"""
UpNest Testing Utilities - JWT Token Generator
Genera tokens JWT válidos para testing local de las Lambda functions
"""

import jwt
import json
from datetime import datetime, timedelta
from typing import Dict, Any

def generate_test_jwt(
    user_id: str = "test-user-123456789",
    username: str = "testuser@example.com",
    cognito_groups: list = None,
    expires_in_hours: int = 24
) -> str:
    """
    Genera un JWT token válido para testing local
    
    Args:
        user_id: El sub (user ID) del token
        username: El username del usuario
        cognito_groups: Lista de grupos de Cognito (opcional)
        expires_in_hours: Horas hasta que expire el token
        
    Returns:
        JWT token como string
    """
    if cognito_groups is None:
        cognito_groups = ["users"]
    
    # Payload del token
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "aud": "75g0r5a7bbp1mgpmqrg3e1iibm",  # Client ID de Cognito
        "cognito:groups": cognito_groups,
        "email_verified": True,
        "iss": f"https://cognito-idp.eu-south-2.amazonaws.com/eu-south-2_WInbcDDjo",
        "cognito:username": username,
        "aud": "75g0r5a7bbp1mgpmqrg3e1iibm",
        "event_id": "test-event-id",
        "token_use": "id",
        "auth_time": int(now.timestamp()),
        "exp": int((now + timedelta(hours=expires_in_hours)).timestamp()),
        "iat": int(now.timestamp()),
        "email": username
    }
    
    # Para testing local, usamos un secret simple
    # En producción, Cognito usa claves RSA
    secret = "test-secret-for-local-development-only"
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def generate_test_users_tokens() -> Dict[str, Dict[str, Any]]:
    """
    Genera tokens para múltiples usuarios de prueba
    
    Returns:
        Dict con usuarios de prueba y sus tokens
    """
    test_users = {
        "user1": {
            "userId": "user-1-test-123456",
            "email": "user1@test.com",
            "username": "user1@test.com",
            "token": None
        },
        "user2": {
            "userId": "user-2-test-789012", 
            "email": "user2@test.com",
            "username": "user2@test.com",
            "token": None
        },
        "admin": {
            "userId": "admin-test-456789",
            "email": "admin@test.com", 
            "username": "admin@test.com",
            "token": None
        }
    }
    
    # Generar tokens para cada usuario
    for user_key, user_data in test_users.items():
        groups = ["admins"] if user_key == "admin" else ["users"]
        user_data["token"] = generate_test_jwt(
            user_id=user_data["userId"],
            username=user_data["username"],
            cognito_groups=groups
        )
    
    return test_users

def create_test_events_with_auth():
    """
    Crea test events JSON con tokens JWT válidos
    """
    users = generate_test_users_tokens()
    
    # Imprimir tokens para uso en test events
    print("=== TOKENS JWT PARA TEST EVENTS ===")
    for user_key, user_data in users.items():
        print(f"\n{user_key.upper()}:")
        print(f"User ID: {user_data['userId']}")
        print(f"Email: {user_data['email']}")
        print(f"Token: {user_data['token']}")
        print("-" * 50)
    
    return users

if __name__ == "__main__":
    create_test_events_with_auth()
