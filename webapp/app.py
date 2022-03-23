from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title="Info Viz Example", paragraph_title="Testing123")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)