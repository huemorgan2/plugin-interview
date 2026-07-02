# plugin-interview

Adaptive **knowledge-elicitation interviews** for [Luna](https://github.com/huemorgan/luna).
The agent runs a discovery conversation; the plugin owns the *structure* — a live
coverage map, the transcript, and a publishable markdown brief.

## What you get

- **9 tools** — `interview_start`, `interview_set_topics`, `interview_record_answer`,
  `interview_revise_topics`, `interview_next`, `interview_get`, `interview_brief`,
  `interview_list`, `interview_complete`.
- An **Interviews** section in the **left sidebar** (the work area, not Settings):
  list → coverage rings → per-interview detail (domain understanding, coverage map,
  transcript, brief with copy/download). Served as a full-pane iframe.
- A **first-run greeting**: the first time it loads after install, it hands the
  agent a **muted message** (008.994) — a collapsible `▸ Interview installed` line
  — that prompts the agent to explain what the plugin is and, using what it
  already knows about the owner, suggest 2–3 concrete interviews to fill the gaps
  in its background on them. Fires **once** (persisted flag in
  `plugin_interview_meta`), best-effort and non-blocking, and retries on a later
  boot if no conversation exists yet.

## Owns its own DB tables (SDK enabler E4)

This is the first Luna plugin to own DB tables purely through the SDK:

```python
from luna_sdk import declarative_base, JSONB, UUID
Base = declarative_base()   # its own MetaData — isolated from core
```

Four tables (`plugin_interview_{sessions,topics,turns,meta}`) are created on enable
via `ctx.engine`. No `import luna.*` — only `luna_sdk` + stdlib + SQLAlchemy. Nothing
ever binds to core's metadata, so core migrations and uninstall stay clean.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT © 2026 Hue Morgan
