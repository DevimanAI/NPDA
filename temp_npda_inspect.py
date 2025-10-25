from automata.pda.npda import NPDA
from npda_visualizer import read_npda_from_file
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python temp_npda_inspect.py <npda_definition_file>")
        sys.exit(1)

    npda_definition_file = sys.argv[1]

    try:
        npda = read_npda_from_file(npda_definition_file)
        print("Successfully loaded NPDA from", npda_definition_file)
        print("\n--- Inspecting npda.transitions ---")
        print(npda.transitions)
    except Exception as e:
        print(f"Error loading or validating NPDA: {e}")
        sys.exit(1)