import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Base,
    User,
    Dataset,
    Dashboard,
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        user = User(username="larryweya")
        dataset = Dataset(
            user=user, bamboo_host="http://bamboo.io",
            dataset_id="d59dee1092e74e2da947ac75c7b5fcfa")
        dataset = Dataset(
            user=user, bamboo_host="http://bamboo.io",
            dataset_id="bb9bdf69384b4400a08fcf7ecc4b0a01")
        dataset2 = Dataset(
            user=user, bamboo_host="http://192.168.56.2:8000",
            dataset_id="361bbd13d61c47718dd8e1ec36197acc")
        dashboard = Dashboard(user=user, title="Students Survey",
                              slug="students-survey")
        DBSession.add(user)
