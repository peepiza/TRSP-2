import uuid
import time
from datetime import datetime
from typing import Optional, Tuple
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from fastapi import HTTPException, status, Request, Response


SECRET_KEY = "your-secret-key-here-change-in-production"
serializer = URLSafeTimedSerializer(SECRET_KEY)


users_db = {
    "user123": {
        "password": "password123",
        "user_id": str(uuid.uuid4()),
        "username": "user123"
    }
}


def authenticate_user(username: str, password: str) -> Optional[str]:
    """Аутентификация пользователя"""
    if username in users_db and users_db[username]["password"] == password:
        return users_db[username]["user_id"]
    return None


def create_session_token(user_id: str, timestamp: Optional[int] = None) -> str:
    """Создание токена сессии с подписью"""
    if timestamp is None:
        timestamp = int(time.time())
    
    # Формат: user_id.timestamp
    data = f"{user_id}.{timestamp}"
    signature = serializer.dumps(data)
    return signature


def verify_session_token(token: str) -> Tuple[Optional[str], Optional[int]]:
    """Проверка токена сессии и возврат user_id и timestamp"""
    try:
        # Расшифровываем токен
        data = serializer.loads(token, max_age=300)  # 5 минут максимальное время жизни
        parts = data.split('.')
        
        if len(parts) != 2:
            return None, None
        
        user_id = parts[0]
        timestamp = int(parts[1])
        
        return user_id, timestamp
    except (SignatureExpired, BadSignature, ValueError):
        return None, None


def update_session_if_needed(
    response: Response,
    current_token: str,
    last_activity: int
) -> Tuple[bool, Optional[str]]:
    """
    Проверка необходимости обновления сессии
    Возвращает (нужно_ли_обновить, новый_токен)
    """
    current_time = int(time.time())
    time_passed = current_time - last_activity
    
    # Если прошло больше 5 минут - сессия истекла
    if time_passed > 300:
        return False, None
    
    # Если прошло больше 3 минут - обновляем
    if time_passed >= 180:
        # Получаем user_id из текущего токена
        user_id, _ = verify_session_token(current_token)
        if user_id:
            new_token = create_session_token(user_id, current_time)
            return True, new_token
    
    return False, None


def get_current_user_from_session(request: Request, response: Response) -> dict:
    """
    Получение текущего пользователя из сессии
    С проверкой времени активности (Задание 5.3)
    """
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Unauthorized"}
        )
    
    # Проверяем валидность токена
    user_id, timestamp = verify_session_token(session_token)
    
    if not user_id or not timestamp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid session"}
        )
    
    # Проверяем актуальность сессии
    current_time = int(time.time())
    time_passed = current_time - timestamp
    
    if time_passed > 300:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Session expired"}
        )
    
    # Обновляем сессию если нужно
    should_update, new_token = update_session_if_needed(
        response, session_token, timestamp
    )
    
    if should_update and new_token:
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=300,
            secure=False  # Для тестирования, в production должен быть True
        )
    
    # Находим пользователя
    for user_data in users_db.values():
        if user_data["user_id"] == user_id:
            return {
                "user_id": user_id,
                "username": user_data["username"]
            }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"message": "User not found"}
    )