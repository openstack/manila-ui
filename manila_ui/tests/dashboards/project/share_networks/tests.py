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

from django.urls import reverse
import mock
from neutronclient.client import exceptions
from openstack_auth import policy
from openstack_dashboard import api

from manila_ui.api import manila as api_manila
from manila_ui.api import network as api_manila_network
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:project:share_networks:index')


class ShareNetworksViewTests(test.TestCase):

    def test_create_share_network(self):
        share_net = test_data.active_share_network
        url = reverse('horizon:project:share_networks:share_network_create')
        neutron_net_id = self.networks.first().id
        formData = {
            'name': 'new_share_network',
            'description': 'This is test share network',
            'method': 'CreateForm',
            'neutron_net_id': neutron_net_id,
        }
        for net in self.networks.list():
            formData['subnet-choices-%s' % net.id] = net.subnets[0].id
        self.mock_object(
            api.neutron, "subnet_list",
            mock.Mock(return_value=self.subnets.list()))
        self.mock_object(
            api_manila_network, "network_list",
            mock.Mock(return_value=self.networks.list()))
        self.mock_object(
            api_manila, "share_network_create",
            mock.Mock(return_value=share_net))

        self.client.post(url, formData)

        api_manila.share_network_create.assert_called_with(
            mock.ANY, name=formData['name'], neutron_net_id=neutron_net_id,
            neutron_subnet_id=formData['subnet-choices-%s' % neutron_net_id],
            description=formData['description'])
        api_manila_network.network_list.assert_called_once_with(mock.ANY)
        api.neutron.subnet_list.assert_has_calls([
            mock.call(mock.ANY, network_id=network.id)
            for network in self.networks.list()
        ], any_order=True)

    def test_delete_share_network(self):
        share_network = test_data.inactive_share_network
        formData = {'action': 'share_networks__delete__%s' % share_network.id}
        self.mock_object(api_manila, "share_network_delete")
        self.mock_object(
            api_manila, "share_network_list",
            mock.Mock(return_value=[
                test_data.active_share_network, share_network]))
        self.mock_object(
            api.neutron, "network_list",
            mock.Mock(return_value=self.networks.list()))
        self.mock_object(
            api.neutron, "subnet_list",
            mock.Mock(return_value=self.subnets.list()))

        res = self.client.post(INDEX_URL, formData)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_network_list.assert_called_once_with(
            mock.ANY, detailed=True)
        api_manila.share_network_delete.assert_called_once_with(
            mock.ANY, share_network.id)
        api.neutron.network_list.assert_called_once_with(mock.ANY)
        api.neutron.subnet_list.assert_called_once_with(mock.ANY)

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
            api.neutron, "network_get", mock.Mock(return_value=network))
        self.mock_object(
            api.neutron, "subnet_get", mock.Mock(return_value=subnet))
        url = reverse('horizon:project:share_networks:share_network_detail',
                      args=[share_net.id])

        res = self.client.get(url)

        self.assertContains(res, "<h1>Share Network Details: %s</h1>"
                                 % share_net.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_net.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_net.id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % network.name_or_id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % subnet.name_or_id, 1, 200)
        self.assertContains(res, "<a href=\"/project/security_services"
                                 "/%s\">%s</a>" % (sec_service.id,
                                                   sec_service.name), 1, 200)
        self.assertNoMessages()
        api_manila.share_network_security_service_list.assert_called_once_with(
            mock.ANY, share_net.id)
        api_manila.share_server_list.assert_called_once_with(
            mock.ANY, search_opts={'share_network_id': share_net.id})
        api_manila.share_network_get.assert_called_once_with(
            mock.ANY, share_net.id)
        api.neutron.network_get.assert_called_once_with(
            mock.ANY, share_net.neutron_net_id)
        api.neutron.subnet_get.assert_called_once_with(
            mock.ANY, share_net.neutron_subnet_id)

    def test_detail_view_network_not_found(self):
        share_net = test_data.active_share_network
        sec_service = test_data.sec_service
        url = reverse('horizon:project:share_networks:share_network_detail',
                      args=[share_net.id])
        self.mock_object(
            api_manila, "share_server_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "share_network_get", mock.Mock(return_value=share_net))
        self.mock_object(
            api_manila, "share_network_security_service_list",
            mock.Mock(return_value=[sec_service]))
        self.mock_object(
            api.neutron, "network_get", mock.Mock(
                side_effect=exceptions.NeutronClientException('fake', 500)))
        self.mock_object(
            api.neutron, "subnet_get", mock.Mock(
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
        self.assertContains(res, "<a href=\"/project/security_services"
                                 "/%s\">%s</a>" % (sec_service.id,
                                                   sec_service.name), 1, 200)
        self.assertNoMessages()
        api_manila.share_network_security_service_list.assert_called_once_with(
            mock.ANY, share_net.id)
        api_manila.share_server_list.assert_called_once_with(
            mock.ANY, search_opts={'share_network_id': share_net.id})
        api_manila.share_network_get.assert_called_once_with(
            mock.ANY, share_net.id)
        api.neutron.network_get.assert_called_once_with(
            mock.ANY, share_net.neutron_net_id)
        api.neutron.subnet_get.assert_called_once_with(
            mock.ANY, share_net.neutron_subnet_id)

    def test_update_share_network(self):
        share_net = test_data.inactive_share_network
        formData = {
            'method': 'UpdateForm',
            'name': share_net.name,
            'description': share_net.description,
        }
        url = reverse('horizon:project:share_networks:share_network_update',
                      args=[share_net.id])
        self.mock_object(api_manila, "share_network_update")
        self.mock_object(
            api_manila, "share_network_get", mock.Mock(return_value=share_net))
        self.mock_object(
            api_manila, "share_network_security_service_list",
            mock.Mock(return_value=[test_data.sec_service]))
        self.mock_object(
            api_manila, "security_service_list",
            mock.Mock(return_value=[test_data.sec_service]))
        self.mock_object(
            policy, 'check',
            mock.Mock(side_effect=(lambda *args, **kwargs: True)))

        res = self.client.post(url, formData)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_network_security_service_list.assert_called_once_with(
            mock.ANY, share_net.id)
        api_manila.security_service_list.assert_has_calls([
            mock.call(mock.ANY),
            mock.call(mock.ANY, search_opts={'share_network_id': share_net.id})
        ])
        api_manila.share_network_get.assert_called_once_with(
            mock.ANY, share_net.id)
        api_manila.share_network_update.assert_called_once_with(
            mock.ANY,
            share_net.id,
            name=formData['name'],
            description=formData['description'])
        self.assertTrue(policy.check.called)
