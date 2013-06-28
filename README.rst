======
Selena
======

Installation
------------

Requirements
~~~~~~~~~~~~
Selena requires Python 2.7 which is included in the latest Ubuntu Server 12.04 LTS systems::

  $ sudo apt-get install python-dev python-virtualenv

Message queue
~~~~~~~~~~~~~

Selena communicates with a central queue with `Redis <http://redis.io/>`_ as the broker. Install redis::

  $ sudo apt-get install redis-server

Since lost tasks can always be resent, the durability guarantees that Redis
provides by default are not necessary. You can significantly speed up the queue
by commenting out the ``save`` lines from ``/etc/redis/redis.conf``.

We can check the status of the Redis server::

  $ redis-cli -h localhost -p 6379 -n 0 info

Virtual Environment
~~~~~~~~~~~~~~~~~~~

Let's create a virtual environment for Python in the user's home::

  $ virtualenv . --distribute --no-site-packages

System User
~~~~~~~~~~~

Unprivileged and not owned by a person::

  $ sudo adduser --home /home/selena selena
  $ sudo su - selena

In any shell the user can *activate* the virtual environment. As a result of
that, the default Python executable and helper scripts will point to those
within the virtualenv directory structure::

  $ which python
  /usr/local/bin/python
  $ . bin/activate
  (selena)$ which python
  /home/selena/bin/python

Database
~~~~~~~~

Selena uses and supports MySQL. To install MySQL invoke::

  $ sudo apt-get install mysql-server libmysqlclient-dev libmysqld-dev

You now have to create a database and a user for Selena system. You can find many tutorials for that on the Internet.


Cache
~~~~~

Selena requires some cache system like *memcached*. Install::

  $ sudo apt-get install memcached


Installing from pip
~~~~~~~~~~~~~~~~~~~

Simply invoke::

  (selena)$ pip install selena

Installing from sources
~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, to live on the bleeding edge, you can clone the selena git
repository to ``project`` and install it manually::

  (selena)$ git clone git://github.com/allegro/selena.git project
  (selena)$ cd project
  (selena)$ pip install -e .


Selena Agent
~~~~~~~~~~~~

To function properly, Selena needs `Selena-agent <http://github.com/allegro/selena-agent>`_ package installed and configured.


Configuration
-------------

Create file /INSTALL_DIR/selena/settings-local.py and fill in the appropriate
data.

Fill MySQL connection data::

  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your database name',
        'USER': 'your database username',
        'PASSWORD': 'your database password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB,character_set_connection=utf8,collation_connection=utf8_unicode_ci'
        }
    }
  }

Generate new secret keys::

  SECRET_KEY = 'very_unique_string'
  AES_SECRET_KEY = b'sixteen byte key'

Set the number of minutes that will be displayed by the service errors, example 30::

  ERROR_TIME_INTERVAL =  30

Define RQ queues. The `default` queue is required. You have to also define one queue for main selena agent, for example `agent_1`::

  RQ_QUEUES = {
      'default': {
          'HOST': '127.0.0.1',  # Redis host
          'PORT': 6379,  # Redis port
          'DB': None,
          'PASSWORD': None,
      },
      'agent_1': {
          'HOST': '127.0.0.1',
          'PORT': 6379,
          'DB': None,
          'PASSWORD': None,
     },
  }

You can define additional queues: `planner`, `archiving`, `dispacher`, `monitors`, `stats`. They are used as follows:

    *planner* - enable or disable planned technical breaks

    *archiving* - create partitions, archive data

    *dispacher* - run monitoring tasks for services

    *monitors* - collect results from agents

    *stats* - calculate statistics


You also have to configure cache. Sample cache configuration (for default `memcached` configs)::

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }


Database preparation
~~~~~~~~~~~~~~~~~~~~

After creating the ``settings-local.py`` file, synchronize the database with
sources by running the standard ``syncdb`` management command::

  $(selena): selena syncdb

then run migrations command::

  $(selena): selena migrate


Create partitions in the database by using the command::

  $(selena): selena createpartitions


Run web interface
~~~~~~~~~~~~~~~~~

To run selena web interface use the command::

  (selena)$ selena runserver 8080


Configuration agents
~~~~~~~~~~~~~~~~~~~~

When your selena web interface is running you must add a main agents to your selena instance. Open this link in your browser `http://localhost:8080/admin/services/agent/add/ <http://localhost:8080/admin/services/agent/add/>`_ and log in into administration panel.

You will see a form where you have to fill the name of your main agent, add a queue (remember the name of the queue must be set in your Selena agent `settings-local.py` file), and check the main agent checkbox. After the agent is added you will see `Salt` column in your agent row. Copy this string and add to the Selena-agent `settings-local.py` file in `SALT` variable. It is very important, because without it there will be no communication with the Selena-agent.

Add monitored services
~~~~~~~~~~~~~~~~~~~~~~
In administration panel add a service which will be monitored by Selena.
Open this link in browser `http://localhost:8080/admin/services/service/add/ <http://localhost:8080/admin/services/service/add/>`_ and add a service URL to be monitored.


Commands
~~~~~~~~

Run a single monitoring service::

  (selena)$: selena monitorall

Search incidents::

  (selena)$: selena searchincidents

Activate/Deactivate technical breaks::

  (selena)$: selena technicalbreaks

For optimization, there are commands to archive service monitoring results.
If you create partitions in MySQL database run command::

 (selena)$: selena createpartitions

You will need to run the command that merges monitoring data older than 8 days and moves it to the archive::

  (selena)$: selena makearchive

If you want to run the commands asynchronically, you can add an ``--async-mode=1`` option to them.

Automation
~~~~~~~~~~

You can configure Cron to monitor automatically in background. To edit crontab run command::

    $(selena): crontab -e

and add this content::

  */1 * * * * /YOUR_VIRTUAL_ENV_PATH/bin/selena monitorall
  */1 * * * * /YOUR_VIRTUAL_ENV_PATH/bin/selena searchincidents --async-mode=1
  */5 * * * * /YOUR_VIRTUAL_ENV_PATH/bin/selena technicalbreaks --async-mode=1
  0 1 * * * /YOUR_VIRTUAL_ENV_PATH/bin/selena createpartitions --async-mode=1
  30 1 * * * /YOUR_VIRTUAL_ENV_PATH/bin/selena makearchive --async-mode=1

Of course you can set your own time to execute these commands in Cron.


To see the results of the monitoring in a browser, open the following address:
`http://localhost:8080 <http://localhost:8080>`_
