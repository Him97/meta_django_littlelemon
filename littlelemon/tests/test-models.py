import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import models
from LittleLemonAPI.models import (
    Category,
    Booking,
    Menu,
    MenuItem,
    Cart,
    Order,
    OrderItem
)


class ModelTestCase(TestCase):
    def test_get_item(self):
        item = MenuItem.objects.create(
            title="IceCream", price=80, inventory=100)
        self.assertEqual(item, "IceCream: 80")

    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'password')
        self.category = Category.objects.create(
            slug='testslug', title='Test Title')
        self.menu = Menu.objects.create(
            title='Test Menu', price=10.99, inventory=50)
        self.menu_item = MenuItem.objects.create(
            title='Test Item',
            price=1.99,
            featured=True,
            category=self.category
        )
        self.cart = Cart.objects.create(
            user=self.user,
            menuitem=self.menu_item,
            quantity=2,
            unit_price=1.99,
            price=3.98)

        self.order = Order.objects.create(
            user=self.user, delivery_crew=None, status=False, total=0)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            menuitem=self.menu_item,
            quantity=2,
            unit_price=1.99,
            price=3.98)

    def tearDown(self):
        self.user.delete()
        self.category.delete()
        self.menu.delete()
        self.menu_item.delete()
        self.cart.delete()
        self.order.delete()
        self.order_item.delete()
        User.objects.all().delete()
        Category.objects.all().delete()
        Menu.objects.all().delete()
        MenuItem.objects.all().delete()
        Cart.objects.all().delete()
        Order.objects.all().delete()
        OrderItem.objects.all().delete()


class CategoryModelTestCase(ModelTestCase):
    def test_category_model(self):
        category = Category.objects.get(slug='testslug')
        self.assertEqual(category.title, 'Test Title')


class BookingModelTestCase(ModelTestCase):
    def test_booking_model(self):
        booking = Booking.objects.create(
            first_name='John',
            last_name='Doe',
            reservation_slot=10,
            guest_number=2,
            comment='Test comment'
        )
        self.assertEqual(booking.first_name, 'John')
        self.assertEqual(booking.last_name, 'Doe')
        self.assertEqual(booking.reservation_slot, 10)
        self.assertEqual(booking.guest_number, 2)
        self.assertEqual(booking.comment, 'Test comment')


class MenuModelTestCase(ModelTestCase):
    def test_menu_model(self):
        menu = Menu.objects.get(title='Test Menu')
        self.assertEqual(menu.price, 10.99)
        self.assertEqual(menu.inventory, 50)
        self.assertEqual(menu.menu_item_description,
                         'Test menu item description')


class MenuItemModelTestCase(ModelTestCase):
    def test_menu_item_model(self):
        menu_item = MenuItem.objects.get(title='Test Item')
        self.assertEqual(menu_item.price, 1.99)
        self.assertEqual(menu_item.featured, True)
        self.assertEqual(menu_item.category, self.category)
        self.assertEqual(menu_item.inventory, 50)

    def test_get_item_method(self):
        menu_item = MenuItem.objects.get(title='Test Item')
        self.assertEqual(menu_item.get_item(), 'Test Item: 1.99')


class CartModelTestCase(ModelTestCase):
    def test_cart_model(self):
        cart = Cart.objects.get(menuitem=self.menu_item, user=self.user)
        self.assertEqual(cart.menuitem, self.menu_item)
        self.assertEqual(cart.quantity, 2)
        self.assertEqual(cart.unit_price, 1.99)
        self.assertEqual(cart.price, 3.98)


class OrderModelTestCase(ModelTestCase):
    def test_order_model(self):
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.delivery_crew, None)
        self.assertEqual(order.status, False)
        self.assertEqual(order.total, 0)
        self.assertEqual(order.date, None)


class OrderItemModelTestCase(ModelTestCase):
    def test_order_item_model(self):
        order_item = OrderItem.objects.get(
            order=self.order, menuitem=self.menu_item)
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.menuitem, self.menu_item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.unit_price, 1.99)
        self.assertEqual(order_item.price, 3.98)

    def test_unique_together(self):
        another_order_item = OrderItem.objects.create(
            order=self.order, menuitem=self.menu_item, quantity=2)
        with self.assertRaises(OrderItem.DoesNotExist):
            OrderItem.objects.get(
                order=self.order, menu_item=self.menu_item, quantity=2)

    def test_order_item_delete(self):
        order_item = OrderItem.objects.get(
            order=self.order, menuitem=self.menu_item)
        order_item.delete()
        with self.assertRaises(OrderItem.DoesNotExist):
            OrderItem.objects.get(order=self.order, menuitem=self.menu_item)


if __name__ == '__main__':
    unittest.main()
