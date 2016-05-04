# Copyright (c) 2014 NetApp, Inc.
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
import collections

try:
    # NOTE(vponomaryov): Try import latest modules, assuming we have
    # manilaclient that is new enough and have v2 API support.
    from manilaclient.v2 import quotas
    from manilaclient.v2 import security_services
    from manilaclient.v2 import share_networks
    from manilaclient.v2 import share_snapshots
    from manilaclient.v2 import shares
except ImportError:
    # NOTE(vponomaryov): If we got here then we have old manilaclient.
    from manilaclient.v1 import quotas
    from manilaclient.v1 import security_services
    from manilaclient.v1 import share_networks
    from manilaclient.v1 import share_snapshots
    from manilaclient.v1 import shares

from manilaclient.v2 import share_export_locations
from manilaclient.v2 import share_instances
from manilaclient.v2 import share_servers

from openstack_dashboard import api
from openstack_dashboard.usage import quotas as usage_quotas


share = shares.Share(
    shares.ShareManager(None),
    {'id': "11023e92-8008-4c8b-8059-7f2293ff3887",
     'status': 'available',
     'size': 40,
     'name': 'Share name',
     'description': 'Share description',
     'share_proto': 'NFS',
     'metadata': {},
     'created_at': '2014-01-27 10:30:00',
     'share_server_id': '1',
     'share_network_id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'availability_zone': 'Test AZ'})

nameless_share = shares.Share(
    shares.ShareManager(None),
    {'id': "4b069dd0-6eaa-4272-8abc-5448a68f1cce",
     'status': 'available',
     'size': 10,
     'name': '',
     'description': '',
     'share_proto': 'NFS',
     'export_location': "/dev/hda",
     'metadata': {},
     'created_at': '2010-11-21 18:34:25',
     'share_type': 'vol_type_1',
     'share_server_id': '1',
     'share_network_id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'availability_zone': 'Test AZ'})

other_share = shares.Share(
    shares.ShareManager(None),
    {'id': "21023e92-8008-1234-8059-7f2293ff3889",
     'status': 'in-use',
     'size': 10,
     'name': u'my_share',
     'description': '',
     'share_proto': 'NFS',
     'metadata': {},
     'created_at': '2013-04-01 10:30:00',
     'share_type': None,
     'share_server_id': '1',
     'share_network_id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'availability_zone': 'Test AZ'})

admin_export_location = share_export_locations.ShareExportLocation(
    share_export_locations.ShareExportLocationManager(None),
    {'id': '6921e862-88bc-49a5-a2df-efeed9acd583',
     'path': '1.1.1.1:/path/to/admin/share',
     'preferred': False,
     'is_admin_only': True,
     'share_instance_id': 'e1c2d35e-fe67-4028-ad7a-45f668732b1d'}
)

user_export_location = share_export_locations.ShareExportLocation(
    share_export_locations.ShareExportLocationManager(None),
    {'id': 'b6bd76ce-12a2-42a9-a30a-8a43b503867d',
     'path': '2.2.2.2:/path/to/user/share',
     'preferred': True,
     'is_admin_only': False,
     'share_instance_id': 'e1c2d35e-fe67-4028-ad7a-45f668732b1d'}
)

export_locations = [admin_export_location, user_export_location]

rule = collections.namedtuple('Access', ['access_type', 'access_to', 'status',
                                         'id'])

user_rule = rule('user', 'someuser', 'active',
                 '10837072-c49e-11e3-bd64-60a44c371189')
ip_rule = rule('ip', '1.1.1.1', 'active',
               '2cc8e2f8-c49e-11e3-bd64-60a44c371189')
cephx_rule = rule('cephx', 'alice', 'active',
                  '235481bc-1a84-11e6-9666-68f728a0492e')

snapshot = share_snapshots.ShareSnapshot(
    share_snapshots.ShareSnapshotManager(None),
    {'id': '5f3d1c33-7d00-4511-99df-a2def31f3b5d',
     'name': 'test snapshot',
     'description': 'share snapshot',
     'size': 40,
     'status': 'available',
     'share_id': '11023e92-8008-4c8b-8059-7f2293ff3887'})

inactive_share_network = share_networks.ShareNetwork(
    share_networks.ShareNetworkManager(None),
    {'id': '6f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'name': 'test_share_net',
     'description': 'test share network',
     'status': 'INACTIVE',
     'neutron_net_id': 'fake_neutron_net_id',
     'neutron_subnet_id': 'fake_neutron_subnet_id'})

active_share_network = share_networks.ShareNetwork(
    share_networks.ShareNetworkManager(None),
    {'id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'name': 'test_share_net',
     'description': 'test share network',
     'status': 'ACTIVE',
     'neutron_net_id': 'fake_neutron_net_id',
     'neutron_subnet_id': 'fake_neutron_subnet_id'})

sec_service = security_services.SecurityService(
    security_services.SecurityServiceManager(None),
    {'id': '7f3d1c33-8d10-4511-29df-a2def31f3b5d',
     'server': '1.1.1.1',
     'dns_ip': '2.2.2.2',
     'user': 'someuser',
     'password': 'somepass',
     'type': 'active_directory',
     'name': 'test-sec-service',
     'description': 'test security service',
     'domain': 'testdomain',
     })


share_instance = share_instances.ShareInstance(
    share_instances.ShareInstanceManager(None),
    {'id': 'fake_share_instance_no_ss_id',
     'status': 'available',
     'host': 'host1@backend1#pool1',
     'availability_zone': 'zone1',
     'share_id': 'fake_share_id_1',
     'share_network_id': 'fake_share_network_id_1',
     'share_server_id': 'fake_share_server_id_1',
     'created_at': '2016-04-26 13:14:15'}
)


share_instance_no_ss = share_instances.ShareInstance(
    share_instances.ShareInstanceManager(None),
    {'id': 'fake_share_instance_id',
     'status': 'available',
     'host': 'host2@backend2#pool2',
     'availability_zone': 'zone2',
     'share_id': 'fake_share_id_2',
     'share_network_id': None,
     'share_server_id': None,
     'created_at': '2016-04-26 14:15:16'}
)

share_server = share_servers.ShareServer(
    share_servers.ShareServerManager(None),
    {'id': 'fake_share_server_id1',
     'status': 'active',
     'share_network_id': 'fake_share_network_id1',
     'share_network_name': 'fake_share_network_name1',
     'project_id': 'fake_project_id1',
     'backend_details': {
         'foo_key': 'foo_value',
         'bar_key_foo': 'bar_value_foo',
     },
     'host': 'fakehost1@fakebackend1#fakepool1'}
)

share_server_errored = share_servers.ShareServer(
    share_servers.ShareServerManager(None),
    {'id': 'fake_share_server_id2',
     'status': 'error',
     'share_network_id': 'fake_share_network_id2',
     'share_network_name': 'fake_share_network_name2',
     'project_id': 'fake_project_id2',
     'backend_details': {},
     'host': 'fakehost2@fakebackend2#fakepool2'}
)


# Quota Sets
quota_data = dict(shares='1',
                  share_snapshots='1',
                  share_gigabytes='1000')
quota = quotas.QuotaSet(quotas.QuotaSetManager(None), quota_data)

# Quota Usages
quota_usage_data = {'gigabytes': {'used': 0, 'quota': 1000},
                    'shares': {'used': 0, 'quota': 10},
                    'snapshots': {'used': 0, 'quota': 10},
                    'share_networks': {'used': 0, 'quota': 10}}
quota_usage = usage_quotas.QuotaUsage()
for k, v in quota_usage_data.items():
    quota_usage.add_quota(api.base.Quota(k, v['quota']))
    quota_usage.tally(k, v['used'])

# Manila Limits
limits = {"absolute": {"totalSharesUsed": 1,
                       "totalShareGigabytesUsed": 5,
                       "maxTotalShareGigabytes": 1000,
                       "maxTotalShares": 10}}
