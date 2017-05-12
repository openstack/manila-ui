========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/manila-ui.svg
    :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

===============================
manila-ui
===============================

Manila Management Dashboard

* Free software: Apache license

.. Uncomment these bullet items when the project is integrated into OpenStack
.. item * Documentation: http://docs.openstack.org/developer/manila-ui

* Source: http://git.openstack.org/cgit/openstack/manila-ui
* Bugs: http://bugs.launchpad.net/manila-ui


Installation instructions
-------------------------

For Manila UI installation in RDO, see:
`Installing Manila UI in RDO`_. For other distributions, begin by
cloning the Horizon and Manila UI repositories::

    git clone https://github.com/openstack/horizon
    git clone https://github.com/openstack/manila-ui

Create a virtual environment and install Horizon dependencies::

    cd horizon
    python tools/install_venv.py

Set up your ``local_settings.py`` file::

    cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py

Open up the copied ``local_settings.py`` file in your preferred text
editor. You will want to customize several settings:

-  ``OPENSTACK_HOST`` should be configured with the hostname of your
   OpenStack server. Verify that the ``OPENSTACK_KEYSTONE_URL`` and
   ``OPENSTACK_KEYSTONE_DEFAULT_ROLE`` settings are correct for your
   environment. (They should be correct unless you modified your
   OpenStack server to change them.)


Install Manila UI with all dependencies in your virtual environment::

    tools/with_venv.sh pip install -e ../manila-ui/

And enable it in Horizon::

    cp ../manila-ui/manila_ui/local/enabled/_*.py openstack_dashboard/local/enabled
    cp ../manila-ui/manila_ui/local/local_settings.d/_90_manila_*.py openstack_dashboard/local/local_settings.d


Starting the app
----------------

If everything has gone according to plan, you should be able to run::

    ./run_tests.sh --runserver 0.0.0.0:8080

and have the application start on port 8080. The horizon dashboard will
be located at http://localhost:8080/

Installing Manila UI in RDO
---------------------------

In order to install Manila UI in [RDO](https://www.rdoproject.org),
please follow the steps below (you may need to use `sudo` privileges
if you are not root)::

# yum install -y openstack-manila-ui
# systemctl restart httpd
# systemctl restart memcached

Manila UI will now be available through OpenStack Horizon; look for
the Shares tab under Project > Compute. You can access Horizon with
Manila UI using the same URL and port as before.

_`Configuration`
----------------

It is possible to enable or disable some Manila UI features. To do so,
look for files located in "manila_ui/local/local_settings.d/" directory,
where you can redefine the values of the OPENSTACK_MANILA_FEATURES dict::

    * enable_replication
    * enable_migration
    * enable_public_share_type_creation
    * enable_public_shares
    * enabled_share_protocols

By default, enabled_share_protocols within the OPENSTACK_MANILA_FEATURES
dict contains a list with all the supported protocols. The operator can
change this to display to users only those protocols that has been deployed
and are available to use. E.g. if only NFS is available, the operator is
expected to redefine enabled_share_protocols as follows:

.. code-block:: python

    OPENSTACK_MANILA_FEATURES = {
       'enable_replication': True,
       'enable_migration': True,
       'enable_public_share_type_creation': True,
       'enable_public_shares': True,
       'enabled_share_protocols': ['NFS'],
    }

Contributing
------------

When implementing a new feature, you may think about making it optional,
so it could be enabled or disabled in different deployments.

How to use it:

.. code-block:: python

    from django.conf import settings
    manila_config = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
    manila_config.get('your_new_config_option', 'value_of_config_option')

See `Configuration`_ section for more configuration details.

It is also expected that each addition of new logic to Manila UI is covered by
unit tests.

Test modules should be located under "manila_ui/tests", satisfying
the following template when tests are written for a specific module::

    manila_ui[/tests]/path/to/[test_]modulename.py

However, when testing the flow between different modules (using test app),
the tests can be added to a test module that can satisfy
the following template::

    manila_ui[/tests]/path/to/directory/tests.py

Manila UI tests use the mock library for testing.

Running unit tests
------------------

The unit tests can be executed directly from within this Manila UI plugin
project directory by using::

    $ cd ../manila-ui
    $ tox

This is made possible by the dependency in test-requirements.txt upon the
horizon source, which pulls down all of the horizon and openstack_dashboard
modules that the plugin uses.

To run only py27 unit tests, use following command::

    $ tox -e py27

To run only py34 unit tests, use following command::

    $ tox -e py34

To run unit tests using specific Django version use the following::

    $ tox -e py27dj17
    $ tox -e py27dj18
    $ tox -e py27dj19
    $ tox -e py27dj110
