"""
Technical Feasibility Validator Agent for LUDEX Framework (Sprint 10)

Validates game mechanics against Unity/Unreal/Godot technical capabilities.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def technical_feasibility_validator_node(state: GameDesignState) -> GameDesignState:
    """
    Technical Feasibility Validator Agent Node.
    Role: Validate mechanics against game engine capabilities.
    """
    logger.info("technical_feasibility_validator_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.3  # Lower temperature for technical accuracy
        )
        
        mechanics = state.get("mechanics", [])
        technical_stack = state.get("technical_stack", {})
        
        system_msg = SystemMessage(content="""You are a **Technical Feasibility Validator** expert in Unity, Unreal Engine, and Godot.

Validate game mechanics against engine capabilities and provide implementation guidance.

Output JSON:
```json
{
  "feasibility_score": 0.85,
  "validated_mechanics": [
    {
      "mechanic": "First-person movement",
      "engine": "Unity",
      "feasibility": "HIGH",
      "implementation": "CharacterController + Cinemachine",
      "estimated_complexity": "LOW",
      "required_assets": ["Standard Assets", "Cinemachine"],
      "potential_issues": []
    }
  ],
  "technical_risks": [
    {"risk": "Performance bottleneck", "mitigation": "..."}
  ],
  "recommended_engine": "Unity / Unreal / Godot",
  "engine_justification": "...",
  "estimated_dev_time_months": 6
}
```""")
        
        human_msg = HumanMessage(content=f"""Validate technical feasibility:
**Mechanics**: {mechanics}
**Proposed Stack**: {technical_stack}

Assess:
1. Engine recommendation
2. Implementation complexity
3. Required assets/plugins
4. Technical risks
5. Development timeline""")
        
        result = await safe_agent_invoke(
            agent_name="TechnicalFeasibilityValidator",
            llm=llm,
            messages=[system_msg, human_msg],
            state=state,
            tools=[]  # RAG tools will be added later
        )
        
        if result is None:
            return state
        
        output = result.get("content", "{}")
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        
        import json
        try:
            feasibility_report = json.loads(output)
        except json.JSONDecodeError:
            feasibility_report = {"raw_output": output}
        
        logger.info(
            "technical_feasibility_validator_completed",
            feasibility_score=feasibility_report.get("feasibility_score", 0),
            recommended_engine=feasibility_report.get("recommended_engine", "Unknown")
        )
        
        return {
            **state,
            "technical_feasibility": feasibility_report
        }
    
    except Exception as e:
        logger.exception("technical_feasibility_validator_error", error=str(e))
        return state
