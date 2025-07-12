import sys
from pathlib import Path
from flask import Flask, render_template

ROOT_DIR = Path(__file__).resolve().parent.parent

from pik_utils.json_func import load_json_data 

app = Flask(__name__)
    
@app.route('/')
def index():
    projects = load_json_data()
    return render_template('index.html', projects=projects)

if __name__ == '__main__':
    app.run(debug=True)