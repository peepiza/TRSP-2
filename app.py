from fastapi import FastAPI, HTTPException, status, Request, Response, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
import time
from typing import Optional

from models import UserCreate, LoginRequest, CommonHeaders
from products import sample_products, get_product_by_id, search_products
from auth import (
    authenticate_user, create_session_token, 
    get_current_user_from_session, users_db
)


app = FastAPI(
    title="FastAPI Control Work",
    description="Контрольная работа по технологиям разработки серверных приложений",
    version="1.0.0"
)


# ============= Задание 3.1 =============
@app.post("/create_user", response_model=UserCreate)
async def create_user(user: UserCreate):
    """
    Создание пользователя (Задание 3.1)
    Принимает данные пользователя и возвращает их
    """
    return user


# ============= Задание 3.2 =============
@app.get("/product/{product_id}")
async def get_product(product_id: int):
    """
    Получение информации о товаре по ID (Задание 3.2)
    """
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Product not found"}
        )
    return product


@app.get("/products/search")
async def search_products_endpoint(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10
):
    """
    Поиск товаров (Задание 3.2)
    """
    if limit <= 0:
        limit = 10
    
    results = search_products(keyword, category, limit)
    return results


# ============= Задания 5.1, 5.2, 5.3 =============
@app.post("/login")
async def login(login_data: LoginRequest, response: Response):
    """
    Вход в систему (Задания 5.1, 5.2, 5.3)
    Устанавливает cookie сессии
    """
    user_id = authenticate_user(login_data.username, login_data.password)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid credentials"}
        )
    
    # Создаем токен с текущим временем
    current_time = int(time.time())
    session_token = create_session_token(user_id, current_time)
    
    # Устанавливаем cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=300,  # 5 минут
        secure=False  # Для тестирования, в production должен быть True
    )
    
    return {"message": "Login successful", "user_id": user_id}


@app.get("/profile")
async def get_profile(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user_from_session)
):
    """
    Получение профиля пользователя (Задания 5.1, 5.2, 5.3)
    Защищенный маршрут с проверкой сессии
    """
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "message": "Profile information"
    }


@app.get("/user")
async def get_user(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user_from_session)
):
    """
    Получение информации о пользователе (Задание 5.1)
    """
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "message": "User information"
    }


# ============= Задание 5.4 =============
@app.get("/headers")
async def get_headers(
    headers: CommonHeaders = Depends()
):
    """
    Получение заголовков (Задание 5.4)
    """
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


@app.get("/info")
async def get_info(
    headers: CommonHeaders = Depends(),
    response: Response = None
):
    """
    Получение информации с заголовками и серверным временем (Задание 5.4)
    """
    # Добавляем заголовок с серверным временем
    current_time = datetime.now().isoformat()
    response.headers["X-Server-Time"] = current_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }


# ============= Дополнительные эндпоинты для тестирования =============
@app.get("/")
async def root():
    """
    Корневой эндпоинт
    """
    return {
        "message": "FastAPI Control Work",
        "endpoints": [
            "/create_user - POST",
            "/product/{product_id} - GET",
            "/products/search - GET",
            "/login - POST",
            "/profile - GET",
            "/user - GET",
            "/headers - GET",
            "/info - GET"
        ]
    }


@app.get("/test/session")
async def test_session(request: Request):
    """
    Тестовый эндпоинт для проверки сессии
    """
    session_token = request.cookies.get("session_token")
    return {
        "has_session": session_token is not None,
        "session_token": session_token
    }