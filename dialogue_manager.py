
import json
import os

SAVE_FILE = "savegame.json"

class DialogueManager:
    def __init__(self, dialog_tree, ui):
        self.nodes = {node["id"]: node for node in dialog_tree["nodes"]}
        self.current_node = None
        self.state = {
            "relationship_olivia": 0,
            "inventory": []
        }
        self.history = []
        self.ui = ui

    def save_game(self):
        """Saves the current game state to a file."""
        save_data = {
            "current_node": self.current_node["id"],
            "state": self.state,
            "history": [(node["id"], choice) for node, choice in self.history]
        }
        with open(SAVE_FILE, "w") as file:
            json.dump(save_data, file, indent=4)
        self.ui.display_text("\n[Game Saved]")

    def load_game(self):
        """Loads the game state from a save file."""
        if not os.path.exists(SAVE_FILE):
            self.ui.display_text("\n[No saved game found.]")
            return False

        with open(SAVE_FILE, "r") as file:
            save_data = json.load(file)

        self.current_node = self.nodes.get(save_data["current_node"])
        self.state = save_data["state"]
        self.history = [(self.nodes[node_id], choice) for node_id, choice in save_data["history"]]

        self.ui.display_text("\n[Game Loaded]")
        return True

    def start_dialogue(self, start_node_id):
        """Start dialogue from the given node."""
        if not self.load_game():
            self.current_node = self.nodes.get(start_node_id)
            if not self.current_node:
                self.ui.display_text("Invalid start node!")
                return
        self.run_dialogue_loop()

    def display_current_node(self):
        """Display the current dialogue node and valid choices."""
        node = self.current_node
        self.ui.display_text(f"{node['speaker']}: {node['text']}")

        valid_choices = self.get_valid_choices(node["choices"])
        if valid_choices:
            self.ui.display_choices(valid_choices)
        else:
            self.ui.display_text("\n[End of conversation]")

    def get_valid_choices(self, choices):
        """Return choices that meet condition requirements."""
        return [
            choice for choice in choices
            if all(self.state.get(cond, 0) >= val for cond, val in choice.get("conditions", {}).items())
        ]

    def choose_option(self, choice_index):
        """Process the player's choice and move to the next node."""
        valid_choices = self.get_valid_choices(self.current_node["choices"])

        if not valid_choices:
            self.ui.display_text("\nNo choices available. The conversation has ended.")
            return False

        if choice_index < 1 or choice_index > len(valid_choices):
            self.ui.display_text("\nInvalid choice. Please enter a valid option.")
            return True

        choice = valid_choices[choice_index - 1]

        # Apply effects
        for key, value in choice.get("effects", {}).items():
            self.state[key] += value

        # Handle inventory changes
        self.update_inventory(choice)

        # Store history for backtracking
        self.history.append((self.current_node, choice))

        # Move to the next node
        next_node_id = choice["next_node"]
        self.current_node = self.nodes.get(next_node_id)

        if not self.current_node:
            self.ui.display_text("\n[Error] Next node does not exist.")
            return False

        return True

    def update_inventory(self, choice):
        """Modify inventory based on dialogue choice."""
        if "inventory_add" in choice:
            for item in choice["inventory_add"]:
                self.state["inventory"].append(item)
                self.ui.display_text(f"\n[Inventory] You received: {item}")

        if "inventory_remove" in choice:
            for item in choice["inventory_remove"]:
                if item in self.state["inventory"]:
                    self.state["inventory"].remove(item)
                    self.ui.display_text(f"\n[Inventory] You lost: {item}")
                else:
                    self.ui.display_text(f"\n[Inventory] You don't have {item} to lose.")

    def go_back(self):
        """Allow the player to undo their last choice."""
        if not self.history:
            self.ui.display_text("\nNo previous choices to go back to.")
            return

        last_node, last_choice = self.history.pop()
        self.current_node = last_node

        # Revert effects of the last choice
        for key, value in last_choice.get("effects", {}).items():
            self.state[key] -= value

        # Revert inventory changes
        if "inventory_add" in last_choice:
            for item in last_choice["inventory_add"]:
                if item in self.state["inventory"]:
                    self.state["inventory"].remove(item)

        if "inventory_remove" in last_choice:
            for item in last_choice["inventory_remove"]:
                self.state["inventory"].append(item)

        self.ui.display_text("\nReverted to previous choice.")
        self.display_current_node()

    def show_inventory(self):
        """Displays the player's current inventory."""
        inventory = self.state["inventory"]
        if inventory:
            self.ui.display_text("\n[Inventory] You have: " + ", ".join(inventory))
        else:
            self.ui.display_text("\n[Inventory] You have nothing.")

    def run_dialogue_loop(self):
        """Main loop to interact with the user."""
        while self.current_node:
            self.display_current_node()

            if not self.get_valid_choices(self.current_node["choices"]):
                restart = self.ui.get_input("\nRestart? (y/n): ").strip().lower()
                restart = "yes" if restart.startswith("y") else "no"
                if restart == "yes":
                    self.start_dialogue("node_001")
                break

            user_input = self.ui.get_input("\nChoice (back/inventory/save/load/#): ").strip().lower()

            # Normalize input and check for partial matches
            user_input = user_input.strip().lower()
            if user_input.startswith("b"):  # back
                self.go_back()
                continue
            elif "inv" in user_input:  # inventory
                self.show_inventory()
                continue
            elif user_input.startswith("s"):  # save
                self.save_game()
                continue
            elif user_input.startswith("l"):  # load
                if self.load_game():
                    self.run_dialogue_loop()
                continue

            try:
                choice_index = int(user_input)
                if not self.choose_option(choice_index):
                    break
            except ValueError:
                self.ui.display_text("\nInvalid input. Please enter a number or a command.")
