import os
from ..models import EditableHTML, User, Instance
from flask_login import current_user, login_required
from . import main
from .. import db
import stripe
from app import csrf
from ..account.forms import RegistrationForm
from flask import flash, redirect, render_template, request, url_for, jsonify
from ..email import send_email
from flask_rq import get_queue
import random
import requests
import json

stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
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


@main.route('/get-status/<app_id>/<auth>')
def get_status(app_id, auth):
    with requests.Session() as s:
        s.trust_env = False
        new_h = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % auth,
            "Accept": "application/vnd.heroku+json; version=3"
        }
        print(new_h)
        status = s.get('https://api.heroku.com/app-setups/{}'.format(app_id), headers=new_h)
        print(status.request.headers)
        status = status.text
    return status


@main.route('/launch/<auth>', methods=['GET', 'POST'])
@login_required
def launch(auth):
    with requests.Session() as s:
        txt = auth
        new_h = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % txt,
            "Accept": "application/vnd.heroku+json; version=3"
        }
        password = generate_password()
        data = {
            "source_blob": {
                "url": "https://github.com/hack4impact/maps4all/tarball/master"
            }, 
            "overrides": {
                "env": {
                    "MAIL_USERNAME": os.environ['MAIL_USERNAME'],
                    "MAIL_PASSWORD": os.environ['MAIL_PASSWORD'],
                    "TWILIO_AUTH_TOKEN": os.environ['TWILIO_AUTH_TOKEN'],
                    "TWILIO_ACCOUNT_SID": os.environ['TWILIO_ACCOUNT_SID'],
                    "ADMIN_EMAIL": current_user.email,
                    "ADMIN_PASSWORD": password
                }
            }
        }
        new_app = s.post('https://api.heroku.com/app-setups', 
                         headers=new_h, data=json.dumps(data)
                         ).text

        print(new_app)
        
        app_id = json.loads(new_app)['id']
        app_url = json.loads(new_app)['app']['name']
        
        status = s.get('https://api.heroku.com/app-setups/{}'.format(app_id), headers=new_h).text
        instance = Instance(name=app_url, owner_id=current_user.id, email=current_user.email, default_password=password, app_id=app_id)
        db.session.add(instance)
        db.session.commit()
    return render_template('main/launch.html', status=status, app_id=app_id, auth=auth, instance=instance)

    
def generate_password():
    s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    passlen = 8
    p =  "".join(random.sample(s,passlen ))
    return p

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
            'client_secret': os.environ['HEROKU_OAUTH_SECRET']
        }).text
        res = json.loads(res)
        txt = res['access_token']
    return redirect(url_for('main.launch', auth=txt))
