#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import sys
import traceback
from logging.handlers import RotatingFileHandler
from flask import Flask, flash, request, make_response, redirect, Response, url_for, render_template, abort
from werkzeug.utils import secure_filename
# from datetime import timedelta
# from functools import update_wrapper
from gen import generate_from_text
from cache import cache_file
from multiprocessing import Process, Queue
from pympler import asizeof
# from redis import Redis





dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = dir_path + "/teksty"
ALLOWED_EXTENSIONS = set(['txt'])

sdir = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), 'static')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False
app.config["APPLICATION_ROOT"] = "/epygone"

# redis = Redis(host='redis', port=6379)

handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)


def get_files():
    return sorted([name for name in os.listdir(UPLOAD_FOLDER) if not name.startswith('.')])


TEXT_CACHE = {}

for file in get_files():
    print('Caching {}...'.format(file))
    q = Queue()
    # p = Process(target=cache_file, args=(q, UPLOAD_FOLDER, file))
    cache_file(q, UPLOAD_FOLDER, file)
    # p.start()
    file_dict = q.get()
    print(type(file_dict))
    print(file_dict)
    # p.terminate()
    # p.join()

    key_name = '{}'.format(file)
    
    TEXT_CACHE.update({ key_name : file_dict })

print('CACHE SIZE: {} bytes'.format(asizeof.asizeof(TEXT_CACHE, detail=1)))


def parse_tadeoa(rand=True, **kwargs):
    redis.incr('hits')
    print('REDIS HITS: ', redis.get('hits'))
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
    res = generate_from_text(file=UPLOAD_FOLDER + "/" +
                             file, num=num, prnt=0, cache=TEXT_CACHE)
    return ((res[0], file, num), res[1])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def tadeoa():
    files = sorted([name for name in os.listdir(
        UPLOAD_FOLDER) if name != '.DS_Store'])
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
        gm, file, num = parse_tadeoa()[0]
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
    resp = Response(js, status=status,
                    mimetype='application/json; charset=utf-8')
    return resp


@app.route('/api/books', methods=['GET'])
def api_books():
    files = sorted([name for name in os.listdir(
        UPLOAD_FOLDER) if not name.startswith('.')])
    js = json.dumps({'books': files},
                    indent=2, ensure_ascii=False)
    resp = Response(js, status=200, mimetype='application/json; charset=utf-8')
    return resp


@app.route('/api/<string:book>/<int:sents>', methods=['GET'])
def api_go(book, sents):
    try:
        gm, file, num = parse_tadeoa(rand=0, book=book, sents=sents)[0]
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
    resp = Response(js, status=status,
                    mimetype='application/json; charset=utf-8')
    return resp


# if __name__ == '__main__':
#     # print(dir_path, UPLOAD_FOLDER)
#     app.run(debug=1, host='0.0.0.0')
