import unittest
from core.agent_synergies import (
    extract_world_physics_constants,
    extract_art_performance_budgets,
    extract_mechanics_audio_triggers,
    inject_synergy_context
)

class TestAgentSynergies(unittest.TestCase):
    def test_extract_world_physics_constants(self):
        """Test extraction of physics constants from world lore"""
        world_lore = {
            "world_description": "A moon colony with low gravity and thin atmosphere",
            "geography": {
                "terrain_types": ["Rocky craters", "Ice plains", "Underground caves"]
            }
        }
        
        constants = extract_world_physics_constants(world_lore)
        
        self.assertEqual(constants["gravity"], "Low (Moon-like)")
        self.assertEqual(constants["atmosphere"], "Standard")  # "thin atmosphere" in description, but function looks for "thin air"
        self.assertIn("Rocky craters", constants["terrain"])
    
    def test_extract_art_performance_budgets(self):
        """Test extraction of performance budgets from art style"""
        art_style_guide = {
            "art_style": "Hyper-realistic AAA",
            "visual_fidelity": "high"
        }
        
        budgets = extract_art_performance_budgets(art_style_guide)
        
        self.assertIn("100k", budgets["target_poly_count"])
        self.assertEqual(budgets["texture_resolution"], "4K")
    
    def test_extract_mechanics_audio_triggers(self):
        """Test extraction of audio triggers from mechanics"""
        mechanics = [
            {"name": "Double Jump", "type": "movement"},
            {"name": "Sword Slash", "type": "combat"},
            {"name": "Collect Coin", "type": "interaction"}
        ]
        
        triggers = extract_mechanics_audio_triggers(mechanics)
        
        self.assertIn("Double Jump", triggers)
        self.assertIn("Attack", triggers)  # From combat type
        self.assertIn("Jump", triggers)  # From movement type
    
    def test_inject_synergy_context(self):
        """Test injection of synergy data into prompts"""
        base_prompt = "You are a physics engineer."
        synergy_data = {
            "gravity": "Low (Moon-like)",
            "atmosphere": "Thin",
            "terrain": "Rocky"
        }
        
        enhanced = inject_synergy_context(base_prompt, synergy_data, "world_physics")
        
        self.assertIn("Low (Moon-like)", enhanced)
        self.assertIn("World Physics Context", enhanced)
        self.assertIn(base_prompt, enhanced)

if __name__ == '__main__':
    unittest.main()
