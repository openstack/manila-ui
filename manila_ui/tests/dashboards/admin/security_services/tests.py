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
from openstack_dashboard.api import keystone as api_keystone

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.admin import utils
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test
from manila_ui.tests.test_data import keystone_data

INDEX_URL = reverse('horizon:admin:security_services:index')


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
        url = reverse(
            'horizon:admin:security_services:security_service_detail',
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

    def test_detail_view_with_exception(self):
        url = reverse(
            'horizon:admin:security_services:security_service_detail',
            args=[test_data.sec_service.id])
        self.mock_object(
            api_manila, "security_service_get",
            mock.Mock(side_effect=horizon_exceptions.NotFound(404)))

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

        res = self.client.post(INDEX_URL, formData)

        api_keystone.tenant_list.assert_called_once_with(mock.ANY)
        api_manila.security_service_delete.assert_called_once_with(
            mock.ANY, test_data.sec_service.id)
        api_manila.security_service_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        self.assertRedirectsNoFollow(res, INDEX_URL)
