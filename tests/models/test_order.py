import pytest
from product.factories import ProductFactory
from order.factories import OrderFactory, UserFactory


@pytest.mark.django_db
def test_order_creation():
    user = UserFactory()
    product1 = ProductFactory()
    product2 = ProductFactory()
    order = OrderFactory(user=user, product=[product1, product2])

    assert order.user == user
    assert product1 in order.product.all()
    assert product2 in order.product.all()
