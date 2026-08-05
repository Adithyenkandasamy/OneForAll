# OneForAll Backend

AI-first Manufacturing Intelligence Platform — modular monolith.

- **Application Layer** (`app/`): auth, API, users, notifications, conversations, history, logging, email. No business AI.
- **AI Layer** (`app/agents/`): one isolated package per business AI agent (inventory first).
- **Shared Kernel** (`app/shared/`): the only code agents may import — LLM provider, MCP client/manager, agent runner, event bus.
- **Data ownership**: Google Sheets is the source of truth for inventory (accessed ONLY via MCP). Supabase stores only platform-owned data.

## Layout

```
app/
├── api/          HTTP contracts (thin)
├── core/         config, DI container, security, exceptions, logging, events
├── database/     engine / session / supabase client factories
├── models/       SQLAlchemy ORM (platform tables)
├── schemas/      Pydantic v2 DTOs
├── services/     application use-cases
├── repositories/ data access (the only place Supabase is touched)
├── middleware/   auth, request-id, rate-limit, error handler
├── utils/        pure helpers
├── shared/       LLM, MCP, agent runner, event bus, Result types
├── agents/       AI agents (inventory, procurement, planning, ...)
└── prompts/      shared prompt templates
```

## Run (once implemented)

```bash
uv sync
uv run uvicorn app.main:app --reload
```
