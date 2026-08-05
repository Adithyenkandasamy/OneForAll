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

## Run

```bash
cp .env.example .env   # then fill in secrets
uv sync
uv run uvicorn app.main:app --reload
```

### Environment

- `SUPABASE_URL` — your Supabase **Postgres DSN** (canonical; also derives the REST URL).
- `DATABASE_URL` — SQLAlchemy async DSN. Optional; when unset `SUPABASE_URL` is used.
  Supabase's direct `db.<ref>.supabase.co` host is IPv6-only — from IPv4-only networks
  use the session pooler, e.g. `postgresql+asyncpg://postgres.<ref>:<pwd>@aws-0-<region>.pooler.supabase.com:5432/postgres`.
- `SMITHIRY_AI` — Smithery API key.
- `SMITHIRY_SPACE` — full Smithery toolbox URL, e.g. `https://mcp.smithery.ai/<space>`.

Platform tables (`users`, `ai_history`, `notifications`, ...) are created against the
working database with:

```bash
uv run python -c "import asyncio; from app.database.session import init_db; asyncio.run(init_db())"
```

### MCP integration notes

The Smithery endpoint (`app/shared/mcp/servers.json` → server `toolbox`) is a **toolbox**
runtime: Google Sheets must be connected and authorized there first
(`get_toolbox_status` reports `auth_required` with a `setupUrl`). Once authorized, sheets
tools are reachable via `search_toolbox` / `execute`; the inventory agent's tool gateway
(`app/agents/inventory/mcp_tools.py`) filters the live tool list accordingly.
