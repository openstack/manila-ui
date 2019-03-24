============
Installation
============

DevStack Installation
---------------------

Add this repo as an external repository into your ``local.conf`` file::

    [[local|localrc]]
    enable_plugin manila-ui https://git.openstack.org/openstack/manila-ui

Manual Installation
-------------------

Begin by installing Horizon following the `Horizon Manual Installation Guide <https://docs.openstack.org/horizon/latest/install/from-source.html>`__
and clone Manila UI repository::

    git clone https://git.openstack.org/openstack/manila-ui

Install Manila UI with all dependencies. From within the horizon folder::

    pip install -e ../manila-ui/

And enable it in Horizon.::

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
