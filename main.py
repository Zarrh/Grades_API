from flask import Flask
from flask import request
from scraper import get_grades

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Grades API'

@app.route('/retrieve', methods=['POST'])
def retrieve():
    if request.form['username'] and request.form['password'] and request.form['school_code']:
        return get_grades(request.form['username'], request.form['password'], request.form['school_code'])
    return "Invalid request"