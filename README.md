# Magicpin Vera AI Bot Challenge

## Architecture

This application consists of two main parts:
1. **FastAPI Backend Bot:** A stateful, robust Python HTTP server mimicking "Vera". It maintains in-memory state of merchants, categories, customers, and triggers, and utilizes a deterministic rule-based composition engine (with optional LLM hooks) to generate context-aware WhatsApp-style messages.
2. **React + Vite Frontend Dashboard:** A modern, clean, light-themed SaaS dashboard designed for manual testing, demoing, and simulating all backend endpoints right from the browser.

### 4-Context Composition Framework

The composer extracts state from four domains:
- **Category:** The business vertical (e.g., dentists, gyms) with tone definitions, research insights, and trends.
- **Merchant:** Specific business info, live offers, and performance metrics.
- **Customer:** (Optional) Customer visit history, preferences.
- **Trigger:** The event causing the bot to fire (e.g., `perf_spike`, `recall_due`).

When `/v1/tick` is called, the composer merges these into a high-converting, hyper-specific action.

## Deployment Options

### Option 1: Simple Deployment on Render/Railway (Recommended)
You can deploy the application as a single Web Service. The FastAPI server automatically serves the built frontend dashboard at the root `/`.

1. **Deploy the repository** to Render or Railway.
2. **Build Command:**
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && npm run build
   ```
   *(Or just `pip install -r requirements.txt` if you only want the backend API).*
3. **Start Command:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```


## Running Locally

### Backend
Make sure you have Python 3.11+ installed.
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```
This automatically loads the `./dataset` JSON files into memory.

### Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```


## How to use the Dashboard

Open `http://localhost:8080` (or your Vite dev server `http://localhost:5173`) in your browser.
1. **Overview:** See system uptime, `/v1/metadata`, and currently loaded context counts.
2. **Context Manager:** Push new context JSON payloads to `/v1/context`. It handles versioning properly (returning `409` for stale payloads).
3. **Tick Simulator:** Enter a trigger ID and run `/v1/tick`. View the beautifully formatted generated message actions (body, cta, rationale, etc).
4. **Reply Simulator:** Simulate incoming merchant/customer messages to `/v1/reply`. Test how it handles positive ("Yes"), negative ("Stop"), auto-replies ("Thank you for contacting"), and questions.

