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

from mox import IsA  # noqa

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.project.shares import test_data

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test
from openstack_dashboard.usage import quotas


INDEX_URL = reverse('horizon:project:shares:index')


class SharesTests(test.TestCase):

    def test_index(self):
        snaps = [test_data.snapshot]
        shares = [test_data.share, test_data.nameless_share,
                  test_data.other_share]
        share_networks = [test_data.inactive_share_network,
                          test_data.active_share_network]
        security_services = [test_data.sec_service]

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
        self.assertTemplateUsed(res, 'project/shares/index.html')
