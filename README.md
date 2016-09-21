Semantic Indexer
================

Introduction
----------------
This repository contains the semantic indexer and a tool for
sparql endpoints discovering registered in datahub.io.

Datahub Usage
---------------
If you want to update the list of sparql endpoints. You can run
datahub/find_sparql_endpoints.py, be sure to add your api key to
datahub/datahub-credentials.json before doing so.

Indexer Deployment Guide
----------------
Clone the project to your server and follow the following
instructions. This guide describes how to deploy the project
on debian. In other unix or linux distribution package names
may differ.

If you are familiar with rabbitmq and psql configuration
feel free to skip the relevant sections.

### Install Requirements.

1. Install postgresql, the development package is required by
	the python connector.

		apt-get install postgresql-9.4
		apt-get install postgresql-server-dev-9.4

2. Install rabbitmq.

		apt-get install rabbitmq-server

3. Install python.

		apt-get install python
		apt-get install python-pip

3. Install python requirements. You will probably want to
	install these in a virtualenv.

		pip install -r indexer/requirements.txt

### Postgres configuration.

It is important to note that the application assumes that peer
authentication is used and will attempt to connect without
using a password.

The default debian postgres installation is configured to use
peer authentication for all users. If you are not familiar with
postres's authentication configuration see [https://www.postgresql.org/docs/9.4/static/auth-methods.html](https://www.postgresql.org/docs/9.4/static/auth-methods.html). All you
need to know is that under the default configuration in order
to connect to a database the system username must match
the database user username.

For the simplest configuration do the following.

1. Create a new db user with the current username.

	Run

		createuser

2. Create a database.
	user name should match the system usersname
	Run

		sudo -u postgres createdb {databasename} -O {username}

3. Test that the user and database are correctly created.

	Run

		psql -d {databasename}

	You should now see a prompt connected to the database.
	If you are having problems go over the [postresql documentation](https://www.postgresql.org/docs/9.4/static/auth-pg-hba-conf.html)

### Rabbitmq configuration

On a fresh installation the user "guest" is created with
password "guest" and read and write permissions to the
"/" vhost.

If you are not familiar with the rabbitmq
server see [its documentation](https://www.rabbitmq.com/admin-guide.html)

If you wish to create another user and vhost use the following
commands.

Run

	rabbitmqctl add_user {username} {password}

	rabbitmqctl add_vhost {vhost}

	rabbitmqctl set_permissions [-p vhost] {username} ".*" ".*" ".*"

The last command sets full configure, write and read.
permissions to the user for the specified host. By default
new users have no permissions.

### Indexer configuration

Important note:

The application assumes that postgresql is setup to use peer
authentication and will NOT attempt to use a password.

1. Ensure settings.json is correct.

	1. database name and database user name.
		Set the database name and the database owners name
		the user name should match the system users username.

		i.e

			"database": {
				"name": "backlinks",
				"user": "pavlov"
			}

	2. Rabbitmq credentials
		Set the rabbitmq server credentials to use.

		If you have not created a new user and vhost you can
		use the following.

			"rabbitmq": {
				"user": "guest",
				"pass": "guest",
				"vhost": "/"
			}

	3. Data-paths
		This section contains only one item the path to the
		file containing the sparql endpoints to query.

	3. Worker counts.
		db-workers the count of processes writing to the
		database.
		web-workers the count of processes querying sparql
		endpoints and processing results. Keep in mind
		processing the results is cpu intensive

	4. Queue names
		db-queue, web-worker-endpoints-queue, log-event-queue. These
		names set the names of the rabbitmq queues used for communication
		between the different workers.

	5. Logging
		These are python logging settings if you are not familiar with
		the python logging system see the [relevant python documentation]
		(https://docs.python.org/2/library/logging.html)

Running indexer/index.py
------------------------
index.py will output a unique session id, that has been passed
as an argument to all child processes. In order to kill all
the processes use the following command.

	ps ax | grep {session_id} | sed 's/^ //' | cut -d ' ' -f 1 | xargs kill

i.e

	ps ax | grep 10169789888 | sed 's/^ //' | cut -d ' ' -f 1 | xargs kill
