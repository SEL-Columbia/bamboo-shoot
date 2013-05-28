import unittest
import transaction

from pyramid import testing
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
    HTTPBadRequest,
)

from .models import (DBSession, Base, User, Dataset, DatasetFactory)


class TestViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('stem')
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.user = User.query().first()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_user_view(self):
        from .views import user_show
        request = testing.DummyRequest()
        request.context = User(username="bob")
        result = user_show(request)
        self.assertIsInstance(result['user'], User)

    def test_dataset_view(self):
        from .views import dataset_show
        request = testing.DummyRequest()
        user = User(username="bob")
        dataset = Dataset(
            dataset_id="12345678", bamboo_host="http://bamboo.io")
        dataset.__parent__ = user
        request.context = dataset
        result = dataset_show(request)
        self.assertIsInstance(result['dataset'], Dataset)

    def test_dataset_create(self):
        from .views import dataset_create
        request = testing.DummyRequest()
        user = User(username="bob")
        dataset_factory = DatasetFactory(request)
        dataset_factory.__parent__ = user
        request.context = dataset_factory
        request.POST['url'] = "http://bamboo.io/datasets/123456"
        result = dataset_create(request)
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(
            result.location, "%(host)s/bob/datasets/123456" %
                             {'host': request.host_url})

    def test_dataset_create_catches_duplicate_datasets(self):
        from .views import dataset_create
        request = testing.DummyRequest()
        user = User(username="bob")
        dataset = Dataset(
            user=user, bamboo_host="http://bamboo.io", dataset_id="123456")
        DBSession.add(user)
        DBSession.flush()
        dataset_factory = DatasetFactory(request)
        dataset_factory.__parent__ = user
        request.context = dataset_factory
        request.POST['url'] = "http://bamboo.io/datasets/123456"
        result = dataset_create(request)
        self.assertNotIsInstance(result, HTTPFound)


class ModelTests(unittest.TestCase):
    def test_dataset_extract_values_from_url(self):
        source_url = "http://bamboo.io/datasets/12345678"
        user = User(username="bob")
        dataset = Dataset(user=user)
        dataset.extract_values_from_url(source_url)
        expected_url = "http://bamboo.io"
        expected_dataset_id = "12345678"
        self.assertEqual(dataset.bamboo_host, expected_url)
        self.assertEqual(dataset.dataset_id, expected_dataset_id)


class TestViewIntegration(unittest.TestCase):
    def setUp(self):
        from webtest import TestApp
        self.testapp = TestApp("config:test.ini", relative_to="./")
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def _create_user(self, username):
        user = User(username=username)
        with transaction.manager:
            DBSession.add(user)
        return User.query().first()

    def _create_dataset(self, user_id, dataset_id, url):
        dataset = Dataset(
            user_id=user_id, dataset_id=dataset_id, bamboo_host=url)
        with transaction.manager:
            DBSession.add(dataset)
        return Dataset.query().first()

    def tearDown(self):
        DBSession.remove()

    def test_user_show(self):
        self._create_user("bob")
        response = self.testapp.get('/bob')
        self.assertEqual(response.status_code, 200)

    def test_dataset_show(self):
        user = self._create_user("bob")
        dataset = self._create_dataset(user.id, "123456", "http://bamboo.io")
        response = self.testapp.get(
            '/%(user)s/datasets/%(dataset_id)s' % (
                {'user': user.username, 'dataset_id': dataset.dataset_id}))
        self.assertEqual(response.status_code, 200)

    def test_dataset_create(self):
        user = self._create_user("bob")
        params = {'url': 'http://bamboo.io/datasets/123456'}
        response = self.testapp.post(
            '/%(user)s/datasets/new' % ({'user': user.username}), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location, "http://localhost/bob/datasets/123456")
