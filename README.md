# Memo System

1. Architecture
2. Close the memosystem
3. Configuration
4. Initialization
5. Using Docker

# Architecture
![Architecture](https://github.com/iotexpert/memosystem/blob/main/arch.png?raw=true)
# Configuration
In order to use the system you will need to take the following steps:
1. Copy the configuration file templates to make the docker and settings configuration
2. Choose the location of memo files and database files and create the directory structure
3. Select and Configure the Database (SQLite or MySQL)
4. Select AD/LDAP or Local Authentication - and configure
5. Configure the mailer
6. Configure HTTPS or HTTP (intelligence test)
## Copy the configuration templates
All of the system configuration is done by copying the appropriate template and then making modifcations that are specific to your configuration
|File|Template|Description|
|---|---|---|
|docker-compose.yml|docker-compose.yml.template||
|memos/Dockerfile|memos/Dockerfile.template||
|memos/settings.py|memos/settings.py.template||

On my unix box I run the following commands to copy the templates
``` bash
cp docker-compose.yml.template docker-compose.yml
cp memos/Dockerfile.template memos/Dockerfile
cp memos/settings_local.py.template memos/settings.py
```
This will give you a local copy of the configuration files which Docker, MySQL, SQLite, Flask etc will use.
## Local Files
When the system is running it will need to store the memos and memo meta data into the file system.  The docker compose will need to "mount" the local file system into the docker containers.  In my installation I created a directory at the top level called "memo_files".  In this directory I make three subdirectories, one for the files (static) one for the mysql and one for the sqlite.
```
mkdir memo_files
mkdir memo_files/static
mkdir memo_files/mysql
mkdir memo_files/sqlite
```
## Configure the Database
The system is built using [SQL Alchemy](https://www.sqlalchemy.org) to support all database interaction.  This library gives you a selection of database.  I have tested [SQLite](https://www.sqlite.org/) and [MySQL](https://mysql.com) but the others will probably work as well - YMMV.  For a production use I recommend MySQL.
### MySQL
In order to configure the MySQL instance you will need to modify the "docker-compose.yml" to setup the users, passwords and files.  Then you will need to modify the settings.py to setup the same.
#### Configure docker-compose.yml for MySQL
The database section of the provided tempalte for docker-compose.yml looks like this:
```yml
  mysql:  # This container host the mysql instance.
    image: mysql
    container_name: mysql
    command: --default-authentication-plugin=mysql_native_password
    restart: always
    environment:
    # You should change these passwords... and then
    # type in the passwords into the file memos/memos/settings.py
      MYSQL_ROOT_PASSWORD: "test123"
      MYSQL_DATABASE: "memos"
      MYSQL_USER: "memosystem"
      MYSQL_PASSWORD: "memopw"
#    ports:
#      - 3306:3306
    volumes:
    # you need to fix the hardcoded source path
      - /Users/arh/proj/memosystem/memo_files/mysql:/var/lib/mysql
```
In your docker-compose.yml configuration file you need to setup:
1. MYSQL_ROOT_PASSWORD: "test123"
2. MYSQL_DATABASE: "memos"
3. MYSQL_USER: "memosystem"
4. MYSQL_PASSWORD: "memopw"

I reccomend that you choose a good password, though it may not "really" matter given the MySQL is hidden in a docker container.  Then you need to specify the path to your mysql files.
```
- /Users/arh/proj/memosystem/memo_files/mysql:/var/lib/mysql
```
Unfortunately you CANNOT use a relative path for some stupid Docker reason

#### Configure the MySQL Database in settings.py
In the settings.py file you need to configure the SQLAlchemy to talk to MySQL.  
```
#os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@mysql/memos'
```
To do this you
1. remove the comment # (and make sure that the sqllite line is commented)
2. Change the URL for the user (user), password (password), server aka the docker container name (mysql) and database (memos)
Here is an example with user=memosystem password=memopw server=mysql database=memos  
```
os.environ['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://memosystem:memopw@mysql/memos'
```
### SQLite
If you want to use sqlite you modify the settings_local.py and the docker-compose.yml.  Start with the settings_local.py.  You want to turn on the sqlite url.  It is just a PATH to the site.db (the database file).  The name of the database file doesnt really matter - though I have been calling it site.db.  The "///sqlite/" part tells the sqlite to store the file in /app/memos/sqlite. 
```
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite/site.db'
```
In order to not loose your data you should mount a directory from the host onto /apps/memos/sqlite.  To do this modify docker-compose.yml.  In the "memosystem" section add the line with the bind mount (the last line of this block).  This will mount the directory from your memosystem/memo_files/sqlite so that the database file is preserverd.
```
  memosystem:     # This container hosts the uwsgi & flask
    build: ./memos
    container_name: memosystem
    restart: always
    ports:
      # if you are going to run flask without the uwsgi etc... then you need this port
#      - 5000:5000
      - 80:80
      - 443:443
    volumes:
    # Unfortunately the volume must be an absolute path to the
    # memos.  This directory will hold the raw files + the meta jsons
    # of the memos... and should be backed up
      - /Users/arh/proj/memosystem/memo_files/static:/app/memos/static
      - /Users/arh/proj/memosystem/memo_files/sqlite:/app/memos/sqlite
```
## Authentication
## Mailer
## HTTPS / HTTP
# Initialization
In order to intialize the system there is a python program called "configure.py" that can perform two functions
1. Initialize the tables in the database based on the database configuration
2. Copy the static files from the "memos/memos/template_static_files" into the "memos/memos/static" directory

# Using Docker

cd memos
docker build -t memosystem .
docker run -d -p 5000:5000 -v /Users/arh/proj/memosystem/memo_files:/app/memos/static --name memosystem memosystem
docker exec memosystem python configure.py

metal flask + sqlite
metal flask + metal mysql
metal flask + docker mysql
docker flask + sqlite
docker flask + nginx + sqlite
docker flask + nginx + mysql
