# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 OpenStack Foundation
# Copyright 2012 Nebula, Inc.
# Copyright (c) 2012 X.commerce, a business unit of eBay Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import
import logging

from django.conf import settings
from manilaclient import client as manila_client
import six

from horizon import exceptions
from horizon.utils.memoized import memoized  # noqa
from openstack_dashboard.api import base


LOG = logging.getLogger(__name__)

MANILA_UI_USER_AGENT_REPR = "manila_ui_plugin_for_horizon"
MANILA_VERSION = "2.32"  # requires manilaclient 1.13.0 or newer
MANILA_SERVICE_TYPE = "sharev2"

# API static values
SHARE_STATE_AVAILABLE = "available"
DEFAULT_QUOTA_NAME = 'default'


def manilaclient(request):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    manila_url = ""
    try:
        manila_url = base.url_for(request, MANILA_SERVICE_TYPE)
    except exceptions.ServiceCatalogException:
        LOG.debug('no share service configured.')
        return None
    LOG.debug('manilaclient connection created using token "%s" and url "%s"' %
              (request.user.token.id, manila_url))
    c = manila_client.Client(
        MANILA_VERSION,
        username=request.user.username,
        input_auth_token=request.user.token.id,
        project_id=request.user.tenant_id,
        service_catalog_url=manila_url,
        insecure=insecure,
        cacert=cacert,
        http_log_debug=settings.DEBUG,
        user_agent=MANILA_UI_USER_AGENT_REPR,
    )
    c.client.auth_token = request.user.token.id
    c.client.management_url = manila_url

    return c


def share_list(request, search_opts=None):
    return manilaclient(request).shares.list(search_opts=search_opts)


def share_get(request, share_id):
    share_data = manilaclient(request).shares.get(share_id)
    return share_data


def share_create(request, size, name, description, proto, snapshot_id=None,
                 metadata=None, share_network=None, share_type=None,
                 is_public=None, availability_zone=None):
    return manilaclient(request).shares.create(
        proto, size, name=name, description=description,
        share_network=share_network, snapshot_id=snapshot_id,
        metadata=metadata, share_type=share_type, is_public=is_public,
        availability_zone=availability_zone)


def share_delete(request, share_id):
    return manilaclient(request).shares.delete(share_id)


def share_update(request, share_id, name, description, is_public=''):
    share_data = {'display_name': name, 'display_description': description}
    if not isinstance(is_public, six.string_types):
        is_public = six.text_type(is_public)
    if is_public and is_public.lower() != 'none':
        share_data['is_public'] = is_public
    return manilaclient(request).shares.update(share_id, **share_data)


def share_rules_list(request, share_id):
    return manilaclient(request).shares.access_list(share_id)


def share_export_location_list(request, share_id):
    return manilaclient(request).share_export_locations.list(share_id)


def share_instance_export_location_list(request, share_instance_id):
    return manilaclient(request).share_instance_export_locations.list(
        share_instance_id)


def share_allow(request, share_id, access_type, access_to, access_level):
    return manilaclient(request).shares.allow(
        share_id, access_type, access_to, access_level)


def share_deny(request, share_id, rule_id):
    return manilaclient(request).shares.deny(share_id, rule_id)


def share_manage(request, service_host, protocol, export_path,
                 driver_options=None, share_type=None,
                 name=None, description=None, is_public=False):
    return manilaclient(request).shares.manage(
        service_host=service_host,
        protocol=protocol,
        export_path=export_path,
        driver_options=driver_options,
        share_type=share_type,
        name=name,
        description=description,
        is_public=is_public,
    )


def migration_start(request, share, dest_host, force_host_assisted_migration,
                    writable, preserve_metadata, preserve_snapshots,
                    nondisruptive, new_share_network_id, new_share_type_id):
    return manilaclient(request).shares.migration_start(
        share,
        host=dest_host,
        force_host_assisted_migration=force_host_assisted_migration,
        writable=writable,
        preserve_metadata=preserve_metadata,
        preserve_snapshots=preserve_snapshots,
        nondisruptive=nondisruptive,
        new_share_network_id=new_share_network_id,
        new_share_type_id=new_share_type_id
    )


def migration_complete(request, share):
    return manilaclient(request).shares.migration_complete(share)


def migration_get_progress(request, share):
    return manilaclient(request).shares.migration_get_progress(share)


