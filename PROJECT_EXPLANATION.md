# Orvixo AI (OneForAll) - Project Explanation

## Overview

**Orvixo AI** is an AI-powered **Manufacturing Intelligence Platform** that transforms traditional Google Sheets-based inventory management into an intelligent assistant. Users ask natural-language questions about factory inventory and get AI-generated analysis, risk detection, and reorder recommendations.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI (async), SQLAlchemy (async ORM) |
| Database | Supabase (PostgreSQL) |
| AI/LLM | Groq API with Llama 3.3 70B Versatile |
| Integration | Model Context Protocol (MCP) for Google Sheets |
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS v4, shadcn/ui |
| Auth | JWT (access + refresh tokens), bcrypt |

---

## Architecture

```
User (Browser)
    │
    ▼
Next.js Frontend (Port 3000)
    │  Axios + JWT Bearer
    ▼
FastAPI Backend (Port 8000, prefix /api/v1)
    │
    ├── Middleware (CORS, RequestID, RateLimit, ErrorHandler)
    │
    ├── API Routes (auth, users, conversations, notifications, history, dashboard)
    │
    ├── Agent Routers (inventory, executive)
    │
    ├── DI Container (composition root)
    │       │
    │       ├── Services → Repositories → SQLAlchemy AsyncSession → Postgres
    │       │
    │       └── InventoryAgent
    │               │
    │               ├── AgentRunner (tool-calling loop)
    │               │       │
    │               │       └── GroqProvider (LLM: Llama 3.3 70B)
    │               │
    │               └── SheetsMcpGateway → MCP Client → MCP Server (stdio subprocess)
    │                                                           │
    │                                                           └── inventory_server.py
    │                                                                   │
    │                                                                   └── gspread → Google Sheets
    │
    └── ExecutiveAgent (direct Groq call, no MCP tools)
```

---

## Core Components

### 1. Inventory Agent (Fully Implemented)

The main agent that analyzes factory inventory from Google Sheets.

**Available MCP Tools (7):**
- `get_material` - Get single material by ID
- `search_materials` - Search across all columns
- `get_supplier_stats` - Materials per supplier
- `get_low_stock` - Materials below reorder point
- `query_inventory` - Flexible filtered queries
- `get_columns` - List column names
- `update_cell` - Update inventory (write-only, operator/admin roles)

**How it works:**
1. User asks a question (e.g., "Which materials are low on stock?")
2. Agent receives the query with user's role permissions
3. LLM decides which tools to call
4. Tools execute via MCP server (spawns Python subprocess)
5. MCP server connects to Google Sheets via gspread
6. Results return to LLM for analysis
7. LLM generates natural language response with risk flags

### 2. Executive Agent (Partially Implemented)

A higher-level "Central Intelligence Orchestrator" that provides cross-domain manufacturing intelligence. Currently makes direct LLM calls without MCP tools.

### 3. Agent Runner (Tool-Calling Loop)

The core orchestration loop:
```
1. Send system prompt + user query to LLM
2. LLM returns tool calls (if needed)
3. Execute tools via MCP gateway
4. Feed results back to LLM
5. Repeat until LLM gives final answer or max iterations reached
```

---

## MCP (Model Context Protocol) Integration

MCP provides a **secure, modular bridge** between AI agents and external data sources.

### How MCP Works:

1. **Config Files** (`app/shared/mcp/servers/*.json`) - Server connection parameters
2. **MCP Manager** - Loads configs, resolves environment variables
3. **MCP Transport** - stdio or HTTP adapters
4. **MCP Client** - Wraps MCP sessions (each in isolated event loop)
5. **MCP Servers** - Standalone Python processes for Google Sheets

### MCP Server Implementation:

```python
# inventory_server.py
- Uses gspread to connect to Google Sheets
- Loads data into pandas DataFrame for analytics
- Provides 7 analytical tools
- The update_cell tool writes directly to sheets
- Invalidates cache after updates
```

### Isolation Strategy:

Each MCP session runs in its own event loop on a worker thread. This contains crashes - a failed MCP call surfaces as a clean 503 error instead of crashing the request.

---

## Authentication & Authorization

### User Roles:
- **viewer** - Read-only access (default)
- **operator** - Can update inventory
- **admin** - Full access + user management

### Auth Flow:
1. **Register** → Creates user with `viewer` role
2. **Login** → Returns access token (60min) + refresh token (7 days)
3. **Request** → JWT in `Authorization: Bearer` header
4. **Refresh** → Exchange refresh token for new access token
5. **Logout** → Revoke refresh token

### Role-Based Access:
- Viewer: Can ask questions, search inventory
- Operator: Can also update inventory cells
- Admin: Can manage users + all operator permissions

