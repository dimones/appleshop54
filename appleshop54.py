from flask import *

app = Flask(__name__)
from flask_admin import Admin
admin = Admin(app, name='appleshop54', template_mode='bootstrap3')


@app.route('/')
def main():
    return render_template('index.html',body=render_template('main.html'))

@app.route('/contacts')
def contacts():
    return render_template('index.html',body=render_template('page.html'))


@app.route('/f32d73dc8d1d.html')
def f32d73dc8d1d():
    return 'a1a24e65907a'

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
