# -*- coding: utf-8 -*-
import os
import random
import json
from flask import Flask, flash, request, redirect, url_for, render_template, abort
from werkzeug.utils import secure_filename
from gen import generate_from_text

dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = dir_path + "/teksty"
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False

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
def get_random():
    try:
        files = [name for name in os.listdir(UPLOAD_FOLDER) if not name.startswith('.')]
        file = random.choice(files)
        num = random.randint(1,10)
        gm = generate_from_text(file=UPLOAD_FOLDER + "/" + file, num=num, prnt=0)
    except Exception as e:
        print('API ERROR', e)
        abort(404)
    return json.dumps({'source': file,'data': gm['raw']}, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    # print(dir_path, UPLOAD_FOLDER)
    app.run(debug=1,host='0.0.0.0')
