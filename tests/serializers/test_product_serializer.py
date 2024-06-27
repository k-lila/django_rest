import pytest
from product.factories import CategoryFactory, ProductFactory
from product.serializers.product_serializer import ProductSerializer


@pytest.mark.django_db
def test_product_serializer():
    category = CategoryFactory()
    product = ProductFactory(category=[category])
    serializer = ProductSerializer(instance=product)

    assert serializer.data["title"] == product.title
    assert serializer.data["description"] == product.description
    assert serializer.data["price"] == product.price
    assert serializer.data["active"] == product.active

    serialized_categories = serializer.data["category"]

    assert serialized_categories[0]["title"] == category.title
    assert serialized_categories[0]["slug"] == category.slug
    assert serialized_categories[0]["description"] == category.description
    assert serialized_categories[0]["active"] == category.active
