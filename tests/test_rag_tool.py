import unittest
from tools.domain_knowledge_tool import DomainKnowledgeTool

class TestRAGTool(unittest.TestCase):
    def test_tool_instantiation(self):
        tool = DomainKnowledgeTool()
        self.assertEqual(tool.name, "domain_knowledge_tool")
        self.assertTrue(hasattr(tool, "_run"))

if __name__ == '__main__':
    unittest.main()
