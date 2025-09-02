import sqlite3
import re
import random

class MarkovChainDB:
    def __init__(self, db_path='markov.db', max_order=3):
        self.max_order = max_order
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
        self.END_TOKENS = {'.', '!', '?'}

    def _create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS transitions (
                    order_n INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    next_word TEXT NOT NULL,
                    count INTEGER NOT NULL,
                    PRIMARY KEY (order_n, state, next_word)
                )
            ''')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_state ON transitions(state)')

    def tokenize(self, text):
        # tokenize words and keep punctuation as separate tokens
        tokens = re.findall(r"\w+|[.!?,'\";:-]", text.lower())
        return tokens

    def train(self, text):
        tokens = self.tokenize(text)
        n = len(tokens)
        with self.conn:
            for order in range(1, self.max_order + 1):
                for i in range(n - order):
                    state = ' '.join(tokens[i:i+order])
                    next_word = tokens[i+order]

                    # Try to update count if exists
                    cur = self.conn.execute(
                        'SELECT count FROM transitions WHERE order_n=? AND state=? AND next_word=?',
                        (order, state, next_word)
                    )
                    row = cur.fetchone()
                    if row:
                        count = row[0] + 1
                        self.conn.execute(
                            'UPDATE transitions SET count=? WHERE order_n=? AND state=? AND next_word=?',
                            (count, order, state, next_word)
                        )
                    else:
                        self.conn.execute(
                            'INSERT INTO transitions (order_n, state, next_word, count) VALUES (?, ?, ?, 1)',
                            (order, state, next_word)
                        )

    def _get_next_word(self, state_tokens):
        """
        Try to get next word for given state tokens with backoff.
        """
        for order in reversed(range(1, len(state_tokens) + 1)):
            state = ' '.join(state_tokens[-order:])
            cur = self.conn.execute(
                'SELECT next_word, count FROM transitions WHERE order_n=? AND state=?',
                (order, state)
            )
            results = cur.fetchall()
            if results:
                words, counts = zip(*results)
                total = sum(counts)
                probabilities = [c / total for c in counts]
                next_word = random.choices(words, weights=probabilities, k=1)[0]
                return next_word
        return None

    def generate(self, seed=None, max_length=50):
        if seed:
            seed_tokens = self.tokenize(seed)
            # Use last max_order tokens of seed or less
            state_tokens = seed_tokens[-self.max_order:] if len(seed_tokens) >= self.max_order else seed_tokens
        else:
            # Pick random starting state from max order
            cur = self.conn.execute(
                'SELECT state FROM transitions WHERE order_n=? ORDER BY RANDOM() LIMIT 1',
                (self.max_order,)
            )
            row = cur.fetchone()
            if not row:
                return ""
            state_tokens = row[0].split()

        output = list(state_tokens)

        for _ in range(max_length - len(state_tokens)):
            next_word = self._get_next_word(output)
            if not next_word:
                break
            output.append(next_word)
            if next_word in self.END_TOKENS:
                break  # Stop at sentence end

        # Post-process output: attach punctuation properly and capitalize sentences
        final_tokens = []
        capitalize_next = True
        for token in output:
            if token in self.END_TOKENS or token in {',', ';', ':', '-', '"', "'"}:
                if final_tokens:
                    final_tokens[-1] += token
                else:
                    final_tokens.append(token)
                if token in self.END_TOKENS:
                    capitalize_next = True
            else:
                if capitalize_next:
                    token = token.capitalize()
                    capitalize_next = False
                final_tokens.append(token)

        return ' '.join(final_tokens)
    
    def close(self):
        self.conn.close()
      
