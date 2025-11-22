import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from core.agent_synergies import extract_mechanics_system_requirements, inject_synergy_context
from tools.retrieval_tool import RetrievalTool
from config.settings import settings

logger = structlog.get_logger(__name__)

async def system_designer_node(state: GameDesignState):
    """
    System Designer (Technical Architect) Agent Node.
    Role: Validate technical feasibility, select stack, and design core architecture.
    """
    logger.info("system_designer_started")

    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.5
        )

        retrieval_tool = RetrievalTool()
        tools = [retrieval_tool.search_engine_docs]
        
        # SYNERGY: Extract system requirements from MechanicsDesigner
        mechanics = state.get("mechanics", [])
        requirements = extract_mechanics_system_requirements(mechanics)

        base_prompt = """You are a **Technical Architect** (formerly System Designer) specializing in Game Engine Architecture.
        Your goal is to design the technical foundation of the game, selecting the engine, language, and critical systems.

        Consider:
        - Mechanics complexity
        - Target platforms
        - Multiplayer requirements (if any)
        - Performance constraints

        Output Format (JSON):
        {
            "engine": "Unity 6 / Unreal Engine 5 / Godot 4",
            "language": "C# / C++ / GDScript",
            "architecture_pattern": "ECS / MVC / Singleton / ScriptableObjects",
            "critical_packages": ["Netcode for GameObjects", "Cinemachine", "DOTS", "Chaos Physics"],
            "technical_risks": [
                {"risk": "High entity count", "mitigation": "Use DOTS/ECS"},
                {"risk": "Complex networking", "mitigation": "Server-authoritative architecture"}
            ],
            "platform_considerations": {
                "PC": "High fidelity, keyboard/mouse",
                "Console": "Controller support, TRC compliance",
                "Mobile": "Touch controls, battery optimization"
            }
        }
        """
        
        # SYNERGY: Inject mechanics requirements into prompt
        system_msg = SystemMessage(content=inject_synergy_context(base_prompt, requirements, "mechanics_system"))

        mechanics_str = str(state.get("mechanics", []))
        platforms = str(state.get("target_platforms", ["PC"]))
        
        human_msg = HumanMessage(content=f"""Design technical architecture for:
        Mechanics: {mechanics_str}
        Platforms: {platforms}
        """)

        result = await safe_agent_invoke(
            agent_name="SystemDesigner",
            llm=llm,
            tools=tools,
            messages=[system_msg, human_msg],
            state=state
        )

        import json
        try:
            output_str = result.get("content", "{}")
            if "```json" in output_str:
                output_str = output_str.split("```json")[1].split("```")[0].strip()
            tech_stack = json.loads(output_str)
        except:
            tech_stack = {
                "engine": "Unity",
                "language": "C#",
                "architecture_pattern": "Monobehaviour",
                "critical_packages": [],
                "technical_risks": [{"risk": "Parse Error", "mitigation": "Manual Review"}],
                "platform_considerations": {}
            }

        return {
            **state,
            "technical_stack": tech_stack,
            # "current_step": "producer", # Removed to let graph handle flow
            # "messages": state["messages"] + [HumanMessage(content=str(tech_stack))] # Optional
        }

    except Exception as e:
        logger.error("system_designer_failed", error=str(e))
        return {
            **state,
            "errors": state.get("errors", []) + [str(e)]
        }
