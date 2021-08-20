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

from manilaclient.v2 import messages
from manilaclient.v2 import security_services
from manilaclient.v2 import share_access_rules
from manilaclient.v2 import share_export_locations
from manilaclient.v2 import share_group_snapshots
from manilaclient.v2 import share_group_types
from manilaclient.v2 import share_groups
from manilaclient.v2 import share_instances
from manilaclient.v2 import share_networks
from manilaclient.v2 import share_replicas
from manilaclient.v2 import share_servers
from manilaclient.v2 import share_snapshot_export_locations
from manilaclient.v2 import share_snapshots
from manilaclient.v2 import share_types
from manilaclient.v2 import shares


class FakeAPIClient(object):
    client = "fake_client"


share = shares.Share(
    shares.ShareManager(FakeAPIClient),
    {'id': "11023e92-8008-4c8b-8059-7f2293ff3887",
     'status': 'available',
     'size': 40,
     'name': 'Share name',
     'description': 'Share description',
     'is_public': False,
     'share_proto': 'NFS',
     'metadata': {},
     'created_at': '2014-01-27 10:30:00',
     'share_server_id': '1',
     'share_network_id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'availability_zone': 'Test AZ',
     'replication_type': 'readable',
     'share_group_id': 'fake_share_group_id',
     'mount_snapshot_support': False})

nameless_share = shares.Share(
    shares.ShareManager(FakeAPIClient),
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
     'availability_zone': 'Test AZ',
     'replication_type': None,
     'mount_snapshot_support': False})

share_with_metadata = shares.Share(
    shares.ShareManager(FakeAPIClient),
    {'id': "0ebb3748-c1dr-4bb6-8315-0354e7691fff",
     'status': 'available',
     'size': 40,
     'name': 'Share with metadata',
     'description': 'Share description',
     'share_proto': 'NFS',
     'metadata': {'aaa': 'bbb'},
     'created_at': '2016-06-31 00:00:00',
     'share_server_id': '1',
     'share_network_id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'availability_zone': 'Test AZ',
     'replication_type': 'readable',
     'mount_snapshot_support': False})

other_share = shares.Share(
    shares.ShareManager(FakeAPIClient),
    {'id': "21023e92-8008-1234-8059-7f2293ff3889",
     'status': 'in-use',
     'size': 10,
     'name': 'my_share',
     'description': '',
     'share_proto': 'NFS',
     'metadata': {},
     'created_at': '2013-04-01 10:30:00',
     'share_type': None,
     'share_server_id': '1',
     'share_network_id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'availability_zone': 'Test AZ',
     'replication_type': 'readable',
     'mount_snapshot_support': False})

shares_list = [share, nameless_share, other_share]

share_replica = share_replicas.ShareReplica(
    share_replicas.ShareReplicaManager(FakeAPIClient),
    {'id': '11023e92-8008-4c8b-8059-replica00001',
     'availability_zone': share.availability_zone,
     'host': 'fake_host_1',
     'share_id': share.id,
     'status': 'available',
     'replica_state': 'active',
     'created_at': '2016-07-19 19:46:13',
     'updated_at': '2016-07-19 19:47:14'}
)

share_replica2 = share_replicas.ShareReplica(
    share_replicas.ShareReplicaManager(FakeAPIClient),
    {'id': '11023e92-8008-4c8b-8059-replica00002',
     'availability_zone': share.availability_zone,
     'host': 'fake_host_2',
     'share_id': share.id,
     'status': 'available',
     'replica_state': 'in_sync',
     'created_at': '2016-07-19 20:46:13',
     'updated_at': '2016-07-19 20:47:14'}
)

share_replica3 = share_replicas.ShareReplica(
    share_replicas.ShareReplicaManager(FakeAPIClient),
    {'id': '11023e92-8008-4c8b-8059-replica00003',
     'availability_zone': share.availability_zone,
     'host': 'fake_host_3',
     'share_id': share.id,
     'status': 'available',
     'replica_state': 'active',
     'created_at': '2016-07-19 21:46:13',
     'updated_at': '2016-07-19 21:47:14'}
)

