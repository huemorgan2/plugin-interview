"""The one-time post-install greeting (muted message → explain + suggest interviews).

`on_install` is not wired in the loader, so the plugin greets on the first
`on_load` after install, guarded by a persisted flag. These tests exercise that
once-only logic with the store flag + `ctx.send_muted_message` stubbed — no real
engine or Luna runtime required.
"""

from __future__ import annotations

import types

import pytest

from plugin_interview import (
    _INSTALL_GREETING_NOTE,
    _INSTALL_GREETING_TITLE,
    InterviewPlugin,
)


class _FakeStore:
    def __init__(self) -> None:
        self.greeted = False

    async def was_install_greeted(self) -> bool:
        return self.greeted

    async def mark_install_greeted(self) -> None:
        self.greeted = True


class _FakeCtx:
    def __init__(self, send) -> None:
        self.send_muted_message = send


def _recorder(result):
    calls = []

    async def _send(title, content, **kwargs):
        calls.append({"title": title, "content": content, "kwargs": kwargs})
        return result

    _send.calls = calls
    return _send


def _plugin_with_store():
    plugin = InterviewPlugin()
    plugin._store = _FakeStore()
    return plugin


async def test_greets_once_and_marks_flag():
    send = _recorder({"responded": True})
    plugin = _plugin_with_store()

    sent = await plugin._greet_install_once(_FakeCtx(send))

    assert sent is True
    assert plugin._store.greeted is True
    assert len(send.calls) == 1
    call = send.calls[0]
    assert call["title"] == _INSTALL_GREETING_TITLE
    assert call["kwargs"].get("respond") is True


async def test_does_not_greet_twice():
    send = _recorder({"responded": True})
    plugin = _plugin_with_store()

    assert await plugin._greet_install_once(_FakeCtx(send)) is True
    assert await plugin._greet_install_once(_FakeCtx(send)) is False
    assert len(send.calls) == 1


async def test_retries_when_no_conversation():
    send = _recorder({"error": "no target conversation", "responded": False})
    plugin = _plugin_with_store()

    sent = await plugin._greet_install_once(_FakeCtx(send))

    assert sent is False
    assert plugin._store.greeted is False  # will retry next boot
    assert len(send.calls) == 1


async def test_noop_when_context_lacks_muted_channel():
    plugin = _plugin_with_store()
    ctx = types.SimpleNamespace()  # no send_muted_message

    assert await plugin._greet_install_once(ctx) is False
    assert plugin._store.greeted is False


def test_note_explains_and_suggests_interviews():
    note = _INSTALL_GREETING_NOTE
    assert "interview_start" in note
    assert "suggest" in note.lower()
    # anchored on what the agent already knows about the owner
    assert "know" in note.lower()
