# BMC Control-M UI

Serves the BMC Control-M landing page and embedded chat widget from `public/`.

## Quick start

```bash
npm install
npm start
```

Open **http://localhost:3000**

Same commands on Windows, macOS, and Linux.

## Chat widget

The widget posts to **`/api/chat`** on the UI server (port 3000), which proxies to the Python agent on **http://127.0.0.1:5001** by default.

In a **second terminal**, from the repo root:

```bash
npm run install:agent
npm run start:agent
```

Each message uses `api_registry.yaml` → `tool_generator.py` → BMC APIs.

## Files

```
api/
├── index.js              ← Express static server
├── public/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── chatbot-widget.js
└── src/middleware/
```
