# Copyright (c) 2015 Mirantis, Inc.
# All Rights Reserved.
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

import ddt

from openstack_dashboard.api import base as horizon_api

from manila_ui.api import manila as api
from manila_ui.tests import helpers as base


@ddt.ddt
class ManilaApiTests(base.APITestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.id = "fake_id"
        self.mock_object(horizon_api, "QuotaSet")

    # Share tests

    @ddt.data(
        {},
        None,
        {"name": "fake_share"},
        {"limit": "3"},
        {"host": "fake_share_host"},
        {"sort_key": "id", "sort_dir": "asc"},
    )
    def test_share_list(self, kwargs):
        result = api.share_list(self.request, search_opts=kwargs)

        self.assertEqual(
            self.manilaclient.shares.list.return_value, result)

        expected_kwargs = kwargs or {}
        self.manilaclient.shares.list.assert_called_once_with(
            search_opts=expected_kwargs)

    def test_share_get(self):
        api.share_get(self.request, self.id)

        self.manilaclient.shares.get.assert_called_once_with(self.id)

    @ddt.data((None, True), ("some_fake_sg_id", False))
    @ddt.unpack
    def test_share_create(self, sg_id, is_public):
        kwargs = {
            "share_network": "fake_sn",
            "snapshot_id": "fake_snapshot_id",
            "metadata": {"k1": "v1", "k2": "v2"},
            "share_type": "fake_st",
            "is_public": is_public,
            "availability_zone": "fake_az",
            "share_group_id": sg_id,
        }
        size = 5
        name = "fake_name"
        desc = "fake_description"
        proto = "fake_share_protocol"

        api.share_create(self.request, size, name, desc, proto, **kwargs)

        self.manilaclient.shares.create.assert_called_once_with(
            proto, size, name=name, description=desc, **kwargs)

    @ddt.data(None, "some_fake_sg_id")
    def test_share_delete(self, sg_id):
        s_id = "fake_share_id"

        api.share_delete(self.request, s_id, sg_id)

        self.manilaclient.shares.delete.assert_called_once_with(
            s_id, share_group_id=sg_id)

    @ddt.data(("", "", True), ("share_name", "", True),
              ("share_name", "share_description", True),
              ("", "share_description", True),
              ("", "", False), ("share_name", "", False),
              ("share_name", "share_description", False),
              ("", "share_description", False))
    @ddt.unpack
    def test_share_update(self, name, description, is_public):
        api.share_update(self.request, self.id, name, description, is_public)

        self.manilaclient.shares.update.assert_called_once_with(
            self.id, display_name=name, display_description=description,
            is_public=is_public)

    # Shares ACLs tests

    def test_share_rules_list(self):
        result = api.share_rules_list(self.request, self.id)

        self.assertEqual(
            self.manilaclient.share_access_rules.
            access_list.return_value, result)

        self.manilaclient.share_access_rules.\
            access_list.assert_called_once_with(self.id)

    def test_share_rule_get(self):
        result = api.share_rule_get(self.request, self.id)

        self.assertEqual(
            self.manilaclient.share_access_rules.get.
            return_value, result)

        self.manilaclient.share_access_rules.get.\
            assert_called_once_with(self.id)

    def test_share_rule_set_metadata(self):
        fake_metadata = {
            "aim": "testing",
            "project": "test",
        }

        api.share_rule_set_metadata(
            self.request, self.id, fake_metadata)

        self.manilaclient.share_access_rules.\
            set_metadata.assert_called_once_with(self.id, fake_metadata)

    def test_share_rule_unset_metadata(self):
        fake_key = "test"

        api.share_rule_unset_metadata(
            self.request, self.id, fake_key)

        self.manilaclient.share_access_rules.\
            unset_metadata.assert_called_once_with(self.id, fake_key)

    def test_list_share_export_locations(self):
        api.share_export_location_list(self.request, self.id)

        self.manilaclient.share_export_locations.list.assert_called_once_with(
            self.id)

    def test_list_share_instance_export_locations(self):
        api.share_instance_export_location_list(self.request, self.id)

        client = self.manilaclient
        client.share_instance_export_locations.list.assert_called_once_with(
            self.id)

    @ddt.data(("ip", "10.0.0.13", "rw", {'testkey': "testval"}),
              ("ip", "10.0.0.13", None, None),
              ("ip", "10.0.0.13", "ro", {'key1': "val1"}),
              ("user", "demo", "rw", {'key2': "val2"}),
              ("user", "demo", None, None),
              ("user", "demo", "ro", None),
              ("cephx", "alice", "rw", {'test': "some"}),
              ("cephx", "alice", None, None),
              ("cephx", "alice", "ro", None))
    @ddt.unpack
    def test_share_allow(self, access_type, access_to, access_level, metadata):
        api.share_allow(self.request, self.id, access_type,
                        access_to, access_level, metadata)

        self.manilaclient.shares.allow.assert_called_once_with(
            self.id, access_type, access_to, access_level, metadata)

    def test_share_deny(self):
        fake_rule_id = "fake_rule_id"
        api.share_deny(self.request, self.id, fake_rule_id)

        self.manilaclient.shares.deny.assert_called_once_with(
            self.id, fake_rule_id)

    # Share manage/unmanage tests

    def test_share_manage(self):
        api.share_manage(
            self.request,
            service_host="fake_service_host",
            protocol="fake_protocol",
            export_path="fake_export_path",
            driver_options={"fake_key": "fake_value"},
            share_type="fake_share_type",
            name="fake_name",
            description="fake_description",
            is_public="fake_is_public",
        )

        self.manilaclient.shares.manage.assert_called_once_with(
            service_host="fake_service_host",
            protocol="fake_protocol",
            export_path="fake_export_path",
            driver_options={"fake_key": "fake_value"},
            share_type="fake_share_type",
            name="fake_name",
            description="fake_description",
            is_public="fake_is_public",
        )

    def test_share_unmanage(self):
        api.share_unmanage(self.request, self.id)

        self.manilaclient.shares.unmanage.assert_called_once_with(self.id)

    # Share migration tests

    def test_migration_start(self):
        api.migration_start(self.request, 'fake_share', 'fake_host', False,
                            True, True, True, True, 'fake_net_id',
                            'fake_type_id')

        self.manilaclient.shares.migration_start.assert_called_once_with(
            'fake_share',
            host='fake_host',
            force_host_assisted_migration=False,
            nondisruptive=True,
            writable=True,
            preserve_metadata=True,
            preserve_snapshots=True,
            new_share_network_id='fake_net_id',
            new_share_type_id='fake_type_id'
        )

    def test_migration_complete(self):
        api.migration_complete(self.request, 'fake_share')

        self.manilaclient.shares.migration_complete.assert_called_once_with(
            'fake_share')

    def test_migration_cancel(self):
        api.migration_cancel(self.request, 'fake_share')
        self.manilaclient.shares.migration_cancel.assert_called_once_with(
            'fake_share')

    @ddt.data(
        ('name_updated_1', 'description_updated', True),
        ('name_updated_2', 'description_updated', False),
        ('name_updated_3', None, True),
    )
    @ddt.unpack
    def test_share_type_update(
            self, name, description, is_public):
        api.share_type_update(self.request, self.id, name,
                              description, is_public)

        self.manilaclient.share_types.get.return_value.update.\
            assert_called_once_with(name=name,
                                    description=description,
                                    is_public=is_public)

    def test_migration_get_progress(self):
        api.migration_get_progress(self.request, 'fake_share')

        (self.manilaclient.shares.migration_get_progress.
            assert_called_once_with('fake_share'))

    # Share resize tests
    @ddt.data(("123", "78"), ("2", "5"),
              ("75", "21"), ("0", "2"),
              ("18", "62"), ("-1", "3"))
    @ddt.unpack
    def test_share_resize(self, new_size, orig_size):
        api.share_resize(self.request, self.id, new_size, orig_size)
        if orig_size > new_size:
            self.manilaclient.shares.shrink.assert_called_once_with(
                self.id, new_size)
        else:
            self.manilaclient.shares.extend.assert_called_once_with(
                self.id, new_size)

    # Share snapshots tests

    def test_share_revert(self):
        share = 'fake_share'
        snapshot = 'fake_snapshot'

        api.share_revert(self.request, share, snapshot)

        self.manilaclient.shares.revert_to_snapshot.assert_called_once_with(
            share, snapshot)

    def test_share_snapshot_get(self):
        snapshot = 'fake_snapshot'

        api.share_snapshot_get(self.request, snapshot)

        self.manilaclient.share_snapshots.get.assert_called_once_with(snapshot)

    @ddt.data(("", ""), ("share_name", ""),
              ("share_name", "share_description"),
              ("", "share_description"),)
    @ddt.unpack
    def test_share_snapshot_update(self, name, description):
        snapshot = 'fake_snapshot'

        api.share_snapshot_update(self.request, snapshot, name, description)

        self.manilaclient.share_snapshots.update.assert_called_once_with(
            snapshot, display_name=name, display_description=description)

    @ddt.data(
        {},
        {"detailed": True},
        {"detailed": False},
        {"search_opts": {"foo": "bar"}},
        {"sort_key": "id", "sort_dir": "asc"},
    )
    def test_share_snapshot_list(self, kwargs):
        result = api.share_snapshot_list(self.request, **kwargs)

        self.assertEqual(
            self.manilaclient.share_snapshots.list.return_value, result)
        self.manilaclient.share_snapshots.list.assert_called_once_with(
            detailed=kwargs.get("detailed", True),
            search_opts=kwargs.get("search_opts"),
            sort_key=kwargs.get("sort_key"),
            sort_dir=kwargs.get("sort_dir"),
        )

    @ddt.data(True, False)
    def test_snapshot_create(self, force):
        name = 'fake_snapshot_name'
        description = "fake_snapshot_description"

        api.share_snapshot_create(
            self.request, self.id, name, description, force)

        self.manilaclient.share_snapshots.create.assert_called_once_with(
            self.id, name=name, description=description, force=force)

    def test_snapshot_delete(self):
        snapshot_id = 'fake_snapshot_id'

        api.share_snapshot_delete(self.request, snapshot_id)

        self.manilaclient.share_snapshots.delete.assert_called_once_with(
            snapshot_id)

    def test_allow_snapshot(self):
        access_type = "fake_type"
        access_to = "fake_value"

        api.share_snapshot_allow(self.request, self.id, access_type,
                                 access_to)

        client = self.manilaclient
        client.share_snapshots.allow.assert_called_once_with(
            self.id, access_type, access_to)

    def test_deny_snapshot(self):
        api.share_snapshot_deny(self.request, self.id, self.id)

        client = self.manilaclient
        client.share_snapshots.deny.assert_called_once_with(self.id, self.id)

    def test_list_snapshot_rules(self):
        api.share_snapshot_rules_list(self.request, self.id)

        client = self.manilaclient
        client.share_snapshots.access_list.assert_called_once_with(self.id)

    def test_list_snapshot_export_locations(self):
        api.share_snap_export_location_list(self.request, self.id)

        client = self.manilaclient
        client.share_snapshot_export_locations.list.assert_called_once_with(
            snapshot=self.id)

    def test_list_snapshot_instance_export_locations(self):
        api.share_snap_instance_export_location_list(self.request, self.id)

        client = self.manilaclient
        client.share_snapshot_export_locations.list.assert_called_once_with(
            snapshot_instance=self.id)

    # Share network tests

    @ddt.data(
        {},
        {"detailed": True},
        {"detailed": False},
        {"detailed": False, "search_opts": {"foo": "bar"}},
    )
    def test_share_network_list(self, kwargs):
        api.share_network_list(self.request, **kwargs)

        self.manilaclient.share_networks.list.assert_called_once_with(
            detailed=kwargs.get("detailed", False),
            search_opts=kwargs.get("search_opts", None))

    @ddt.data(
        {},
        {"name": "foo_name"},
        {"description": "foo_desc"},
        {"neutron_net_id": "foo_neutron_net_id"},
        {"neutron_subnet_id": "foo_neutron_subnet_id"},
        {"name": "foo_name", "description": "foo_desc",
         "neutron_net_id": "foo_neutron_net_id",
         "neutron_subnet_id": "foo_neutron_subnet_id"},
    )
    def test_share_network_create(self, kwargs):
        expected_kwargs = {
            "name": None,
            "description": None,
            "neutron_net_id": None,
            "neutron_subnet_id": None,
            "availability_zone": None
        }
        expected_kwargs.update(**kwargs)

        api.share_network_create(self.request, **kwargs)

        mock_sn_create = self.manilaclient.share_networks.create
        mock_sn_create.assert_called_once_with(**expected_kwargs)

    def test_share_network_get(self):
        share_net_id = 'fake_share_net_id'

        api.share_network_get(self.request, share_net_id)

        self.manilaclient.share_networks.get.assert_called_once_with(
            share_net_id)

    @ddt.data(("", ""), ("share_net_name", ""),
              ("share_net_name", "share_net_description"),
              ("", "share_net_description"))
    @ddt.unpack
    def test_share_network_update(self, name, description):
        share_net_id = "fake_share_network"

        api.share_network_update(self.request, share_net_id, name, description)

        self.manilaclient.share_networks.update.assert_called_once_with(
            share_net_id, name=name, description=description)

    def test_share_network_delete(self):
        share_network_id = "fake_share_network"

        api.share_network_delete(self.request, share_network_id)

        self.manilaclient.share_networks.delete.assert_called_once_with(
            share_network_id)

    @ddt.data(
        {"share_network_id": "some_network_id"},
        {"share_network_id": "some_network_id",
         "neutron_net_id": "some_neutron_net_id",
         "neutron_subnet_id": "some_neutron_subnet_id",
         "availability_zone": "some_availability_zone"},
    )
    def test_share_network_subnet_create(self, kwargs):
        expected_kwargs = {
            "share_network_id": None,
            "neutron_net_id": None,
            "neutron_subnet_id": None,
            "availability_zone": None
        }

        expected_kwargs.update(**kwargs)
        api.share_network_subnet_create(self.request, **kwargs)
        self.manilaclient.share_network_subnets.create.assert_called_once_with(
            **expected_kwargs)

    # Share server tests

    @ddt.data(
        {},
        {"name": "fake_share_server"},
        {"limit": "10"},
        {"host": "fake_share_server_host"},
        {"sort_key": "id", "sort_dir": "asc"},
    )
    def test_share_server_list(self, kwargs):
        result = api.share_server_list(self.request, search_opts=kwargs)

        self.assertEqual(
            self.manilaclient.share_servers.list.return_value, result)

        self.manilaclient.share_servers.list.assert_called_once_with(
            search_opts=kwargs)

    def test_share_server_get(self):
        share_serv_id = 'fake_share_server'
        api.share_server_get(self.request, share_serv_id)

        self.manilaclient.share_servers.get.assert_called_once_with(
            share_serv_id)

    def test_share_server_delete(self):
        share_serv_id = "fake_share_server"

        api.share_server_delete(self.request, share_serv_id)

        self.manilaclient.share_servers.delete.assert_called_once_with(
            share_serv_id)

    # Security service tests

    @ddt.data(
        {},
        {"search_opts": {"foo": "bar"}},
    )
    def test_security_service_list(self, kwargs):
        api.security_service_list(self.request, **kwargs)

        self.manilaclient.security_services.list.assert_called_once_with(
            detailed=True,
            search_opts=kwargs.get("search_opts", None))

    def test_security_service_get(self):
        sec_service_id = 'fake_sec_service_id'
        api.security_service_get(self.request, sec_service_id)

        self.manilaclient.security_services.get.assert_called_once_with(
            sec_service_id)

    @ddt.data(
        ("ldap", {}),
        ("kerberos", {}),
        ("ldap",
            {"dns_ip": "8.8.8.8", "ou": "fakeOU",
             "name": "my_fake_ldap_security_service",
             "description": "LDAP security service"}),
        ("kerberos",
            {"server": "10.254.0.3",
             "user": "demo", "password": "s3cr37",
             "name": "my_fake_kerberos_security_service",
             "description": "Kerberos security service"})
    )
    @ddt.unpack
    def test_security_service_create(self, ss_type, kwargs):
        expected_kwargs = {
            "dns_ip": None,
            "ou": None,
            "server": None,
            "domain": None,
            "password": None,
            "user": None,
            "name": None,
            "description": None
        }
        expected_kwargs.update(**kwargs)

        api.security_service_create(self.request, ss_type, **kwargs)

        mock_sec_service_create = self.manilaclient.security_services.create
        mock_sec_service_create.assert_called_once_with(
            ss_type, **expected_kwargs)

    @ddt.data(
        {"dns_ip": "8.8.4.4", "ou": "testOU",
         "server": "10.254.0.3", "domain": "None",
         "password": "wr67p6", "user": "demo",
         "name": "my_fake_ldap_security_service_2",
         "description": "LDAP security service 2"},
        {"dns_ip": "None", "ou": "None",
         "server": "10.254.0.10", "domain": "None",
         "password": "None", "user": "demo",
         "name": "my_fake_kerberos_security_service_2",
         "description": "Kerberos security service 2"}
    )
    def test_security_service_update(self, kwargs):
        sec_service_id = "fake_sec_service_id"

        api.security_service_update(self.request, sec_service_id, **kwargs)

        mock_sec_service_update = self.manilaclient.security_services.update
        mock_sec_service_update.assert_called_once_with(
            sec_service_id, **kwargs)

    def test_security_service_delete(self):
        sec_service_id = "fake_sec_service_id"

        api.security_service_delete(self.request, sec_service_id)

        self.manilaclient.security_services.delete.assert_called_once_with(
            sec_service_id)

    # Share network security service tests

    def test_share_network_security_service_add(self):
        share_network_id = "fake_share_net_id"
        sec_service_id = "fake_sec_service_id"

        api.share_network_security_service_add(
            self.request, share_network_id, sec_service_id)

        mock_sn_sec_service_add = (
            self.manilaclient.share_networks.add_security_service)

        mock_sn_sec_service_add.assert_called_once_with(
            share_network_id, sec_service_id)

    def test_share_network_security_service_remove(self):
        share_network_id = "fake_share_net_id"
        sec_service_id = "fake_sec_service_id"

        api.share_network_security_service_remove(
            self.request, share_network_id, sec_service_id)

        mock_sn_sec_service_rm = (
            self.manilaclient.share_networks.remove_security_service)

        mock_sn_sec_service_rm.assert_called_once_with(
            share_network_id, sec_service_id)

    def test_share_network_security_service_list(self):
        share_network_id = "fake_share_net_id"

        api.share_network_security_service_list(
            self.request, share_network_id)

        search_opts = {"share_network_id": share_network_id}

        self.manilaclient.security_services.list.assert_called_once_with(
            search_opts=search_opts)

    # Share metadata tests

    def test_share_set_metadata(self):
        fake_metadata = {
            "aim": "testing",
            "project": "my_abc",
            "deadline": "01/01/2020"
        }

        api.share_set_metadata(
            self.request, self.id, fake_metadata)

        self.manilaclient.shares.set_metadata.assert_called_once_with(
            self.id, fake_metadata)

    def test_share_delete_metadata(self):
        fake_keys = ["aim", "project", "deadline"]

        api.share_delete_metadata(
            self.request, self.id, fake_keys)

        self.manilaclient.shares.delete_metadata.assert_called_once_with(
            self.id, fake_keys)

    # Default quota tests

    def test_default_quota_get(self):
        project_id = 'fake_project_id'

        api.tenant_quota_get(self.request, project_id)

        self.manilaclient.quotas.get.assert_called_once_with(project_id)

    @ddt.data(
        ({'share_gigabytes': 333}, {'gigabytes': 333}),
        ({'share_snapshot_gigabytes': 444}, {'snapshot_gigabytes': 444}),
        ({'share_snapshots': 14}, {'snapshots': 14}),
        ({'snapshots': 14}, {'snapshots': 14}),
        ({'gigabytes': 14}, {'gigabytes': 14}),
        ({'snapshot_gigabytes': 314}, {'snapshot_gigabytes': 314}),
        ({'shares': 24}, {'shares': 24}),
        ({'share_networks': 14}, {'share_networks': 14}),
    )
    @ddt.unpack
    def test_tenant_quota_update(self, provided_kwargs, expected_kwargs):
        tenant_id = 'fake_tenant_id'

        api.tenant_quota_update(self.request, tenant_id, **provided_kwargs)

        self.manilaclient.quotas.update.assert_called_once_with(
            tenant_id, **expected_kwargs)
        self.manilaclient.quota_classes.update.assert_not_called()

    @ddt.data(
        ({'share_gigabytes': 333}, {'gigabytes': 333}),
        ({'share_snapshot_gigabytes': 444}, {'snapshot_gigabytes': 444}),
        ({'share_snapshots': 14}, {'snapshots': 14}),
        ({'snapshots': 14}, {'snapshots': 14}),
        ({'gigabytes': 14}, {'gigabytes': 14}),
        ({'snapshot_gigabytes': 314}, {'snapshot_gigabytes': 314}),
        ({'shares': 24}, {'shares': 24}),
        ({'share_networks': 14}, {'share_networks': 14}),
    )
    @ddt.unpack
    def test_default_quota_update(self, provided_kwargs, expected_kwargs):
        api.default_quota_update(self.request, **provided_kwargs)

        self.manilaclient.quota_classes.update.assert_called_once_with(
            api.DEFAULT_QUOTA_NAME, **expected_kwargs)

    def test_tenant_quota_get(self):
        tenant_id = 'fake_tenant_id'
        result = api.tenant_quota_get(self.request, tenant_id)

        self.assertIsNotNone(result)
        self.manilaclient.quotas.get.assert_called_once_with(tenant_id)

    @ddt.data({
        'shares': 24, 'gigabytes': 333, 'snapshots': 14,
        'snapshot_gigabytes': 444, 'share_networks': 14,
        "share_groups": 30, "share_group_snapshots": 5,
    })
    @ddt.unpack
    def test_ui_data_map(self, **kwargs):
        expected_result = {
            'shares': 24, 'share_gigabytes': 333, 'share_snapshots': 14,
            'share_snapshot_gigabytes': 444, 'share_networks': 14,
            "share_groups": 30, "share_group_snapshots": 5,
        }

        converted_result_for_ui = {}
        for field in api.MANILA_QUOTA_FIELDS:
            converted_result_for_ui[field] = (
                kwargs[api.MANILA_QUOTA_FIELDS_DATA_MAP[field]])

        self.assertEqual(expected_result, converted_result_for_ui)

    # Share type tests

    def test_share_type_list(self):
        api.share_type_list(self.request)

        self.manilaclient.share_types.list.assert_called_once_with()

    def test_share_type_get(self):
        share_type_id = "fake_share_type_id"

        api.share_type_get(self.request, share_type_id)

        self.manilaclient.share_types.get.assert_called_once_with(
            share_type_id)

    @ddt.data(True, False)
    def test_share_type_create_with_default_values(self, dhss):
        name = 'fake_share_type_name'

        api.share_type_create(self.request, name, dhss)

        self.manilaclient.share_types.create.assert_called_once_with(
            name=name,
            spec_driver_handles_share_servers=dhss,
            description=None,
            is_public=True)

    @ddt.data(
        (True, "fake_description", True),
        (False, "fake_description", True),
        (True, "fake_description", False),
        (False, "fake_description", False),
    )
    @ddt.unpack
    def test_share_type_create_with_custom_values(
            self, dhss, description, is_public):
        name = 'fake_share_type_name'

        api.share_type_create(
            self.request, name, dhss, description,
            is_public)

        self.manilaclient.share_types.create.assert_called_once_with(
            name=name,
            description=description,
            spec_driver_handles_share_servers=dhss,
            is_public=is_public)

    def test_share_type_delete(self):
        share_type_id = "fake_share_type_id"

        api.share_type_delete(self.request, share_type_id)

        self.manilaclient.share_types.delete.assert_called_once_with(
            share_type_id)

    def test_share_type_get_extra_specs(self):
        share_type_id = "fake_share_type_id"

        api.share_type_get_extra_specs(self.request, share_type_id)

        share_types_get = self.manilaclient.share_types.get
        share_types_get.assert_called_once_with(share_type_id)
        share_types_get.return_value.get_keys.assert_called_once()

    def test_share_type_set_extra_specs(self):
        data = {"foo": "bar"}

        api.share_type_set_extra_specs(self.request, self.id, data)

        share_types_get = self.manilaclient.share_types.get
        share_types_get.assert_called_once_with(self.id)
        share_types_get.return_value.set_keys.assert_called_once_with(data)

    def test_share_type_unset_extra_specs(self):
        keys = ["foo", "bar"]

        api.share_type_unset_extra_specs(self.request, self.id, keys)

        share_types_get = self.manilaclient.share_types.get
        share_types_get.assert_called_once_with(self.id)
        share_types_get.return_value.unset_keys.assert_called_once_with(keys)

    def test_share_type_access_list(self):
        share_type_id = "fake_share_type_id"

        api.share_type_access_list(self.request, share_type_id)

        self.manilaclient.share_type_access.list.assert_called_once_with(
            share_type_id)

    def test_share_type_access_add(self):
        share_type_id = "fake_share_type_id"
        project_id = "fake_project_id"

        api.share_type_access_add(self.request, share_type_id, project_id)

        mock_share_type_access_add = (
            self.manilaclient.share_type_access.add_project_access)

        mock_share_type_access_add.assert_called_once_with(
            share_type_id, project_id)

    def test_share_type_access_remove(self):
        share_type_id = "fake_share_type_id"
        project_id = "fake_project_id"

        api.share_type_access_remove(self.request, share_type_id, project_id)

        mock_share_type_access_rm = (
            self.manilaclient.share_type_access.remove_project_access)

        mock_share_type_access_rm.assert_called_once_with(
            share_type_id, project_id)

    # Share replica tests

    def test_share_replica_list(self):
        api.share_replica_list(self.request)

        self.manilaclient.share_replicas.list.assert_called_once_with(None)

    def test_share_replica_list_with_filter_by_share(self):
        api.share_replica_list(self.request, share="FOO")

        self.manilaclient.share_replicas.list.assert_called_once_with("FOO")

    def test_share_replica_create(self):
        share = "FOO_share"
        availability_zone = "BAR_availability_zone"

        api.share_replica_create(
            self.request, share, availability_zone)

        self.manilaclient.share_replicas.create.assert_called_once_with(
            share,
            availability_zone=availability_zone
        )

    def test_share_replica_get(self):
        api.share_replica_get(self.request, "fake")

        self.manilaclient.share_replicas.get.assert_called_once_with("fake")

    def test_share_replica_delete(self):
        api.share_replica_delete(self.request, "fake")

        self.manilaclient.share_replicas.delete.assert_called_once_with("fake")

    def test_share_replica_promote(self):
        api.share_replica_promote(self.request, "fake")

        self.manilaclient.share_replicas.promote.assert_called_once_with(
            "fake")

    def test_share_replica_resync(self):
        api.share_replica_resync(self.request, "fake")

        self.manilaclient.share_replicas.resync.assert_called_once_with("fake")

    def test_share_replica_reset_status(self):
        replica = "fake_replica"
        status = "fake_status"

        api.share_replica_reset_status(self.request, replica, status)

        self.manilaclient.share_replicas.reset_state.assert_called_once_with(
            replica, status)

    def test_share_replica_reset_state(self):
        replica = "fake_replica"
        state = "fake_state"

        api.share_replica_reset_state(self.request, replica, state)

        mock_reset_state = self.manilaclient.share_replicas.reset_replica_state
        mock_reset_state.assert_called_once_with(replica, state)

    # Share instance tests

    def test_share_instance_list(self):
        api.share_instance_list(self.request)

        self.manilaclient.share_instances.list.assert_called_once_with()

    def test_share_instance_get(self):
        api.share_instance_get(self.request, self.id)

        self.manilaclient.share_instances.get.assert_called_once_with(self.id)

    # Availability zone and pool tests

    def test_availability_zone_list(self):
        api.availability_zone_list(self.request)

        self.manilaclient.availability_zones.list.assert_called_once_with()

    @ddt.data({}, {"detailed": True}, {"detailed": False})
    def test_pool_list(self, kwargs):
        api.pool_list(self.request, **kwargs)

        self.manilaclient.pools.list.assert_called_once_with(
            detailed=kwargs.get("detailed", False))

    # Share groups tests

    def test_share_group_create(self):
        name = "fake_sg_name"
        kwargs = {
            "description": "fake_desc",
            "share_group_type": "fake_sg_type",
            "share_types": ["fake", "list", "of", "fake", "share", "types"],
            "share_network": "fake_sn",
            "source_share_group_snapshot": "fake_source_share_group_snapshot",
            "availability_zone": "fake_az",
        }

        result = api.share_group_create(self.request, name, **kwargs)

        self.assertEqual(
            self.manilaclient.share_groups.create.return_value, result)
        self.manilaclient.share_groups.create.assert_called_once_with(
            name=name, **kwargs)

    def test_share_group_get(self):
        sg = "fake_share_group"

        result = api.share_group_get(self.request, sg)

        self.assertEqual(
            self.manilaclient.share_groups.get.return_value, result)
        self.manilaclient.share_groups.get.assert_called_once_with(sg)

    def test_share_group_update(self):
        sg = "fake_share_group"
        name = "fake_name"
        desc = "fake_desc"

        result = api.share_group_update(self.request, sg, name, desc)

        self.assertEqual(
            self.manilaclient.share_groups.update.return_value, result)
        self.manilaclient.share_groups.update.assert_called_once_with(
            sg, name=name, description=desc)

    @ddt.data({}, {"force": True}, {"force": False})
    def test_share_group_delete(self, kwargs):
        sg = 'fake_share_group'

        api.share_group_delete(self.request, sg, **kwargs)

        self.manilaclient.share_groups.delete.assert_called_once_with(
            sg, force=kwargs.get("force", False))

    def test_share_group_reset_state(self):
        sg = 'fake_share_group'
        state = 'fake_state'

        result = api.share_group_reset_state(self.request, sg, state)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_groups.reset_state.return_value,
            result)
        self.manilaclient.share_groups.reset_state.assert_called_once_with(
            sg, state)

    @ddt.data(
        {},
        {"detailed": True},
        {"detailed": False},
        {"search_opts": {"foo": "bar"}},
        {"sort_key": "id", "sort_dir": "asc"},
    )
    def test_share_group_list(self, kwargs):
        result = api.share_group_list(self.request, **kwargs)

        self.assertEqual(
            self.manilaclient.share_groups.list.return_value, result)
        self.manilaclient.share_groups.list.assert_called_once_with(
            detailed=kwargs.get("detailed", True),
            search_opts=kwargs.get("search_opts"),
            sort_key=kwargs.get("sort_key"),
            sort_dir=kwargs.get("sort_dir"),
        )

    # Share Group Snapshots tests

    def test_share_group_snapshot_create(self):
        sg = 'fake_share_group'
        name = 'fake_name'
        desc = 'fake_description'

        result = api.share_group_snapshot_create(self.request, sg, name, desc)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_snapshots.create.return_value,
            result)
        self.manilaclient.share_group_snapshots.create.assert_called_once_with(
            share_group=sg, name=name, description=desc)

    def test_share_group_snapshot_get(self):
        sgs = 'fake_share_group_snapshot'

        result = api.share_group_snapshot_get(self.request, sgs)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_snapshots.get.return_value, result)
        self.manilaclient.share_group_snapshots.get.assert_called_once_with(
            sgs)

    def test_share_group_snapshot_update(self):
        sgs = 'fake_share_group_snapshot'
        name = 'fake_name'
        desc = 'fake_description'

        result = api.share_group_snapshot_update(self.request, sgs, name, desc)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_snapshots.update.return_value,
            result)
        self.manilaclient.share_group_snapshots.update.assert_called_once_with(
            sgs, name=name, description=desc)

    @ddt.data(True, False)
    def test_share_group_snapshot_delete(self, force):
        sgs = 'fake_share_group_snapshot'

        result = api.share_group_snapshot_delete(self.request, sgs, force)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_snapshots.delete.return_value,
            result)
        self.manilaclient.share_group_snapshots.delete.assert_called_once_with(
            sgs, force=force)

    def test_share_group_snapshot_reset_state(self):
        sgs = 'fake_share_group_snapshot'
        state = 'fake_state'

        result = api.share_group_snapshot_reset_state(self.request, sgs, state)

        rs_method = self.manilaclient.share_group_snapshots.reset_state
        self.assertIsNotNone(result)
        self.assertEqual(rs_method.return_value, result)
        rs_method.assert_called_once_with(sgs, state)

    @ddt.data(
        {},
        {'detailed': False},
        {'detailed': True, 'search_opts': 'foo',
         'sort_key': 'k', 'sort_dir': 'v'},
    )
    def test_share_group_snapshot_list(self, kwargs):
        result = api.share_group_snapshot_list(self.request, **kwargs)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_snapshots.list.return_value,
            result)
        self.manilaclient.share_group_snapshots.list.assert_called_once_with(
            detailed=kwargs.get('detailed', True),
            search_opts=kwargs.get('search_opts'),
            sort_key=kwargs.get('sort_key'),
            sort_dir=kwargs.get('sort_dir'))

    # Share Group Types tests

    @ddt.data(
        {'is_public': True},
        {'is_public': False, 'group_specs': {'foo': 'bar'}},
        {'group_specs': {}},
    )
    def test_share_group_type_create(self, kwargs):
        name = 'fake_sgt_name'
        sts = ['fake', 'list', 'of', 'share', 'types']

        result = api.share_group_type_create(self.request, name, sts, **kwargs)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_types.create.return_value,
            result)
        self.manilaclient.share_group_types.create.assert_called_once_with(
            name=name, share_types=sts,
            is_public=kwargs.get('is_public', False),
            group_specs=kwargs.get('group_specs'))

    def test_share_group_type_get(self):
        sgt = "fake_sgt"

        result = api.share_group_type_get(self.request, sgt)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_types.get.return_value, result)
        self.manilaclient.share_group_types.get.assert_called_once_with(sgt)

    @ddt.data(True, False)
    def test_share_group_type_list(self, show_all):
        result = api.share_group_type_list(self.request, show_all)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_types.list.return_value, result)
        self.manilaclient.share_group_types.list.assert_called_once_with(
            show_all=show_all)

    def test_share_group_type_delete(self):
        sgt = 'fake_share_group_type'

        result = api.share_group_type_delete(self.request, sgt)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_types.delete.return_value, result)
        self.manilaclient.share_group_types.delete.assert_called_once_with(sgt)

    def test_share_group_type_access_list(self):
        sgt = 'fake_share_group_type'

        result = api.share_group_type_access_list(self.request, sgt)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.share_group_type_access.list.return_value,
            result)
        self.manilaclient.share_group_type_access.list.assert_called_once_with(
            sgt)

    def test_share_group_type_access_add(self):
        sgt = 'fake_share_group_type'
        project = 'fake_project'

        result = api.share_group_type_access_add(self.request, sgt, project)

        sgt_access = self.manilaclient.share_group_type_access
        self.assertIsNotNone(result)
        self.assertEqual(
            sgt_access.add_project_access.return_value, result)
        sgt_access.add_project_access.assert_called_once_with(sgt, project)

    def test_share_group_type_access_remove(self):
        sgt = 'fake_share_group_type'
        project = 'fake_project'

        result = api.share_group_type_access_remove(self.request, sgt, project)

        sgt_access = self.manilaclient.share_group_type_access
        self.assertIsNotNone(result)
        self.assertEqual(
            sgt_access.remove_project_access.return_value, result)
        sgt_access.remove_project_access.assert_called_once_with(sgt, project)

    def test_share_group_type_set_specs(self):
        sgt = 'fake_share_group_type'
        group_specs = 'fake_specs'

        result = api.share_group_type_set_specs(self.request, sgt, group_specs)

        get_method = self.manilaclient.share_group_types.get
        self.assertIsNotNone(result)
        self.assertEqual(get_method.return_value.set_keys.return_value, result)
        get_method.assert_called_once_with(sgt)
        get_method.return_value.set_keys.assert_called_once_with(group_specs)

    def test_share_group_type_unset_specs(self):
        sgt = 'fake_share_group_type'
        keys = ['fake', 'list', 'of', 'keys', 'for', 'deletion']

        result = api.share_group_type_unset_specs(self.request, sgt, keys)

        get_method = self.manilaclient.share_group_types.get
        self.assertIsNotNone(result)
        self.assertEqual(
            get_method.return_value.unset_keys.return_value, result)
        get_method.assert_called_once_with(sgt)
        get_method.return_value.unset_keys.assert_called_once_with(keys)

    def test_share_group_type_get_specs(self):
        sgt = 'fake_share_group_type'

        result = api.share_group_type_get_specs(self.request, sgt)

        get_method = self.manilaclient.share_group_types.get
        self.assertIsNotNone(result)
        self.assertEqual(
            get_method.return_value.get_keys.return_value, result)
        get_method.assert_called_once_with(sgt)
        get_method.return_value.get_keys.assert_called_once_with()

    @ddt.data(None, "some_fake_message_id")
    def test_share_messages_get(self, message_id):
        result = api.messages_get(self.request, message_id)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.messages.get.return_value,
            result)
        self.manilaclient.messages.get.assert_called_once_with(message_id)

    @ddt.data(
        {},
        {'search_opts': 'foo', 'sort_key': 'k', 'sort_dir': 'v'},
    )
    def test_messages_list(self, kwargs):
        result = api.messages_list(self.request, **kwargs)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.messages.list.return_value,
            result)
        self.manilaclient.messages.list.assert_called_once_with(
            search_opts=kwargs.get('search_opts'),
            sort_key=kwargs.get('sort_key'),
            sort_dir=kwargs.get('sort_dir'))

    @ddt.data(None, "some_fake_message_id")
    def test_messages_delete(self, message_id):
        result = api.messages_delete(self.request, message_id)

        self.assertIsNotNone(result)
        self.assertEqual(
            self.manilaclient.messages.delete.return_value,
            result)
        self.manilaclient.messages.delete.assert_called_once_with(message_id)
