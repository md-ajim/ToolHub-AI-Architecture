import json

import pytest
from django.core.cache import cache

from apps.ai_workspace.models import ProviderKind
from apps.ai_workspace.providers import (
    PROVIDER_ADAPTERS,
    get_adapter,
)
from apps.ai_workspace.providers.base import ChatRequest, ChatChunk, ProviderError
from apps.ai_workspace.providers.openai_compatible import (
    DeepSeekAdapter,
    MistralAdapter,
    OpenAIBaseAdapter,
    OpenAIAdapter,
    OpenAICompatibleAdapter,
    QwenAdapter,
    SelfHostedAdapter,
    XAIAdapter,
)
from apps.ai_workspace.providers.anthropic import AnthropicAdapter
from apps.ai_workspace.providers.google import GoogleAdapter
from apps.ai_workspace.providers.huggingface import HuggingFaceAdapter
from apps.ai_workspace.provider_registry import (
    get_all_provider_kinds,
    get_available_providers,
    is_provider_available,
    check_provider_health,
    get_provider_health_snapshot,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def openai_settings(settings):
    settings.OPENAI_API_KEY = "sk-test-openai"


@pytest.fixture
def anthropic_settings(settings):
    settings.ANTHROPIC_API_KEY = "sk-ant-test"


@pytest.fixture
def google_settings(settings):
    settings.GOOGLE_AI_API_KEY = "test-google-key"


class TestProviderKindChoices:
    def test_all_expected_kinds_present(self):
        labels = {choice[0] for choice in ProviderKind.choices}
        for expected in [
            "mock",
            "openai",
            "openai_compatible",
            "google",
            "anthropic",
            "deepseek",
            "qwen",
            "xai",
            "mistral",
            "huggingface",
            "self_hosted",
            "open",
        ]:
            assert expected in labels

    def test_registry_matches_model_choices(self):
        from apps.ai_workspace.providers import PROVIDER_ADAPTERS

        model_kinds = {choice[0] for choice in ProviderKind.choices}
        # Every kind declared in ProviderKind must have an adapter registered.
        for kind in model_kinds:
            assert kind in PROVIDER_ADAPTERS, f"No adapter registered for ProviderKind '{kind}'"


class TestOpenAIBaseAdapter:
    def test_name_not_implemented(self):
        adapter = OpenAIBaseAdapter()
        with pytest.raises(NotImplementedError):
            _ = adapter.name

    def test_not_configured_without_key(self, settings):
        settings.OPENAI_API_KEY = ""
        adapter = OpenAIAdapter()
        assert adapter.is_configured() is False

    def test_configured_with_key(self, openai_settings):
        adapter = OpenAIAdapter()
        assert adapter.is_configured() is True

    def test_openai_uses_correct_env(self, openai_settings):
        adapter = OpenAIAdapter()
        assert adapter._api_key == "sk-test-openai"
        assert adapter._api_base == "https://api.openai.com/v1"
        assert adapter.name == "openai"


class TestOfficialProviderAdapters:
    @pytest.mark.parametrize(
        "cls,env_var,default_base",
        [
            (DeepSeekAdapter, "DEEPSEEK_API_KEY", "https://api.deepseek.com/v1"),
            (QwenAdapter, "QWEN_API_KEY", "https://dashscope.aliyuncs.com/compatible/v1"),
            (XAIAdapter, "XAI_API_KEY", "https://api.x.ai/v1"),
            (MistralAdapter, "MISTRAL_API_KEY", "https://api.mistral.ai/v1"),
        ],
    )
    def test_adapter_config(self, settings, cls, env_var, default_base):
        setattr(settings, env_var, "key-123")
        adapter = cls()
        assert adapter.is_configured() is True
        assert adapter._api_key == "key-123"
        assert adapter._api_base == default_base

    def test_openai_compatible_legacy_env(self, settings):
        settings.AI_WORKSPACE_OPENAI_API_KEY = "legacy-key"
        settings.AI_WORKSPACE_OPENAI_BASE_URL = "https://custom.example.com/v1"
        adapter = OpenAICompatibleAdapter()
        assert adapter.is_configured() is True
        assert adapter._api_key == "legacy-key"
        assert adapter._api_base == "https://custom.example.com/v1"
        assert adapter.name == "openai_compatible"

    def test_self_hosted_adapter(self, settings):
        settings.AI_WORKSPACE_SELF_HOSTED_API_KEY = "sh-key"
        settings.AI_WORKSPACE_SELF_HOSTED_BASE_URL = "https://my-llm.local/v1"
        adapter = SelfHostedAdapter()
        assert adapter.is_configured() is True
        assert adapter.name == "self_hosted"


class TestAnthropicAdapter:
    def test_not_configured(self, settings):
        settings.ANTHROPIC_API_KEY = ""
        adapter = AnthropicAdapter()
        assert adapter.is_configured() is False

    def test_configured(self, anthropic_settings):
        adapter = AnthropicAdapter()
        assert adapter.is_configured() is True

    def test_converts_vision_data_url(self):
        messages = AnthropicAdapter._convert_messages(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "describe"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64,aGVsbG8="
                            },
                        },
                    ],
                }
            ]
        )
        assert messages[0]["content"][1]["source"]["data"] == "aGVsbG8="

    def test_unconfigured_raises_provider_error(self, settings):
        settings.ANTHROPIC_API_KEY = ""
        adapter = AnthropicAdapter()
        request = ChatRequest(messages=[{"role": "user", "content": "hi"}], model="claude-3")
        with pytest.raises(ProviderError) as exc_info:
            list(adapter.stream_chat(request))
        assert exc_info.value.code == "provider_not_configured"


