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

## Owns its own DB tables (SDK enabler E4)

This is the first Luna plugin to own DB tables purely through the SDK:

```python
from luna_sdk import declarative_base, JSONB, UUID
Base = declarative_base()   # its own MetaData — isolated from core
```

Three tables (`plugin_interview_{sessions,topics,turns}`) are created on enable via
`ctx.engine`. No `import luna.*` — only `luna_sdk` + stdlib + SQLAlchemy. Nothing ever
binds to core's metadata, so core migrations and uninstall stay clean.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT © 2026 Hue Morgan
