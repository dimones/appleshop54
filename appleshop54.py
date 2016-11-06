from flask import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/f32d73dc8d1d.html')
def f32d73dc8d1d():
    return render_template('ya.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