---

## Database Models

| Model | Purpose |
|-------|---------|
| User | Auth identity, role, profile |
| RefreshToken | Token rotation, revocation |
| Conversation | Chat sessions |
| Message | Chat history |
| AIHistory | Analysis audit trail |
| Notification | User alerts |
| Setting | App configuration |
| AuditLog | Action tracking |

---

## API Endpoints

### Auth:
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Get tokens
- `POST /api/v1/auth/refresh` - Refresh tokens
- `POST /api/v1/auth/logout` - Revoke token
- `GET /api/v1/auth/me` - Current user

### Inventory Agent:
- `POST /api/v1/agents/inventory/chat` - Ask AI question
- `GET /api/v1/agents/inventory/search` - Search inventory
- `POST /api/v1/agents/inventory/update` - Update cell (operator/admin)

### Executive Agent:
- `POST /api/v1/agents/executive/chat` - Ask central AI

### Admin:
- `GET /api/v1/users` - List users (admin)
- `PATCH /api/v1/users/{id}` - Update user (admin)

---

## Frontend Pages

| Page | Status | Description |
|------|--------|-------------|
| Dashboard | ✅ | Enterprise overview, metrics, charts |
| Login | ✅ | Email/password authentication |
| Central AI | ✅ | Chat interface for executive agent |
| Inventory | 🔲 | Stub (uses API directly) |
| Plants | 🔲 | Stub |
| Machines | 🔲 | Stub |
| Monitoring | 🔲 | Stub |
| Maintenance | 🔲 | Stub |
| Analytics | 🔲 | Stub |
| Team | 🔲 | Stub |
| Settings | 🔲 | Stub |

---

## Data Flow Example

**User asks: "Which materials are below minimum stock?"**

```
1. Frontend → POST /api/v1/agents/inventory/chat
   Body: {"query": "Which materials are below minimum stock?"}

2. FastAPI → Authenticate JWT → Fetch User → Check role

3. InventoryService.answer()
   → Creates AgentContext(user_id, role, can_write=False)
   → Calls InventoryAgent.run(query, ctx)

4. InventoryAgent.run()
   → Filters tools: READ_TOOLS (no update_cell)
   → Fetches tool schemas from MCP server
   → Builds AgentRunner with GroqProvider

5. AgentRunner.run()
   → Messages: [system_prompt, user_query]
   → Calls GroqProvider.complete(messages, tools)
   → Groq returns: tool_calls: [{name: "get_low_stock", arguments: {}}]
   → Calls execute_tool("get_low_stock", {})
     → MCP Client spawns subprocess
     → inventory_server loads Google Sheet
     → Filters: qty <= reorder_point
     → Returns JSON results
   → Result appended to messages
   → Calls Groq again with tool result
   → Groq returns final text answer

6. Agent extracts risk_flags, saves to AIHistory

7. FastAPI returns response to frontend

8. Frontend displays AI analysis
```

---

## Key Design Patterns

1. **Hexagonal Architecture** - Agents depend on ports (interfaces), not implementations
2. **Dependency Injection** - All collaborators injected via DI Container
3. **Strategy Pattern** - LLM provider and MCP transport are swappable
4. **Repository Pattern** - Generic BaseRepository with type-safe entity access
5. **Event-Driven** - Domain events + in-process event bus (for future microservices)
6. **MCP Isolation** - Each session in own event loop (contains crashes)
7. **RBAC** - Three-tier roles with tool allow-list filtering

---

## Configuration

All settings from `.env` file:

| Category | Key Settings |
|----------|--------------|
| App | `app_name`, `app_env`, `debug`, `cors_origins` |
| Auth | `secret_key`, `access_token_expire_minutes` (60) |
| Database | `database_url`, `supabase_url` |
| LLM | `GROQ_API_KEY_INVENTORY`, `groq_model`, `llm_max_iterations` (10) |
| Sheets | `SHEETS_SPREADSHEET_ID`, `GOOGLE_APPLICATION_CREDENTIALS` |

---

## Summary

Orvixo AI is a full-stack manufacturing intelligence platform that:

1. **Connects to Google Sheets** via MCP protocol
2. **Uses LLM (Llama 3.3)** for natural language understanding
3. **Provides role-based access** (viewer/operator/admin)
4. **Supports read + write operations** (with proper permissions)
5. **Maintains audit trail** of all AI interactions
6. **Extensible architecture** for future agents (supply chain, maintenance, etc.)

The MCP integration allows secure, modular communication between AI agents and external data sources, while the clean architecture makes it easy to add new agents or swap LLM providers.
