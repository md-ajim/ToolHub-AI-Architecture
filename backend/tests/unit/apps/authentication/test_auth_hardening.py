"""Phase B auth hardening: logout blacklist, throttles, OAuth gates, reset."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="hard@example.com", password="StrongPass123!")


def _client(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    return client


@pytest.mark.django_db
class TestLogoutBlacklist:
    def test_logout_blacklists_refresh_token(self, user):
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res = client.post("/api/v1/auth/logout/", {"refresh": str(refresh)}, format="json")
        assert res.status_code == 200
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

        assert BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists()

    def test_logout_requires_auth(self):
        res = APIClient().post("/api/v1/auth/logout/", {}, format="json")
        assert res.status_code in (401, 403)

    def test_logout_without_token_still_succeeds(self, user):
        res = _client(user).post("/api/v1/auth/logout/", {}, format="json")
        assert res.status_code == 200


@pytest.mark.django_db
class TestPasswordResetInvalidatesSessions:
    def test_reset_blacklists_outstanding_tokens(self, user):
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

        from apps.authentication.services import process_reset_password

        refresh = RefreshToken.for_user(user)
        jti = refresh["jti"]
        assert not BlacklistedToken.objects.filter(token__jti=jti).exists()

        token_generator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        assert process_reset_password(uid, token, "BrandNewPass123!") is True
        assert BlacklistedToken.objects.filter(token__jti=jti).exists()

        user.refresh_from_db()
        assert user.check_password("BrandNewPass123!")


@pytest.mark.django_db
class TestAuthThrottlesConfigured:
    @pytest.mark.parametrize(
        "view_path,scope",
        [
            ("apps.authentication.views.RegisterView", "auth_register"),
            ("apps.authentication.views.CustomTokenObtainPairView", "auth_login"),
            ("apps.authentication.views.ForgotPasswordView", "auth_password"),
            ("apps.authentication.views.ResetPasswordView", "auth_password"),
            ("apps.authentication.views.GoogleLoginView", "auth_oauth"),
            ("apps.authentication.views.GitHubLoginView", "auth_oauth"),
        ],
    )
    def test_scoped_throttle_present(self, view_path, scope):
        from django.utils.module_loading import import_string

        view = import_string(view_path)
        assert view.throttle_scope == scope
        assert len(view.throttle_classes) > 0

    def test_forgot_password_trips_after_burst(self):
        import random

        from rest_framework.test import APIClient

        # 10/hour scope: 11 rapid anonymous posts → 429 on the last.
        # Random source IP per run: throttle buckets persist in cache
        # across runs, so a fixed IP would inherit other runs' hits.
        ip = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        statuses = []
        for _ in range(11):
            res = APIClient().post(
                "/api/v1/auth/forgot-password/",
                {"email": "nobody@example.com"},
                format="json",
                REMOTE_ADDR=ip,
            )
            statuses.append(res.status_code)
        assert statuses[-1] == 429
        assert all(s == 200 for s in statuses[:-1])


@pytest.mark.django_db
class TestGitHubGetRemoved:
    def test_get_code_endpoint_gone(self):
        res = _client().get("/api/v1/auth/github/?code=abc123")
        assert res.status_code == 405


@pytest.mark.django_db
class TestGoogleTokenVerification:
    def _patch_google(self, monkeypatch, tokeninfo=None, userinfo=None):
        import requests as req_module

        class DummyResp:
            def __init__(self, status_code, payload):
                self.status_code = status_code
                self._payload = payload
                self.text = str(payload)

            def json(self):
                return self._payload

        def fake_get(url, **kwargs):
            if "tokeninfo" in url:
                return DummyResp(200, tokeninfo or {})
            return DummyResp(200, userinfo or {})

        monkeypatch.setattr(req_module, "get", fake_get)

    def test_wrong_audience_rejected(self, monkeypatch, settings):
        from apps.authentication.services import process_google_login

        settings.GOOGLE_CLIENT_ID = "test-client-id"
        self._patch_google(
            monkeypatch,
            tokeninfo={"aud": "other-app", "iss": "accounts.google.com", "exp": 9999999999,
                       "email": "a@b.com"},
        )
        assert process_google_login(id_token="tok") is None

    def test_wrong_issuer_rejected(self, monkeypatch):
        from apps.authentication.services import process_google_login

        self._patch_google(
            monkeypatch,
            tokeninfo={"aud": "", "iss": "evil.com", "exp": 9999999999, "email": "a@b.com"},
        )
        # No client id configured in test env → aud skipped, issuer must fail.
        assert process_google_login(id_token="tok") is None

    def test_expired_token_rejected(self, monkeypatch):
        from apps.authentication.services import process_google_login

        self._patch_google(
            monkeypatch,
            tokeninfo={"aud": "", "iss": "accounts.google.com", "exp": 1, "email": "a@b.com"},
        )
        assert process_google_login(id_token="tok") is None

    def test_code_exchange_requires_client_id(self, settings):
        from apps.authentication.services import process_google_login

        settings.GOOGLE_CLIENT_ID = ""
        settings.GOOGLE_CLIENT_SECRET = ""
        assert process_google_login(code="some-code") is None
