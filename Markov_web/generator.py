def load_text_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()
