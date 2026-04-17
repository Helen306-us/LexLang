from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import sys

# Agregar el directorio 'files' a sys.path para poder importar lexlang
sys.path.append(os.path.join(os.path.dirname(__file__), 'files'))
from lexlang import Interpreter

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'lexlang.html')

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    
    interp = Interpreter()
    results = interp.run(code)
    
    return jsonify(results)

if __name__ == '__main__':
    print("Iniciando servidor LexLang en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
