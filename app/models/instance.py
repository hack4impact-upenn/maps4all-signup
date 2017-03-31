from .. import db

# One to Many
# One User can have Many Instances
class Instances(db.model):
    __tablename__ = 'instances'
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.String(64))
    name = db.Column(db.String(64), unique=True) # name of the instance
    is_active = db.Column(db.Boolean, default=False)
    port = db.Column(db.Integer)
    owner_id = Column(Integer, ForeignKey('users.id'))

