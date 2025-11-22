"""
Optional Validator Agent for LUDEX Framework.

This agent performs cross-validation between different data sources
(IGDB, Steam, SteamSpy) to detect inconsistencies and flag warnings.

Only runs when `enable_validation` is True in GameDesignState.
"""

import structlog
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def validator_node(state: GameDesignState) -> GameDesignState:
    """
    Validator Agent Node (OPTIONAL).
    Role: Cross-validate data between IGDB, Steam, and SteamSpy.
    
    Only runs if state.get("enable_validation", False) is True.
    """
    logger.info("validator_started")
    
    # Check if validation is enabled
    if not state.get("enable_validation", False):
        logger.info("validation_skipped", reason="enable_validation=False")
        return state
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.3  # Lower temperature for analytical task
        )
        
        # Extract data from state
        market_analysis = state.get("market_analysis", {})
        raw_data_cache = state.get("raw_data_cache", {})
        
        # If no data to validate, skip
        if not market_analysis or not raw_data_cache:
            logger.warning("validator_no_data", reason="Missing market_analysis or raw_data_cache")
            return state
        
        # System prompt for validation
        system_msg = SystemMessage(content="""You are a Data Quality Analyst for game design research.
        Your role is to cross-validate data from multiple sources and flag inconsistencies.
        
        Your Validation Checks:
        1. **Price Consistency**: Compare IGDB price vs Steam price (±10% tolerance)
        2. **Genre Alignment**: Check if IGDB genres match Steam tags
        3. **Release Date Verification**: Cross-check release dates
        4. **Player Count Sanity**: Flag unrealistic player counts (negative, impossibly high)
        5. **Popularity Alignment**: Compare IGDB popularity with SteamSpy owners/players
        
        Output Format (JSON):
        {
          "validation_passed": true/false,
          "warnings": [
            {
              "severity": "INFO / WARNING / CRITICAL",
              "category": "price / genre / date / player_count / popularity",
              "message": "Description of inconsistency",
              "affected_field": "Field name",
              "igdb_value": "value from IGDB",
              "steam_value": "value from Steam",
              "steamspy_value": "value from SteamSpy (if applicable)",
              "suggested_action": "What to do about this"
            }
          ],
          "confidence_score": 0-100
        }
        
        Severity Levels:
        - **INFO**: Minor discrepancies, likely just different data sources (e.g., price difference <5%)
        - **WARNING**: Notable inconsistencies that should be reviewed (e.g., genre mismatch)
        - **CRITICAL**: Major problems that could invalidate the analysis (e.g., game doesn't exist on Steam)
        
        Be objective and data-driven. Don't flag warnings unless there's a real inconsistency.
        """)
        
        # Prepare validation context
        igdb_data = raw_data_cache.get("igdb", {})
        steam_data = raw_data_cache.get("steam", {})
        steamspy_data = raw_data_cache.get("steamspy", {})
        
        validation_context = f"""
        # Validation Task
        
        Cross-validate data for game: **{state.get('concept', 'Unknown Game')}**
        
        ## Data Sources
        
        ### IGDB Data:
        {igdb_data if igdb_data else "No IGDB data available"}
        
        ### Steam Data:
        {steam_data if steam_data else "No Steam data available"}
        
        ### SteamSpy Data:
        {steamspy_data if steamspy_data else "No SteamSpy data available"}
        
        ## MarketAnalyst Summary:
        {market_analysis}
        
        Perform cross-validation and return warnings in JSON format.
        """
        
        human_msg = HumanMessage(content=validation_context)
        
        # Invoke LLM
        result = await safe_agent_invoke(
            agent_name="Validator",
            llm=llm,
            messages=[system_msg, human_msg],
            state=state,
            tools=[]
        )
        
        if result is None:
            logger.error("validator_failed", reason="safe_agent_invoke returned None")
            return state
        
        # Parse validation output (expecting JSON)
        validation_output = result.get("content", "{}")
        
        # Try to extract JSON from markdown code blocks if present
        if "```json" in validation_output:
            validation_output = validation_output.split("```json")[1].split("```")[0].strip()
        elif "```" in validation_output:
            validation_output = validation_output.split("```")[1].split("```")[0].strip()
        
        import json
        try:
            validation_result = json.loads(validation_output)
        except json.JSONDecodeError:
            logger.error("validator_parse_error", output=validation_output[:200])
            validation_result = {
                "validation_passed": False,
                "warnings": [{
                    "severity": "CRITICAL",
                    "category": "system",
                    "message": "Failed to parse validation output",
                    "affected_field": "N/A",
                    "suggested_action": "Review raw output"
                }],
                "confidence_score": 0
            }
        
        # Update state with validation warnings
        state_update = {
            "validation_warnings": validation_result.get("warnings", []),
            "validation_passed": validation_result.get("validation_passed", True),
            "validation_confidence": validation_result.get("confidence_score", 50)
        }
        
        logger.info(
            "validator_completed",
            warnings_count=len(validation_result.get("warnings", [])),
            passed=validation_result.get("validation_passed", True)
        )
        
        return {**state, **state_update}
    
    except Exception as e:
        logger.exception("validator_error", error=str(e))
        # Don't fail the workflow, just skip validation
        return {
            **state,
            "validation_warnings": [{
                "severity": "WARNING",
                "category": "system",
                "message": f"Validation failed: {str(e)}",
                "affected_field": "N/A",
                "suggested_action": "Validation skipped due to error"
            }]
        }
