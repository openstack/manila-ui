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

from django.core.urlresolvers import reverse
import mock

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.project.shares import test_data
from openstack_dashboard import api
from openstack_dashboard.test import helpers as test
from openstack_dashboard.usage import quotas


INDEX_URL = reverse('horizon:admin:shares:index')


class SharesTests(test.BaseAdminViewTests):

    def test_index(self):
        snaps = [test_data.snapshot]
        shares = [test_data.share, test_data.nameless_share,
                  test_data.other_share]
        share_networks = [test_data.inactive_share_network,
                          test_data.active_share_network]
        security_services = [test_data.sec_service]

        api.keystone.tenant_list = mock.Mock(return_value=([], None))
        api_manila.share_list = mock.Mock(return_value=shares)
        api_manila.share_snapshot_list = mock.Mock(return_value=snaps)
        api_manila.share_network_list = mock.Mock(return_value=share_networks)
        api_manila.security_service_list = mock.Mock(
            return_value=security_services)
        api_manila.share_network_get = mock.Mock()
        api.neutron.network_list = mock.Mock(return_value=[])
        api.neutron.subnet_list = mock.Mock(return_value=[])
        quotas.tenant_limit_usages = mock.Mock(
            return_value=test_data.quota_usage)
        quotas.tenant_quota_usages = mock.Mock(
            return_value=test_data.quota_usage)
        res = self.client.get(INDEX_URL)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'admin/shares/index.html')

    def test_delete_share(self):
        share = test_data.share

        formData = {'action':
                    'shares__delete__%s' % share.id}

        api.keystone.tenant_list = mock.Mock(return_value=([], None))
        api_manila.share_delete = mock.Mock()
        api_manila.share_get = mock.Mock(
            return_value=test_data.share)
        api_manila.share_list = mock.Mock(
            return_value=[test_data.share])
        url = reverse('horizon:admin:shares:index')
        res = self.client.post(url, formData)
        api_manila.share_delete.assert_called_with(
            mock.ANY, test_data.share.id)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_delete_share_network(self):
        share_network = test_data.inactive_share_network

        formData = {'action':
                    'share_networks__delete__%s' % share_network.id}

        api.keystone.tenant_list = mock.Mock(return_value=([], None))
        api.neutron.network_list = mock.Mock(return_value=[])
        api.neutron.subnet_list = mock.Mock(return_value=[])
        api_manila.share_network_delete = mock.Mock()
        api_manila.share_network_get = mock.Mock(
            return_value=[test_data.inactive_share_network])
        api_manila.share_network_list = mock.Mock(
            return_value=[test_data.active_share_network,
                          test_data.inactive_share_network])
        url = reverse('horizon:admin:shares:index')
        res = self.client.post(url, formData)
        api_manila.share_network_delete.assert_called_with(
            mock.ANY, test_data.inactive_share_network.id)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_delete_snapshot(self):
        share = test_data.share
        snapshot = test_data.snapshot

        formData = {'action':
                    'snapshots__delete__%s' % snapshot.id}

        api.keystone.tenant_list = mock.Mock(return_value=([], None))
        api_manila.share_snapshot_delete = mock.Mock()
        api_manila.share_snapshot_get = mock.Mock(
            return_value=snapshot)
        api_manila.share_snapshot_list = mock.Mock(
            return_value=[snapshot])
        api_manila.share_list = mock.Mock(
            return_value=[share])
        url = reverse('horizon:admin:shares:index')
        res = self.client.post(url, formData)
        api_manila.share_snapshot_delete.assert_called_with(
            mock.ANY, test_data.snapshot.id)

        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_delete_security_service(self):
        security_service = test_data.sec_service

        formData = {'action':
                    'security_services__delete__%s' % security_service.id}

        api.keystone.tenant_list = mock.Mock(return_value=([], None))
        api_manila.security_service_delete = mock.Mock()
        api_manila.security_service_list = mock.Mock(
            return_value=[test_data.sec_service])
        url = reverse('horizon:admin:shares:index')
        res = self.client.post(url, formData)
        api_manila.security_service_delete.assert_called_with(
            mock.ANY, test_data.sec_service.id)
        self.assertRedirectsNoFollow(res, INDEX_URL)
