from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class EntitlementAPITest(APITestCase):
    def _qa_user(self, email="qa-test@toolhub.local"):
        return User.objects.create_user(email=email, password="TestPass123!", is_qa_user=True)

    def _normal_user(self, email="normal@example.com"):
        return User.objects.create_user(email=email, password="TestPass123!")

    def test_qa_user_gets_max_entitlement(self):
        qa = self._qa_user()
        self.client.force_authenticate(qa)
        res = self.client.get("/api/v1/subscriptions/entitlements/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data["data"]
        self.assertTrue(data["is_qa_user"])
        self.assertEqual(data["plan_code"], "qa")
        self.assertEqual(data["tier"], "max")
        # The -1 sentinel is the established "unlimited" value (see ratelimit.py).
        self.assertEqual(data["credits"], -1)
        self.assertEqual(data["limits"]["daily_limit"], -1)
        self.assertEqual(data["limits"]["storage_limit"], -1)
        self.assertEqual(data["limits"]["batch_limit"], -1)
        self.assertEqual(data["limits"]["api_limit"], -1)
        self.assertTrue(data["features"]["ai_access"])

    def test_normal_user_unchanged(self):
        normal = self._normal_user()
        self.client.force_authenticate(normal)
        res = self.client.get("/api/v1/subscriptions/entitlements/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data["data"]
        self.assertFalse(data.get("is_qa_user", False))
        self.assertNotEqual(data["plan_code"], "qa")
        # Normal (no-plan) user must NOT inherit the QA unlimited sentinel.
        self.assertNotEqual(data["limits"]["daily_limit"], -1)

    def test_anonymous_gets_free_defaults(self):
        res = self.client.get("/api/v1/subscriptions/entitlements/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data["data"]
        self.assertFalse(data.get("is_qa_user", False))
        self.assertEqual(data["plan_code"], "free")

    def test_qa_flag_exposed_on_profile(self):
        qa = self._qa_user()
        self.client.force_authenticate(qa)
        res = self.client.get("/api/v1/accounts/profile/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["data"]["is_qa_user"])

    def test_normal_flag_false_on_profile(self):
        normal = self._normal_user()
        self.client.force_authenticate(normal)
        res = self.client.get("/api/v1/accounts/profile/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["data"]["is_qa_user"])


class UsageSummaryAPITest(APITestCase):
    def _qa_user(self, email="qa-test@toolhub.local"):
        return User.objects.create_user(email=email, password="TestPass123!", is_qa_user=True)

    def _normal_user(self, email="normal@example.com"):
        return User.objects.create_user(email=email, password="TestPass123!")

    def test_qa_user_usage_reports_unlimited_credits(self):
        qa = self._qa_user()
        self.client.force_authenticate(qa)
        res = self.client.get("/api/v1/ai-workspace/usage/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data["data"]
        self.assertEqual(data["tier"], "max")
        self.assertEqual(data["credits"], -1)
        self.assertEqual(data["daily_limit"], -1)

    def test_normal_user_usage_reports_wallet_balance(self):
        normal = self._normal_user()
        self.client.force_authenticate(normal)
        res = self.client.get("/api/v1/ai-workspace/usage/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data["data"]
        # Normal users keep their real balance/tier; no QA sentinel leaked.
        self.assertNotEqual(data["credits"], -1)
        self.assertNotEqual(data["tier"], "max")
        self.assertNotEqual(data["daily_limit"], -1)
