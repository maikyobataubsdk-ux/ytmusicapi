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
