from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from pricing.models import Service
from .models import Cart, CartItem, Order, OrderItem
from datetime import timedelta

class CartTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Create test services
        self.service1 = Service.objects.create(name='Service 1', price=1000, category='cat1', duration=timedelta(hours=1), description='Test service 1')
        self.service2 = Service.objects.create(name='Service 2', price=2000, category='cat2', duration=timedelta(hours=2), description='Test service 2')
        # Create client and login
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_add_to_cart(self):
        url = reverse('cart:add_to_cart', args=[self.service1.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('cart:view_cart'))
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, service=self.service1)
        self.assertEqual(cart_item.quantity, 1)

    def test_view_cart(self):
        # Add item to cart first
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, service=self.service1, quantity=2)
        url = reverse('cart:view_cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Service 1')
        self.assertContains(response, '2')

    def test_checkout(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, service=self.service1, quantity=1)
        url = reverse('cart:checkout')
        response = self.client.post(url)
        # After checkout, cart should be empty
        cart.refresh_from_db()
        self.assertEqual(cart.items.count(), 0)
        # Order should be created
        order = Order.objects.get(user=self.user)
        order_item = OrderItem.objects.get(order=order, service=self.service1)
        self.assertEqual(order_item.quantity, 1)
        self.assertRedirects(response, reverse('cart:order_success', args=[order.id]))

    def test_order_success(self):
        order = Order.objects.create(user=self.user)
        url = reverse('cart:order_success', args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Adjust assertion to check for order id in response content
        self.assertContains(response, str(order.id))
