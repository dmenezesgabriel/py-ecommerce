from src.application.dto.category_dto import CategoryResponse
from src.application.dto.product_dto import ProductResponse
from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.product_entity import ProductEntity


def serialize_product(product: ProductEntity) -> ProductResponse:
    return ProductResponse(
        sku=product.sku,
        name=product.name,
        category_name=product.category.name,
        price=product.price.amount,
        quantity=product.inventory.quantity,
    )


def serialize_category(category: CategoryEntity) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.name,
    )
