from sqlalchemy import desc
from ..docker import docker
from .. import db


def filter(source):
    return ''.join(c for c in source if c.isalnum() or c == ' ')


def generate_secret():
    return 'super secret key lol lol omg so secret'


def generate_password():
    return 'password'


# One to Many
# One User can have Many Instances
class Instance(db.Model):
    __tablename__ = 'instances'
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.String(64))
    port = db.Column(db.Integer)
    status = db.Column(db.String(64))
    secret = db.Column(db.String(64), unique=False)  # SECRET_KEY

    name = db.Column(db.String(64), unique=True)  # name of the instance
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(64))
    default_password = db.Column(db.String(64))

    def __init__(self, **kwargs):
        super(Instance, self).__init__(**kwargs)

        count = Instance.query.count()
        if count > 0:
            highest_port = Instance.query.order_by(
                desc(Instance.port)).limit(1).first().port
        else:
            highest_port = 3000

        if highest_port is None:
            highest_port = 3000

        self.port = highest_port + 1

        if self.secret is None:
            # TODO: generate per instance secret key
            self.secret = generate_secret()

        if self.email is None:
            self.email = self.owner.email

        if self.default_password is None:
            self.default_password = generate_password()

    def create_container(self):
        self.status = 'Trial'
        docker.create(self)

    def stop_container(self):
        self.status = 'Inactive'
        docker.stop(self)

    def start_container(self):
        self.is_active = True
        docker.start(self)

    def sanitized_name(self):
        return filter(self.name)

    def __repr__(self):
        return '<Instance \'%s\'>' % self.name
