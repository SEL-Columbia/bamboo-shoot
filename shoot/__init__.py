from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    UserFactory,
    DatasetFactory,
)

from .models import group_finder


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['session_key'])
    config = Configurator(
        settings=settings, root_factory='shoot.models.RootFactory',
        session_factory=session_factory)
    # auth
    authentication_policy = AuthTktAuthenticationPolicy(
        settings['auth_key'], callback=group_finder, hashalg='sha512')
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    includeme(config)
    return config.make_wsgi_app()


def includeme(config):
    config.add_static_view('static', 'shoot:static', cache_max_age=3600)
    config.add_route('default', '/')
    # traversed routes
    config.add_route(
        'user', '/*traverse', factory=UserFactory)
    config.scan()
