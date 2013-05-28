import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'PasteScript',
    'pyramid',
    'pybamboo',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'uwsgi',
    'MySQL-python',
    'webtest',
    'fabric',
    'uwsgi',
]

setup(name='shoot',
      version='0.1',
      description='shoot',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='bamboo UI web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='shoot',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = shoot:main
      [console_scripts]
      initialize_shoot_db = shoot.scripts.initializedb:main
      """,
      )
