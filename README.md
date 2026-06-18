# BMC Control-M + TinyLlama

BMC automation assistant powered by a local TinyLlama model. API definitions live in `agent/api_registry.yaml`; the chat UI is in `api/public/`.

Works on **Windows**, **macOS**, and **Linux** (Node.js + Python 3 required).

## Prerequisites

| Tool | Windows | macOS / Linux |
|------|---------|----------------|
| Node.js | [nodejs.org](https://nodejs.org) | same, or Homebrew |
| Python 3 | [python.org](https://www.python.org/downloads/) — check **“Add python.exe to PATH”** | `python3` (often preinstalled or via Homebrew) |

## Quick start

From the **project root** (this repo):

### 1. One-time setup

```bash
npm run setup
```

Copy and edit BMC credentials:

```bash
# macOS / Linux
cp agent/.env.example agent/.env

# Windows (Command Prompt or PowerShell)
copy agent\.env.example agent\.env
```

Set `AUTOMATION_USER` and `AUTOMATION_PASS` in `agent/.env` (see `agent/.env.example`).

### 2. Start integrated (UI + agent, recommended)

One command starts both services so the chat widget, intent registry, and API registry work end-to-end:

```bash
npm start
```

Equivalent:

```bash
npm run dev
```

| Service | URL | Role |
|---------|-----|------|
| UI | http://localhost:3000 | Landing page + chat (proxies to agent) |
| Agent | http://localhost:5001/api/chat | TinyLlama + `intent_registry.yaml` + `api_registry.yaml` |

Open **http://localhost:3000**, use the chat widget. Messages go: **UI → `/api/chat` proxy → agent → BMC APIs**.

Press **Ctrl+C** once to stop both processes.

First integrated start may download TinyLlama (~2.2 GB).

**Full integrated flow (copy-paste):**

```bash
cd /path/to/BMC_Integration-top-level-registry
npm run setup
cp agent/.env.example agent/.env   # Windows: copy agent\.env.example agent\.env
# edit agent/.env with BMC credentials
npm start
```

### Or run separately (two terminals)

**Terminal 1 — UI:** `npm run start:api` → http://localhost:3000  

**Terminal 2 — Agent:** `npm run start:agent` → http://localhost:5001/api/chat  

Terminal-only chat (no browser): `npm run start:agent:cli`

## Windows notes

- Use **Command Prompt**, **PowerShell**, or **Windows Terminal** — same `npm` commands as above.
- If `python` is not found, reinstall Python and enable **Add to PATH**, or use the **py** launcher: `py -3 -m venv agent\.venv`
- Do not paste lines that start with `#` from docs; those are comments only.

## macOS / Linux notes

- Use `npm` scripts above (they pick `.venv/bin/python` or `.venv\Scripts\python.exe` automatically).
- If global `pip` is blocked, `npm run install:agent` still works — it uses a project virtual env.
- **Port 5000 in use?** macOS AirPlay Receiver uses it. The agent defaults to **5001**. Override with `AGENT_PORT=5002 npm run start:agent` and `AGENT_URL=http://127.0.0.1:5002 npm run start:api` on the UI.

## Project layout

| Path | Purpose |
|------|---------|
| `api/public/` | BMC landing page + chat widget |
| `api/index.js` | Static UI server |
| `scripts/` | Cross-platform install/start helpers |
| `agent/api_registry.yaml` | BMC API registry (single source of truth) |
| `agent/server.py` | HTTP API for the chat widget |
| `agent/agent.py` | Conversational agent CLI |
| `agent/tool_generator.py` | Registry → LangChain tools |
