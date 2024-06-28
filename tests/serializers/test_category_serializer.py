import pytest
from product.factories import CategoryFactory
from product.serializers.category_serializer import CategorySerializer


@pytest.mark.django_db
def test_category_serializer():
    category = CategoryFactory()
    serializer = CategorySerializer(instance=category)
    assert serializer.data["title"] == category.title
    assert serializer.data["slug"] == category.slug
    assert serializer.data["description"] == category.description
    assert serializer.data["active"] == category.active
