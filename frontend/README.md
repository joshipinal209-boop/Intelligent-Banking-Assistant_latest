# FinCore Intelligent Banking Assistant — Frontend

This is a production-ready, minimal-dependency React + Vite + TypeScript frontend for the FinCore Intelligent Banking Assistant.

## Features
- **Real-time Chat**: Interaction with the LLM orchestration backend.
- **Agent Observability**: Per-agent JSON outputs and provenance tracking (MCP, KG, Retrieval).
- **Latency Monitoring**: Client and server-side latency badges.
- **Risk Indicators**: Scaled risk levels and Human-in-the-loop escalation status.
- **Session Audit**: Slide-out drawer to view the full audit trail for the current session.
- **Scenario Shortcuts**: 8 quick-action buttons for common banking use cases.

## Getting Started

### Prerequisites
- Node.js (v18+)
- npm

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```
The app will be available at `http://localhost:5173`.

### Backend Configuration
By default, the frontend connects to the backend at `http://localhost:8080`.
You can change this at runtime:
1. Click the **Settings** (gear) icon in the header.
2. Update the **API Base URL**.
3. Click **Save Changes**.

## Project Structure
- `src/components`: UI modules (Chat, AgentPanel, Drawer, etc.).
- `src/lib/api.ts`: Configurable API client.
- `src/lib/types.ts`: Shared TypeScript interfaces.
- `src/styles.css`: Dark-themed global CSS.
