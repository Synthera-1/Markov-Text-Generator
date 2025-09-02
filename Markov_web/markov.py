import random
from collections import defaultdict
import re

class MarkovChain:
    def __init__(self, order=2):
        self.order = order
        self.model = defaultdict(lambda: defaultdict(int))

    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def train(self, text):
        tokens = self.tokenize(text)
        if len(tokens) < self.order + 1:
            print("Text too short for training.")
            return
        for i in range(len(tokens) - self.order):
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            self.model[state][next_word] += 1

    def generate(self, length=50):
        if not self.model:
            return ""
        state = random.choice(list(self.model.keys()))
        output = list(state)
        for _ in range(length - self.order):
            next_words = self.model.get(state)
            if not next_words:
                break
            words = list(next_words.keys())
            counts = list(next_words.values())
            total = sum(counts)
            probabilities = [count / total for count in counts]
            next_word = random.choices(words, weights=probabilities)[0]
            output.append(next_word)
            state = tuple(output[-self.order:])
        result = ' '.join(output)
        return result[0].upper() + result[1:] + '.'

    def generate_one_word(self, current_state):
        """Generate next word from current state tuple"""
        next_words = self.model.get(current_state)
        if not next_words:
            return None
        words = list(next_words.keys())
        counts = list(next_words.values())
        total = sum(counts)
        probabilities = [count / total for count in counts]
        return random.choices(words, weights=probabilities)[0]

