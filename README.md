# Document Manager

## Installation
1. Configure the shell environment
2. Install the python environment
3. Configure a database
4. Setup the directory for the data
5. Initialize the database
6. Configure the authentication
7. Turn on the webserver

### Configure the shell environment
All of the configuration variable for the system (passwords etc.) must be initialized before starting the webserver.  In the Git Repository there is a file called "en.sh.template" which contains all of the needed variables.  I reccomend that you make a copy of this file e.g. "cp en.sh.tempalte env.sh".  Then edit the variables to suit your installation.  Before running the web server you can ". env.sh" to load the variables into the shell.

### Install the python environment
1. Make a virtual environment "python3 -v venv env"
2. Activate it "source env/bin/activate"
3. Install the requirements "pip install -r requirements.txt"

### Configure a database
The document manager system is built on SQL Alchecmy which allows it to retarget to different database.  I have tried by SQLLite and MySQL

#### Configure SQLLite

#### Configure MySQL
1. Create a new mysql database called "docmgr" 
2. Create a user for "docmgr"
3. Create a password for the "docmgr" user



### Setup the directory for the data


### Intialize the database

### Configure Authentication

### Turn on the webserver


# docker
cd memos
docker build -t memosystem .
docker run -d -p 5000:5000 -v /Users/arh/proj/memosystem/memo_files:/app/memos/static --name memosystem memosystem
docker exec memosystem python configure.py