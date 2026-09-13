from app.services import cqc_entitlements


def test_unconfigured_cqc_lookup_fails_closed(monkeypatch):
    class Settings:
        cqc_entitlement_api_url = ""
        cqc_entitlement_shared_secret = ""
        cqc_entitlement_timeout_seconds = 3.0

    monkeypatch.setattr(cqc_entitlements, "get_settings", lambda: Settings())
    assert cqc_entitlements.cqc_entitlements_for_email("member@example.com") == {
        "products": [], "active": False, "source": "not_configured"
    }


def test_cqc_max_expands_to_rulemirror_pro(monkeypatch):
    class Settings:
        cqc_entitlement_api_url = "https://oryntraai.com"
        cqc_entitlement_shared_secret = "a" * 48
        cqc_entitlement_timeout_seconds = 3.0

    class Response:
        def read(self):
            return b'{"products":["cqc_max","oryntra_pro","rulemirror_pro"],"active":true,"expires_at":null}'

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(cqc_entitlements, "get_settings", lambda: Settings())
    monkeypatch.setattr(cqc_entitlements.urllib.request, "urlopen", lambda *_args, **_kwargs: Response())
    result = cqc_entitlements.cqc_entitlements_for_email("member@example.com")
    assert result["rulemirror_pro"] is True
    assert result["products"] == ["cqc_max", "oryntra_pro", "rulemirror_pro"]
