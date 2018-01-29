from flask import url_for, current_app
from flask_login import current_user

import CloudFlare
import requests

from . import db


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
            'https://api.heroku.com/users/{}'.format(
                current_user.heroku_user_id),
            headers=headers,
        )

        resp.raise_for_status()

        verified = resp.json()['verified']
        current_user.heroku_verified = verified
        db.session.add(current_user)
        db.session.commit()

        return verified


def register_subdomain(instance):
    """
    :instance is the heroku instance to register a subdomain for
    """

    custom_domain = '{}.maps4all.org'.format(instance.url_name)

    # First, we ask heroku to create the domain.

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

        resp = s.post(
            'https://api.heroku.com/apps/{}/domains'.format(instance.app_id),
            headers=headers,
            data={'hostname': custom_domain}
        )

        resp.raise_for_status()

        target = resp.json()['cname']

    # Second, we actually create the subdomain.
    cf = CloudFlare.CloudFlare(
        current_app.config['CF_API_EMAIL'],
        current_app.config['CF_API_KEY'])

    dns_record = {
        'type': 'CNAME',
        'name': instance.url_name,
        'content': target,
    }

    cf.zones.dns_records.post(
        current_app.config['CF_ZONE_IDENT'],
        data=dns_record)
