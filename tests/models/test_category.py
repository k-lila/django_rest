import pytest
from product.models import Category
from product.factories import CategoryFactory


@pytest.mark.django_db
def test_category():
    category = CategoryFactory()

    assert category.title is not None
    assert category.slug is not None
    assert category.description is not None
    assert category.active in [True, False]

    saved_category = Category.objects.get(slug=category.slug)
    assert saved_category.title == category.title
    assert saved_category.slug == category.slug
    assert saved_category.description == category.description
    assert saved_category.active == category.active
