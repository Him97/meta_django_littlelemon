from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from LittleLemonAPI.models import Menu
from LittleLemonAPI.serializers import MenuItemSerializer


class MenuViewTest(TestCase):
    def setUp(self):
        Menu.objects.create(
            title='Dish1', description='Description1', price=10.0)
        Menu.objects.create(
            title='Dish2', description='Description2', price=15.0)

        self.client = APIClient()

    def test_getall(self):
        url = reverse('menu-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        menu_items = Menu.objects.all()
        serializer = MenuItemSerializer(menu_items, many=True)

        self.assertEqual(response.data, serializer.data)
