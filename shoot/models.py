import logging
import re
from pyramid.security import (Allow, Deny, Everyone, Authenticated,
                              ALL_PERMISSIONS, DENY_ALL)

from sqlalchemy import (Column, Integer, String, ForeignKey, DateTime, func)

from sqlalchemy.orm import (relationship, backref, synonym)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import Index, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (scoped_session, sessionmaker)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

dataset_regexp = re.compile(r'(.+)/datasets/(\w+)')


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
                dataset_id=key, user=self.__parent__).one()
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
    _factories = {'datasets': DatasetFactory}

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
    # TODO: make dataset_id and user_id unique together
    __tablename__ = 'dataset'
    __table_args__ = (
        Index('uix_user_id_dataset_id', 'user_id', 'dataset_id', unique=True),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    bamboo_host = Column(String(100), nullable=False)
    dataset_id = Column(String(100), nullable=False)
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
            'user', traverse=(self.user.username, 'datasets', self.dataset_id,))
