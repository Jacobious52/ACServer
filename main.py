from build import compile_files
import problem
from flask import Flask
from flask import request, make_response, current_app
from flask import jsonify
from datetime import timedelta
from functools import update_wrapper
import student
from student import Student
from multiprocessing import cpu_count

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
    resp = jsonify({"status": "It's Working!"})
    resp.status_code = 200
    return resp

@app.before_request
def option_autoreply():
    '''this allows Cross Site Requests'''
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
    '''this allows Cross Site Requests'''
    h = resp.headers
    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
    return resp

@app.route('/user/id/<id>', methods=['GET'])
def user(id):
    resp = jsonify(Student(id).dict)
    resp.status_code = 200
    return resp

@app.route('/users', methods=['GET'])
def users():
    resp = jsonify({'users': student.list_all()})
    resp.status_code = 200
    return resp

@app.route('/build/id/<id>', methods=['POST'])
def build(id):
    '''POST request for a build. id as arg and files json as body'''
    resp = jsonify({'message':'fail'})
    resp.status_code = 405
    if request.headers['Content-Type'] == 'application/json':
        if 'files' in request.json:
            err = compile_files(request.json['files'])

            # log to student model
            s = Student(id)
            s.create_action_build(request.json['problem'], request.json['files'], err)
            s.sync()

            resp = jsonify({'errors': err})
            resp.status_code = 200
    return resp

@app.route('/problems/id/<id>', methods=['GET'])
def problems(id):
    '''GET request for problems set'''

    # log to student model
    s = Student(id)
    s.create_action_refresh_problems()
    s.sync()

    # return problems back to client
    resp = jsonify({'problems': problem.PROBLEMS})
    resp.status_code = 200
    return resp

@app.route('/login/id/<id>', methods=['GET'])
def login(id):
    '''GET request for login. currently used just for logging'''

    # log to student model
    s = Student(id)
    s.create_action_login()
    s.sync()

    # return problems back to client
    resp = jsonify({'status': 'ok'})
    resp.status_code = 200
    return resp

@app.route('/logout/id/<id>', methods=['GET'])
def logout(id):
    '''GET request for logout. currently used just for logging'''

    # log to student model
    s = Student(id)
    s.create_action_logout()
    s.sync()

    # return problems back to client
    resp = jsonify({'status': 'ok'})
    resp.status_code = 200
    return resp

@app.route('/question/id/<id>/q/<q>', methods=['GET'])
def question(id, q):
    '''GET request for change question. just used for logging'''

    # log to student model
    s = Student(id)
    s.create_action_question(q)
    s.sync()

    # return problems back to client
    resp = jsonify({'status': 'ok'})
    resp.status_code = 200
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, processes=cpu_count())
