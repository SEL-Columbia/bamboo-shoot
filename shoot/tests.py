import unittest
import transaction

from webob.multidict import MultiDict
from pyramid import testing
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
    HTTPBadRequest,
)

from .models import (
    DBSession,
    Base,
    User,
    Dataset,
    Dashboard,
    DatasetFactory,
    DashboardFactory,
    newest,
    Chart
)


class TestViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('shoot')
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.user = User.query().first()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_dataset_list(self):
        from .views import dataset_list
        request = testing.DummyRequest()
        user = User(username="bob")
        dataset_factory = DatasetFactory(request)
        dataset_factory.__parent__ = user
        request.context = dataset_factory
        result = dataset_list(request)
        self.assertIsInstance(result['user'], User)

    def test_dataset_show(self):
        from .views import dataset_show
        request = testing.DummyRequest()
        user = User(username="bob")
        dataset = Dataset(
            dataset_id="12345678", bamboo_host="http://bamboo.io",
            title="Test Dataset")
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
        dataset_url = "http://bamboo.io/datasets/123456"
        request.POST['url'] = dataset_url
        request.POST['title'] = "Test Dataset"
        result = dataset_create(request)
        self.assertIsInstance(result, HTTPFound)
        # retrieve the dataset
        new_dataset = Dataset.query().filter_by(
            user=user, bamboo_host="http://bamboo.io", dataset_id="123456")\
            .one()
        self.assertEqual(
            result.location,
            "%(host)s/bob/datasets/%(id)s" % {
                'host': request.host_url,
                'id': new_dataset.id})
        # check dataset fields
        self.assertEqual(new_dataset.bamboo_host, "http://bamboo.io")
        self.assertEqual(new_dataset.dataset_id, "123456")
        self.assertEqual(new_dataset.title, "Test Dataset")

    def test_dataset_create_catches_duplicate_datasets(self):
        from .views import dataset_create
        request = testing.DummyRequest()
        user = User(username="bob")
        dataset = Dataset(
            user=user, bamboo_host="http://bamboo.io", dataset_id="123456",
            title="Test Dataset")
        DBSession.add(user)
        DBSession.flush()
        dataset_factory = DatasetFactory(request)
        dataset_factory.__parent__ = user
        request.context = dataset_factory
        request.POST['url'] = "http://bamboo.io/datasets/123456"
        request.POST['title'] = "A Duplicate Test Dataset"
        result = dataset_create(request)
        self.assertNotIsInstance(result, HTTPFound)

    def test_dashboard_create_without_fields(self):
        pass

    def test_dashboard_create_with_fields(self):
        from .views import dashboard_create
        request = testing.DummyRequest()
        user = User(username="bob")
        dashboard_factory = DashboardFactory(request)
        dashboard_factory.__parent__ = user
        request.context = dashboard_factory
        dataset = Dataset(user=user, title="Test Dataset",
                          bamboo_host="http://bamboo.io", dataset_id="12345")
        DBSession.add(user)
        DBSession.flush()
        params = MultiDict([('title', "Test Dashboard"),
                            ('id', dataset.id),
                            ('fields[]', 'sex'), ('fields[]', 'income')])
        request.POST = params
        result = dashboard_create(request)
        # check dashboard was created - retrieve newest
        dashboard = newest(
            Dashboard.query().filter_by(user=user), Dashboard.id)
        # check that we get a redirect
        self.assertIsInstance(result, HTTPFound)
        # check location
        self.assertEqual(result.location, "%(host)s/bob/dashboards/%(slug)s" % {
                'host': request.host_url,
                'slug': dashboard.slug})
        # check charts
        charts = Chart.query().all()
        #import ipdb; ipdb.set_trace()
        self.assertEqual(
            sorted([c.title for c in charts]), sorted(['sex', 'income']))


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

    def _create_dataset(self, **kwargs):
        dataset = Dataset(**kwargs)
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
        dataset = self._create_dataset(
            user_id=user.id, dataset_id="123456",
            bamboo_host="http://bamboo.io", title="Test Dataset")
        url = '/%(user)s/datasets/%(dataset_id)s' % (
                {'user': user.username, 'dataset_id': dataset.id})
        response = self.testapp.get(url)
        self.assertEqual(response.status_code, 200)

    def test_dataset_create(self):
        user = self._create_user("bob")
        params = {
            'url': 'http://bamboo.io/datasets/123456',
            'title': 'Test Dataset'
        }
        response = self.testapp.post(
            '/%(user)s/datasets/new' % ({'user': user.username}), params)
        self.assertEqual(response.status_code, 302)
