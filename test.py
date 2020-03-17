import unittest
from config import Config
from app import create_app, db
from app.models import User, Strain, load_user
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

    # TODO: Integration
    def test_auth_creds(self):
        u = User()
        u.username = 'Kaz'
        u.hash_password('pass')
        db.session.add(u)
        # db.session.commit()
        self.assertEqual(helper.auth_creds('Kaz', 'pass'), u)
        self.assertFalse(helper.auth_creds('Not', 'kaz'))

    # TODO: Unit
    def test_validate_next_page(self):
        valid_url = '/index'
        still_valid_url = 'google.com'
        not_valid_url = 'http://google.com'
        self.assertTrue(helper.validate_next_page(valid_url))
        self.assertTrue(helper.validate_next_page(still_valid_url))
        self.assertFalse(helper.validate_next_page(not_valid_url))
        self.assertFalse(helper.validate_next_page(None))

    # TODO: Integration
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

    # TODO: Integration
    def test_create_prev_next_urls(self):
        strains = helper.populate_test_strains(strain_dict=donezo.done)
        db.session.add_all(strains)

        user = User()
        user.username = 'Test'
        user.hash_password('pass')
        db.session.add(user)

        strains_to_try = Strain.query.limit(5).all()
        for strain in strains_to_try:
            user.try_strain(strain)

        # db.session.commit()
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

    # TODO: Integration
    def test_get_search_results(self):
        strains = helper.populate_test_strains(strain_dict=donezo.done)
        db.session.add_all(strains)

        # 4 initial results, 1 secondary
        q = '1'
        initial_query = Strain.initial_query(q)
        count = initial_query.count()
        results = helper.get_search_results(count=count, initial=initial_query, per_page=5, search_string=q)
        self.assertEqual(results, ['1024', '10th Planet', '12 Year OG', '13 Dawgs', '$100 OG'])

        # 2 initial results, 1 secondary results
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
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_load_user(self):
        user = helper.create_test_user()
        db.session.add(user)

        self.assertEqual(load_user(1), user)
        self.assertIsNone(load_user(2))

    def test_tried_relationship(self):
        strain = helper.populate_test_strain()
        user = helper.create_test_user()

        db.session.add_all([strain, user])

        self.assertEqual(user.tried.all(), [])
        self.assertEqual(user.tried.count(), 0)

        user.tried.append(strain)
        self.assertEqual(user.tried.all(), [strain])
        self.assertEqual(user.tried.count(), 1)

    def test_try_strain(self):
        strain = helper.populate_test_strain()
        user = helper.create_test_user()

        db.session.add_all([strain, user])

        self.assertEqual(user.tried.all(), [])
        self.assertEqual(user.tried.count(), 0)

        user.try_strain(strain)
        self.assertEqual(user.tried.all(), [strain])
        self.assertEqual(user.tried.count(), 1)

    def test_untry_strain(self):
        strain = helper.populate_test_strain()
        user = helper.create_test_user()

        db.session.add_all([strain, user])

        user.tried.append(strain)
        self.assertEqual(user.tried.all(), [strain])

        user.untry_strain(strain)
        self.assertEqual(user.tried.all(), [])
        self.assertEqual(user.tried.count(), 0)

    def test_has_tried(self):
        user = helper.create_test_user()
        strain = helper.populate_test_strain()
        db.session.add_all([user, strain])
        self.assertFalse(user.has_tried(strain))

        user.tried.append(strain)
        self.assertTrue(user.has_tried(strain))

    def test_has_not_tried(self):
        strains = helper.populate_test_strains(strain_dict=donezo.done)
        db.session.add_all(strains)

        user = helper.create_test_user()
        db.session.add(user)

        s = Strain.query.all()
        user.tried.extend(s[:5])
        self.assertEqual(set(user.tried.all()), set(s[:5]))
        self.assertEqual(set(user.has_not_tried()), set(s[5:]))

    def test_password_hashing(self):
        user = User()
        user.username = 'Test'
        user.hash_password('pass')

        self.assertTrue(user.verify_password('pass'))
        self.assertFalse(user.verify_password('notpass'))

    def test_repr(self):
        user = helper.create_test_user()
        self.assertEqual(str(user), '<User Test>')


class StrainModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_tried_by_relationship(self):
        user = helper.create_test_user()
        strain = helper.populate_test_strain()
        db.session.add_all([user, strain])
        self.assertEqual(strain.tried_by.all(), [])

        strain.tried_by.append(user)
        self.assertEqual(strain.tried_by.all(), [user])

    def test_initial_query(self):
        strains = helper.populate_test_strains(strain_dict=donezo.done)
        db.session.add_all(strains)

        self.assertEqual(Strain.initial_query('og').all(), [])
        self.assertEqual(Strain.initial_query('1').all(), [('1024',), ('10th Planet',), ('12 Year OG',), ('13 Dawgs',)])

    def test_follow_up_query(self):
        strains = helper.populate_test_strains(strain_dict=donezo.done)
        db.session.add_all(strains)

        self.assertEqual(Strain.follow_up_query('zoo').all(), [])
        self.assertEqual(Strain.follow_up_query('old').all(), [('24k Gold',)])
        self.assertEqual(Strain.follow_up_query('ea').all(), [('12 Year OG',), ('3 Bears OG',)])
        self.assertEqual(Strain.follow_up_query('og').all(), [('$100 OG',), ('12 Year OG',), ('3 Bears OG',)])

    def test_avatar(self):
        strain = helper.populate_test_strain()
        self.assertEqual(strain.avatar(), 'https://www.gravatar.com/avatar/098f6bcd4621d373cade4e832627b4f6?d=identicon&s=128')

    def test_search(self):
        strains = helper.populate_test_strains(strain_dict=donezo.done)
        db.session.add_all(strains)

        gold = Strain.query.filter_by(name='24k Gold').first()
        year = Strain.query.filter_by(name='12 Year OG').first()
        hundred = Strain.query.filter_by(name='$100 OG').first()
        bears = Strain.query.filter_by(name='3 Bears OG').first()

        self.assertEqual(Strain.search('zoo').all(), [])
        self.assertEqual(Strain.search('old').all(), [gold])
        self.assertEqual(Strain.search('ea').all(), [year, bears])
        self.assertEqual(Strain.search('og').all(), [hundred, year, bears])

    def test_name_to_index(self):
        strains = helper.populate_test_strains(strain_dict=donezo.done)
        db.session.add_all(strains)

        self.assertEqual(Strain.name_to_index('3 Bears OG').first(), ('3-bears-og',))
        self.assertEqual(Strain.name_to_index('12 Year OG').first(), ('12-year-og',))
        self.assertEqual(Strain.name_to_index('24k Gold').first(), ('24k-gold',))
        self.assertIsNone(Strain.name_to_index('zoo').first())

    def test_repr(self):
        strain = helper.populate_test_strain()
        self.assertEqual(str(strain), '<Strain Test>')


if __name__ == '__main__':
    unittest.main()
