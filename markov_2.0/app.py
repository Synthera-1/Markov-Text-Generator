from flask import Flask, request, jsonify, render_template
import sqlite3
import random
import re

app = Flask(__name__)

DB = 'markov.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS transitions (
        prefix TEXT,
        next_word TEXT,
        count INTEGER,
        PRIMARY KEY (prefix, next_word)
    )
    ''')
    conn.commit()
    conn.close()

def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()

def train(text, n):
    text = clean_text(text)
    words = text.split()
    if len(words) < n + 1:
        return
    
    conn = get_db()
    c = conn.cursor()

    for i in range(len(words) - n):
        prefix = ' '.join(words[i:i+n])
        next_word = words[i+n]
        
        c.execute('SELECT count FROM transitions WHERE prefix=? AND next_word=?', (prefix, next_word))
        row = c.fetchone()
        if row:
            c.execute('UPDATE transitions SET count=count+1 WHERE prefix=? AND next_word=?', (prefix, next_word))
        else:
            c.execute('INSERT INTO transitions (prefix, next_word, count) VALUES (?, ?, 1)', (prefix, next_word))
    
    conn.commit()
    conn.close()

def predict_next(prefix):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT next_word, count FROM transitions WHERE prefix=?', (prefix,))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return None
    
    total = sum(row['count'] for row in rows)
    r = random.randint(1, total)
    upto = 0
    for row in rows:
        upto += row['count']
        if upto >= r:
            return row['next_word']
    return None

def generate_text(start_text, n, length=20):
    start_text = clean_text(start_text)
    words = start_text.split()
    if len(words) < n:
        return f"Please enter at least {n} words to start."
    
    output_words = words[:]
    prefix_words = words[-n:]

    for _ in range(length):
        prefix = ' '.join(prefix_words)
        next_word = predict_next(prefix)
        if not next_word:
            break
        output_words.append(next_word)
        prefix_words = output_words[-n:]
    return ' '.join(output_words)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/train', methods=['POST'])
def train_route():
    data = request.json
    text = data.get('text', '')
    n = data.get('n', 3)
    try:
        n = int(n)
        if n < 1 or n > 10:
            return jsonify({"status": "error", "message": "n must be between 1 and 10."}), 400
    except:
        return jsonify({"status": "error", "message": "Invalid n value."}), 400
    
    train(text, n)
    return jsonify({"status": "success", "message": f"Model trained on given text with n={n}."})

@app.route('/predict', methods=['POST'])
def predict_route():
    data = request.json
    start_text = data.get('start_text', '')
    n = data.get('n', 3)
    try:
        n = int(n)
        if n < 1 or n > 10:
            return jsonify({"status": "error", "message": "n must be between 1 and 10."}), 400
    except:
        return jsonify({"status": "error", "message": "Invalid n value."}), 400
    
    if len(start_text.split()) < n:
        return jsonify({"status": "error", "message": f"Enter at least {n} words to start prediction."}), 400
    
    generated = generate_text(start_text, n, length=20)
    return jsonify({"status": "success", "generated_text": generated})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
