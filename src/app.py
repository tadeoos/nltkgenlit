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

sdir = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), 'static')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False
# cors = CORS(app, resources={r"/rand": {"origins": "*"}})


def parse_tadeoa(rand=True, **kwargs):
    files = [name for name in os.listdir(
        UPLOAD_FOLDER) if not name.startswith('.')]
    if rand:
        file = random.choice(files)
        num = random.randint(2, 8)
    else:
        book = kwargs.get('book', 'pl-szulc-skepy.txt')
        try:
            file = [b for b in files if b.startswith(book)][0]
        except Exception:
            print('raised')
            raise
        num = kwargs.get('sents', 2)
    return (generate_from_text(file=UPLOAD_FOLDER + "/" + file, num=num, prnt=0), file, num)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def tadeoa():
    files = [name for name in os.listdir(UPLOAD_FOLDER) if name != '.DS_Store']
    file = 'CHOOSE ABOVE'
    gm = {'text': ''}
    num = 1
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


@app.route('/api', methods=['GET'])
def api():
    return render_template("api.html")

@app.route('/api/rand', methods=['GET'])
# @crossdomain(origin='*')
def api_random():
    try:
        gm, file, num = parse_tadeoa()
    except Exception as e:
        print('API ERROR', e)
        gm = {'text': "Error"}
        # abort(404)
    js = json.dumps({'source': file, 'data': gm, 'len': num},
                    indent=2, ensure_ascii=False)
    resp = Response(js, status=200, mimetype='application/json; charset=utf-8')
    return resp


@app.route('/api/<string:book>/<int:sents>', methods=['GET'])
# @crossdomain(origin='*')
def api_go(book, sents):
    try:
        gm, file, num = parse_tadeoa(rand=0, book=book, sents=sents)
    except Exception as e:
        print('API ERROR', e)
        gm = {'text': "Error"}
        # abort(404)
    js = json.dumps({'source': file, 'data': gm, 'len': num},
                    indent=2, ensure_ascii=False)
    resp = Response(js, status=200, mimetype='application/json; charset=utf-8')
    return resp


if __name__ == '__main__':
    # print(dir_path, UPLOAD_FOLDER)
    app.run(debug=1, host='0.0.0.0')
