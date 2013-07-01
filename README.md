bamboo-shoot
============

Bamboo UI client

Getting Started
---------------

```bash
git clone git@github.com:modilabs/bamboo-shoot.git
cd bamboo-shoot
cp local.ini.dev.sample local.ini
# open local.ini and update database settings, session_key and auth_key

# create a python virtual env
$venv/bin/python setup.py develop
$venv/bin/initialize_shoot_db development.ini

# install submodules
git submodule init
git submodule update

# start the server
$venv/bin/pserve development.ini
```
