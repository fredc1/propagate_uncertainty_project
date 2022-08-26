import codecs
import csv

from flask import render_template, Flask, flash, request, redirect, url_for, session, send_file
from config import Config
from expression import Expression
from io import BytesIO

# TODO clean up user input handling ideally raise exceptions instead of sending to special page
#  and handle with flask builtin (use flash where makes sense)
# TODO fill function docs and do general code cleanup/refactor
# TODO update tests for expression API
# TODO cleanup and refine landing page instructions
# TODO cleanup and refine variables page (add picture with example for table)
# TODO Google Adds

ALLOWED_EXTENSIONS = {'csv'}

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
    except ValueError as e:
        explain = str(e) + " (Check Documentation Tab) "
        return render_template('invalid_input.html', error_str=expr_str, lower_case_explanation_str=explain)

    session['expr'] = expr_str
    expr_vars = expr_obj.get_variables()
    return render_template('variables.html', variables=expr_vars, expression=expr_str)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_prop_results_from_stream(stream, variables, columns, expression) -> BytesIO:
    results_strs_list = []
    header = ""
    for colname in columns:
        header += f'{colname},'

    header += f'{expression.user_str},expression_uncertainty\n'
    results_strs_list.append(header)
    for row in stream:
        values_arr = []
        result_str = ""

        for i in range(len(variables)):
            var_ind = 2 * i
            unc_ind = var_ind + 1
            values_arr.append((variables[i], row[var_ind], row[unc_ind]))
            result_str += f"{row[var_ind]},{row[unc_ind]},"

        prop_result = expression.propagate_uncertainty(values_arr).split("+/-")
        result_str += f"{prop_result[0]},{prop_result[1]}\n"
        results_strs_list.append(result_str)
    full_string = "".join(results_strs_list)
    f = BytesIO(bytes(full_string, encoding='utf-8'))
    return f


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    expr_str = session["expr"]
    try:
        expr_obj = Expression(expr_str)
    except ValueError as e:
        explain = str(e) + " (Check Documentation Tab) "
        return render_template('invalid_input.html', error_str=expr_str, lower_case_explanation_str=explain)

    variables = expr_obj.get_variables()

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return render_template('invalid_input.html', error_str="file upload",
                                   lower_case_explanation_str="no file part")
            # flash('No file part')
            # return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return render_template('invalid_input.html', error_str="file upload",
                                   lower_case_explanation_str="no selected file")
            # flash('No selected file')
            # return redirect(request.url)
        if file and allowed_file(file.filename):
            stream = codecs.iterdecode(file.stream, 'utf-8')
            filereader = csv.reader(stream)
            columns = filereader.__next__()
            data_table = []
            for row in filereader:
                data_table.append(row)

            if len(columns) != 2 * len(variables):
                return render_template('invalid_input.html', error_str=columns.__repr__(),
                                       lower_case_explanation_str="there should be twice as many columns as variables "
                                                                  "in csv. one for each variable and one for each "
                                                                  "uncertainty directly adjacent")
            for i in range(len(columns)):
                if i % 2 == 0:
                    if not columns[i].isalpha():
                        return render_template('invalid_input.html', error_str=columns[i],
                                               lower_case_explanation_str=f"the first row must match the variable names spelling and this order: {variables.__repr__()}")
                    if columns[i] != variables[i // 2]:
                        return render_template('invalid_input.html', error_str=columns[i],
                                               lower_case_explanation_str=f"column names must match variable names and be in this order: {variables.__repr__()}")
            for row in data_table:
                for i in range(len(row)):
                    if i % 2 == 0 and not is_valid_float_or_int_pos_or_neg(row[i]):
                        return render_template('invalid_input.html', error_str=row[i],
                                               lower_case_explanation_str=f"value contains non numeric characters")
                    elif i % 2 == 1:
                        if not is_valid_float_or_int_pos_or_neg(row[i]):
                            return render_template('invalid_input.html', error_str=row[i],
                                                   lower_case_explanation_str=f"value contains non numeric characters")
                        if row[i][0] == '-':
                            return render_template('invalid_input.html', error_str=row[i],
                                                   lower_case_explanation_str=f"uncertainty cannot be negative")

            result_stream = get_prop_results_from_stream(data_table, variables, columns, expr_obj)
    return send_file(result_stream, mimetype='text/csv', as_attachment=True, download_name='results.csv')


def is_valid_float_or_int_pos_or_neg(num_str):
    if num_str[0] == '-':
        if len(num_str) < 2:
            return False
        num_str = num_str[1:]
    decimal_allowed = True
    for c in num_str:

        if not c.isdigit() and c != ".":
            return False
        if c == "." and not decimal_allowed:
            return False
        if c == ".":
            decimal_allowed = False
    return True


@app.route('/upload_single_measurement', methods=['GET', 'POST'])
def upload_single_measurement():
    expr_str = session["expr"]

    try:
        expr_obj = Expression(expr_str)
    except ValueError as e:
        explain = str(e) + " (Check Documentation Tab) "
        return render_template('invalid_input.html', error_str=expr_str, lower_case_explanation_str=explain)

    variables = expr_obj.get_variables()
    values_arr = []
    for var in variables:
        val = request.form[f'val_{var}']
        unc = request.form[f'unc_{var}']

        if not is_valid_float_or_int_pos_or_neg(val) or not is_valid_float_or_int_pos_or_neg(unc):
            return render_template('invalid_input.html', error_str=val + "+/-" + unc,
                                   lower_case_explanation_str="contains non numeric values")
        if unc[0] == '-':
            return render_template('invalid_input.html', error_str=unc,
                                   lower_case_explanation_str="uncertainty cannot be negative")
        values_arr.append((var, val, unc))

    result_str = expr_obj.propagate_uncertainty(values_arr)
    results = result_str.split("+/-")
    return render_template('result.html', results=results, expression=expr_str)


@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File Too Large', 413


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
