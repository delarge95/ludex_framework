from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from core.state_v2 import SpiralState, CoreState, WorkingState

class ContextManager:
    """
    Manages the context window for agents by pruning messages and 
    generating specific state views to prevent hallucination and reduce token usage.
    """
    
    def __init__(self):
        # Define view mappings: Role -> List of state keys to include
        self.view_mappings = {
            "default": ["core", "working"], # Fallback: see everything
            
            # Sprint 13 Agents
            "audio_director": [
                "core.concept", 
                "core.genre", 
                "core.narrative_theme", 
                "core.art_direction_pillars",
                "working.mechanics", 
                "working.narrative_structure", 
                "working.environment_design",
                "working.audio_design" # Own output
            ],
            "physics_engineer": [
                "core.concept",
                "core.genre",
                "core.engine_choice",
                "working.mechanics",
                "working.environment_design",
                "working.technical_stack",
                "working.physics_spec" # Own output
            ],
            
            # Sprint 14 Agents
            "economy_balancer": [
                "core.concept",
                "core.genre",
                "core.market_analysis",
                "working.mechanics",
                "working.systems",
                "working.production_plan" # For monetization timing
            ],
            "network_architect": [
                "core.target_platform",
                "core.engine_choice",
                "working.mechanics", # To know if multiplayer is needed
                "working.technical_stack"
            ],
            
            # Sprint 15 Agents
            "level_designer": [
                "core.concept",
                "core.narrative_theme",
                "working.mechanics",
                "working.narrative_structure",
                "working.environment_design",
                "working.level_design" # Own output
            ],
            "performance_analyst": [
                "core.target_platform",
                "core.engine_choice",
                "working.technical_stack",
                "working.environment_design", # Poly count risk
                "working.character_visuals", # Poly count risk
                "working.performance_spec" # Own output
            ],
            
            # Sprint 16 Agent
            "qa_planner": [
                "core.target_platform",
                "working.mechanics",
                "working.systems",
                "working.technical_stack",
                "working.qa_plan" # Own output
            ]
        }

    def prune_messages(self, messages: List[BaseMessage], max_messages: int = 10) -> List[BaseMessage]:
        """
        Keeps the SystemMessage (if present) and the last N messages.
        Preserves the conversation flow while discarding old context.
        """
        if not messages:
            return []
            
        pruned = []
        
        # Always keep the first message if it's a SystemMessage
        if isinstance(messages[0], SystemMessage):
            pruned.append(messages[0])
            remaining_messages = messages[1:]
        else:
            remaining_messages = messages
            
        # Keep the last N messages
        if len(remaining_messages) > max_messages:
            pruned.extend(remaining_messages[-max_messages:])
        else:
            pruned.extend(remaining_messages)
            
        return pruned

    def generate_view(self, state: SpiralState, agent_role: str) -> Dict[str, Any]:
        """
        Extracts a specific view of the state for a given agent.
        Flattens nested keys (e.g., 'core.concept') into a single dictionary.
        """
        keys_to_include = self.view_mappings.get(agent_role, self.view_mappings["default"])
        view = {}
        
        for key_path in keys_to_include:
            value = self._get_nested_value(state, key_path)
            if value is not None:
                # Use the last part of the key as the key in the view
                # e.g., 'core.concept' -> 'concept'
                # But if there's a collision, we might need to be smarter. 
                # For now, simple mapping.
                view_key = key_path.split(".")[-1]
                view[view_key] = value
                
        return view

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Helper to retrieve 'core.concept' from the state dict."""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