share_mount_snapshot = shares.Share(
    shares.ShareManager(FakeAPIClient),
    {'id': "11023e92-8008-4c8b-8059-7f2293ff3888",
     'status': 'available',
     'size': 40,
     'name': 'Share name',
     'description': 'Share description',
     'share_proto': 'NFS',
     'metadata': {},
     'created_at': '2014-01-27 10:30:00',
     'share_server_id': '1',
     'share_network_id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'availability_zone': 'Test AZ',
     'replication_type': 'readable',
     'mount_snapshot_support': True})

admin_export_location = share_export_locations.ShareExportLocation(
    share_export_locations.ShareExportLocationManager(FakeAPIClient),
    {'id': '6921e862-88bc-49a5-a2df-efeed9acd583',
     'path': '1.1.1.1:/path/to/admin/share',
     'preferred': False,
     'is_admin_only': True,
     'share_instance_id': 'e1c2d35e-fe67-4028-ad7a-45f668732b1d'}
)

user_export_location = share_export_locations.ShareExportLocation(
    share_export_locations.ShareExportLocationManager(FakeAPIClient),
    {'id': 'b6bd76ce-12a2-42a9-a30a-8a43b503867d',
     'path': '2.2.2.2:/path/to/user/share',
     'preferred': True,
     'is_admin_only': False,
     'share_instance_id': 'e1c2d35e-fe67-4028-ad7a-45f668732b1d'}
)

export_locations = [admin_export_location, user_export_location]

admin_snapshot_export_locations = [
    share_snapshot_export_locations.ShareSnapshotExportLocation(
        share_snapshot_export_locations.ShareSnapshotExportLocationManager(
            FakeAPIClient),
        {'id': '6921e862-88bc-49a5-a2df-efeed9acd584',
         'path': '1.1.1.1:/path/to/admin/share',
         'is_admin_only': True,
         'share_snapshot_instance_id': 'e1c2d35e-fe67-4028-ad7a-45f668732b1e'}
    ),
    share_snapshot_export_locations.ShareSnapshotExportLocation(
        share_snapshot_export_locations.ShareSnapshotExportLocationManager(
            FakeAPIClient),
        {'id': '6921e862-88bc-49a5-a2df-efeed9acd585',
         'path': '1.1.1.2:/path/to/admin/share',
         'is_admin_only': False,
         'share_snapshot_instance_id': 'e1c2d35e-fe67-4028-ad7a-45f668732b1f'}
    )
]

user_snapshot_export_locations = [
    share_snapshot_export_locations.ShareSnapshotExportLocation(
        share_snapshot_export_locations.ShareSnapshotExportLocationManager(
            FakeAPIClient),
        {'id': 'b6bd76ce-12a2-42a9-a30a-8a43b503867e',
         'path': '1.1.1.1:/path/to/user/share_snapshot'}
    ),
    share_snapshot_export_locations.ShareSnapshotExportLocation(
        share_snapshot_export_locations.ShareSnapshotExportLocationManager(
            FakeAPIClient),
        {'id': 'b6bd76ce-12a2-42a9-a30a-8a43b503867f',
         'path': '1.1.1.2:/not/too/long/path/to/user/share_snapshot'}
    )
]
ip_rule = share_access_rules.ShareAccessRule(
    share_access_rules.ShareAccessRuleManager(FakeAPIClient),
    {'id': 'ca8b755c-fe13-497f-81d0-fd2f13a30a78',
     'access_level': 'rw',
     'access_to': '1.1.1.1',
     'access_type': 'ip',
     'state': 'active',
     'access_key': '',
     'created_at': '2021-03-03T14:29:41.000000',
     'updated_at': '',
     "metadata": {},
     })

user_rule = share_access_rules.ShareAccessRule(
    share_access_rules.ShareAccessRuleManager(FakeAPIClient),
    {'id': '0837072-c49e-11e3-bd64-60a44c371189',
     'access_level': 'rw',
     'access_to': 'someuser',
     'access_type': 'user',
     'state': 'active',
     'access_key': '',
     'created_at': '2021-03-03T14:29:41.000000',
     'updated_at': '',
     'metadata': {'abc': 'ddd'},
     })

