from flask_wtf import generate_csrf, validate_csrf

@instances.route('/get-status/<app_id>/<auth>')
def get_status(app_id, auth):
    with requests.Session() as s:
        s.trust_env = False
        new_h = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % auth,
            "Accept": "application/vnd.heroku+json; version=3"
        }
        status = s.get('https://api.heroku.com/apps/{}/builds'.format(app_id), headers=new_h)
        status = status.text
        if len(json.loads(status)) > 0:
            status = json.dumps(json.loads(status)[0])
        else:
            status = 'fail'
    return status


@instances.route('/create-instance')
@login_required
def create_instance():
    link = 'https://id.heroku.com/oauth/authorize?' +\
           'client_id={}&response_type=code&scope={}&state={}'.format(
            os.environ['HEROKU_OAUTH_ID'], 'global', generate_csrf())
    return render_template('account/create_instance.html', link=link)


@instances.route('/launch/<auth>', methods=['GET', 'POST'])
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
        app_id = json.loads(new_app)['app']['id']
        app_url = json.loads(new_app)['app']['name']
        print(app_id, app_url)

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


@instances.route('/auth/heroku/callback/')
def cb():
    with requests.Session() as s:
        s.trust_env = False
        code = request.args.get('code')
        res = s.post('https://id.heroku.com/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_secret': os.environ['HEROKU_OAUTH_SECRET']
        }).text
        res_json = json.loads(res)

        refresh_token = res_json['refresh_token']
        current_user.heroku_refresh_token = refresh_token
        db.session.add(current_user)
        db.session.commit()

    return redirect(url_for('main.launch', auth=txt))
