from typing import Type, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from tools.retrieval_tool import search_design_patterns, search_engine_docs

class DomainKnowledgeInput(BaseModel):
    query: str = Field(description="The specific concept or technical term to search for.")
    domain: str = Field(description="The domain to search: 'patterns', 'engine', 'narrative', 'market'.")

class DomainKnowledgeTool(BaseTool):
    name: str = "domain_knowledge_tool"
    description: str = "Search for professional game design knowledge, technical documentation, and market patterns. Use this to ground your decisions in reality."
    args_schema: Type[BaseModel] = DomainKnowledgeInput

    def _run(self, query: str, domain: str = "patterns") -> str:
        """Execute the search based on domain."""
        try:
            if domain == "engine":
                return search_engine_docs(query)
            elif domain == "patterns":
                return search_design_patterns(query)
            # Fallback or future domains
            else:
                return search_design_patterns(query)
        except Exception as e:
            return f"Error searching domain knowledge: {str(e)}"

    async def _arun(self, query: str, domain: str = "patterns") -> str:
        """Async implementation (currently synchronous wrapper)."""
        return self._run(query, domain)
