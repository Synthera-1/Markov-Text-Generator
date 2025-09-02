import random
import re
from collections import defaultdict

class MarkovChain:
    def __init__(self, order=2):
        self.order = order
        self.model = defaultdict(list)

    def tokenize(self, text):
        # Simple word tokenizer
        return re.findall(r"\b\w+\b", text.lower())

    def train(self, text):
        tokens = self.tokenize(text)
        if len(tokens) < self.order + 1:
            return

        for i in range(len(tokens) - self.order):
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            self.model[state].append(next_word)

    def generate(self, length=50):
        if not self.model:
            return ""

        state = random.choice(list(self.model.keys()))
        output = list(state)

        for _ in range(length - self.order):
            next_words = self.model.get(state)
            if not next_words:
                break
            next_word = random.choice(next_words)
            output.append(next_word)
            state = tuple(output[-self.order:])

        return ' '.join(output).capitalize() + '.'
