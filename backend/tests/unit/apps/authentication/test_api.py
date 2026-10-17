from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationAPITest(APITestCase):
    def test_register_user(self):
        url = '/api/v1/auth/register/'
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!',
            'full_name': 'New User'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'newuser@example.com')
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_login_user(self):
        # Setup — verified users can log in
        User.objects.create_user(email='login@example.com', password='SecurePassword123!', email_verified=True)
        
        url = '/api/v1/auth/login/'
        data = {
            'email': 'login@example.com',
            'password': 'SecurePassword123!'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])

    def test_login_blocked_when_unverified(self):
        User.objects.create_user(email='unverified@example.com', password='SecurePassword123!', email_verified=False)

        response = self.client.post('/api/v1/auth/login/', {
            'email': 'unverified@example.com',
            'password': 'SecurePassword123!'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['errors']['code'], 'email_not_verified')

    def test_login_allowed_after_verification(self):
        from apps.authentication.services import request_verification_otp, verify_email_otp

        User.objects.create_user(email='verifyme@example.com', password='SecurePassword123!', email_verified=False)
        code = request_verification_otp('verifyme@example.com')
        self.assertTrue(code)
        ok, reason = verify_email_otp('verifyme@example.com', code)
        self.assertTrue(ok, reason)

        response = self.client.post('/api/v1/auth/login/', {
            'email': 'verifyme@example.com',
            'password': 'SecurePassword123!'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_otp_verify_endpoint(self):
        from apps.authentication.services import request_verification_otp

        User.objects.create_user(email='otpuser@example.com', password='SecurePassword123!', email_verified=False)
        code = request_verification_otp('otpuser@example.com')

        response = self.client.post('/api/v1/auth/verify-otp/', {
            'email': 'otpuser@example.com',
            'otp': code,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # Wrong code rejected
        User.objects.create_user(email='otpfail@example.com', password='SecurePassword123!', email_verified=False)
        request_verification_otp('otpfail@example.com')
        bad = self.client.post('/api/v1/auth/verify-otp/', {
            'email': 'otpfail@example.com',
            'otp': '000000',
        }, format='json')
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(bad.data['success'])

    def test_resend_verification(self):
        User.objects.create_user(email='resendme@example.com', password='SecurePassword123!', email_verified=False)
        response = self.client.post('/api/v1/auth/resend-verification/', {
            'email': 'resendme@example.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
