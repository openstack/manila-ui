# Copyright (c) 2014 NetApp, Inc.
# Copyright (c) 2015 Mirantis, Inc.
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

"""
This module contains test suites that cover tabs from admin dashboard
by getting generated pages and verifying results.
"""

import ddt
from django.core.urlresolvers import reverse
from manilaclient import exceptions as manila_client_exc
import mock
from neutronclient.client import exceptions

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.admin.shares import utils
from manila_ui.tests.dashboards.project.shares import test_data
from manila_ui.tests import helpers as test
from manila_ui.tests.test_data import keystone_data

from openstack_dashboard.api import keystone as api_keystone
from openstack_dashboard.api import neutron as api_neutron
from openstack_dashboard.usage import quotas

INDEX_URL = reverse('horizon:admin:shares:index')


@ddt.ddt
class SharesTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.mock_object(utils.timeutils, 'now', mock.Mock(return_value=1))
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(keystone_data.projects, None)))
        # Reset taken list of projects to avoid test interference
        utils.PROJECTS = {}

    @ddt.data(True, False)
    def test_index_with_all_tabs(self, single_time_slot):
        snaps = [test_data.snapshot]
        shares = [test_data.share, test_data.nameless_share,
                  test_data.other_share]
        share_networks = [test_data.inactive_share_network,
                          test_data.active_share_network]
        security_services = [test_data.sec_service]
        if single_time_slot:
            utils.timeutils.now.side_effect = [4] + [5 + i for i in range(4)]
        else:
            utils.timeutils.now.side_effect = [4] + [24 + i for i in range(4)]

        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=shares))
        self.mock_object(
            api_manila, "share_snapshot_list", mock.Mock(return_value=snaps))
        self.mock_object(
            api_manila, "share_network_list",
            mock.Mock(return_value=share_networks))
        self.mock_object(
            api_manila, "share_type_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "share_server_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "security_service_list",
            mock.Mock(return_value=security_services))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        self.mock_object(
            api_neutron, "network_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_neutron, "subnet_list", mock.Mock(return_value=[]))
        self.mock_object(
            quotas, "tenant_limit_usages",
            mock.Mock(return_value=test_data.quota_usage))
        self.mock_object(
            quotas, "tenant_quota_usages",
            mock.Mock(return_value=test_data.quota_usage))

        res = self.client.get(INDEX_URL)

        if single_time_slot:
            api_keystone.tenant_list.assert_called_once_with(mock.ANY)
        else:
            api_keystone.tenant_list.assert_has_calls(
                [mock.call(mock.ANY)] * 2)
        api_neutron.network_list.assert_called_once_with(mock.ANY)
        api_neutron.subnet_list.assert_called_once_with(mock.ANY)
        api_manila.share_type_list.assert_called_once_with(mock.ANY)
        api_manila.share_server_list.assert_called_once_with(mock.ANY)
        api_manila.share_network_list.assert_called_once_with(
            mock.ANY, detailed=True, search_opts={'all_tenants': True})
        api_manila.security_service_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        api_manila.share_snapshot_list.assert_called_with(
            mock.ANY, search_opts={'all_tenants': True})
        api_manila.share_list.assert_called_with(mock.ANY)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'admin/shares/index.html')

    def test_delete_share(self):
        url = reverse('horizon:admin:shares:index')
        share = test_data.share
        formData = {'action': 'shares__delete__%s' % share.id}
        self.mock_object(
            api_manila, "share_snapshot_list", mock.Mock(return_value=[]))
        self.mock_object(api_manila, "share_delete")
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=[share]))

        res = self.client.post(url, formData)

        api_keystone.tenant_list.assert_called_once_with(mock.ANY)
        api_manila.share_delete.assert_called_once_with(mock.ANY, share.id)
        api_manila.share_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        api_manila.share_snapshot_list.assert_called_once_with(
            mock.ANY, detailed=True, search_opts={'all_tenants': True})
        self.assertRedirectsNoFollow(res, INDEX_URL)


