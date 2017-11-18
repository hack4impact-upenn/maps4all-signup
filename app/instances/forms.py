from flask_wtf import Form
from wtforms.validators import InputRequired, Length

from ..models import Instance

class LaunchInstanceForm(Form):
    name = StringField(
        'App name',
        validators=[InputRequired(), Length(1, 32)],
        description='Name your app so you can identify it.'
        )
    submit = SubmitField('Create App')

    def validate_name(self, field):
        if Instance.query.filter_by(name=field.data).count() > 0:
            raise ValidationError('Instance name already registered.')
