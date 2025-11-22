import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import graphs.main_graph...")
    from graphs.main_graph import graph
    print("Successfully imported graph!")
except Exception as e:
    print(f"Error importing graph: {e}")
    import traceback
    traceback.print_exc()
