# Memo System
The Memo System is a light weight web based document managment system for maintaining and distributing internal memos.  This readme provides an overview of the system as well as instructions for installation and configuration.  This document has the following sections:
1. Architecture
2. Install with git clone
3. Configuration
4. Initialization
5. Filesystem
6. Azure
7. Useful Docker Commands

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
|memos/settings_local.py|memos/settings_local.py.template|The configuration file for the Flask application|

On my unix box I run the following commands to copy the templates
``` bash
cp docker-compose.yml.template docker-compose.yml
cp memos/Dockerfile.template memos/Dockerfile
cp memos/settings_local.py.template memos/settings_local.py
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
The system is built using [SQL Alchemy](https://www.sqlalchemy.org) to support all database interaction.  This library gives you a selection of targetable databases.  I have tested [SQLite](https://www.sqlite.org/),  [MySQL](https://mysql.com) and Microsoft SQL Server but the others will probably work as well - YMMV.  For a production use I recommend MySQL.
### MySQL
You may choose to target a MySQL server that you already have in your enterprise.  To do this you can skip the docker configuration.  If you want a Docker container running a private MySQL you will need to modify the "docker-compose.yml" (which you copied from the template) to setup the users, passwords and files.  Then you will need to modify the settings_local.py to setup to match.
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
    # type in the passwords into the file memos/memos/settings_local.py
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

I reccomend that you choose a good password, though it may not "really" matter given the MySQL is hidden in a Docker container (don't hate me Winston).  Then you need to specify the path to your MySQL files.  If you do not configure the /var/lib/mysql you will loose your database when the image is rebuilt.  The formation of this line is "- host_path:container_path"  In the example below it is my home directory, which is also the location of this Git repository.  Unfortunately you CANNOT use a relative path for some stupid Docker reason

```
- /Users/arh/proj/memosystem/memo_files/mysql:/var/lib/mysql
```
#### Configure the MySQL Database in settings_local.py
In the settings_local.py file you need to configure the SQLAlchemy to talk to MySQL.  I include an example for SQLite as well as MySQL
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

### SQL Server
I have no idea how to setup a SQL Server.  So you will have to sort that out yourself.  However, on the client side, the SQL Alchemy to SQL Server connection is done using [pyodbc](https://pypi.org/project/pyodbc/) and [Linux SQL Server odbc driver](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16)  

To use a SQL Server database you will need to configure the URL which has this crazy format:
```
os.environ['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+18+for+SQL+Server'
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


# Azure
Inside of my company we are running the memosystem inside of an Azure Container Instance (ACI).  To make this work you need:
1. Azure Resource Group
2. Azure Virtual Network and Subnet
3. Azure Storage Account with File Shares
4. Azure Container Instance
5. Azure Routing
6. Other Userful Azure Commands

## Azure Portal Shell
The simplest thing for me was to use the bash shell available on the Azure portal.  You can run it by clicking in the upper right side of the portal.
![Architecture](https://github.com/iotexpert/memosystem/blob/main/doc/azure-portal.png?raw=true)

## Azure Resource Group
Once you have the shell going you can create a new resource group by running
```
az group create -l westus -n RG-Memo
```
## Azure Virtual Network (VNET) and Subnet
The container you make will need to be attached to a private network for use inside of your organization.  In order to create a subnet for your container inside of the resouce group run
```
MEMO_RG=RG-Memo
MEMO_VNET=memo_vnet
MEMO_ADDRESS=10.1.2.0/24
MEMO_SUBNET=memo_subnet

az network vnet create --resource-group $MEMO_RG --name $MEMO_VNET \
       --address-prefix $MEMO_ADDRESS \
       --subnet-name $MEMO_SUBNET \
       --subnet-prefix $MEMO_ADDRESS
```

## Azure Storage Account with File Shares
The files inside of the container will be BLOWN AWAY when you delete the container.  You want to make sure and save your memos (and configuration).  To do this you should create a Storage Account and a file share to mount to the inside of your Azure Container Instance.  To do this
```
MEMO_STORAGE_BASE=memofiles
MEMO_LOCATION=westus
MEMO_SHARE_NAME=memo_files

az storage account create -g $MEMO_RG -n $MEMO_STORAGE_BASE -l $MEMO_LOCATION --sku Standard_LRS
MEMO_STORAGE_KEY=$(az storage account keys list --resource-group $MEMO_RG --account-name $MEMO_STORAGE_BASE --query "[0].value" --output
 tsv)
az storage share create --account-name $MEMO_STORAGE_BASE --name $MEMO_SHARE_NAME --account-key $MEMO_STORAGE_KEY
```

## Azure Container Instance
Now that you have a network and a fileshare the last step is to actually create the container and get it going.  You have two basic choices for the source of your image, either an [Azure Container Registry](https://docs.microsoft.com/en-us/cli/azure/acr?view=azure-cli-latest) or the [Docker Hub](https://hub.docker.com).  I orignally planned on using the Azure Container Registry, but the only value I could figure out was that it was "private".  If you decide that you want to do that, you can read the instruction at the link above.  It is my intent that as we make changes to the MemoSystem we wil keep a fresh image posted to docker hub.  To do that I do the following (but you wont have to because it is already done)
```
docker build -t iotexpert/memos:latest .
docker push iotexpert/memos:latest
```

The following comnmand will pull the image of the memo system from the docker hub (which you created above) and insert it into a running Azure Container Instance
```
MEMO_CONTAINER=container-memo

az container create -g $MEMO_RG --name $MEMO_CONTAINER \
   --vnet $MEMO_VNET --subnet $MEMO_SUBNET \
             --image iotexpert/memos:latest \
             --location $MEMO_LOCATION \
             --os-type Linux \
             --ports 80 \
             --azure-file-volume-account-name $MEMO_STORAGE_BASE \
             --azure-file-volume-share-name $MEMO_SHARE_NAME \
             --azure-file-volume-account-key $MEMO_STORAGE_KEY \
             --azure-file-volume-mount-path /app/memos/static
```

## Azure Routing
The final step is to attach your virtual network to your internal network.  This will be organization dependant.

## Other Userful Azure Commands
1. Log into the container instance
2. Look at the running container
3. Examine the Log Files

### Log into the container instance
```
az container exec --resource-group RG-Docker-Memosystem --name container-memo-prod --exec-command "/bin/sh"
```

### List the running containers
```
alan@Azure:~$ az container list -g RG-Docker-MemoSystem -o table
Name                 ResourceGroup         Status     Image                   IP:ports        Network    CPU/Memory       OsType    Location
-------------------  --------------------  ---------  ----------------------  --------------  ---------  ---------------  --------  ----------
container-memo-prod  RG-Docker-MemoSystem  Succeeded  iotexpert/memos:latest  10.9.1.4:80,80  Private    1.0 core/1.5 gb  Linux     westus
container-memo-test  RG-Docker-MemoSystem  Succeeded  iotexpert/memos:latest  10.9.0.4:80,80  Private    1.0 core/1.5 gb  Linux     westus
```
### Examine the log files
```
alan@Azure:~$ az container logs --resource-group RG-Docker-Memosystem --name container-memo-prod
Checking for script in /app/prestart.sh
Running script /app/prestart.sh
Running inside /app/prestart.sh, you could add migrations to this file, e.g.:

#! /usr/bin/env sh

# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head

/usr/lib/python2.7/dist-packages/supervisor/options.py:461: UserWarning: Supervisord is running as root and it is searching for its configuration file in default locations (including its current working directory); you probably want to specify a "-c" argument specifying an absolute path to a configuration file for improved security.
  'Supervisord is running as root and it is searching '
2022-06-02 11:15:10,223 CRIT Supervisor is running as root.  Privileges were not dropped because no user is specified in the config file.  If you intend to run as root, you can set user=root in the config file to avoid this message.
2022-06-02 11:15:10,223 INFO Included extra file "/etc/supervisor/conf.d/supervisord.conf" during parsing
2022-06-02 11:15:10,231 INFO RPC interface 'supervisor' initialized
2022-06-02 11:15:10,232 CRIT Server 'unix_http_server' running without any HTTP authentication checking
2022-06-02 11:15:10,232 INFO supervisord started with pid 1

... [ a bunch of stuff deleted]

vacuum = true
die-on-term = true
base = /app
venv = /app/env
module = app
callable = app
chdir = /app
ini = /etc/uwsgi/uwsgi.ini

... [ a bunch of stuff deleted]

uWSGI running as root, you can use --uid/--gid/--chroot options
*** WARNING: you are running uWSGI as root !!! (use the --uid flag) *** 
python threads support enabled

spawned uWSGI worker 2 (pid: 22, cores: 2)
running "unix_signal:15 gracefully_kill_them_all" (master-start)...
2022-06-02 11:15:13,174 INFO success: quit_on_failure entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
[pid: 22|app: 0|req: 1/1] 10.9.1.4 () {32 vars in 326 bytes} [Thu Jun  2 11:24:28 2022] GET / => generated 3674 bytes in 244 msecs (HTTP/1.1 200) 3 headers in 171 bytes (1 switches on core 0)
10.9.1.4 - - [02/Jun/2022:11:24:28 +0000] "GET / HTTP/1.1" 200 3674 "-" "curl/7.64.0" "-"
[pid: 20|app: 0|req: 1/2] 10.9.1.4 () {32 vars in 326 bytes} [Thu Jun  2 14:30:36 2022] GET / => generated 3674 bytes in 246 msecs (HTTP/1.1 200) 3 headers in 171 bytes (1 switches on core 0)
10.9.1.4 - - [02/Jun/2022:14:30:36 +0000] "GET / HTTP/1.1" 200 3674 "-" "curl/7.64.0" "-"
```

# Some Usefull Docker Commands

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

