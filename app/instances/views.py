from flask import render_template, current_app
from flask_wtf.csrf import generate_csrf
from flask_login import current_user, login_required
from urllib.parse import quote

from . import instances
from ..utils import get_heroku_token, register_subdomain
from .forms import LaunchInstanceForm
from ..models import Instance
from ..decorators import heroku_auth_required
from .. import db

import string
import random
import requests
import re


@instances.route('/heroku-authorize')
@login_required
def heroku_authorize():
    link = 'https://id.heroku.com/oauth/authorize?' +\
           'client_id={}&response_type=code&scope={}&state={}'.format(
            current_app.config['HEROKU_CLIENT_ID'], 'global',
            quote(generate_csrf()))
    return render_template('instances/heroku_authorize.html', oauth_link=link)


def generate_secret(pass_len):
    s = string.ascii_letters + string.digits
    p = ''.join(random.SystemRandom().choice(s) for _ in range(pass_len))
    return p


@instances.route('/verify-needed', methods=['GET'])
def require_verification():
    return render_template('instances/verify_needed.html')


@instances.route('/launch', methods=['GET', 'POST'])
@login_required
@heroku_auth_required
def launch():
    form = LaunchInstanceForm()
    if form.validate_on_submit():
        name = form.name.data

        username_in_app = current_user.email
        password_in_app = generate_secret(8)

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

            data = {
                'source_blob': {
                    'url': 'https://github.com/hack4impact/maps4all/tarball/master'  # noqa
                },
                'overrides': {
                    'env': {
                        # TODO: Doesn't this effectively leak our Twilio and
                        # Sendgrid accounts and put more load on our accounts?
                        'MAIL_USERNAME': current_app.config['MAIL_USERNAME'],
                        'MAIL_PASSWORD': current_app.config['MAIL_PASSWORD'],
                        'TWILIO_AUTH_TOKEN':
                            current_app.config['TWILIO_AUTH_TOKEN'],
                        'TWILIO_ACCOUNT_SID':
                            current_app.config['TWILIO_ACCOUNT_SID'],
                        'ADMIN_EMAIL': username_in_app,
                        'ADMIN_PASSWORD': password_in_app,
                    }
                }
            }

            herokuified_name = name.lower().replace(' ', '-')
            if re.match(r'^[a-z][a-z0-9-]{2,29}$', herokuified_name):
                data['app'] = {
                    'name': herokuified_name
                }

            resp = s.post(
                'https://api.heroku.com/app-setups',
                headers=headers,
                json=data
            )

            resp.raise_for_status()

            app_id = resp.json()['app']['id']
            app_setup_id = resp.json()['id']

            instance = Instance(
                name=name,
                url_name=herokuified_name,
                owner_id=current_user.id,
                email=current_user.email,
                app_id=app_id
            )
            db.session.add(instance)
            db.session.commit()

            # TODO: actually check that this is available, maybe even let user
            # config themselves
            register_subdomain(instance)

            return render_template('instances/launch_status.html',
                                   app_setup_id=app_setup_id, auth=auth)

    return render_template('instances/launch_form.html', form=form)


@instances.route('/_get-status/<app_setup_id>/<auth>')
def get_status(app_setup_id, auth):
    with requests.Session() as s:
        # TODO: why is trust_env false?
        s.trust_env = False
        headers = {
            'Authorization': 'Bearer {}'.format(auth),
            'Accept': 'application/vnd.heroku+json; version=3'
        }
        resp = s.get('https://api.heroku.com/app-setups/{}'
                     .format(app_setup_id), headers=headers)
        resp.raise_for_status()

    return resp.text


@instances.route('/')
@login_required
def manage_instances():
    """Page for users to manage and view their instances"""
    instances = Instance.query.filter_by(owner_id=current_user.id)
    return render_template('instances/instances.html', instances=instances)
