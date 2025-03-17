from dialogue_manager import DialogueManager
from ui_manager import ConsoleUI
import json

# Load dialogue data from JSON file
with open("NukedPossumSprings/data/dialogue.json", "r") as file:
    dialog_tree = json.load(file)

# Initialize UI and DialogueManager
ui = ConsoleUI()
dialogue_manager = DialogueManager(dialog_tree, ui)

# Start the dialogue system
dialogue_manager.start_dialogue("node_001")