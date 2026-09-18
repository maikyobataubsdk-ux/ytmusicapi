import json

import pytest

from cloudflare.src.index import get_yt_instance, on_fetch


class MockRequest:
    def __init__(self, url, method="GET"):
        self.url = url
        self.method = method


class MockEnv:
    def __init__(self, auth=None):
        if auth:
            self.YT_AUTH = auth


@pytest.mark.asyncio
async def test_worker_options():
    req = MockRequest("https://worker.dev/", method="OPTIONS")
    res = await on_fetch(req, MockEnv())
    assert res.status == 204


@pytest.mark.asyncio
async def test_worker_root():
    req = MockRequest("https://worker.dev/")
    res = await on_fetch(req, MockEnv())
    assert res.status == 200
    data = json.loads(res.body)
    assert data["status"] == "ok"
    assert "/search?q=query[&filter=songs|videos|albums|artists|playlists]" in data["endpoints"]


@pytest.mark.asyncio
async def test_worker_search_missing_q():
    req = MockRequest("https://worker.dev/search")
    res = await on_fetch(req, MockEnv())
    assert res.status == 400
    data = json.loads(res.body)
    assert "error" in data


@pytest.mark.asyncio
async def test_worker_unknown_route():
    req = MockRequest("https://worker.dev/unknown")
    res = await on_fetch(req, MockEnv())
    assert res.status == 404
    data = json.loads(res.body)
    assert data["error"] == "Endpoint not found"


def test_get_yt_instance_auth_json():
    auth_str = '{"authorization": "Bearer ya29.test_token", "user-agent": "Mozilla/5.0"}'
    inst = get_yt_instance(auth_str)
    assert inst is not None


def test_get_yt_instance_undefined_auth():
    inst = get_yt_instance("undefined")
    assert inst is not None


@pytest.mark.asyncio
async def test_worker_env_undefined():
    req = MockRequest("https://worker.dev/")
    env = MockEnv(auth="undefined")
    res = await on_fetch(req, env)
    assert res.status == 200


def test_cert_verify_default_non_existent_path(monkeypatch):
    import cloudflare.src.requests.adapters as adapters
    from cloudflare.src.requests.adapters import HTTPAdapter

    class MockConn:
        cert_reqs = None
        ca_certs = None
        ca_cert_dir = None

    adapter = HTTPAdapter()
    conn = MockConn()

    # Mock DEFAULT_CA_BUNDLE_PATH to a path that does not exist on disk
    monkeypatch.setattr(adapters, "DEFAULT_CA_BUNDLE_PATH", "/session/metadata/certifi/cacert.pem")

    # cert_verify with verify=True when default CA path doesn't exist should keep CERT_REQUIRED
    adapter.cert_verify(conn, "https://example.com", verify=True, cert=None)
    assert conn.cert_reqs == "CERT_REQUIRED"
    assert conn.ca_certs is None
    assert conn.ca_cert_dir is None


def test_cert_verify_custom_non_existent_path():
    from cloudflare.src.requests.adapters import HTTPAdapter

    class MockConn:
        cert_reqs = None
        ca_certs = None
        ca_cert_dir = None

    adapter = HTTPAdapter()
    conn = MockConn()

    # cert_verify with explicit custom string path that doesn't exist should raise OSError
    with pytest.raises(OSError, match="Could not find a suitable TLS CA certificate bundle"):
        adapter.cert_verify(conn, "https://example.com", verify="/nonexistent/custom/ca.pem", cert=None)


def test_pyodide_http_should_patch_without_xmlhttprequest(monkeypatch):
    import sys
    import types
    import cloudflare.src.pyodide_http as pyodide_http

    class MockJSModule:
        def __getattr__(self, name):
            raise AttributeError(name)

    monkeypatch.setitem(sys.modules, "js", MockJSModule())
    assert pyodide_http.should_patch() is False


def test_urllib3_send_request_without_xmlhttprequest(monkeypatch):
    import sys
    import types

    class MockJSModule:
        def __getattr__(self, name):
            raise AttributeError(name)

    monkeypatch.setitem(sys.modules, "js", MockJSModule())

    import cloudflare.src.urllib3.contrib.emscripten.fetch as fetch_mod

    called_jspi = []

    def mock_send_jspi_request(req, streaming):
        called_jspi.append((req, streaming))
        return fetch_mod.EmscriptenResponse(status_code=200, headers={}, body=b"ok", request=req)

    monkeypatch.setattr(fetch_mod, "send_jspi_request", mock_send_jspi_request)

    dummy_req = fetch_mod.EmscriptenRequest("GET", "https://example.com")
    resp = fetch_mod.send_request(dummy_req)
    assert resp.status_code == 200
    assert len(called_jspi) == 1