def migration_cancel(request, share):
    return manilaclient(request).shares.migration_cancel(share)


def share_unmanage(request, share):
    # Param 'share' can be either string with ID or object with attr 'id'.
    return manilaclient(request).shares.unmanage(share)


def share_extend(request, share_id, new_size):
    return manilaclient(request).shares.extend(share_id, new_size)


def share_snapshot_get(request, snapshot_id):
    return manilaclient(request).share_snapshots.get(snapshot_id)


def share_snapshot_update(request, snapshot_id, name, description):
    snapshot_data = {'display_name': name,
                     'display_description': description}
    return manilaclient(request).share_snapshots.update(
        snapshot_id, **snapshot_data)


def share_snapshot_list(request, detailed=True, search_opts=None,
                        sort_key=None, sort_dir=None):
    # Example of 'search_opts' value:
    # {'share_id': 'id_of_existing_share'}
    return manilaclient(request).share_snapshots.list(
        detailed=detailed,
        search_opts=search_opts,
        sort_key=sort_key,
        sort_dir=sort_dir,
    )


def share_snapshot_create(request, share_id, name=None,
                          description=None, force=False):
    return manilaclient(request).share_snapshots.create(
        share_id, force=force, name=name, description=description)


def share_snapshot_delete(request, snapshot_id):
    return manilaclient(request).share_snapshots.delete(snapshot_id)


def share_snapshot_allow(request, snapshot_id, access_type, access_to):
    return manilaclient(request).share_snapshots.allow(
        snapshot_id, access_type, access_to)


def share_snapshot_deny(request, snapshot_id, rule_id):
    return manilaclient(request).share_snapshots.deny(snapshot_id, rule_id)


def share_snapshot_rules_list(request, snapshot_id):
    return manilaclient(request).share_snapshots.access_list(snapshot_id)


def share_snap_export_location_list(request, snapshot):
    return manilaclient(request).share_snapshot_export_locations.list(
        snapshot=snapshot)


def share_snap_instance_export_location_list(request, snapshot_instance):
    return manilaclient(request).share_snapshot_export_locations.list(
        snapshot_instance=snapshot_instance)


def share_server_list(request, search_opts=None):
    return manilaclient(request).share_servers.list(search_opts=search_opts)


def share_server_get(request, share_serv_id):
    return manilaclient(request).share_servers.get(share_serv_id)


def share_server_delete(request, share_serv_id):
    return manilaclient(request).share_servers.delete(share_serv_id)


def share_network_list(request, detailed=False, search_opts=None):
    return manilaclient(request).share_networks.list(detailed=detailed,
                                                     search_opts=search_opts)


def share_network_create(request, neutron_net_id=None, neutron_subnet_id=None,
                         name=None, description=None):
    return manilaclient(request).share_networks.create(
        neutron_net_id=neutron_net_id, neutron_subnet_id=neutron_subnet_id,
        name=name, description=description)


def share_network_get(request, share_net_id):
    return manilaclient(request).share_networks.get(share_net_id)


def share_network_update(request, share_net_id, name=None, description=None):
    return manilaclient(request).share_networks.update(
        share_net_id, name=name, description=description)


def share_network_delete(request, share_network_id):
    return manilaclient(request).share_networks.delete(share_network_id)


def security_service_list(request, search_opts=None):
    return manilaclient(request).security_services.list(
        detailed=True,
        search_opts=search_opts)


def security_service_get(request, sec_service_id, search_opts=None):
    return manilaclient(request).security_services.get(sec_service_id)


def security_service_create(request, type, dns_ip=None, server=None,
                            domain=None, user=None, password=None, name=None,
                            description=None):
    return manilaclient(request).security_services.create(
        type, dns_ip=dns_ip, server=server, domain=domain, user=user,
        password=password, name=name, description=description)


def security_service_update(request, security_service_id, dns_ip=None,
                            server=None,
                            domain=None, user=None, password=None, name=None,
                            description=None):
    return manilaclient(request).security_services.update(
        security_service_id, dns_ip=dns_ip, server=server, domain=domain,
        user=user, password=password, name=name, description=description,
    )


def security_service_delete(request, security_service_id):
    return manilaclient(request).security_services.delete(security_service_id)


def share_network_security_service_add(request, share_network_id,
                                       security_service_id):
    return manilaclient(request).share_networks.add_security_service(
        share_network_id, security_service_id)