cephx_rule = share_access_rules.ShareAccessRule(
    share_access_rules.ShareAccessRuleManager(FakeAPIClient),
    {'id': '235481bc-1a84-11e6-9666-68f728a0492e',
     'access_level': 'rw',
     'access_to': 'alice',
     'access_type': 'cephx',
     'state': 'active',
     'access_key': 'AQAdFCNYDCapMRAANuK/CiEZbog2911a+t5dcQ==',
     'created_at': '2021-03-03T14:29:41.000000',
     'updated_at': '',
     'metadata': {'test': 'true'},
     })

share_access_list = [user_rule, cephx_rule, ip_rule]

snapshot = share_snapshots.ShareSnapshot(
    share_snapshots.ShareSnapshotManager(FakeAPIClient),
    {'id': '5f3d1c33-7d00-4511-99df-a2def31f3b5d',
     'name': 'test snapshot',
     'description': 'share snapshot',
     'size': 40,
     'status': 'available',
     'share_id': '11023e92-8008-4c8b-8059-7f2293ff3887'})

snapshot_mount_support = share_snapshots.ShareSnapshot(
    share_snapshots.ShareSnapshotManager(FakeAPIClient),
    {'id': '5f3d1c33-7d00-4511-99df-a2def31f3b5e',
     'name': 'test snapshot',
     'description': 'share snapshot',
     'size': 40,
     'status': 'available',
     'share_id': '11023e92-8008-4c8b-8059-7f2293ff3888'})

inactive_share_network = share_networks.ShareNetwork(
    share_networks.ShareNetworkManager(FakeAPIClient),
    {'id': '6f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'name': 'test_share_net',
     'description': 'test share network',
     'status': 'INACTIVE',
     'neutron_net_id': 'fake_neutron_net_id',
     'neutron_subnet_id': 'fake_neutron_subnet_id'})

active_share_network = share_networks.ShareNetwork(
    share_networks.ShareNetworkManager(FakeAPIClient),
    {'id': '7f3d1c33-8d00-4511-29df-a2def31f3b5d',
     'name': 'test_share_net',
     'description': 'test share network',
     'status': 'ACTIVE',
     'neutron_net_id': 'fake_neutron_net_id',
     'neutron_subnet_id': 'fake_neutron_subnet_id'})

sec_service = security_services.SecurityService(
    security_services.SecurityServiceManager(FakeAPIClient),
    {'id': '7f3d1c33-8d10-4511-29df-a2def31f3b5d',
     'server': '1.1.1.1',
     'dns_ip': '2.2.2.2',
     'ou': 'someOU',
     'user': 'someuser',
     'password': 'somepass',
     'type': 'active_directory',
     'name': 'test-sec-service',
     'description': 'test security service',
     'domain': 'testdomain',
     })


share_instance = share_instances.ShareInstance(
    share_instances.ShareInstanceManager(FakeAPIClient),
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
    share_instances.ShareInstanceManager(FakeAPIClient),
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
    share_servers.ShareServerManager(FakeAPIClient),
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
    share_servers.ShareServerManager(FakeAPIClient),
    {'id': 'fake_share_server_id2',
     'status': 'error',
     'share_network_id': 'fake_share_network_id2',
     'share_network_name': 'fake_share_network_name2',
     'project_id': 'fake_project_id2',
     'backend_details': {},
     'host': 'fakehost2@fakebackend2#fakepool2'}
)

share_type = share_types.ShareType(
    share_types.ShareTypeManager(FakeAPIClient),
    {'id': 'share-type-id1',
     'name': 'test-share-type1',
     'share_type_access:is_public': True,
     'extra_specs': {
         'snapshot_support': True,
         'driver_handles_share_servers': False}
     }
)

share_type_private = share_types.ShareType(
    share_types.ShareTypeManager(FakeAPIClient),
    {'id': 'share-type-id2',
     'name': 'test-share-type2',
     'share_type_access:is_public': False,
     'extra_specs': {'driver_handles_share_servers': False}}
)

share_type_dhss_true = share_types.ShareType(
    share_types.ShareTypeManager(FakeAPIClient),
    {'id': 'share-type-id3',
     'name': 'test-share-type3',
     'share_type_access:is_public': True,
     'extra_specs': {'driver_handles_share_servers': True}}
)

