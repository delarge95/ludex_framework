from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class AskDirectorInput(BaseModel):
    question: str = Field(description="The specific question to ask the user/director")
    context: str = Field(description="Brief context explaining why this input is needed")
    urgency: str = Field(description="Urgency level: 'low', 'medium', 'high'")

class AskDirectorTool(BaseTool):
    """
    Tool that allows agents to pause execution and request user input.
    This enables human-in-the-loop decision making for ambiguous situations.
    """
    name: str = "ask_the_director"
    description: str = "Ask the user/director a question when you encounter ambiguity or need creative direction. Use this ONLY when the decision significantly impacts the design and you cannot infer the answer from existing context."
    args_schema: Type[BaseModel] = AskDirectorInput
    
    def _run(self, question: str, context: str, urgency: str = "medium") -> str:
        """
        Stores the question in state and signals the workflow to pause.
        The actual answer will come from the user via the frontend.
        """
        # In a real implementation, this would:
        # 1. Store the question in the state's `director_questions` list
        # 2. Set `awaiting_input = True`
        # 3. Return a placeholder that tells the agent to wait
        
        return f"[DIRECTOR INPUT REQUESTED] Your question has been sent to the director. The workflow will pause until they respond. Question: {question}"
    
    async def _arun(self, question: str, context: str, urgency: str = "medium") -> str:
        """Async version"""
        return self._run(question, context, urgency)
