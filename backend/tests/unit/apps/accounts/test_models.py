from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Profile

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            full_name='Test User'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertEqual(user.full_name, 'Test User')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

class ProfileModelTest(TestCase):
    def test_profile_creation(self):
        user = User.objects.create_user(email='testprofile@example.com', password='password')
        profile = Profile.objects.create(user=user, bio='Test bio')
        
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(str(profile), 'testprofile@example.com Profile')
