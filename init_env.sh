#!/bin/bash
CURRENT_DIR='pwd'
VIRTUAL_ENV_DIR=~/virtual_env
WORKSPACE=~/workspace

function log {
  echo "***** $1"
  echo ""
}

function install_package {
  log "installing package $@"
  sudo apt-get install -y $@
}

function configuration_easy_install {
  log "config easy_install...."
  curl -o setuptools-0.6c11-py2.7.egg http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg#md5=bfa92100bd772d5a213eedd356d64086
  sudo sh setuptools-0.6c11-py2.7.egg
}

function install_pip {
 sudo easy_install pip
}

function install_virtual_env {
 sudo pip install virtualenv
}

function create_data_winner_virtual_env {
 log "creating data_winner virtual environment"
 mkdir $VIRTUAL_ENV_DIR -p 
 (cd $VIRTUAL_ENV_DIR && virtualenv datawinner)
 echo "alias dw='source $VIRTUAL_ENV_DIR/datawinner/bin/activate'" >> ~/.bashrc
}

function copy_bash_profile_to_postgres_user_home {
 sudo cp "$@/.bashrc"  '/var/lib/postgresql'
}

function swich_user_to_postgres { 
 sudo su postgres -c run_as_postgres
}

function create_env {
 log "create env..."
 configuration_easy_install
 install_pip
 install_virtual_env
 create_data_winner_virtual_env
}

function create_postgres_db {
 log "create postgres db..."
 echo "PATH='$PATH:/usr/lib/postgresql/9.0/bin'" >> ~/.bashrc
 source ~/.bashrc
 #initdb ~/var/postgres9
}

function create_geodjango_db {
 log "create geodjango db"
 createdb geodjango
 psql -d geodjango -c 'create role jenkins login createdb createrole;'
 psql -d geodjango -f '/usr/share/postgresql/9.0/contrib/postgis-1.5/postgis.sql' 
 psql -d geodjango -f '/usr/share/postgresql/9.0/contrib/postgis-1.5/spatial_ref_sys.sql' 
 psql -d geodjango -c 'grant all privileges on all tables in schema public to jenkins;'      
}

function create_postgis_template_db {
 log "create postgis template db..."
 createdb -E UTF8 template_postgis
 psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
 psql -d template_postgis -f '/usr/share/postgresql/9.0/contrib/postgis-1.5/postgis.sql' # Loading the PostGIS SQL routines  
 psql -d template_postgis -f '/usr/share/postgresql/9.0/contrib/postgis-1.5/spatial_ref_sys.sql'  
 psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;" # Enabling users to alter spatial tables.  
 psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"  
 psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"     
}

function create_db {
 log "create db..."
 create_postgres_db && \
 create_geodjango_db && \
 create_postgis_template_db
}

function clone_code_base {
  mkdir $WORKSPACE
  clone_repository datawinners
  clone_repository mangrove
  clone_repository shape_files
}

function clone_repository {
 git clone https://github.com/mangroveorg/$1.git $WORKSPACE/$1
}

function update_repository {
 log "updating repository...."
 sudo apt-get install python-software-properties -y
 sudo add-apt-repository 'ppa:ubuntugis/ubuntugis-unstable'
 sudo add-apt-repository 'ppa:pitti/postgresql'
 sudo add-apt-repository 'ppa:pi-deb/gis'
 sudo add-apt-repository "deb http://ubuntu.mirror.cambrium.nl/ubuntu/ oneiric main universe"
 sudo apt-get update
}

function copy_bash_profile_to_postgres_user_home {
 sudo cp "$CURRENT_USER_HOME/.bashrc"  '/var/lib/postgresql'
}

function swich_user_to_postgres { 
 sudo su postgres run_as_postgres.sh $CURRENT_USER_HOME 
}

function change_passwd {
 log "change postgres password"
 sudo passwd postgres
}

function add_postgres_to_admin {
 sudo usermod -a -G sudo postgres
}

function add_current_user_to_postgresql {
 sudo -u postgres createuser --superuser $USER
}

function main {
  update_repository
  install_package curl vim python-dev couchdb postgresql-9.0 postgis postgresql-client-9.0 postgresql-client-common postgresql-common libgeos-3.2.2 postgresql-9.0-postgis git-core python-gdal libpq-dev gettext libxml2-dev libxslt-dev && \
  #change_passwd && \
  #add_postgres_to_admin && \
  #swich_user_to_postgres
  #copy_bash_profile_to_postgres_user_home && \
  add_current_user_to_postgresql && \
  create_env && \
  create_db && \
  clone_code_base && \
  log 'dev environment is ok!'
}

main
