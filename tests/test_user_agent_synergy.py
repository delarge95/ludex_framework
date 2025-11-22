import unittest
from tools.ask_director_tool import AskDirectorTool
from agents.governance.interactive_breakpoint import create_progress_summary

class TestUserAgentSynergy(unittest.TestCase):
    def test_ask_director_tool_instantiation(self):
        """Test that AskDirectorTool can be instantiated"""
        tool = AskDirectorTool()
        self.assertEqual(tool.name, "ask_the_director")
        self.assertTrue(hasattr(tool, "_run"))
    
    def test_ask_director_execution(self):
        """Test asking a question"""
        tool = AskDirectorTool()
        result = tool._run(
            question="Should the combat be realistic or arcade-style?",
            context="Physics system design needs direction",
            urgency="high"
        )
        self.assertIn("DIRECTOR INPUT REQUESTED", result)
        self.assertIn("combat", result)
    
    def test_progress_summary_creation(self):
        """Test progress summary generation"""
        mock_state = {
            "current_phase": "production",
            "iteration_count": 2,
            "reasoning_log": [
                {"agent_name": "MechanicsDesigner"},
                {"agent_name": "NarrativeArchitect"}
            ],
            "working": {
                "mechanics": [{"name": "Jump"}],
                "narrative_structure": {"acts": 3}
            }
        }
        
        summary = create_progress_summary(mock_state)
        
        self.assertEqual(summary["current_phase"], "production")
        self.assertEqual(summary["iteration"], 2)
        self.assertIn("MechanicsDesigner", summary["completed_agents"])
        self.assertIn("mechanics", summary["key_artifacts"])

if __name__ == '__main__':
    unittest.main()
