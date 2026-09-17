import httpx
import pytest
from kif.core.models import ProviderError, ProviderErrorCode
from kif.providers.deepseek import DeepSeekAdapter


def _adapter() -> DeepSeekAdapter:
    return DeepSeekAdapter(api_key="test-key-not-real", base_url="https://example.invalid", model="deepseek-flash")


@pytest.mark.parametrize("status,expected", [(400, ProviderErrorCode.INVALID_REQUEST), (401, ProviderErrorCode.AUTH_ERROR), (402, ProviderErrorCode.QUOTA_EXHAUSTED), (403, ProviderErrorCode.AUTH_ERROR), (408, ProviderErrorCode.TIMEOUT), (429, ProviderErrorCode.RATE_LIMIT), (500, ProviderErrorCode.PROVIDER_DOWN), (503, ProviderErrorCode.PROVIDER_DOWN), (418, ProviderErrorCode.UNKNOWN_PROVIDER_ERROR)])
def test_http_status_normalization(status, expected):
    adapter = _adapter()
    resp = httpx.Response(status, json={"error": {"message": "boom"}}, request=httpx.Request("POST", "https://example.invalid/chat/completions"))
    with pytest.raises(ProviderError) as exc:
        adapter._raise_normalized(resp)
    assert exc.value.code == expected
    assert exc.value.status_code == status


def test_success_status_does_not_raise():
    adapter = _adapter()
    resp = httpx.Response(200, json={"ok": True}, request=httpx.Request("POST", "https://example.invalid/chat/completions"))
    adapter._raise_normalized(resp)


def test_non_json_error_body_falls_back_to_text():
    adapter = _adapter()
    resp = httpx.Response(500, text="<html>internal error</html>", request=httpx.Request("POST", "https://example.invalid/chat/completions"))
    with pytest.raises(ProviderError) as exc:
        adapter._raise_normalized(resp)
    assert exc.value.code == ProviderErrorCode.PROVIDER_DOWN
    assert "internal error" in exc.value.message


def test_missing_api_key_raises_auth_error(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ProviderError) as exc:
        DeepSeekAdapter()
    assert exc.value.code == ProviderErrorCode.AUTH_ERROR
