from flask import flash, redirect, render_template, current_app, url_for
from flask_wtf.csrf import generate_csrf
from flask_rq import get_queue
from flask_login import current_user, login_required
from urllib.parse import quote
from app import csrf

from . import instances
from ..utils import get_heroku_token, register_subdomain, update_subdomain
from .forms import LaunchInstanceForm, ChangeSubdomainForm
from ..models import Instance
from ..decorators import heroku_auth_required
from .. import db
from ..email import send_email

import string
import random
import requests


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
        # App name and URL
        url_name = form.url.data.lower()

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
                'Accept': 'application/vnd.heroku+json; version=3',
                'Content-Type': 'application/json'
            }

            data = {
                'source_blob': {
                    'url': 'https://github.com/hack4impact/maps4all/tarball/master'  # noqa
                },
                'overrides': {
                    'env': {
                        'ADMIN_EMAIL': username_in_app,
                        'ADMIN_PASSWORD': password_in_app,
                    }
                }
            }

            resp = s.post(
                'https://api.heroku.com/app-setups',
                headers=headers,
                json=data
            )

            resp.raise_for_status()

            app_id = resp.json()['app']['id']
            app_setup_id = resp.json()['id']
            app_name = resp.json()['app']['name']  # heroku app name

            instance = Instance(
                name=app_name,
                url_name=url_name,
                owner_id=current_user.id,
                email=username_in_app,
                default_password=password_in_app,
                app_id=app_id
            )
            db.session.add(instance)
            db.session.commit()

            register_subdomain(instance)

            return render_template(
                'instances/launch_status.html',
                app_setup_id=app_setup_id,
                auth=auth,
                instance=instance,
                email=username_in_app,
                password=password_in_app,
                name=url_name)

    return render_template('instances/launch_form.html', form=form)


@instances.route('/_get-status/<app_setup_id>/<auth>')
def get_status(app_setup_id, auth):
    with requests.Session() as s:
        s.trust_env = False
        headers = {
            'Authorization': 'Bearer {}'.format(auth),
            'Accept': 'application/vnd.heroku+json; version=3'
        }
        resp = s.get('https://api.heroku.com/app-setups/{}'
                     .format(app_setup_id), headers=headers)
        resp.raise_for_status()

    return resp.text

@csrf.exempt
@instances.route('/send-admin-email/<email>/<password>/<name>', methods=['GET', 'POST'])
def send_admin_email(email, password, name):
    print("HANA GETTING TO SEND ADMIN EMAIL")
    get_queue().enqueue(
        send_email,
        recipient=current_user.email,
        subject='Admin Login Information',
        template='instances/email/admin_login_info',
        full_name=current_user.full_name(),
        url_name=name,
        email=current_user.email,
        default_password=password)


@instances.route('/')
@login_required
def view_instances():
    """Page for users to manage and view their instances"""
    instances = Instance.query.filter_by(owner_id=current_user.id)
    return render_template('instances/index.html', instances=instances)


@instances.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def manage(id):
    instance = Instance.query.filter_by(id=id).first()
    if not instance or instance.owner_id != current_user.id:
        return render_template('errors/403.html'), 403
    subdomain_form = ChangeSubdomainForm(url=instance.url_name)
    if subdomain_form.validate_on_submit():
        new_url_name = subdomain_form.url.data
        if new_url_name == instance.url_name:
            return redirect(url_for('instances.manage', id=id))
        elif new_url_name == 'www' \
                or Instance.query.filter_by(url_name=new_url_name).count() > 0:
            flash('The URL http://{}.maps4all.org is already taken.'
                  .format(new_url_name), 'form-error')
        else:
            # register new subdomain
            update_subdomain(new_url_name, instance)
            instance.url_name = new_url_name
            db.session.add(instance)
            db.session.commit()
            flash('Changed subdomain to <a href="http://{}.maps4all.org"> \
                    http://{}.maps4all.org</a>'.format(instance.url_name,
                                                       instance.url_name),
                  'form-success')
            return redirect(url_for('instances.manage', id=id))
    return render_template('instances/manage.html',
                           instance=instance,
                           subdomain_form=subdomain_form)
