import random

# ============================================================================
# Dials and Constants
# ============================================================================
# Probability (0.0 to 1.0) that the prompt blocks will be shuffled
SHUFFLE_PROBABILITY = 0.50

class PhraseRandomizer:
    def __init__(self, prob: float = 0.50):
        self.prob = prob
        
    def process_prompt(self, text: str) -> str:
        """
        Takes a highly structured prompt separated by double newlines (\n\n)
        and randomly shuffles the semantic blocks to remove order bias.
        """
        # The prompts are structured into blocks separated by \n\n
        blocks = [block.strip() for block in text.split('\n\n') if block.strip()]
        
        # If there's only 1 block, we can't shuffle it at the paragraph level
        if len(blocks) <= 1:
            return text
            
        # Randomization Probability Dial
        if random.random() <= self.prob:
            random.shuffle(blocks)
        
        # Rejoin with double newlines
        return '\n\n'.join(blocks)

if __name__ == "__main__":
    # Quick test
    randomizer = PhraseRandomizer()
    sample = (
        "We need a comprehensive feature design for a drag-and-drop workflow visualizer for pipeline step configuration.\n\n"
        "This component will run in an edge environment with limited memory (256 MB) and intermittent network connectivity.\n\n"
        "Please provide a detailed architectural specification including:\n"
        "- Functional and non-functional requirements\n"
        "- Component architecture diagrams and data flows"
    )
    print("Original:\n", sample)
    print("\nRandomized:\n", randomizer.process_prompt(sample))
