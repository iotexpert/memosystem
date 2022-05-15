# Memo System

# Architecture
![Architecture](https://github.com/iotexpert/memosystem/blob/main/arch.png?raw=true)
# Configuration
In order to use the system you will need to take the following steps:
1. Choose a Database (SQLite or MySQL)
2. Set the passwords for the database
3. Choose AD/LDAP or Local Authentication
5. Set the passwords for the admin account (if using local authentication)
6. Setting the mailer configuration
7. Choose the location of memo files
8. Choose HTTPS or HTTP (intelligence test)
9. Choose Docker or Bare Metal

All of the system configuration is done by copying the appropriate template and then making modifcations that are specific to your configuration
|File|Template|Description|
|---|---|---|
|docker-compose.yml|docker.compose.template||
|memos/Dockerfile|memos/Dockerfile.template||
|memos/settings.py|memos/settings.py.template||
## Database
balasdfklj
## Authentication
## Mailer
## HTTPS / HTTP
## Docker


# Initialization
In order to intialize the system there is a python program called "configure.py"  that can perform two functions
1. Initialize the tables in the database based on the database configuration
2. Copy the static files from the memos/memos/template_static_files into the "memos/memos/static" directory

# Docker
You can use Docker containers to host the Flask memo application and a MySQL database.  In order to make this work you will need to configure the following files:

# Configure bare metal + sqlite
# Configure bare metal + MySql
# Configure Docker

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