class TestGoogleAdapter:
    def test_not_configured(self, settings):
        settings.GOOGLE_AI_API_KEY = ""
        adapter = GoogleAdapter()
        assert adapter.is_configured() is False

    def test_configured(self, google_settings):
        adapter = GoogleAdapter()
        assert adapter.is_configured() is True

    def test_converts_vision_data_url(self):
        contents = GoogleAdapter._convert_messages(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "describe"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64,aGVsbG8="
                            },
                        },
                    ],
                }
            ]
        )
        assert contents[0]["parts"][1]["inline_data"]["data"] == "aGVsbG8="

    def test_unconfigured_raises_provider_error(self, settings):
        settings.GOOGLE_AI_API_KEY = ""
        adapter = GoogleAdapter()
        request = ChatRequest(messages=[{"role": "user", "content": "hi"}], model="gemini-1.5")
        with pytest.raises(ProviderError) as exc_info:
            list(adapter.stream_chat(request))
        assert exc_info.value.code == "provider_not_configured"


class TestGetAdapter:
    def test_known_provider(self):
        adapter = get_adapter("mock")
        assert adapter.name == "mock"

    def test_unknown_provider_raises(self):
        with pytest.raises(ProviderError):
            get_adapter("nonexistent")


class TestProviderRegistry:
    def test_get_all_provider_kinds_includes_official(self):
        kinds = get_all_provider_kinds()
        assert "openai" in kinds
        assert "anthropic" in kinds
        assert "google" in kinds
        assert "deepseek" in kinds
        assert "qwen" in kinds

    def test_unconfigured_provider_not_available(self, settings):
        settings.ANTHROPIC_API_KEY = ""
        settings.GOOGLE_AI_API_KEY = ""
        settings.OPENAI_API_KEY = ""
        assert is_provider_available("anthropic") is False
        assert is_provider_available("google") is False
        assert is_provider_available("openai") is False

    def test_configured_provider_available(self, openai_settings):
        assert is_provider_available("openai") is True

    def test_get_available_providers_filters(self, settings, openai_settings):
        settings.ANTHROPIC_API_KEY = ""
        available = get_available_providers()
        assert "openai" in available
        assert "anthropic" not in available


class TestProviderHealth:
    def test_unconfigured_provider_health(self, settings):
        settings.ANTHROPIC_API_KEY = ""
        health = check_provider_health("anthropic")
        assert health["provider"] == "anthropic"
        assert health["configured"] is False
        assert health["healthy"] is False
        assert health["status"] == "unconfigured"

    def test_configured_provider_health(self, openai_settings):
        health = check_provider_health("openai")
        assert health["configured"] is True
        assert health["healthy"] is True
        assert health["status"] == "healthy"

    def test_health_is_cached(self, openai_settings):
        first = check_provider_health("openai")
        first["status"] = "degraded"
        cache.set(
            "ai_workspace:provider_health:" + __import__("hashlib").md5(b"openai").hexdigest(),
            first,
            60,
        )
        second = check_provider_health("openai")
        assert second["status"] == "degraded"

    def test_snapshot_includes_all_kinds(self):
        snapshot = get_provider_health_snapshot()
        kinds = {entry["provider"] for entry in snapshot}
        assert "openai" in kinds
        assert "anthropic" in kinds
        assert "google" in kinds


