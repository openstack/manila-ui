=============
Configuration
=============

It is possible to enable or disable some Manila UI features. To do so,
look for files located in "manila_ui/local/local_settings.d/" directory,
where you can redefine the values of the OPENSTACK_MANILA_FEATURES dict:

* enable_share_groups
* enable_replication
* enable_migration
* enable_public_share_type_creation
* enable_public_share_group_type_creation
* enable_public_shares
* enabled_share_protocols

By default, enabled_share_protocols within the OPENSTACK_MANILA_FEATURES
dict contains a list with all the supported protocols. The operator can
change this to display to users only those protocols that has been deployed
and are available to use. E.g. if only NFS is available, the operator is
expected to redefine enabled_share_protocols as follows:

.. code-block:: python

    OPENSTACK_MANILA_FEATURES = {
       'enable_share_groups': True,
       'enable_replication': True,
       'enable_migration': True,
       'enable_public_share_type_creation': True,
       'enable_public_share_group_type_creation': True,
       'enable_public_shares': True,
       'enabled_share_protocols': ['NFS'],
    }
