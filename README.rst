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

    cp ../manila-ui/manila_ui/enabled/_90_manila_*.py openstack_dashboard/local/enabled


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

Unit testing
------------

The unit tests can be executed directly from within this Manila UI plugin
project directory by using::

    cd ../manila-ui
    ./run_tests.sh

This is made possible by the dependency in test-requirements.txt upon the
horizon source, which pulls down all of the horizon and openstack_dashboard
modules that the plugin uses.