class TestHuggingFaceAdapter:
    def test_not_configured_when_no_token_exists(self, settings):
        settings.HF_API_TOKEN = ""
        settings.HUGGINGFACE_API_KEY = ""
        adapter = HuggingFaceAdapter()
        assert adapter.is_configured() is False

    def test_configured_when_hf_api_token_exists(self, settings):
        settings.HF_API_TOKEN = "dummy-hf-token"
        settings.HUGGINGFACE_API_KEY = ""
        adapter = HuggingFaceAdapter()
        assert adapter.is_configured() is True
        assert adapter._api_key == "dummy-hf-token"

    def test_huggingface_api_key_remains_working_fallback(self, settings):
        settings.HF_API_TOKEN = ""
        settings.HUGGINGFACE_API_KEY = "dummy-fallback-key"
        adapter = HuggingFaceAdapter()
        assert adapter.is_configured() is True
        assert adapter._api_key == "dummy-fallback-key"

    def test_unconfigured_raises_provider_error(self, settings):
        settings.HF_API_TOKEN = ""
        settings.HUGGINGFACE_API_KEY = ""
        adapter = HuggingFaceAdapter()
        request = ChatRequest(messages=[{"role": "user", "content": "hi"}], model="meta-llama/Llama-3.3-70B-Instruct")
        with pytest.raises(ProviderError) as exc_info:
            list(adapter.stream_chat(request))
        assert exc_info.value.code == "provider_not_configured"

    def test_requests_use_router_base_url(self, settings):
        settings.HF_API_TOKEN = "dummy-token"
        settings.AI_WORKSPACE_HF_BASE_URL = "https://router.huggingface.co/v1"
        adapter = HuggingFaceAdapter()
        assert adapter._api_base == "https://router.huggingface.co/v1"
        assert adapter.name == "huggingface"

    def test_custom_router_base_url(self, settings):
        settings.HF_API_TOKEN = "dummy-token"
        settings.AI_WORKSPACE_HF_BASE_URL = "https://custom-router.example.com/v1"
        adapter = HuggingFaceAdapter()
        assert adapter._api_base == "https://custom-router.example.com/v1"

    def test_chat_completion_request_payload_and_headers(self, settings, monkeypatch):
        settings.HF_API_TOKEN = "mock-token-xyz"
        settings.AI_WORKSPACE_HF_BASE_URL = "https://router.huggingface.co/v1"
        adapter = HuggingFaceAdapter()

        recorded = {}

        class DummyResponse:
            status_code = 200
            def iter_lines(self, decode_unicode=True):
                yield "data: " + json.dumps({
                    "choices": [{"delta": {"content": "Hello world"}}],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 2},
                })
                yield "data: [DONE]"
            def close(self):
                recorded["closed"] = True

        def mock_post(url, headers=None, json=None, stream=False, timeout=None):
            recorded["url"] = url
            recorded["headers"] = headers
            recorded["json"] = json
            recorded["stream"] = stream
            recorded["timeout"] = timeout
            return DummyResponse()

        monkeypatch.setattr("requests.post", mock_post)

        request = ChatRequest(
            messages=[{"role": "user", "content": "hi"}],
            model="meta-llama/Llama-3.3-70B-Instruct:groq",
            max_output_tokens=100,
            temperature=0.7,
        )
        chunks = list(adapter.stream_chat(request))

        assert recorded["url"] == "https://router.huggingface.co/v1/chat/completions"
        assert recorded["headers"]["Authorization"] == "Bearer mock-token-xyz"
        assert recorded["headers"]["Content-Type"] == "application/json"
        assert recorded["json"]["model"] == "meta-llama/Llama-3.3-70B-Instruct:groq"
        assert recorded["json"]["max_tokens"] == 100
        assert recorded["json"]["temperature"] == 0.7
        assert recorded["json"]["stream"] is True
        assert recorded["stream"] is True

        assert len(chunks) == 1
        assert chunks[0].text == "Hello world"
        assert chunks[0].input_tokens == 5
        assert chunks[0].output_tokens == 2
        assert recorded.get("closed") is True

    def test_provider_suffixes_preserved(self, settings, monkeypatch):
        settings.HF_API_TOKEN = "token"
        adapter = HuggingFaceAdapter()

        models_tested = []

        class DummyResponse:
            status_code = 200
            def iter_lines(self, decode_unicode=True):
                yield "data: [DONE]"
            def close(self):
                pass

        def mock_post(url, headers=None, json=None, stream=False, timeout=None):
            models_tested.append(json["model"])
            return DummyResponse()

        monkeypatch.setattr("requests.post", mock_post)

        for mid in [
            "meta-llama/Llama-3.3-70B-Instruct",
            "meta-llama/Llama-3.3-70B-Instruct:fastest",
            "meta-llama/Llama-3.3-70B-Instruct:cheapest",
            "meta-llama/Llama-3.3-70B-Instruct:preferred",
            "openai/gpt-oss-120b:groq",
        ]:
            list(adapter.stream_chat(ChatRequest(messages=[{"role": "user", "content": "hi"}], model=mid)))

        assert models_tested == [
            "meta-llama/Llama-3.3-70B-Instruct",
            "meta-llama/Llama-3.3-70B-Instruct:fastest",
            "meta-llama/Llama-3.3-70B-Instruct:cheapest",
            "meta-llama/Llama-3.3-70B-Instruct:preferred",
            "openai/gpt-oss-120b:groq",
        ]

    def test_router_error_converted_to_provider_error(self, settings, monkeypatch):
        settings.HF_API_TOKEN = "dummy-token"
        adapter = HuggingFaceAdapter()

        class DummyErrorResponse:
            status_code = 401
            text = '{"error": "Invalid token"}'
            def close(self):
                pass

        monkeypatch.setattr("requests.post", lambda *args, **kwargs: DummyErrorResponse())

        request = ChatRequest(messages=[{"role": "user", "content": "hi"}], model="test-model")
        with pytest.raises(ProviderError) as exc_info:
            list(adapter.stream_chat(request))
        assert exc_info.value.code == "provider_error"
        assert "401" in exc_info.value.message

    def test_rate_limit_converted_to_rate_limited_error(self, settings, monkeypatch):
        settings.HF_API_TOKEN = "dummy-token"
        adapter = HuggingFaceAdapter()

        class DummyRateLimitResponse:
            status_code = 429
            text = '{"error": "Too Many Requests"}'
            def close(self):
                pass

        monkeypatch.setattr("requests.post", lambda *args, **kwargs: DummyRateLimitResponse())

        request = ChatRequest(messages=[{"role": "user", "content": "hi"}], model="test-model")
        with pytest.raises(ProviderError) as exc_info:
            list(adapter.stream_chat(request))
        assert exc_info.value.code == "rate_limited"
        assert "429" in exc_info.value.message


