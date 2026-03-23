from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re


class UserCreate(BaseModel):
    """Модель для создания пользователя (Задание 3.1)"""
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    age: Optional[int] = Field(None, ge=0, le=150, description="Возраст пользователя")
    is_subscribed: Optional[bool] = Field(False, description="Подписка на рассылку")
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Возраст должен быть положительным числом')
        return v


class LoginRequest(BaseModel):
    """Модель для логина"""
    username: str
    password: str


class ProfileResponse(BaseModel):
    """Модель ответа профиля"""
    user_id: str
    username: str
    message: str


class CommonHeaders(BaseModel):
    """Модель для обработки заголовков (Задание 5.4)"""
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")
    
    class Config:
        allow_population_by_field_name = True
    
    @validator('accept_language')
    def validate_accept_language(cls, v):
        """Валидация формата Accept-Language"""
        if not v:
            raise ValueError('Accept-Language header is required')
        
        pattern = r'^[a-zA-Z]{2}(-[a-zA-Z]{2})?(,[a-zA-Z]{2}(-[a-zA-Z]{2})?;q=[0-9]\.[0-9])*$'
       
        if not re.match(r'^[a-zA-Z-;,=0-9.]+$', v):
            raise ValueError('Invalid Accept-Language format')
        return v
    