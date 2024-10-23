
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group, Permission
from django.test import Client
from django.db import connections, DEFAULT_DB_ALIAS
from django.core import management

from user.models import User


class UserViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        self.superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass"
        )
        self.group = Group.objects.create(name="TestGroup")
        self.permission = Permission.objects.create(codename='test_test', name='Can View', content_type_id=1)

    def test_create_user(self):
        response = self.client.post(reverse('create_user'), {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.get(email='newuser@example.com') is not None)

    def test_login_user(self):
        response = self.client.post(reverse('login_user'), {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        self.client.login(email='admin@example.com', password='adminpass')
        user_to_delete = User.objects.create_user(
            email="deleteuser@example.com",
            password="deletepass123"
        )
        response = self.client.post(reverse('delete_user', args=[user_to_delete.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='deleteuser@example.com').exists())

    def test_add_user_to_group(self):
        self.client.login(email='admin@example.com', password='adminpass')
        response = self.client.post(reverse('add_user_to_group', args=[self.user.id, self.group.name]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.group in self.user.groups.all())

    def test_remove_user_from_group(self):
        self.client.login(email='admin@example.com', password='adminpass')
        self.user.groups.add(self.group)
        response = self.client.post(reverse('remove_user_from_group', args=[self.user.id, self.group.name]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.group in self.user.groups.all())

    def test_add_permission_to_user(self):
        self.client.login(email='admin@example.com', password='adminpass')
        response = self.client.post(reverse('add_permission_to_user', args=[self.user.id, 'add_user']))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.has_perm('user.add_user'))

    def test_remove_permission_from_user(self):
        self.client.login(email='admin@example.com', password='adminpass')
        self.user.user_permissions.add(self.permission)
        response = self.client.post(reverse('remove_permission_from_user', args=[self.user.id, 'test_test']))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.has_perm('user.test_test'))

    def test_create_user_invalid(self):
        response = self.client.post(reverse('create_user'), {
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(first_name='New').exists())

    def test_login_user_invalid_credentials(self):
        response = self.client.post(reverse('login_user'), {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)

    def test_session_after_login(self):
        login_response = self.client.post(reverse('login_user'), {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(login_response.status_code, 200)

        session_cookie = self.client.cookies.get('sessionid')
        self.assertIsNotNone(session_cookie, "Session cookie should be set after login")

        session_check_response = self.client.get(reverse('session_check'))
        self.assertEqual(session_check_response.status_code, 200)
        self.assertIn('User testuser@example.com is authenticated', session_check_response.json().get('message'))

    def test_session_check_without_login(self):
        response = self.client.get(reverse('session_check'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login


class DatabaseConnectionTests(TestCase):
    def test_connection_is_usable(self):
        connection = connections[DEFAULT_DB_ALIAS]
        self.assertTrue(connection.is_usable())

    def test_flush_command(self):
        User.objects.create_user(username='tempuser', email='tempuser@email.com', password='temppass')
        user_count_before = User.objects.count()
        self.assertEqual(user_count_before, 1)

        management.call_command('flush', verbosity=0, interactive=False)

        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, 0)
