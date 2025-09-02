import argparse
from markov import MarkovChain
from generator import load_text_file

def main():
    parser = argparse.ArgumentParser(description="Markov Chain Text Generator")
    parser.add_argument('--input', type=str, required=True, help='Input text file path')
    parser.add_argument('--order', type=int, default=2, help='Markov chain order')
    parser.add_argument('--length', type=int, default=50, help='Number of words to generate')
    parser.add_argument('--interactive', action='store_true', help='Generate text word-by-word interactively')
    args = parser.parse_args()

    text = load_text_file(args.input)
    mc = MarkovChain(order=args.order)
    mc.train(text)

    if args.interactive:
        # Start with a random state
        state = random.choice(list(mc.model.keys()))
        output = list(state)
        print(' '.join(output), end='', flush=True)

        for _ in range(args.length - args.order):
            next_word = mc.generate_one_word(state)
            if next_word is None:
                break
            print(' ' + next_word, end='', flush=True)
            output.append(next_word)
            state = tuple(output[-args.order:])
        print()
    else:
        generated_text = mc.generate(length=args.length)
        print("\nGenerated Text:\n")
        print(generated_text)

if __name__ == '__main__':
    main()
