from flask import Flask
from forms import ExpressionForm
from flask import render_template, flash, redirect, request
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/', methods=['GET'])
def index():

    return render_template('index.html', title='form title', expr="", with_results=False)


@app.route('/submit_expression', methods=['GET', 'POST'])
def submit_expression():
    expression = request.form['expression']
    vars = ['x','y']
    uploadtype = "manual"
    print(expression)
    return render_template('variables.html', title='form title', variables=vars, variable_string=uploadtype, with_results=False)


@app.route('/input_variables')
def format_variable_input():
    expression = request.args['expr']
    #for character in expression, add that character to a struct that will be passed to the template that will generate input fields for every variable
    #then one button will submit them all and go to another route that will perform the calculation and will redirect to the results page with a link
    #to go back to the home page and start over the process.

    return redirect(f'/input_variables')


@app.route('/result', methods = ['GET', 'POST'])
def format_result():
    pass


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
