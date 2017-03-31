from .. import db
from sqlalchemy import desc
from ...docker import docker


# One to Many
# One User can have Many Instances
class Instance(db.model):
    __tablename__ = 'instances'
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.String(64))
    port = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=False)
    secret = db.Column(db.String(64), unique=False)  # SECRET_KEY

    name = db.Column(db.String(64), unique=True)  # name of the instance
    name = db.Column(db.String(64), unique=True)  # name of the instance
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, **kwargs):
        highest_inst = Instance.query.order_by(desc(Instance.port)).limit(1)
        if highest_inst is None:
            highest_port = 3000
        else:
            highest_port = highest_inst.port

        self.port = highest_port + 1

        if self.secret is None:
            self.secret = 'super secret key lol lol omg so secret'

    def start_container(self):
        self.is_active = True
        docker.start(self)

    def stop_container(self):
        self.is_active = False
        docker.stop(self)

    def __repr__(self):
        return '<Instance \'%s\'>' % self.name
