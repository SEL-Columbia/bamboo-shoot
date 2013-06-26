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
    Dashboard,
    DashboardFactory,
)


@view_config(route_name='default', renderer='templates/default.pt')
def default(request):
    return HTTPFound(
        request.route_url('user', traverse=(
            'modilabs', 'datasets')))


@view_config(context=User, route_name='user', name='',
             renderer='templates/user.pt')
def user_show(request):
    user = request.context
    return {'user': user}


@view_config(context=DatasetFactory, route_name='user', name='',
             renderer='templates/datasets.pt')
def dataset_list(request):
    user = request.context.__parent__
    datasets = Dataset.query().filter_by(user=user)
    return {'user': user, 'datasets': datasets}


@view_config(context=Dataset, route_name='user', name='',
             renderer='templates/dataset.pt')
def dataset_show(request):
    dataset = request.context
    return {'dataset': dataset}


@view_config(context=DatasetFactory, route_name='user', name='new',
             request_method='POST', renderer='templates/datasets.pt')
def dataset_create(request):
    user = request.context.__parent__
    dataset = Dataset(user=user)
    dataset.extract_values_from_url(request.POST['url'])
    dataset.title = request.POST['title']
    # check for a duplicate
    dataset.save()
    try:
        DBSession.flush()
    except IntegrityError:
        DBSession.rollback()
        request.session.flash(
            u"The dataset already exists in your account.", "error")
    else:
        return HTTPFound(dataset.url(request))
    return {'user': user}


@view_config(context=DashboardFactory, route_name='user', name='',
             renderer='templates/dashboards.pt')
def dashboard_list(request):
    user = request.context.__parent__
    dashboards = Dashboard.query().filter_by(user=user)
    return {'user': user, 'dashboards': dashboards}


@view_config(context=Dashboard, route_name='user', name='',
             renderer='templates/dashboard.pt')
def dashboard_show(request):
    dashboard = request.context
    return {'dashboard': dashboard}


@view_config(context=DashboardFactory, route_name='user', name='new',
             request_method='POST')
def dashboard_create(request):
    user = request.context.__parent__
    dashboard = Dashboard(user=user)
    dashboard.title = request.POST['title']
    dashboard.save()
    DBSession.flush()
    return HTTPFound(
        request.route_url('user', traverse=(
            user.username, 'dashboards', dashboard.slug)))
            #user.username, 'dashboards', dahsboard.slug))) TODO: use this misspelling in tests


@view_config(context=Dashboard, route_name='user', name='charts',
             renderer='json')
def charts_show(request):
    dashboard = request.context
    return {'charts': dashboard.charts}
