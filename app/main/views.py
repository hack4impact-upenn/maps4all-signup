import os
from ..models import EditableHTML, User, Instance
from flask_login import current_user, login_required
from . import main
from .. import db
import stripe
from app import csrf
from ..account.forms import RegistrationForm
from flask import flash, redirect, render_template, request, url_for, current_app
from ..email import send_email
from flask_rq import get_queue
import random
import requests
import json

# TODO: delete these, or make them formally part of config. Before they were
# coming straight from environment variables.
stripe_keys = {
  'secret_key': 'abc123',
  'publishable_key': 'abc123'
}

stripe.api_key = stripe_keys['secret_key']


@main.route('/', methods=['GET', 'POST'])
def index():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        confirm_link = url_for('account.confirm', token=token, _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='Confirm Your Account',
            template='account/email/confirm',
            user=user,
            confirm_link=confirm_link)
        flash('A confirmation link has been sent to {}.'.format(user.email),
              'warning')
        return redirect(url_for('main.index'))
    return render_template('main/index.html', form=form)


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)


@main.route('/faq')
def faq():
    editable_html_obj = EditableHTML.get_editable_html('faq')
    return render_template('main/faq.html',
                           editable_html_obj=editable_html_obj)


@main.route('/start/<name>', methods=['POST'])
@main.route('/start', methods=['POST'])
@csrf.exempt
def start(name):
    instance = Instance.query.filter_by(name=name).first()
    instance.start_container()
    return "OK", 200


@main.route('/stop/<name>', methods=['POST'])
@main.route('/stop', methods=['POST'])
@csrf.exempt
def stop(name):
    instance = Instance.query.filter_by(name=name).first()
    instance.stop_container()
    print("RUNNING STATUS {}".format(instance.is_running))
    return "OK", 200


@main.route('/partners')
def partners():
    editable_html_obj = EditableHTML.get_editable_html('faq')
    return render_template('main/partners.html',
                           editable_html_obj=editable_html_obj)


@main.route('/auth/heroku/callback/')
def cb():
    with requests.Session() as s:
        s.trust_env = False
        code = request.args.get('code')
        res = s.post('https://id.heroku.com/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_secret': current_app.config['HEROKU_CLIENT_SECRET']
        })
        res.raise_for_status()

        res_json = res.json()
        refresh_token = res_json['refresh_token']
        current_user.heroku_refresh_token = refresh_token
        db.session.add(current_user)
        db.session.commit()

    return redirect(url_for('instances.launch'))
