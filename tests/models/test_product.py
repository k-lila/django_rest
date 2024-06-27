import pytest
from product.factories import CategoryFactory, ProductFactory


@pytest.mark.django_db
def test_product():
    category = CategoryFactory()
    product = ProductFactory(category=[category])
    assert product.title is not None
    assert product.price is not None
    assert category in product.category.all()
