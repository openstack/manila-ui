# Copyright 2020 Red Hat, Inc.
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
from django.urls import reverse
from openstack_dashboard.api import keystone as api_keystone
from unittest import mock

from horizon import exceptions as horizon_exceptions

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.admin import utils
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test
from manila_ui.tests.test_data import keystone_data


INDEX_URL = reverse('horizon:admin:user_messages:index')


@ddt.ddt
class UserMessagesViewTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(keystone_data.projects, None)))
        # Reset taken list of projects to avoid test interference
        utils.PROJECTS = {}

    @ddt.data(None, Exception('fake'))
    def test_view(self, exc):
        message_1 = test_data.fake_message_1
        message_2 = test_data.fake_message_2
        message_3 = test_data.fake_message_3
        fake_message_list = [message_1, message_2, message_3]
        url = reverse('horizon:admin:user_messages:index')
        self.mock_object(
            api_manila, "messages_list",
            mock.Mock(side_effect=exc, return_value=fake_message_list))

        self.client.get(url)

        self.assertNoMessages()
        api_manila.messages_list.assert_called_once_with(mock.ANY)

    @ddt.data(None, Exception('fake'))
    def test_delete_message(self, exc):
        message = test_data.fake_message_1
        formData = {'action': 'user_messages__delete__%s' % message.id}
        self.mock_object(api_manila, "messages_delete",
                         mock.Mock(side_effect=exc))
        self.mock_object(
            api_manila, "messages_list",
            mock.Mock(return_value=[message]))

        res = self.client.post(INDEX_URL, formData)

        self.assertEqual(res.status_code, 302)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.messages_list.assert_called_once_with(mock.ANY)
        api_manila.messages_delete.assert_called_once_with(
            mock.ANY, test_data.fake_message_1.id)


@ddt.ddt
class UserMessagesDetailViewTests(test.BaseAdminViewTests):

    def test_detail_view(self):
        message = test_data.fake_message_1
        url = reverse('horizon:admin:user_messages:user_messages_detail',
                      args=[message.id])
        self.mock_object(
            api_manila, "messages_get", mock.Mock(return_value=message))

        res = self.client.get(url)

        self.assertContains(res, "<h1>User Message Details: %s</h1>"
                                 % message.id,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % message.id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % message.action_id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % message.user_message, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % message.message_level, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % message.resource_type, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % message.resource_id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % message.request_id, 1, 200)

        self.assertNoMessages()
        api_manila.messages_get.assert_called_once_with(
            mock.ANY, message.id)

    def test_detail_view_with_exception(self):
        message = test_data.fake_message_1
        url = reverse(
            'horizon:admin:user_messages:user_messages_detail',
            args=[message.id])
        self.mock_object(
            api_manila, "messages_get",
            mock.Mock(side_effect=horizon_exceptions.NotFound(404)))
        res = self.client.get(url)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.messages_get.assert_called_once_with(mock.ANY, message.id)
