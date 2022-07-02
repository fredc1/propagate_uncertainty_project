from flask import Flask
from forms import ExpressionForm
from flask import render_template, flash, redirect, request
from config import Config
from expression import Expression

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/submit_expression', methods=['GET', 'POST'])
def parse_expression_and_get_input():
    expr_str = request.form['expression']
    try:
        expr_obj = Expression(expr_str)
    except ValueError:
        explain = "one of the words used in your expression is not a legal input"
        return render_template('invalid_input.html', error_str=expr_str, lower_case_explanation_str=explain)
    expr_vars = expr_obj.get_variables()
    upload_type = "manual"
    return render_template('variables.html', variables=expr_vars, expression=expr_str, variable_string=upload_type)


@app.route('/results', methods=['GET', 'POST'])
def get_results():
    expr_str = request.form['expression']


@app.route("/info")
def info():
    return render_template('info.html')


@app.route("/docs")
def docs():
    return render_template('docs.html')


def main():
    app.run(host="127.0.0.1", port=8080, debug=True)


if __name__ == '__main__':
    main()
