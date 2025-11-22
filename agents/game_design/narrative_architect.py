"""
Narrative Architect Agent for LUDEX Framework (Sprint 10)

This agent applies narrative theory frameworks to design compelling story structures
for game concepts. It references established frameworks like Hero's Journey,
Three-Act Structure, and Kishōtenketsu.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def narrative_architect_node(state: GameDesignState) -> GameDesignState:
    """
    Narrative Architect Agent Node.
    Role: Lead Narrative Designer applying story structure frameworks.
    
    Applies frameworks like:
    - Hero's Journey (Campbell's Monomyth)
    - Three-Act Structure (Syd Field)
    - Kishōtenketsu (for non-Western narratives)
    """
    logger.info("narrative_architect_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.8  # Higher temperature for creativity
        )
        
        concept = state.get("concept", "")
        genre = state.get("genre", "Unknown")
        market_analysis = state.get("market_analysis", {})
        
        system_msg = SystemMessage(content="""You are a **Lead Narrative Architect** specialized in interactive storytelling for games.

Your expertise includes:
1. **Story Structure Frameworks**:
   - Hero's Journey / Monomyth (Joseph Campbell)
   - Three-Act Structure (Syd Field)
   - Kishōtenketsu (Japanese four-act structure)
   - Vogler's Writer's Journey

2. **Character Arc Design**:
   - Protagonist (motivations, flaws, transformation)
   - Supporting cast (mentor, rival, comic relief)
   - Antagonist (compelling motivations, philosophy)

3. **Narrative-Gameplay Integration**:
   - Ludonarrative harmony (story and mechanics reinforce each other)
   - Environmental storytelling opportunities
   - Emergent narrative potential

4. **Themesand Tone**:
   - Primary and secondary themes
   - Tone consistency (dark/light, serious/satirical)

**Output Format** (JSON):
```json
{
  "narrative_framework": "Hero's Journey / Three-Act / Kishōtenketsu",
  "protagonist": {
    "name": "Suggested protagonist name",
    "motivation": "Core drive (e.g., revenge, discovery, redemption)",
    "flaw": "Character weakness to overcome",
    "arc": "Brief transformation journey"
  },
  "antagonist": {
    "name": "Suggested antagonist name",
    "motivation": "Why they oppose the protagonist",
    "philosophy": "Their worldview/justification"
  },
  "story_beats": [
    {"act": 1, "beat": "Inciting Incident", "gameplay_milestone": "Tutorial complete", "description": "..."},
    {"act": 2, "beat": "Midpoint Reversal", "gameplay_milestone": "Boss 1 defeated", "description": "..."}
  ],
  "themes": ["Primary: ...", "Secondary: ..."],
  "tone": "Dark & Gritty / Whimsical / Epic / Satirical",
  "environmental_storytelling": ["Idea 1", "Idea 2"],
  "ludonarrative_harmony": "How story and gameplay reinforce each other",
  "narrative_references": ["Game A's approach to...", "Book B's structure"]
}
```

Be specific and cite narrative theory when applicable.""")
        
        human_msg = HumanMessage(content=f"""Design a compelling narrative structure for this game concept:

**Concept**: {concept}
**Genre**: {genre}
**Market Context**: {market_analysis}

Apply appropriate narrative frameworks and create:
1. Protagonist with clear arc
2. Compelling antagonist
3. Story beats aligned with gameplay milestones
4. Themes and tone
5. How narrative integrates with gameplay

Output as JSON following the specified schema.""")
        
        result = await safe_agent_invoke(
            agent_name="NarrativeArchitect",
            llm=llm,
            messages=[system_msg, human_msg],
            state=state,
            tools=[]  # RAG tools will be added later
        )
        
        if result is None:
            logger.error("narrative_architect_failed")
            return state
        
        # Parse narrative output
        narrative_output = result.get("content", "{}")
        
        # Try to extract JSON
        if "```json" in narrative_output:
            narrative_output = narrative_output.split("```json")[1].split("```")[0].strip()
        elif "```" in narrative_output:
            narrative_output = narrative_output.split("```")[1].split("```")[0].strip()
        
        import json
        try:
            narrative_structure = json.loads(narrative_output)
        except json.JSONDecodeError:
            logger.warning("narrative_architect_json_parse_failed", output=narrative_output[:200])
            # Fallback: store as raw text
            narrative_structure = {"raw_output": narrative_output}
        
        logger.info(
            "narrative_architect_completed",
            framework=narrative_structure.get("narrative_framework", "Unknown"),
protagonist_name=narrative_structure.get("protagonist", {}).get("name", "Unknown")
        )
        
        return {
            **state,
            "narrative_structure": narrative_structure
        }
    
    except Exception as e:
        logger.exception("narrative_architect_error", error=str(e))
        return state
