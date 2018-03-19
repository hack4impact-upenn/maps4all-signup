from flask_wtf import Form
from wtforms.validators import InputRequired, Length
from wtforms.fields import StringField, SubmitField

from ..models import Instance


class LaunchInstanceForm(Form):
    url = StringField(
        'Application URL',
        validators=[InputRequired(), Length(1, 32)],
        description="Pick a URL for your app, which can be changed later. \
        You may only use letters, numbers, and dashes."
    )
    submit = SubmitField('Create app')

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
            self.url.errors.append(
                'You may only use letters, numbers, and dashes.')
            return False
        if url_name == 'www':
            self.url.errors.append('Invalid subdomain URL.')
            return False
        if Instance.query.filter_by(url_name=url_name).count() > 0:
            self.url.errors.append(
                'The URL http://{}.maps4all.org is already in use.'
                .format(url_name))
            return False
        return True