class TestHuggingFaceVisionInlining:
    def test_relative_image_url_is_inlined_to_data_url(self, tmp_path, settings):
        settings.HF_API_TOKEN = "dummy-token"
        settings.MEDIA_ROOT = str(tmp_path)
        settings.MEDIA_URL = "/media/"

        import base64
        import io

        from PIL import Image

        img = Image.new("RGB", (20, 20), (10, 200, 80))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        p = tmp_path / "img.jpg"
        p.write_bytes(buf.getvalue())

        adapter = HuggingFaceAdapter()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What color?"},
                    {"type": "image_url", "image_url": {"url": "/media/img.jpg"}},
                ],
            }
        ]
        out = adapter._inline_remote_images(messages)
        assert messages != out
        part = out[0]["content"][1]
        assert part["image_url"]["url"].startswith("data:image/jpeg;base64,")
        decoded = base64.b64decode(part["image_url"]["url"].split(",", 1)[1])
        assert len(decoded) > 0

    def test_data_url_and_http_url_pass_through(self, settings):
        settings.HF_API_TOKEN = "dummy-token"
        adapter = HuggingFaceAdapter()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "hi"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,AAAA"}},
                    {"type": "image_url", "image_url": {"url": "https://example.com/a.png"}},
                ],
            }
        ]
        out = adapter._inline_remote_images(messages)
        assert messages == out

    def test_no_content_parts_untouched(self, settings):
        settings.HF_API_TOKEN = "dummy-token"
        adapter = HuggingFaceAdapter()
        messages = [{"role": "user", "content": "plain text"}]
        assert adapter._inline_remote_images(messages) == messages

