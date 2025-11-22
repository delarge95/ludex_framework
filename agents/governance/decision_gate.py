import structlog
import json
from datetime import datetime
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage
from core.state_v2 import SpiralState, Decision, DecisionOption
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke

logger = structlog.get_logger(__name__)

async def generate_decision(
    state: SpiralState,
    context_data: str,
    decision_title: str,
    decision_description: str,
    gate_id: str
) -> Decision:
    """
    Generates a Decision object with LLM-created options and risk analysis.
    """
    logger.info(f"generating_decision_{gate_id}")
    
    try:
        llm = create_model(provider=state.get("llm_provider", "github"), model_type="smart")
        
        prompt = f"""
        You are a Strategic Game Director.
        We are at a critical decision point: **{decision_title}**
        
        **Context**:
        {context_data}
        
        **Goal**:
        Generate 3 distinct strategic options for the user to choose from.
        1. **Safe Bet**: Low risk, standard execution.
        2. **Ambitious Pivot**: High risk, high reward, innovative.
        3. **Resource Heavy**: High quality, but expensive/time-consuming.
        
        For each option, estimate a Risk Score (0-100, where 100 is extremely risky).
        
        Return a JSON object:
        {{
            "options": [
                {{
                    "id": "opt_safe",
                    "label": "Safe Bet Title",
                    "description": "Detailed description...",
                    "risk_score": 10,
                    "projected_impact": "Impact analysis..."
                }},
                {{
                    "id": "opt_ambitious",
                    "label": "Ambitious Pivot Title",
                    "description": "...",
                    "risk_score": 80,
                    "projected_impact": "..."
                }},
                {{
                    "id": "opt_quality",
                    "label": "High Quality Title",
                    "description": "...",
                    "risk_score": 40,
                    "projected_impact": "..."
                }}
            ]
        }}
        """
        
        result = await safe_agent_invoke(llm, [SystemMessage(content=prompt)], f"decision_gate_{gate_id}")
        
        options_data = result.get("options", [])
        
        # Convert to DecisionOption objects
        options: List[DecisionOption] = []
        for opt in options_data:
            options.append({
                "id": opt.get("id", "unknown"),
                "label": opt.get("label", "Unknown Option"),
                "description": opt.get("description", ""),
                "risk_score": opt.get("risk_score", 50),
                "projected_impact": opt.get("projected_impact", "")
            })
            
        return {
            "id": gate_id,
            "title": decision_title,
            "description": decision_description,
            "options": options,
            "selected_option_id": None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"decision_generation_failed_{gate_id}", error=str(e))
        # Fallback decision
        return {
            "id": gate_id,
            "title": decision_title,
            "description": "Error generating options. Please proceed manually.",
            "options": [
                {"id": "continue", "label": "Continue", "description": "Proceed as planned.", "risk_score": 0, "projected_impact": "None"}
            ],
            "selected_option_id": None,
            "timestamp": datetime.now().isoformat()
        }
