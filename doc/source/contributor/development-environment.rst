.. _development-environment:

====================
Developing manila-ui
====================

For simple documentation and code fixes, you don't need a comprehensive test
environment with this project's main dependencies such as manila,
python-manilaclient and horizon. Before submitting any code fixes for review,
you can run :ref:`unit-tests` locally. To try your changes with manila-ui and
Horizon and all other dependencies, we recommend the use of DevStack.

DevStack
--------

DevStack can help you setup a simple development environment for developing and
testing manila-ui. Read the section about DevStack in the `manila
contributor guide`_.

.. note::

    We absolutely recommend using a ``fake shared file system back end`` as
    opposed to a real storage system to experience the full capabilities of
    manila UI. Manila UI is built with the assumption that all APIs manila
    exposes are usable. In reality, different real world storage back ends
    have `different capabilities`_ and this project doesn't need to worry
    about them to provide a general purpose graphical user interface to Manila.
    A fake driver provides fake storage, so don't expect to be able to mount
    or use the shared file systems that you create with it.

You can use the following local.conf file to configure DevStack including
Manila and manila-ui using a few fake back ends:

.. code-block:: console

    [[local|localrc]]

    # auth
    ADMIN_PASSWORD=nomoresecret
    DATABASE_PASSWORD=$ADMIN_PASSWORD
    RABBIT_PASSWORD=$ADMIN_PASSWORD
    SERVICE_PASSWORD=$ADMIN_PASSWORD

    # enable logging for DevStack
    LOGFILE=/opt/stack/logs/stack.sh.log

    # Logging mode for DevStack services
    VERBOSE=True

    # manila
    enable_plugin manila https://opendev.org/openstack/manila

    # manila-ui
    enable_plugin manila-ui https://opendev.org/openstack/manila-ui

    # python-manilaclient
    LIBS_FROM_GIT=python-manilaclient

    # share driver
    SHARE_DRIVER=manila.tests.share.drivers.dummy.DummyDriver

    # share types
    MANILA_DEFAULT_SHARE_TYPE_EXTRA_SPECS='snapshot_support=True create_share_from_snapshot_support=True revert_to_snapshot_support=True mount_snapshot_support=True'
    MANILA_CONFIGURE_DEFAULT_TYPES=True

    # backends and groups
    MANILA_ENABLED_BACKENDS=alpha,beta,gamma,delta
    MANILA_CONFIGURE_GROUPS=alpha,beta,gamma,delta,membernet,adminnet

    # alpha
    MANILA_OPTGROUP_alpha_share_driver=manila.tests.share.drivers.dummy.DummyDriver
    MANILA_OPTGROUP_alpha_driver_handles_share_servers=True
    MANILA_OPTGROUP_alpha_share_backend_name=ALPHA
    MANILA_OPTGROUP_alpha_network_config_group=membernet
    MANILA_OPTGROUP_alpha_admin_network_config_group=adminnet

    # beta
    MANILA_OPTGROUP_beta_share_driver=manila.tests.share.drivers.dummy.DummyDriver
    MANILA_OPTGROUP_beta_driver_handles_share_servers=True
    MANILA_OPTGROUP_beta_share_backend_name=BETA
    MANILA_OPTGROUP_beta_network_config_group=membernet
    MANILA_OPTGROUP_beta_admin_network_config_group=adminnet

    # gamma
    MANILA_OPTGROUP_gamma_share_driver=manila.tests.share.drivers.dummy.DummyDriver
    MANILA_OPTGROUP_gamma_driver_handles_share_servers=False
    MANILA_OPTGROUP_gamma_share_backend_name=GAMMA
    MANILA_OPTGROUP_gamma_replication_domain=DUMMY_DOMAIN

    # delta
    MANILA_OPTGROUP_delta_share_driver=manila.tests.share.drivers.dummy.DummyDriver
    MANILA_OPTGROUP_delta_driver_handles_share_servers=False
    MANILA_OPTGROUP_delta_share_backend_name=DELTA
    MANILA_OPTGROUP_delta_replication_domain=DUMMY_DOMAIN

    # membernet
    MANILA_OPTGROUP_membernet_network_api_class=manila.network.standalone_network_plugin.StandaloneNetworkPlugin
    MANILA_OPTGROUP_membernet_standalone_network_plugin_gateway=10.0.0.1
    MANILA_OPTGROUP_membernet_standalone_network_plugin_mask=24
    MANILA_OPTGROUP_membernet_standalone_network_plugin_network_type=vlan
    MANILA_OPTGROUP_membernet_standalone_network_plugin_segmentation_id=1010
    MANILA_OPTGROUP_membernet_standalone_network_plugin_allowed_ip_ranges=10.0.0.10-10.0.0.209
    MANILA_OPTGROUP_membernet_network_plugin_ipv4_enabled=True

    # adminnet
    MANILA_OPTGROUP_adminnet_network_api_class=manila.network.standalone_network_plugin.StandaloneNetworkPlugin
    MANILA_OPTGROUP_adminnet_standalone_network_plugin_gateway=11.0.0.1
    MANILA_OPTGROUP_adminnet_standalone_network_plugin_mask=24
    MANILA_OPTGROUP_adminnet_standalone_network_plugin_network_type=vlan
    MANILA_OPTGROUP_adminnet_standalone_network_plugin_segmentation_id=1011
    MANILA_OPTGROUP_adminnet_standalone_network_plugin_allowed_ip_ranges=11.0.0.10-11.0.0.19,11.0.0.30-11.0.0.39,11.0.0.50-11.0.0.199
    MANILA_OPTGROUP_adminnet_network_plugin_ipv4_enabled=True


Once your DevStack is ready, you can log into the OpenStack Dashboard and
explore the ``Share`` dashboards under `Project` and `Admin` sections that are
included due to manila-ui.

See the `Horizon user guide`_ for instructions regarding logging into the
OpenStack Dashboard.


.. _unit-tests:

Running unit tests
------------------

The unit tests can be executed directly from within this Manila UI plugin
project directory by using::

    $ cd ../manila-ui
    $ tox

This is made possible by the dependency in test-requirements.txt upon the
horizon source, which pulls down all of the horizon and openstack_dashboard
modules that the plugin uses.

To run only py3 unit tests, use following command::

    $ tox -e py3

To run unit tests using specific Django version use the following::

    $ tox -e py3-dj22
    $ tox -e py3-dj110



.. _manila contributor guide: https://docs.openstack.org/manila/latest/contributor/development-environment-devstack.html
.. _different capabilities: https://docs.openstack.org/manila/latest/admin/share_back_ends_feature_support_mapping.html
.. _Horizon user guide: https://docs.openstack.org/horizon/latest/user/log-in.html
