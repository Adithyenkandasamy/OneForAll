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
- `GOOGLE_PROJECT_ID` — Google Cloud project id for the sheets service account.
- `GOOGLE_APPLICATION_CREDENTIALS` — absolute path to the service-account JSON key.
- `SHEETS_SPREADSHEET_ID` — the inventory Google Sheet (injected into every sheets call).
- `SHEETS_RANGE` — A1 range of the inventory table, e.g. `Inventory!A1:H1000`.

Platform tables (`users`, `ai_history`, `notifications`, ...) are created against the
working database with:

```bash
uv run python -c "import asyncio; from app.database.session import init_db; asyncio.run(init_db())"
```

### MCP integration notes

MCP servers are declared **one JSON file per service** in
`app/shared/mcp/servers/`; `app/shared/mcp/manager.py` loads every `*.json`
and substitutes `${VAR}` placeholders from the environment. The inventory
agent uses `servers/gsheets.json` → server `gsheets`, which is
[`mcp-gsheets`](https://github.com/freema/mcp-gsheets) (freema), a stdio
server launched via `npx -y mcp-gsheets@latest` with a Google service-account
key. It exposes `sheets_*` tools (`sheets_get_values`, `sheets_append_values`,
`sheets_update_values`, ...) that take a `spreadsheetId` and A1 ranges.

The agent NEVER calls Google Sheets directly: `app/agents/inventory/mcp_tools.py`
exposes a small semantic surface (`read_sheet`, `search_sheet`, `get_row`,
`append_row`, `update_cell`) and translates each call to the real `sheets_*`
tool, injecting `SHEETS_SPREADSHEET_ID` / `SHEETS_RANGE`. Missing credentials
or an unreachable server surface as `MCP_UNAVAILABLE` (503).
