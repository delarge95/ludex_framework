# ARA Game Design Studio - Walkthrough

## Overview
This walkthrough guides you through running the new **Interactive UI** for the ARA Game Design Studio. The system consists of a React frontend (Next.js) and a FastAPI backend (Python) communicating via WebSockets.

## Prerequisites
- Node.js & npm
- Python 3.12+
- IGDB API Credentials (in `.env`)

## 1. Start the Backend
The backend runs the LangGraph agents and exposes the API.

1. Open a terminal in the project root (`d:\Downloads\TRABAJO_DE_GRADO\ara_framework`).
2. Activate your virtual environment (if applicable).
3. Run the server:
   ```bash
   python api/server.py
   ```
   *You should see: `Uvicorn running on http://0.0.0.0:8000`*

## 2. Start the Frontend
The frontend provides the interactive dashboard.

1. Open a **new** terminal.
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *You should see: `Ready in Xms` and `Local: http://localhost:3000`*

## 3. Using the Studio
1. Open your browser to [http://localhost:3000](http://localhost:3000).
2. You will see the **ARA Game Studio** dashboard.
3. Enter a game concept in the text area (e.g., *"A survival horror game set in a submerged underwater city"*).
4. Click **Start Production**.

## 4. Verification Checklist
- [ ] **Agent Status**: Watch the "The Studio" panel. Agents should cycle from "Idle" to "Working" (blue spinner) to "Done" (green check) sequentially.
  - Market Analyst -> Mechanics Designer -> System Designer -> Producer -> GDDWriter
- [ ] **Real-time Updates**: The console logs in the browser should show WebSocket messages (`agent_update`).
- [ ] **GDD Generation**: Once the process finishes, the "Game Design Document" panel on the right will populate with the full Markdown report.

## Troubleshooting
- **WebSocket Error**: Ensure the backend is running on port 8000.
- **IGDB Error**: Check your `.env` file for valid `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET`.
- **Missing Dependencies**: Run `pip install -r requirements.txt` in root and `npm install` in `frontend/`.
