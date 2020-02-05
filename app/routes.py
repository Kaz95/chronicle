from flask import render_template
from app import app


@app.route('/')
@app.route('/home')
def home():
    who = 'World'
    return render_template('home.html', title='Home', who=who)
