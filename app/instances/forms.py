from flask_wtf import Form
from wtforms.validators import InputRequired, Length
from wtforms.fields import StringField, SubmitField
from wtforms import ValidationError

from ..models import Instance


class LaunchInstanceForm(Form):
    name = StringField(
        'App name',
        validators=[InputRequired(), Length(1, 32)],
        description='Name your app so you can identify it.'
        )
    submit = SubmitField('Create app')

    def validate_name(self, field):
        if Instance.query.filter_by(name=field.data).count() > 0:
            raise ValidationError('Instance name already registered.')


class ChangeSubdomainForm(Form):
    # must be instantiated by setting the "instance" field in views.py
    url = StringField(
        'New Application URL',
        validators=[InputRequired(), Length(1, 32)],
        description='Pick a new URL for your app. You may only use letters, numbers, and dashes.'
    )
    submit = SubmitField('Change subdomain')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        url_name = self.url.data.lower()
        if url_name[0] == '-' or url_name[-1] == '-':
            self.url.errors.append(
                'Your URL may not begin or end with "-" symbols.')
            return False
        if not all(c.isalnum() or c == '-' for c in url_name):
            self.url.errors.append('You may only use .')
            return False
        return True
