from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class NewPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),
                        Length(max=64)])
    headline = StringField('Headline', validators=[DataRequired(),
                           Length(max=64)])
    body = TextAreaField('Body', validators=[DataRequired()])
