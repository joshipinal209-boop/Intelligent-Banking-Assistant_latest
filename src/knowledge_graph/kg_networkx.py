import sys
import os

# Add src to path if needed for local execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kg.engine import get_kg_engine

def load_graph():
    print("Initializing Knowledge Graph (NetworkX)...")
    try:
        engine = get_kg_engine()
        num_nodes = engine.graph.number_of_nodes()
        num_edges = engine.graph.number_of_edges()
        print(f"Graph loaded successfully with {num_nodes} nodes and {num_edges} edges.")
    except Exception as e:
        print(f"Error loading graph: {e}")
        sys.exit(1)

if __name__ == "__main__":
    load_graph()
