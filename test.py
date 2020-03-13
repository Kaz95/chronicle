import unittest
from config import Config
from app import create_app, db
from app.models import User, Strain
from app.auth import routes


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class AuthCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_auth_creds(self):
        u = User()
        u.username = 'Kaz'
        u.hash_password('pass')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(routes.auth_creds('Kaz', 'pass'), u)
        self.assertFalse(routes.auth_creds('Not', 'kaz'))

    def test_validate_next_page(self):
        valid_url = '/index'
        still_valid_url = 'google.com'
        not_valid_url = 'http://google.com'
        self.assertTrue(routes.validate_next_page(valid_url))
        self.assertTrue(routes.validate_next_page(still_valid_url))
        self.assertFalse(routes.validate_next_page(not_valid_url))
        self.assertFalse(routes.validate_next_page(None))

    def test_create_user(self):
        u = routes.create_user('Kaz', 'pass')
        db.session.add(u)
        db.session.commit()
        attempted_user_query = User.query.filter_by(username='Kaz').first()
        self.assertEqual(attempted_user_query, u)
        self.assertTrue(u.verify_password('pass'))
        self.assertFalse(u.verify_password('notmypass'))

