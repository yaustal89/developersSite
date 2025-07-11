import sys
from pathlib import Path
from flask import Flask, render_template

ROOT_DIR = Path(__file__).resolve().parent.parent
PIK_PARSER_DIR = ROOT_DIR / "pik_parser"

sys.path.append(str(ROOT_DIR))
from pik_parser.pikParser import load_json_data

JSON_FILE = ROOT_DIR / "pik_parser" / "pik_projects_full.json"

app = Flask(__name__)
    
@app.route('/')
def index():
    projects = load_json_data(JSON_FILE)
    return render_template('index.html', projects=projects)

if __name__ == '__main__':
    app.run(debug=True)