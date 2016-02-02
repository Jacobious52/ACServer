from flask import Flask
from flask import request, make_response, current_app
from flask import jsonify
import subprocess
from datetime import timedelta
from functools import update_wrapper


#TODO: make this into a class with student model and stuff
def compile_files(files):
    for f in files:
        with open(f['/tmp/name'], 'w') as file:
            file.write(f['body'])
    process = subprocess.Popen(["g++", ' '.join([f['name'] for f in files if not f['name'].endswith('.h')]), \
    '-o temp.o', '-Wall', '-Wextra', \
    '-pedantic' , \
    '-fdiagnostics-parseable-fixits'], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = process.communicate()
    return err.strip()

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/')
def index():
    return "It's Working!"

@app.before_request
def option_autoreply():
    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']
        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers
        return resp

@app.after_request
def set_allow_origin(resp):
    h = resp.headers
    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
    return resp


@app.route('/build/id/<id>', methods=['POST'])
def build(id):
    resp = jsonify({'message':'fail'})
    resp.status_code = 405
    if request.headers['Content-Type'] == 'application/json':
        if 'files' in request.json:
            err = compile_files(request.json['files'])
            resp = jsonify({'errors': err.split('clang:')})
            resp.status_code = 200
    print(resp)
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
