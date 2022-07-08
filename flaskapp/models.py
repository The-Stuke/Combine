from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    scan = db.relationship('Scans', backref='username', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Scans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    md5 = db.Column(db.String(), unique=True, nullable=False)
    url = db.Column(db.String(), nullable=False)
    domain = db.Column(db.String(), nullable=False)
    user_agent = db.Column(db.String(), nullable=False)
    scan_time = db.Column(db.String(), nullable=False)
    screenshot_path = db.Column(db.String(), nullable=False, default='default.jpg')
    dom_path = db.Column(db.String())
    user_who_scanned = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    whois_path = db.Column(db.String())
    links_path = db.Column(db.String())
    ip = db.Column(db.String())
    vt_link = db.Column(db.String())

    def _repr__(self):
        return f"Scans('{self.id}', '{self.url}')"