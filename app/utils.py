from flask import url_for, current_app
from flask_login import current_user

from . import db

import requests

def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)


def get_heroku_token(s, refresh_token, heroku_secret):
    """Exchanges a heroku_refresh_token for a session_token

    :s is a requests.Session object
    :refresh_token is the heroku refresh token
    :heroku_secret is the heroku client secret
    """

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_secret': heroku_secret
    }

    resp = s.post('https://id.heroku.com/oauth/token', data=data)
    # TODO: ALL requests should always be raised for status. Make changes
    # elsewhere.

    resp.raise_for_status()

    return resp.json()['access_token']


def check_user_verified_status():
    with requests.Session() as s:
        s.trust_env = False
        auth = get_heroku_token(
            s,
            current_user.heroku_refresh_token,
            current_app.config['HEROKU_CLIENT_SECRET']
        )

        headers = {
            'Authorization': 'Bearer {}'.format(auth),
            'Accept': 'application/vnd.heroku+json; version=3'
        }

        resp = s.get(
            'https://api.heroku.com/users/{}'.format(current_user.heroku_user_id),
            headers=headers,
        )

        verified = resp.json()['verified']
        current_user.heroku_verified = verified
        db.session.add(current_user)
        db.session.commit()

        return verified
