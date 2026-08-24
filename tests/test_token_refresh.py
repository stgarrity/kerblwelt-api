"""Offline regression tests for the token-refresh / anti-storm behaviour.

These tests prove that:
  * an expired access token (HTTP 401) triggers exactly one throttled refresh
    and a single retry - never a request storm;
  * a failed refresh surfaces as ``TokenExpiredError`` (so the HA coordinator
    triggers a re-auth) instead of looping;
  * refresh attempts are throttled to at most one per ``_MIN_REFRESH_INTERVAL``.

A hard socket block guarantees no request ever reaches the live Kerbl API.
"""

import socket

import pytest

from kerblwelt_api.auth import AuthManager
from kerblwelt_api.client import KerblweltClient
from kerblwelt_api.exceptions import APIError, TokenExpiredError, TokenRefreshError


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    """Fail loudly if any test tries to open a real socket."""

    def _boom(*args, **kwargs):
        raise AssertionError("network access attempted during offline test")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket.socket, "connect_ex", _boom)


class FakeResponse:
    """Minimal async-context-manager stand-in for an aiohttp response."""

    def __init__(self, status, json_data=None, text_data=""):
        self.status = status
        self._json = json_data if json_data is not None else {}
        self._text = text_data

    async def json(self):
        return self._json

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeSession:
    """Records calls and returns queued responses without any I/O."""

    def __init__(self):
        self.request_calls = []
        self.post_calls = []
        self.post_payloads = []
        self.request_responses = []
        self.refresh_responses = []

    def request(self, method, url, **kwargs):
        self.request_calls.append((method, url))
        assert self.request_responses, f"unexpected request: {method} {url}"
        return self.request_responses.pop(0)

    def post(self, url, **kwargs):
        self.post_calls.append(url)
        self.post_payloads.append(kwargs.get("json"))
        assert "/auth/refresh" in url, f"unexpected post: {url}"
        assert self.refresh_responses, "unexpected refresh post"
        return self.refresh_responses.pop(0)


async def _make_client(session):
    client = KerblweltClient(session=session)
    # Emulate an authenticated context manager without opening a session.
    client._auth = AuthManager(session)
    client._auth.set_tokens("old-access", "refresh-token")
    return client


async def test_401_triggers_single_refresh_and_retry():
    """A 401 refreshes once and retries once, then succeeds."""
    session = FakeSession()
    session.request_responses = [
        FakeResponse(401, text_data="expired"),
        FakeResponse(200, json_data={"ok": True}),
    ]
    session.refresh_responses = [
        FakeResponse(201, json_data={"accessToken": "new-access", "refreshToken": "new-refresh"}),
    ]

    client = await _make_client(session)
    data = await client._request("GET", "/user")

    assert data == {"ok": True}
    assert len(session.request_calls) == 2  # original + one retry, no storm
    assert len(session.post_calls) == 1  # exactly one refresh
    assert client._auth.access_token == "new-access"


async def test_failed_refresh_raises_token_expired():
    """If the refresh itself is rejected, surface TokenExpiredError (no loop)."""
    session = FakeSession()
    session.request_responses = [FakeResponse(401, text_data="expired")]
    session.refresh_responses = [FakeResponse(401, text_data="refresh expired")]

    client = await _make_client(session)
    with pytest.raises(TokenExpiredError):
        await client._request("GET", "/user")

    assert len(session.request_calls) == 1  # no retry after failed refresh
    assert len(session.post_calls) == 1  # single refresh attempt


async def test_no_refresh_when_disallowed():
    """The retry itself must not attempt another refresh (breaks any loop)."""
    session = FakeSession()
    session.request_responses = [FakeResponse(401, text_data="still 401")]

    client = await _make_client(session)
    with pytest.raises(APIError) as excinfo:
        await client._request("GET", "/user", _allow_refresh=False)

    assert excinfo.value.status_code == 401
    assert len(session.request_calls) == 1
    assert len(session.post_calls) == 0  # never refreshed


async def test_refresh_payload_includes_access_token():
    """Regression: /auth/refresh requires BOTH accessToken and refreshToken.

    Sending only refreshToken returns 400 "accessToken must be a string", which
    previously took the integration offline until a full restart.
    """
    session = FakeSession()
    session.refresh_responses = [
        FakeResponse(201, json_data={"accessToken": "a2", "refreshToken": "r2"}),
    ]

    auth = AuthManager(session)
    auth.set_tokens("expired-access", "refresh-token")

    await auth.refresh_access_token()

    assert session.post_payloads == [
        {"accessToken": "expired-access", "refreshToken": "refresh-token"}
    ]


async def test_refresh_is_throttled():
    """Two refreshes inside the throttle window: the second is rejected."""
    session = FakeSession()
    session.refresh_responses = [
        FakeResponse(201, json_data={"accessToken": "a2", "refreshToken": "r2"}),
    ]

    auth = AuthManager(session)
    auth.set_tokens("a1", "r1")

    await auth.refresh_access_token()
    assert len(session.post_calls) == 1

    with pytest.raises(TokenRefreshError):
        await auth.refresh_access_token()
    assert len(session.post_calls) == 1  # throttled: no second network call
