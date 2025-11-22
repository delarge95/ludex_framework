import unittest
from pydantic import ValidationError
from core.contracts import BaseContract, validate_input, validate_output, NarrativeContext, ArtContext

class TestContracts(unittest.TestCase):
    def test_narrative_context_valid(self):
        """Test that valid data passes narrative contract"""
        data = {
            "tone": "Dark and mysterious",
            "themes": ["redemption", "revenge"],
            "key_events": ["Opening scene", "Final battle"]
        }
        result = validate_input(data, NarrativeContext)
        self.assertEqual(result.tone, "Dark and mysterious")
        self.assertEqual(len(result.themes), 2)
    
    def test_narrative_context_invalid(self):
        """Test that invalid data fails validation"""
        data = {
            "tone": "Dark",
            # Missing 'themes' and 'key_events'
        }
        with self.assertRaises(ValidationError):
            validate_input(data, NarrativeContext)
    
    def test_art_context_valid(self):
        """Test ArtContext validation"""
        data = {
            "art_style": "Gritty realism",
            "visual_mood": "Oppressive"
        }
        result = validate_output(data, ArtContext)
        self.assertEqual(result.art_style, "Gritty realism")

if __name__ == '__main__':
    unittest.main()
