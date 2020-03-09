from app import db, login
from passlib.hash import pbkdf2_sha256 as pwd_context
from flask_login import UserMixin
from hashlib import md5


# TODO: Test
@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


tried = db.Table('tried',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('strain_id', db.Integer, db.ForeignKey('strain.id')))


# TODO: Test
# TODO: Clean up these var names eventually. They are ravioli.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    tried = db.relationship('Strain', secondary=tried, backref=db.backref('tried_by', lazy='dynamic'), lazy='dynamic')

    def has_tried(self, strain):
        return self.tried.filter(tried.c.strain_id == strain.id).count() > 0

    def has_not_tried(self):
        return Strain.query.filter(~self.tried.exists())

    def try_strain(self, strain):
        if not self.has_tried(strain):
            self.tried.append(strain)

    def untry_strain(self, strain):
        if self.has_tried(strain):
            self.tried.remove(strain)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return f'<User {self.username}>'


# TODO: Test
class Strain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.String(25), index=True, unique=True)
    name = db.Column(db.String(50))
    leafly = db.Column(db.String(50), unique=True)
    species = db.Column(db.String(8))
    description = db.Column(db.String(1000))

    @classmethod
    def paginate_all(cls, page, app):
        return cls.query.paginate(page, app.config['STRAINS_PER_PAGE'], False)

    def avatar(self, size=128):
        digest = md5(self.name.lower().encode()).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return f'<Strain {self.name}>'
