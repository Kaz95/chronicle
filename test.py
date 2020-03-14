import unittest
from config import Config
from app import create_app, db
from app.models import User, Strain
from app.auth import routes
from app import helper
from app import donezo


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SERVER_NAME = ''


class AuthHelperCase(unittest.TestCase):
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
        # db.session.commit()
        self.assertEqual(helper.auth_creds('Kaz', 'pass'), u)
        self.assertFalse(helper.auth_creds('Not', 'kaz'))

    def test_validate_next_page(self):
        valid_url = '/index'
        still_valid_url = 'google.com'
        not_valid_url = 'http://google.com'
        self.assertTrue(helper.validate_next_page(valid_url))
        self.assertTrue(helper.validate_next_page(still_valid_url))
        self.assertFalse(helper.validate_next_page(not_valid_url))
        self.assertFalse(helper.validate_next_page(None))

    def test_create_user(self):
        u = helper.create_user('Kaz', 'pass')
        db.session.add(u)
        # db.session.commit()
        attempted_user_query = User.query.filter_by(username='Kaz').first()
        self.assertEqual(attempted_user_query, u)
        self.assertTrue(u.verify_password('pass'))
        self.assertFalse(u.verify_password('notmypass'))


class MainHelperCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_prev_next_urls(self):
        helper.populate_test_strains(strain_dict=donezo.done, db=db)
        user = User()
        user.username = 'Test'
        user.hash_password('pass')
        db.session.add(user)

        strains_to_try = Strain.query.limit(5).all()
        for strain in strains_to_try:
            user.try_strain(strain)

        all_strains = Strain.query.paginate(1, 1, False)
        tried_strains = user.tried.paginate(1, 1, False)
        searched_strains = Strain.search('10').paginate(1, 1, False)

        # All Strains test
        prev_url, next_url = helper.create_prev_next_urls(all_strains)
        self.assertIsNone(prev_url)
        self.assertEqual(next_url, '/strains?page=2')

        all_strains = all_strains.next()
        prev_url, next_url = helper.create_prev_next_urls(all_strains)
        self.assertEqual(prev_url, '/strains?page=1')
        self.assertEqual(next_url, '/strains?page=3')

        while all_strains.has_next:
            all_strains = all_strains.next()

        prev_url, next_url = helper.create_prev_next_urls(all_strains)
        self.assertIsNone(next_url)
        self.assertEqual(prev_url, '/strains?page=9')

        # Tried Strains Test
        prev_url, next_url = helper.create_prev_next_urls(tried_strains, filt='tried')
        self.assertIsNone(prev_url)
        self.assertEqual(next_url, '/strains?filter=tried&page=2')

        tried_strains = tried_strains.next()
        prev_url, next_url = helper.create_prev_next_urls(tried_strains, filt='tried')
        self.assertEqual(prev_url, '/strains?filter=tried&page=1')
        self.assertEqual(next_url, '/strains?filter=tried&page=3')

        while tried_strains.has_next:
            tried_strains = tried_strains.next()

        prev_url, next_url = helper.create_prev_next_urls(tried_strains, filt='tried')
        self.assertIsNone(next_url)
        self.assertEqual(prev_url, '/strains?filter=tried&page=4')

        # Searched Strains Test
        prev_url, next_url = helper.create_prev_next_urls(searched_strains, filt='search', q='10')
        self.assertIsNone(prev_url)
        self.assertEqual(next_url, '/strains?filter=search&q=10&page=2')

        searched_strains = searched_strains.next()
        prev_url, next_url = helper.create_prev_next_urls(searched_strains, filt='search', q=10)
        self.assertEqual(prev_url, '/strains?filter=search&q=10&page=1')
        self.assertEqual(next_url, '/strains?filter=search&q=10&page=3')

        searched_strains = searched_strains.next()
        prev_url, next_url = helper.create_prev_next_urls(searched_strains, filt='search', q=10)
        self.assertEqual(prev_url, '/strains?filter=search&q=10&page=2')
        self.assertIsNone(next_url)

    def test_get_search_results(self):
        helper.populate_test_strains(strain_dict=donezo.done, db=db)

        # 5 initial results, 0 secondary
        q = '1'
        initial_query = Strain.initial_query(q)
        count = initial_query.count()
        results = helper.get_search_results(count=count, initial=initial_query, per_page=5, search_string=q)
        self.assertEqual(results, ['1024', '10th Planet', '12 Year OG', '13 Dawgs', '$100 OG'])

        # 3 initial results, 0 secondary results
        q = '10'
        initial_query = Strain.initial_query(q)
        count = initial_query.count()
        results = helper.get_search_results(count=count, initial=initial_query, per_page=5, search_string=q)
        self.assertEqual(results, ['1024', '10th Planet', '$100 OG'])

        # 3 initial results, 2 secondary results
        q = '2'
        initial_query = Strain.initial_query(q)
        count = initial_query.count()
        results = helper.get_search_results(count=count, initial=initial_query, per_page=5, search_string=q)
        self.assertEqual(results, ['2 Fast 2 Vast', '22', '24k Gold', '1024', '12 Year OG'])

        # 0 initial results, 3 secondary results
        q = 'og'
        initial_query = Strain.initial_query(q)
        count = initial_query.count()
        results = helper.get_search_results(count=count, initial=initial_query, per_page=5, search_string=q)
        self.assertEqual(results, ['$100 OG', '12 Year OG', '3 Bears OG'])

        # 0 initial results, 5 secondary results
        q = 'g'
        initial_query = Strain.initial_query(q)
        count = initial_query.count()
        results = helper.get_search_results(count=count, initial=initial_query, per_page=5, search_string=q)
        self.assertEqual(results, ['$100 OG', '12 Year OG', '13 Dawgs', '24k Gold', '3 Bears OG'])


class UserModelCase(unittest.TestCase):
    pass


class StrainModelCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