share_type_alt = share_types.ShareType(
    share_types.ShareTypeManager(FakeAPIClient),
    {'id': 'share-type-id4',
     'name': 'test-share-type4',
     'share_type_access:is_public': True,
     'extra_specs': {
         'snapshot_support': True,
         'driver_handles_share_servers': False}
     }
)

share_group_type = share_group_types.ShareGroupType(
    share_group_types.ShareGroupTypeManager(FakeAPIClient),
    {'id': 'fake_share_group_type_id1',
     'name': 'fake_share_group_type_name',
     'share_types': [share_type.id],
     'group_specs': {'k1': 'v1', 'k2': 'v2'},
     'is_public': True}
)

share_group_type_private = share_group_types.ShareGroupType(
    share_group_types.ShareGroupTypeManager(FakeAPIClient),
    {'id': 'fake_private_share_group_type_id2',
     'name': 'fake_private_share_group_type_name',
     'share_types': [share_type.id, share_type_private.id],
     'group_specs': {'k1': 'v1', 'k2': 'v2'},
     'is_public': False}
)

share_group_type_dhss_true = share_group_types.ShareGroupType(
    share_group_types.ShareGroupTypeManager(FakeAPIClient),
    {'id': 'fake_share_group_type_id3',
     'name': 'fake_share_group_type_name',
     'share_types': [share_type_dhss_true.id],
     'group_specs': {'k3': 'v3', 'k4': 'v4'},
     'is_public': True}
)

share_group_type_alt = share_group_types.ShareGroupType(
    share_group_types.ShareGroupTypeManager(FakeAPIClient),
    {'id': 'fake_share_group_type_id4',
     'name': 'fake_share_group_type_name',
     'share_types': [share_type_alt.id],
     'group_specs': {'k5': 'v5', 'k6': 'v6'},
     'is_public': True}
)

share_group = share_groups.ShareGroup(
    share_groups.ShareGroupManager(FakeAPIClient),
    {'id': 'fake_share_group_id',
     'name': 'fake_share_group_name',
     'description': 'fake sg description',
     'status': 'available',
     'share_types': [share_type.id],
     'share_group_type_id': share_group_type.id,
     'source_share_group_snapshot_id': None,
     'share_network_id': None,
     'share_server_id': None,
     'availability_zone': None,
     'host': 'fake_host_987654321',
     'consistent_snapshot_support': None,
     'created_at': '2017-05-31T13:36:15.000000',
     'project_id': 'fake_project_id_987654321'}
)

share_group_nameless = share_groups.ShareGroup(
    share_groups.ShareGroupManager(FakeAPIClient),
    {'id': 'fake_nameless_share_group_id',
     'name': None,
     'status': 'available',
     'share_types': [share_type.id],
     'share_group_type_id': share_group_type.id,
     'source_share_group_snapshot_id': None,
     'share_network_id': None,
     'share_server_id': None,
     'availability_zone': None,
     'host': 'fake_host_987654321',
     'consistent_snapshot_support': None,
     'created_at': '2017-05-31T13:36:15.000000',
     'project_id': 'fake_project_id_987654321'}
)

share_group_dhss_true = share_groups.ShareGroup(
    share_groups.ShareGroupManager(FakeAPIClient),
    {'id': 'fake_dhss_true_share_group_id',
     'name': 'fake_dhss_true_share_group_name',
     'status': 'available',
     'share_types': [share_type_dhss_true.id],
     'share_group_type_id': share_group_type_dhss_true.id,
     'source_share_group_snapshot_id': None,
     'share_network_id': 'fake_share_network_id',
     'share_server_id': 'fake_share_server_id',
     'availability_zone': None,
     'host': 'fake_host_987654321',
     'consistent_snapshot_support': 'pool',
     'created_at': '2017-05-31T23:59:59.000000',
     'project_id': 'fake_project_id_987654321'}
)

share_group_snapshot = share_group_snapshots.ShareGroupSnapshot(
    share_group_snapshots.ShareGroupSnapshotManager(FakeAPIClient),
    {'id': 'fake_share_group_snapshot_id_1',
     'name': 'fake_share_group_snapshot_name',
     'status': 'available',
     'share_group_id': share_group.id,
     'description': 'fake sgs description',
     'created_at': '2017-06-01T13:13:13.000000',
     'project_id': 'fake_project_id_987654321',
     'members': [
         {'share_id': 'fake_share_id_1', 'id': 'fake_ssi_id_1', 'size': 1},
         {'share_id': 'fake_share_id_2', 'id': 'fake_ssi_id_2', 'size': 2},
     ]}
)

