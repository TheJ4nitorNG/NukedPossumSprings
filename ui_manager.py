class ConsoleUI:
    """Handles console-based input and output for the dialogue system."""

    @staticmethod
    def display_text(text):
        """Prints dialogue text to the console."""
        print(text)

    @staticmethod
    def display_choices(choices):
        """Displays available choices to the user."""
        print("\nChoices:")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice['text']}")

    @staticmethod
    def get_input(prompt):
        """Gets user input from the console."""
        return input(prompt)