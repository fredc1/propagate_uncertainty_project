from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class ExpressionForm(FlaskForm):
    expr = StringField('', validators=[DataRequired()])
    submit = SubmitField('Propagate!')