share_group_snapshot_nameless = share_group_snapshots.ShareGroupSnapshot(
    share_group_snapshots.ShareGroupSnapshotManager(FakeAPIClient),
    {'id': 'fake_share_group_snapshot_id_2_nameless',
     'name': None,
     'status': 'available',
     'share_group_id': share_group_nameless.id,
     'description': 'fake nameless sgs description',
     'created_at': '2017-06-02T14:14:14.000000',
     'project_id': 'fake_project_id_987654321',
     'members': []}
)

# Manila Limits
limits = {"totalSharesUsed": 1,
          "totalShareSnapshotsUsed": 1,
          "totalShareGigabytesUsed": 500,
          "totalSnapshotGigabytesUsed": 500,
          "maxTotalShares": 10,
          "maxTotalShareSnapshots": 10,
          "maxTotalShareGigabytes": 1000,
          "maxTotalSnapshotGigabytes": 1000,
          }

limits_negative = {"totalSharesUsed": 10,
                   "totalShareSnapshotsUsed": 10,
                   "totalShareGigabytesUsed": 1000,
                   "totalSnapshotGigabytesUsed": 1000,
                   "maxTotalShares": 10,
                   "maxTotalShareSnapshots": 10,
                   "maxTotalShareGigabytes": 1000,
                   "maxTotalSnapshotGigabytes": 1000,
                   }

# Manila User Messages
fake_message_1 = messages.Message(
    messages.MessageManager(FakeAPIClient),
    {'resource_id': "351cc796-2d79-4a08-b878-a8ed933b6b68",
     'message_level': 'ERROR',
     'user_message': 'allocate host: No storage could be allocated for'
                     ' this share request. Trying again with a different'
                     ' size or share type may succeed.',
     'expires_at': '2017-07-10T10:27:43.000000',
     'id': '4b319d29-d5b7-4b6e-8e7c-8d6e53f3c3d5',
     'created_at': '2017-07-10T10:26:43.000000',
     'detail_id': '002',
     'request_id': 'req-24e7ccb6-a7d5-4ddd-a8e4-d8f72a4509c8',
     'project_id': '2e3de76b49b444fd9dc7ca9f7048ce6b',
     'resource_type': 'SHARE',
     'action_id': '001'})

fake_message_2 = messages.Message(
    messages.MessageManager(FakeAPIClient),
    {'resource_id': "25b4c0cc-e711-4c6f-b9fd-72d6b5c62bce",
     'message_level': 'ERROR',
     'user_message': 'Driver does not expect share-network to be provided '
                     'with current configuration.',
     'expires_at': '2018-09-10T09:37:45.000000',
     'id': 'd01d03ee-7758-4175-a6b5-853329dd2f4e',
     'created_at': '2018-09-10T09:36:45.000000',
     'detail_id': '003',
     'request_id': 'req-fa568ab0-d6b3-4b32-899d-637ee006fed4',
     'project_id': '2e3de76b49b444fd9dc7ca9f7048ce6b',
     'resource_type': 'SHARE',
     'action_id': '002'})

fake_message_3 = messages.Message(
    messages.MessageManager(FakeAPIClient),
    {'resource_id': "4befdc84-2796-44e1-8645-14b651bfb787",
     'message_level': 'ERROR',
     'user_message': 'Share has no replica with "replica_state" '
                     'set to "active"',
     'expires_at': '2020-09-09T22:37:13.000000',
     'id': '1e1c493f-d07d-48e9-93a8-ef5ad4b8ca8a',
     'created_at': '2020-09-09T22:36:13.000000',
     'detail_id': '004',
     'request_id': 'req-29449bc8-d0ec-4d6b-b37c-85d0f04251b1',
     'project_id': '2e3de76b49b444fd9dc7ca9f7048ce6b',
     'resource_type': 'SHARE_REPLICA',
     'action_id': '002'})
