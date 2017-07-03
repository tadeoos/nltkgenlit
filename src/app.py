#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import traceback
from logging.handlers import RotatingFileHandler
from flask import Flask, flash, request, make_response, current_app, redirect, Response, url_for, render_template, abort
from werkzeug.utils import secure_filename
from datetime import timedelta
from functools import update_wrapper
from gen import generate_from_text, generate_cache



dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = dir_path + "/teksty"
ALLOWED_EXTENSIONS = set(['txt'])

sdir = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), 'static')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False
app.config["APPLICATION_ROOT"] = "/epygone"

handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)


def get_files():
    return [name for name in os.listdir(UPLOAD_FOLDER) if not name.startswith('.')]

TEXT_CACHE = generate_cache(UPLOAD_FOLDER, get_files())
# cors = CORS(app, resources={r"/rand": {"origins": "*"}})
# print(TEXT_CACHE)

def parse_tadeoa(rand=True, **kwargs):
    files = get_files()
    if rand:
        file = random.choice(files)
        num = random.randint(2, 8)
    else:
        book = kwargs.get('book', 'pl-szulc-sklepy.txt')
        try:
            file = [b for b in files if b.startswith(book)][0]
        except Exception:
            app.logger.error('An error occurred in parse_tadeoa')
            print('raised')
            raise
        num = kwargs.get('sents', 2)
    return (generate_from_text(file=UPLOAD_FOLDER + "/" + file, num=num, prnt=0, cache=TEXT_CACHE), file, num)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def tadeoa():
    files = sorted([name for name in os.listdir(UPLOAD_FOLDER) if name != '.DS_Store'])
    file = 'CHOOSE ABOVE'
    gm = {'text': ''}
    num = 1
    return render_template("index.html", files=files, gm=gm['text'], org=file, num=num)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    files = [name for name in os.listdir(
        UPLOAD_FOLDER) if not name.startswith('.')]
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
            return redirect('/epygone/upload')

    return render_template("teksty.html", files=files)


@app.route('/api', methods=['GET'])
def api():
    return render_template("api.html")

@app.route('/api/rand', methods=['GET'])
def api_random():
    try:
        gm, file, num = parse_tadeoa()
        status = 200
    except Exception as e:
        print('API ERROR', e)
        print(traceback.print_exc())
        app.logger.error('api/rand error: {}'.format(traceback.print_exc()))
        gm = {'text': "Error"}
        file = "error"
        num = 0
        status = 500

    js = json.dumps({'source': file, 'data': gm, 'len': num},
                    indent=2, ensure_ascii=False)
    resp = Response(js, status=status, mimetype='application/json; charset=utf-8')
    return resp

@app.route('/api/books', methods=['GET'])
def api_books():
    files = sorted([name for name in os.listdir(UPLOAD_FOLDER) if not name.startswith('.')])
    js = json.dumps({'books': files},
                    indent=2, ensure_ascii=False)
    resp = Response(js, status=200, mimetype='application/json; charset=utf-8')
    return resp

@app.route('/api/<string:book>/<int:sents>', methods=['GET'])
def api_go(book, sents):
    try:
        gm, file, num = parse_tadeoa(rand=0, book=book, sents=sents)
        status = 200
    except Exception as e:
        print('API ERROR', e)
        print(traceback.print_exc())
        app.logger.error('api/custom error: {}'.format(traceback.print_exc()))
        gm = {'text': "Error"}
        file = book
        num = sents
        status = 500
        # abort(404)
    js = json.dumps({'source': file, 'data': gm, 'len': num},
                    indent=2, ensure_ascii=False)
    resp = Response(js, status=status, mimetype='application/json; charset=utf-8')
    return resp


# if __name__ == '__main__':
#     # print(dir_path, UPLOAD_FOLDER)
#     app.run(debug=1, host='0.0.0.0')
