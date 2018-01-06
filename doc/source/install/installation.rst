============
Installation
============

Manual Installation
-------------------

For Manila UI installation in RDO, see: :ref:`install-rdo`.
For other distributions, begin by
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

.. _install-rdo:

Installing Manila UI in RDO
---------------------------

In order to install Manila UI in `RDO <https://www.rdoproject.org>`__,
please follow the steps below (you may need to use `sudo` privileges
if you are not root)::

# yum install -y openstack-manila-ui
# systemctl restart httpd
# systemctl restart memcached

Manila UI will now be available through OpenStack Horizon; look for
the Shares tab under Project > Compute. You can access Horizon with
Manila UI using the same URL and port as before.