class ShareInstanceTests(test.BaseAdminViewTests):

    def test_list_share_instances(self):
        share_instances = [
            test_data.share_instance,
            test_data.share_instance_no_ss,
        ]
        url = reverse('horizon:admin:shares:share_instances_tab')
        self.mock_object(
            api_manila, "share_instance_list",
            mock.Mock(return_value=share_instances))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        self.mock_object(
            api_keystone, "tenant_list", mock.Mock(return_value=([], None)))

        res = self.client.get(url)

        self.assertContains(res, "<h1>Shares</h1>")
        self.assertContains(
            res,
            '<a href="/admin/shares/share_servers/%s" >%s</a>' % (
                share_instances[0].share_server_id,
                share_instances[0].share_server_id),
            1, 200)
        self.assertContains(
            res,
            '<a href="/admin/shares/share_networks/%s" >%s</a>' % (
                share_instances[0].share_network_id,
                share_instances[0].share_network_id),
            1, 200)
        for si in share_instances:
            self.assertContains(
                res, '<a href="/admin/shares/share_instances/%s" >%s</a>' % (
                    si.id, si.id))
            self.assertContains(res, si.host)
            self.assertContains(res, si.availability_zone)
            self.assertContains(
                res,
                '<a href="/project/shares/%s/" >%s</a>' % (
                    si.share_id, si.share_id),
                1, 200)
        api_manila.share_instance_list.assert_called_once_with(mock.ANY)
        self.assertEqual(5, api_keystone.tenant_list.call_count)
        self.assertEqual(3, api_neutron.is_service_enabled.call_count)

    def test_detail_view_share_instance(self):
        share_instance = test_data.share_instance
        share_id = share_instance.share_id
        ss_id = share_instance.share_server_id
        url = reverse('horizon:admin:shares:share_instance_detail',
                      args=[share_instance.id])
        self.mock_object(
            api_manila, "share_instance_get",
            mock.Mock(return_value=share_instance))
        self.mock_object(
            api_manila, "share_instance_export_location_list",
            mock.Mock(return_value=test_data.export_locations))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertContains(
            res, "<h1>Share Instance Details: %s</h1>" % share_instance.id,
            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_instance.id, 1, 200)
        self.assertContains(res, "<dd>Available</dd>", 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_instance.host, 1, 200)
        self.assertContains(
            res, "<dd>%s</dd>" % share_instance.availability_zone, 1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/project/shares/%s/\">%s</a></dd>" % (
                share_id, share_id),
            1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/project/shares/share_networks/%s\">%s</a></dd>" % (
                share_instance.share_network_id,
                share_instance.share_network_id),
            1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/shares/share_servers/%s\">%s</a></dd>" % (
                ss_id, ss_id),
            1, 200)
        self.assertNoMessages()
        api_manila.share_instance_get.assert_called_once_with(
            mock.ANY, share_instance.id)
        api_manila.share_instance_export_location_list.assert_called_once_with(
            mock.ANY, share_instance.id)
        self.assertEqual(3, api_neutron.is_service_enabled.call_count)

    def test_detail_view_share_instance_with_exception(self):
        share_instance = test_data.share_instance
        url = reverse('horizon:admin:shares:share_instance_detail',
                      args=[share_instance.id])
        self.mock_object(
            api_manila, "share_instance_get",
            mock.Mock(side_effect=manila_client_exc.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_instance_get.assert_called_once_with(
            mock.ANY, share_instance.id)


class ShareServerTests(test.BaseAdminViewTests):

    def test_list_share_servers(self):
        share_servers = [
            test_data.share_server,
            test_data.share_server_errored,
        ]
        projects = [
            type('FakeProject', (object, ),
                 {'id': s.project_id, 'name': '%s_name' % s.project_id})
            for s in share_servers
        ]
        projects_dict = {p.id: p for p in projects}
        url = reverse('horizon:admin:shares:share_servers_tab')
        self.mock_object(
            api_manila, "share_server_list",
            mock.Mock(return_value=share_servers))
        self.mock_object(
            api_manila, "share_list",
            mock.Mock(side_effect=[
                [], [test_data.share], [test_data.nameless_share]]))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(projects, None)))

        res = self.client.get(url)

        self.assertContains(res, "<h1>Shares</h1>")
        for share_server in share_servers:
            self.assertContains(
                res,
                '<a href="/admin/shares/share_servers/%s" >%s</a>' % (
                    share_server.id, share_server.id),
                1, 200)
            self.assertContains(res, share_server.host, 1, 200)
            self.assertContains(
                res, projects_dict[share_server.project_id].name, 1, 200)
            self.assertContains(
                res,
                '<a href="/admin/shares/share_networks/%s" >%s</a>' % (
                    share_server.share_network_id,
                    share_server.share_network),
                1, 200)
        api_manila.share_list.assert_has_calls([
            mock.call(
                mock.ANY, search_opts={'share_server_id': share_server.id})
            for share_server in share_servers
        ])
        api_manila.share_server_list.assert_called_once_with(mock.ANY)
        self.assertEqual(1, api_keystone.tenant_list.call_count)
        self.assertEqual(3, api_neutron.is_service_enabled.call_count)

    def test_detail_view_share_server(self):
        share_server = test_data.share_server
        shares = [test_data.share, test_data.nameless_share]
        url = reverse(
            'horizon:admin:shares:share_server_detail', args=[share_server.id])
        self.mock_object(
            api_manila, "share_server_get",
            mock.Mock(return_value=share_server))
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=shares))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertContains(
            res, "<h1>Share Server Details: %s</h1>" % share_server.id,
            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_server.id, 1, 200)
        self.assertContains(res, "<dd>Active</dd>", 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_server.host, 1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/shares/share_networks/%s\">%s</a></dd>" % (
                share_server.share_network_id,
                share_server.share_network_name),
            1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" % (
                shares[0].id, shares[0].name),
            1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" % (
                shares[1].id, shares[1].id),
            1, 200)
        for k, v in share_server.backend_details.items():
            self.assertContains(res, "<dt>%s</dt>" % k)
            self.assertContains(res, "<dd>%s</dd>" % v)
        self.assertNoMessages()
        api_manila.share_server_get.assert_called_once_with(
            mock.ANY, share_server.id)
        api_manila.share_list.assert_called_once_with(
            mock.ANY, search_opts={"share_server_id": share_server.id})
        self.assertEqual(3, api_neutron.is_service_enabled.call_count)

    def test_detail_view_share_server_with_exception(self):
        share_server = test_data.share_server
        url = reverse('horizon:admin:shares:share_server_detail',
                      args=[share_server.id])
        self.mock_object(
            api_manila, "share_server_get",
            mock.Mock(side_effect=manila_client_exc.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_server_get.assert_called_once_with(
            mock.ANY, share_server.id)


class SecurityServicesTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(keystone_data.projects, None)))
        # Reset taken list of projects to avoid test interference
        utils.PROJECTS = {}

    def test_detail_view(self):
        sec_service = test_data.sec_service
        self.mock_object(
            api_manila, "security_service_get",
            mock.Mock(return_value=sec_service))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        url = reverse('horizon:admin:shares:security_service_detail',
                      args=[sec_service.id])

        res = self.client.get(url)

        self.assertContains(res, "<h1>Security Service Details: %s</h1>"
                                 % sec_service.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % sec_service.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % sec_service.id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % sec_service.user, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % sec_service.server, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % sec_service.dns_ip, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % sec_service.domain, 1, 200)
        self.assertNoMessages()
        api_manila.security_service_get.assert_called_once_with(
            mock.ANY, sec_service.id)
        self.assertEqual(3, api_neutron.is_service_enabled.call_count)

    def test_detail_view_with_exception(self):
        url = reverse('horizon:admin:shares:security_service_detail',
                      args=[test_data.sec_service.id])
        self.mock_object(
            api_manila, "security_service_get",
            mock.Mock(side_effect=manila_client_exc.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.security_service_get.assert_called_once_with(
            mock.ANY, test_data.sec_service.id)

    def test_delete_security_service(self):
        security_service = test_data.sec_service
        formData = {
            'action': 'security_services__delete__%s' % security_service.id,
        }
        self.mock_object(api_manila, "security_service_delete")
        self.mock_object(
            api_manila, "security_service_list",
            mock.Mock(return_value=[test_data.sec_service]))
        url = reverse('horizon:admin:shares:index')

        res = self.client.post(url, formData)

        api_keystone.tenant_list.assert_called_once_with(mock.ANY)
        api_manila.security_service_delete.assert_called_once_with(
            mock.ANY, test_data.sec_service.id)
        api_manila.security_service_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        self.assertRedirectsNoFollow(res, INDEX_URL)


class ShareNetworksTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(keystone_data.projects, None)))
        # Reset taken list of projects to avoid test interference
        utils.PROJECTS = {}

    def test_detail_view(self):
        share_net = test_data.active_share_network
        sec_service = test_data.sec_service
        self.mock_object(
            api_manila, "share_server_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "share_network_get", mock.Mock(return_value=share_net))
        self.mock_object(
            api_manila, "share_network_security_service_list",
            mock.Mock(return_value=[sec_service]))
        network = self.networks.first()
        subnet = self.subnets.first()
        self.mock_object(
            api_neutron, "network_get", mock.Mock(return_value=network))
        self.mock_object(
            api_neutron, "subnet_get", mock.Mock(return_value=subnet))
        url = reverse('horizon:project:shares:share_network_detail',
                      args=[share_net.id])
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertContains(res, "<h1>Share Network Details: %s</h1>"
                                 % share_net.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_net.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_net.id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % network.name_or_id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % subnet.name_or_id, 1, 200)
        self.assertContains(res, "<a href=\"/project/shares/security_services"
                                 "/%s\">%s</a>" % (sec_service.id,
                                                   sec_service.name), 1, 200)
        self.assertNoMessages()
        api_manila.share_network_security_service_list.assert_called_once_with(
            mock.ANY, share_net.id)
        api_manila.share_server_list.assert_called_once_with(
            mock.ANY, search_opts={'share_network_id': share_net.id})
        api_manila.share_network_get.assert_called_once_with(
            mock.ANY, share_net.id)
        api_neutron.network_get.assert_called_once_with(
            mock.ANY, share_net.neutron_net_id)
        api_neutron.subnet_get.assert_called_once_with(
            mock.ANY, share_net.neutron_subnet_id)
        self.assertEqual(3, api_neutron.is_service_enabled.call_count)

    def test_detail_view_network_not_found(self):
        share_net = test_data.active_share_network
        sec_service = test_data.sec_service
        url = reverse('horizon:project:shares:share_network_detail',
                      args=[share_net.id])
        self.mock_object(
            api_manila, "share_server_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "share_network_get", mock.Mock(return_value=share_net))
        self.mock_object(
            api_manila, "share_network_security_service_list",
            mock.Mock(return_value=[sec_service]))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        self.mock_object(
            api_neutron, "network_get", mock.Mock(
                side_effect=exceptions.NeutronClientException('fake', 500)))
        self.mock_object(
            api_neutron, "subnet_get", mock.Mock(
                side_effect=exceptions.NeutronClientException('fake', 500)))

        res = self.client.get(url)

        self.assertContains(res, "<h1>Share Network Details: %s</h1>"
                                 % share_net.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_net.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_net.id, 1, 200)
        self.assertContains(res, "<dd>Unknown</dd>", 2, 200)
        self.assertNotContains(res, "<dd>%s</dd>" % share_net.neutron_net_id)
        self.assertNotContains(res,
                               "<dd>%s</dd>" % share_net.neutron_subnet_id)
        self.assertContains(res, "<a href=\"/project/shares/security_services"
                                 "/%s\">%s</a>" % (sec_service.id,
                                                   sec_service.name), 1, 200)
        self.assertNoMessages()
        api_manila.share_network_security_service_list.assert_called_once_with(
            mock.ANY, share_net.id)
        api_manila.share_server_list.assert_called_once_with(
            mock.ANY, search_opts={'share_network_id': share_net.id})
        api_manila.share_network_get.assert_called_once_with(
            mock.ANY, share_net.id)
        api_neutron.network_get.assert_called_once_with(
            mock.ANY, share_net.neutron_net_id)
        api_neutron.subnet_get.assert_called_once_with(
            mock.ANY, share_net.neutron_subnet_id)
        self.assertEqual(3, api_neutron.is_service_enabled.call_count)

    def test_detail_view_with_exception(self):
        url = reverse('horizon:admin:shares:share_network_detail',
                      args=[test_data.active_share_network.id])
        self.mock_object(
            api_manila, "share_network_get",
            mock.Mock(side_effect=manila_client_exc.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_network_get.assert_called_once_with(
            mock.ANY, test_data.active_share_network.id)

    def test_delete_share_network(self):
        share_network = test_data.inactive_share_network
        formData = {'action': 'share_networks__delete__%s' % share_network.id}
        self.mock_object(
            api_neutron, "network_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_neutron, "subnet_list", mock.Mock(return_value=[]))
        self.mock_object(api_manila, "share_network_delete")
        self.mock_object(
            api_manila, "share_network_list",
            mock.Mock(return_value=[
                test_data.active_share_network,
                test_data.inactive_share_network]))

        res = self.client.post(INDEX_URL, formData)

        api_keystone.tenant_list.assert_called_once_with(mock.ANY)
        api_manila.share_network_delete.assert_called_once_with(
            mock.ANY, test_data.inactive_share_network.id)
        api_manila.share_network_list.assert_called_once_with(
            mock.ANY, detailed=True, search_opts={'all_tenants': True})
        api_neutron.network_list.assert_called_once_with(mock.ANY)
        api_neutron.subnet_list.assert_called_once_with(mock.ANY)
        self.assertRedirectsNoFollow(res, INDEX_URL)


class SnapshotsTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(keystone_data.projects, None)))
        # Reset taken list of projects to avoid test interference
        utils.PROJECTS = {}

    def test_detail_view(self):
        snapshot = test_data.snapshot
        share = test_data.share
        url = reverse('horizon:project:shares:snapshot-detail',
                      args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertContains(res, "<h1>Snapshot Details: %s</h1>"
                                 % snapshot.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.id, 1, 200)
        self.assertContains(res,
                            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" %
                            (snapshot.share_id, share.name), 1, 200)
        self.assertContains(res, "<dd>%s GiB</dd>" % snapshot.size, 1, 200)
        self.assertNoMessages()
        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)
        self.assertEqual(3, api_neutron.is_service_enabled.call_count)

    def test_detail_view_with_exception(self):
        url = reverse('horizon:admin:shares:snapshot-detail',
                      args=[test_data.snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get",
            mock.Mock(side_effect=manila_client_exc.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, test_data.snapshot.id)

    def test_delete_snapshot(self):
        share = test_data.share
        snapshot = test_data.snapshot
        formData = {'action': 'snapshots__delete__%s' % snapshot.id}
        self.mock_object(api_manila, "share_snapshot_delete")
        self.mock_object(
            api_manila, "share_snapshot_list",
            mock.Mock(return_value=[snapshot]))
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=[share]))
        url = reverse('horizon:admin:shares:index')

        res = self.client.post(url, formData)

        api_keystone.tenant_list.assert_called_once_with(mock.ANY)
        api_manila.share_snapshot_delete.assert_called_once_with(
            mock.ANY, test_data.snapshot.id)
        api_manila.share_snapshot_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        api_manila.share_list.assert_called_once_with(mock.ANY)
        self.assertRedirectsNoFollow(res, INDEX_URL)


class ShareTypeTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.share_type = test_data.share_type
        self.url = reverse('horizon:admin:shares:update_type',
                           args=[self.share_type.id])
        self.mock_object(
            api_manila, "share_type_get",
            mock.Mock(return_value=self.share_type))
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(keystone_data.projects, None)))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        # Reset taken list of projects to avoid test interference
        utils.PROJECTS = {}

    def test_create_share_type(self):
        url = reverse('horizon:admin:shares:create_type')
        data = {
            'is_public': True,
            'name': 'my_share_type',
            'spec_driver_handles_share_servers': 'False'
        }
        form_data = data.copy()
        form_data['spec_driver_handles_share_servers'] = 'false'
        self.mock_object(api_manila, "share_type_create")

        res = self.client.post(url, data)

        api_manila.share_type_create.assert_called_once_with(
            mock.ANY, form_data['name'],
            form_data['spec_driver_handles_share_servers'],
            is_public=form_data['is_public'])
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_update_share_type_get(self):
        res = self.client.get(self.url)

        api_manila.share_type_get.assert_called_once_with(
            mock.ANY, self.share_type.id)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'admin/shares/update_share_type.html')

    def test_update_share_type_post(self):
        data = {
            'extra_specs': 'driver_handles_share_servers=True'
        }
        form_data = {
            'extra_specs': {'driver_handles_share_servers': 'True'},
        }
        self.mock_object(api_manila, "share_type_set_extra_specs")

        res = self.client.post(self.url, data)

        api_manila.share_type_set_extra_specs.assert_called_once_with(
            mock.ANY, self.share_type.id, form_data['extra_specs'])
        self.assertRedirectsNoFollow(res, INDEX_URL)
