# Maps4All Signup
[![Circle CI](https://circleci.com/gh/hack4impact/maps4all-signup.svg?style=svg)](https://circleci.com/gh/hack4impact/maps4all-signup)



## License
[MIT License](LICENSE.md)


## Team Members

- Santiago Buenahora
- Roberta Nin Feliz
- Rani Iyer
- Katie Jiang
- Hunter Lightman
- Hana Pearlman
- Ben Sandler
- Stephanie Shi
- Abhinav Suri

## Synopsis

A signup page for maps4all to allow for one-click deployment of the [maps4all](https://github.com/hack4impact/maps4all) project 

## Setting up

##### Clone the repo

```
$ git clone https://github.com/hack4impact/maps4all-signup.git
$ cd maps4all-signup
```

##### Initialize a virtualenv

```
$ pip install virtualenv
$ virtualenv -p python3 venv
$ source venv/bin/activate
```
(If you're on a mac) Make sure xcode tools are installed
```
$ xcode-select --install
```

##### Install the dependencies

```
$ pip install -r requirements.txt
```

##### Other dependencies for running locally

You need to install [Foreman](https://ddollar.github.io/foreman/) and [Redis](http://redis.io/). Chances are, these commands will work:

```
$ gem install foreman
```

For Mac (using [homebrew](http://brew.sh/)):

```
$ brew install redis
```

For Linux (Fedora)

```
$ sudo dnf install redis
```

For Linux (Debian/Ubuntu):

```
$ sudo apt-get install redis-server
```

If you don't want to install redis locally, you can use Redis container with docker

```
$ docker pull redis:latest
$ docker run -d -p 6379:6379 --name maps4all-redis redis:latest
```

##### Set your environment variables

Create a `config.env` file in your directory and include the following variables:

* `MAIL_PASSWORD` and `MAIL_USERNAME` are your login credentials for [Sendgrid](https://sendgrid.com/).
* `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` allow you to use the Twilio API to send text messages. They can be obtained through the [Twilio console](https://www.twilio.com/login).
* `ADMIN_EMAIL` and `ADMIN_PASSWORD` allow you to login as an administrator to Maps4All-Signup on your local machine.
* `HEROKU_CLIENT_ID` and `HEROKU_CLIENT_SECRET` allow you to host the new Maps4All instances on Heroku by enabling Heroku authentication. To obtain these credentials, create an account on [Heroku](https://www.heroku.com). Then, select Settings from the Manage Account option on Heroku. Add a new API Client with a name and a callback of the form `http://localhost:5000/auth/heroku/callback/` if you are deploying locally (otherwise use something like `http://your_domain.com/auth/heroku/callback`) to get the HEROKU_CLIENT_ID and HEROKU_CLIENT_SECRET.
* `CF_API_EMAI`, `CF_API_KEY`, and `CF_ZONE_IDENT` allow you to access new Maps4All instances as subdomains of maps4all.org.

Your `config.env` file should look something like this:
```
MAIL_PASSWORD=XXXXXXXXXXXXXXX
MAIL_USERNAME=XXXXXXXXXXXXXXX
TWILIO_ACCOUNT_SID=XXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=XXXXXXXXXXXXXXX
ADMIN_EMAIL=XXXXXXXXXXXXXXX
ADMIN_PASSWORD=XXXXXXXXXXXXXXX
HEROKU_CLIENT_ID=XXXXXXXXXXXXXXX
HEROKU_CLIENT_SECRET=XXXXXXXXXXXXXXX
CF_API_EMAIL=XXXXXXXXXXXXXXX
CF_API_KEY=XXXXXXXXXXXXXXX
CF_ZONE_IDENT=XXXXXXXXXXXXXXX
```

##### Create the database

```
$ python manage.py recreate_db
```

##### Other setup (e.g. creating roles in database)

```
$ python manage.py setup_dev
```

## Running the app

```
$ source venv/bin/activate
$ honcho start -f Local
```
Then navigate to `http://localhost:5000` on your preferred browser to open the web app.

## Project Structure


```
├── Procfile
├── README.md
├── app
│   ├── __init__.py
│   ├── account
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── admin
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── assets
│   │   ├── scripts
│   │   │   ├── app.js
│   │   │   └── vendor
│   │   │       ├── jquery.min.js
│   │   │       ├── semantic.min.js
│   │   │       └── tablesort.min.js
│   │   └── styles
│   │       ├── app.scss
│   │       └── vendor
│   │           └── semantic.min.css
│   ├── assets.py
│   ├── decorators.py
│   ├── email.py
│   ├── instances
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── main
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── instance.py
│   │   ├── miscellaneous.py
│   │   └── user.py
│   ├── static
│   │   ├── fonts
│   │   │   └── vendor
│   │   ├── images
│   │   └── styles
│   │       └── app.css
│   ├── templates
│   │   ├── account
│   │   │   ├── email
│   │   │   ├── join_invite.html
│   │   │   ├── login.html
│   │   │   ├── manage.html
│   │   │   ├── options.html
│   │   │   ├── register.html
│   │   │   ├── reset_password.html
│   │   │   └── unconfirmed.html
│   │   ├── admin
│   │   │   ├── index.html
│   │   │   ├── manage_user.html
│   │   │   ├── new_user.html
│   │   │   └── registered_users.html
│   │   ├── errors
│   │   ├── instances
│   │   │   ├── email
│   │   │   ├── create_instance.html
│   │   │   ├── heroku_authorize.html
│   │   │   ├── launch_form.html
│   │   │   ├── launch_status.html
│   │   │   ├── verify_needed.html
│   │   │   └── instances.html
│   │   ├── layouts
│   │   │   └── base.html
│   │   ├── macros
│   │   │   ├── form_macros.html
│   │   │   ├── check_password.html
│   │   │   ├── page_macros.html
│   │   │   └── nav_macros.html
│   │   ├── main
│   │   │   ├── index.html
│   │   │   ├── faq.html
│   │   │   ├── about.html
│   │   │   └── partners.html
│   │   └── partials
│   │       ├── _flashes.html
│   │       └── _head.html
│   └── utils.py
├── config.py
├── manage.py
├── requirements
└── tests
    ├── test_basics.py
    └── test_user_model.py
```

## License
[MIT License](LICENSE.md)