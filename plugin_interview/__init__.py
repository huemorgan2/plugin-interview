"""plugin-interview — adaptive knowledge-elicitation interviews.

Drop-in, fully decoupled (008.001). The plugin owns *state and structure*
(coverage map, turns, brief); the agent does the research, judgment, and
conversation. Copying this folder enables it; deleting it removes it cleanly.
No core wiring file is edited to add it.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from luna_sdk import (
    LunaPlugin,
    PluginContext,
    PluginManifest,
    SidebarSection,
)

from .models import ALL_TABLES
from .prompts import CAPABILITY_NOTE
from .store import InterviewStore
from .tools import register_tools

log = logging.getLogger("plugin-interview")

# One-time greeting handed to the agent the first time the plugin loads after
# being installed. `on_install` is not wired in the loader, so we detect "first
# load after install" with a persisted flag (store.was_install_greeted) instead.
_INSTALL_GREETING_TITLE = "Interview installed"
_INSTALL_GREETING_NOTE = (
    "The Interview plugin was just installed. It lets you run an adaptive "
    "knowledge-elicitation interview — you ask the owner one focused question at a "
    "time and it builds a structured coverage map + brief from their answers "
    "(start one with the `interview_start` tool; there's also an Interviews pane "
    "in the left sidebar).\n\n"
    "In a short, friendly message: (1) briefly explain what this plugin is and why "
    "it's useful — a fast way to get what's in the owner's head into a brief you "
    "can act on. (2) Then, using what you ALREADY know about this owner (their "
    "identity, mission, past conversations and memory), suggest 2\u20133 concrete "
    "interviews that would collect the background you're currently missing to serve "
    "them better — name each one specifically (e.g. \u201cyour business & who it's "
    "for\u201d, \u201cyour writing voice\u201d, \u201cthis project's goals & "
    "constraints\u201d) and tie it to what you know about them. (3) Offer to start "
    "one now. Keep it warm and concrete; do not dump a generic feature list."
)


class InterviewPlugin(LunaPlugin):
    manifest = PluginManifest(
        name="plugin-interview",
        shown_name="Interview",
        icon="messages-square",
        image="assets/icon.png",
        version="0.2.0",
        description="Adaptive knowledge-elicitation interviews → structured briefs.",
        category="global",
        license="MIT",
        db_tables=[t.name for t in ALL_TABLES],
        routes_module="routes",
        sidebar_sections=[
            SidebarSection(
                id="interview",
                label="Interviews",
                icon="messages-square",
                sort_order=45,
            ),
        ],
    )

    def __init__(self) -> None:
        self._store: InterviewStore | None = None

    async def on_load(self, ctx: PluginContext) -> None:
        async with ctx.engine.begin() as conn:
            for table in ALL_TABLES:
                await conn.run_sync(table.create, checkfirst=True)
        self._store = InterviewStore(ctx.db_session_factory)
        register_tools(ctx, self._store)
        self._schedule_install_greeting(ctx)
        log.info("plugin-interview loaded (tools=9, tables=%d)", len(ALL_TABLES))

    async def prompt_sections(self) -> list[Any]:
        return [CAPABILITY_NOTE]

    def _schedule_install_greeting(self, ctx: PluginContext) -> None:
        """Fire the one-time post-install greeting without blocking load.

        Runs as a background task so booting/installing returns immediately; any
        failure is swallowed (a greeting must never break plugin load).
        """
        async def _run() -> None:
            try:
                await self._greet_install_once(ctx)
            except Exception:  # noqa: BLE001 — greeting is best-effort
                log.debug("interview.install_greeting_failed", exc_info=True)

        try:
            asyncio.get_running_loop().create_task(_run())  # noqa: RUF006
        except RuntimeError:
            pass

    async def _greet_install_once(self, ctx: PluginContext) -> bool:
        """Send the post-install greeting exactly once. Returns True if sent now.

        Idempotent via a persisted flag. If no conversation exists yet (the muted
        helper returns an ``error``), the flag is left unset so the greeting is
        retried on a later load once the owner has a chat open.
        """
        send = getattr(ctx, "send_muted_message", None)
        if send is None or self._store is None:
            return False
        if await self._store.was_install_greeted():
            return False
        result = await send(
            _INSTALL_GREETING_TITLE, _INSTALL_GREETING_NOTE, respond=True
        )
        if isinstance(result, dict) and result.get("error"):
            return False
        await self._store.mark_install_greeted()
        return True
