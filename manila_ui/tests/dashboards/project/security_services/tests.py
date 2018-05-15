# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
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
from openstack_dashboard import api

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:project:security_services:index')


class SecurityServicesViewTests(test.TestCase):

    def test_create_security_service(self):
        sec_service = test_data.sec_service
        formData = {
            'name': u'new_sec_service',
            'description': u'This is test security service',
            'method': u'CreateForm',
            'dns_ip': '1.2.3.4',
            'user': 'SomeUser',
            'password': 'safepass',
            'confirm_password': 'safepass',
            'type': 'ldap',
            'domain': 'TEST',
            'server': 'testserver',
        }
        url = reverse(
            'horizon:project:security_services:security_service_create')
        self.mock_object(
            api_manila, "security_service_create",
            mock.Mock(return_value=sec_service))

        res = self.client.post(url, formData)

        del formData['method']
        del formData['confirm_password']
        api_manila.security_service_create.assert_called_with(
            mock.ANY, **formData)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_delete_security_service(self):
        security_service = test_data.sec_service
        formData = {
            'action': 'security_services__delete__%s' % security_service.id,
        }
        self.mock_object(api_manila, "security_service_delete")
        self.mock_object(
            api_manila, "security_service_list",
            mock.Mock(return_value=[security_service]))

        res = self.client.post(INDEX_URL, formData)

        api_manila.security_service_list.assert_called_with(mock.ANY)
        api_manila.security_service_delete.assert_called_with(
            mock.ANY, security_service.id)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_detail_view(self):
        sec_service = test_data.sec_service
        self.mock_object(
            api_manila, "security_service_get",
            mock.Mock(return_value=sec_service))
        url = reverse(
            'horizon:project:security_services:security_service_detail',
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
            'horizon:project:security_services:security_service_detail',
            args=[test_data.sec_service.id])
        self.mock_object(
            api_manila, "security_service_get",
            mock.Mock(side_effect=horizon_exceptions.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.security_service_get.assert_called_once_with(
            mock.ANY, test_data.sec_service.id)

    def test_update_security_service_get(self):
        sec_service = test_data.sec_service
        url = reverse(
            'horizon:project:security_services:security_service_update',
            args=[sec_service.id])
        self.mock_object(
            api_manila, "security_service_get",
            mock.Mock(return_value=sec_service))
        self.mock_object(
            api.neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertNoMessages()
        self.assertTemplateUsed(
            res, 'project/security_services/update.html')
        api_manila.security_service_get.assert_called_once_with(
            mock.ANY, sec_service.id)

    def test_update_security_service_post(self):
        sec_service = test_data.sec_service
        url = reverse(
            'horizon:project:security_services:security_service_update',
            args=[sec_service.id])
        formData = {
            'method': 'UpdateForm',
            'name': sec_service.name,
            'description': sec_service.description,
        }
        self.mock_object(api_manila, "security_service_update")
        self.mock_object(
            api_manila, "security_service_get",
            mock.Mock(return_value=sec_service))

        res = self.client.post(url, formData)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.security_service_get.assert_called_once_with(
            mock.ANY, sec_service.id)
        api_manila.security_service_update.assert_called_once_with(
            mock.ANY,
            sec_service.id,
            name=formData['name'],
            description=formData['description'])
