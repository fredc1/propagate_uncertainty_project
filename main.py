import codecs
import csv

from flask import Flask
from werkzeug.wsgi import wrap_file

from forms import ExpressionForm
from flask import render_template, Flask, flash, request, redirect, url_for, session, send_file
from config import Config
from expression import Expression
from io import BytesIO
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/submit_expression', methods=['GET', 'POST'])
def parse_expression_and_get_input():
    expr_str = request.form['expression']
    session['expr'] = expr_str
    try:
        expr_obj = Expression(expr_str)
    except ValueError:
        explain = "one of the words used in your expression is not a legal input. Remember each variable must a single lower or upper case letter."
        return render_template('invalid_input.html', error_str=expr_str, lower_case_explanation_str=explain)
    expr_vars = expr_obj.get_variables()
    return render_template('variables.html', variables=expr_vars, expression=expr_str)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_measurements', methods=['GET', 'POST'])
def upload_file():
    expr_str = session['expr']
    try:
        expr_obj = Expression(expr_str)
    except ValueError:
        explain = "one of the words used in your expression is not a legal input"
        return render_template('invalid_input.html', error_str=expr_str, lower_case_explanation_str=explain)

    variables = expr_obj.get_variables()

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return render_template('invalid_input.html', error_str="file upload", lower_case_explanation_str="no file part")
            #flash('No file part')
            #return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return render_template('invalid_input.html', error_str="file upload", lower_case_explanation_str="no selected file")
            #flash('No selected file')
            #return redirect(request.url)
        if file and allowed_file(file.filename):
            stream = codecs.iterdecode(file.stream, 'utf-8')
            filereader = csv.reader(stream)
            columns = filereader.__next__()

            if len(columns) != len(variables):
                return render_template('invalid_input.html', error_str=columns.__repr__(), lower_case_explanation_str="number of columns of csv do not match number of variables")
            for i in range(len(columns)):
                if not columns[i].isalpha():
                    return render_template('invalid_input.html', error_str=columns[i],
                                           lower_case_explanation_str=f"the first row must match the variable names spelling and this order: {variables.__repr__()}")
                if columns[i] != variables[i] and columns[i].lower() != variables[i] and columns[i] != variables[i].lower():
                    return render_template('invalid_input.html', error_str=columns[i],
                                           lower_case_explanation_str=f"column names must match variable names and be in this order: {variables.__repr__()}")
            for row in filereader:
                print(f"{row.__repr__()}\n")
    return "end for now"


@app.route("/info")
def info():
    return render_template('info.html')


@app.route("/docs")
def docs():
    return render_template('docs.html')

@app.route("/test_entry")
def test_route():
    return render_template('file_download.html')

@app.route("/file_download", methods=['GET', 'POST'])
def download():
    full_string = "a,b\n1,2\n3,4\n"
    f = BytesIO(bytes(full_string, encoding='utf-8'))
    return send_file(f, mimetype = 'text/csv', as_attachment=True, download_name = 'results.csv')

def main():
    app.run(host="127.0.0.1", port=8080, debug=True)


if __name__ == '__main__':
    main()