def share_network_security_service_remove(request, share_network_id,
                                          security_service_id):
    return manilaclient(request).share_networks.remove_security_service(
        share_network_id, security_service_id)


def share_network_security_service_list(request, share_network_id):
    return manilaclient(request).security_services.list(
        search_opts={'share_network_id': share_network_id})


def share_set_metadata(request, share_id, metadata):
    return manilaclient(request).shares.set_metadata(share_id, metadata)


def share_delete_metadata(request, share_id, keys):
    return manilaclient(request).shares.delete_metadata(share_id, keys)


def tenant_quota_get(request, tenant_id):
    return base.QuotaSet(manilaclient(request).quotas.get(tenant_id))


def tenant_quota_update(request, tenant_id, **kwargs):
    return manilaclient(request).quotas.update(tenant_id, **kwargs)


def default_quota_get(request, tenant_id):
    return base.QuotaSet(manilaclient(request).quotas.defaults(tenant_id))


def default_quota_update(request, **kwargs):
    manilaclient(request).quota_classes.update(DEFAULT_QUOTA_NAME, **kwargs)


def share_type_list(request):
    return manilaclient(request).share_types.list()


def share_type_get(request, share_type_id):
    return manilaclient(request).share_types.get(share_type_id)


def share_type_create(request, name, spec_driver_handles_share_servers,
                      spec_snapshot_support=True, is_public=True):
    return manilaclient(request).share_types.create(
        name=name,
        spec_driver_handles_share_servers=spec_driver_handles_share_servers,
        spec_snapshot_support=spec_snapshot_support,
        is_public=is_public)


def share_type_delete(request, share_type_id):
    return manilaclient(request).share_types.delete(share_type_id)


def share_type_get_extra_specs(request, share_type_id):
    return manilaclient(request).share_types.get(share_type_id).get_keys()


def share_type_set_extra_specs(request, share_type_id, extra_specs):
    return manilaclient(request).share_types.get(
        share_type_id).set_keys(extra_specs)


def share_type_unset_extra_specs(request, share_type_id, keys):
    return manilaclient(request).share_types.get(
        share_type_id).unset_keys(keys)


def share_type_access_list(request, share_type_id):
    return manilaclient(request).share_type_access.list(share_type_id)


def share_type_access_add(request, share_type_id, project_id):
    return manilaclient(request).share_type_access.add_project_access(
        share_type_id, project_id)


def share_type_access_remove(request, share_type_id, project_id):
    return manilaclient(request).share_type_access.remove_project_access(
        share_type_id, project_id)


def share_replica_list(request, share=None):
    return manilaclient(request).share_replicas.list(share)


def share_replica_create(request, share, availability_zone,
                         share_network=None):
    return manilaclient(request).share_replicas.create(
        share,
        availability_zone=availability_zone,
        share_network=share_network)


def share_replica_get(request, replica):
    return manilaclient(request).share_replicas.get(replica)


def share_replica_delete(request, replica):
    return manilaclient(request).share_replicas.delete(replica)


def share_replica_promote(request, replica):
    return manilaclient(request).share_replicas.promote(replica)


def share_replica_reset_status(request, replica, status):
    return manilaclient(request).share_replicas.reset_state(
        replica, status)


def share_replica_reset_state(request, replica, state):
    return manilaclient(request).share_replicas.reset_replica_state(
        replica, state)


def share_replica_resync(request, replica):
    return manilaclient(request).share_replicas.resync(replica)


def tenant_absolute_limits(request):
    limits = manilaclient(request).limits.get().absolute
    limits_dict = {}
    for limit in limits:
        # -1 is used to represent unlimited quotas
        if limit.value == -1:
            limits_dict[limit.name] = float("inf")
        else:
            limits_dict[limit.name] = limit.value
    return limits_dict


def share_instance_list(request):
    return manilaclient(request).share_instances.list()


def share_instance_get(request, share_instance_id):
    return manilaclient(request).share_instances.get(share_instance_id)


def availability_zone_list(request):
    return manilaclient(request).availability_zones.list()


def pool_list(request, detailed=False):
    return manilaclient(request).pools.list(detailed=detailed)


@memoized
def is_replication_enabled():
    manila_config = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
    return manila_config.get('enable_replication', True)


@memoized
def is_migration_enabled():
    manila_config = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
    return manila_config.get('enable_migration', True)
