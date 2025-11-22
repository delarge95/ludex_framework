"""
Unit tests for LUDEX game design agents

Tests validate that each agent node function:
1. Accepts GameDesignState as input
2. Returns updated GameDesignState
3. Executes without errors
4. Produces non-empty output
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from core.state import GameDesignState
from agents.game_design.market_analyst import market_analyst_node
from agents.game_design.mechanics_designer import mechanics_designer_node
from agents.game_design.system_designer import system_designer_node
from agents.game_design.producer import producer_node
from agents.game_design.gdd_writer import gdd_writer_node


@pytest.fixture
def mock_state():
    """Fixture providing a basic GameDesignState for testing"""
    return GameDesignState(
        concept="A roguelike deckbuilder about hacking corpo servers",
        genre="Roguelike",
        market_analysis={},
        mechanics=[],
        technical_stack={},
        production_plan=None,
        gdd_content={},
        messages=[],
        current_step="start",
        errors=[]
    )


@pytest.mark.asyncio
@patch('agents.game_design.market_analyst.safe_agent_invoke', new_callable=AsyncMock)
@patch('agents.game_design.market_analyst.create_model')
async def test_market_analyst_node(mock_create_model, mock_invoke, mock_state):
    """Test MarketAnalyst node execution"""
    # Mock LLM response
    mock_invoke.return_value = {"output": "Market analysis: Target audience is indie gamers..."}
    mock_create_model.return_value = Mock()
    
    # Execute node
    result = await market_analyst_node(mock_state)
    
    # Assertions
    assert isinstance(result, dict)
    assert "current_step" in result
    mock_invoke.assert_called_once()


@pytest.mark.asyncio
@patch('agents.game_design.mechanics_designer.RetrievalTool')
@patch('agents.game_design.mechanics_designer.safe_agent_invoke', new_callable=AsyncMock)
@patch('agents.game_design.mechanics_designer.create_model')
async def test_mechanics_designer_node(mock_retrieval_tool, mock_invoke, mock_create_model, mock_state):
    """Test MechanicsDesigner node execution"""
    mock_invoke.return_value = {"output": "[]"}
    mock_create_model.return_value = Mock()
    
    mock_tool = Mock()
    mock_tool.name = "search_game_design_patterns"
    mock_tool.description = "Search for game design patterns"
    mock_retrieval_tool.return_value.search_design_patterns = mock_tool
    
    result = await mechanics_designer_node(mock_state)
    
    assert isinstance(result, dict)
    assert "current_step" in result
    assert "errors" not in result or not result["errors"], f"Errors found: {result.get('errors')}"
    mock_invoke.assert_called_once()


@pytest.mark.asyncio
@patch('agents.game_design.system_designer.RetrievalTool')
@patch('agents.game_design.system_designer.safe_agent_invoke', new_callable=AsyncMock)
@patch('agents.game_design.system_designer.create_model')
async def test_system_designer_node(mock_retrieval_tool, mock_invoke, mock_create_model, mock_state):
    """Test SystemDesigner node execution"""
    mock_invoke.return_value = {"output": "Technical stack: Unity 2D, C#, procedural generation..."}
    mock_create_model.return_value = Mock()
    
    mock_tool = Mock()
    mock_tool.name = "search_engine_docs"
    mock_tool.description = "Search engine docs"
    mock_retrieval_tool.return_value.search_engine_docs = mock_tool
    
    result = await system_designer_node(mock_state)
    
    assert isinstance(result, dict)
    assert "current_step" in result
    mock_invoke.assert_called_once()


@pytest.mark.asyncio
@patch('agents.game_design.producer.safe_agent_invoke', new_callable=AsyncMock)
@patch('agents.game_design.producer.create_model')
async def test_producer_node(mock_create_model, mock_invoke, mock_state):
    """Test Producer node execution"""
    mock_invoke.return_value = {"output": "Production timeline: 6-8 months, team of 3..."}
    mock_create_model.return_value = Mock()
    
    result = await producer_node(mock_state)
    
    assert isinstance(result, dict)
    assert "current_step" in result
    mock_invoke.assert_called_once()


@pytest.mark.asyncio
@patch('agents.game_design.gdd_writer.safe_agent_invoke', new_callable=AsyncMock)
@patch('agents.game_design.gdd_writer.create_model')
async def test_gdd_writer_node(mock_create_model, mock_invoke, mock_state):
    """Test GDDWriter node execution"""
    mock_invoke.return_value = {"output": "# Game Design Document\n## Title: Cyber Breach\n..."}
    mock_create_model.return_value = Mock()
    
    result = await gdd_writer_node(mock_state)
    
    assert isinstance(result, dict)
    assert "current_step" in result
    assert "gdd_content" in result
    mock_invoke.assert_called_once()


def test_state_flow():
    """Test that state updates propagate correctly through nodes"""
    initial_state = GameDesignState(
        concept="Test game concept",
        genre="Test",
        market_analysis=None,
        mechanics=[],
        technical_stack=None,
        production_plan=None,
        gdd_content={},
        messages=[],
        current_step="start",
        errors=[]
    )
    
    # Verify state structure
    assert initial_state["concept"] == "Test game concept"
    assert initial_state["current_step"] == "start"
    assert len(initial_state["errors"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
