import structlog
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from graphs.game_design_graph import create_game_design_graph
from core.state import GameDesignState
from api.metrics_router import router as metrics_router
from config.settings import settings

logger = structlog.get_logger(__name__)

app = FastAPI(title="LUDEX Studio API")

# Include routers
app.include_router(metrics_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("websocket_send_failed", error=str(e))

manager = ConnectionManager()

# Request Model
class GameRequest(BaseModel):
    concept: str
    genre: str = "Unknown"

# Graph Runner
async def run_graph_background(concept: str, genre: str):
    """Runs the LangGraph workflow and broadcasts updates."""
    try:
        logger.info("starting_graph_execution", concept=concept)
        
        # Notify start
        await manager.broadcast({
            "type": "status",
            "agent": "system",
            "status": "started",
            "message": f"Starting analysis for: {concept}"
        })

        graph = create_game_design_graph()
        
        initial_state = GameDesignState(
            concept=concept,
            genre=genre,
            market_analysis=None,
            mechanics=[],
            technical_stack=None,
            production_plan=None,
            gdd_content={},
            messages=[],
            current_step="start",
            errors=[]
        )

        # Stream events using astream_events for granular transparency
        # version="v1" is standard for LangGraph
        async for event in graph.astream_events(initial_state, version="v1"):
            kind = event["event"]
            
            # 1. Handle Tool Execution Events (Real-time Transparency)
            if kind == "on_tool_start":
                await manager.broadcast({
                    "type": "tool_call_started",
                    "agent": event.get("metadata", {}).get("langgraph_node", "unknown"),
                    "tool": event["name"],
                    "args": event["data"].get("input")
                })
                logger.info("tool_started", tool=event["name"])
                
            elif kind == "on_tool_end":
                await manager.broadcast({
                    "type": "tool_call_completed",
                    "agent": event.get("metadata", {}).get("langgraph_node", "unknown"),
                    "tool": event["name"],
                    "result": str(event["data"].get("output"))[:200] + "..." # Truncate for UI
                })
                logger.info("tool_ended", tool=event["name"])

            # 2. Handle Node Completion (State Updates)
            elif kind == "on_chain_end":
                # We only care about the top-level node completion, which usually matches the node name
                node_name = event.get("metadata", {}).get("langgraph_node")
                if node_name and node_name != "__start__":
                    output = event["data"].get("output")
                    if isinstance(output, dict): # Ensure it's a state update
                        await manager.broadcast({
                            "type": "agent_update",
                            "agent": node_name,
                            "status": "done",
                            "data": output
                        })
                        
                        # If GDD is ready, send it
                        if "gdd_content" in output:
                            await manager.broadcast({
                                "type": "gdd_update",
                                "markdown": output["gdd_content"].get("full_doc", "")
                            })

        # Notify completion
        await manager.broadcast({
            "type": "status",
            "agent": "system",
            "status": "completed",
            "message": "Game Design Document generated successfully."
        })

    except Exception as e:
        logger.error("graph_execution_failed", error=str(e))
        await manager.broadcast({
            "type": "error",
            "message": str(e)
        })

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "LUDEX Game Design API"}

@app.post("/start")
async def start_generation(request: GameRequest, background_tasks: BackgroundTasks):
    """Starts the game design generation process."""
    background_tasks.add_task(run_graph_background, request.concept, request.genre)
    return {"status": "started", "message": "Generation queued"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Listen for client messages
            message = await websocket.receive_json()
            message_type = message.get("type")
            
            if message_type == "director_answer":
                # Director answer received from client
                answer = message.get("answer", "")
                logger.info("director_answer_received", answer=answer)
                # TODO: Resume graph with this answer
                # For now, just acknowledge
                await websocket.send_json({
                    "type": "director_answer_received",
                    "status": "processing"
                })
                
            elif message_type == "gate_approve":
                # Gate approved by user
                gate = message.get("gate")
                logger.info("gate_approved", gate=gate)
                # TODO: Resume graph execution
                await websocket.send_json({
                    "type": "gate_approved",
                    "gate": gate
                })
                
            elif message_type == "gate_reject":
                # Gate rejected by user
                logger.info("gate_rejected")
                await websocket.send_json({
                    "type": "gate_rejected",
                    "status": "cancelled"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/config/providers")
async def get_providers():
    """Get available LLM providers."""
    from core.model_factory import get_available_providers
    return {"providers": get_available_providers()}

@app.post("/config/provider")
async def set_provider(data: dict):
    """Set the active LLM provider."""
    provider = data.get("provider")
    model = data.get("model")
    
    if not provider:
        raise HTTPException(status_code=400, detail="Provider is required")
        
    # In a real implementation, we would update a global config or session state.
    # For now, we'll just log it and return success, as the graph builds models dynamically.
    # To make this persistent, we might need to update settings or a database.
    logger.info("provider_switched", provider=provider, model=model)
    
    return {"status": "success", "provider": provider, "model": model}


# ============================================================
# DATA INSPECTION ENDPOINTS (Sprint 9)
# ============================================================

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for data inspection endpoints."""
    expected_key = settings.DATA_INSPECTOR_API_KEY
    
    # If no API key configured, allow all (dev mode)
    if not expected_key:
        logger.warning("data_inspector_no_auth", message="DATA_INSPECTOR_API_KEY not set, allowing all requests")
        return True
    
    if x_api_key != expected_key:
        logger.warning("data_inspector_auth_failed", provided_key=x_api_key[:10] if x_api_key else None)
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    return True


# In-memory storage for raw data (in production, use Redis or database)
_raw_data_store: Dict[str, Dict[str, Any]] = {}


@app.get("/data/{agent}/{source}")
async def get_raw_data(
    agent: str,
    source: str,
    api_key_valid: bool = Header(None, alias="X-API-Key", include_in_schema=False)
):
    """
    Get raw API data for a specific agent and source.
    
    Requires X-API-Key header for authentication.
    
    Args:
        agent: Agent name (e.g., "market_analyst")
        source: Data source (e.g., "igdb", "steam", "steamspy")
    
    Returns:
        Raw API response data
    """
    # Manual API key verification
    verify_api_key(api_key_valid)
    
    key = f"{agent}:{source}"
    
    if key not in _raw_data_store:
        raise HTTPException(status_code=404, detail=f"No data found for {agent}/{source}")
    
    logger.info("data_inspection_request", agent=agent, source=source)
    return _raw_data_store[key]


@app.post("/data/{agent}/{source}")
async def store_raw_data(
    agent: str,
    source: str,
    data: Dict[str, Any],
    api_key_valid: bool = Header(None, alias="X-API-Key", include_in_schema=False)
):
    """
    Store raw API data for later inspection.
    
    This endpoint is called internally by agents to cache raw data.
    """
    verify_api_key(api_key_valid)
    
    key = f"{agent}:{source}"
    _raw_data_store[key] = data
    
    logger.info("data_stored", agent=agent, source=source, size_bytes=len(str(data)))
    return {"status": "stored", "key": key}


@app.get("/data/validation/warnings")
async def get_validation_warnings(
    api_key_valid: bool = Header(None, alias="X-API-Key", include_in_schema=False)
):
    """
    Get all validation warnings from the latest workflow run.
    
    Returns warnings from the Validator agent if validation was enabled.
    """
    verify_api_key(api_key_valid)
    
    # In a real implementation, this would fetch from the latest state
    # For now, return from in-memory store
    warnings = _raw_data_store.get("validator:warnings", [])
    
    return {
        "warnings": warnings,
        "count": len(warnings) if isinstance(warnings, list) else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)
