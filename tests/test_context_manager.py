import unittest
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from core.context_manager import ContextManager
from core.state_v2 import SpiralState, CoreState, WorkingState

class TestContextManager(unittest.TestCase):
    def setUp(self):
        self.cm = ContextManager()
        
    def test_prune_messages(self):
        # Create a list of 15 messages (1 System + 14 others)
        messages = [SystemMessage(content="System")]
        for i in range(14):
            messages.append(HumanMessage(content=f"Msg {i}"))
            
        # Prune to keep 10
        pruned = self.cm.prune_messages(messages, max_messages=10)
        
        # Should have 11 messages (1 System + 10 others)
        # Wait, logic says: if len > max, keep last max.
        # If System is present, keep System + last max?
        # Let's check implementation:
        # if System: pruned.append(System), remaining = messages[1:]
        # if len(remaining) > max: pruned.extend(remaining[-max:])
        
        self.assertEqual(len(pruned), 11) # 1 System + 10 Human
        self.assertEqual(pruned[0].content, "System")
        self.assertEqual(pruned[-1].content, "Msg 13")
        
    def test_generate_view_audio_director(self):
        # Mock State
        state = {
            "core": {
                "concept": "Epic RPG",
                "genre": "RPG",
                "narrative_theme": "Redemption",
                "art_direction_pillars": ["Dark", "Gritty"],
                "market_analysis": {"target_audience": "Teens"} # Should be hidden
            },
            "working": {
                "mechanics": [{"name": "Jump"}],
                "narrative_structure": {"acts": 3},
                "environment_design": {"biomes": ["Forest"]},
                "technical_stack": {"engine": "Unity"} # Should be hidden
            }
        }
        
        view = self.cm.generate_view(state, "audio_director")
        
        # Check included fields
        self.assertIn("concept", view)
        self.assertIn("narrative_theme", view)
        self.assertIn("mechanics", view)
        
        # Check excluded fields
        self.assertNotIn("market_analysis", view)
        self.assertNotIn("technical_stack", view)
        
        # Check values
        self.assertEqual(view["concept"], "Epic RPG")

if __name__ == '__main__':
    unittest.main()
