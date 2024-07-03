import json

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.urls import reverse

from product.factories import CategoryFactory, ProductFactory
from order.factories import UserFactory, OrderFactory
from order.models import Order


class TestOrderViewSet(APITestCase):

    client = APIClient()

    def setUp(self):
        self.category = CategoryFactory(title="tech")
        self.product = ProductFactory(
            title="mouse", price=100, category=[self.category]
        )
        self.order = OrderFactory(product=[self.product])

    def test_order(self):
        response = self.client.get(reverse("order-list", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = json.loads(response.content)[0]
        self.assertEqual(order_data["product"][0]["title"], self.product.title)
        self.assertEqual(order_data["product"][0]["price"], self.product.price)
        self.assertEqual(order_data["product"][0]["active"], self.product.active)
        self.assertEqual(
            order_data["product"][0]["category"][0]["title"], self.category.title
        )

    def test_create_order(self):
        user = UserFactory()
        product = ProductFactory()
        data = json.dumps({"products_id": [product.id], "user": user.id})
        response = self.client.post(
            reverse("order-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_order(self):
        response = self.client.get(reverse("order-list", kwargs={"version": "v1"}))
        order_data = json.loads(response.content)
        response_product_id = order_data[0]["product"][0]["id"]
        product_id = list(self.order.product.values_list("id", flat=True))[0]
        self.assertEqual(response_product_id, product_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_order(self):
        response = self.client.delete(
            reverse("order-detail", kwargs={"version": "v1", "pk": self.order.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
