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

from openstack_dashboard import api
from oslo_utils import timeutils
from unittest import mock

from manila_ui.api import manila as api_manila
from manila_ui.dashboards import utils
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test


class ShareNetworkSubnetsViewTests(test.TestCase):
    class FakeAZ(object):
        def __init__(self, name, id):
            self.name = name
            self.id = id
            self.created_at = timeutils.utcnow()

    def test_create_share_network_subnets(self):
        share_net = test_data.active_share_network
        network_id = share_net.id
        url = '/project/share_networks/' + network_id + '/subnets/create'
        neutron_net_id = self.networks.first().id
        sanitized_net_id = utils.transform_dashed_name(neutron_net_id)

        formData = {
            'method': 'CreateForm',
            'neutron_net_id': utils.transform_dashed_name(neutron_net_id),
            'availability_zone': 'fake_az',
            f'subnet-choices-{sanitized_net_id}':
                self.networks.first().subnets[0].id,
        }

        self.mock_object(
            api.neutron, "subnet_list",
            mock.Mock(return_value=self.subnets.list()))
        self.mock_object(
            api.neutron, "network_list",
            mock.Mock(return_value=self.networks.list()))
        self.mock_object(
            api_manila, "share_network_get",
            mock.Mock(return_value=mock.Mock(name='test_network'))
        )
        self.mock_object(
            api_manila, "share_network_subnet_create",
            mock.Mock(return_value=share_net))
        self.mock_object(
            api_manila, "availability_zone_list",
            mock.Mock(return_value=[self.FakeAZ('fake_az', 'fake_az')])
        )

        # Get response from create subnet url using formData values
        res = self.client.post(url, formData)

        self.assertNoFormErrors(res)
        self.assertMessageCount(error=0, warning=0)

        api_manila.availability_zone_list.assert_called_once_with(mock.ANY)
        api.neutron.network_list.assert_called_once_with(mock.ANY)
        api.neutron.subnet_list.assert_has_calls([
            mock.call(mock.ANY, network_id=network.id)
            for network in self.networks.list()
        ], any_order=True)
        api_manila.share_network_subnet_create.assert_called_once_with(
            mock.ANY,
            share_network_id=network_id,
            neutron_net_id=neutron_net_id,
            neutron_subnet_id=self.networks.first().subnets[0].id,
            availability_zone='fake_az')
