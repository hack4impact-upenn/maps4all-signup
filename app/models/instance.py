from .. import db


# One to Many
# One User can have Many Instances
class Instance(db.Model):
    __tablename__ = 'instances'
    id = db.Column(db.Integer, primary_key=True)

    # app_id uniquely identifies a deployment on heroku
    app_id = db.Column(db.String(1000), unique=False)
    name = db.Column(db.String(64), unique=True)  # name of the instance
    url_name = db.Column(db.String(64), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(64))
    default_password = db.Column(db.String(64))

    def __repr__(self):
        return '<Instance \'%s\'>' % self.name
