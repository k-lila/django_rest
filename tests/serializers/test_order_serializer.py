import pytest

from django.contrib.auth.models import User
from product.models import Product, Category
from product.serializers import CategorySerializer, ProductSerializer
from product.factories import ProductFactory
from order.serializers import OrderSerializer
from order.factories import UserFactory, OrderFactory


@pytest.mark.django_db
def test_order_serializer():
    user = UserFactory()
    product1 = ProductFactory()
    product2 = ProductFactory()
    order = OrderFactory(user=user, product=[product1, product2])
    serializer = OrderSerializer(order)
    serialized_product_title = [
        product["title"] for product in serializer.data["product"]
    ]
    assert serialized_product_title == [product1.title, product2.title]
    assert serializer.get_total(order) == (product1.price + product2.price)
