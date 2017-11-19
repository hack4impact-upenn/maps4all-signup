from flask import render_template, url_for, current_app, flash, redirect
from flask_wtf.csrf import generate_csrf
from flask_login import current_user, login_required
from urllib.parse import quote

from . import instances
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


def generate_secret(pass_len):
    s = string.ascii_letters + string.digits
    p = ''.join(random.SystemRandom().choice(s) for _ in range(pass_len))
    return p


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

            if resp.status_code == 422 and resp.json() is not None and \
               resp.json()['id'] == 'verification_needed':
                # TODO: Test this case before merging.
                flash('Your Heroku account is still unverified. Please \
                       verify it by adding a credit/debit card to your \
                       account. Read more at https://devcenter.heroku.com/articles/account-verification',  # noqa
                       'error')
                return redirect(url_for('instances.launch'))

            resp.raise_for_status()

            app_id = resp.json()['app']['id']
            app_setup_id = resp.json()['id']

            instance = Instance(
                name=name,
                owner_id=current_user.id,
                email=current_user.email,
                app_id=app_id
            )
            db.session.add(instance)
            db.session.commit()

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
            "Accept": "application/vnd.heroku+json; version=3"
        }
        resp = s.get('https://api.heroku.com/app-setups/{}'
                     .format(app_setup_id), headers=headers)
        resp.raise_for_status()

    return resp.text


@instances.route('/instances')
@login_required
def manage_instances():
    """Page for users to manage and view their instances"""
    instances = Instance.query.filter_by(owner_id=current_user.id)
    return render_template('instances/instances.html', instances=instances)
