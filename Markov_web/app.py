from flask import Flask, render_template, request
from markov import MarkovChain

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_text = ''
    if request.method == 'POST':
        input_text = request.form.get('input_text')
        order = int(request.form.get('order', 2))
        length = int(request.form.get('length', 50))

        if input_text:
            mc = MarkovChain(order=order)
            mc.train(input_text)
            generated_text = mc.generate(length=length)

    return render_template('index.html', generated_text=generated_text)

if __name__ == '__main__':
    app.run(debug=True)
