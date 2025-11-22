from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from core.state import GameDesignState
from config.settings import settings
import json

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=settings.GITHUB_TOKEN,
    base_url="https://models.inference.ai.azure.com"
)

async def director_node(state: GameDesignState) -> GameDesignState:
    """
    The Director Agent:
    1. Analyzes the user's concept.
    2. Asks clarifying questions if the concept is vague.
    3. Determines the production mode (Prototype vs Full).
    4. Refines the concept once sufficient information is gathered.
    """
    
    print(f"🎬 Director is analyzing concept: {state['concept']}")
    
    # If we are already waiting for input and just got it, we proceed to re-analyze
    # The 'messages' list in state would contain the user's answer if this was a chat app,
    # but here we assume state['concept'] might be updated or we look at the last message.
    
    system_msg = SystemMessage(content="""You are the Studio Director of a prestigious Indie Game Studio.
    Your goal is to greenlight projects, but you are strict about clarity.
    
    Analyze the user's game concept.
    
    # DECISION LOGIC:
    1. **VAGUE CONCEPT**: If the concept is too short (e.g. "A platformer") or missing key elements (Genre, Core Hook, Vibe), you MUST ask clarifying questions.
       - Limit to 1-2 most critical questions.
       - Be concise and professional but encouraging.
    
    2. **CLEAR CONCEPT**: If the concept has a Genre, a Hook, and a general Vibe, you proceed to production.
       - Refine the concept into a "Pitch" format.
       - Select a Production Mode:
         - "prototype": If it sounds experimental or small scope.
         - "full": If it sounds like a commercial indie product.
    
    # OUTPUT FORMAT (STRICT JSON):
    {
        "status": "clarification_needed" | "ready",
        "questions": ["Question 1?", "Question 2?"],  // Only if clarification_needed
        "production_mode": "prototype" | "full",       // Only if ready
        "refined_concept": "The refined pitch...",     // Only if ready
        "rationale": "Why you made this decision"
    }
    """)
    
    user_msg = HumanMessage(content=f"Concept: {state['concept']}")
    
    response = await llm.ainvoke([system_msg, user_msg])
    
    try:
        content = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        
        if data["status"] == "clarification_needed":
            print(f"❓ Director asks: {data['questions']}")
            state["awaiting_input"] = True
            state["director_questions"] = data["questions"]
            # We do NOT change the concept yet, we wait for user input
        else:
            print(f"✅ Director approved: {data['production_mode']}")
            state["awaiting_input"] = False
            state["director_questions"] = []
            state["production_mode"] = data["production_mode"]
            state["refined_concept"] = data["refined_concept"]
            # Update the main concept with the refined version for other agents
            state["concept"] = data["refined_concept"]
            
    except Exception as e:
        print(f"❌ Director Error: {e}")
        # Fallback: Assume ready if JSON fails
        state["awaiting_input"] = False
        state["production_mode"] = "prototype"
    
    return state
