from sqlalchemy import desc
from ..docker import docker
from .. import db


# TODO: what is this for??
def filter(source):
    return ''.join(c for c in source if c.isalnum() or c == ' ')


# One to Many
# One User can have Many Instances
class Instance(db.Model):
    __tablename__ = 'instances'
    id = db.Column(db.Integer, primary_key=True)

    # app_id uniquely identifies a deployment on heroku
    app_id = db.Column(db.String(1000), unique=False)
    name = db.Column(db.String(64), unique=True)  # name of the instance
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # TODO: if this will always be current_user.email, it should be removed and
    # we should just refer to that.
    email = db.Column(db.String(64))
    default_password = db.Column(db.String(64))

    # TODO: Can we eliminate all of these below fields?
    subscription = db.Column(db.String(128))
    port = db.Column(db.Integer)
    is_running = db.Column(db.Boolean)
    secret = db.Column(db.String(64), unique=False)  # SECRET_KEY

    def __init__(self, **kwargs):
        super(Instance, self).__init__(**kwargs)

        # TODO: delete all this port business logic
        count = Instance.query.count()
        if count > 0:
            highest_port = Instance.query.order_by(
                desc(Instance.port)).limit(1).first().port
        else:
            highest_port = 3000

        if highest_port is None:
            highest_port = 3000

        self.port = highest_port + 1

        if self.email is None:
            self.email = self.owner.email

    def set_subscription(self, id):
        self.subscription = id
        db.session.add(self)
        db.session.commit()

    def create_container(self):
        self.is_running = True
        db.session.add(self)
        db.session.commit()
        print("CREATED: {}".format(self.is_running))
        docker.create(self)
        return True

    def stop_container(self):
        self.is_running = False
        docker.stop(self)
        db.session.add(self)
        db.session.commit()
        print("STOP: {}".format(self.is_running))
        return True

    def start_container(self):
        self.is_running = True
        docker.start(self)
        db.session.add(self)
        db.session.commit()
        print("START: {}".format(self.is_running))
        return True

    def sanitized_name(self):
        return filter(self.name)

    def __repr__(self):
        return '<Instance \'%s\'>' % self.name
