bamboo-shoot
============

Bamboo UI client

Getting Started
---------------

- cd <directory containing this file>

- cp local.ini.dev.sample local.ini

- open local.ini and update database settings, session_key and auth_key

- create a python virtual env

- $venv/bin/python setup.py develop

- $venv/bin/initialize_shoot_db development.ini

- $venv/bin/pserve development.ini
