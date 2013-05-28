from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
    HTTPBadRequest,
)
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError, IntegrityError

from .models import (
    DBSession,
    User,
    Dataset,
    DatasetFactory,
)


@view_config(route_name='default', renderer='templates/default.pt')
def default(request):
    return {}


@view_config(context=User, route_name='user', name='',
             renderer='templates/user.pt')
def user_show(request):
    user = request.context
    return {'user': user}


@view_config(context=Dataset, route_name='user', name='',
             renderer='templates/dataset.pt')
def dataset_show(request):
    dataset = request.context
    return {'dataset': dataset}


@view_config(context=DatasetFactory, route_name='user', name='new',
             request_method='POST', renderer='templates/user.pt')
def dataset_create(request):
    user = request.context.__parent__
    dataset = Dataset(user=user)
    dataset.extract_values_from_url(request.POST['url'])
    # check for a duplicate
    dataset.save()
    try:
        DBSession.flush()
    except IntegrityError:
        DBSession.rollback()
        request.session.flash(
            u"The dataset already exists in your account.", "error")
    else:
        return HTTPFound(
            request.route_url('user', traverse=(
                user.username, 'datasets', dataset.dataset_id)))
    return {'user': user}
