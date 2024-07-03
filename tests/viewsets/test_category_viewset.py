import json

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.urls import reverse

from product.factories import CategoryFactory
from product.models.category import Category


class TestCategoryViewSet(APITestCase):

    client = APIClient()

    def setUp(self):
        self.category = CategoryFactory(title="_test")

    def test_get_all_category(self):
        response = self.client.get(reverse("category-list", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category_data = json.loads(response.content)
        self.assertEqual(category_data[0]["title"], self.category.title)

    def test_create_category(self):
        data = json.dumps({"title": "test"})
        response = self.client.post(
            reverse("category-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        create_category = Category.objects.get(title="test")
        self.assertEqual(create_category.title, "test")

    def test_get_category(self):
        response = self.client.get(reverse("category-list", kwargs={"version": "v1"}))
        category_data = json.loads(response.content)
        self.assertEqual(category_data[0]["slug"], self.category.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_category(self):
        response = self.client.delete(
            reverse("category-detail", kwargs={"version": "v1", "pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
