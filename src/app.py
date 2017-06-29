# -*- coding: utf-8 -*-
import os
import random
import json
from flask import Flask, flash, request, make_response, current_app, redirect, Response, url_for, render_template, abort
from werkzeug.utils import secure_filename
from datetime import timedelta
from functools import update_wrapper
from gen import generate_from_text



dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = dir_path + "/teksty"
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False
# cors = CORS(app, resources={r"/rand": {"origins": "*"}})


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, list):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, list):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def tadeoa():
    files = [name for name in os.listdir(UPLOAD_FOLDER) if name != '.DS_Store']
    file = 'CHOOSE ABOVE'
    gm = {'text':''}
    num = 1
    if request.method == 'POST':
        if not request.form.get('random', None):
            num = request.form.get('quantity')
            file = request.form.get('book')
            if '..' in file:
                file = random.choice(files)    
        else:
            file = random.choice(files)
            num = random.randint(1,10)
        gm = generate_from_text(file="teksty/" + file, num=int(num), prnt=0)

    return render_template("index.html", files=files, gm=gm['text'], org=file, num=num)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file',
                                    filename=filename))

    os.system('tree -C -h teksty/ | aha |  tr "\n" "|" | grep -o "<pre>.*</pre>" | tr "|" "\n" > templates/lib.html')
    
    return render_template("teksty.html")

@app.route('/rand', methods=['GET'])
@crossdomain(origin='*')
def get_random():
    try:
        files = [name for name in os.listdir(UPLOAD_FOLDER) if not name.startswith('.')]
        file = random.choice(files)
        num = random.randint(1,10)
        print(num)
        gm = generate_from_text(file=UPLOAD_FOLDER + "/" + file, num=num, prnt=0)
    except Exception as e:
        print('API ERROR', e)
        gm = {'text': "Error"}
        # abort(404)
    js = json.dumps({'source': file,'data': gm, 'len': num}, indent=2, ensure_ascii=False)
    resp = Response(js, status=200, mimetype='application/json; charset=utf-8')
    return resp


if __name__ == '__main__':
    # print(dir_path, UPLOAD_FOLDER)
    app.run(debug=1,host='0.0.0.0')
