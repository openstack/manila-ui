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

from django.urls import reverse
from horizon import exceptions as horizon_exceptions
import mock
from neutronclient.client import exceptions
from openstack_dashboard.api import keystone as api_keystone
from openstack_dashboard.api import neutron as api_neutron

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.admin import utils
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test
from manila_ui.tests.test_data import keystone_data

INDEX_URL = reverse('horizon:admin:share_networks:index')


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
        url = reverse('horizon:admin:share_networks:share_network_detail',
                      args=[share_net.id])

        res = self.client.get(url)

        self.assertContains(res, "<h1>Share Network Details: %s</h1>"
                                 % share_net.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_net.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_net.id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % network.name_or_id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % subnet.name_or_id, 1, 200)
        self.assertContains(res, "<a href=\"/admin/security_services"
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

    def test_detail_view_network_not_found(self):
        share_net = test_data.active_share_network
        sec_service = test_data.sec_service
        url = reverse('horizon:admin:share_networks:share_network_detail',
                      args=[share_net.id])
        self.mock_object(
            api_manila, "share_server_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "share_network_get", mock.Mock(return_value=share_net))
        self.mock_object(
            api_manila, "share_network_security_service_list",
            mock.Mock(return_value=[sec_service]))
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
        self.assertContains(res, "<a href=\"/admin/security_services"
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

    def test_detail_view_with_exception(self):
        url = reverse('horizon:admin:share_networks:share_network_detail',
                      args=[test_data.active_share_network.id])
        self.mock_object(
            api_manila, "share_network_get",
            mock.Mock(side_effect=horizon_exceptions.NotFound(404)))

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
