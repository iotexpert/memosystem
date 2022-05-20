# Memo System
The Memo System is a light weight web based document managment system for maintaining and distributing internal memos.  This readme provides an overview of the system as well as instructions for installation and configuration.  This document has the following sections:
1. Architecture
2. Install with git clone
3. Configuration
4. Initialization
5. Filesystem
6. Useful Docker Commands

# Architecture
The system is built using a classic three-tier-client-architecture.  The system is written in Python and uses the SQLAlchemy library to provide an abstration layer to the database which allows the use of MySQL/SQLite or SQL Server.  The system uses the database to store meta data of the memos.  The raw datafiles are stored in the underlying operating system's filesystem.  The system is built to enable simple use of Docker to containerize the database and the Python flask webserver.  The picture below is an overview of the top level architecture.


![Architecture](https://github.com/iotexpert/memosystem/blob/main/doc/3tier.png?raw=true)

The picture below shows an example implementation where the memosystem and the database are implemented using Docker.

![Architecture](https://github.com/iotexpert/memosystem/blob/main/doc/arch.png?raw=true)
# Clone the Memosystem
The first step in building the system is to pick out a location where you want the system to reside and then clone this repsitory e.g.
```
cd /some/place/to/store
git clone git@github.com:iotexpert/memosystem.git
```
# Configuration
In order to configure the system you will need to take the following steps:
1. Copy the configuration file templates to create your specific Docker and system configuration
2. Choose the location of memo files and database files and create the directory structure
3. Select and configure the database (SQLite or MySQL or SQL Server)
4. Select AD/LDAP or Local Authentication - and configure
5. Configure the mailer
6. Configure HTTPS or HTTP (intelligence test)
## Copy the configuration templates
All of the system configuration is done by copying the appropriate template and then making modifcations that are specific to your configuration
|File|Template|Description|
|---|---|---|
|docker-compose.yml|docker-compose.yml.template|Overall Docker configuration specifies ports etc.|
|memos/Dockerfile|memos/Dockerfile.template|The Docker configuration for the memosystem including Flask and NGINX|
|memos/settings.py|memos/settings.py.template|The configuration file for the Flask application|

On my unix box I run the following commands to copy the templates
``` bash
cp docker-compose.yml.template docker-compose.yml
cp memos/Dockerfile.template memos/Dockerfile
cp memos/settings_local.py.template memos/settings.py
```
This will give you a local copy of the configuration files which Docker, MySQL, SQLite, Flask etc will use.
## Local Files
When the system is running it will need to store the memos and memo meta data onto a permanant file system on the host.  The docker compose will need to "mount" the local file system into the docker containers.  In my installation I created a directory at the top level called "memo_files".  In this directory I make three subdirectories, one for the files (static) one for the mysql and one for the sqlite.
```
mkdir memo_files
mkdir memo_files/static
mkdir memo_files/mysql
mkdir memo_files/sqlite
```
## Configure the Database
The system is built using [SQL Alchemy](https://www.sqlalchemy.org) to support all database interaction.  This library gives you a selection of targetable databases.  I have tested [SQLite](https://www.sqlite.org/) and [MySQL](https://mysql.com) but the others will probably work as well - YMMV.  For a production use I recommend MySQL.
### MySQL
You may choose to target a MySQL server that you already have in your enterprise.  To do this you can skip the docker configuration.  If you want a Docker container running a private MySQL you will need to modify the "docker-compose.yml" (which you copied from the template) to setup the users, passwords and files.  Then you will need to modify the settings.py to setup to match.
#### Configure docker-compose.yml for MySQL
The database section of the provided template for docker-compose.yml looks like this:
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

I reccomend that you choose a good password, though it may not "really" matter given the MySQL is hidden in a Docker container (don't hate me Winston).  Then you need to specify the path to your MySQL files.  If you do not configure the /var/lib/mysql you will loose your database when the image is rebuilt.  The formation of this line is "- host_path:container_path"  In the example below it is my home directory, which is alse the location of this Git repository.  Unfortunately you CANNOT use a relative path for some stupid Docker reason

```
- /Users/arh/proj/memosystem/memo_files/mysql:/var/lib/mysql
```
#### Configure the MySQL Database in settings.py
In the settings.py file you need to configure the SQLAlchemy to talk to MySQL.  I include an example for SQLite as well as MySQL
```
#os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@mysql/memos'
```
To do this you
1. remove the comment # from the MySQL URL (and make sure that the sqlite line is commented)
2. Change the URL for the user (user), password (password), server aka the docker container name (mysql) and database (memos)
Here is an example with user=memosystem password=memopw server=mysql database=memos  
```
os.environ['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://memosystem:memopw@mysql/memos'
```
### SQLite
If you want to use sqlite you modify the settings_local.py and the docker-compose.yml.  Start with the settings_local.py.  You want to turn on the sqlite url.  It is just a PATH to the site.db (the database file).  The name of the database file doesnt really matter - though I have been calling it site.db.  The "///sqlite/" part tells the sqlite to store the file in /app/memos/sqlite (in the container). 
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
You have two choices for authenticating users:
1. LDAP / Active Directory
2. Users as specific in the local database (of the system)

### LDAP / Active Directory
When you use LDAP, any user in your LDAP will have access to the system.  You will need to update these environment variables in your settings_local.py
```python
# LDAP settings. If LDAP_HOST is not specified, ldap lookups will be skipped.
os.environ["LDAP_HOST"] = "ldap.com" # host name of LDAP server without schema or port
os.environ["LDAP_PORT"] = "389" # 389 or 636
os.environ["LDAP_SCHEMA"] = "ldap" # ldap or ldaps
os.environ['LDAP_USER'] =  'service_acct' # Sevice account to authenticate to ldap server
os.environ['LDAP_PASSWORD'] = 'passwd' # password for service account
os.environ["LDAP_USERNAME"] = "CN={},OU=Users,OU=Company,DC=Company,DC=local".format(os.getenv('LDAP_USER')) # Full ldap locator of service account
os.environ["LDAP_BASE_DN"] = "OU=Company,DC=Company,DC=local" # Base OU to search for accounts in
os.environ["LDAP_USER_OBJECT_FILTER"] = "(&(objectclass=Person)(mail=%s))" # ldap lookup condition
os.environ["LDAP_USER_NAME"] = "sAMAccountName" # field to map to user id
os.environ["LDAP_EMAIL"] = "mail"  # field to map to email
os.environ["LDAP_ADMIN_GRP"] = "CN=A-GRP;CN=A2-GRP"  # Group name designating admin role (semicolon separated list)
os.environ["LDAP_READ_GRP"] = "CN=R-Grp"  # Group name designating read all role (semicolon separated list)
os.environ["PYTHON_LDAP_TRACE_LEVEL"] = "0"
```
### Local Authentication
If you choose to use local authentication, then users will be able to create accounts by themselves using the register button.  All of this user data will be stored in a table in the local database.  The adminstrator will also be able to update the users via the "configure" command which is found in the top level.  e.g. to create a local user you can run
```
configure -u arh:arh@badass.com:arh_secret_password
```
will make an account for ARH.  If you want to make arh an administrator you can the run
```
configure -ad arh true
```
## Mailer
## HTTPS / HTTP
# Start Docker
Once you have completed the configuration tasks you can start the Docker system by running
```
docker compose build
docker up -d
```
The first command will create the Docker images for the MySQL and the Memosystem.  The second command will start them up.  If you want to just run the "memosystem" you can run
```
docker compose build memosystem
docker up -d memosystem
```
# Initialization
Now that you have running containers for the database and the memosytem software, you will need to initialize the system.  To a first order for the system to work you need
1. The table structure created in the database server
2. The static files copied into the filesystem
There is a python program called "configure" that can perform a bunch of different functions

|Option|Description|
|---|---|
|-db or --database|Initialize all of the tables in the database|
|-s or --static|Copy all the static files from /memos/template_static_files to /memos/static|
|--all or -a|Intialize tables & copy static files i.e. -db & -s|
|-u or --user user\:email\:pw or configure --user user\:email:pw|Create a new user e.g. configure -u arh:alan@alan.com:secret123|
|-ad or --admin user true\|false|Make the user an admin e.g. configure -ad arh true|
|-ra or --readall user true\|false|Make the user a readll e.g. configure -ra harrold true|
|-p or --password user pw|Reset the password of the user to pw e.g. configure -p arh secret456|
|--resetdb|DESTRUCTIVE BLOW AWAY OF ALL DATABSE TABLES!!!! Gone forever|
|--clear|DESTRUCTIVE BLOW AWAY OF ALL MEMO FILES!!!! Gone forever|

To get the system going the first you will want to do something like this:
```
docker compose build
docker compose up -d
docker exec memosystem configure --all
docker exec memosystem configure --user user1:user1@something.com:secret123
docker exec memosystem configure -ad user1 true
```
In general if you have docker running you can run the configure command like this:
```
docker compose exec configure -u arh:arh@badass.com:secret314
```
Or you can shell into the docker container and then run the command like this:
```
docker exec -it memosystem /bin/sh
configure -ad harrold true
exit
```
# Filesystem
The raw memo files are stored in the directory memos/static/memos/username/memo#/memoversion/.   Individual memo files are assinged a random 48-bit UUID to mask their contents.  In order to know the mapping of the original filename to the memo you can either look in the database or in the json meta data file.  The file called meta-username-memo#-memoversion.json olds a copy of all of the meta data associated with that memo.  For instance meta-arh-1-a contains
```json
{"title": "test1", "number": 1, "version": "A", "confidential": false, "distribution": "", "keywords": "", "userid": "arh", "memo_state": "MemoState.Active", "signers": "", "references": "", "files": [("0fb820d8-5b9d-4c56-a6ba-4099a815b284","Alan Hawse IR Website.jpg")]}
```
If you look at the filesystem you can see that there are two files, the json and the 48-bit UUID file, which is really "Alan Hawse ..."
```
(env) arh (testdocker *) A $ pwd
/Users/arh/proj/memosystem/memo_files/static/memos/arh/1/A
(env) arh (testdocker *) A $ ls
0fb820d8-5b9d-4c56-a6ba-4099a815b284	meta-arh-1-A.json
(env) arh (testdocker *) A $ 
```
This was done to provide a mechanism to rebuild the memosystem in the event of something catostrophic.

# Using Some usefull Docker Commands

|Command|Function|
|---|---|
|docker compose build memosystem|Use the Docker compose file + the dockerfile to make images for the memosystem and the mysql database|
|docker compose build mysql|Build an image for mysql|
|docker ps|Show all running docker containers|
|docker compose up memosystem|Start the container for the memosystem|
|docker compose up -d memosystem|Start the memosystem container in the background (detached)|
|docker compose up -d mysql|Start the mysql server in the background|
|docker compose up|Bring up both the memosystem and mysql|
|docker compose restart|restart the mysql and memosystem|
|docker compose down|Stop the running containers for the memosystem and mysql|
|docker compose stop memosystem|stop the memosystem container|
|docker exec memosystem command|run the "command" inside of the memosystem container e.g ls /app|
|docker exec -it memosystem /bin/sh|Start an interactive shell inside of the running memosystem container|
|docker cp filename memosystem:/app|Copy a file from the host filesystem INTO the memosystem container|
|docker container ls|List the active containers ... same as docker ps|
|docker container rm memosystem|Remove the memosystem container|
|docker container prune|Remove all containers that are not running|
|docker image ls|List the active docker images|
|docker image rm memosystem|remove the docker image for the memosystem|
|docker image prune|Prune the inactive images|