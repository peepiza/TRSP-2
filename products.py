from typing import List, Optional
from pydantic import BaseModel


class Product(BaseModel):
    """Модель товара"""
    product_id: int
    name: str
    category: str
    price: float


sample_products = [
    Product(product_id=123, name="Smartphone", category="Electronics", price=599.99),
    Product(product_id=456, name="Phone Case", category="Accessories", price=19.99),
    Product(product_id=789, name="Iphone", category="Electronics", price=1299.99),
    Product(product_id=101, name="Headphones", category="Accessories", price=99.99),
    Product(product_id=202, name="Smartwatch", category="Electronics", price=299.99),
]


def get_product_by_id(product_id: int) -> Optional[Product]:
    """Получить товар по ID"""
    for product in sample_products:
        if product.product_id == product_id:
            return product
    return None


def search_products(
    keyword: str, 
    category: Optional[str] = None, 
    limit: int = 10
) -> List[Product]:
    """Поиск товаров по ключевому слову и категории"""
    results = []
    keyword_lower = keyword.lower()
    
    for product in sample_products:
        # Проверка по ключевому слову
        if keyword_lower not in product.name.lower():
            continue
        
        if category and product.category.lower() != category.lower():
            continue
        
        results.append(product)
        
        if len(results) >= limit:
            break
    
    return results