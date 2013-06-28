import logging
import re
from slugify import slugify
from pyramid.security import (Allow, Deny, Everyone, Authenticated,
                              ALL_PERMISSIONS, DENY_ALL)

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
    event,
    desc
)
from sqlalchemy.orm import (relationship, backref, synonym)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

dataset_regexp = re.compile(r'(.+)/datasets/(\w+)')


def generate_slug(column, value, unique_query):
    i = 0
    base_slug = slugify(value)
    slug = base_slug
    while unique_query.filter(column == slug).count() > 0:
        i += 1
        slug = "{0}-{1}".format(base_slug, i)
    return slug


def set_slug(mapper, connection, target):
    target_column = mapper.class_.slug_target_column()
    source_column = mapper.class_.slug_source_column()
    slug = generate_slug(
        target_column, target.__getattribute__(
            source_column.name), target.slug_unique_query())
    target.__setattr__(target_column.name, slug)


class Slugable(object):
    def slug_unique_query(self):
        raise NotImplementedError

    @classmethod
    def slug_target_column(cls):
        return cls.slug

    @classmethod
    def slug_source_column(cls):
        return cls.name


def newest(query, sort_by):
    return query.order_by(desc(sort_by)).first()


class Model(object):
    def save(self):
        DBSession.add(self)

    @classmethod
    def query(cls, **kwargs):
        return DBSession.query(cls, **kwargs)

    def delete(self):
        DBSession.delete(self)


Base = declarative_base(cls=Model)


class UserFactory(object):
    # allows any resource created by StoreFactory to be accessible by g:su
    __acl__ = [
        (Allow, "g:su", ALL_PERMISSIONS),
    ]
    __name__ = None
    __parent__ = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        logger = logging.getLogger(__name__)
        try:
            user = User.query().filter_by(username=key).one()
        except NoResultFound as e:
            logger.debug(
                "Couldn't find a user with username {0}, {1}".format(
                    key, self.request.url))
            raise KeyError
        else:
            logger.debug(
                "Found a user with username %s" % key)
            user.__parent__ = self
            user.__name__ = key
            user.request = self.request
            return user


class DatasetFactory(object):
    __name__ = None
    __parent__ = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        logger = logging.getLogger(__name__)
        try:
            dataset = Dataset.query().filter_by(
                id=key).one()
        except NoResultFound:
            logger.debug(
                "Couldn't find a dataset with id {0}, {1}".format(
                    key, self.request.url))
            raise KeyError
        else:
            logger.debug(
                "Found a dataset with id %s" % key)
            dataset.__parent__ = self
            dataset.__name__ = key
            return dataset


# TODO: create a generic model factory for all model lookups
class DashboardFactory(object):
    __name__ = None
    __parent__ = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        logger = logging.getLogger(__name__)
        try:
            dashboard = Dashboard.query().filter_by(
                slug=key, user=self.__parent__).one()
        except NoResultFound:
            logger.debug(
                "Couldn't find a dashboard with slug {0}, {1}".format(
                    key, self.request.url))
            raise KeyError
        else:
            logger.debug(
                "Found a dashboard with slug %s" % key)
            dashboard.__parent__ = self
            dashboard.__name__ = key
            return dashboard


class RootFactory(object):
    __acl__ = [
        (Allow, "g:su", ALL_PERMISSIONS),
        (Allow, Authenticated, 'authenticated'),
    ]

    def __init__(self, request):
        self.request = request


def group_finder(user_id, request):
    return ['g:su']


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    _factories = {'datasets': DatasetFactory, 'dashboards': DashboardFactory}

    def __getitem__(self, key):
        logger = logging.getLogger(__name__)
        try:
            factory = self._factories[key](self.request)
        except AttributeError:
            logger.debug(
                "Couldn't find a factory for {0}, {1}".format(
                    key, self.request.url))
            raise KeyError
        else:
            logger.debug(
                "Found a factory for %s" % key)
            factory.__parent__ = self
            factory.__name__ = key
            return factory

    def url(self, request):
        return request.route_url(
            'user', traverse=(self.username,))


class Dataset(Base):
    # TODO: make dataset_id, bamboo_host and user_id unique together
    __tablename__ = 'dataset'
    __table_args__ = (
        Index('uix_user_id_host_dataset_id', 'user_id', 'bamboo_host',
              'dataset_id', unique=True),)
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    bamboo_host = Column(String(100), nullable=False)
    dataset_id = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref=backref('datasets'))
    added_on = Column(DateTime(
        timezone=True), nullable=False, default=func.now())

    def extract_values_from_url(self, bamboo_host):
        groups = re.match(dataset_regexp, bamboo_host).groups()
        self.bamboo_host = groups[0]
        self.dataset_id = groups[1]

    @property
    def bamboo_url(self):
        return "%(url)s/datasets/%(dataset_id)s" % (
            {'url':self.bamboo_host, 'dataset_id': self.dataset_id})

    def url(self, request):
        return request.route_url(
            'user', traverse=(self.user.username, 'datasets', self.id,))


class Dashboard(Base, Slugable):
    __tablename__ = 'dashboard'
    __table_args__ = (
        Index('uix_user_id_slug', 'user_id', 'slug', unique=True),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    user = relationship('User', backref=backref('dashboards'))
    added_on = Column(DateTime(
        timezone=True), nullable=False, default=func.now())

    def slug_unique_query(self):
        return Dataset.query()

    @classmethod
    def slug_source_column(cls):
        return cls.title

    def charts_url(self, request):
        return request.route_url(
            'user', traverse=(self.user.username, 'dashboards', self.slug,
                              'charts',))

    def url(self, request):
        return request.route_url(
            'user', traverse=(self.user.username, 'dashboards', self.slug))

    def __json__(self, request):
        return {
            'title': self.title,
            'date_created': self.added_on.isoformat(),
            'charts_url': self.charts_url(request)
        }

event.listen(Dashboard, 'before_insert', set_slug)


class Chart(Base):
    __tablename__ = 'chart'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    x_field_id = Column(String(100), nullable=True)
    y_field_id = Column(String(100), nullable=True)
    dashboard_id = Column(Integer, ForeignKey('dashboard.id'), nullable=False)
    dashboard = relationship('Dashboard', backref=backref('charts'))
    dataset_id = Column(Integer, ForeignKey('dataset.id'), nullable=False)
    dataset = relationship('Dataset', backref=backref('charts'))
    added_on = Column(DateTime(
        timezone=True), nullable=False, default=func.now())

    def __json__(self, request):
        return {
            'title': self.title,
            'bamboo_host': self.dataset.bamboo_host,
            'dataset_id': self.dataset.dataset_id,
            'x_field_id': self.x_field_id,
            'y_field_id': self.y_field_id
        }