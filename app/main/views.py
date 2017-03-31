import os
from flask import render_template, request
from ..models import EditableHTML, User, Instance
from flask_login import current_user, login_required
from . import main
from .. import db
import stripe
from app import csrf

stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
}


stripe.api_key = stripe_keys['secret_key']
@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/pay')
@login_required
def pay():
  return render_template('main/pay.html', user=current_user,  key=stripe_keys['publishable_key'])


@main.route('/charge', methods=['POST'])
@login_required
@csrf.exempt
def charge():
    customer = stripe.Customer.create(
        email=current_user.email,
        source=request.form['stripeToken']
    )

    user = User.query.filter_by(email=current_user.email).first()
    user.stripe_id = customer.id
    db.session.commit()

    subscription = stripe.Subscription.create(
      customer=customer.id,
      plan="setup",
    )

    return render_template('main/charge.html')


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


@main.route('/launch/<name>')
@login_required
def launch(name):
    instance = Instance(name=name, owner=current_user)
    db.session.add(instance)
    db.session.commit()

    # TODO: verify instance has been paid for!

    instance.create_container()
    db.session.commit()

    url = 'localhost:' + str(instance.port)
    org = instance.name
    owner = instance.owner.full_name()

    return render_template('main/launch.html', url=url, org=org, owner=owner)


@main.route('/partners')
def partners():
    editable_html_obj = EditableHTML.get_editable_html('faq')
    return render_template('main/partners.html',
                           editable_html_obj=editable_html_obj)
