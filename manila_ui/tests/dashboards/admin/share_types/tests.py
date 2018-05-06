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
import mock
from openstack_dashboard.api import keystone as api_keystone
from openstack_dashboard.api import neutron as api_neutron

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.admin import utils
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test
from manila_ui.tests.test_data import keystone_data

INDEX_URL = reverse('horizon:admin:share_types:index')


class ShareTypeTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.share_type = test_data.share_type
        self.url = reverse('horizon:admin:share_types:update_type',
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
        url = reverse('horizon:admin:share_types:create_type')
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
        self.assertTemplateUsed(res, 'admin/share_types/update.html')

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
